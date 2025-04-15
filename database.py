import os
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()


client = MongoClient(os.getenv("MONGO_URI"))
db = client["onboarding_agent"]

employee = db["employee"]
surveys = db["surveys"]
communication_logs = db["communication_logs"]
preboarding_employee = db['preboarding_employee']
pre_surveys = db['pre_surveys']
smtpdetails = db['smtpdetails']
survey_links = db['survey_links']
keka_creds = db['keka_creds']
companys = db['company']
