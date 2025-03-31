# Note that for all routes associated with a bluprint, we must first assign the bluprint name before referencing a function in url_for(...)
# Ex: url_for("login") -> url_for("auth.login")
import os
from dotenv import load_dotenv
from flask import render_template, request, redirect, url_for, flash
import pandas as pd
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
BLOBS = show_azure_blobs(
    connection_string = CONNECTION_STRING,
    container_name = CONTAINER_NAME
)
FILE_NAME = max(BLOBS)


# Read in default music events from Azure Blob Storage
df = read_from_azure_blob_storage(
    connection_string = CONNECTION_STRING,
    container_name = CONTAINER_NAME,
    file_name = FILE_NAME
)


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
    df_refined = df.copy()
    df_refined = df_refined[
        (pd.to_datetime(df_refined["Date"]) >= pd.to_datetime(datetime.now().date()))
    ].reset_index(drop = True)
    print(df_refined.head())
    default_venues = list(df_refined["Venue"].unique())
    form = FilterForm(default_venues = default_venues)
    if "gig_filter_submit" in request.form:
        print(request.form)
        if form.start_date.data:
            df_refined = df_refined[
                (pd.to_datetime(df_refined["Date"]) >= pd.to_datetime(form.start_date.data))
            ].reset_index(drop = True)
        if form.end_date.data:
            df_refined = df_refined[
                (pd.to_datetime(df_refined["Date"]) <= pd.to_datetime(form.end_date.data))
            ].reset_index(drop = True)
        if form.venue_filter.data:
            df_refined = df_refined[
                (df_refined["Venue"].isin(list(form.venue_filter.data)))
            ].reset_index(drop = True)
        if form.search_field.data:
            df_refined = df_refined[
                df_refined["Title"].str.lower().str.contains(form.search_field.data.lower()) |
                df_refined["Venue"].str.lower().str.contains(form.search_field.data.lower())
            ]
        if len(df_refined) < len(df):
            flash("Filter applied!")
    data_refined = df_refined.to_dict("records")
    contact_form = ContactForm()
    if contact_form.validate_on_submit():
        conn = smtplib.SMTP("smtp.gmail.com")
        my_email = os.getenv("GMAIL_USER_EMAIL")
        my_password = os.getenv("GMAIL_APP_PASSWORD")
        message = EmailMessage()
        message["From"] = my_email
        message["To"] = my_email
        message["subject"] = f"""{contact_form.name.data} ({contact_form.email.data}) has reached out from your website."""
        message.set_content(form.message.data)
        conn.starttls()
        conn.login(
            user = my_email,
            password = my_password
        )
        conn.send_message(message)
        conn.close()
        return(redirect(url_for("contact")))
    return(render_template(
        "gigs.html",
        data = data_refined,
        form = form,
        contact_form = contact_form,
        recaptcha_site_key = os.getenv("RECAPTCHA_PUBLIC_KEY")
    ))


# For refreshing filters on the MAIN GIGS page
@bp.route('/refresh_filters', methods = ["GET", "POST"])
def refresh_filters():
    username = request.args.get("username")
    if username:
        return(redirect(url_for("main.profile", username = username)))
    return(redirect(url_for('main.gigs', community_type = "following_users")))