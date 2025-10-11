import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for the Brainstorm Buddy application."""
    
    # --- Gemini AI Configuration ---
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-2.5-flash" 

    # --- Application Limits ---
    MAX_TEXT_LENGTH = 10000 
    
    # --- Database Configuration ---
    DATABASE_URL = "sqlite:///brainstorm_buddy.db"