import json
from scholasticate.location import Location
from flask import render_template, request, url_for, redirect, session
import scholasticate.database as db
from scholasticate.util import getUsefulUserInformation, render_template_wrapper

def route(app):
    @app.route('/acceptUser/<accepted_id>', methods=['POST'])
    def acceptUser(accepted_id):
        print("acceptUser called in route file!")
        userID = session.get('userID')
        if userID is None:
            return redirect(url_for('auth.login'))
        
        database = db.Database()
        user = database.get_student(int(userID))
        acceptedUser = database.get_student(int(accepted_id))
        if (acceptedUser is None):
            return "Invalid ID!"
        user.add_accepted(acceptedUser)

        return "200"