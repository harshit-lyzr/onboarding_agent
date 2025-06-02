import requests


def get_keka_token(client_id: str, client_secret: str, api_key: str) -> dict:
    url = "https://login.keka.com/connect/token"

    payload = {
        "grant_type": "kekaapi",
        "scope": "kekaapi",
        "client_id": client_id,
        "client_secret": client_secret,
        "api_key": api_key
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0"
    }

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching token: {e}")
        return {"error": str(e)}


def get_keka_employees(bearer_token: str) -> dict:
    url = "https://lyzr.keka.com/api/v1/hris/employees?inProbation=false&inNoticePeriod=false"

    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {bearer_token}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching employees: {e}")
        return {"error": str(e)}


def get_keka_preboarding_candidates(bearer_token: str) -> dict:
    url = "https://lyzr.keka.com/api/v1/hire/preboarding/candidates?stage=4&status=0"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {bearer_token}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise error for bad responses (4xx/5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        return {"error": f"HTTP error occurred: {http_err}", "status_code": response.status_code}
    except requests.exceptions.RequestException as req_err:
        return {"error": f"Request error occurred: {req_err}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}
