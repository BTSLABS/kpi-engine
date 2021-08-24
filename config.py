import requests
from requests.api import request
from configurator import get_conf
class Config(object):
    start_time = "2021-02-13T13:17:00.000Z"
    influxdb_time = "1680000ms"
    payload = ""
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/plain',
    'Cache-Control': 'no-cache'
    }
    request_type = "POST"

    ticket = requests.request(request_type, get_conf('url')+"/crosswork/sso/v1/tickets?username="+get_conf('username')+"&password="+get_conf('password'), headers=headers, data=payload, verify=False).text

    payload='service=https%3A%2F%2F172.23.193.107%3A30603%2Fapp-dashboard'
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'text/plain',
      'Cache-Control': 'no-cache'
    }

    token = request(request_type, get_conf('url')+"/crosswork/sso/v1/tickets/"+ticket, headers=headers, data=payload, verify=False).text
    