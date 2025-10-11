Of course. Here is a comprehensive `README.md` file for your Brainstorm Buddy project.

-----

# 🧠 Brainstorm Buddy: Your AI-Powered Learning Companion

[](https://www.python.org/)
[](https://streamlit.io/)
[](https://opensource.org/licenses/MIT)

Brainstorm Buddy is an intelligent, all-in-one learning application designed to help users master any subject through a suite of AI-powered tools.

-----

## 🚀 Live Demo

You can access the live, deployed version of the application here:

**[https://aicte-ai-cloud-aipoweredstudytabreadme-ov-file-afawfvr8ysjptq6.streamlit.app/)** 
-----

## ✨ Key Features

  * **User Authentication**: Secure sign-up and login system to manage personal user data.
  * **Personalized Dashboard**: A central hub that tracks your study progress, daily streak, and skill mastery across different topics.
  * **🗺️ AI Study Planner**: Generate a structured, day-by-day learning roadmap for any topic to guide your studies.
  * **💬 AI Tutor Chat**: Get instant, detailed explanations for complex topics by chatting with an AI assistant that can use uploaded documents for context.
  * **🧩 Interactive Quizzes**: Test your knowledge with dynamically generated multiple-choice quizzes based on your study materials.
  * **🃏 Kinetic Flashcards & Spaced Repetition**: Create flashcard decks from your notes and master them using the scientifically-backed SM-2 spaced repetition algorithm to optimize memory retention.
  * **📝 Content Tools**:
      * **Explain a Topic**: Get simple, clear explanations of any topic or document.
      * **Summarize Notes**: Condense long texts or uploaded PDFs into concise, easy-to-review bullet points.
  * **🌐 Community Hub**: Share your flashcard decks with the community and study from decks created by other users.

-----

## 🛠️ Technical Architecture

Brainstorm Buddy is built with a modern Python stack, prioritizing a reactive user experience and robust backend logic.

  * **Frontend**: The entire user interface is built with **Streamlit**, featuring custom CSS for a polished, modern aesthetic.
  * **Database**:
      * **SQLite** serves as the lightweight, file-based database.
      * **SQLAlchemy** is used as the Object-Relational Mapper (ORM) for elegant and Pythonic database interactions.
  * **AI Integration**:
      * Powered by **Google's Gemini Pro** large language model.
      * A dedicated `AIClient` class abstracts all API calls, using carefully engineered prompts to ensure reliable JSON and text outputs.
  * **Core Libraries**: The project relies on `bcrypt` for secure password hashing, `PyPDF2` for PDF text extraction, and `python-dotenv` for environment management.

-----

## ⚙️ Getting Started

Follow these steps to run the project on your local machine.

### Prerequisites

  * Python 3.8+
  * `pip` package installer

### Installation

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/YourUsername/YourRepoName.git
    cd YourRepoName
    ```

2.  **Set Up a Virtual Environment** (Recommended)

    ```bash
    # Create the environment
    python -m venv venv

    # Activate it (macOS/Linux)
    source venv/bin/activate

    # Activate it (Windows)
    venv\Scripts\activate
    ```

3.  **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a file named `.env` in the root directory and add your Google Gemini API key:

    ```
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```

### Running the Application

Once the installation is complete, run the following command in your terminal:

```bash
streamlit run app.py
```

Your web browser will automatically open a new tab with the Brainstorm Buddy application running.

-----

## 🤝 Contributing

Contributions are welcome\! If you have suggestions for improvements or want to fix a bug, please feel free to fork the repository, make your changes, and open a pull request.

-----

## 📄 License


This project is licensed under the MIT License. See the `LICENSE` file for more details.

