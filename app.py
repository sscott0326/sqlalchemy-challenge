#Import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import and_, or_

#Import Flask
from flask import Flask, jsonify

#Import NumPy
import numpy as np

#Import Mean
from scipy import mean

#Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#Reflect existing database
Base = automap_base()

#Reflect tables
Base.prepare(engine, reflect=True)

#Save references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Setup
app = Flask(__name__)

#Routes
@app.route("/")
def home():
    '''List API Routes'''
    return (
        f"Welcome!<br/>"
        f"<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"For temperature data given a start and end date, <br/>"
        f"please enter in format (mm-dd-yyyy). Do not add 0 before months 1-9.<br/>"
        f"Start route: /api/v1.0/<start><br/>"
        f"Start/end route: /api/v1.0/<start>/<end><br/>"
        )   

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create session link to DB
    session = Session(engine)

    #Query for last 12 months of precipitation data
    past_year = (session
             .query(Measurement.date, Measurement.prcp)
             .filter(Measurement.date > '2016-08-23')
             .order_by(Measurement.date)
             .all()
            )
    session.close()

    #Create dictionary from query and append to a list
    all_prcp = []
    for date, prcp in past_year:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)
    
    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    #Create session link to DB
    session = Session(engine)

    #Query all station names
    station_query = session.query(Station.name).all()

    session.close()

    #Convert list of tuples to list
    all_stations = list(np.ravel(station_query))

    return jsonify(all_stations)

    

@app.route("/api/v1.0/tobs")
def tobs():
    #Create session link to DB
    session = Session(engine)
    past_year_active = (session.
                        query(Measurement.tobs, Measurement.date).
                        filter(
                             and_(
                                Measurement.date > '2016-08-18',
                                Measurement.station == 'USC00519281')).
                                all()
                         )
    session.close()

     #Create dictionary from query and append to a list
    active_temp = []
    for date, tobs in past_year_active:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        active_temp.append(temp_dict)
    
    return jsonify(active_temp)


@app.route("/api/v1.0/<start>")
def start(start):
    #Create session link to DB
    session = Session(engine)

    lowest_temp = (session.
               query(Measurement.tobs).
               filter(Measurement.date >= start).
               order_by(Measurement.tobs).
               first()
              )

    highest_temp = (session.
                query(Measurement.tobs).
                filter(Measurement.date >= start).
                order_by(Measurement.tobs.desc()).
                first()
               )

    #Filter out any null values from tobs column then find average of remaining list
    temps = (session.
         query(Measurement.tobs).
         filter(Measurement.date >= start)
        )
    not_null_temps = []
    for temp in temps:
        if type(temp.tobs) == float:
            not_null_temps.append(temp.tobs)
    avg_temp = mean(not_null_temps)

    return (
        f"Start date: {start}<br/>"
        f"<br/>"
        f"Temperature Data:<br/>"
        f"TMIN: {lowest_temp}<br/>"
        f"TMAX: {highest_temp}<br/>"
        f"TAVG: {avg_temp}<br/>"
        )

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    #Create session link to DB
    session = Session(engine)

    lowest_start_end = (session.
                        query(Measurement.tobs).
                        filter(
                            and_(
                                Measurement.date >= start,
                                Measurement.date <= end
                                )).
                        order_by(Measurement.tobs).
                        first()     
                        )

    highest_start_end = (session.
                        query(Measurement.tobs).
                        filter(
                            and_(
                                Measurement.date >= start,
                                Measurement.date <= end
                            )).
                        order_by(Measurement.tobs.desc()).
                        first()
                            
                        ) 

    #Filter out any null values from tobs column then find average of remaining list
    temps_start_end = (session.
                        query(Measurement.tobs).
                        filter(
                            and_(
                                Measurement.date >= start,
                                Measurement.date <= end
                                )
                            )
                        )

    not_null_temps_start_end = []
    for temp in temps_start_end:
        if type(temp.tobs) == float:
            not_null_temps_start_end.append(temp.tobs)
    avg_temp_start_end = mean(not_null_temps_start_end)

    return (
        f"Start date: {start}<br/>"
        f"End date: {end}<br/>"
        f"<br/>"
        f"Temperature Data:<br/>"
        f"TMIN: {lowest_start_end}<br/>"
        f"TMAX: {highest_start_end}<br/>"
        f"TAVG: {avg_temp_start_end}<br/>"
        )


    return ""


if __name__ == "__main__":
    app.run(debug=True)