# Import the dependencies.
from flask import Flask, jsonify
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


#################################################
# Database Setup
#################################################
# Create an engine for the hawaii.sqlite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)
Base.classes.keys()


station= Base.classes.station
measurement= Base.classes.measurement

#################################################
# Flask Setup
#################################################
# Create a Flask app instance
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# Define the homepage route
@app.route('/')
def homepage():
    return (
        f"Welcome to the Climate app for surfers!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )



#set up app pages
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    all_stations = session.query(station.station).all()

    session.close()

    station_names = [row.station for row in all_stations]

    return jsonify(station_names)



#set up app page
@app.route("/api/v1.0/precipitation")

def precipitation():
    session = Session(engine)

    latest_date = session.query(func.max(measurement.date)).scalar()
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    year_ago = latest_date - dt.timedelta(days=365)
    precipitation_data = session.query(measurement.date, measurement.prcp)\
        .filter(measurement.date >= year_ago)\
        .all()
    
    session.close()

    prcp_dict = {}

    for date, prcp in precipitation_data:
        prcp_dict[date] = prcp

    return jsonify(prcp_dict)


#set up app page
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

# find most active station
    most_active_station = session.query(measurement.station)\
        .group_by(measurement.station)\
        .order_by(func.count(measurement.station).desc())\
        .first()[0]
    
# find date range for the previous year
    latest_date = session.query(func.max(measurement.date)).scalar()
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    year_ago = latest_date - dt.timedelta(days=365)
    
# temp observations for the most active station in the previous year
    results = session.query(measurement.date, measurement.tobs)\
        .filter(measurement.station == most_active_station)\
        .filter(measurement.date >= year_ago)\
        .all()
# Close the session
    session.close()
    
# Convert the results into a list of dictionaries
    tobs_data = []
    for date, tobs in results:
        tobs_data.append({'date': date, 'temperature': tobs})
    
    return jsonify(tobs_data)  




@app.route('/api/v1.0/<start>')
def temp_stats_start(start):
# Create a session
    session = Session(engine)
    
# Convert start date to datetime object
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    
# temp stats for dates greater than or equal to start date
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
        .filter(measurement.date >= start_date)\
        .all()
    
# Close the session
    session.close()

 # Extract temperature statistics
    tmin, tavg, tmax = results[0]
    
# Return JSON response
    return jsonify({'TMIN': tmin, 'TAVG': tavg, 'TMAX': tmax})




#app page
@app.route('/api/v1.0/<start>/<end>')
def temp_stats_start_end(start, end):
# Create a session
    session = Session(engine)
    
# Convert start and end dates to datetime objects
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')
    
# temperature stats for dates between start and end dates
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(Measurement.tobs))\
        .filter(measurement.date >= start_date)\
        .filter(measurement.date <= end_date)\
        .all()
    
# Close the session
    session.close()

#temperature stats
    tmin, tavg, tmax = results[0]
    
# Return JSON response
    return jsonify({'TMIN': tmin, 'TAVG': tavg, 'TMAX': tmax})


if __name__ == "__main__":
    app.run(debug=True)








