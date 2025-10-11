# study_planner.py
from config import Config

def validate_text_input(text, field_name="Text"):
    """
    Validate user-provided text input to ensure it's not empty and not too long.
    Returns a tuple: (is_valid: bool, message: str)
    """
    if not text or not str(text).strip():
        return False, f"{field_name} cannot be empty."
    
    # This 'if' statement now has an indented block below it.
    if len(str(text)) > getattr(Config, "MAX_TEXT_LENGTH", 4000):
        return False, f"{field_name} is too long. Limit to {Config.MAX_TEXT_LENGTH} characters."
    
    return True, "Valid input."