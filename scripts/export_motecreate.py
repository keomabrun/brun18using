import json
import influxdb
import time
import calendar
import tools

# open output file
out_file = open('../data/motecreate.csv','w')

# configure influxDB
influxClient = influxdb.client.InfluxDBClient(
    host        = 'localhost',
    port        = '8086',
    database    = 'realms'
)

# query influxDB
query       =   "SELECT * FROM SOL_TYPE_DUST_EVENTMOTECREATE"
query       +=  " WHERE site='FRA_evalab' GROUP BY mac"
json_list   = tools.influxdb_to_json(influxClient.query(query).raw)

# write json to file
out_file.write('time,mac,id,lat,long,board\n')
for obj in json_list:
    # query for latitude and longitude
    latitude = ""
    longitude = ""
    board = ""
    query   = "SELECT temperature,latitude,longitude,board FROM SOL_TYPE_DUST_OAP_TEMPSAMPLE"
    query  += " WHERE time < '" + obj["timestamp"] + "'"
    query  += " and mac='" + obj["value"]["macAddress"] + "'"
    query  += " GROUP by mac"
    query  += " ORDER BY time DESC LIMIT 1"
    res     = influxClient.query(query).raw

    if len(res) > 0:
        res_json = tools.influxdb_to_json(influxClient.query(query).raw)[0]

        if "latitude" in res_json["value"] and res_json["value"]["latitude"] is not None:
            latitude = res_json["value"]["latitude"]
            longitude = res_json["value"]["longitude"]

        if "board" in res_json["value"] and res_json["value"]["board"] is not None:
            board = res_json["value"]["board"]

    if board:
        out_file.write(
            str(tools.iso_to_epoch(obj["timestamp"]))+','+\
            obj["value"]["macAddress"]+','+\
            str(obj["value"]["moteId"])+','+\
            str(latitude)+','+\
            str(longitude)+','+\
            board+\
            '\n'
        )
