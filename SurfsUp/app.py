# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()
print(Base.classes.keys())

# Save references to each table
Measurement = Base.classes.measurement

Station = Base.classes.station

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#1 - Homepage
@app.route("/")
def welcome():
  #  """List all available api routes."""
    return (
       "<div style='text-align: center; color: blue; font-family: Arial, sans-serif;'>"
        "<h1>Welcome to the Climate Data API</h1>"
        "<p>Available Links for Climate App:</p>" 
         

        "<div style='display: flex; flex-direction: column; align-items: center;'>" 
        f"<br/><a href='/api/v1.0/precipitation'> Precipitation</a><br/>"
       
        f"<br/><a href='/api/v1.0/stations'>Stations </a> <br/>"
        f"<br/>Link below shows the data for Station - USC00519281 <br/>"
        f"<br/><a href='/api/v1.0/tobs'> /api/v1.0/tobs </a> <br/>"

        f"<br/>Link below is dynamic and requires route as in ex:/api/v1.0/2016-08-23 <br/>"
        f"<br/><a href='/api/v1.0/&lt;start&gt'> /api/v1.0/&lt;start&gt</a> <br/>"
        f"<br/><a href='/api/v1.0/2016-11-10'> Start Date 2016-11-10</a> <br/>"

        f"<br/>Link below is dynamic and requires route as in ex:/api/v1.0/2016-08-23/2017-08-23 <br/>"
        f"<br/><a href='/api/v1.0/&lt;start&gt;/&lt;end&gt'> /api/v1.0/&lt;start&gt;/&lt;end&gt</a><br/> "
         f"<br/><a href='/api/v1.0/2016-08-23/2017-08-23'> Start Date 2016-08-23 - End Date 2017-08-23</a><br/> "
       
         "</div>"
         "</div>"
    )


#2 - Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
#Create link session   
   session = Session(engine)

# list of stations from the dataset
   most_recent_record = session.query(Measurement).order_by(func.datetime(Measurement.date).desc()).first()
   most_recent_date = datetime.strptime(most_recent_record.date, '%Y-%m-%d').date()

#find the start date from the most recent date we have in the dataset.
   start = most_recent_date - timedelta(days=365)
   date_prcp = session.query(Measurement.date,Measurement.prcp).filter(Measurement.date >= start).all()
   session.close()
   prcp_data = {date: prcp for date, prcp in date_prcp}
   return jsonify(prcp_data)
 

#3 - Stations   
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_no = session.query(Station.station,Station.name).all()
    session.close()
    station_data = {station: name for station,name in station_no}
    return jsonify(station_data)
#Query the dates and temperature observations of the most-active station for the previous year of data

#4 - Tobs
@app.route("/api/v1.0/tobs")
def tobs():
    # 
    session = Session(engine)
    most_recent_record = session.query(Measurement).filter(Measurement.station == 'USC00519281').order_by(func.datetime(Measurement.date).desc()).first()
    most_recent_record.date
    most_recent_date = datetime.strptime(most_recent_record.date, '%Y-%m-%d').date()
    start = most_recent_date - timedelta(days=365)

    tobs_data = session.query(Measurement.station,Measurement.date,Measurement.prcp,Measurement.tobs).filter(Measurement.date >= start).filter(Measurement.station == 'USC00519281').all()
    session.close()
    station_tobs_data = [{'station': (e[0]), 'date': (e[1]),'prcp':(e[2]),'tobs':(e[3])} for e in tobs_data]
    
    return jsonify(station_tobs_data)    

#5 - Start and End - pull the min,max and average.

@app.route("/api/v1.0/<start>")
def start_date(start):
   
    session = Session(engine)
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""
    start_tobs = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    session.close()

    start_tobs_list = []
    for min, max, avg in start_tobs:
        start_dict = {}
        start_dict["min"] = min
        start_dict["max"] = max
        start_dict["avg"] = avg
        start_tobs_list.append(start_dict)
    return jsonify(start_tobs_list)

# Start and End date.
@app.route("/api/v1.0/<start>/<end>")
def start_date_end(start,end):
    
    session = Session(engine)
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range."""
    start_end_tobs = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    start_tobs_list = []
    for min, max, avg in start_end_tobs:
        start_dict = {}
        start_dict["min"] = min
        start_dict["max"] = max
        start_dict["avg"] = avg
        start_tobs_list.append(start_dict)
    return jsonify(start_tobs_list)
if __name__ == '__main__':
    app.run(debug=False)