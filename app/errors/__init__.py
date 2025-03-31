from flask import Blueprint


# Use blueprints to make components of the app more independent of the application instance
# i.e., promotes portability/re-usability 
bp = Blueprint("errors", __name__)


# Import at bottom to avoid circular dependencies
# Register the error handler routes with  the "errors" Flask Blueprint
from app.errors import handlers