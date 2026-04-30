# 🚀 Team Task Manager (Full-Stack)

A simple full-stack web application that allows teams to create projects, assign tasks, and track progress with role-based access control (Admin/Member).

---

## 📌 Overview

This project was built as part of a full-stack assessment. It demonstrates core software engineering concepts including authentication, REST APIs, database relationships, and role-based access control.

---

## ✨ Features

### 🔐 Authentication

* User Signup & Login
* JWT-based authentication

### 👥 Role-Based Access

* **Admin**

  * Create projects
  * Assign tasks
* **Member**

  * View assigned tasks
  * Update task status

### 📁 Project Management

* Create and view projects

### 📋 Task Management

* Create tasks
* Assign tasks to users
* Update task status (Pending / In Progress / Done)

### 📊 Dashboard

* Total tasks
* Completed tasks
* Overdue tasks

---

## 🛠️ Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy

### Frontend

* HTML, CSS, JavaScript

### Database

* SQLite (default)

### Deployment

* Railway

---

## ⚙️ Setup Instructions (Local)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/team-task-manager.git
cd team-task-manager
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
uvicorn main:app --reload
```

### 5. Open in browser

```
http://127.0.0.1:8000
```

---

## 🔗 API Endpoints

### Auth

* `POST /signup` → Register user
* `POST /login` → Login user

### Projects

* `POST /projects` → Create project (Admin only)
* `GET /projects` → View projects

### Tasks

* `POST /tasks` → Create task (Admin only)
* `GET /tasks` → View tasks
* `PUT /tasks/{id}` → Update task status

### Dashboard

* `GET /dashboard` → Task summary

---

## 🌍 Live Deployment

https://team-task-manager-production-9dc6.up.railway.app

---

## 🎥 Demo Video

👉 **Demo Video Link:** [Add your video link here]

---

## 📂 Project Structure

```
backend/
 ├── main.py
 ├── models.py
 ├── database.py
 ├── routes/
 │    ├── auth.py
 │    ├── project.py
 │    ├── task.py

frontend/
 ├── index.html
 ├── login.html
 ├── dashboard.html
```

---

## 🧠 Design Decisions

* Used FastAPI for fast API development and clean structure
* Implemented JWT for secure authentication
* Used role-based logic to control access
* Kept UI minimal to focus on functionality

---

## 🚧 Future Improvements

* Add team collaboration features
* Improve UI with React
* Add notifications & comments on tasks
* Add file attachments

---

## 👨‍💻 Author

Rahul Patel
Bachelor of Technology (CSE)
Teegala Krishna Reddy Engineering College

---


