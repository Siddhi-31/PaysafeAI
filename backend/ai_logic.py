import random
import datetime
import math

# ─────────────────────────────────────────────
# ZONE DEFINITIONS  (city zones like GigArmor)
# ─────────────────────────────────────────────
ZONES = {
    1: {"name": "Zone 1 – Whitefield",    "base_risk": 20, "base_premium": 60},
    2: {"name": "Zone 2 – Koramangala",   "base_risk": 35, "base_premium": 72},
    3: {"name": "Zone 3 – HSR Layout",    "base_risk": 30, "base_premium": 68},
    4: {"name": "Zone 4 – Marathahalli",  "base_risk": 55, "base_premium": 84},
    5: {"name": "Zone 5 – Hebbal",        "base_risk": 45, "base_premium": 76},
}

# ─────────────────────────────────────────────
# WEATHER ENGINE
# ─────────────────────────────────────────────
WEATHER_CONDITIONS = [
    {"label": "Clear",     "icon": "☀️",  "risk_weight": 0,  "trigger": False},
    {"label": "Cloudy",    "icon": "☁️",  "risk_weight": 10, "trigger": False},
    {"label": "Rainy",     "icon": "🌧️",  "risk_weight": 35, "trigger": False},
    {"label": "Heavy Rain","icon": "⛈️",  "risk_weight": 65, "trigger": True},
    {"label": "Stormy",    "icon": "🌩️",  "risk_weight": 80, "trigger": True},
    {"label": "Foggy",     "icon": "🌫️",  "risk_weight": 30, "trigger": False},
    {"label": "Heatwave",  "icon": "🔆",  "risk_weight": 50, "trigger": True},
]

# ─────────────────────────────────────────────
# TRIGGER ENGINE
# ─────────────────────────────────────────────
TRIGGERS = [
    {
        "id": "RAIN",
        "name": "Rainfall Trigger",
        "icon": "🌧️",
        "api_source": "OpenWeatherMap + IMD",
        "threshold_label": "50mm/hr",
        "threshold_value": 50,
        "unit": "mm/hr",
    },
    {
        "id": "AQI",
        "name": "AQI / Pollution Trigger",
        "icon": "🟫",
        "api_source": "CPCB AQI Feed + IQAir API",
        "threshold_label": "200 AQI",
        "threshold_value": 200,
        "unit": "AQI",
    },
    {
        "id": "HEAT",
        "name": "Heatwave Trigger",
        "icon": "🔆",
        "api_source": "IMD Heat Index API",
        "threshold_label": "40°C",
        "threshold_value": 40,
        "unit": "°C",
    },
    {
        "id": "FLOOD",
        "name": "Flood / Waterlog Trigger",
        "icon": "🌊",
        "api_source": "NDMA Flood Alerts",
        "threshold_label": "Alert Level 2",
        "threshold_value": 2,
        "unit": "level",
    },
    {
        "id": "WIND",
        "name": "High Wind Trigger",
        "icon": "💨",
        "api_source": "Weatherstack + IMD",
        "threshold_label": "60km/h",
        "threshold_value": 60,
        "unit": "km/h",
    },
]


def simulate_triggers() -> list:
    """Simulate live trigger values and statuses."""
    result = []
    for t in TRIGGERS:
        if t["id"] == "RAIN":
            current_val = round(random.uniform(10, 120), 1)
            threshold = t["threshold_value"]
        elif t["id"] == "AQI":
            current_val = random.randint(80, 380)
            threshold = t["threshold_value"]
        elif t["id"] == "HEAT":
            current_val = round(random.uniform(28, 48), 1)
            threshold = t["threshold_value"]
        elif t["id"] == "FLOOD":
            current_val = round(random.uniform(0, 3.5), 1)
            threshold = t["threshold_value"]
        else:  # WIND
            current_val = round(random.uniform(10, 100), 1)
            threshold = t["threshold_value"]

        firing = current_val >= threshold
        watching = (current_val >= threshold * 0.75) and not firing

        if firing:
            status = "FIRING"
        elif watching:
            status = "WATCHING"
        else:
            status = "NORMAL"

        # Generate a mini intensity bar (10 bars)
        bar_count = 10
        bars = []
        for i in range(bar_count):
            level = (i + 1) / bar_count
            val_pct = current_val / (threshold * 1.5)
            if level <= val_pct:
                if val_pct >= 0.85:
                    bars.append("red")
                elif val_pct >= 0.6:
                    bars.append("orange")
                else:
                    bars.append("yellow")
            else:
                bars.append("empty")

        result.append({
            **t,
            "current_value": current_val,
            "threshold": threshold,
            "status": status,
            "firing": firing,
            "watching": watching,
            "bars": bars,
        })
    return result


