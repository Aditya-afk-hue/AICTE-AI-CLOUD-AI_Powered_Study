# Only run this file if you want to find what are the models are support by your Gemini API token
import google.generativeai as genai
genai.configure(api_key="AIzaSyB5ER3FZDpfZ0CDaDbyifTHCF70IM0C-Js")
for m in genai.list_models():
    print(m.name, " -> ", m.supported_generation_methods)
