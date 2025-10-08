# Student AI Travel Planner (Streamlit + Gemini/OpenAI)

A beginner-friendly, student-focused travel planner that generates personalized, budget-aware itineraries using Streamlit and either Gemini or OpenAI. Designed for classroom use: modular, well-commented, and easy to tweak.

---

## Features

- **Student-centered:** Budget-aware plans, public transit emphasis, hostels/homestays, and safety tips.
- **AI provider switch:** Use either **Gemini** or **OpenAI** via a single config.
- **Streamlit UI:** Clean form to input destination, duration, budget, interests, transport, and stay.
- **Structured outputs:** Valid JSON itinerary + concise student-friendly summary.
- **Modular code:** Config, AI client, planner logic, and app separated for learning clarity.

---

## Prerequisites

- **API keys:** You need at least one of:
  - **Gemini API key:** From Google AI Studio. (or)
  - **OpenAI API key:** From OpenAI platform.
- **Environment:** Google Colab (recommended) or local Python 3.9+.
- **Packages:** streamlit, google-generativeai, openai.

---

## Quick start in Google Colab

1. **Install dependencies**
   ```python
   !pip -q install streamlit google-generativeai openai
   ```

2. **Set environment variables**
   ```python
   import os

   # Choose provider: "gemini" or "openai"
   os.environ["PROVIDER"] = "gemini"   # or "openai"

   # API keys (set at least one)
   os.environ["GEMINI_API_KEY"] = "YOUR_GEMINI_KEY"
   os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_KEY"
   ```

3. **Create config.py**
   ```python
   %%writefile config.py
   import os

   class Config:
       PROVIDER = os.environ.get("PROVIDER", "gemini").lower()

       # Gemini
       GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
       GEMINI_MODEL = "gemini-pro"  # safe default; change if you have access to 1.5 models

       # OpenAI
       OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
       OPENAI_MODEL = "gpt-4o-mini"

       DEFAULT_CURRENCY = "INR"
       MAX_DAYS = 14
       MIN_DAYS = 1
   ```

