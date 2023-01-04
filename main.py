from flask import Flask,render_template,request,redirect
from database_management import *

# app=Flask(__name__)

# @app.route('/')
# def home():
#     return render_template('home.html')

delete_tables()

create()