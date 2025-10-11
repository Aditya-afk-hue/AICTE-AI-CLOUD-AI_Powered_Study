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
    
    /* --- NEW: QUIZ AND FLASHCARD STYLES --- */
    .quiz-option {
        transition: all 0.2s ease-in-out;
        border: 1px solid #334155;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .quiz-option:hover {
        background-color: #334155; /* Slate 700 */
        cursor: pointer;
    }
    .flashcard {
        perspective: 1000px;
        height: 250px;
        border-radius: 1rem;
    }
    .flashcard-inner {
        position: relative;
        width: 100%;
        height: 100%;
        text-align: center;
        transition: transform 0.6s;
        transform-style: preserve-3d;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    }
    .flashcard-front, .flashcard-back {
        position: absolute;
        width: 100%;
        height: 100%;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
        border-radius: 1rem;
        font-size: 1.5rem;
    }
    .flashcard-front {
        background: linear-gradient(135deg, #60A5FA, #3B82F6);
        color: white;
    }
    .flashcard-back {
        background: linear-gradient(135deg, #A78BFA, #8B5CF6);
        color: white;
        transform: rotateY(180deg);
    }

    /* --- FIX for Expander/Expander Icon Focus Ring --- */
    [data-testid="stExpander"] summary:focus,
    [data-testid="stExpander"] summary:focus-visible {
        outline: none !important;
        box-shadow: 0 0 0 2px #4F46E5; /* Custom focus ring using box-shadow */
        border-radius: 0.5rem;
    }

    /* --- FINAL FIX for Icon Text Bug --- */
    /* This robustly targets and hides Streamlit's default arrow icon container,
       which was incorrectly rendering as text. Your custom emoji will remain. */
    [data-testid="stExpander"] [data-testid="stExpanderHeader"] > :first-child {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)


# --- 2. APP CONSTANTS ---
# UI FIX: Simplified the task options to a list as the icon classes were not being used
TASK_OPTIONS = [
    "📊 Learning Dashboard",
    "🧠 Spaced Repetition Review",
    "🗺️ AI Study Planner",
    "🌐 Community Hub",
    "---",
    "💬 AI Tutor Chat",
    "✨ Explain a Topic",
    "📝 Summarize Notes",
    "🧩 Interactive Quiz",
    "🃏 Kinetic Flashcards"
]


# --- 3. INITIALIZE AI CLIENT ---
@st.cache_resource
def get_ai_client(): return AIClient()
client = get_ai_client()

# ==================================
# --- 4. AUTHENTICATION & MAIN FLOW ---
# ==================================

if 'user' not in st.session_state:
    auth_cols = st.columns((1, 1.5), gap="large")
    
    with auth_cols[0]:
        st.title("Welcome to 🧠 Brainstorm Buddy")
        st.markdown("### Your personal AI-powered learning companion.")
        st.write("") 

        choice = st.radio("Choose Action", ["Login", "Sign Up"], label_visibility="collapsed")

        if choice == "Login":
            st.header("Login to Your Account")
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="aditya_ranjan")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Login", type="primary", use_container_width=True)
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
                submitted = st.form_submit_button("Sign Up", type="primary", use_container_width=True)
                if submitted:
                    if not new_username or not new_password:
                        st.error("Username and password cannot be empty.")
                    elif db.query(User).filter(User.username == new_username).first():
                        st.error("Username already exists.")
                    else:
                        new_user = create_user(db, new_username, new_password)
                        st.session_state.user = new_user
                        st.success("Account created successfully! Welcome.")
                        st.rerun()
    with auth_cols[1]:
        st.write("<br><br><br><br>", unsafe_allow_html=True)
        st.subheader("Master Any Subject with AI")
        
        features = {
            "🧠 Personalized Learning Paths": "Generate custom study roadmaps tailored to your goals.",
            "🧩 Interactive Quizzes": "Test your knowledge with dynamic, AI-generated questions.",
            "🃏 Kinetic Flashcards": "Reinforce memory with our intelligent spaced repetition system.",
            "💬 24/7 AI Tutor": "Get instant explanations and answers to your toughest questions."
        }
        
        for title, description in features.items():
            with st.container(border=True):
                st.markdown(f"<h5>{title}</h5>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #94A3B8;'>{description}</p>", unsafe_allow_html=True)

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
        try:
            return uploaded_file.read().decode("utf-8")
        except:
            st.warning("Could not read the uploaded file as text. Only text-based files and PDFs are fully supported for content extraction.")
            return ""


    def extract_json_from_string(text):
        """Finds and extracts the first valid JSON object or array from a string."""
        match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
        if match:
            return match.group(1).strip()
        
        first_bracket = -1
        last_bracket = -1
        
        first_curly = text.find('{')
        first_square = text.find('[')
        
        if first_curly != -1 and (first_square == -1 or first_curly < first_square):
            first_bracket = first_curly
            last_bracket = text.rfind('}')
        elif first_square != -1:
            first_bracket = first_square
            last_bracket = text.rfind(']')

        if first_bracket != -1 and last_bracket != -1:
            return text[first_bracket : last_bracket + 1].strip()

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

    def calculate_daily_streak(user_id):
        """Calculates the user's daily study streak."""
        today = datetime.date.today()
        
        study_dates = db.query(func.date(StudyTopic.timestamp)).filter(
            StudyTopic.user_id == user_id
        ).distinct().order_by(func.date(StudyTopic.timestamp).desc()).all()
        
        study_dates = [d[0] for d in study_dates]
        
        if not study_dates:
            return 0

        if study_dates[0] not in [today, today - datetime.timedelta(days=1)]:
            return 0

        streak = 0
        expected_date = today
        
        if study_dates[0] == today - datetime.timedelta(days=1):
            expected_date = today - datetime.timedelta(days=1)

        for study_date in study_dates:
            if study_date == expected_date:
                streak += 1
                expected_date -= datetime.timedelta(days=1)
            else:
                break
                
        return streak

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
                keys_to_clear = ['quiz_data', 'final_score_info', 'flashcards_data', 'review_queue', 'show_answer', 'explain_topic_input', 'quiz_topic_input', 'current_question_index', 'score', 'user_answers', 'answer_submitted', 'current_flashcard_index', 'chat_file_context']
                for key in keys_to_clear:
                    st.session_state.pop(key, None)

        for task_name in TASK_OPTIONS:
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
        
        st.markdown("---")
        st.subheader("Contribute")
        st.markdown("Love this project? We're open source! Feel free to contribute on [GitHub](https://github.com/Aditya-afk-hue/).", unsafe_allow_html=True)


    user_id = get_current_user_id()

    # ============================
    # --- 7. TASK IMPLEMENTATIONS ---
    # ============================

    st.header(st.session_state.current_task)

    if st.session_state.current_task == "📊 Learning Dashboard":
        tasks_completed = db.query(StudyTopic).filter(StudyTopic.user_id == user_id).count()
        quizzes_passed = db.query(QuizResult).filter(QuizResult.user_id == user_id, QuizResult.is_passed == 1).count()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Topics Studied", tasks_completed)
        col2.metric("Quizzes Passed", quizzes_passed)
        streak = calculate_daily_streak(user_id)
        col3.metric("Daily Streak", f"🔥 {streak} Day{'s' if streak != 1 else ''}")
        st.markdown("---")
        
        st.subheader("🏆 Skills Mastery")
        mastery_data = db.query(QuizResult.topic_name, func.avg(QuizResult.score * 100.0 / QuizResult.total_questions).label('avg_score')).filter(QuizResult.user_id == user_id).group_by(QuizResult.topic_name).all()
        if not mastery_data:
            st.info("Complete quizzes on different topics to see your mastery levels here!")
        else:
            for topic, avg_score in mastery_data:
                avg_score = round(avg_score)
                level = "🟢 Mastered" if avg_score >= 80 else "🟡 Intermediate" if avg_score >= 50 else "🔴 Beginner"
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
                        st.session_state.navigate_to = "✨ Explain a Topic"
                        st.session_state.prefill_topic = topic
                        st.rerun()
                    if t_col2.button(f"Quiz me on '{topic}'", key=f"quiz_{topic}", use_container_width=True):
                        st.session_state.navigate_to = "🧩 Interactive Quiz"
                        st.session_state.prefill_topic = topic
                        st.rerun()

    elif st.session_state.current_task == "🧠 Spaced Repetition Review":
        due_cards = db.query(Flashcard).join(FlashcardDeck).filter(FlashcardDeck.user_id == user_id, Flashcard.next_review_date <= datetime.date.today()).all()
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
        uploaded_file = st.file_uploader("Upload a document for context (any type)", type=None, key="chat_uploader")
        if uploaded_file:
            with st.spinner("Reading file..."):
                file_context = extract_file_text(uploaded_file)
                st.session_state.chat_file_context = file_context
                st.info("File uploaded as context. Ask a question about it below.")

        if "messages" not in st.session_state: st.session_state.messages = []
        for message in st.session_state.messages:
            with st.chat_message(message["role"]): st.markdown(message["content"])

        if prompt := st.chat_input("Ask your question..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            with st.chat_message("assistant"):
                full_prompt = prompt
                if st.session_state.get("chat_file_context"):
                    context = st.session_state.chat_file_context
                    full_prompt = f"Using the following document as context:\n---\n{context}\n---\n\nAnswer the student's question: {prompt}"
                
                response = client.ask_gemini(f"As an AI Tutor, answer the student's question: {full_prompt}")
                st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})


    elif st.session_state.current_task == "✨ Explain a Topic":
        if "prefill_topic" in st.session_state:
            st.session_state.explain_topic_input = st.session_state.pop("prefill_topic")

        with st.form("explain_form"):
            st.subheader("Explain a Topic or Document")
            topic_from_text = st.text_area("Enter a topic, paste content, or ask a question to explain:", key="explain_topic_input")
            uploaded_file = st.file_uploader("Or upload a document to explain its contents", type=None)

            submitted = st.form_submit_button("Explain", type="primary", use_container_width=True)
            if submitted:
                final_content = ""
                if uploaded_file is not None:
                    final_content = extract_file_text(uploaded_file)
                else:
                    final_content = topic_from_text

                is_valid, msg = validate_text_input(final_content, "Content")
                if not is_valid: 
                    st.error(msg)
                else:
                    with st.spinner("🤖 AI is preparing an explanation..."):
                        explanation = client.explain_topic(final_content)
                        get_and_store_topic(final_content)
                    st.markdown(explanation)


    elif st.session_state.current_task == "📝 Summarize Notes":
        with st.form("summary_form"):
            st.subheader("Summarize Your Notes")
            notes_from_text = st.text_area("Paste notes here:", height=250)
            uploaded_file = st.file_uploader("Or upload a document to summarize", type=None)

            submitted = st.form_submit_button("Summarize", type="primary", use_container_width=True)
            if submitted:
                final_notes = ""
                if uploaded_file is not None:
                    final_notes = extract_file_text(uploaded_file)
                else:
                    final_notes = notes_from_text

                is_valid, msg = validate_text_input(final_notes, "Notes")
                if not is_valid: 
                    st.error(msg)
                else:
                    with st.spinner("🤖 AI is distilling the key points..."):
                        summary = client.summarize_notes(final_notes)
                        get_and_store_topic(final_notes)
                    st.markdown(summary)

    elif st.session_state.current_task == "🧩 Interactive Quiz":
        if 'quiz_data' not in st.session_state:
            if "prefill_topic" in st.session_state:
                st.session_state.quiz_topic_input = st.session_state.pop("prefill_topic")
            
            with st.form("quiz_generation_form"):
                st.subheader("Generate a New Quiz")
                quiz_text_from_area = st.text_area("Paste text or enter a topic to be quizzed on.", height=250, key="quiz_topic_input")
                uploaded_file = st.file_uploader("Or upload a document to generate a quiz from", type=None)
                
                num_q = st.slider("Number of Questions:", 3, 10, 5)
                submitted = st.form_submit_button("Generate Quiz", type="primary", use_container_width=True)
                if submitted:
                    final_quiz_text = ""
                    if uploaded_file is not None:
                        final_quiz_text = extract_file_text(uploaded_file)
                    else:
                        final_quiz_text = quiz_text_from_area
                    
                    is_valid, msg = validate_text_input(final_quiz_text, "Quiz Text")
                    if not is_valid:
                        st.error(msg)
                    else:
                        with st.spinner("🤖 AI is crafting your quiz..."):
                            quiz_json_str = client.generate_quiz(final_quiz_text, num_q)
                            st.session_state.current_quiz_topic = get_and_store_topic(final_quiz_text)
                        try:
                            st.session_state.quiz_data = json.loads(extract_json_from_string(quiz_json_str))
                            st.session_state.current_question_index = 0
                            st.session_state.score = 0
                            st.session_state.user_answers = [None] * len(st.session_state.quiz_data)
                            st.session_state.answer_submitted = False
                            st.rerun()
                        except (json.JSONDecodeError, TypeError):
                            st.error("AI returned an invalid format. Please try again.")
                            st.code(quiz_json_str)
        
        elif 'final_score_info' not in st.session_state:
            st.subheader(f"Quiz on: {st.session_state.get('current_quiz_topic', 'General Knowledge')}")
            
            progress = st.session_state.current_question_index / len(st.session_state.quiz_data)
            st.progress(progress, text=f"Question {st.session_state.current_question_index + 1}/{len(st.session_state.quiz_data)}")

            q = st.session_state.quiz_data[st.session_state.current_question_index]

            with st.container(border=True):
                st.subheader(f"Question {st.session_state.current_question_index + 1}")
                st.markdown(f"**{q['question']}**")

                for i, option in enumerate(q["options"]):
                    is_correct = (option == q["answer"])
                    is_selected = (st.session_state.user_answers[st.session_state.current_question_index] == option)
                    
                    button_type = "secondary"
                    if st.session_state.answer_submitted:
                        if is_correct: button_type = "primary"
                        elif is_selected: button_type = "secondary"
                    
                    if st.button(option, key=f"q_{st.session_state.current_question_index}_{i}", use_container_width=True, type=button_type, disabled=st.session_state.answer_submitted):
                        st.session_state.user_answers[st.session_state.current_question_index] = option
                        st.session_state.answer_submitted = True
                        if is_correct:
                            st.session_state.score += 1
                        st.rerun()

            if st.session_state.answer_submitted:
                user_answer = st.session_state.user_answers[st.session_state.current_question_index]
                if user_answer == q["answer"]:
                    st.success("Correct!")
                else:
                    st.error(f"Incorrect. The correct answer was: {q['answer']}")
                
                if st.session_state.current_question_index < len(st.session_state.quiz_data) - 1:
                    if st.button("Next Question →", use_container_width=True, type="primary"):
                        st.session_state.current_question_index += 1
                        st.session_state.answer_submitted = False
                        st.rerun()
                else:
                    if st.button("Finish Quiz", use_container_width=True, type="primary"):
                        total = len(st.session_state.quiz_data)
                        score = st.session_state.score
                        percent = int(100 * score / total) if total > 0 else 0
                        db.add(QuizResult(topic_name=st.session_state.current_quiz_topic, score=score, total_questions=total, is_passed=(1 if percent >= 80 else 0), user_id=user_id))
                        db.commit()
                        st.session_state.final_score_info = {"score": score, "total": total, "percent": percent}
                        st.rerun()

        else:
            info = st.session_state.final_score_info
            st.balloons()
            st.success("🎉 Quiz Complete!")

            score_cols = st.columns(3)
            with score_cols[0]: st.metric("Correct", f"{info['score']}")
            with score_cols[1]: st.metric("Incorrect", f"{info['total'] - info['score']}")
            with score_cols[2]: st.metric("Final Score", f"{info['percent']}%")

            if st.button("⬅️ Take a New Quiz", use_container_width=True):
                keys_to_clear = ['quiz_data', 'final_score_info', 'current_question_index', 'score', 'user_answers', 'answer_submitted']
                for key in keys_to_clear:
                    st.session_state.pop(key, None)
                st.rerun()
    
    elif st.session_state.current_task == "🃏 Kinetic Flashcards":
        if 'flashcards_data' not in st.session_state:
            with st.form("flashcard_form"):
                st.subheader("Generate New Flashcards")
                fc_text_from_area = st.text_area("Paste notes or enter a topic:", height=250)
                uploaded_file = st.file_uploader("Or upload a document to generate flashcards from", type=None)

                num_c = st.slider("Number of Flashcards:", 3, 15, 5)
                submitted = st.form_submit_button("Generate Flashcards", type="primary", use_container_width=True)
                if submitted:
                    final_fc_text = ""
                    if uploaded_file is not None:
                        final_fc_text = extract_file_text(uploaded_file)
                    else:
                        final_fc_text = fc_text_from_area
                    
                    is_valid, msg = validate_text_input(final_fc_text, "Flashcard Text")
                    if not is_valid: 
                        st.error(msg)
                    else:
                        with st.spinner("🤖 AI is creating flashcards..."):
                            fc_json_str = client.generate_flashcards(final_fc_text, num_c)
                            st.session_state.flashcard_topic = get_and_store_topic(final_fc_text)
                        try:
                            st.session_state.flashcards_data = json.loads(extract_json_from_string(fc_json_str))
                            st.session_state.current_flashcard_index = 0
                            st.session_state.card_flipped = False
                            st.rerun()
                        except (json.JSONDecodeError, TypeError):
                            st.error("AI returned an invalid format. Please try again.")
                            st.code(fc_json_str)
        
        else:
            if not st.session_state.flashcards_data:
                st.info("No flashcards generated yet.")
            else:
                st.subheader("Generated Flashcards Preview")
                
                total_cards = len(st.session_state.flashcards_data)
                card_index = st.session_state.get('current_flashcard_index', 0)
                current_card = st.session_state.flashcards_data[card_index]

                transform_style = "transform: rotateY(180deg);" if st.session_state.get('card_flipped', False) else ""

                st.markdown(f"""
                <div class="flashcard">
                    <div class="flashcard-inner" style="{transform_style}">
                        <div class="flashcard-front">{current_card['front']}</div>
                        <div class="flashcard-back">{current_card['back']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("") # Spacer

                if st.button("Flip Card", use_container_width=True):
                    st.session_state.card_flipped = not st.session_state.get('card_flipped', False)
                    st.rerun()
                
                nav_cols = st.columns([1, 1, 1])
                with nav_cols[0]:
                    if st.button("◀️ Previous", use_container_width=True, disabled=(card_index == 0)):
                        st.session_state.current_flashcard_index -= 1
                        st.session_state.card_flipped = False
                        st.rerun()
                with nav_cols[1]:
                    st.markdown(f"<p style='text-align: center; color: white;'>Card {card_index + 1} of {total_cards}</p>", unsafe_allow_html=True)

                with nav_cols[2]:
                    if st.button("Next ▶️", use_container_width=True, disabled=(card_index == total_cards - 1)):
                        st.session_state.current_flashcard_index += 1
                        st.session_state.card_flipped = False
                        st.rerun()
                
                st.markdown("---")

                with st.form("save_deck_form"):
                    st.subheader("Save Deck to Collection")
                    deck_topic = st.text_input("Deck Name", value=st.session_state.get("flashcard_topic", "Flashcard Deck"))
                    is_public_deck = st.checkbox("Make this deck public for other users?", value=False)
                    
                    submitted = st.form_submit_button("Save to My Decks", type="primary", use_container_width=True)
                    if submitted:
                        new_deck = FlashcardDeck(topic_name=deck_topic, user_id=user_id, is_public=is_public_deck)
                        db.add(new_deck)
                        db.flush()
                        
                        for card in st.session_state.flashcards_data:
                            db.add(Flashcard(front=card['front'], back=card['back'], deck_id=new_deck.id))
                        
                        db.commit()
                        st.success(f"Deck '{deck_topic}' saved! Study it in the 'Review' section.")
                        
                        keys_to_clear = ['flashcards_data', 'current_flashcard_index', 'card_flipped']
                        for key in keys_to_clear:
                            st.session_state.pop(key, None)
                        st.stop()


    elif st.session_state.current_task == "🗺️ AI Study Planner":
        existing_roadmaps = db.query(StudyRoadmap).filter(StudyRoadmap.user_id == user_id).all()
        if not existing_roadmaps:
            st.write("Generate a structured, interactive study plan!")
            with st.form("planner_form"):
                topic = st.text_input("What topic do you want to master?", placeholder="e.g., Data Structures & Algorithms")
                days = st.number_input("How many days to learn?", 1, 30, 7)
                if st.form_submit_button("🗺️ Generate Plan", type="primary", use_container_width=True):
                    is_valid, msg = validate_text_input(topic, "Topic")
                    if not is_valid: st.error(msg)
                    else:
                        with st.spinner("🤖 AI is designing your learning journey..."):
                            roadmap_json = client.generate_roadmap_json(topic, days)
                            try:
                                roadmap_data = json.loads(extract_json_from_string(roadmap_json))
                                new_roadmap = StudyRoadmap(topic=topic, user_id=user_id)
                                db.add(new_roadmap)
                                db.flush()
                                
                                for day_str, topics_for_day in roadmap_data.items():
                                    day_num_match = re.search(r'\d+', day_str)
                                    if not day_num_match: continue
                                    day_num = int(day_num_match.group())
                                    
                                    for sub_topic in topics_for_day:
                                        db.add(RoadmapItem(sub_topic=sub_topic, roadmap_id=new_roadmap.id, day_number=day_num))
                                
                                db.commit()
                                get_and_store_topic(topic, is_explicit_topic=True)
                                st.success("Your plan is ready!")
                                st.rerun()
                            except (json.JSONDecodeError, AttributeError, TypeError, OperationalError) as e:
                                st.error(f"AI returned an invalid format or a database error occurred. Please try again. Error: {e}"); st.code(roadmap_json)
        else:
            roadmap = existing_roadmaps[-1]
            st.subheader(f"Your Roadmap: {roadmap.topic}")

            def toggle_completion(item_id):
                item = db.query(RoadmapItem).filter(RoadmapItem.id == item_id).first()
                if item: item.is_completed = not item.is_completed; db.commit()
            
            items_by_day = {}
            if roadmap.items:
                 for item in sorted(roadmap.items, key=lambda x: x.day_number if x.day_number is not None else -1):
                    if item.day_number not in items_by_day:
                        items_by_day[item.day_number] = []
                    items_by_day[item.day_number].append(item)

            for day_num in sorted(items_by_day.keys()):
                # UI FIX: Added a calendar icon to the expander to fix rendering bugs
                with st.expander(f"**Day {day_num}**", expanded=True, icon="🗓️"):
                    for item in items_by_day[day_num]:
                        with st.container(border=True):
                            col1, col2, col3, col4 = st.columns([0.1, 0.5, 0.2, 0.2])
                            with col1: 
                                st.checkbox("", item.is_completed, key=f"check_{item.id}", on_change=toggle_completion, args=(item.id,), label_visibility="collapsed")
                            with col2: 
                                st.markdown(f"~~**{item.sub_topic}**~~" if item.is_completed else f"**{item.sub_topic}**")
                            with col3:
                                if st.button("✨ Explain", key=f"explain_{item.id}", use_container_width=True):
                                    st.session_state.navigate_to = "✨ Explain a Topic"
                                    st.session_state.prefill_topic = item.sub_topic
                                    st.rerun()
                            with col4:
                                if st.button("🧩 Quiz", key=f"quiz_{item.id}", use_container_width=True):
                                    st.session_state.navigate_to = "🧩 Interactive Quiz"
                                    st.session_state.prefill_topic = item.sub_topic
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
            public_decks = []

        if not public_decks:
            st.info("No public decks available yet. Create a deck and make it public to share with the community!")
        else:
            for deck in public_decks:
                with st.container(border=True):
                    col1, col2 = st.columns([0.8, 0.2])
                    with col1:
                        st.subheader(f"Deck: {deck.topic_name}")
                        creator = deck.user.username if deck.user else "Unknown"
                        st.caption(f"{len(deck.cards)} cards | Created by: {creator}")
                    with col2:
                        if st.button("Study Deck", key=f"study_{deck.id}", use_container_width=True):
                            cloned_deck = FlashcardDeck(
                                topic_name=deck.topic_name,
                                user_id=user_id,
                                is_public=False
                            )
                            db.add(cloned_deck)
                            db.flush()

                            for card in deck.cards:
                                db.add(Flashcard(
                                    front=card.front,
                                    back=card.back,
                                    deck_id=cloned_deck.id
                                ))
                            
                            db.commit()
                            st.success(f"Deck '{deck.topic_name}' was added to your collection!")

    # --- 8. FOOTER ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("🚀 Developed by Brainstorm Buddy team | Powered by Gemini AI | © 2025")
