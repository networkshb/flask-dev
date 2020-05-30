from flask import Blueprint

print(100)
api = Blueprint('api', __name__)
print(200)

from . import views

