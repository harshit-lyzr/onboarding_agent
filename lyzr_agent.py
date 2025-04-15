import requests
import os
import json
from dotenv import load_dotenv


load_dotenv()


API_KEY = os.getenv("LYZR_KEY")
API_URL = os.getenv("API_URL")


def email_generation(agent_id: str, message: str):
    payload = {
        "user_id": "harshit@lyzr.ai",
        "agent_id": agent_id,
        "session_id": agent_id,
        "message": message
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }
    response = requests.post(API_URL, json=payload, headers=headers)
    data = json.loads(response.json()['response'])

    return data
