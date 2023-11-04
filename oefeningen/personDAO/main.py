from db import db
from models import PersonDAO
from flask import Flask, render_template, request,current_app
from flask_restful import reqparse, abort, Api, Resource
import logging
from datetime import datetime

#creating the app
app = Flask(__name__)
api = Api(app)

#configuring the sql database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///people.db"

#configuring the app with the extension
db.init_app(app)

logging.basicConfig(filename='peopleDB.log', encoding='utf-8', level=logging.DEBUG)

# creating a database like the blueprint in models.py
with app.app_context():
    db.create_all()

formData = {}

def berekenverschil(timeA,timeB, r = False):
    timeObjA = datetime.strptime(timeA,"%d-%m-%y %H:%M") if r else datetime.strptime(timeA,"%Y-%m-%dT%H:%M")
    timeObjB = datetime.strptime(timeB,"%d-%m-%y %H:%M") if r else datetime.strptime(timeB,"%Y-%m-%dT%H:%M")
    return (timeObjA - timeObjB).total_seconds()

def persistData(pdict, r = False):
    verschil = berekenverschil(pdict["vertrekdatum"],pdict["geboortedatum"], r)
    ts = datetime.strptime(pdict["geboortedatum"],"%d-%m-%y %H:%M") if r else datetime.strptime(pdict["geboortedatum"],"%Y-%m-%dT%H:%M")
    print(ts)
    person = PersonDAO(voornaam = pdict["voornaam"],
                       familienaam = pdict["familienaam"],
                       geboortetijdstip =  ts,
                       verblijfsduur = verschil)
    db.session.add(person)
    db.session.commit()

parser = reqparse.RequestParser()
parser.add_argument('voornaam')
parser.add_argument('familienaam')
parser.add_argument('geboortedatum')
parser.add_argument('vertrekdatum')

class Person(Resource):
    def get(self):
        personList = []
        persons = db.session.execute(db.select(PersonDAO).order_by(PersonDAO.voornaam)).scalars()
        print(persons)
        for person in persons: 
            verblijfsdUUR = person.verblijfsduur/3600
            fVerblijf = f"{verblijfsdUUR:.2f}"
            personDict = {
                "voornaam": person.voornaam,
                "familienaam": person.familienaam,
                "geboortedatum": person.geboortetijdstip.strftime("%d-%m-%y %H:%M:%S"),
                "verblijfsduur": fVerblijf + " uur"
            }
            personList.append(personDict)
        return personList
    
    def post(self):
        args = parser.parse_args()
        reqdata = {
            "voornaam": args["voornaam"],
            "familienaam": args["familienaam"],
            "geboortedatum": args["geboortedatum"],
            "vertrekdatum": args["vertrekdatum"]
        }
        print(reqdata)
        persistData(reqdata, True)
        return "de request is succesvol verwerkt"
        
    
api.add_resource(Person, '/persons')

@app.route("/")
def showEntries():
    PersonDAO.update_access_time()
    personList = []
    persons = db.session.execute(db.select(PersonDAO).order_by(PersonDAO.voornaam)).scalars()
    print(persons)
    for person in persons: 
        verblijfsdUUR = person.verblijfsduur/3600
        fVerblijf = f"{verblijfsdUUR:.2f}"
        personDict = {
            "voornaam": person.voornaam,
            "familienaam": person.familienaam,
            "geboortedatum": person.geboortetijdstip.strftime("%d-%m-%y %H:%M:%S"),
            "verblijfsduur": fVerblijf + " uur"
        }
        personList.append(personDict)
    last_access_time = PersonDAO.last_used  # Haal de laatste toegangstijd op
    return render_template("index.html", data = personList, tijdstip = last_access_time)

@app.route("/peoplesform", methods = ["POST", "GET"])
def formHandler():
    if request.method == "GET":
        return current_app.send_static_file("form.html")
    else:
        formdata = {
            "voornaam": request.form.get("voornaam"),
            "familienaam": request.form.get("familienaam"),
            "geboortedatum": request.form.get("geboortedatum"),
            "vertrekdatum": request.form.get("vertrekdatum")
        }
        print(formdata)
        persistData(formdata)
        return "het formulier is succesvol verwerkt"

            