# ─────────────────────────────────────────────
# GPS / ZONE ENGINE
# ─────────────────────────────────────────────
def verify_gps_zone(zone_id: int) -> dict:
    """Simulate GPS geofence verification."""
    zone = ZONES.get(zone_id, ZONES[4])
    confirmed = random.random() > 0.08  # 92% GPS match rate
    flagged = not confirmed
    return {
        "zone_id": zone_id,
        "zone_name": zone["name"],
        "gps_confirmed": confirmed,
        "flagged_for_review": flagged,
        "coordinates": {
            "lat": round(12.9716 + random.uniform(-0.05, 0.05), 6),
            "lng": round(77.5946 + random.uniform(-0.05, 0.05), 6),
        },
    }


# ─────────────────────────────────────────────
# FRAUD SCORING ENGINE
# ─────────────────────────────────────────────
def calculate_fraud_score(mobile: str, claims_count: int = 0) -> dict:
    """ML-simulated fraud scoring."""
    base_score = random.randint(5, 40)
    # More claims = slightly higher fraud signal
    claim_penalty = min(claims_count * 3, 30)
    raw_score = base_score + claim_penalty
    fraud_score = min(raw_score, 95)

    if fraud_score < 25:
        risk_label = "LOW RISK"
        approved = True
    elif fraud_score < 55:
        risk_label = "MEDIUM RISK"
        approved = True
    else:
        risk_label = "HIGH RISK"
        approved = False

    return {
        "fraud_score": fraud_score,
        "risk_label": risk_label,
        "approved": approved,
        "signals": _generate_fraud_signals(fraud_score),
    }


def _generate_fraud_signals(score: int) -> list:
    all_signals = [
        "Claim frequency normal",
        "GPS location verified",
        "Device fingerprint matched",
        "Time pattern consistent",
        "No duplicate submissions",
        "Weather correlation valid",
    ]
    bad_signals = [
        "Multiple claims in 24h window",
        "GPS location mismatch",
        "Unusual claim time",
        "Device not recognized",
    ]
    signals = random.sample(all_signals, k=min(3, len(all_signals)))
    if score > 50:
        signals.append(random.choice(bad_signals))
    return signals


# ─────────────────────────────────────────────
# AI RISK ENGINE
# ─────────────────────────────────────────────
def calculate_ai_risk(zone_id: int = 4) -> dict:
    """Full AI risk calculation with zone, weather, AQI, time context."""
    zone = ZONES.get(zone_id, ZONES[4])

    # Weather
    weather_choice = random.choice(WEATHER_CONDITIONS)
    weather_risk = weather_choice["risk_weight"]

    # AQI
    aqi = random.randint(20, 380)
    if aqi <= 50:
        aqi_risk = 0
    elif aqi <= 100:
        aqi_risk = 10
    elif aqi <= 150:
        aqi_risk = 20
    elif aqi <= 200:
        aqi_risk = 35
    elif aqi <= 300:
        aqi_risk = 55
    else:
        aqi_risk = 70

    # Time
    hour = datetime.datetime.now().hour
    if 22 <= hour or hour < 5:
        time_risk, time_label = 40, "Night hours"
    elif 8 <= hour <= 10 or 17 <= hour <= 20:
        time_risk, time_label = 30, "Rush hour"
    elif 5 <= hour < 8:
        time_risk, time_label = 15, "Early morning"
    else:
        time_risk, time_label = 5, "Daytime"

    # Combine with zone base risk
    zone_risk = zone["base_risk"]
    risk_score = round(
        (weather_risk * 0.30)
        + (aqi_risk * 0.25)
        + (time_risk * 0.20)
        + (zone_risk * 0.25)
    )
    risk_score = max(0, min(100, risk_score))

    if risk_score < 30:
        risk_level = "Low"
    elif risk_score < 60:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return {
        "weather": weather_choice["label"],
        "weather_icon": weather_choice["icon"],
        "weather_triggers": weather_choice["trigger"],
        "aqi": aqi,
        "time_context": time_label,
        "zone_id": zone_id,
        "zone_name": zone["name"],
        "risk_score": risk_score,
        "risk_level": risk_level,
    }


