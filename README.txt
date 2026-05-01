# 🚀 Team Task Manager

A full-stack **Team Task Management System** built using **FastAPI (Backend)** and **React + Vite (Frontend)**.  
This application helps teams manage projects, assign tasks, and track progress efficiently.

---

## 🌐 Live Demo

- 🔗 Frontend: https://team-task-manager-lime.vercel.app/
- 🔗 Backend API: https://team-task-manager-production-a8c9.up.railway.app/docs

---

## 📌 Features

### 🔐 Authentication
- User Signup & Login
- JWT-based Authentication
- Role-based Access (Admin / User)

### 👥 User Management
- Admin can view all users
- Role-based permissions

### 📁 Project Management
- Create Projects (Admin)
- View Projects

### ✅ Task Management
- Create Tasks
- Assign Tasks to team members
- Update task status (Pending / In Progress / Done)
- View tasks based on role

### 📊 Dashboard
- Total Tasks
- Completed Tasks
- In Progress Tasks
- Overdue Tasks

---

## 🛠️ Tech Stack

### Frontend
- React (Vite)
- CSS

### Backend
- FastAPI
- SQLAlchemy
- SQLite / PostgreSQL (Railway)
- JWT Authentication

### Deployment
- Frontend: Vercel
- Backend: Railway

---

## 📂 Project Structure

team-task-manager/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── Procfile
│
├── frontend/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   └── .env
│
└── README.md

---

## ⚙️ Setup Instructions

### 🔹 Backend Setup

cd backend  
pip install -r requirements.txt  
uvicorn main:app --reload  

Backend runs on:  
http://127.0.0.1:8000  

---

### 🔹 Frontend Setup

cd frontend  
npm install  
npm run dev  

Frontend runs on:  
http://localhost:5173  

---

## 🔑 Environment Variables

### Frontend (.env)

VITE_API_BASE_URL=https://team-task-manager-production-a8c9.up.railway.app

---

## 🔒 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | /signup  | Register user |
| POST   | /login   | Login user |
| GET    | /users   | Get all users (Admin) |
| GET    | /projects | Get projects |
| POST   | /projects | Create project |
| GET    | /tasks   | Get tasks |
| POST   | /tasks   | Create task |
| PUT    | /tasks/{id} | Update task |
| GET    | /dashboard | Dashboard data |

---

## 🧪 Testing

- FastAPI Swagger UI → /docs  
- Postman  

---

## 🚀 Deployment

### Backend (Railway)
- Connected GitHub repo
- Auto deploy enabled
- Runs on `$PORT`

### Frontend (Vercel)
- Deployed using GitHub integration
- Environment variable configured

---

## ⚠️ Issues Faced & Fixes

- CORS Error → Fixed using FastAPI CORSMiddleware  
- Railway Port Issue → Used `$PORT`  
- Environment Variables → Configured correctly in Vercel  

---

## 📌 Future Enhancements

- Notifications system  
- File uploads  
- Real-time updates  
- Improved UI/UX  

---

## 👨‍💻 Author

Rahul Patel Raparthi
B.Tech Student 
Teegala Krishna Reddy Engineering College
Computer Science and Engineering

---

## ⭐ Conclusion

This project demonstrates:
- Full-stack development
- API design using FastAPI
- Frontend integration with React
- Deployment using modern tools

---

💡 Thank you for reviewing this project!
