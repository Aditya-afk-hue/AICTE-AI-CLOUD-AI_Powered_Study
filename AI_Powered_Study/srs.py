# srs.py
import datetime
from database import Flashcard

def update_card(card: Flashcard, quality: int):
    """
    Updates a flashcard's SRS data based on the SM-2 algorithm.
    :param card: The SQLAlchemy Flashcard object.
    :param quality: The user's rating of their recall (0-5 scale).
                    A quality score of 0-2 is "Hard", 3-4 is "Good", and 5 is "Easy".
    """
    if quality < 3:
        # If the response quality is low, reset the learning process for this card.
        card.repetitions = 0
        card.interval = 1
    else:
        # If the response quality is good, calculate the new ease factor.
        # The ease factor determines how much the interval should increase.
        card.ease_factor = max(1.3, card.ease_factor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        
        # Calculate the next interval based on the number of repetitions.
        if card.repetitions == 0:
            card.interval = 1
        elif card.repetitions == 1:
            card.interval = 6
        else:
            card.interval = round(card.interval * card.ease_factor)
        
        card.repetitions += 1
        
    # Schedule the next review date by adding the new interval to today's date.
    card.next_review_date = datetime.date.today() + datetime.timedelta(days=card.interval)
    
    return card
