from statsmodels.tsa.arima.model import ARIMA

def get_cpu_threshold_thresholds(data):
    threshold_data = data["pulse_cpu_threshold"]["Cisco-IOS-XR-wdsysmon-fd-oper:system-monitoring/cpu-utilization"]["mean_total_cpu_five_minute"]
    level1_threshold, level2_threshold = calculate_threshold_with_arima(threshold_data)
    
    thresholds = {
        "pulse_cpu_threshold_template.tick": {
            "level2_threshold": str(level2_threshold),
            "level1_threshold": str(level1_threshold)
        }
    }
    
    return thresholds



def calculate_threshold_with_arima(pd_serie):
    model = ARIMA(pd_serie, order=(2,0,2))
    model_fit = model.fit()
    result = model_fit.get_forecast()
    return (result.conf_int(alpha=0.1)["upper mean_total_cpu_five_minute"].values[0], result.conf_int(alpha=0.05)["upper mean_total_cpu_five_minute"].values[0])