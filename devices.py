import requests
import json
from configurator import get_conf

def submit_request(url, payload, headers, request_type):
    response = requests.request(request_type, url, headers=headers, data=payload, verify=False)
    return response


def device_parameter_provider(token, devices, kpi_profiles):
    url = get_conf('url')
    payload = json.dumps({
      "devices": devices,
      "kpi_profiles": kpi_profiles
    })
    headers = {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/json'
    }
    
    request_type = "POST"
    
    return url, payload, headers, request_type
    
def enable_kpi_profiles_with_parameters(url, payload, headers, request_type):
    url = url + "/crosswork/hi/v1/kpiprofileassoc/write"
    response = submit_request(url, payload, headers, request_type)
    return json.loads(response.text)
    
    
def enable_kpi_profiles(token, devices, kpi_profiles):
    url, payload, headers, request_type = device_parameter_provider(token, devices, kpi_profiles)
    return enable_kpi_profiles_with_parameters(url, payload, headers, request_type)


def disable_kpi_profiles_with_parameters(url, payload, headers, request_type):
    url = url + "/crosswork/hi/v1/kpiprofileassoc/delete"
    response = submit_request(url, payload, headers, request_type)
    return json.loads(response.text)

def disable_kpi_profiles(token, devices, kpi_profiles):
    url, payload, headers, request_type = device_parameter_provider(token, devices, kpi_profiles)
    return disable_kpi_profiles_with_parameters(url, payload, headers, request_type)

def get_enabled_devices_from_kpi_profile_name_with_parameters(url, payload, headers, request_type):
    url = url + "/crosswork/hi/v1/kpiprofileassoc/query"
    response = submit_request(url, payload, headers, request_type)
    return json.loads(response.text)

def get_enabled_devices_from_kpi_profile_name(token, kpi_profile_name):
    url, payload, headers, request_type = device_parameter_provider(token, [""], [kpi_profile_name])
    response = get_enabled_devices_from_kpi_profile_name_with_parameters(url, payload, headers,request_type)
    devices = []
    if  response["device_kpi_profiles"] != {}:
        for device in response["device_kpi_profiles"]["devices"]:
            devices.append(device["device_id"])
        
    return devices

def check_job_status_with_parameters(url, payload, headers, request_type):
    url = url + "/crosswork/hi/v1/kpiprofile/jobDetails"
    response = submit_request(url, payload, headers, request_type)
    return json.loads(response.text)["txn_results"][0]

def check_job_status(token, tx_id):
    url, _, headers, request_type = device_parameter_provider(token, [""], [""])
    payload = json.dumps({
    "tx_id": tx_id,
    "limit": 1
    })

    return check_job_status_with_parameters(url, payload, headers, request_type)
