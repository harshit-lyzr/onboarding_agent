import os
import signal
import sys
from datetime import datetime
from database import employees, smtp, surveys, company, survey_link
from send_email import send_email
from lyzr_agent import email_generation

# Graceful shutdown handler
def handle_sigterm(signum, frame):
    print("Received SIGTERM. Performing cleanup...")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)

today = datetime.utcnow().date()

# List of (day_offset, survey_flag)
email_schedule = [
    (-15, "day_015_sent", "67f775b9b8cd188b46f4ae15"),
    (-7, "day_07_sent", "67f7791addf6166b76976550"),
    (0, "day_0_sent", "67f781e3df4ef875bff451e4"),
    (1, "day_1_sent", "67f787b1df4ef875bff45221"),
    (7, "day_7_sent", "67f78f003b84a4b9724e6925"),
    (30, "day_30_sent", "67f78f67ddf6166b76976666"),
    (90, "day_90_sent", "67f78fb9ddf6166b7697666f"),
]

def main():
    try:
        print("Starting onboarding email task...")
        
        for emp in employees.find({"status": "active"}):
            print(f"Processing employee: {emp.get('firstname', 'Unknown')} {emp.get('lastname', 'Unknown')}")

            joining_date = emp.get("joining_date")
            if not joining_date:
                continue

            days_since_joining = (today - joining_date.date()).days
            print(f"Days since joining: {days_since_joining}")

            survey = surveys.find_one({"user_id": emp["user_id"]})
            survey_links = survey_link.find_one({"user_id": emp["user_id"]})
            if not survey:
                continue
            company_info = company.find_one({"user_id": emp["user_id"]})

            update_fields = {}

            for target_day, flag, agent_id in email_schedule:
                if days_since_joining == target_day and not survey.get(flag):
                    data = smtp.find_one({"user_id": emp["user_id"]})
                    if flag == "day_0_sent":
                        success = email_generation(agent_id,
                                               f"Employee details: \nEmployee name: {emp['firstname']} {emp['lastname']} Joining Date: {emp['joining_date']} Company Name: {company_info['company']}")
                        send_email(success['subject'], success['content'], company_info, data)
                    elif flag in ["day_1_sent", "day_7_sent", "day_30_sent", "day_90_sent"]:
                        success = email_generation(agent_id,
                                               f"Form Link: {survey_links[flag]}")
                        send_email(success['subject'], success['content'], emp, data)
                    else:
                        success = email_generation(agent_id, f"Company Name: {company_info['company']} Employee Name: {emp['firstname']}")
                        send_email(success['subject'], success['content'], emp, data)

                    update_fields[flag] = True
                    update_fields["last_sent_at"] = datetime.utcnow()
                    employees.update_one({"user_id": emp["user_id"]}, {"$set": {"stage": flag}})
                    print(f"Sent email for {flag}")
                    break

            if update_fields:
                surveys.update_one({"user_id": emp["user_id"]}, {"$set": update_fields})

        print("Task completed successfully")

    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
