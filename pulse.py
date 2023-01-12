# -*- coding: utf-8 -*-
import sys
import websocket
import ssl
import json
import _thread
import time
import datetime
import calendar
import os
import logging

from gql import Client, gql
from gql.transport.websockets import WebsocketsTransport
from influxdb import InfluxDBClient
from dateutil.parser import parse
import requests

# settings from EnvionmentValue
influxhost=os.getenv('INFLUXDB_HOST', "localhost")
influxport=os.getenv('INFLUXDB_PORT', 8086)
influxuser=os.getenv('INFLUXDB_USER', 'root')
influxpw=os.getenv('INFLUXDB_PW', 'root')
influxdb=os.getenv('INFLUXDB_DATABASE', 'tibberPulse')
tibbertoken=os.getenv('TIBBER_TOKEN', 'NOTOKEN')
tibberhomeid=os.getenv('TIBBER_HOMEID', 'NOID')

global adr
adr = "DEFAULT"
headers = {"Authorization": "Bearer "+tibbertoken}

subscription_query = """
subscription {{
    liveMeasurement(homeId:"{home_id}"){{
        timestamp
        power
        accumulatedConsumption
        accumulatedCost
        voltagePhase1
        voltagePhase2
        voltagePhase3
        currentL1
        currentL2
        currentL3
        lastMeterConsumption
    }}
}}
""".format(home_id=tibberhomeid)

influx_client = InfluxDBClient(influxhost, influxport, influxuser, influxpw, influxdb)

def ifStringZero(val):
    val = str(val).strip()
    if val.replace('.','',1).isdigit():
      res = float(val)
    else:
      res = None
    return res

def console_handler(data):
    if 'liveMeasurement' in data:
        measurement = data['liveMeasurement']
        timestamp = measurement['timestamp']
        timeObj = parse(timestamp)
        hourMultiplier = timeObj.hour+1
        daysInMonth = calendar.monthrange(timeObj.year, timeObj.month)[1]
        power = measurement['power']
        #min_power = measurement['minPower']
        #max_power = measurement['maxPower']
        #avg_power = measurement['averagePower']
        accumulated = measurement['accumulatedConsumption']
        accumulated_cost = measurement['accumulatedCost']
        #currency = measurement['currency']
        voltagePhase1 = measurement['voltagePhase1']
        voltagePhase2 = measurement['voltagePhase2']
        voltagePhase3 = measurement['voltagePhase3']
        currentL1 = measurement['currentL1']
        currentL2 = measurement['currentL2']
        currentL3 = measurement['currentL3']
        lastMeterConsumption = measurement['lastMeterConsumption']
        #print(accumulated)
        
        output = [
        {
            "measurement": "pulse",
            "time": timestamp,
            "tags": {
                "address": adr
            },
            "fields": {
                "power": ifStringZero(power),
                "consumption": ifStringZero(accumulated),
                "cost": ifStringZero(accumulated_cost),
                "voltagePhase1": ifStringZero(voltagePhase1),
                "voltagePhase2": ifStringZero(voltagePhase2),
                "voltagePhase3": ifStringZero(voltagePhase3),
                "currentL1": ifStringZero(currentL1),
                "currentL2": ifStringZero(currentL2),
                "currentL3": ifStringZero(currentL3),
                "lastMeterConsumption": ifStringZero(lastMeterConsumption),
                "hourmultiplier": hourMultiplier,
                "daysInMonth": daysInMonth
            }
        }
        ]
        print(output)
        influx_client.write_points(output)
        

def run_query(query, headers): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://api.tibber.com/v1-beta/gql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

def fetch_data(url, subscription_query, headers):
    transport = WebsocketsTransport(
        url=url,
        headers=headers,
        ping_interval=60,
        pong_timeout=10
    )
    # Using `async with` on the client will start a connection on the transport
    # and provide a `session` variable to execute queries on this connection
    ws_client = Client(
        transport=transport,
        fetch_schema_from_transport=True
    )

    for result in ws_client.subscribe(gql(subscription_query)):
        #print (result)
        console_handler(result)

if tibbertoken == 'NOTOKEN':
    print("Tibber token is missing!")
else:
    if tibberhomeid == 'NOID':
        #Try to automaticly get homeid:
        query = "{ viewer { homes { address { address1 } id } } }"
        resp = run_query(query, headers)
        id = resp['data']['viewer']['homes'][0]['id']
        tibberhomeid = id
        adr = resp['data']['viewer']['homes'][0]['address']['address1']
        print("Using homeid '"+id+"' ("+adr+")")
    # Get subscription URI
    request_res = run_query("{viewer{websocketSubscriptionUrl}}", headers)
    ws_uri = request_res['data']['viewer']['websocketSubscriptionUrl']

    print("Sleep for 5 secs.")
    time.sleep(5)
    print("Run GQL query.")
    fetch_data(ws_uri, subscription_query, headers)