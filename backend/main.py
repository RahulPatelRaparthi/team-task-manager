import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# ---------------- CONFIG ----------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./team_task_manager.db")
SECRET_KEY = os.getenv("SECRET_KEY", "team-task-manager-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

app = FastAPI(title="Team Task Manager API", version="1.0.0")

# ✅ FINAL CORS FIX (works everywhere)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# ---------------- DATABASE MODELS ----------------

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="Member")


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, default="")
    status = Column(String, default="Pending")
    deadline = Column(DateTime, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"))
    created_by = Column(Integer, ForeignKey("users.id"))

Base.metadata.create_all(bind=engine)

# ---------------- SCHEMAS ----------------

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "Member"


class LoginRequest(BaseModel):
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

# ---------------- HELPERS ----------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def admin_required(current_user: User = Depends(get_current_user)):
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="Only Admin can perform this action")
    return current_user

# ---------------- ROUTES ----------------

@app.post("/signup")
def signup(user_data: SignupRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if user_data.role not in ["Admin", "Member"]:
        raise HTTPException(status_code=400, detail="Role must be Admin or Member")

    user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role=user_data.role
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User registered successfully", "user_id": user.id}


@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    })

    return {"access_token": token, "token_type": "bearer"}


@app.post("/projects")
def create_project(project: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    new_project = Project(
        name=project.name,
        description=project.description,
        created_by=current_user.id
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return {"message": "Project created", "id": new_project.id}


@app.get("/projects")
def get_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Project).all()


@app.post("/tasks")
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(admin_required)):
    new_task = Task(**task.dict(), created_by=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"message": "Task created"}


@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role.lower() == "admin":
        return db.query(Task).all()
    return db.query(Task).filter(Task.assigned_to == current_user.id).all()


@app.put("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if current_user.role.lower() != "admin" and task.assigned_to != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    task.status = update.status
    db.commit()

    return {"message": "Task updated"}


@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tasks = db.query(Task).all()
    return {
        "total": len(tasks),
        "completed": len([t for t in tasks if t.status == "Done"])
    }


# ✅ ROOT ROUTE
@app.get("/")
def home():
    return {
        "message": "Team Task Manager API running",
        "docs": "/docs"
    }
