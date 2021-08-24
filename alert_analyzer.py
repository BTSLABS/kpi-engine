from pymongo import MongoClient
from datetime import datetime, timezone, timedelta
from dateutil.parser import isoparse
import time
from thresholds import get_cpu_threshold_thresholds
import os
from bson.objectid import ObjectId
import json
from config import Config
from messenger import Messenger
import requests
from configurator import get_conf

client = MongoClient(get_conf('mongodb')) #MongoClient('mongodb://localhost:27017/')
db = client.AlertDatabase
msg = Messenger()
kpi_list = []

def get_alert_count_all(db, device):
    count = db.Alerts.find({'series.tags.Producer': device}).count()
    return count

def get_alert_count_kpi_profile(db, device, kpi_profile):
    count = db.Alerts.find({'series.tags.Producer': device, 'series.tags.profile_id': kpi_profile}).count()
    return count

def get_alert_count_kpi(db, device, kpi_profile, kpi):
    count = db.Alerts.find({'series.tags.Producer': device, 'series.tags.kpi_id': kpi, 'series.tags.profile_id': kpi_profile}).count()
    return count

def get_alert_count_tracked(device, kpi_profile, kpi):
    count = db.Alerts.find({'series.tags.Producer': device, 'series.tags.kpi_id': kpi, 'series.tags.profile_id': kpi_profile, 'is_tracked': 1}).count()
    return count

def get_alert_count_update_required(device, kpi_profile, kpi):
    count = db.Alerts.find({'series.tags.Producer': device, 'series.tags.kpi_id': kpi, 'series.tags.profile_id': kpi_profile, 'is_update_required': 1}).count()
    return count

def check_if_new(doc_id):
    # check if received alert is new or a 'returned to normal' message
    cursor = db.Alerts.find({'_id': doc_id})
    for doc in cursor:
        alert = doc

    if alert['series'][0]['tags']['state'] == 'clear':
        db.Alerts.update_one({'_id':doc_id}, {"$set": {'is_tracked': 0}}, upsert=False)
        cursor = db.Alerts.find({'series.tags.Producer': alert['series'][0]['tags']['Producer'],
                                  'series.tags.kpi_id': alert['series'][0]['tags']['kpi_id'],
                                  'series.tags.profile_id': alert['series'][0]['tags']['profile_id'],
                                  'series.values.0.10': alert['series'][0]['values'][0][10]})

        if cursor.count():
            for doc in cursor:
                related = doc

            db.Alerts.update_one({'_id': related['_id']}, {"$set": {'is_tracked': 0}}, upsert=False)

    else:
        db.Alerts.update_one({'_id':doc_id}, {"$set": {'is_tracked': 1}}, upsert=False)

def check_tracked_time(time_window):
    kpi_list = []
    cursor = db.Alerts.find({'is_tracked': 1})
    for doc in cursor:
        recv_time = doc['series'][0]['values'][0][0]
        if (datetime.now(timezone.utc) - isoparse(recv_time)).total_seconds() > time_window:
            db.Alerts.update_one({'_id':doc['_id']}, {"$set": {'is_update_required': 1}}, upsert=False)
            kpi_list.append([str(doc['_id']),
                            doc['series'][0]['tags']['Producer'],
                            doc['series'][0]['tags']['profile_id'],
                            doc['series'][0]['tags']['kpi_id']])
            
            calculate_threshold(doc['_id'])
            if get_conf('auto_update') == 'True':
                #update_threshold(doc['series'][0]['tags']['Producer'],
                #                    doc['series'][0]['tags']['profile_id'],
                #                    doc['series'][0]['tags']['kpi_id'])
                URL = "http://localhost:5000/update_device/" + doc['series'][0]['tags']['Producer'] + "/" + doc['series'][0]['tags']['profile_id'] + "/" + doc['series'][0]['tags']['kpi_id']
                requests.get(url = URL)
                db.Alerts.update_one({'_id':doc['_id']}, {"$set": {'is_update_required': 0}}, upsert=False)
                db.Alerts.update_one({'_id':doc['_id']}, {"$set": {'is_tracked': 0}}, upsert=False)
    
    kpi_list_dict = {'kpi_list' : kpi_list}
    cursor = db.Updates.find({})
    if cursor.count():
        for doc in cursor:
            db.Updates.insert_one(kpi_list_dict)

    if get_conf('auto_update') == 'True':
        send_updated_notif()
    else:
        send_update_req_notif()

