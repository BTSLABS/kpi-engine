import json
import configparser
from subprocess import call

config = configparser.ConfigParser()

def update_conf(conf_json):
    conf_dict = json.loads(conf_json)

    config['DEFAULT']['url'] = str(conf_dict.get("url"))
    config['DEFAULT']['username'] = str(conf_dict.get("username"))
    config['DEFAULT']['password'] = str(conf_dict.get("password"))
    config['DEFAULT']['mongodb'] = str(conf_dict.get("mongodb"))
    config['DEFAULT']['check_period'] = str(conf_dict.get("check_period"))
    config['DEFAULT']['track_time'] = str(conf_dict.get("track_time"))
    config['DEFAULT']['auto_update'] = str(conf_dict.get("auto_update"))
    config['DEFAULT']['influxdb_ip'] = str(conf_dict.get("influxdb_ip"))
    config['DEFAULT']['influxdb_port'] = str(conf_dict.get("influxdb_port"))
    config['DEFAULT']['influxdb_name'] = str(conf_dict.get("influxdb_name"))
    config['DEFAULT']['admin_email'] = str(conf_dict.get("admin_email"))
    config['DEFAULT']['room_id'] = str(conf_dict.get("room_id"))
    config['DEFAULT']['webexapi_token'] = str(conf_dict.get("webexapi_token"))
    config['DEFAULT']['ngrok_token'] = str(conf_dict.get("ngrok_token"))
    config['DEFAULT']['webex_enable'] = str(conf_dict.get("webex_enable"))

    with open('configuration.ini', 'w') as configfile:
        config.write(configfile)


def get_conf(field = 'all'):
    config.read('configuration.ini')
    conf_dict = {
        "url" : config['DEFAULT']['url'],
        "username" : config['DEFAULT']['username'],
        "password" : config['DEFAULT']['password'],
        "mongodb" : config['DEFAULT']['mongodb'],
        "check_period" : int(config['DEFAULT']['check_period']),
        "track_time" : int(config['DEFAULT']['track_time']),
        "auto_update" : config['DEFAULT']['auto_update'],
        "influxdb_ip" : config['DEFAULT']['influxdb_ip'],
        "influxdb_port" : int(config['DEFAULT']['influxdb_port']),
        "influxdb_name" : config['DEFAULT']['influxdb_name'],
        "admin_email" : config['DEFAULT']['admin_email'],
        "room_id" : config['DEFAULT']['room_id'],
        "webexapi_token" : config['DEFAULT']['webexapi_token'],
        "ngrok_token" : config['DEFAULT']['ngrok_token'],
        "webex_enable" : config['DEFAULT']['webex_enable']
    }

    conf_json = json.dumps(conf_dict)

    if field == 'all':
        return conf_json
    else:
        return conf_dict[field]
