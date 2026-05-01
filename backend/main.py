import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# ================= CONFIG =================
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./team_task_manager.db")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

# Fix Railway postgres URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ================= APP =================
app = FastAPI()

# 🔥 FINAL CORS FIX (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allow all origins (fix for your error)
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ================= MODELS =================
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(String)


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    status = Column(String, default="Pending")
    project_id = Column(Integer)
    assigned_to = Column(Integer)
    deadline = Column(DateTime)


Base.metadata.create_all(bind=engine)

# ================= SCHEMAS =================
class Signup(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str


class Login(BaseModel):
    email: EmailStr
    password: str


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = ""


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    project_id: int
    assigned_to: int
    deadline: Optional[datetime] = None


class TaskUpdate(BaseModel):
    status: str

# ================= UTILS =================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(p):
    return pwd_context.hash(p)


def verify_password(p, h):
    return pwd_context.verify(p, h)


def create_token(data: dict):
    data["exp"] = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.id == payload.get("user_id")).first()
        if not user:
            raise HTTPException(status_code=401)
        return user
    except JWTError:
        raise HTTPException(status_code=401)


def admin_only(user: User = Depends(get_current_user)):
    if user.role.lower() != "admin":
        raise HTTPException(status_code=403)
    return user

# ================= ROUTES =================
@app.get("/")
def home():
    return {"message": "API Running 🚀"}

# ---------- AUTH ----------
@app.post("/signup")
def signup(data: Signup, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Email exists")

    user = User(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        role=data.role,
    )

    db.add(user)
    db.commit()
    return {"msg": "User created"}


@app.post("/login")
def login(data: Login, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid credentials")

    token = create_token({"user_id": user.id})

    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        },
    }

# ---------- USERS ----------
@app.get("/users")
def users(db: Session = Depends(get_db), u: User = Depends(admin_only)):
    return db.query(User).all()

# ---------- PROJECTS ----------
@app.post("/projects")
def create_project(data: ProjectCreate, db: Session = Depends(get_db), u: User = Depends(admin_only)):
    p = Project(name=data.name, description=data.description, created_by=u.id)
    db.add(p)
    db.commit()
    return p


@app.get("/projects")
def get_projects(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    return db.query(Project).all()

# ---------- TASKS ----------
@app.post("/tasks")
def create_task(data: TaskCreate, db: Session = Depends(get_db), u: User = Depends(admin_only)):
    t = Task(**data.dict())
    db.add(t)
    db.commit()
    return t


@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    if u.role.lower() == "admin":
        return db.query(Task).all()
    return db.query(Task).filter(Task.assigned_to == u.id).all()


@app.put("/tasks/{id}")
def update_task(id: int, data: TaskUpdate, db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == id).first()
    if not task:
        raise HTTPException(404)

    if u.role.lower() != "admin" and task.assigned_to != u.id:
        raise HTTPException(403)

    task.status = data.status
    db.commit()
    return {"msg": "Updated"}

# ---------- DASHBOARD ----------
@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db), u: User = Depends(get_current_user)):
    tasks = db.query(Task).all() if u.role.lower() == "admin" else db.query(Task).filter(Task.assigned_to == u.id).all()

    return {
        "total_tasks": len(tasks),
        "completed_tasks": len([t for t in tasks if t.status == "Done"]),
        "in_progress_tasks": len([t for t in tasks if t.status == "In Progress"]),
        "overdue_tasks": len([t for t in tasks if t.deadline and t.deadline < datetime.utcnow()])
    }
