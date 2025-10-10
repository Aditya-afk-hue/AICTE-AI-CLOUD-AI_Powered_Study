# config.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    """
    Configuration class to hold settings and environment variables.
    It does not import any other project files to prevent circular imports.
    """
    # [cite_start]Load the Gemini API key from the environment variable [cite: 1]
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Define the AI model to use. 
    # Switched to a stable, widely available model to prevent access issues.
    GEMINI_MODEL = "gemini-2.5-flash"
    
    # Define a maximum character limit for text inputs
    MAX_TEXT_LENGTH = 100000