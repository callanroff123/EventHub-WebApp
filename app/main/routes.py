# Note that for all routes associated with a bluprint, we must first assign the bluprint name before referencing a function in url_for(...)
# Ex: url_for("login") -> url_for("auth.login")
import os
from dotenv import load_dotenv
from flask import render_template, request, redirect, url_for, flash, jsonify
import requests
import ast
import smtplib
from email.message import EmailMessage
from datetime import datetime
from app.main.forms import FilterForm, ContactForm
from app.main import bp
from app.utilities.azure_blob_connection import read_from_azure_blob_storage, show_azure_blobs


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
    current_date = datetime.now().date()
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
    json_data = [d | {"Artist_Certainty_Int": float(d["Artist_Certainty"])} for d in json_data]
    current_date = datetime.now().date()
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
        form = form
    ))


# For refreshing filters on the MAIN GIGS page
@bp.route('/refresh_filters', methods = ["GET", "POST"])
def refresh_filters():
    return(redirect(url_for('main.gigs', community_type = "following_users")))


# Contact page
@bp.route("/contact", methods = ["GET", "POST"])
def contact():
    contact_form = ContactForm()
    if "contact_submit" in request.form and contact_form.validate_on_submit():
        conn = smtplib.SMTP("smtp.gmail.com")
        my_email = os.getenv("GMAIL_USER_EMAIL")
        my_password = os.getenv("GMAIL_APP_PASSWORD")
        message = EmailMessage()
        message["From"] = my_email
        message["To"] = my_email
        message["subject"] = f"""{contact_form.name.data} ({contact_form.email.data}) has reached out from EventHub."""
        message.set_content(contact_form.message.data)
        conn.starttls()
        conn.login(
            user = my_email,
            password = my_password
        )
        conn.send_message(message)
        conn.close()
        flash("Message sent!")
        return(redirect(url_for("main.gigs")))
    return(render_template(
        "contact.html",
        contact_form = contact_form,
        recaptcha_site_key = os.getenv("RECAPTCHA_PUBLIC_KEY")
    ))