import influxdb
import tools
import context
import pandas as pd

# open input file
df_snapshot = pd.read_csv(context.DATA_FOLDER + "snapshot.csv")

# open output file
out_file = open(context.DATA_FOLDER + 'hr_device.csv', 'w')

# configure influxDB
influxClient = influxdb.client.InfluxDBClient(
    host        = 'localhost',
    port        = '8086',
    database    = 'realms'
)

# query influxDB
query       =   "SELECT * FROM SOL_TYPE_DUST_NOTIF_HRDEVICE"
query       +=  " WHERE site='" + context.SITE + "'"
query       +=  " AND time > '" + context.STARTDATE + "'"
query       +=  " AND time < '" + context.STOPDATE + "'"
query       +=  " GROUP BY mac"
json_list   = tools.influxdb_to_json(influxClient.query(query).raw)

# write json to file
out_file.write("time,mac,charge,queueOcc,numTxOk,lat,long\n")
for obj in json_list:
    time = tools.iso_to_epoch(obj["timestamp"])
    mote_info = tools.get_mote_info(df_snapshot, obj["mac"], time)

    out_file.write(
        str(time)+',' +
        str(obj["mac"]) + ',' +
        str(obj["value"]["charge"]) + ',' +
        str(obj["value"]["queueOcc"]) + ',' +
        str(obj["value"]["numTxOk"]) + ',' +
        str(mote_info["lat"]) + ',' +
        str(mote_info["long"]) +
        '\n'
    )
