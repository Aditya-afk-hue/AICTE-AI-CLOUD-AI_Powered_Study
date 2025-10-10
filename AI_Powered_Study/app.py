# app.py
import streamlit as st
import json
import re
import datetime
from PyPDF2 import PdfReader
from ai_client import AIClient
from study_planner import validate_text_input
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import OperationalError

# --- Database, Auth, and SRS Imports ---
from database import init_db, get_db, User, StudyTopic, QuizResult, FlashcardDeck, Flashcard, StudyRoadmap, RoadmapItem, KnowledgeNode, KnowledgeEdge, RoadmapProject
from auth import create_user, authenticate_user
from srs import update_card

# --- Initialize Database ---
init_db()
db_gen = get_db()
db: Session = next(db_gen)


# --- 1. AESTHETIC AND UI CONFIGURATION ---
st.set_page_config(page_title="Brainstorm Buddy", layout="wide", initial_sidebar_state="expanded")

# --- NEW & IMPROVED STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    /* --- General App Styling --- */
    html, body, [class*="st-"] {
        font-family: 'Poppins', sans-serif;
    }
    .stApp {
        background-color: #0F172A; /* Slate 900 */
    }
    .st-emotion-cache-16txtl3 {
        padding-top: 2rem;
    }
    
    /* --- Main Title --- */
    h1 {
        font-weight: 700;
        background: -webkit-linear-gradient(45deg, #38BDF8, #818CF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* --- Sidebar Styling --- */
    [data-testid="stSidebar"] {
        background-color: #1E293B; /* Slate 800 */
        border-right: 1px solid #334155; /* Slate 700 */
    }
    
    /* --- Main Content Button Styling --- */
    .stButton>button {
        border-radius: 0.5rem;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border: 2px solid #4F46E5;
        background-color: transparent;
        color: #F8FAFC;
        transition: all 0.2s ease-in-out;
        text-align: left !important; /* Ensures sidebar button text is aligned left */
    }
    .stButton>button:hover {
        background-color: #4F46E5;
        color: #FFFFFF;
        border-color: #4F46E5;
        box-shadow: 0 0 15px rgba(79, 70, 229, 0.5);
    }
    .stButton>button[kind="primary"] {
        background-color: #4F46E5;
        color: #FFFFFF;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #4338CA;
        border-color: #4338CA;
        box-shadow: 0 0 20px rgba(67, 56, 202, 0.6);
    }

    /* --- Container and Card Styling --- */
    [data-testid="stVerticalBlock"] .st-emotion-cache-12w0qpk, 
    [data-testid="stForm"], .st-chat-message {
        background-color: #1E293B; /* Slate 800 */
        border: 1px solid #334155; /* Slate 700 */
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* --- Metric Styling --- */
    [data-testid="stMetric"] {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 0.75rem;
        padding: 1rem;
        text-align: center;
    }
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #94A3B8; /* Slate 400 */
    }
    [data-testid="stMetricValue"] {
        font-size: 2.5rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    
    /* --- Progress Bar Styling --- */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #38BDF8, #818CF8);
    }
</style>
""", unsafe_allow_html=True)


# --- 2. APP CONSTANTS ---
TASK_OPTIONS = {
    "📊 Learning Dashboard": "fa-solid fa-chart-line",
    "🧠 Spaced Repetition Review": "fa-solid fa-brain",
    "🗺️ AI Study Planner": "fa-solid fa-map-signs",
    "🌐 Community Hub": "fa-solid fa-users",
    "---": "---",
    "💬 AI Tutor Chat": "fa-solid fa-comments",
    "✨ Explain a Topic": "fa-solid fa-lightbulb",
    "📝 Summarize Notes": "fa-solid fa-file-alt",
    "🧩 Interactive Quiz": "fa-solid fa-puzzle-piece",
    "🃏 Kinetic Flashcards": "fa-solid fa-layer-group"
}
TASK_MAP = {k.split(" ")[0].lower().replace("📊", "").replace("🧠", "").replace("🗺️", "").replace("🌐", "").replace("💬", "").replace("✨", "").replace("📝", "").replace("🧩", "").replace("🃏", ""): k for k, v in TASK_OPTIONS.items() if v != "---"}


# --- 3. INITIALIZE AI CLIENT ---
@st.cache_resource
def get_ai_client(): return AIClient()
client = get_ai_client()

# ==================================
# --- 4. AUTHENTICATION & MAIN FLOW ---
# ==================================

if 'user' not in st.session_state:
    st.title("Welcome to 🧠 Brainstorm Buddy")
    st.markdown("### Your personal AI-powered learning companion.")
    
    auth_cols = st.columns((1, 1.5), gap="large")
    with auth_cols[0]:
        choice = st.radio("Choose Action", ["Login", "Sign Up"], label_visibility="collapsed")

        if choice == "Login":
            st.header("Login to Your Account")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="aditya_ranjan")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
                if submitted:
                    user = authenticate_user(db, username, password)
                    if user:
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
        
        if choice == "Sign Up":
            st.header("Create a New Account")
            with st.form("signup_form"):
                new_username = st.text_input("Username", placeholder="Choose a unique username")
                new_password = st.text_input("Password", type="password", placeholder="Choose a strong password")
                submitted = st.form_submit_button("Sign Up", use_container_width=True, type="primary")
                if submitted:
                    if not new_username or not new_password:
                        st.error("Username and password cannot be empty.")
                    elif db.query(User).filter(User.username == new_username).first():
                        st.error("Username already exists.")
                    else:
                        create_user(db, new_username, new_password)
                        st.success("Account created successfully! Please log in.")
    with auth_cols[1]:
        st.write("") # Spacer
        # --- FIX: Replaced the broken GIF, updated `use_column_width` to `use_container_width` ---
        st.image("https://images.pexels.com/photos/7130475/pexels-photo-7130475.jpeg", use_container_width=True)

else:
    # --- 5. UTILITY FUNCTIONS ---
    def get_current_user_id():
        return st.session_state.user.id

    def extract_file_text(uploaded_file):
        if uploaded_file is None: return ""
        if uploaded_file.type == "text/plain": return uploaded_file.read().decode("utf-8")
        elif uploaded_file.type == "application/pdf":
            try:
                pdf, text = PdfReader(uploaded_file), ""
                for page in pdf.pages: text += page.extract_text() or ""
                return text
            except Exception: return ""
        return ""

    def extract_json_from_string(text):
        match = re.search(r"```json\s*([\s\S]*?)\s*```|([\s\S]*\[[\s\S]*\]|[\s\S]*\{[\s\S]*\})", text)
        if match: return match.group(1) if match.group(1) else match.group(2)
        return text
    
    def get_and_store_topic(content, is_explicit_topic=False):
        user_id = get_current_user_id()
        if is_explicit_topic:
            topic_title = content
        else:
            topic_prompt = f"Analyze the following text and provide a concise, 2-4 word topic title for it. Only return the title and nothing else.\n\nTEXT: \"\"\"{content[:1000]}\"\"\""
            topic_title = client.ask_gemini(topic_prompt).strip()
        
        new_topic = StudyTopic(topic_name=topic_title, user_id=user_id)
        db.add(new_topic)
        db.commit()
        return topic_title

    # --- 6. HEADER AND SIDEBAR NAVIGATION ---
    with st.sidebar:
        st.title(f"🧠 Brainstorm Buddy")
        st.markdown("---")
        st.success(f"Welcome, **{st.session_state.user.username}**!")
        if st.button("Logout"):
            del st.session_state.user
            st.rerun()
        st.markdown("---")
        st.subheader("AI Toolkit")

        if st.session_state.get("navigate_to"):
            st.session_state.current_task = st.session_state.pop("navigate_to")
        if 'current_task' not in st.session_state:
            st.session_state.current_task = "📊 Learning Dashboard"
        
        def set_current_task(task_name):
            """Callback function to update the current task and clear old state."""
            if st.session_state.current_task != task_name:
                st.session_state.current_task = task_name
                # Clear state from other tools to ensure a fresh start
                keys_to_clear = ['quiz_data', 'final_score_info', 'flashcards_data', 'review_queue', 'show_answer']
                for key in keys_to_clear:
                    st.session_state.pop(key, None)

        for task_name in TASK_OPTIONS.keys():
            if task_name == "---":
                st.markdown("---")
                continue
            
            st.button(
                label=task_name,
                key=f"nav_{task_name}",
                on_click=set_current_task,
                args=(task_name,),
                use_container_width=True,
                type="primary" if st.session_state.current_task == task_name else "secondary"
            )

    user_id = get_current_user_id()

    # ============================
    # --- 7. TASK IMPLEMENTATIONS ---
    # ============================

    # Main content title
    st.header(st.session_state.current_task)

    if st.session_state.current_task == "📊 Learning Dashboard":
        tasks_completed = db.query(StudyTopic).filter(StudyTopic.user_id == user_id).count()
        quizzes_passed = db.query(QuizResult).filter(QuizResult.user_id == user_id, QuizResult.is_passed == 1).count()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Topics Studied", tasks_completed)
        col2.metric("Quizzes Passed", quizzes_passed)
        col3.metric("Daily Streak", "🔥 1 Day")
        
        st.markdown("---")
        
        st.subheader("🏆 Skills Mastery")
        mastery_data = db.query(
            QuizResult.topic_name,
            func.avg(QuizResult.score * 100.0 / QuizResult.total_questions).label('avg_score')
        ).filter(QuizResult.user_id == user_id).group_by(QuizResult.topic_name).all()

        if not mastery_data:
            st.info("Complete quizzes on different topics to see your mastery levels here!")
        else:
            for topic, avg_score in mastery_data:
                avg_score = round(avg_score)
                if avg_score >= 80: level = "🟢 Mastered"
                elif avg_score >= 50: level = "🟡 Intermediate"
                else: level = "🔴 Beginner"
                st.write(f"**{topic}**")
                st.progress(int(avg_score), text=f"{level} ({avg_score}%)")
        
        st.markdown("---")
        
        st.subheader("🎯 Recommended Focus Areas")
        weak_topics = [t[0] for t in db.query(QuizResult.topic_name).filter(QuizResult.user_id == user_id, QuizResult.is_passed == 0).distinct().all()]
        
        if not weak_topics:
            st.info("Your focus areas will appear here after you score below 80% on a quiz!")
        else:
            st.write("Based on your quiz performance, you should review these topics:")
            for topic in weak_topics:
                with st.container(border=True):
                    st.warning(f"Review Recommended: **{topic}**")
                    t_col1, t_col2 = st.columns(2)
                    if t_col1.button(f"Explain '{topic}'", key=f"explain_{topic}", use_container_width=True):
                        st.session_state.navigate_to, st.session_state.prefill_topic = "✨ Explain a Topic", topic
                        st.rerun()
                    if t_col2.button(f"Quiz me on '{topic}'", key=f"quiz_{topic}", use_container_width=True):
                        st.session_state.navigate_to, st.session_state.prefill_topic = "🧩 Interactive Quiz", topic
                        st.rerun()

    elif st.session_state.current_task == "🧠 Spaced Repetition Review":
        due_cards = db.query(Flashcard).join(FlashcardDeck).filter(
            FlashcardDeck.user_id == user_id,
            Flashcard.next_review_date <= datetime.date.today()
        ).all()
        
        if 'review_queue' not in st.session_state:
            st.session_state.review_queue = due_cards
        
        if not st.session_state.review_queue:
            st.success("🎉 All done! You have no cards to review today.")
        else:
            st.info(f"You have **{len(st.session_state.review_queue)}** cards to review.")
            current_card = st.session_state.review_queue[0]
            
            with st.container(border=True):
                st.markdown(f"<div style='font-size: 24px; text-align: center; min-height: 100px; display: flex; align-items: center; justify-content: center;'>{current_card.front}</div>", unsafe_allow_html=True)
                
                if st.button("Show Answer", use_container_width=True, key="show_answer_btn"):
                    st.session_state.show_answer = True

                if st.session_state.get('show_answer'):
                    st.markdown("---")
                    st.markdown(f"<div style='font-size: 20px; text-align: center; color: #818CF8;'>{current_card.back}</div>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    st.write("How well did you remember?")
                    r_col1, r_col2, r_col3 = st.columns(3)
                    
                    def handle_review(quality_score):
                        update_card(current_card, quality_score)
                        db.commit()
                        st.session_state.review_queue.pop(0)
                        st.session_state.show_answer = False
                        st.rerun()

                    if r_col1.button("🟥 Hard", use_container_width=True): handle_review(0)
                    if r_col2.button("🟨 Good", use_container_width=True): handle_review(3)
                    if r_col3.button("🟩 Easy", use_container_width=True): handle_review(5)

    elif st.session_state.current_task == "💬 AI Tutor Chat":
        if "messages" not in st.session_state: st.session_state.messages = []
        for message in st.session_state.messages:
            with st.chat_message(message["role"]): st.markdown(message["content"])
        if prompt := st.chat_input("Ask your question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                response = client.ask_gemini(f"As an AI Tutor, answer the student's question: {prompt}")
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    elif st.session_state.current_task == "✨ Explain a Topic":
        default_topic = st.session_state.pop("prefill_topic", "")
        topic = st.text_input("What topic do you want to understand?", value=default_topic)
        if st.button("Explain Topic", use_container_width=True, type="primary"):
            is_valid, msg = validate_text_input(topic, "Topic")
            if not is_valid: st.error(msg)
            else:
                with st.spinner("🤖 AI is preparing an explanation..."):
                    explanation = client.explain_topic(topic)
                    get_and_store_topic(topic, is_explicit_topic=True)
                st.markdown(explanation)

    elif st.session_state.current_task == "📝 Summarize Notes":
        input_method = st.radio("Choose input:", ["Paste Text", "Upload File"], horizontal=True)
        notes = st.text_area("Paste notes:", height=300) if input_method == "Paste Text" else extract_file_text(st.file_uploader("Upload .txt or .pdf", type=["txt", "pdf"]))
        if st.button("Summarize", use_container_width=True, type="primary"):
            is_valid, msg = validate_text_input(notes, "Notes")
            if not is_valid: st.error(msg)
            else:
                with st.spinner("🤖 AI is distilling the key points..."):
                    summary = client.summarize_notes(notes)
                    get_and_store_topic(notes)
                st.markdown(summary)

    elif st.session_state.current_task == "🧩 Interactive Quiz":
        if 'quiz_data' not in st.session_state:
            default_topic = st.session_state.pop("prefill_topic", "")
            quiz_text = st.text_area("Paste text or enter a topic to be quizzed on.", height=250, value=default_topic)
            num_q = st.slider("Number of Questions:", 3, 10, 5)
            if st.button("Generate Quiz", use_container_width=True, type="primary"):
                is_valid, msg = validate_text_input(quiz_text, "Quiz Text")
                if not is_valid: st.error(msg)
                else:
                    with st.spinner("🤖 AI is crafting your quiz..."):
                        quiz_json_str = client.generate_quiz(quiz_text, num_q)
                        st.session_state.current_quiz_topic = get_and_store_topic(quiz_text)
                    try:
                        st.session_state.quiz_data = json.loads(extract_json_from_string(quiz_json_str))
                        st.session_state.user_answers = {}
                        st.rerun()
                    except json.JSONDecodeError:
                        st.error("AI returned an invalid format. Please try again.")
                        st.code(quiz_json_str)
        else:
            st.subheader(f"Quiz on: {st.session_state.get('current_quiz_topic', 'General Knowledge')}")
            with st.form("quiz_form"):
                for i, q in enumerate(st.session_state.quiz_data):
                    st.write(f"**{i+1}. {q['question']}**")
                    st.session_state.user_answers[i] = st.radio(f"Options for Q{i+1}", q["options"], key=f"q{i}", index=None, label_visibility="collapsed")
                
                if st.form_submit_button("Submit", use_container_width=True, type="primary"):
                    score = sum(1 for i, q in enumerate(st.session_state.quiz_data) if st.session_state.user_answers.get(i) == q["answer"])
                    total = len(st.session_state.quiz_data)
                    percent = int(100 * score / total) if total > 0 else 0
                    db.add(QuizResult(topic_name=st.session_state.current_quiz_topic, score=score, total_questions=total, is_passed=(1 if percent >= 80 else 0), user_id=user_id))
                    db.commit()
                    st.session_state.final_score_info = {"score": score, "total": total, "percent": percent}
                    del st.session_state.quiz_data
                    st.rerun()
                
        if 'final_score_info' in st.session_state:
            info = st.session_state.final_score_info
            st.success("🎉 Quiz Complete!")
            st.metric("Final Score", f"{info['score']}/{info['total']}", f"{info['percent']}%")
            if info['percent'] >= 80: st.balloons()
            if st.button("New Quiz"):
                del st.session_state.final_score_info
                st.rerun()
    
    elif st.session_state.current_task == "🃏 Kinetic Flashcards":
        fc_text = st.text_area("Paste notes or enter a topic:", height=250)
        num_c = st.slider("Number of Flashcards:", 3, 15, 5)
        if st.button("Generate Flashcards", use_container_width=True, type="primary"):
            is_valid, msg = validate_text_input(fc_text, "Flashcard Text")
            if not is_valid: st.error(msg)
            else:
                with st.spinner("🤖 AI is creating flashcards..."):
                    fc_json_str = client.generate_flashcards(fc_text, num_c)
                    st.session_state.flashcard_topic = get_and_store_topic(fc_text)
                try:
                    st.session_state.flashcards_data = json.loads(extract_json_from_string(fc_json_str))
                except json.JSONDecodeError:
                    st.error("AI returned invalid format. Please try again.")
                    st.code(fc_json_str)
        
        if 'flashcards_data' in st.session_state and st.session_state.flashcards_data:
            st.markdown("---")
            deck_topic = st.text_input("Deck Name", value=st.session_state.get("flashcard_topic", "Flashcard Deck"))
            is_public_deck = st.checkbox("Make this deck public for other users?", value=False)
            if st.button("💾 Save Deck", use_container_width=True, type="primary"):
                new_deck = FlashcardDeck(topic_name=deck_topic, user_id=user_id, is_public=is_public_deck)
                db.add(new_deck)
                for card in st.session_state.flashcards_data:
                    db.add(Flashcard(front=card['front'], back=card['back'], deck=new_deck))
                db.commit()
                st.success(f"Deck '{deck_topic}' saved! Study it in the 'Review' section.")
            
            st.subheader("Generated Flashcards Preview")
            for card in st.session_state.flashcards_data:
                with st.container(border=True):
                    st.markdown(f"**Front:** {card['front']}\n\n**Back:** {card['back']}")

    elif st.session_state.current_task == "🗺️ AI Study Planner":
        existing_roadmaps = db.query(StudyRoadmap).filter(StudyRoadmap.user_id == user_id).all()
        if not existing_roadmaps:
            st.write("Generate a structured, interactive study plan!")
            with st.form("planner_form"):
                topic = st.text_input("What topic do you want to master?", placeholder="e.g., Data Structures & Algorithms")
                days = st.number_input("How many days to learn?", 1, 30, 7)
                if st.form_submit_button("🗺️ Generate Plan", type="primary"):
                    is_valid, msg = validate_text_input(topic, "Topic")
                    if not is_valid: st.error(msg)
                    else:
                        with st.spinner("🤖 AI is designing your learning journey..."):
                            roadmap_json = client.generate_roadmap_json(topic, days)
                            try:
                                sub_topics = json.loads(extract_json_from_string(roadmap_json))
                                new_roadmap = StudyRoadmap(topic=topic, user_id=user_id)
                                db.add(new_roadmap)
                                for sub in sub_topics: db.add(RoadmapItem(sub_topic=sub, roadmap=new_roadmap))
                                db.commit()
                                get_and_store_topic(topic, is_explicit_topic=True)
                                st.success("Your plan is ready!")
                                st.rerun()
                            except json.JSONDecodeError:
                                st.error("AI returned invalid format. Please try again."); st.code(roadmap_json)
        else:
            roadmap = existing_roadmaps[-1]
            st.subheader(f"Your Roadmap: {roadmap.topic}")
            def toggle_completion(item_id):
                item = db.query(RoadmapItem).filter(RoadmapItem.id == item_id).first()
                if item: item.is_completed = not item.is_completed; db.commit()
            
            for item in roadmap.items:
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([0.1, 0.5, 0.2, 0.2])
                    with col1: 
                        st.checkbox("", item.is_completed, key=f"check_{item.id}", on_change=toggle_completion, args=(item.id,), label_visibility="collapsed")
                    with col2: 
                        if item.is_completed:
                            st.markdown(f"~~**{item.sub_topic}**~~")
                        else:
                            st.markdown(f"**{item.sub_topic}**")
                    with col3:
                        if st.button("✨ Explain", key=f"explain_{item.id}", use_container_width=True):
                            st.session_state.navigate_to, st.session_state.prefill_topic = "✨ Explain a Topic", item.sub_topic
                            st.rerun()
                    with col4:
                        if st.button("🧩 Quiz", key=f"quiz_{item.id}", use_container_width=True):
                            st.session_state.navigate_to, st.session_state.prefill_topic = "🧩 Interactive Quiz", item.sub_topic
                            st.rerun()
                            
            if st.button("Create a New Roadmap", use_container_width=True):
                for r in existing_roadmaps: db.delete(r)
                db.commit(); st.rerun()

    elif st.session_state.current_task == "🌐 Community Hub":
        st.write("Explore flashcard decks created by other users.")
        try:
            public_decks = db.query(FlashcardDeck).filter(FlashcardDeck.is_public == True).all()
        except OperationalError:
            st.error("⚠️ Database Schema Mismatch!")
            st.info("Your database file is out of sync with the new community features. To fix this, please delete the file 'brainstorm_buddy.db' and restart the application. This will create a fresh database with the correct structure. (Note: This will reset existing user data).")
            public_decks = [] # Set to empty list to prevent the app from crashing.

        if not public_decks:
            st.info("No public decks available. Create a deck and make it public to share!")
        else:
            for deck in public_decks:
                with st.container(border=True):
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        st.subheader(f"Deck: {deck.topic_name}")
                        st.caption(f"{len(deck.cards)} cards | Created by: {deck.user.username}")
                    with col2:
                        if st.button("Study Deck", key=f"study_{deck.id}", use_container_width=True):
                            st.success(f"Feature to clone and study decks coming soon!")

    # --- 8. FOOTER ---
    st.markdown("---")
    st.caption("🚀 Developed by Aditya Ranjan Samal | Powered by Gemini AI | © 2025")