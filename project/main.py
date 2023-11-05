from db import db
from models import AppointmentDAO
from flask import Flask, render_template, request,current_app, redirect, url_for, jsonify
from flask_restful import reqparse, abort, Api, Resource
import logging
import functools
from datetime import datetime

#creating the app
app = Flask(__name__)
api = Api(app)

#configuring the sql database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///appointments.db"

#configuring the app with the extension
db.init_app(app)

# Logger for database creation
db_creation_logger = logging.getLogger("DatabaseCreation")
db_creation_logger.setLevel(logging.INFO)  # Set the logging level to INFO
db_creation_handler = logging.FileHandler("db_creation.log")  # Log file for database creation
db_creation_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
db_creation_logger.addHandler(db_creation_handler)

# Logger for querying
query_logger = logging.getLogger("DatabaseQuery")
query_logger.setLevel(logging.INFO)  # Set the logging level to INFO
query_handler = logging.FileHandler("query.log")  # Log file for database queries
query_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
query_logger.addHandler(query_handler)

# creating a database like the blueprint in models.py
with app.app_context():
    db.create_all()

def persistData(aDict, r = False):
    """
    This function wil convert the given dictionary into a AppointmentDAO object and persists it to the database.

    Args:
        aDict: dictionary to convert.
        r: Set this to true when data is received as JSON from the API.

    Returns:
        Nothing.
    """
    tijd_in_seconden = berekenverschil(aDict["duurtijd"], aDict["starttijd"],r)
    startTijd = datetime.strptime(aDict["starttijd"],"%d-%m-%y %H:%M") if r else datetime.strptime(aDict["starttijd"],"%Y-%m-%dT%H:%M")
    afspraak = AppointmentDAO(titel = aDict["titel"],
                              starttijd = startTijd,
                              duurtijd = tijd_in_seconden)
    # appointmentList.append(afspraak)
    db.session.add(afspraak)
    db.session.commit()

def berekenverschil(timeA,timeB, r = False):
    timeObjA = datetime.strptime(timeA,"%d-%m-%y %H:%M") if r else datetime.strptime(timeA,"%Y-%m-%dT%H:%M")
    timeObjB = datetime.strptime(timeB,"%d-%m-%y %H:%M") if r else datetime.strptime(timeB,"%Y-%m-%dT%H:%M")
    return (timeObjA - timeObjB).total_seconds()

def get_afspraak_by_id(afspraakID):
    try:
        # Query the database using SQLAlchemy to retrieve afspraak by ID
        afspraak = AppointmentDAO.query.filter_by(id=afspraakID).first()
        return afspraak
    except Exception as e:
        # Handle any exceptions that might occur during the database query
        print(f"Error: {str(e)}")
        return None  # Return None if an error occurs

def logIO(logger=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Zoek naar de logger in verschillende bronnen
            nonlocal logger
            if logger is None:
                caller_obj = args[0]  # De eerste parameter is altijd de caller (bij een methode)
                logger = getattr(caller_obj, "logger", None)  # Zoek in de caller
                if logger is None:
                    class_obj = caller_obj.__class__  # Haal de klasse van de caller op
                    logger = getattr(class_obj, "logger", None)  # Zoek in de klasse van de caller

            try:
                input_args = args, kwargs
                result = func(*args, **kwargs)
                log_message = f"Inputs: {input_args}, Output: {result}"
                logger.info(log_message)
                return result
            except Exception as e:
                if logger:
                    log_message = f"Error: {str(e)}"
                    logger.error(log_message)
                raise

        return wrapper
    return decorator

# appointmentList = []

@app.route("/nieuw", methods = ["POST", "GET"])
@logIO(db_creation_logger)
def formHandler():
    if request.method == "GET":
        return current_app.send_static_file("form.html")
    else:
        aDict = {
            "titel": request.form.get("titel"),
            "startTijd":request.form.get("starttijdstip"),
            "duurtijd": request.form.get("duurtijd")
        }
        persistData(aDict)
        return redirect(url_for('formHandler'))

@app.route("/zoek", methods = ["GET", "POST"])
@logIO(query_logger)
def zoekAfspraak():
    if request.method == "GET":
        return current_app.send_static_file("zoekForm.html")
    else:
        gevonden_afspraken = []
        titel = request.form.get("titel")
        # for afspraak in appointmentList:
        #     if afspraak.titel == titel:
        #         gevonden_afspraken.append(afspraak)

        afspraken = AppointmentDAO.query.filter_by(titel=titel).order_by(AppointmentDAO.titel).all()
        for afspraak in afspraken:
            duurtijd_afspraak = afspraak.duurtijd/3600
            formatted_duurtijd = f"{duurtijd_afspraak:.2f}"
            afspraak_dict = {
                "afspraak": afspraak,
                "duurtijd": formatted_duurtijd
            }
            gevonden_afspraken.append(afspraak_dict)
        return render_template("afspraak.html", data = gevonden_afspraken)

parser = reqparse.RequestParser()
parser.add_argument('titel')
parser.add_argument('starttijd')
parser.add_argument('duurtijd') 

class Afspraak(Resource):
    @logIO(query_logger)
    def get(self):
        afspraak_lijst = []
        afspraken = db.session.execute(db.select(AppointmentDAO).order_by(AppointmentDAO.titel)).scalars()
        for afspraak in afspraken: 
            duurtijd_afspraak = afspraak.duurtijd/3600
            formatted_duurtijd = f"{duurtijd_afspraak:.2f}"
            afspraakDict = {
                "titel": afspraak.titel,
                "starttijd": afspraak.starttijd.strftime("%d-%m-%y %H:%M"),
                "duurtijd": formatted_duurtijd + " uur"
            }
            afspraak_lijst.append(afspraakDict)
        if afspraak_lijst:
            return afspraak_lijst
        else:
            return {"message": "geen afspraken gevonden"}, 404
        
    @logIO(db_creation_logger)
    def post(self):
            args = parser.parse_args()
            reqdata = {
                "titel": args["titel"],
                "starttijd": args["starttijd"],
                "duurtijd": args["duurtijd"]
            }
            print(reqdata)
            persistData(reqdata,True)
            return "de request is succesvol verwerkt"    


api.add_resource(Afspraak, '/afspraak')   

class AfspraakResource(Resource):
    def get(self, afspraak_id):
        # Retrieve afspraak from the database based on afspraak_id
        afspraak = get_afspraak_by_id(afspraak_id)  # Implement this function to retrieve afspraak from the database
        if afspraak:
            # Convert afspraak object to a dictionary or serialize it as needed
            afspraak_data = {
                "id": afspraak.id,
                "titel": afspraak.titel,
                "starttijd": afspraak.starttijd.strftime("%Y-%m-%dT%H:%M:%S"),
                "duurtijd": afspraak.duurtijd
            }
            return afspraak_data
        else:
            return {"message": "Afspraak niet gevonden"}, 404

# Add the resource to the Flask-RESTful Api
api.add_resource(AfspraakResource, '/afspraak/<int:afspraak_id>')
    
if __name__ == "__main__":
    app.run(debug=True)