# ─────────────────────────────────────────────
# PREMIUM ENGINE
# ─────────────────────────────────────────────
def calculate_premium(zone_id: int, risk_score: int) -> dict:
    """ML-calculated weekly premium based on zone + risk."""
    zone = ZONES.get(zone_id, ZONES[4])
    base = zone["base_premium"]
    multiplier = 1.0 + (risk_score / 200)  # 0–50% uplift
    weekly_premium = round(base * multiplier)
    max_payout = weekly_premium * 10
    return {
        "weekly_premium": weekly_premium,
        "max_payout": max_payout,
        "zone_name": zone["name"],
        "calculation": f"Zone {zone_id} ML-calculated",
    }


# ─────────────────────────────────────────────
# PAYOUT ENGINE
# ─────────────────────────────────────────────
def calculate_payout(base: float, risk_level: str, fraud_approved: bool = True) -> dict:
    if not fraud_approved:
        return {"amount": 0, "status": "BLOCKED", "reason": "Fraud risk too high"}

    multipliers = {"Low": 1.0, "Medium": 1.5, "High": 2.2}
    mult = multipliers.get(risk_level, 1.0)
    amount = round(base * mult)
    return {
        "amount": amount,
        "multiplier": mult,
        "status": "APPROVED",
        "reason": f"{risk_level} risk × {mult}x multiplier",
    }


# ─────────────────────────────────────────────
# LIVE TRIGGER LOG GENERATOR
# ─────────────────────────────────────────────
def generate_trigger_log() -> list:
    now = datetime.datetime.now()
    events = [
        {
            "time": (now - datetime.timedelta(minutes=random.randint(1, 5))).strftime("%H:%M:%S"),
            "type": "trigger",
            "icon": "🌧️",
            "message": f"Rainfall trigger FIRED — {random.randint(60, 100)}mm/hr Zone {random.randint(1,5)}",
            "sub": f"{random.randint(300, 400)} claims queued",
        },
        {
            "time": (now - datetime.timedelta(minutes=random.randint(6, 12))).strftime("%H:%M:%S"),
            "type": "gps",
            "icon": "📍",
            "message": f"GPS verification complete — {random.randint(320, 360)} valid",
            "sub": f"{random.randint(2, 8)} flagged for review",
        },
        {
            "time": (now - datetime.timedelta(minutes=random.randint(13, 20))).strftime("%H:%M:%S"),
            "type": "fraud",
            "icon": "🛡️",
            "message": f"Fraud scoring complete — {random.randint(300, 360)} low-risk",
            "sub": f"{random.randint(1, 5)} delayed",
        },
        {
            "time": (now - datetime.timedelta(minutes=random.randint(21, 30))).strftime("%H:%M:%S"),
            "type": "payout",
            "icon": "💸",
            "message": f"UPI payouts sent — ₹{random.randint(40000, 80000):,} disbursed",
            "sub": f"Avg ₹{random.randint(150, 250)} per claim",
        },
    ]
    return events