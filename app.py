from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
import jwt
from datetime import datetime, timedelta
from email_helper import send_login_notification

from site_routes import site_bp
from venue_routes import venue_bp

app = Flask(__name__)
app.secret_key = "R0bV1z0M3nuAPI2025!SecureKeyXtra" 
app.permanent_session_lifetime = timedelta(minutes=60)
def make_session_permanent():
    session.permanent = True
app.register_blueprint(site_bp)
app.register_blueprint(venue_bp)

# 🔧 Replace this with your actual Function App base URL
API_BASE = "http://localhost:7231/api"

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def home():
    print("Session user:", session.get("user"))
    return render_template("home.html")

@app.route('/organizations', endpoint='list_organizations')
@login_required
def list_organizations():
    try:
        headers = {"Authorization": f"Bearer {session['token']}"}
        print("Token:", session.get("token"))
        response = requests.get(f"{API_BASE}/organizations", headers=headers)
        print(response.status_code, response.text)
        organizations = response.json()
    except Exception as e:
        print(f"Error fetching organizations: {e}")
        organizations = []
    return render_template("organizations.html", organizations=organizations)

@app.route('/organizations/add', methods=['GET', 'POST'])
@login_required
def add_organization():
    if 'token' not in session:
        flash("Please log in as SuperAdmin to continue.", "warning")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        org_data = {
            "name": request.form['name'],
            "address": request.form['address'],
            "city": request.form['city'],
            "state": request.form['state'],
            "zipCode": request.form['zipCode'],
            "contactPhone": request.form['contactPhone'],
            "contactEmail": request.form['contactEmail']
        }

        headers = {
            "Authorization": f"Bearer {session['token']}"
        }
        try:
            response = requests.post(f"{API_BASE}/organizations", json=org_data, headers=headers)
            if response.status_code == 201:
                flash("Organization created successfully!", "success")
                return redirect(url_for('home'))
            elif response.status_code == 403:
                flash("You are not authorized to create organizations.", "danger")
            else:
                flash(f"Failed to create organization. {response.status_code}", "danger")
        except Exception as e:
            flash(f"Error: {e}", "danger")

    return render_template("add_organization.html")

@app.route('/organizations/edit/<org_id>', methods=['GET', 'POST'])
@login_required
def edit_organization(org_id):
    if 'token' not in session:
        flash("Please log in as SuperAdmin to continue.", "warning")
        return redirect(url_for('login'))
    token = session.get('token')
    headers = {'Authorization': f'Bearer {token}'} if token else {}

    if request.method == 'POST':
        updated_data = {
            "id": org_id,
            "name": request.form['name'],
            "address": request.form['address'],
            "city": request.form['city'],
            "state": request.form['state'],
            "zipCode": request.form['zipCode'],
            "contactPhone": request.form['contactPhone'],
            "contactEmail": request.form['contactEmail'],
            "enteredUTC": datetime.utcnow().isoformat(),
            "enteredBy": session['user']['email']
        }

        try:
            response = requests.put(f"{API_BASE}/organizations/{org_id}", json=updated_data, headers=headers)
            if response.status_code == 204:
                flash("Organization updated successfully", "success")
                return redirect(url_for('organizations'))
            else:
                flash(f"Update failed: {response.text}", "danger")
        except Exception as e:
            flash(f"Update failed: {e}", "danger")

    # GET logic
    try:
        response = requests.get(f"{API_BASE}/organizations/{org_id}", headers=headers)
        if response.status_code == 200:
            org = response.json()
            return render_template("organization_edit.html", org=org)
        else:
            flash("Failed to fetch organization", "danger")
            return redirect(url_for('organizations'))
    except Exception as e:
        flash(f"Error: {e}", "danger")
        return redirect(url_for('organizations'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            response = requests.post(f"{API_BASE}/auth/login", json={"email": email, "password": password})
            if response.status_code == 200:
                data = response.json()
                token = data['token']
                user_info = data['user']

                # Store token and user info in session
                session['token'] = token
                session['user'] = user_info  # user_info contains firstName, lastName, etc.

                print("DEBUG: user =", user_info)
                print("DEBUG: session['user'] =", session.get("user"))
                
                flash("Login successful", "success")
                send_login_notification(email)
                return redirect(url_for('home'))
            else:
                flash("Invalid credentials", "danger")
        except Exception as e:
            flash(f"Login failed: {e}", "danger")

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

#Venues Management





@app.before_request
def require_login():
    allowed_routes = ['login', 'static']  # Static = CSS, JS, etc.
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect(url_for('login'))
    
if __name__ == "__main__":
    app.run(debug=True)

