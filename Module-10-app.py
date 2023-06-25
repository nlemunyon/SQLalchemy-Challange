# Import the dependencies.
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime

from flask import Flask, jsonify



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

# Flask Setup
#################################################
app = Flask(__name__)



# Flask Routes
#################################################
@app.route("/")
def Homepage():
    return (
        f"Welcome to my API Homepage<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<date>"
        f"/api/v1.0/<start>/<end>"
    )
@app.route("/api/v1.0/precipitation")
def Precipitation():
    session = Session(engine)
    year_prior='2016-08-23'
    recent='2017-08-23'
    results = session.query(Measurement).filter(Measurement.date>=year_prior).filter(Measurement.date<=recent).all()
    session.close()
    precipitation_amt = []
    both_values=[]
    date_values=[]
    rain_values=[]
    date_rain_dictionary={}


    for rain in results:
        if rain.date is not None and rain.date not in date_rain_dictionary:
           date_rain_dictionary[rain.date]=[]
        elif rain.prcp is not None:
            date_rain_dictionary[rain.date].append(rain.prcp)
    
    return jsonify(date_rain_dictionary)


@app.route("/api/v1.0/stations")
def Stations():
    session = Session(engine)
    station_results = session.query(Station).all()
    session.close()
    station_info=[]
    for info in station_results:
        station_dict={}
        station_dict["id"]=info.id
        station_dict["station"]=info.station
        station_dict["name"]=info.name
        station_dict["lat"]=info.latitude
        station_dict["lon"]=info.longitude
        station_dict["elevation"]=info.elevation
        station_info.append(station_dict)
    return(station_info)
            
@app.route("/api/v1.0/tobs")
def Tobs():
    #most active station: USC00519281. This was determined in part 1 of this assignment
    year_prior='2016-08-23'
    recent='2017-08-23'
    session = Session(engine)
    tobs_results = session.query(Measurement).filter(Measurement.station=='USC00519281').filter(Measurement.date>=year_prior).filter(Measurement.date<=recent).all()
    session.close()
    tobs_info=[]

    for item in tobs_results:
        tobs_dictionary={}
        tobs_dictionary={}
        tobs_dictionary['date']=item.date
        tobs_dictionary['Rain']=item.prcp
        tobs_info.append(tobs_dictionary)

    return(tobs_info)


@app.route("/api/v1.0/<date>")
def start_date(date):
    # Enter a start date in yyyy-mm-dd format
    date1 = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    session = Session(engine)

    # gathering min, max, and avg
    min_val = session.query(func.min(Measurement.tobs)).filter(Measurement.date > date1).scalar()
    max_val = session.query(func.max(Measurement.tobs)).filter(Measurement.date > date1).scalar()
    avg_val = session.query(func.avg(Measurement.tobs)).filter(Measurement.date > date1).scalar()

    session.close()

    
    return {"min_temperature": min_val,
            "max_temperature": max_val,
            "avg_temperature":round(avg_val,2)
    }

@app.route("/api/v1.0/<start>/<end>")
def start__end_date(start,end):
     # Enter a start date and end date in yyyy-mm-dd format
    date1 = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    date2 = datetime.datetime.strptime(end, "%Y-%m-%d").date()

    # gathering min, max, and avg
    session = Session(engine)
    min_val1 = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= date1).filter(Measurement.date <=date2).scalar()
    max_val1 = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= date1).filter(Measurement.date <=date2).scalar()
    avg_val1 = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= date1).filter(Measurement.date <=date2).scalar()
    session.close()

    return {"min_temperature": min_val1,
            "max_temperature": max_val1,
            "avg_temperature":round(avg_val1,2)
    }


if __name__ == '__main__':
    app.run(debug=True)



