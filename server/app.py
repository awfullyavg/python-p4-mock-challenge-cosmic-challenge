#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientist_list = [scientist.to_dict(rules=('-missions',)) for scientist in Scientist.query.all()]
        return make_response(scientist_list, 200)
    
    def post(self):
        request_json = request.get_json()
        try:
            new_scientist = Scientist(name=request_json['name'], field_of_study=request_json['field_of_study'])
            db.session.add(new_scientist)
            db.session.commit()
            return make_response(new_scientist.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
api.add_resource(Scientists, '/scientists')



class Scientists_by_id(Resource):
    def get(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        return make_response(scientist.to_dict(), 200)
    

    def patch(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        try:
            request_json = request.get_json()
            for key in request_json:
                setattr(scientist, key, request_json[key])
            db.session.add(scientist)
            db.session.commit()
            return make_response(scientist.to_dict(), 202)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

    
    def delete(self, id):
        scientist = Scientist.query.filter(Scientist.id == id).first()
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        else:
            missions = Mission.query.filter(Mission.scientist_id == id).all()
            for mission in missions:
                db.session.delete(mission)
        db.session.delete(scientist)
        db.session.commit()
        return make_response({}, 204)
    
api.add_resource(Scientists_by_id, '/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        planet_list = [planet.to_dict(rules=('-missions',)) for planet in Planet.query.all()]
        return make_response(planet_list, 200)
api.add_resource(Planets, '/planets')

class Missions(Resource):
    def post(self):
        request_json = request.get_json()
        try:
            new_mission = Mission(name=request_json['name'], scientist_id=request_json['scientist_id'], planet_id=request_json['planet_id'])
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)
api.add_resource(Missions, '/missions')        



if __name__ == '__main__':
    app.run(port=5555, debug=True)
