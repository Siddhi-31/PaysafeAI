from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import datetime
import random

from ai_logic import (
    calculate_ai_risk,
    calculate_payout,
    calculate_premium,
    calculate_fraud_score,
    verify_gps_zone,
    simulate_triggers,
    generate_trigger_log,
    ZONES,
)

app = FastAPI(title="PaySafe AI — Enhanced Backend", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── In-Memory Store ─────────────────────────
users: dict = {}          # mobile → {password, name, zone_id, role, claims_count, premium}
claims: list = []         # list of claim dicts
claim_counter: int = 8800  # CLM-XXXX numbering

BASE_PAYOUT = 500.0

# ─── Models ──────────────────────────────────
class RegisterRequest(BaseModel):
    mobile: str
    password: str
    name: str
    zone_id: Optional[int] = 4

class LoginRequest(BaseModel):
    mobile: str
    password: str

class ClaimRequest(BaseModel):
    mobile: str

class SimulateTriggerRequest(BaseModel):
    trigger_id: str
    zone_id: Optional[int] = 4

# ─── Root ─────────────────────────────────────
@app.get("/")
def root():
    return {"message": "PaySafe AI Backend v2.0 running", "status": "ok"}

# ─── Auth ─────────────────────────────────────
@app.post("/api/register")
def register(body: RegisterRequest):
    mobile = body.mobile.strip()
    if not mobile or not body.password.strip():
        raise HTTPException(400, "Mobile and password are required.")
    if mobile in users:
        raise HTTPException(409, "User already registered.")

    risk_data = calculate_ai_risk(body.zone_id)
    premium_data = calculate_premium(body.zone_id, risk_data["risk_score"])

    users[mobile] = {
        "password": body.password.strip(),
        "name": body.name.strip() or f"User_{mobile[-4:]}",
        "zone_id": body.zone_id,
        "role": "user",
        "claims_count": 0,
        "premium": premium_data,
        "registered_at": datetime.datetime.now().isoformat(),
        "days_protected": 0,
        "payout_mtd": 0,
    }
    return {
        "success": True,
        "message": f"Welcome to PaySafe AI, {users[mobile]['name']}!",
        "zone": ZONES.get(body.zone_id, ZONES[4])["name"],
        "weekly_premium": premium_data["weekly_premium"],
    }


@app.post("/api/login")
def login(body: LoginRequest):
    mobile = body.mobile.strip()
    if mobile not in users:
        raise HTTPException(404, "Mobile not found. Register first.")
    if users[mobile]["password"] != body.password.strip():
        raise HTTPException(401, "Incorrect password.")

    u = users[mobile]
    # Seed admin account
    role = "admin" if mobile == "9999999999" else u.get("role", "user")

    return {
        "success": True,
        "name": u["name"],
        "mobile": mobile,
        "role": role,
        "zone_id": u["zone_id"],
        "zone_name": ZONES.get(u["zone_id"], ZONES[4])["name"],
        "premium": u["premium"],
        "claims_count": u["claims_count"],
        "payout_mtd": u.get("payout_mtd", 0),
        "days_protected": u.get("days_protected", 0),
    }


# ─── Dashboard ────────────────────────────────
@app.get("/api/dashboard/{mobile}")
def get_dashboard(mobile: str):
    if mobile not in users:
        raise HTTPException(404, "User not found.")
    u = users[mobile]
    zone_id = u["zone_id"]

    risk_data = calculate_ai_risk(zone_id)
    premium_data = calculate_premium(zone_id, risk_data["risk_score"])
    live_triggers = simulate_triggers()
    firing_triggers = [t for t in live_triggers if t["firing"]]

    # Alerts
    alerts = []
    for ft in firing_triggers:
        alerts.append({
            "type": "firing",
            "icon": ft["icon"],
            "message": f"{ft['name']} FIRED — {ft['current_value']}{ft['unit']} Zone {zone_id}",
            "sub": f"Payout processing · Expected in ~2 min",
        })
    if risk_data["aqi"] > 150:
        alerts.append({
            "type": "watching",
            "icon": "🟫",
            "message": f"AQI {risk_data['aqi']} watching threshold",
            "sub": f"Needs 3hr above 200 to trigger",
        })

    return {
        "success": True,
        "name": u["name"],
        "zone_id": zone_id,
        "zone_name": ZONES.get(zone_id, ZONES[4])["name"],
        "risk_score": risk_data["risk_score"],
        "risk_level": risk_data["risk_level"],
        "weather": risk_data["weather"],
        "weather_icon": risk_data["weather_icon"],
        "aqi": risk_data["aqi"],
        "weekly_premium": premium_data["weekly_premium"],
        "max_payout": premium_data["max_payout"],
        "payout_mtd": u.get("payout_mtd", 0),
        "days_protected": u.get("days_protected", 0),
        "alerts": alerts,
        "active_triggers": len(firing_triggers),
        "coverage": {
            "premium": premium_data["weekly_premium"],
            "max_payout": premium_data["max_payout"],
            "zone": ZONES.get(zone_id, ZONES[4])["name"],
            "week_progress": random.randint(40, 85),
            "week_day": f"Week 3 of 4 — Day {random.randint(1,7)}",
            "status": "ACTIVE",
        },
    }


# ─── Claims ────────────────────────────────────
@app.post("/api/claim")
def file_claim(body: ClaimRequest):
    global claim_counter
    mobile = body.mobile.strip()
    if mobile not in users:
        raise HTTPException(404, "User not found.")

    u = users[mobile]
    zone_id = u["zone_id"]

    # Step 1: AI Risk
    risk_data = calculate_ai_risk(zone_id)

    # Step 2: GPS Verification
    gps = verify_gps_zone(zone_id)

    # Step 3: Fraud Scoring
    fraud = calculate_fraud_score(mobile, u["claims_count"])

    # Step 4: Payout Calculation
    payout_result = calculate_payout(BASE_PAYOUT, risk_data["risk_level"], fraud["approved"])

    # Step 5: Store claim
    claim_counter += 1
    clm_id = f"CLM-{claim_counter}"
    now = datetime.datetime.now()

    status = "PAID" if fraud["approved"] else "BLOCKED"
    claim_record = {
        "claim_id": clm_id,
        "mobile": mobile,
        "name": u["name"],
        "zone_id": zone_id,
        "zone_name": gps["zone_name"],
        "timestamp": now.strftime("%d %b %Y, %H:%M"),
        "trigger_source": "OpenWeatherMap + IMD",
        "trigger_type": f"{risk_data['weather']} — Zone {zone_id}",
        "weather": risk_data["weather"],
        "weather_icon": risk_data["weather_icon"],
        "aqi": risk_data["aqi"],
        "risk_score": risk_data["risk_score"],
        "risk_level": risk_data["risk_level"],
        "gps_confirmed": gps["gps_confirmed"],
        "gps_zone_match": f"Confirmed — Zone {zone_id}" if gps["gps_confirmed"] else "Mismatch",
        "fraud_score": fraud["fraud_score"],
        "fraud_label": fraud["risk_label"],
        "payout": payout_result["amount"],
        "payout_status": status,
        "steps": [
            {"label": "Trigger Verified", "done": True},
            {"label": "GPS Confirmed", "done": gps["gps_confirmed"]},
            {"label": "Fraud Scored", "done": True},
            {"label": "Payout Queued", "done": fraud["approved"]},
            {"label": "UPI Sent", "done": status == "PAID"},
        ],
    }
    claims.append(claim_record)

    # Update user stats
    users[mobile]["claims_count"] += 1
    users[mobile]["payout_mtd"] = users[mobile].get("payout_mtd", 0) + payout_result["amount"]
    users[mobile]["days_protected"] = users[mobile].get("days_protected", 0) + 1

    return {
        "success": True,
        **claim_record,
    }


@app.get("/api/claims/{mobile}")
def get_user_claims(mobile: str):
    if mobile not in users:
        raise HTTPException(404, "User not found.")
    user_claims = [c for c in claims if c["mobile"] == mobile]
    return {"success": True, "claims": list(reversed(user_claims))}


# ─── Admin ─────────────────────────────────────
@app.get("/api/admin/claims")
def admin_get_all_claims():
    return {
        "success": True,
        "total": len(claims),
        "claims": list(reversed(claims[-50:])),  # last 50
    }


@app.get("/api/admin/users")
def admin_get_users():
    sanitized = []
    for mob, u in users.items():
        sanitized.append({
            "mobile": mob,
            "name": u["name"],
            "zone_id": u["zone_id"],
            "zone_name": ZONES.get(u["zone_id"], ZONES[4])["name"],
            "claims_count": u["claims_count"],
            "payout_mtd": u.get("payout_mtd", 0),
            "role": u.get("role", "user"),
        })
    return {"success": True, "total": len(sanitized), "users": sanitized}


# ─── Triggers ─────────────────────────────────
@app.get("/api/triggers")
def get_triggers():
    triggers = simulate_triggers()
    log = generate_trigger_log()
    firing = [t for t in triggers if t["firing"]]
    return {
        "success": True,
        "total": len(triggers),
        "firing_count": len(firing),
        "triggers": triggers,
        "live_log": log,
    }


@app.post("/api/triggers/simulate")
def simulate_trigger(body: SimulateTriggerRequest):
    """Force-fire a specific trigger for demo."""
    zone = ZONES.get(body.zone_id, ZONES[4])
    return {
        "success": True,
        "message": f"Trigger {body.trigger_id} simulated for {zone['name']}",
        "claims_queued": random.randint(280, 420),
        "estimated_payout": f"₹{random.randint(40000, 90000):,}",
        "processing_time": "~2 minutes",
    }


# ─── Seed admin account on startup ────────────
@app.on_event("startup")
def seed_admin():
    if "9999999999" not in users:
        users["9999999999"] = {
            "password": "admin123",
            "name": "Admin User",
            "zone_id": 4,
            "role": "admin",
            "claims_count": 0,
            "premium": {"weekly_premium": 0, "max_payout": 0, "zone_name": "All Zones"},
            "registered_at": datetime.datetime.now().isoformat(),
            "days_protected": 0,
            "payout_mtd": 0,
        }
        # Seed some sample claims
        sample_claims_data = [
            ("Heavy Rainfall", "⛈️", "High", 210, "PROCESSING", 4),
            ("Heatwave", "🔆", "Medium", 180, "PAID", 4),
            ("AQI Alert", "🟫", "Medium", 150, "PAID", 2),
        ]
        global claim_counter
        for trigger, icon, risk, payout, status, zone in sample_claims_data:
            claim_counter += 1
            claims.append({
                "claim_id": f"CLM-{claim_counter}",
                "mobile": "9999999999",
                "name": "Admin User",
                "zone_id": zone,
                "zone_name": ZONES[zone]["name"],
                "timestamp": "30 Mar 2025, 14:32",
                "trigger_source": "OpenWeatherMap + IMD",
                "trigger_type": f"{trigger} — Zone {zone}",
                "weather": trigger,
                "weather_icon": icon,
                "aqi": random.randint(100, 300),
                "risk_score": random.randint(40, 85),
                "risk_level": risk,
                "gps_confirmed": True,
                "gps_zone_match": f"Confirmed — Zone {zone}",
                "fraud_score": random.randint(5, 25),
                "fraud_label": "LOW RISK",
                "payout": payout,
                "payout_status": status,
                "steps": [
                    {"label": "Trigger Verified", "done": True},
                    {"label": "GPS Confirmed", "done": True},
                    {"label": "Fraud Scored", "done": True},
                    {"label": "Payout Queued", "done": True},
                    {"label": "UPI Sent", "done": status == "PAID"},
                ],
            }) 