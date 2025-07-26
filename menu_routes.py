from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import requests
from auth_utils import require_login

menu_bp = Blueprint("menu", __name__)
from config import API_BASE

@menu_bp.route("/menus/manage/<site_id>")
@require_login
def manage_menus(site_id):
    headers = {
        "Authorization": f"Bearer {session.get('token')}"
    }

    site_res = requests.get(f"{API_BASE}/sites/{site_id}", headers=headers)
    menu_res = requests.get(f"{API_BASE}/sites/{site_id}/menus", headers=headers)

    site = site_res.json() if site_res.ok else {}
    menus = menu_res.json() if menu_res.ok else []

    return render_template("menu.html", site=site, menus=menus)


@menu_bp.route("/menus/import/<site_id>", methods=["GET", "POST"])
@require_login
def import_menus_for_site(site_id):
    if request.method == "POST":
        file = request.files.get("csv_file")
        if not file:
            flash("No file uploaded", "error")
            return redirect(url_for("menu.import_menus_for_site", site_id=site_id))

        headers = {
            "Authorization": f"Bearer {session.get('token')}"
        }

        res = requests.post(
            f"{API_BASE}/menus/import",  # You could include site_id in file rows
            headers=headers,
            data=file.read().decode("utf-8")
        )

        if res.ok:
            flash("Menus imported successfully.", "success")
        else:
            flash(f"Failed to import menus.<br>{res.text}", "error")

        return redirect(url_for("menu.manage_menus", site_id=site_id))

    return render_template("menu_import.html", site_id=site_id)

    