4. **Create ai_client.py**
   ```python
   %%writefile ai_client.py
   from config import Config
   import google.generativeai as genai
   from openai import OpenAI

   class AIClient:
       def __init__(self):
           self.provider = Config.PROVIDER
           if self.provider == "gemini":
               if not Config.GEMINI_API_KEY:
                   raise ValueError("Gemini API key not set.")
               genai.configure(api_key=Config.GEMINI_API_KEY)
               self.model = genai.GenerativeModel(Config.GEMINI_MODEL)

           elif self.provider == "openai":
               if not Config.OPENAI_API_KEY:
                   raise ValueError("OpenAI API key not set.")
               self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
               self.model = Config.OPENAI_MODEL
           else:
               raise ValueError("Unsupported provider.")

       def generate_itinerary(self, prompt):
           if self.provider == "gemini":
               resp = self.model.generate_content(prompt)
               text = getattr(resp, "text", "") or ""
               return self._extract_outputs(text)

           elif self.provider == "openai":
               completion = self.client.chat.completions.create(
                   model=self.model,
                   messages=[
                       {"role": "system", "content": "You are a helpful, budget-aware student travel planner."},
                       {"role": "user", "content": prompt}
                   ]
               )
               text = completion.choices[0].message.content
               return self._extract_outputs(text)

       def _extract_outputs(self, text):
           import json, re
           json_match = re.search(r"```json\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
           itinerary_json = {}
           if json_match:
               try:
                   itinerary_json = json.loads(json_match.group(1))
               except:
                   itinerary_json = {"error": "Failed to parse JSON"}
           summary_text = text[json_match.end():].strip() if json_match else text.strip()
           return {"itinerary_json": itinerary_json, "summary_text": summary_text}
   ```

5. **Create planner.py**
   ```python
   %%writefile planner.py
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
       start_date = params["start_date"] or "an upcoming weekend"

       return f"""
   You are a student-focused travel planner. Create a budget-friendly {duration}-day itinerary for {destination} starting on {start_date}.

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
   ```

6. **Create app.py (Streamlit UI)**
   ```python
   %%writefile app.py
   import streamlit as st
   from ai_client import AIClient
   from planner import validate_inputs, build_prompt

   st.set_page_config(page_title="Student AI Travel Planner", layout="wide")
   st.title("🎒 Student AI Travel Planner")

   with st.form("planner_form"):
       destination = st.text_input("Destination", placeholder="e.g., Ooty, Goa, Jaipur")
       start_date = st.date_input("Start date (optional)", value=None)
       duration_days = st.number_input("Duration (days)", min_value=1, max_value=14, value=3)
       budget_level = st.selectbox("Budget level", ["tight", "moderate", "flexible"])
       transport = st.selectbox("Preferred transport", ["bus/train", "shared cab", "flight"])
       stay_type = st.selectbox("Preferred stay", ["hostel", "homestay", "budget hotel"])
       interests = st.text_input("Interests (comma-separated)", placeholder="nature, food, culture, hiking")
       submitted = st.form_submit_button("Generate Itinerary")

   if submitted:
       ok, msg, normalized = validate_inputs({
           "destination": destination,
           "start_date": str(start_date) if start_date else "",
           "duration_days": int(duration_days),
           "budget_level": budget_level,
           "interests": interests,
           "transport": transport,
           "stay_type": stay_type
       })
       if not ok:
           st.error(msg)
       else:
           prompt = build_prompt(normalized)
           try:
               client = AIClient()
               result = client.generate_itinerary(prompt)
               st.subheader("📋 JSON Itinerary")
               st.json(result["itinerary_json"])
               st.subheader("📝 Student Summary")
               st.write(result["summary_text"])
           except Exception as e:
               st.error(f"Error: {e}")
   ```

7. **Run the Streamlit app**
   ```python
   !streamlit run app.py --server.port 8501 --server.headless true
   ```
   Colab will show a public link (proxied) to open the app.

---

## Running locally (Windows/macOS/Linux)

1. **Clone or create project files**  
   - Save the four files: `config.py`, `ai_client.py`, `planner.py`, `app.py`.

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install streamlit google-generativeai openai
   ```

4. **Set environment variables**
   - Windows (PowerShell):
     ```powershell
     $env:PROVIDER="gemini"    # or "openai"
     $env:GEMINI_API_KEY="YOUR_GEMINI_KEY"
     $env:OPENAI_API_KEY="YOUR_OPENAI_KEY"
     ```
   - macOS/Linux (bash):
     ```bash
     export PROVIDER="gemini"   # or "openai"
     export GEMINI_API_KEY="YOUR_GEMINI_KEY"
     export OPENAI_API_KEY="YOUR_OPENAI_KEY"
     ```

5. **Run**
   ```bash
   streamlit run app.py
   ```
   Streamlit will open on http://localhost:8501.

---

## Model selection tips (Gemini)

- **Common working IDs:**
  - **Text-only:** `gemini-pro` (safe default)
  - **Fast & cost-effective:** `gemini-1.5-flash`
  - **Latest quality:** `gemini-1.5-pro-latest`
- **If you see 404 model errors:**
  - Use `gemini-pro` first.
  - Your account/region may not have access to certain 1.5 models.
  - List available models:
    ```python
    import google.generativeai as genai
    genai.configure(api_key="YOUR_KEY")
    for m in genai.list_models():
        print(m.name, " -> ", m.supported_generation_methods)
    ```

---

## File structure

- **config.py:** Provider, model IDs, defaults (INR, min/max days).
- **ai_client.py:** Unified wrapper for Gemini/OpenAI + JSON extraction.
- **planner.py:** Validation and prompt builder.
- **app.py:** Streamlit UI with form and result display.

---

## Sample test

- **Destination:** Ooty  
- **Start date:** 2025-10-10  
- **Duration:** 3  
- **Budget level:** Tight  
- **Transport:** bus/train  
- **Stay:** hostel  
- **Interests:** nature, tea, viewpoints

Expected: Valid JSON itinerary with daily activities, per-day costs, total estimate, and a short summary focused on student budgets in INR.

---

## Troubleshooting

- **Error: File does not exist: app.py**
  - **Fix:** In Colab, use `%%writefile app.py` to create the file before `streamlit run`.

- **TypeError: validate_inputs() takes 1 positional argument but 7 were given**
  - **Fix:** Use the dict-based call:
    ```python
    ok, msg, normalized = validate_inputs({...})
    ```
    Or redefine `validate_inputs` to accept separate arguments.

- **Gemini 404 model not found**
  - **Fix:** Switch to `gemini-pro` or `gemini-1.5-flash`. Verify available models with `list_models()`.

- **OpenAI authentication errors**
  - **Fix:** Ensure `OPENAI_API_KEY` is set and your account has access to the chosen model (`gpt-4o-mini` recommended for cost-effectiveness).

- **Empty or invalid JSON in output**
  - **Fix:** The app expects the model to return a fenced JSON block. If parsing fails, try re-running with simpler interests or switch providers/models.

---

## Customization

- **Budget granularity:** Add a slider for daily budget caps and adjust estimates in the prompt.
- **Safety notes:** Include female-solo travel or group coordination tips in the prompt.
- **Export:** Add a button to download the JSON/summary as Markdown or PDF.
- **Destinations:** Pre-fill popular student trips (Chennai → Pondicherry, Kodaikanal, Hampi) in a select box.

---

If you’d like, I can provide a single-file version that embeds all modules inside `app.py` for the simplest Colab experience.
