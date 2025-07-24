from flask import Blueprint, request, redirect, url_for, session, render_template, flash
import requests
from auth_utils import require_login

site_bp = Blueprint("site", __name__)

API_BASE = "http://localhost:7231/api" # or import it from config

@site_bp.route('/sites/add', methods=["POST"])
@require_login
def add_site():
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    venue_id = request.form["venue_id"]
    data = {
        "VenueId": venue_id,
        "SiteName": request.form["site_name"],
        "Description": request.form.get("description", ""),
        "EnteredBy": session.get("user", {}).get("Email"),   
        "IsActive": True  # Default to active
    }
    import pprint
    pprint.pprint(data)
    print("SESSION CONTENT:", dict(session))

    res = requests.post(f"{API_BASE}/venues/{venue_id}/sites", json=data, headers=headers)

    if not res.ok:
        flash(f"{session.get("Email"),} Failed to add site.<br>{data}", "error")
    else:
        flash("Site added successfully.", "success")


    venue_res = requests.get(f"{API_BASE}/venue/{venue_id}", headers=headers)
    site_res = requests.get(f"{API_BASE}/venues/{venue_id}/sites", headers=headers)
    org_res = requests.get(f"{API_BASE}/organization/{venue_res.json().get('OrganizationId')}", headers=headers)

    org = org_res.json() if org_res.ok else {}
    venue = venue_res.json()
    sites = site_res.json()

    return render_template("sites.html",
                           venue_id=venue_id,
                           venue_name=venue["VenueName"],
                           org_name=org["Name"],
                           sites=sites)


@site_bp.route('/sites/disable/<site_id>', methods=["POST"])
@require_login
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
    return redirect(url_for("venue.edit_venue", venue_id=venue_id))

@site_bp.route('/sites/edit/<site_id>', methods=["GET", "POST"])
@require_login
def edit_site(site_id):
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}
    venue_id = request.form["venue_id"]

    if request.method == "POST":
        data = {
            "SiteName": request.form["site_name"],
            "Description": request.form["description"],
            "IsActive": "is_active" in request.form,  # Check if checkbox is checked
        }
        res = requests.put(f"{API_BASE}/sites/{site_id}", json=data, headers=headers)

    venue_res = requests.get(f"{API_BASE}/venue/{venue_id}", headers=headers)
    org_res = requests.get(f"{API_BASE}/organization/{venue_res.json().get('OrganizationId')}", headers=headers)
    site_res = requests.get(f"{API_BASE}/venues/{venue_id}/sites", headers=headers)

    org = org_res.json() if org_res.ok else {}
    venue = venue_res.json()
    sites = site_res.json()

    return render_template("sites.html",
                           venue_id=venue_id,
                           venue_name=venue["VenueName"],
                           org_name=org["Name"],
                           sites=sites)

@site_bp.route('/venues/<venue_id>/sites', methods=["GET"])
@require_login
def manage_sites(venue_id):
    token = session.get("token")
    headers = {"Authorization": f"Bearer {token}"}

    
    venue_res = requests.get(f"{API_BASE}/venue/{venue_id}", headers=headers)
    org_res = requests.get(f"{API_BASE}/organization/{venue_res.json().get('OrganizationId')}", headers=headers)
    venue = venue_res.json() if venue_res.ok else {}
    org = org_res.json() if org_res.ok else {}

    org_name = org.get("Name", "Unknown")
    venue_name = venue.get("VenueName", "Unknown")

    sites_res = requests.get(f"{API_BASE}/venues/{venue_id}/sites", headers=headers)
    sites = sites_res.json() if sites_res.ok else []

    return render_template("sites.html",
                           venue_id=venue_id,
                           venue_name=venue_name,
                           org_name=org_name,
                           sites=sites)