import logging
from datetime import datetime
from keka import get_keka_token, get_keka_employees, get_keka_preboarding_candidates
from trigger import add_employee, add_pre_employee
from database import (
    employee,
    preboarding_employee,
    pre_surveys,
    surveys,
    survey_links,
    smtpdetails,
    companys,
    keka_creds
)
from lyzr_agent import email_generation
from smtp_setup import send_email

# Define email schedule as a constant
EMAIL_SCHEDULE = [
    (-15, "day_015_sent", "67f775b9b8cd188b46f4ae15"),
    (-7, "day_07_sent", "67f7791addf6166b76976550"),
    (0, "day_0_sent", "67f781e3df4ef875bff451e4"),
    (1, "day_1_sent", "67f787b1df4ef875bff45221"),
    (7, "day_7_sent", "67f78f003b84a4b9724e6925"),
    (30, "day_30_sent", "67f78f67ddf6166b76976666"),
    (90, "day_90_sent", "67f78fb9ddf6166b7697666f"),
]

TODAY = datetime.utcnow().date()


def parse_iso_date(date_str):
    if date_str.endswith("Z"):
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").date()
    else:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S").date()


def process_employee(emp_type, emp, survey_collection):
    """Processes a single employee for sending emails based on joining date."""

    joining_date_str = emp.get("joiningDate")
    if not joining_date_str:
        logging.warning(f"No joining date found for employee: {emp.get('employee_id') or emp.get('user_id')}")
        return

    joining_date = parse_iso_date(joining_date_str)
    if not joining_date:
        return

    days_since_joining = (TODAY - joining_date).days

    #  Determine whether to search pre_surveys or surveys.
    if emp_type == "employee":
        survey = surveys.find_one(
            {"employee_id": emp.get("employee_id") or emp.get("user_id")})  # check if the employee_id is there
    else:
        survey = pre_surveys.find_one(
            {"employee_id": emp.get("employee_id") or emp.get("user_id")})  # check if the employee_id is there

    if not survey:
        logging.warning(f"No survey found for employee: {emp.get('employee_id') or emp.get('user_id')}")
        return

    survey_link = survey_links.find_one({"user_id": emp["user_id"]})
    company = companys.find_one({"user_id": emp["user_id"]})

    update_fields = {}

    for target_day, flag, agent_id in EMAIL_SCHEDULE:
        if days_since_joining == target_day and not survey.get(flag):
            data = smtpdetails.find_one({"user_id": emp["user_id"]})

            if not data:
                logging.error(f"SMTP details not found for user: {emp['user_id']}")
                continue  # Skip to the next iteration of the loop

            if emp_type == "employee" and flag in ["day_1_sent", "day_7_sent", "day_30_sent", "day_90_sent"]:
                if survey_link and flag in survey_link:
                    success = email_generation(agent_id, "Form Link: " + survey_link[flag])
                else:
                    logging.warning(f"Survey link is not found or key {flag} is missing for survey link {survey_link}")
                    continue
            elif emp_type == "preboarding_employee" and flag in ["day_07_sent", "day_015_sent"]:
                success = email_generation(agent_id,
                                           "Company Name: " + company['company'] + "Employee Name: " + emp['firstName'])
            else:
                logging.warning(f"Invalid flag or employee type. Skipping email: {flag}, {emp_type}")
                continue

            send_email(success['subject'], success['content'], emp, data)

            update_fields[flag] = True
            update_fields["last_sent_at"] = datetime.utcnow()

            # Determine which collection to update based on the emp_type
            collection_to_update = employee if emp_type == "employee" else preboarding_employee
            collection_to_update.update_one({"employee_id": emp["employee_id"] or emp.get("user_id")}, {
                "$set": {"stage": flag}})  # added or emp.get("user_id") to prevent key error

            break

    if update_fields:
        if emp_type == "employee":
            surveys.update_one({"employee_id": emp["employee_id"] or emp.get("user_id")},
                               {"$set": update_fields})  # added or emp.get("user_id") to prevent key error
        else:
            pre_surveys.update_one({"employee_id": emp["employee_id"] or emp.get("user_id")},
                                   {"$set": update_fields})  # added or emp.get("user_id") to prevent key error


# Main Execution
def main():
    # Log basic configuration
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    documents = keka_creds.find()
    for creds in documents:
        token = get_keka_token(creds['client_id'], creds['client_secret'], creds['api_key'])
        employees = get_keka_employees(token['access_token'])
        pre_employee = get_keka_preboarding_candidates(token['access_token'])
        add_employee(employees, "employee", creds['user_id'])
        add_pre_employee(pre_employee, "preboarding_employee", creds['user_id'])

    #  Process employees
    logging.info("Processing active employees...")
    for emp in employee.find({"status": "active"}):
        process_employee("employee", emp, surveys)

    # Process preboarding employees
    logging.info("Processing active preboarding employees...")
    for emp in preboarding_employee.find({"status": "active"}):
        process_employee("preboarding_employee", emp, pre_surveys)


if __name__ == "__main__":
    main()