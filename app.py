# Import dependencies
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
import datetime as dt

from flask import Flask, jsonify


# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station


# Flask Setup 
app = Flask(__name__)


# Flask Routes
@app.route("/")
def welcome():
    return (
    f"Welcome to the Honolulu Climate API!<br/>"
    f"Available Routes:<br/>"
    f"Precipitation data: /api/v1.0/precipitation<br/>"
    f"List of stations: /api/v1.0/stations<br/>"
    f"Temperature data for latest year: /api/v1.0/tobs<br/>"
    f"Temperature data from a start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
    f"Temperature data from a start to end date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
)



# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    queryresult = session.query(Measurement.date,Measurement.prcp).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation (Inches)"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)


# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
        session = Session(engine)
        queryresult = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
        session.close()
        
        stations = []
        for station,name,lat,long,elev in queryresult:
            station_dict = {}
            station_dict["Station"] = station
            station_dict["Name"] = name
            station_dict["Latitude"] = lat
            station_dict["Longitude"] = long
            station_dict["Elevation"] = elev
            stations.append(station_dict)
            
        return jsonify(stations)


# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    latestdate = dt.datetime.strptime(latest_date[0], "%Y-%m-%d")
    startdate = dt.date(latestdate.year -1, latestdate.month, latestdate.day)
    
    active_station = session.query(Measurement.station,func.count(Measurement.id)).group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).first()[0]
    
    queryresult = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= startdate).filter(Measurement.station == active_station).all()
    session.close()
    
    tobs_year = []
    for row in queryresult:
        tobs_dict = {}
        tobs_dict["Date"] = dt.datetime.strptime(row[0],"%Y-%m-%d").date()
        tobs_dict["Temperature (deg F)"] = row[1]
        tobs_year.append(tobs_dict)

    return jsonify(tobs_year)

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
def get_temps_start(start):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    session.close()

    tobs = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Minimum Temperature (deg F)"] = min
        tobs_dict["Average Temperature (deg F)"] = avg
        tobs_dict["Maximum Temperature (deg F)"] = max
        tobs.append(tobs_dict)

    return jsonify(tobs)


# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<stop>")
def get_temps_start_stop(start,stop):
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= stop).all()
    session.close()

    tobs = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Minimum Temperature (deg F)"] = min
        tobs_dict["Average Temperature (deg F)"] = avg
        tobs_dict["Maximum Temperature (deg F)"] = max
        tobs.append(tobs_dict)

    return jsonify(tobs)


# Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
