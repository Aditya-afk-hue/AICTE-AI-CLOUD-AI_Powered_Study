# database.py
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, Date
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

DATABASE_URL = "sqlite:///brainstorm_buddy.db"
Base = declarative_base()

# --- Existing Models ---
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    topics = relationship("StudyTopic", back_populates="user")
    quiz_results = relationship("QuizResult", back_populates="user")
    decks = relationship("FlashcardDeck", back_populates="user")
    roadmaps = relationship("StudyRoadmap", back_populates="user")
    # ADDED RELATIONSHIP FOR QUIZ COLLECTIONS
    quiz_collections = relationship("QuizCollection", back_populates="user")

class StudyTopic(Base):
    __tablename__ = "study_topics"
    id = Column(Integer, primary_key=True, index=True)
    topic_name = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="topics")

class QuizResult(Base):
    __tablename__ = "quiz_results"
    id = Column(Integer, primary_key=True, index=True)
    topic_name = Column(String, index=True)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    is_passed = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="quiz_results")

# --- NEW MODELS FOR SAVING QUIZZES ---
class QuizCollection(Base):
    __tablename__ = "quiz_collections"
    id = Column(Integer, primary_key=True, index=True)
    topic_name = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    is_public = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="quiz_collections")
    questions = relationship("QuizQuestion", back_populates="collection", cascade="all, delete-orphan")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    # Storing options as a JSON string
    options = Column(Text, nullable=False) 
    correct_answer = Column(String, nullable=False)
    collection_id = Column(Integer, ForeignKey("quiz_collections.id"))
    
    collection = relationship("QuizCollection", back_populates="questions")
# ----------------------------------------

class FlashcardDeck(Base):
    __tablename__ = "flashcard_decks"
    id = Column(Integer, primary_key=True, index=True)
    topic_name = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    is_public = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="decks")
    cards = relationship("Flashcard", back_populates="deck", cascade="all, delete-orphan")

class Flashcard(Base):
    __tablename__ = "flashcards"
    id = Column(Integer, primary_key=True, index=True)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    next_review_date = Column(Date, default=datetime.date.today, nullable=False)
    interval = Column(Integer, default=1)
    ease_factor = Column(Float, default=2.5)
    repetitions = Column(Integer, default=0)
    deck_id = Column(Integer, ForeignKey("flashcard_decks.id"))
    
    deck = relationship("FlashcardDeck", back_populates="cards")

class StudyRoadmap(Base):
    __tablename__ = "study_roadmaps"
    id = Column(Integer, primary_key=True)
    topic = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="roadmaps")
    items = relationship("RoadmapItem", back_populates="roadmap", cascade="all, delete-orphan")
    project = relationship("RoadmapProject", back_populates="roadmap", uselist=False, cascade="all, delete-orphan")

class RoadmapItem(Base):
    __tablename__ = "roadmap_items"
    id = Column(Integer, primary_key=True)
    sub_topic = Column(String)
    is_completed = Column(Boolean, default=False)
    roadmap_id = Column(Integer, ForeignKey("study_roadmaps.id"))
    day_number = Column(Integer, nullable=False)
    
    roadmap = relationship("StudyRoadmap", back_populates="items")

class RoadmapProject(Base):
    __tablename__ = 'roadmap_projects'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    roadmap_id = Column(Integer, ForeignKey('study_roadmaps.id'), unique=True)
    
    roadmap = relationship("StudyRoadmap", back_populates="project")

class KnowledgeNode(Base):
    __tablename__ = 'knowledge_nodes'
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    source_edges = relationship("KnowledgeEdge", foreign_keys="[KnowledgeEdge.source_id]", back_populates="source_node", cascade="all, delete-orphan")
    target_edges = relationship("KnowledgeEdge", foreign_keys="[KnowledgeEdge.target_id]", back_populates="target_node", cascade="all, delete-orphan")

class KnowledgeEdge(Base):
    __tablename__ = 'knowledge_edges'
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey('knowledge_nodes.id'), nullable=False)
    target_id = Column(Integer, ForeignKey('knowledge_nodes.id'), nullable=False)
    label = Column(String, nullable=False) 

    source_node = relationship("KnowledgeNode", foreign_keys=[source_id], back_populates="source_edges")
    target_node = relationship("KnowledgeNode", foreign_keys=[target_id], back_populates="target_edges")


# --- Database Engine and Session ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