def send_update_req_notif():
    kpi_list = []
    cursor = db.Updates.find({})
    for doc in cursor:
        kpi_list = doc['kpi_list']

    message = """### The following KPIs require an update: 

---

"""

    for alert in kpi_list:
        message = message + "**Device:** " + alert[1] + ", **KPI Profile:** " + alert[2] + ", **KPI:** " + alert[3] + ", **id:** " + alert[0] + """
"""
    
    message = message + """

"""

    message = message + "To approve updates, type command `/update @kpi-notifier`. If you do not want to update all KPIs, use the web GUI."

    msg.post_message(get_conf('room_id'), message)
    pass

def send_updated_notif():
    kpi_list = []
    cursor = db.Updates.find({})
    for doc in cursor:
        kpi_list = doc['kpi_list']

    message = """### The following KPIs are updated:

---

"""

    for alert in kpi_list:
        message = message + "**Device:** " + alert[1] + ", **KPI Profile:** " + alert[2] + ", **KPI:** " + alert[3] + ", **id:** " + alert[0] + """
"""
    
    message = message + """

"""

    if get_conf('auto_update') == 'True':
        message = message + "Auto updates feature is enabled, you can disable it using the web GUI."
    else:
        message = message + "Auto updates feature is disabled, you can enable it using the web GUI."
    

    msg.post_message(get_conf('room_id'), message)
    pass

def update_all_kpis():
    cursor = db.Updates.find({})
    for doc in cursor:
        kpi_list = doc['kpi_list']
        for alert in kpi_list:
            cursor_2 = db.Alerts.find({'_id': ObjectId(alert[0])})
            for doc_2 in cursor_2:
                #update_threshold(doc_2['series'][0]['tags']['Producer'],
                #                doc_2['series'][0]['tags']['profile_id'],
                #                doc_2['series'][0]['tags']['kpi_id'])
                URL = "http://localhost:5000/update_device/" + doc_2['series'][0]['tags']['Producer'] + "/" + doc_2['series'][0]['tags']['profile_id'] + "/" + doc_2['series'][0]['tags']['kpi_id']
                requests.get(url = URL)
                db.Alerts.update_one({'_id':doc_2['_id']}, {"$set": {'is_update_required': 0}}, upsert=False)
                db.Alerts.update_one({'_id':doc_2['_id']}, {"$set": {'is_tracked': 0}}, upsert=False)

    send_updated_notif()

    for doc in cursor:
        db.Updates.delete_one({'_id':doc['_id']})    


def calculate_threshold(doc_id):
    #get_cpu_threshold_thresholds()
    pass

def change_updated_alert(device, kpi_profile, kpi):
    cursor = db.Alerts.find({'series.tags.Producer': device, 'series.tags.kpi_id': kpi, 'series.tags.profile_id': kpi_profile, 'is_update_required': 1})
    for doc in cursor:
        db.Alerts.update_one({'_id':doc['_id']}, {"$set": {'is_update_required': 0}}, upsert=False)
        db.Alerts.update_one({'_id':doc['_id']}, {"$set": {'is_tracked': 0}}, upsert=False)

def check_update_required_device(device):
    cursor = db.Alerts.find({'series.tags.Producer': device, 'is_update_required': 1})
    if cursor.count():
        return "1"
    else:
        return "0"

def check_update_required_profile(device, kpi_profile):
    cursor = db.Alerts.find({'series.tags.Producer': device, 'series.tags.profile_id': kpi_profile, 'is_update_required': 1})
    if cursor.count():
        return "1"
    else:
        return "0"

def check_update_required_kpi(device, kpi_profile, kpi):
    cursor = db.Alerts.find({'series.tags.Producer': device, 'series.tags.profile_id': kpi_profile, 'series.tags.kpi_id': kpi, 'is_update_required': 1})
    if cursor.count():
        return "1"
    else:
        return "0"

def delete_non_tracked():
    d = db.Alerts.delete_many({'is_tracked': 0})

