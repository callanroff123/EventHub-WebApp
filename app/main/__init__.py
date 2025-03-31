from flask import Blueprint


# Use blueprints to make components of the app more independent of the application instance
# i.e., promotes portability/re-usability 
bp = Blueprint("main", __name__)


# Import at bottom to avoid circular dependencies
# Register the application-specific routes with Flask Blueprint
# I.e., the stuff that's more specific to the application (whereas errors and auth are more resusable across apps)
from app.main import routes, forms