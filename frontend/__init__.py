from flask import Blueprint

bp = Blueprint('frontend', __name__, 
              template_folder='templates',
              static_folder='static',
              url_prefix='/app')

# Import views to register with blueprint
from .views import auth, forms, responses, users
