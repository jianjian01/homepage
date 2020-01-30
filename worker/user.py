import json
import logging
import random
import string

from flask import request, render_template, current_app, jsonify, session, redirect, Blueprint

from db import User, UserStatus
from flask_app import flask_app as app, redis

user_bp = Blueprint('user', __name__, template_folder='templates')
