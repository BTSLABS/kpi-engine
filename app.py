from flask import Flask, render_template, redirect, url_for, request

import time
import requests.api
from config import Config
import os
import json
import pymongo
from alert_analyzer import *

from configurator import *
from subprocess import call

from kpi_info import *
from database_operations import *
from devices import *
from kpi_profile import *
from thresholds import *
from influxdb import InfluxDBClient

app = Flask(__name__)
app.config.from_object(Config)

client = pymongo.MongoClient('mongodb://localhost:27017/')

db = client['AlertDatabase']
collection = db['Alerts']


@app.route('/')
def devices():
    response = get_all_devices()
    for row in response['data']:
        converted_time = time.ctime(int(row['last_upd_time']))
        row['last_upd_time'] = converted_time

    return render_template("devices.html", data=response)

@app.route('/administration')
def admin():
    return render_template("administration.html")

@app.route("/alert", methods=['POST'])
def insert_document():
    req_data = request.get_json()
    doc_id = collection.insert_one(req_data).inserted_id
    check_if_new(doc_id)
    return ('', 204)

@app.route('/webhook', methods=['GET', 'POST'])
def bot_post():
    if request.method == 'GET':
        return 'Request received'
    elif request.method == 'POST':
        if 'application/json' in request.headers.get('Content-Type'):
            data = request.get_json()

            if msg.bot_id == data.get('data').get('personId'):
                return 'Message from self ignored'
            else:
                print(json.dumps(data,indent=4))
                msg.room_id = data.get('data').get('roomId')
                message_id = data.get('data').get('id')
                msg.get_message(message_id)

                if msg.message_text.startswith('/update'):
                    update_all_kpis()

                return ('Successfully updated', 200)
        else: 
            return ('Wrong data format', 400)


@app.route("/update_config", methods=['POST'])
def update_config():
    req_data = json.dumps(request.get_json())
    update_conf(req_data)
    
    call(["/var/lib/snapd/snap/bin/ngrok", "authtoken", get_conf('ngrok_token')])
    call(["systemctl", "restart", "kpy-ngrok.service"])
    
    r = requests.get('http://localhost:4040/api/tunnels')
    ngrok_conf = r.json()

    ngrok_endpoint = ngrok_conf['tunnels'][0]['public_url']

    url = "https://webexapis.com/v1/webhooks"

    payload={}
    headers = {
        'Authorization': 'Bearer ' + get_conf('webexapi_token')
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    webex_webhook = response.json()
    webex_webhook_id = webex_webhook['items'][0]['id']

    url = "https://webexapis.com/v1/webhooks/" + webex_webhook_id

    payload = json.dumps({
        "targetUrl": ngrok_endpoint
    })
    headers = {
        'Authorization': 'Bearer ' + get_conf('webexapi_token'),
        'Content-Type': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    dblist = client.list_database_names()
    if "AlertDatabase" not in dblist:
        db = client['AlertDatabase']
        col_list = db.list_collection_names()
        if "Alerts" not in col_list:
            db.create_collection('Alerts')
        if "Updates" not in col_list:
            db.create_collection('Updates', capped=True, size=5242880, max=1)
            db.Updates.insert_one({[]})

    call(["systemctl", "restart", "kpy-housekeeping.service"])
    call(["systemctl", "restart", "kpy-flask-app.service"])
    

    return ('', 204)

    

@app.route("/get_config", methods=['GET'])
def get_config():
    conf_json = get_conf()
    return conf_json

@app.route('/<host_name>/health', methods=['GET'])
def get_device_threshold_health(host_name):
    health = check_update_required_device(host_name)
    return health

@app.route('/<host_name>/<kpi_profile_name>/health', methods=['GET'])
def get_profile_threshold_health(host_name, kpi_profile_name):
    health = check_update_required_profile(host_name, kpi_profile_name)
    return health

@app.route('/<host_name>/<kpi_profile_name>/<kpi_name>/health', methods=['GET'])
def get_kpi_threshold_health(host_name, kpi_profile_name, kpi_name):
    health = check_update_required_kpi(host_name, kpi_profile_name, kpi_name)
    return health

@app.route('/<host_name>/kpiprofiles')
def kpi(host_name):
    response = get_device_kpi(host_name)


    return render_template("kpiprofiles.html", host_name=host_name, data=response, submitted_kpi="0")


@app.route("/update_device/<device_name>/<kpi_profile_name>/<kpi_name>")
#def update_device(device_name, kpi_profile_name, kpi_name):
#    update_threshold(device_name, kpi_profile_name, kpi_name)
#    return "OK"
def update_device(device_name, kpi_profile_name, kpi_name):
    start_time = Config.start_time
    end_time = "2021-03-10T21:00:00.000Z"
    sources = ["nw_rt_npe_asr9_02.33mrsn"]
    db_name = get_conf('influxdb_name')
    client = InfluxDBClient(get_conf('influxdb_ip'), get_conf('influxdb_port'), db_name)

    devices = get_enabled_devices_from_kpi_profile_name(Config.token, kpi_profile_name)

    disable_job_response = disable_kpi_profiles(Config.token, devices, [kpi_profile_name])

    while check_job_status(Config.token, disable_job_response["txid"])["state"] != "Success" and check_job_status(Config.token, disable_job_response["txid"])["error"] != "Profile not found on any device" and check_job_status(Config.token, disable_job_response["txid"])["error"] != "Profile not found on Device":
        time.sleep(5)

    kpi_profile = get_kpi_profile_information(Config.token, kpi_profile_name)

    kpi_names = get_kpis_from_kpi_profile(kpi_profile)

    sensors = get_sensors_for_kpis(Config.token, kpi_names)

    queries = query_builder_for_kpis(sensors, db_name, start_time, end_time, sources, Config.influxdb_time)

    data = get_data_for_multiple_kpis(client, queries, db_name, start_time, end_time, sources, Config.influxdb_time)
    data = resultset_to_dataframe_multiple_kpis(data)

    # Get KPI profile and update it.
    # emre_deneme = get_kpi_profile_information(token, "emre_deneme_3")

    thresholds = get_cpu_threshold_thresholds(data)
    kpi_profile = update_kpi_payload(kpi_profile, kpi_name, thresholds)
    update_kpi_profile(Config.token, kpi_profile)

    enable_job_response = enable_kpi_profiles(Config.token, devices, [kpi_profile_name])

    while check_job_status(Config.token, enable_job_response["txid"])["state"] != "Success" and check_job_status(Config.token, enable_job_response["txid"])["error"] != "Profile already applied on device":
        time.sleep(5)



    change_updated_alert(device_name, kpi_profile_name, kpi_name)
    
    response = get_device_kpi(device_name)
    return render_template("kpiprofiles.html", host_name=device_name, data=response, submitted_kpi=kpi_profile_name)

def get_all_devices():
    headers = {
        'Authorization': 'Bearer ' + Config.token,
        'Content-Type': 'application/json'
    }
    payload = json.dumps({})

    response = requests.api.request("POST", get_conf('url') + "/crosswork/inventory/v1/nodes/query", headers=headers, data=payload,
                       verify=False)

    return json.loads(response.text)


def get_device_kpi(host_name):
    headers = {
        'Authorization': 'Bearer ' + Config.token,
        'Content-Type': 'application/json'
    }
    payload = json.dumps({"devices": [host_name]})

    response = requests.api.request("POST", get_conf('url') + "/crosswork/hi/v1/kpiprofileassoc/query", headers=headers,
                       data=payload,
                       verify=False)

    return json.loads(response.text)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
