from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import requests
from flask_login import login_required

venue_bp = Blueprint("venue", __name__)
API_BASE = "http://localhost:7231/api"

@venue_bp.route('/venues/<org_id>')
@login_required
def view_venues(org_id):
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    res = requests.get(f"{API_BASE}/organization/{org_id}/venues", headers=headers)
    venues = res.json() if res.ok else []

    org_name = "Organization"
    org_res = requests.get(f"{API_BASE}/organization/{org_id}", headers=headers)
    if org_res.ok:
        org_data = org_res.json()
        org_name = org_data.get("Name", "Organization")

    return render_template("venues.html", venues=venues, org_id=org_id, org_name=org_name)

@venue_bp.route('/venues/<org_id>/add', methods=["GET", "POST"])
@login_required
def add_venue(org_id):
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    if request.method == "POST":
        data = {
            "VenueName": request.form["name"],
            "Location": request.form["location"],
            "Is24Hours": "is24" in request.form,
            "EnteredById": session['user']['id']  # ✅ set EnteredById
        }    
        requests.post(f"{API_BASE}/organization/{org_id}/venues", json=data, headers=headers)
        return redirect(url_for("view_venues", org_id=org_id))
    
    org_name = "Organization"
    res = requests.get(f"{API_BASE}/organizations/{org_id}", headers=headers)
    if res.ok:
        org_data = res.json()
        org_name = org_data.get("Name", "Organization")

    return render_template("venue_form.html", org_id=org_id, org_name=org_name) 

@venue_bp.route('/venues/test')
def test_venues():
    return "Venues route working"

@venue_bp.route('/venues/edit/<venue_id>', methods=["GET", "POST"])
@login_required
def edit_venue(venue_id):
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    if request.method == "POST":
        data = {
            "VenueName": request.form["name"],
            "Location": request.form["location"],
            "Is24Hours": "is24" in request.form
        }
        org_id = request.form["org_id"]
        requests.put(f"{API_BASE}/venues/{venue_id}", json=data, headers=headers)
        return redirect(url_for("view_venues", org_id=org_id))

    # GET venue info
    res = requests.get(f"{API_BASE}/venue/{venue_id}", headers=headers)
    venue = res.json() if res.ok else {}
    
    sites = []
    site_res = requests.get(f"{API_BASE}/venues/{venue_id}/sites", headers=headers)
    if site_res.ok:
        sites = site_res.json()

    # Get org name for display
    org_id = venue.get("OrganizationId", "")
    org_name = "Organization"
    org_res = requests.get(f"{API_BASE}/organization/{org_id}", headers=headers)
    if org_res.ok:
        org_data = org_res.json()
        org_name = org_data.get("Name", "Organization")

    return render_template("venue_form.html", venue=venue, sites=sites, org_id=org_id, org_name=org_name)


@venue_bp.route('/venues/<venue_id>/copy', methods=["POST"])
@login_required
def copy_venue(venue_id):
    new_name = request.form["new_name"]
    data = {"VenueName": new_name}
    headers = {"Authorization": f"Bearer {session['token']}"}
    requests.post(f"{API_BASE}/venues/{venue_id}/copy", json=data, headers=headers)
    return redirect(request.referrer)

@venue_bp.route('/venues/<venue_id>/hours', methods=["GET", "POST"])
@login_required
def manage_hours(venue_id):
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    if request.method == "POST":
        hours_payload = []
        for i in range(7):  # 0 = Sunday, 6 = Saturday
            is_closed = f"closed_{i}" in request.form
            open_time = request.form.get(f"open_{i}") or None
            close_time = request.form.get(f"close_{i}") or None

            hours_payload.append({
                "DayOfWeek": i,
                "OpenTime": open_time,
                "CloseTime": close_time,
                "IsClosed": is_closed
            })

        requests.post(f"{API_BASE}/venues/{venue_id}/hours", json=hours_payload, headers=headers)
        flash("Hours updated successfully", "success")

    res = requests.get(f"{API_BASE}/venues/{venue_id}/hours", headers=headers)
    hours = res.json() if res.ok else []

    # We assume all hours have the same venue name; fetch one if needed
    venue_name = request.form.get("venue_name") or f"Venue {venue_id}"
    org_id = request.args.get("org_id") or ""

    return render_template(
        "venue_hours.html",
        hours=hours,
        venue_name=venue_name,
        venue_id=venue_id,
        org_id=org_id,
        day_labels=["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    )