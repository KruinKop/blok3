from db import Model, Session, engine
session = Session()
from models import PersonDAO
from sqlalchemy import select
from flask import Flask, render_template, request,current_app
import logging
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(filename='peopleDB.log', encoding='utf-8', level=logging.DEBUG)

# creating a database like the blueprint in models.py
Model.metadata.create_all(engine)

personList = []
formData = {}

def berekenverschil(timeA,timeB):
    timeObjA = datetime.strptime(timeA,"%Y-%m-%dT%H:%M")
    timeObjB = datetime.strptime(timeB,"%Y-%m-%dT%H:%M")
    return (timeObjA - timeObjB).total_seconds()

def persistData(pdict):
    verschil = berekenverschil(pdict["vertrekdatum"],pdict["geboortedatum"])
    with Session() as session:
        with session.begin():
            person = PersonDAO(voornaam = pdict["voornaam"] , familienaam = pdict["familienaam"], 
            geboortetijdstip = datetime.strptime(pdict["geboortedatum"],"%Y-%m-%dT%H:%M"),
            verblijfsduur = verschil)
            session.add(person)

@app.route("/")
def showEntries():
    from sqlalchemy import select
    q = select(PersonDAO)
    res = session.execute(q).all()
    print(res)
    for person in res: #altijd index 0 gebruiken op de verschillende teruggekregen tuples
        verblijfsdUUR = person[0].verblijfsduur/3600
        fVerblijf = f"{verblijfsdUUR:.2f}"
        personDict = {
            "voornaam": person[0].voornaam,
            "achternaam": person[0].familienaam,
            "geboortedatum": person[0].geboortetijdstip.strftime("%d-%m-%y %H:%M:%S"),
            "verblijfsduur": fVerblijf + " uur"
        }
        personList.append(personDict)
        # pretty printing the dictionary
    return render_template("index.html", data = personList)

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

            