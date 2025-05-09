# Note that for all routes associated with a bluprint, we must first assign the bluprint name before referencing a function in url_for(...)
# Ex: url_for("login") -> url_for("auth.login")
import os
import numpy as np
from dotenv import load_dotenv
from flask import render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import requests
import ast
import smtplib
from email.message import EmailMessage
from datetime import datetime
from zoneinfo import ZoneInfo
import threading
from app.tasks import send_contact_email
from app.main.forms import FilterForm, ContactForm
from app.main import bp
from app.utilities.azure_blob_connection import read_from_azure_blob_storage, show_azure_blobs
from app.utilities.utils import readable_date


# Read in necessary environment variables to connect to Azure
load_dotenv()
CONNECTION_STRING = os.environ.get("MS_BLOB_CONNECTION_STRING")
CONTAINER_NAME = os.environ.get("MS_BLOB_CONTAINER_NAME")


# API FOR GIG EXTRACTION
@bp.route("/api/gigs", methods = ["GET"])
def get_gigs():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    venue_filter = request.args.get("venue_filter")
    search_field = request.args.get("search_field")
    blobs = show_azure_blobs(
        connection_string = CONNECTION_STRING,
        container_name = CONTAINER_NAME
    )
    latest_file = max(blobs)
    json_data = read_from_azure_blob_storage(
        connection_string = CONNECTION_STRING,
        container_name = CONTAINER_NAME,
        file_name = latest_file
    )
    current_date = datetime.now(tz = ZoneInfo("Australia/Sydney")).date()
    json_data_refined = [d for d in json_data if datetime.strptime(d["Date"], "%Y-%m-%d").date() >= current_date]
    if start_date:
        json_data_refined = [d for d in json_data_refined if datetime.strptime(d["Date"], "%Y-%m-%d").date() >= datetime.strptime(start_date, "%Y-%m-%d").date()]
    if end_date:
        json_data_refined = [d for d in json_data_refined if datetime.strptime(d["Date"], "%Y-%m-%d").date() <= datetime.strptime(end_date, "%Y-%m-%d").date()]
    if venue_filter:
        json_data_refined = [d for d in json_data_refined if d["Venue"] in venue_filter]
    if search_field:
        json_data_refined = [d for d in json_data_refined if (search_field in d["Venue"].lower()) or (search_field in d["Title"].lower())]
    return(jsonify(json_data_refined))


# APP LANDING PAGE
# Quite basic. Just has a link to the main gigs page and the nav-bar
@bp.route("/")
@bp.route("/index")
def index():
    return(render_template(
        "index.html"
    ))


# MAIN GIGS PAGE
# Contains a table of all gigs, and user posts for the community section below.
# Both the gigs and posts have a filter mechanism.
@bp.route("/gigs", methods = ["GET", "POST"])
def gigs():
    blobs = show_azure_blobs(
        connection_string = CONNECTION_STRING,
        container_name = CONTAINER_NAME
    )
    latest_file = max(blobs)
    json_data = read_from_azure_blob_storage(
        connection_string = CONNECTION_STRING,
        container_name = CONTAINER_NAME,
        file_name = latest_file
    )
    json_data = [d | {"Artist_Certainty_Int": float(0 if d["Artist_Certainty"].strip() == "" else d["Artist_Certainty"])} for d in json_data]
    json_data = [d | {"Date_Formatted": readable_date(d["Date"])} for d in json_data]
    max_rank = max([float(d["followers_rank"]) for d in json_data])
    current_date = datetime.now(tz = ZoneInfo("Australia/Sydney")).date()
    all_genres_raw = [ast.literal_eval(d["genres"]) if "[" in d["genres"] else None for d in json_data]
    all_genres = [l for l in all_genres_raw if l is not None and len(l) > 0]
    all_genres = sorted(list(set([i.upper() for sublist in all_genres for i in sublist])))
    form = FilterForm(
        default_venues = list(set([d["Venue"] for d in json_data])),
        default_genres = all_genres
    )
    json_data_refined = [d for d in json_data if datetime.strptime(d["Date"], "%Y-%m-%d").date() >= current_date]
    if "gig_filter_submit" in request.form:
        if form.start_date.data:
            json_data_refined = [d for d in json_data_refined if datetime.strptime(d["Date"], "%Y-%m-%d").date() >= form.start_date.data]
        if form.end_date.data:
            json_data_refined = [d for d in json_data_refined if datetime.strptime(d["Date"], "%Y-%m-%d").date() <= form.end_date.data]
        if form.just_in.data:
            if form.just_in.data == "Just In":
                json_data_refined = [d for d in json_data_refined if (float(d["just_in"]) == 1) and (float(d["followers_rank"]) < np.max([float(d["followers_rank"]) for d in json_data_refined]))]
        if form.venue_filter.data:
            json_data_refined = [d for d in json_data_refined if d["Venue"] in form.venue_filter.data]
        if form.genre_filter.data:
            json_data_refined = [d for d in json_data_refined if d["genres"] != ""]
            json_data_refined = [d for d in json_data_refined if any(i in form.genre_filter.data for i in ast.literal_eval(d["genres"].upper()))]
        if form.search_field.data:
            json_data_refined = [d for d in json_data_refined if (form.search_field.data in d["Venue"].lower()) or (form.search_field.data in d["Title"].lower())]
        if len(json_data_refined) < len(json_data):
            flash("Filter applied!")
    return(render_template(
        "gigs.html",
        data = json_data_refined,
        form = form,
        current_date = current_date.isoformat(),
        max_rank = max_rank
    ))


# For refreshing filters on the MAIN GIGS page
@bp.route('/refresh_filters', methods = ["GET", "POST"])
def refresh_filters():
    return(redirect(url_for('main.gigs', community_type = "following_users")))


@bp.route("/about")
def about():
    return(render_template("about.html"))


# Contact page
@bp.route("/contact", methods = ["GET", "POST"])
def contact():
    contact_form = ContactForm()
    if "contact_submit" in request.form and contact_form.validate_on_submit():
        threading.Thread(
            target = send_contact_email,
            args = (
                contact_form.name.data,
                contact_form.email.data,
                contact_form.message.data
            )
        ).start()
        flash("Message sent!")
        return(redirect(url_for("main.gigs")))
    return(render_template(
        "contact.html",
        contact_form = contact_form,
        recaptcha_site_key = os.getenv("RECAPTCHA_PUBLIC_KEY")
    ))


@bp.route("/terms-of-use")
def terms_of_use():
    return(render_template("terms_of_use.html"))


@bp.route("/privacy-policy")
def privacy_policy():
    return(render_template("privacy_policy.html"))

@bp.route("/faq")
def faq():
    return(render_template("faq.html"))


@bp.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')
