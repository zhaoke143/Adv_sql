from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect, desc


engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# We can view all of the classes that automap found
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)


app = Flask(__name__)


@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f"routes:<br/>"
        
        f"<br/>/api/v1.0/precipitation<br/>"
        f"Dates and temperature data from the last year<br/>"

        f"<br/>/api/v1.0/stations<br/>"
        f"List of stations<br/>"

        f"<br/>/api/v1.0/tobs<br/>"
        f"Temperature data from the past year<br/>"

        f"<br/>start format is %Y-%m-%d<br/>"
        f"example /api/v1.0/2000-01-01<br/>"
        f"Min temperature, the avg temperature, and max temperature for start<br/>"

        f"<br/>api/v1.0/start/end<br/><br/>"
        f"example: /api/v1.0/2000-01-08/2016-01-09<br/>"
        f"Min temperature, the avg temperature, and max temperature for start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    print('receive request from prec page')
    data_prec = session.query(Measurement.date, func.sum(Measurement.prcp)).group_by(Measurement.date)
    prec1 = {}
    for x in data_prec:
        prec1.update({x[0]: x[1]})
    return jsonify(prec1)
    

@app.route("/api/v1.0/stations")
def station():
    print('receive request from station page')
    data_station = session.query(Station.station).all()
    station_name = list(np.ravel(data_station))
    return jsonify(station_name)

    

@app.route("/api/v1.0/tobs")
def temp():
    print('received request from temperature page')
    last_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]   
    last_day_dt = dt.datetime.strptime(last_day, '%Y-%m-%d').date()
    last12m = last_day_dt - dt.timedelta(days=365)
    data_temp = session.query(Station.station, Measurement.date, Measurement.prcp).filter(Measurement.date >= last12m).\
        filter(Measurement.station == Station.station).all()
    data_goaway = list(np.ravel(data_temp))
    return jsonify(data_goaway)

@app.route("/api/v1.0/<start>")
def api1(start):
    x=str(start)
    print("received request from 'start page'")
    data4 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)). \
        filter(Measurement.date >= x).all()
    start1 = {}
    start1.update({"Tmin": data4[0][1], "Tavg": data4[0][1], "Tmax": data4[0][2]})
    return jsonify(start1)

@app.route("/api/v1.0/<start>/<end>")
def api2(start,end):
    x=str(start)
    y=str(end)
    print("received request from 'start/end page'")
    data5 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)). \
        filter(Measurement.date >= x).filter(Measurement.date <= y).all()
    data_end = {}
    data_end.update({"START_DATE":x ,"TMIN": data5[0][1], "TAVG": data5[0][1], "TMAX": data5[0][2],"END_DATE":y})
    return jsonify(data_end)



if __name__=="__main__":
    app.run(debug=True)