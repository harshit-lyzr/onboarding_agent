from database import client,db, employee, preboarding_employee, surveys, pre_surveys


def add_employee(data: dict,collection:str, user_id:str):

    collection = db[collection]

    keka_data = data

    if "error" in keka_data:
        print(f"Error fetching data from Keka: {keka_data['error']}")
        client.close()
        return

    employees = keka_data.get("data", [])

    new_employee_count = 0

    for emp in employees:
        employee_id = emp.get("id")
        if employee_id:
            # Check if the employee already exists in the database
            if not collection.find_one({"employee_id": employee_id}):
                try:
                    filtered_info = {
          "user_id":user_id,
          "employee_id": emp.get("id"),
          "employee_number": emp.get("employeeNumber"),
          "firstName": emp.get("firstName"),
          "lastName": emp.get("lastName"),
          "joiningDate": emp.get("joiningDate"),
          "email": emp.get("email"),
          "mobilePhone": emp.get("mobilePhone"),
          "reporting_manager_email":emp['reportsTo'].get("email"),
                        "status": "active"
      }
                    employee.insert_one(filtered_info)
                    surveys.insert_one({
  "user_id": user_id,
  "day_1_sent": False,
  "day_7_sent": False,
  "day_30_sent": False,
  "day_90_sent": False,
  "employee_id": emp.get("id")
})
                    new_employee_count += 1
                    print(f"Inserted new employee with ID: {employee_id}")
                except Exception as e:
                    print(f"Error inserting employee with ID {employee_id}: {e}")
            else:
                print(f"Employee with ID {employee_id} already exists in the database.")
        else:
            print("Employee data missing 'id' field. Skipping.")

    print(f"Successfully added {new_employee_count} new employees to MongoDB.")


def add_pre_employee(data: dict,collection:str, user_id: str):
    """
    Fetches employee data from Keka and stores it in MongoDB,
    adding only new employees based on their 'id' field.

    Args:
        bearer_token: The Keka API bearer token.
        mongo_uri: The MongoDB connection URI.
        db_name: The name of the MongoDB database.
        collection_name: The name of the MongoDB collection.
    """

    collection = db[collection]

    keka_data = data

    if "error" in keka_data:
        print(f"Error fetching data from Keka: {keka_data['error']}")
        client.close()
        return

    employees = keka_data.get("data", [])

    new_employee_count = 0

    for emp in employees:
        employee_id = emp.get("id")
        if employee_id:
            # Check if the employee already exists in the database
            if not collection.find_one({"employee_id": employee_id}):
                try:
                    filtered_info = {
        "user_id":user_id,
        "employee_id": emp.get("id"),
        "employee_number": emp.get("employeeNumber"),
        "firstName": emp.get("firstName"),
        "lastName": emp.get("lastName"),
        "joiningDate": emp.get("expectedDateOfJoining"),
        "email": emp.get("email"),
        "mobilePhone": emp.get("mobileNumber"),
                        "status":"active"
    }
                    preboarding_employee.insert_one(filtered_info)
                    pre_surveys.insert_one({  "day_07_sent": False,
                  "day_015_sent": False,
                  "day_0_sent": False,
                  "employee_id":emp.get("id"),
                                              "user_id":user_id})
                    new_employee_count += 1
                    print(f"Inserted new employee with ID: {employee_id}")
                except Exception as e:
                    print(f"Error inserting employee with ID {employee_id}: {e}")
            else:
                print(f"Employee with ID {employee_id} already exists in the database.")
        else:
            print("Employee data missing 'id' field. Skipping.")

    print(f"Successfully added {new_employee_count} new employees to MongoDB.")
