from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["demo_agent"]
employees = db["employee"]
surveys = db["surveys"]
logs = db["logs"]
smtp = db["smtpdetails"]
company = db["company_details"]
survey_link = db['survey_links']