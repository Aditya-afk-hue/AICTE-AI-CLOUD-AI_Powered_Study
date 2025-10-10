# ai_client.py
import google.generativeai as genai
from config import Config
import re

class AIClient:
    def __init__(self):
        """Initializes the AI client with the Gemini API configuration."""
        if not Config.GEMINI_API_KEY:
            raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in environment.")
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_MODEL)

    def _extract_text(self, response):
        """Extracts reliable text output from any Gemini response structure."""
        # ... (this function remains the same)
        if not response:
            return "⚠️ No response received from Gemini."
        if hasattr(response, "text") and response.text:
            return response.text.strip()
        try:
            candidates = getattr(response, "candidates", [])
            for cand in candidates:
                parts = getattr(cand.content, "parts", [])
                text_segments = []
                for p in parts:
                    if isinstance(p, dict) and "text" in p:
                        text_segments.append(p["text"])
                    elif hasattr(p, "text"):
                        text_segments.append(p.text)
                if text_segments:
                    return "\n".join(text_segments).strip()
        except Exception as e:
            print(f"[DEBUG] Error extracting parts: {e}")
        return str(response)


    def ask_gemini(self, prompt):
        """Sends a prompt to the Gemini model and returns the extracted text."""
        try:
            response = self.model.generate_content(prompt)
            return self._extract_text(response)
        except Exception as e:
            return f"❌ Gemini API Error: {e}"
            
    def generate_roadmap_json(self, topic, days):
        # ... (this function remains the same)
        prompt = f"""
        You are a curriculum planning expert who only speaks JSON.
        Your task is to generate a structured learning roadmap.

        **Instructions:**
        1. Create a learning plan for the topic "{topic}" to be completed in {days} days.
        2. Break the main topic down into a list of 10 to 15 logical, ordered sub-topics that can be learned sequentially.
        3. The output MUST be a valid JSON array of strings (e.g., `["Introduction to Python", "Variables and Data Types", "Control Flow"]`).
        4. CRITICAL: Do NOT include any introductory text, concluding text, explanations, or markdown formatting like ```json.
        5. The entire response must be a single JSON array starting with `[` and ending with `]`.
        """
        return self.ask_gemini(prompt)


    def explain_topic(self, topic):
        # ... (this function remains the same)
        prompt = f"Explain the topic '{topic}' in simple terms for a student. Include examples and analogies."
        return self.ask_gemini(prompt)

    def summarize_notes(self, text):
        # ... (this function remains the same)
        prompt = f"Summarize the following study notes into short, clear bullet points for revision:\n\n{text}"
        return self.ask_gemini(prompt)

    def generate_quiz(self, text, num_questions=5):
        # ... (this function remains the same)
        prompt = f"""
        You are a strict JSON quiz generation API. Your only function is to generate a valid JSON array of quiz questions based on the provided text.

        **Instructions:**
        1. Generate exactly {num_questions} multiple-choice questions from the content below.
        2. The output MUST be a valid JSON array (`[...]`).
        3. Each object in the array MUST have three keys: "question" (string), "options" (an array of exactly 4 strings), and "answer" (string, which must be one of the options).
        4. CRITICAL: Do NOT include any introductory text, concluding text, explanations, or markdown formatting like ```json.
        5. The entire response must start with `[` and end with `]`, and nothing else.

        **Content to analyze:**
        ---
        {text}
        ---
        """
        return self.ask_gemini(prompt)


    def generate_flashcards(self, text, num_cards=5):
        # ... (this function remains the same)
        prompt = f"""
        You are a strict JSON flashcard generation API. Your only function is to generate a valid JSON array of flashcards based on the provided text.

        **Instructions:**
        1. Generate exactly {num_cards} flashcards from the content below.
        2. The output MUST be a valid JSON array (`[...]`).
        3. Each object in the array MUST have two keys: "front" (string for the question or term) and "back" (string for the answer or definition).
        4. CRITICAL: Do NOT include any introductory text, concluding text, explanations, or markdown formatting like ```json.
        5. The entire response must start with `[` and end with `]`, and nothing else.
        
        **Content to analyze:**
        ---
        {text}
        ---
        """
        return self.ask_gemini(prompt)

    # --- FEATURE: MULTIMODAL CONTENT (DIAGRAMS) ---
    def generate_graphviz_diagram(self, topic):
        """Generates an explanation and a Graphviz DOT diagram for a topic."""
        prompt = f"""
        Explain the concept of "{topic}" for a beginner.
        After the explanation, create a simple visual diagram representing the core idea using Graphviz DOT language.
        The DOT code must be enclosed in a single markdown code block like this: ```dot ... ```
        
        Example for "Linked List":
        This is an explanation of a linked list...
        
        ```dot
        digraph LinkedList {{
            node [shape=box, style=rounded];
            A [label="Node A | Data: 10"];
            B [label="Node B | Data: 20"];
            C [label="Node C | Data: 30"];
            A -> B;
            B -> C;
            C -> "NULL";
        }}
        ```
        """
        response = self.ask_gemini(prompt)
        
        # Use regex to find the dot code block
        dot_match = re.search(r"```dot\s*([\s\S]*?)\s*```", response)
        if dot_match:
            dot_code = dot_match.group(1).strip()
            # Remove the code block from the main explanation
            explanation = response.replace(dot_match.group(0), "").strip()
            return explanation, dot_code
        else:
            return response, None # Return full response as explanation if no diagram found

    # --- FEATURE: ADAPTIVE LEARNING PATHWAYS ---
    def get_prerequisite_topics(self, topic):
        """Gets a list of 1-3 prerequisite topics for a given difficult topic."""
        prompt = f"""
        You are a curriculum expert who only speaks JSON.
        A student is struggling with the topic: "{topic}".
        What are 1 to 3 essential prerequisite topics they should review first?
        
        Your response MUST be a valid JSON array of strings. For example: ["Topic A", "Topic B"].
        Do NOT include any other text or markdown.
        """
        return self.ask_gemini(prompt)

    # --- FEATURE: PROJECT-BASED SYNTHESIS ---
    def generate_project_idea(self, roadmap_topic, completed_subtopics):
        """Generates a project idea based on a learning path."""
        prompt = f"""
        You are a project-based learning expert who only speaks JSON.
        A student is learning about "{roadmap_topic}" and has completed these sub-topics: {', '.join(completed_subtopics)}.
        
        Generate a single, engaging mini-project idea that allows them to apply their new skills.
        
        Your response MUST be a valid JSON object with two keys: "title" (a short, catchy project name) and "description" (a 2-3 sentence summary of the project goal).
        Do NOT include any other text or markdown.
        """
        return self.ask_gemini(prompt)

    # --- FEATURE: KNOWLEDGE GRAPH ---
    def extract_knowledge_graph_dot(self, text_content):
        """Analyzes text and returns a Graphviz DOT string representing the relationships between concepts."""
        prompt = f"""
        You are a knowledge graph expert. Analyze the following text and identify the main concepts and their relationships.
        Represent these relationships as a Graphviz DOT language string.
        
        Instructions:
        1. Identify the key entities/concepts (these will be nodes).
        2. Identify how they are connected (these will be edges with labels).
        3. The output MUST be a valid Graphviz `digraph` string.
        4. Do NOT include any explanation or markdown formatting like ```dot. Just return the raw DOT string.
        
        Text to analyze:
        ---
        {text_content[:2000]}
        ---
        """
        return self.ask_gemini(prompt)