from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectMultipleField, RadioField, EmailField, TextAreaField
from flask_wtf.recaptcha import RecaptchaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length


class FilterForm(FlaskForm):

    user_filter = RadioField(
        label = "Filter Events",
        choices = [
            ("following_only", "Following"),
            ("me", "My Events"),
            ("interested_in", "Interested In"),
            ("all_events", "All")
        ],
        default = "all_events"
    )

    start_date = DateField(
        label = "From: ", 
        format = "%Y-%m-%d"
    )
    end_date = DateField(
        label = "To: ", 
        format = "%Y-%m-%d"
    )
    just_in = RadioField(
        label = "",
        choices = ["All", "Just In"],
        default = "All"
    )
    venue_filter = SelectMultipleField(
        label = "Filter Venues: ",
        choices = []
    )
    genre_filter = SelectMultipleField(
        label = "Filter Genres: ",
        choices = []
    )
    search_field = StringField(
        label = "Keyword: "
    )
    submit = SubmitField("OK")

    def __init__(self, default_venues = None, default_genres = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.venue_filter.choices = default_venues or []
        self.genre_filter.choices = default_genres or []


class ContactForm(FlaskForm):

    name = StringField(
        label = "Name: ",
        validators = [DataRequired(message = "Please Enter this Field.")]
    )
    email = EmailField(label = "Email: ")
    message = TextAreaField(
        label = "Message: ",
        validators = [DataRequired(message = "Please Enter this Field.")],
        render_kw = {
            "rows": 5
        }
    )
    recaptcha = RecaptchaField()
    submit = SubmitField(label = "Send")
