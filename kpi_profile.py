import requests
import json
from configurator import get_conf

def submit_request(url, payload, headers, request_type):
    response = requests.request(request_type, url, headers=headers, data=payload, verify=False)
    return response

def kpi_profile_parameter_provider(token, profile_name_pattern):
    url = get_conf('url')
    payload = json.dumps({
      "profile_name_pattern": profile_name_pattern
    })
    headers = {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/json'
    }
    
    request_type = "POST"
    
    return url, payload, headers, request_type

def get_kpi_profile_information_with_parameters(url, payload, headers, request_type):
    url = url + "/crosswork/hi/v1/kpiprofilemgmt/query"
    response = submit_request(url, payload, headers, request_type)
    for kpi in json.loads(response.text)["profile_controls"]:
        if kpi["id"] == json.loads(payload)["profile_name_pattern"]:
            return kpi
    pass
    
    
def get_kpi_profile_information(token, kpi_profile):
    url, payload, headers, request_type = kpi_profile_parameter_provider(token, kpi_profile)
    return get_kpi_profile_information_with_parameters(url, payload, headers, request_type)


def update_kpi_payload(kpi_profile, kpi_name, thresholds):
    for kpi in kpi_profile['kpis']:
        if kpi["kpi_id"] == kpi_name:
            for kpi_script in kpi["kpi_scripts"]:
                for script in thresholds.keys():
                    if kpi_script["script_id"] == script:
                        for i in kpi_script["parameters"]:
                            for j,k in thresholds[script].items():
                                if i["name"] == j:
                                    i["value"] = k
    return kpi_profile


def update_kpi_profile_with_parameters(url, payload, headers, request_type):
    url = url + "/crosswork/hi/v1/kpiprofilemgmt/write"
    response = submit_request(url, payload, headers, request_type)
    return response


def update_kpi_profile(token, updated_kpi):
    url = get_conf('url')
    payload = json.dumps(updated_kpi)
    headers = {
      'Authorization': 'Bearer ' + token,
      'Content-Type': 'application/json'
    }
    request_type = "PUT"
    return update_kpi_profile_with_parameters(url, payload, headers, request_type)    

# # Get KPI profile and update it.
# emre_deneme = get_kpi_profile_information(token, "emre_deneme_3")
# thresholds = {
#     "pulse_cpu_utilization_template.tick": {
#         "crit_threshold": "13.0",
#         "warn_threshold": "15.0"
#     }
# }
# emre_deneme = update_kpi_payload(emre_deneme, "pulse_cpu_utilization", thresholds)
# update_kpi_profile(token, emre_deneme)

def get_kpis_from_kpi_profile(kpi_profile):
    kpis = []
    for kpi in kpi_profile["kpis"]:
        kpis.append(kpi["kpi_id"])
    return kpis
