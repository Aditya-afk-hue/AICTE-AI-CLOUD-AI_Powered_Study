# config.py

import os

class Config:
    PROVIDER = os.environ.get("PROVIDER", "gemini").lower()

    GEMINI_API_KEY = "AIzaSyC4qYHrjZLRWLxHj4Yn5P-hjnEx6pN7Wr0"
    GEMINI_MODEL = "gemini-2.5-flash"

    # OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
    # OPENAI_MODEL = "gpt-4o-mini"

    DEFAULT_CURRENCY = "INR"
    MAX_DAYS = 14
    MIN_DAYS = 1
