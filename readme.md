# 🛡️ PaySafe AI

PaySafe AI is a **full-stack AI-powered insurance platform** designed for gig workers.
It provides **real-time risk monitoring, automated triggers, and instant claim payouts** using a FastAPI backend and an interactive frontend dashboard.

---

## 🚀 Features

### 🔐 Authentication

* User Registration & Login
* Role-based access (User / Admin)
* Zone-based onboarding

### 📊 Dashboard

* AI Risk Score Gauge
* Weekly Premium Calculation
* Coverage Details & Progress
* Live Alerts (Weather / AQI)

### ⚡ Triggers System

* Real-time disruption triggers:

  * Rainfall 🌧️
  * Heatwave 🌡️
  * AQI ☁️
* Live trigger logs
* Trigger simulation (Admin)

### 💸 Claims System

* Zero-touch claim processing
* AI fraud detection
* Instant payout simulation
* Claim history tracking

### 🤖 Premium Engine

* Dynamic pricing based on:

  * Risk score
  * Weather
  * AQI
* ML-style multiplier logic

### ⚙️ Admin Panel

* View all users
* View all claims
* Risk monitoring dashboard

---

## 🏗️ Project Structure

```
PaySafeAi/
│
├── backend/
│   ├── server.py          # FastAPI app
│   ├── ai_logic.py        # AI risk engine
│
├── frontend/
│   ├── index.html         # Full UI (HTML + CSS + JS)
│
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone <your-repo-link>
cd PaySafeAi
```

---

### 2️⃣ Install Backend Dependencies

```bash
cd backend
pip install fastapi uvicorn
```

---

### 3️⃣ Run Backend Server

⚠️ IMPORTANT (Fix for your error):

If `uvicorn` is not recognized, use:

```bash
python -m uvicorn server:app --reload
```

✅ Server runs at:

```
http://127.0.0.1:8000
```

---

### 4️⃣ Verify Backend

Open:

```
http://127.0.0.1:8000/docs
```

Test APIs like:

* `/api/register`
* `/api/login`
* `/api/dashboard/{mobile}`
* `/api/claim`
* `/api/triggers`

---

### 5️⃣ Run Frontend

Go to frontend folder:

```bash
cd ../frontend
```

Then:

👉 Option 1 (Recommended):

* Open in VS Code
* Right click `index.html`
* Click **"Open with Live Server"**

👉 Option 2:

* Double click `index.html`

---

## 🔗 API Endpoints

| Method | Endpoint                  | Description       |
| ------ | ------------------------- | ----------------- |
| POST   | `/api/register`           | Register user     |
| POST   | `/api/login`              | Login user        |
| GET    | `/api/dashboard/{mobile}` | Dashboard data    |
| GET    | `/api/claims/{mobile}`    | Get user claims   |
| POST   | `/api/claim`              | Trigger claim     |
| GET    | `/api/triggers`           | Get live triggers |
| POST   | `/api/triggers/simulate`  | Simulate trigger  |
| GET    | `/api/admin/users`        | Admin users list  |
| GET    | `/api/admin/claims`       | Admin claims list |

---

## 🔄 Application Flow

```
Frontend (HTML + JS)
        ↓
FastAPI Backend (server.py)
        ↓
AI Logic Engine (ai_logic.py)
        ↓
Risk Score + Premium + Claim
        ↓
Frontend Dashboard Updates
```

---

## 🧪 Demo Credentials

```
Admin Login:
Mobile: 9999999999
Password: admin123
```

---

## 🧠 AI Logic Overview

The system simulates AI using:

* 🌧️ Weather conditions
* 🌫️ AQI levels
* ⏰ Time-based risk
* 📍 Zone-based risk

Outputs:

* Risk Score (0–100)
* Risk Level (Low / Medium / High)
* Premium calculation
* Claim payout

---

## ❗ Common Errors & Fixes

### ❌ "uvicorn not recognized"

✅ Fix:

```bash
python -m uvicorn server:app --reload
```

---

### ❌ Login/Register not working

✔️ Check:

* Backend is running
* API URL is correct in frontend:

```js
const API = 'http://127.0.0.1:8000';
```

---

### ❌ "Cannot connect to backend"

✔️ Make sure:

* Backend is running
* No firewall blocking port 8000

---

## 🎯 Use Case

Built for:

* Gig workers (delivery, drivers)
* Outdoor workers
* Weather-risk dependent jobs

---

## 🚀 Future Enhancements

* 🌐 Real API integration (Weather, AQI)
* 🧠 True ML model (not simulated)
* 🗄️ Database (MongoDB / PostgreSQL)
* 🔐 JWT Authentication
* 📱 Mobile app

---

## 👩‍💻 Authors
Siddhi Jadhav
Samidha Lade
Harshvardhan Chaudhary
Yashasvi Shrivastava
SRM Institute of Science and Technology

---

## 🎉 Conclusion

PaySafe AI shows how insurance can be:

* ⚡ Instant (auto payouts)
* 🧠 Intelligent (AI risk scoring)
* 🌍 Inclusive (for gig workers)

---