from config import Config

def validate_inputs(data):
    destination = (data.get("destination") or "").strip()
    start_date = (data.get("start_date") or "").strip()
    duration_days = int(data.get("duration_days") or 0)
    budget_level = (data.get("budget_level") or "tight").strip().lower()
    interests = [i.strip().lower() for i in (data.get("interests") or "").split(",") if i.strip()]
    transport = (data.get("transport") or "bus/train").strip().lower()
    stay_type = (data.get("stay_type") or "hostel").strip().lower()
    currency = Config.DEFAULT_CURRENCY

    if not destination:
        return False, "Destination is required.", None
    if duration_days < Config.MIN_DAYS or duration_days > Config.MAX_DAYS:
        return False, f"Duration must be between {Config.MIN_DAYS} and {Config.MAX_DAYS} days.", None

    return True, "", {
        "destination": destination,
        "start_date": start_date,
        "duration_days": duration_days,
        "budget_level": budget_level,
        "interests": interests,
        "transport": transport,
        "stay_type": stay_type,
        "currency": currency
    }

def build_prompt(params):
    destination = params["destination"]
    duration = params["duration_days"]
    budget = params["budget_level"]
    interests = ", ".join(params["interests"]) if params["interests"] else "general sightseeing"
    transport = params["transport"]
    stay = params["stay_type"]
    currency = params["currency"]
    start_date = params["start_date"]

    return f"""
You are a student-focused travel planner. Create a budget-friendly {duration}-day itinerary for {destination} starting on {start_date or "an upcoming weekend"}.

Constraints:
- Budget level: {budget}.
- Interests: {interests}.
- Preferred transport: {transport}.
- Preferred stay: {stay}.
- Currency: {currency}.
- Prioritize free/low-cost highlights, student discounts, and safety.

Output format:
1) JSON fenced block with daily plan, meals, transport, accommodation, estimated costs, and tips.
2) Below JSON, a concise student-friendly summary (5-7 sentences).
"""