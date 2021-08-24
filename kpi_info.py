import requests
import json
from configurator import get_conf

def submit_request(url, payload, headers, request_type):
    response = requests.request(request_type, url, headers=headers, data=payload, verify=False)
    return response

def kpi_information_parameter_provider(token, kpis):
    url = get_conf('url')

    payload = json.dumps({
      "kpis": kpis,
      "offset": 0,
    })
    headers = {
      'Authorization': 'Bearer '+token,
      'Content-Type': 'application/json'
    }
    request_type = "POST"
    return url, payload, headers, request_type

def get_kpi_information_with_parameters(url, payload, headers, request_type):
    url = url + "/crosswork/hi/v1/kpimgmt/query"
    response = submit_request(url, payload, headers, request_type)
    return json.loads(response.text)

def get_kpi_information(token, kpis):
    url, payload, headers, request_type = kpi_information_parameter_provider(token, kpis)
    return get_kpi_information_with_parameters(url, payload, headers, request_type)

def get_sensors_for_kpis(token, kpis):
    kpis_sensors = {}
    for kpi in get_kpi_information(token,kpis)["kpis"]["kpi"]:
        kpis_sensors[kpi["kpi_id"]] = {}
        for sensor_group in kpi["sensor_groups"]["sensor_group"]:
            for sensor_path in sensor_group["sensor_paths"]["sensor_path"]:
                splitted_str = sensor_path["path_id"].rsplit("/", 1)
                kpis_sensors[kpi["kpi_id"]].setdefault(splitted_str[0],[]).append(splitted_str[1])
    return kpis_sensors