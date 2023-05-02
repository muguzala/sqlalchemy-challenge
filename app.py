# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import pandas as pd
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d').date()
    
    one_year_ago = recent_date - dt.timedelta(days=365)
    query_results = session.query(Measurement.date, Measurement.prcp).\
                filter(Measurement.date >= one_year_ago).all()
 

    session.close()

    precipitation = []
    for date,prcp in query_results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    all_names = list(np.ravel(results))
    
    return jsonify(all_names)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
                      group_by(Measurement.station).\
                      order_by(func.count(Measurement.station).desc()).all()

    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    recent_date = dt.datetime.strptime(recent_date[0], '%Y-%m-%d').date()
    
    one_year_ago = recent_date - dt.timedelta(days=365)
    most_active_station_id = most_active_stations[0][0]
    query_results = session.query(Measurement.tobs).\
                filter(Measurement.date >= one_year_ago).filter(Measurement.station == most_active_station_id).all()

    session.close()
    all_names = list(np.ravel(query_results))
    
    return jsonify(all_names)


@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    query_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
             filter(Measurement.date >= start_date).all()

    session.close()
    all_names = list(np.ravel(query_results))
    
    return jsonify(all_names)





@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    session = Session(engine)
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    query_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
             filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()
    all_names = list(np.ravel(query_results))
    
    return jsonify(all_names)

if __name__ == '__main__':
    app.run(debug=True)
