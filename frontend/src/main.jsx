import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL || "https://team-task-manager-production-a8c9.up.railway.app";

function App() {
  const [token, setToken] = useState(localStorage.getItem("ttm_token") || "");
  const [user, setUser] = useState(JSON.parse(localStorage.getItem("ttm_user") || "null"));
  const [mode, setMode] = useState("signup");
  const [tab, setTab] = useState("dashboard");
  const [modal, setModal] = useState(null);
  const [message, setMessage] = useState("");
  const [projects, setProjects] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);
  const [dashboard, setDashboard] = useState({
    total_tasks: 0,
    completed_tasks: 0,
    in_progress_tasks: 0,
    overdue_tasks: 0
  });

  const isAdmin = user?.role?.toLowerCase() === "admin";

  async function api(path, options = {}) {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.headers || {})
      }
    });

    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || "Request failed");
    return data;
  }

  async function loadAll() {
    if (!token) return;
    try {
      const [p, t, d] = await Promise.all([api("/projects"), api("/tasks"), api("/dashboard")]);
      setProjects(p);
      setTasks(t);
      setDashboard(d);
      if (isAdmin) {
        const u = await api("/users");
        setUsers(u);
      } else {
        setUsers(user ? [user] : []);
      }
    } catch (err) {
      setMessage(err.message);
    }
  }

  useEffect(() => {
    loadAll();
  }, [token, user?.role]);

  async function handleAuth(e) {
    e.preventDefault();
    setMessage("");
    const data = Object.fromEntries(new FormData(e.currentTarget).entries());

    try {
      if (mode === "signup") {
        await api("/signup", { method: "POST", body: JSON.stringify(data) });
        setMessage("Signup successful. Login now.");
        setMode("login");
        return;
      }

      const result = await api("/login", { method: "POST", body: JSON.stringify(data) });
      setToken(result.access_token);
      setUser(result.user);
      localStorage.setItem("ttm_token", result.access_token);
      localStorage.setItem("ttm_user", JSON.stringify(result.user));
    } catch (err) {
      setMessage(err.message);
    }
  }

  function logout() {
    localStorage.removeItem("ttm_token");
    localStorage.removeItem("ttm_user");
    setToken("");
    setUser(null);
    setTab("dashboard");
    setModal(null);
  }

  async function createProject(e) {
    e.preventDefault();
    setMessage("");
    const data = Object.fromEntries(new FormData(e.currentTarget).entries());
    try {
      await api("/projects", { method: "POST", body: JSON.stringify(data) });
      setModal(null);
      await loadAll();
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function createTask(e) {
    e.preventDefault();
    setMessage("");
    const data = Object.fromEntries(new FormData(e.currentTarget).entries());
    data.project_id = Number(data.project_id);
    data.assigned_to = Number(data.assigned_to);
    data.deadline = data.deadline ? new Date(data.deadline).toISOString() : null;

    try {
      await api("/tasks", { method: "POST", body: JSON.stringify(data) });
      setModal(null);
      await loadAll();
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function updateStatus(taskId, status) {
    try {
      await api(`/tasks/${taskId}`, { method: "PUT", body: JSON.stringify({ status }) });
      await loadAll();
    } catch (err) {
      setMessage(err.message);
    }
  }

  if (!token) {
    return (
      <main className="auth-page">
        <section className="auth-card">
          <h1>Team Task Manager</h1>

          <div className="switch">
            <button className={mode === "signup" ? "active" : ""} onClick={() => setMode("signup")}>Sign Up</button>
            <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")}>Login</button>
          </div>

          <form onSubmit={handleAuth} className="auth-form">
            {mode === "signup" && (
              <>
                <label>Name</label>
                <input name="name" placeholder="John Doe" required />
              </>
            )}

            <label>Email</label>
            <input name="email" type="email" placeholder="your@email.com" required />

            <label>Password</label>
            <input name="password" type="password" placeholder="••••••••" required />

            {mode === "signup" && (
              <>
                <label>Role</label>
                <select name="role" required defaultValue="">
                  <option value="" disabled>Select Role</option>
                  <option value="Admin">Admin</option>
                  <option value="Member">Member</option>
                </select>
              </>
            )}

            <button type="submit">{mode === "signup" ? "Sign Up" : "Login"}</button>
          </form>

          {message && <p className="msg">{message}</p>}
        </section>
      </main>
    );
  }

  return (
    <main className="layout">
      <header className="topbar">
        <div className="brand">
          <span className="logo">📊</span>
          <h1>Team Task Manager</h1>
        </div>
        <div className="profile">
          <span>👤 {user?.name}</span>
          <span className="role">{user?.role?.toUpperCase()}</span>
          <button onClick={logout}>Logout</button>
        </div>
      </header>

      <section className="main">
        <aside className="sidebar">
          <NavButton active={tab === "dashboard"} onClick={() => setTab("dashboard")} icon="📈" text="Dashboard" />
          <NavButton active={tab === "projects"} onClick={() => setTab("projects")} icon="📁" text="Projects" />
          <NavButton active={tab === "tasks"} onClick={() => setTab("tasks")} icon="✅" text="Tasks" />
          <NavButton active={tab === "team"} onClick={() => setTab("team")} icon="👥" text="Team" />
          {isAdmin && <NavButton active={tab === "admin"} onClick={() => setTab("admin")} icon="⚙️" text="Admin" />}
        </aside>

        <section className="content-card">
          {message && <div className="alert">{message}</div>}

          {tab === "dashboard" && (
            <>
              <Title text="Dashboard" />
              <div className="stats">
                <Stat title="Total Tasks" value={dashboard.total_tasks || 0} />
                <Stat title="Completed" value={dashboard.completed_tasks || 0} />
                <Stat title="In Progress" value={dashboard.in_progress_tasks || 0} />
                <Stat title="Overdue" value={dashboard.overdue_tasks || 0} />
              </div>

              <h2 className="sub">Recent Tasks</h2>
              {tasks.length === 0 ? (
                <p className="empty">No tasks assigned</p>
              ) : (
                <div className="table-wrap">
                  {tasks.slice(0, 5).map((task) => <TaskItem key={task.id} task={task} onChange={updateStatus} />)}
                </div>
              )}
            </>
          )}

          {tab === "projects" && (
            <>
              <Title text="Projects" />
              {isAdmin && <button className="primary" onClick={() => setModal("project")}>+ New Project</button>}
              <div className="project-grid">
                {projects.length === 0 ? <p className="empty">No projects found</p> : projects.map((p) => (
                  <div className="project-card" key={p.id}>
                    <h3>{p.name}</h3>
                    <p>{p.description || "No description"}</p>
                    <span>📌 {tasks.filter((t) => t.project_id === p.id).length} tasks</span>
                  </div>
                ))}
              </div>
            </>
          )}

          {tab === "tasks" && (
            <>
              <Title text="Tasks" />
              {isAdmin && <button className="primary" onClick={() => setModal("task")}>+ New Task</button>}
              <div className="task-list">
                {tasks.length === 0 ? <p className="empty">No tasks assigned</p> : tasks.map((task) => (
                  <TaskItem key={task.id} task={task} onChange={updateStatus} />
                ))}
              </div>
            </>
          )}

          {tab === "team" && (
            <>
              <Title text="Team Members" />
              {isAdmin && <button className="primary muted">+ Add Member</button>}
              <table>
                <thead>
                  <tr><th>Name</th><th>Email</th><th>Role</th><th>Joined</th><th>Action</th></tr>
                </thead>
                <tbody>
                  {(isAdmin ? users : [user]).map((u) => (
                    <tr key={u.id}>
                      <td>{u.name}</td>
                      <td>{u.email}</td>
                      <td><span className="role-chip">{u.role?.toUpperCase()}</span></td>
                      <td>{new Date().toLocaleDateString()}</td>
                      <td>-</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </>
          )}

          {tab === "admin" && (
            <>
              <Title text="Admin" />
              <div className="admin-box">
                <h2>Admin Controls</h2>
                <p>Create projects, assign tasks, view all users, and track team progress.</p>
                <p>Members can view assigned tasks and update their task status.</p>
              </div>
            </>
          )}
        </section>
      </section>

      {modal === "project" && (
        <Modal title="New Project" onClose={() => setModal(null)}>
          <form onSubmit={createProject} className="modal-form">
            <label>Project Name</label>
            <input name="name" placeholder="Enter project name" required />
            <label>Description</label>
            <input name="description" placeholder="Project description" />
            <div className="modal-actions">
              <button type="button" className="cancel" onClick={() => setModal(null)}>Cancel</button>
              <button>Create</button>
            </div>
          </form>
        </Modal>
      )}

      {modal === "task" && (
        <Modal title="New Task" onClose={() => setModal(null)}>
          <form onSubmit={createTask} className="modal-form">
            <label>Task Title</label>
            <input name="title" placeholder="Task title" required />

            <label>Description</label>
            <input name="description" placeholder="Task description" />

            <label>Project</label>
            <select name="project_id" required>
              <option value="">Select Project</option>
              {projects.map((p) => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>

            <label>Assign To</label>
            <select name="assigned_to" required>
              <option value="">Select Member</option>
              {users.map((u) => <option key={u.id} value={u.id}>{u.name}</option>)}
            </select>

            <label>Due Date</label>
            <input name="deadline" type="date" />

            <div className="modal-actions">
              <button type="button" className="cancel" onClick={() => setModal(null)}>Cancel</button>
              <button>Create</button>
            </div>
          </form>
        </Modal>
      )}
    </main>
  );
}

function NavButton({ active, onClick, icon, text }) {
  return <button className={`nav ${active ? "active" : ""}`} onClick={onClick}><span>{icon}</span>{text}</button>;
}

function Title({ text }) {
  return <><h1 className="title">{text}</h1><div className="line" /></>;
}

function Stat({ title, value }) {
  return <div className="stat"><p>{title}</p><h2>{value}</h2></div>;
}

function TaskItem({ task, onChange }) {
  return (
    <div className="task-item">
      <div>
        <h3>{task.title}</h3>
        <p>{task.description || "No description"}</p>
        <small>Project ID: {task.project_id} | Assigned To: {task.assigned_to}</small>
      </div>
      <select value={task.status} onChange={(e) => onChange(task.id, e.target.value)}>
        <option>Pending</option>
        <option>In Progress</option>
        <option>Done</option>
      </select>
    </div>
  );
}

function Modal({ title, children, onClose }) {
  return (
    <div className="overlay" onClick={onClose}>
      <section className="modal" onClick={(e) => e.stopPropagation()}>
        <h1>{title}</h1>
        {children}
      </section>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
console.log("API BASE:", API_BASE);
