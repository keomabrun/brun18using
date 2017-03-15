import json
import influxdb
import tools
import context

# ======================= Helpers =============================================

def write_to_file(out_file, json_list):
    # write json to file
    out_file.write("time,source,dest,direction,\n")
    for obj in json_list:
        time = tools.iso_to_epoch(obj["timestamp"])

        out_file.write(
            str(time)+','+\
            str(obj["value"]["source"])+','+\
            str(obj["value"]["dest"])+','+\
            str(obj["value"]["direction"])+','+\
            '\n'
        )

# ======================= Main ================================================

# open output file
path_create_file = open('../data/event_pathcreate.csv', 'w')
path_delete_file = open('../data/event_pathdelete.csv', 'w')

# configure influxDB
influxClient = influxdb.client.InfluxDBClient(
    host        = 'localhost',
    port        = '8086',
    database    = 'realms'
)

# query influxDB
query       =   "SELECT * FROM SOL_TYPE_DUST_EVENTPATHCREATE"
query       +=  " WHERE site='" + context.SITE + "'"
query       +=  " AND time > '" + context.STARTDATE + "'"
query       +=  " AND time < '" + context.STOPDATE + "'"
query       +=  " GROUP BY mac"
json_list   = tools.influxdb_to_json(influxClient.query(query).raw)
write_to_file(path_create_file, json_list)

query       =   "SELECT * FROM SOL_TYPE_DUST_EVENTPATHDELETE"
query       +=  " AND time > '" + context.STARTDATE + "'"
query       +=  " AND time < '" + context.STOPDATE + "'"
query       +=  " GROUP BY mac"
json_list   = tools.influxdb_to_json(influxClient.query(query).raw)
write_to_file(path_delete_file, json_list)
