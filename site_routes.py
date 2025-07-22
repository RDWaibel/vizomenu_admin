from flask import Blueprint, request, redirect, url_for, session, render_template, flash
import requests
from flask_login import login_required

site_bp = Blueprint("site", __name__)

API_BASE = "http://localhost:7231/api" # or import it from config

@site_bp.route('/sites/add', methods=["POST"])
@login_required
def add_site():
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    venue_id = request.form["venue_id"]
    data = {
        "VenueId": venue_id,
        "SiteName": request.form["site_name"],
        "Description": request.form.get("description", ""),
        "EnteredById": session.get("user_id")  # Assumes you store user_id in session
    }

    res = requests.post(f"{API_BASE}/sites", json=data, headers=headers)

    if not res.ok:
        flash("Failed to add site.", "error")

    return redirect(url_for("edit_venue", venue_id=venue_id))

@site_bp.route('/sites/disable/<site_id>', methods=["POST"])
@login_required
def disable_site(site_id):
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # Get the current site to retrieve VenueId
    site_res = requests.get(f"{API_BASE}/sites/{site_id}", headers=headers)
    if not site_res.ok:
        flash("Site not found.", "error")
        return redirect(url_for("list_organizations"))

    site = site_res.json()
    venue_id = site["VenueId"]

    # Send the update
    update_data = { "IsActive": False }
    res = requests.put(f"{API_BASE}/sites/{site_id}", json=update_data, headers=headers)
    
    if not res.ok:
        flash("Failed to disable site.", "error")
    return redirect(url_for("edit_venue", venue_id=venue_id))

@site_bp.route('/sites/edit/<site_id>', methods=["GET", "POST"])
@login_required
def edit_site(site_id):
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    if request.method == "POST":
        data = {
            "SiteName": request.form["site_name"],
            "Description": request.form["description"],
        }
        res = requests.put(f"{API_BASE}/sites/{site_id}", json=data, headers=headers)

        venue_id = request.form["venue_id"]
        return redirect(url_for("edit_venue", venue_id=venue_id))

    # GET site info
    res = requests.get(f"{API_BASE}/sites/{site_id}", headers=headers)
    if not res.ok:
        flash("Could not load site.", "error")
        return redirect(url_for("list_organizations"))

    site = res.json()
    return render_template("site_form.html", site=site)
