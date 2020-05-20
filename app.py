import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#weather app
app = Flask(__name__)

maxDate = session.query(func.max(func.strftime("%Y-%m-%d", Measurement.date))).limit(5).all()
tempValMaxDate = list(np.ravel(maxDate))[0]
tempValMaxDate = dt.datetime.strptime(tempValMaxDate, '%Y-%m-%d')
yearAgo = tempValMaxDate - dt.timedelta(weeks=52.2)

stations = (session.query(Measurement.station, func.count(Measurement.station))
                        .group_by(Measurement.station)
                        .order_by(func.count(Measurement.station).desc())
                        .all())

stationID = stations[0][0]



session.close()

@app.route("/")
def home():
    return (f"Welcome to Hawaii's Climate: Surf's Up <br>"
            f"Available Routes: <br>"
            f"/api/v1.0/stations <br>"
            f"/api/v1.0/precipitation <br>"
            f"/api/v1.0/temperature <br>"
            f"/api/v1.0/<start> <br>"
            f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()

    all_stations = list(np.ravel(results))
    return jsonify(all_stations)
   

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = (session.query(Measurement.date, Measurement.prcp)
                      .filter(Measurement.date > yearAgo)
                      .group_by(Measurement.date)
                      .order_by(Measurement.date)
                      .all())
    
    session.close()

    precipDict = {}
    for result in results:
        precipDict.update({result.date: result.prcp})

    return jsonify(precipDict)

@app.route("/api/v1.0/temperature")
def temperature():
    session = Session(engine)
    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.station == stationID)
                      .filter(Measurement.date > yearAgo)
                      .group_by(Measurement.date)
                      .order_by(Measurement.date)
                      .all())
    
    session.close()

    tempList = []
    for result in results:
        tempDict = {result.date: result.tobs, "Station": result.station}
        tempList.append(tempDict)

    return jsonify(tempList)

@app.route("/api/v1.0/<start>")
def startdate(yearAgo):
    session = Session(engine)

    session.close()


if __name__ == '__main__':
    app.run(debug=True)
