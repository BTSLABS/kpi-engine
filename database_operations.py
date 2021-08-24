import pandas as pd

def query_builder_for_single_model(k, v, db_name, start_time, end_time, sources, time):
    sensor_query = ""
    for sensor in v:
        sensor = sensor.replace("-", "_")
        sensor_query += "mean(\""+sensor+"\") AS \"mean_"+sensor+"\","
    sensor_query = sensor_query.rstrip(",")
    
    source_query = ""
    for source in sources:
        source_query += "\'" + source + "\'" + " OR "
    source_query = source_query.rstrip(" OR ")
    
    final_query = "SELECT " + sensor_query + " FROM " + db_name + ".\"autogen\".\"" + k + "_tcp" + "\" WHERE time > \'" + start_time + "' AND time < \'" + end_time + "\' AND (" + "\"source\" = " + source_query + ") GROUP BY time(" + time + ") FILL(null)"
    return final_query

def query_builder_for_multiple_models(kpi, db_name, start_time, end_time, sources, time):
    final_queries = {}
    for k,v in kpi.items():
        final_queries[k] = query_builder_for_single_model(k,v, db_name, start_time, end_time, sources, time)
    return final_queries

def query_builder_for_kpis(kpis, db_name, start_time, end_time, sources, time):
    kpis_final_queries = {}
    for (k,v) in kpis.items():
        kpis_final_queries[k] = query_builder_for_multiple_models(v, db_name, start_time, end_time, sources, time)
    return kpis_final_queries

def get_data_for_single_kpi(client, queries, db_name, start_time, end_time, sources, time):
    result_sets = {}
    for (k,v) in queries.items():
        result_sets[k] = client.query(v)
    return result_sets

def get_data_for_multiple_kpis(client, kpi_queries, db_name, start_time, end_time, sources, time):
    kpis_result_sets = {}
    for (k,v) in kpi_queries.items():
        kpis_result_sets[k] = get_data_for_single_kpi(client, v, db_name, start_time, end_time, sources, time)
    return kpis_result_sets

def resultset_to_dataframe(resultset):
    array_data = []
    for data_point in resultset.get_points():
        array_data.append(data_point)
    df = pd.DataFrame(array_data)
    df = df.dropna()
    return df

def resultset_to_dataframe_single_kpi(kpi_data):
    kpi_dict = {}
    for (k,v) in kpi_data.items():
        kpi_dict[k] = resultset_to_dataframe(v)
    return kpi_dict

def resultset_to_dataframe_multiple_kpis(kpis_data):
    kpis_dict = {}
    for (k,v) in kpis_data.items():
        kpis_dict[k] = resultset_to_dataframe_single_kpi(v)
    return kpis_dict

# Get data using KPI information
# kpis = get_sensors_for_kpis(token, ["pulse_cpu_utilization"])
# kpi_queries = query_builder_for_kpis(kpis,db_name, start_time, end_time, sources, time)
# get_data_for_multiple_kpis(client, kpi_queries, db_name, start_time, end_time, sources, time)