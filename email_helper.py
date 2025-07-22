# email_helper.py

import requests
API_BASE = "http://localhost:7231/api"

def send_login_notification(user_email):
    #Matches the class in the API
    payload = {
        "to": "rob@vizomenu.com",
        "toName": "Rob Waibel",
        "subject": f"User Login Notification: {user_email}",
        "htmlbody": f"<h3>Login Event</h3><p>User <strong>{user_email}</strong> just logged into the Flask site.</p>",
        "textbody": f"User {user_email} just logged into the Flask site."

    }

    try:
        response = requests.post(f"{API_BASE}/sendemail", json=payload)
        response.raise_for_status()
        print("Login notification sent successfully.")
    except requests.RequestException as e:
        print(f"[Email Error] Failed to send login notification: {e}")
