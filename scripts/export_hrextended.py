import influxdb
import tools
import context
import pandas as pd

# open input file
df_snapshot = pd.read_csv(context.DATA_FOLDER + "snapshot.csv")

# open output file
out_file = open(context.DATA_FOLDER + 'hr_extended.csv', 'w')

# configure influxDB
influxClient = influxdb.client.InfluxDBClient(
    host        = 'sol.paris.inria.fr/influx/',
    port        = '443',
    database    = 'realms'
)

# query influxDB
query       =   "SELECT * FROM SOL_TYPE_DUST_NOTIF_HREXTENDED"
query       +=  " WHERE site='" + context.SITE + "'"
query       +=  " AND time > '" + context.STARTDATE + "'"
query       +=  " AND time < '" + context.STOPDATE + "'"
query       +=  " GROUP BY mac"
json_list   = tools.influxdb_to_json(influxClient.query(query).raw)

# write json to file
out_file.write("time,mac,channel,rssi,lat,long\n")
for obj in json_list:
    time = tools.iso_to_epoch(obj["timestamp"])
    mote_info = tools.get_mote_info(df_snapshot, obj["mac"], time)

    #print obj["value"].keys()
    for channel, value in obj["value"].iteritems():
        if type(value) == dict:
            out_file.write(
                str(time)+',' +
                str(obj["mac"]) + ',' +
                str(channel) + ',' +
                str(value["idleRssi"]) + ',' +
                str(mote_info["lat"]) + ',' +
                str(mote_info["long"]) +
                '\n'
            )
