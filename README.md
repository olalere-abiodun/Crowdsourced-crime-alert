# 🚨 Crowdsource Crime Alert API

A backend system for reporting, managing, and responding to crime incidents and emergency (SOS) alerts.  
Built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**, this project allows users to securely authenticate, report crimes, send SOS alerts, and lets administrators monitor/respond in real time.

---

## ✨ Features

- 🔑 **User Authentication** – JWT-based login & registration
- 📝 **Crime Reporting** – Users can submit detailed crime reports
- 📍 **SOS Alerts** – Send emergency alerts with GPS coordinates
- 📊 **Admin Dashboard Ready** – Expose endpoints for responders/admins to manage reports
- 🗄 **Database Persistence** – PostgreSQL with SQLAlchemy ORM
- ✅ **Automated Tests** – Pytest support with FastAPI `TestClient`

---

## 📂 Project Structure

![Directory Structure](directory-structure.png)

---

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/crowdsource-crime-alert.git
cd crowdsource-crime-alert

---

### 2. Create Virtual Environment

```bash
python -m venv myvenv
source myvenv/bin/activate   # Linux/Mac
myvenv\Scripts\activate      # Windows


### 3. Install Dependencies
```bash
pip install -r requirements.txt


### 4.  Configure Environment Variables

```bash

DATABASE_URL=postgresql://user:password@localhost:5432/crowdcrime
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

---

### 5.  Run database Migration

```bash

alembic upgrade head

### 6.  Start the server

uvicorn app.main:app --reload

## API Endpoint
### 👤 Authentication (/auth)

- POST /auth/signup → Register a new user
    - Body: { "email", "username", "password", "fullname", "role" }

- POST /auth/login → Login and obtain JWT token
    - Body: { "username", "password" }

- GET /auth/me/ → Get current logged-in user profile
    - Headers: Authorization: Bearer <token>

- PUT /auth/users/me → Update current user profile & change password
    - Headers: Authorization: Bearer <token>

### 🚨 Crimes (/crime)

- POST /crime/crimes → Report a new crime
    - Headers: Authorization: Bearer <token>

- GET /crime/crime → Get all crimes

- GET /crime/crime/{id} → Get crime by ID

- DELETE /crime/crime/{id} → Delete a crime (requires authentication)
    - Headers: Authorization: Bearer <token>

### 👍 Voting (/vote)

- POST /vote/crimes/{crime_id}/vote → Vote on a crime
    - Authenticated users → vote is tied to their account
    - Anonymous users → vote is recorded without user_id
    - Body: { "vote_type": "up" | "down" }

- GET /vote/crimes/{crime_id}/votes → Get vote counts for a crime
    - Response: { "authenticated", "anonymous", "total" }

### 🛡️ Admin (/admin)

- POST /admin/crime/{crime_id}/flag → Flag a crime as inappropriate
    - Headers: Authorization: Bearer <admin_token>
    - Body: { "reason", "is_flagged" }

- GET /admin/crimes/flagged → Get all flagged crimes
    - Headers: Authorization: Bearer <admin_token>

- GET /admin/statistics → Get statistics (reports count, crime types, hotspots)
    - Headers: Authorization: Bearer <admin_token>

### 🔔 Alerts (/alerts)

- POST /alerts/subscribe → Subscribe for nearby crime alerts
    - Headers: Authorization: Bearer <token>
    - Body: { "latitude", "longitude", "radius", "is_active" }

- GET /alerts/subscribe → Get current user’s subscription details
    - Headers: Authorization: Bearer <token>

### 🆘 SOS (/sos)

- POST /sos/send_sos → Send an SOS alert (authenticated only)
    - Headers: Authorization: Bearer <token>
    - Body: { "latitude", "longitude", "message" }

- GET /sos/sos_alerts → Retrieve all SOS alerts (admin only)
    - Headers: Authorization: Bearer <admin_token>

---

## 🧪 Running Tests


```bash

pip install pytest
pip install pytest-cov
pytest -v

---

## 🚀 Deployment

You can deploy with:

    1. Docker
    2. Render / Railway / Heroku  
    3. AWS EC2 + Nginx + Gunicorn

---

## 📌 Roadmap

1.  Add SMS notifications for SOS (via Twilio or similar)

2. Build frontend dashboard for admins

3. Add real-time WebSocket alerts

4. Role-based access control (RBAC)

## 👨‍💻 Author

- Olalere S. Abiodun – Backend Developer
📧 shervie20@gmail.com
    🔗 LinkedIn: https://www.linkedin.com/in/olalere-sherifdeen/
    GitHub: @olalere-abiodun


##  📜 License

This project is licensed under the MIT License – free to use, modify, and distribute.

