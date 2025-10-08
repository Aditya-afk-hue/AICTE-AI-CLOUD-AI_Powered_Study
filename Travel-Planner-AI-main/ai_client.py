# ai_client.py
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
            text = resp.text or ""
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