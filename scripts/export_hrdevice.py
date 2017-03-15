import json
import influxdb
import tools

# open output file
out_file = open('../data/hr_device.csv','w')

# configure influxDB
influxClient = influxdb.client.InfluxDBClient(
    host        = 'localhost',
    port        = '8086',
    database    = 'realms'
)

# query influxDB
query       =   "SELECT * FROM SOL_TYPE_DUST_NOTIF_HRDEVICE"
query       +=  " WHERE site='FRA_evalab' GROUP BY mac"
json_list   = tools.influxdb_to_json(influxClient.query(query).raw)

# write json to file
out_file.write("time,mac,charge,queueOcc,numTxOk,lat,long\n")
for obj in json_list:
    time                = tools.iso_to_epoch(obj["timestamp"])
    mote_lat, mote_long = tools.mac_to_position(obj["mac"],time)

    out_file.write(
        str(time)+','+\
        str(obj["mac"])+','+\
        str(obj["value"]["charge"])+','+\
        str(obj["value"]["queueOcc"])+','+\
        str(obj["value"]["numTxOk"])+','+\
        str(obj["value"]["latitude"])+','+\
        str(obj["value"]["longitude"])+\
        '\n'
    )
