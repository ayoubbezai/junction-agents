# agents/gemini_task_agent.py

import google.generativeai as genai
import requests

class GeminiTaskAgent:
    def __init__(self, api_key=None, model_name="gemini-2.0-flash"):
        self.api_key = api_key or "AIzaSyCHlIBXW3UF7lUah8UtuP98-_MH_YU9nc4"
        self.model_name = model_name
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def generate_tasks(self, user_input, prompt=None):
        # The prompt can be customized by the user
        if prompt is None:
            prompt = (
                "You are an AQUAINTEL advisor for aquaculture farmers. "
                "You will receive: (1) a prediction result (with environment quality, bacteria level, and explanations of any issues), "
                "(2) detailed pond information (id, location, pond_name, exact size, safe ranges for parameters, etc.), and "
                "(3) the latest sensor readings for that pond. "
                "Your job is to generate a clear, prioritized list of actionable tips and advice for the farmer, referencing the specific pond and its safe ranges. "
                "If any parameter is outside the safe range, highlight it and explain the risk. "
                "Provide practical, concise, and supportive recommendations to address the issues and improve pond conditions. "
                "Keep each tip short (1-2 lines) so the user can act quickly. "
                "Always tailor your advice to the provided context and data. "
                "Here is the prediction, pond details, and sensor data: " + user_input
            )
        response = self.model.generate_content(prompt)
        return response.text

    def send_tips_to_api(self, pond_id, message, api_url="http://127.0.0.1:8000/api/tips"):
        payload = {
            "pond_id": pond_id,
            "message": message
        }
        response = requests.post(api_url, json=payload)
        return response.status_code, response.text 