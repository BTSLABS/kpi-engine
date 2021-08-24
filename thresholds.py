def get_cpu_threshold_thresholds(data):
    threshold_data = data["pulse_cpu_threshold"]["Cisco-IOS-XR-wdsysmon-fd-oper:system-monitoring/cpu-utilization"]["mean_total_cpu_five_minute"]
#     level2_threshold = threshold_data.mean() + 1.96 * threshold_data.var() / (len(threshold_data)**0.5)
    level1_threshold = threshold_data.mean() + threshold_data.var()
    level2_threshold = threshold_data.mean() + 2*threshold_data.var()
    
    thresholds = {
        "pulse_cpu_threshold_template.tick": {
            "level2_threshold": str(level2_threshold),
            "level1_threshold": str(level1_threshold)
        }
    }
    
    return thresholds