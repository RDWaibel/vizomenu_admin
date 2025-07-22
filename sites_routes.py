from flask import Blueprint, request, redirect, url_for, session, render_template, flash
import requests
from auth_utils import require_login

site_bp = Blueprint("site", __name__)

API_BASE = "http://localhost:7231/api" # or import it from config

@site_bp.route('/sites/add', methods=["POST"])
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

    res = requests.post(f"{API_BASE}/venues/{venue_id}/sites", json=data, headers=headers)

    if not res.ok:
        flash("Failed to add site.", "error")

    return redirect(url_for("edit_venue", venue_id=venue_id))

@site_bp.route('/sites/disable/<site_id>', methods=["POST"])
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
    update_data = { "ChangedById": session.get("user_id") }
    res = requests.put(f"{API_BASE}/sites/{site_id}/toggle", json=update_data, headers=headers)
    
    if not res.ok:
        flash("Failed to disable site.", "error")
    return redirect(url_for("edit_venue", venue_id=venue_id))

@site_bp.route('/sites/edit/<site_id>', methods=["GET", "POST"])
def edit_site(site_id):
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    if request.method == "POST":
        data = {
            "SiteName": request.form["site_name"],
            "Description": request.form["description"],
            "IsActive": "is_active" in request.form,  # Check if checkbox is checked
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

@site_bp.route('/venues/<venue_id>/sites', methods=["GET"])
def manage_sites(venue_id):
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    venue_res = requests.get(f"{API_BASE}/venue/{venue_id}", headers=headers)
    venue = venue_res.json() if venue_res.ok else {}

    org_name = venue.get("OrganizationName", "Unknown")
    venue_name = venue.get("VenueName", "Unknown")

    sites_res = requests.get(f"{API_BASE}/venues/{venue_id}/sites", headers=headers)
    sites = sites_res.json() if sites_res.ok else []

    return render_template("sites.html",
                           venue_id=venue_id,
                           venue_name=venue_name,
                           org_name=org_name,
                           sites=sites)