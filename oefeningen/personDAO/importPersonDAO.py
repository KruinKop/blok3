from db import Model, Session, engine
from models import PersonDAO
from datetime import datetime, timedelta

geboortedatum = datetime(1994,3,31,14,3)
velatenZiekenhuis = datetime(1994,4,1,17,45)
verschil = velatenZiekenhuis-geboortedatum

def main():
    Model.metadata.drop_all(engine)
    Model.metadata.create_all(engine)
    with Session() as session:
        with session.begin():
            ikke = PersonDAO(voornaam = "Jesse", familienaam = "Zaenen", geboortetijdstip = geboortedatum , verblijfsduur = verschil.total_seconds())
            session.add(ikke)
            
if __name__ == "__main__":
    main()