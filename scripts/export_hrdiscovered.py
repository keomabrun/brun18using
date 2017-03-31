import influxdb
import tools
import context
import pandas as pd

# open input file
df_snapshot = pd.read_csv(context.DATA_FOLDER + "snapshot.csv")

# open output file
out_file = open(context.DATA_FOLDER + 'hr_discovered.csv', 'w')

# configure influxDB
influxClient = influxdb.client.InfluxDBClient(
    host        = 'localhost',
    port        = '8086',
    database    = 'realms'
)

# query influxDB
query       =   "SELECT * FROM SOL_TYPE_DUST_NOTIF_HRDISCOVERED"
query       +=  " WHERE site='" + context.SITE + "'"
query       +=  " AND time > '" + context.STARTDATE + "'"
query       +=  " AND time < '" + context.STOPDATE + "'"
query       +=  " GROUP BY mac"
json_list   = tools.influxdb_to_json(influxClient.query(query).raw)

# write json to file
out_file.write("time,mac,neighborMac,rssi,numRx,distance\n")

for obj in json_list:
    time = tools.iso_to_epoch(obj["timestamp"])
    mote_info = tools.get_mote_info(df_snapshot, obj["mac"], time)

    for key, nghbr in obj["value"]["discoveredNeighbors"].iteritems():
        distance = None
        nghbr_info = tools.get_mote_info(df_snapshot, nghbr["neighborId"], time)

        if nghbr_info["lat"] is not None and mote_info["lat"] is not None:
            distance = tools.distance_on_unit_sphere(
                mote_info["lat"],
                mote_info["long"],
                nghbr_info["lat"],
                nghbr_info["long"]
            )
        else:
            distance = None

        if nghbr_info["mac"] is not "":
            out_file.write(
                str(time) + ',' +
                str(obj["mac"]) + ',' +
                str(nghbr_info["mac"]) + ',' +
                str(nghbr["rssi"]) + ',' +
                str(nghbr["numRx"]) + ',' +
                str(distance) +
                '\n'
            )
