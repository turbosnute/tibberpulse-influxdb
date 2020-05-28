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

client = InfluxDBClient(influxhost, influxport, influxuser, influxpw, influxdb)

header = {
    'Sec-WebSocket-Protocol': 'graphql-subscriptions'
}

def ifStringZero(val):
    val = str(val).strip()
    if val.replace('.','',1).isdigit():
      res = float(val)
    else:
      res = None
    return res

def console_handler(ws, message):
    data = json.loads(message)
    if 'payload' in data:
        measurement = data['payload']['data']['liveMeasurement']
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

        client.write_points(output)

        print(output)

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    def run(*args):
        init_data = {
            'type':'init',
            'payload':'token={token}'.format(token=tibbertoken)
        }
        init = json.dumps(init_data)
        ws.send(init)

        query = """
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

        subscribe_data = {
            'query': query,
            'type':'subscription_start',
            'id': 0
        }
        subscribe = json.dumps(subscribe_data)
        ws.send(subscribe)

    _thread.start_new_thread(run, ())


def initialize_websocket():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://api.tibber.com/v1-beta/gql/subscriptions",
                              header = header,
                              on_message = console_handler,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE, "check_hostname": False})
    
def run_query(query): # A simple function to use requests.post to make the API call. Note the json= section.
    request = requests.post('https://api.tibber.com/v1-beta/gql', json={'query': query}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))


if tibbertoken == 'NOTOKEN':
    print("Tibber token is missing!")
else:
    if tibberhomeid == 'NOID':
        #Try to automaticly get homeid:
        headers = {"Authorization": "Bearer "+tibbertoken}
        query = "{ viewer { homes { address { address1 } id } } }"
        resp = run_query(query)
        id = resp['data']['viewer']['homes'][0]['id']
        tibberhomeid = id
        adr = resp['data']['viewer']['homes'][0]['address']['address1']
        print("Using homeid '"+id+"' ("+adr+")")

    initialize_websocket()