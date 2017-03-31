import influxdb
import tools
import context
import pandas as pd

# ======================= Main ================================================

# open input file
df_snapshot = pd.read_csv(context.DATA_FOLDER + "snapshot.csv")

# open output file
out_file = open(context.DATA_FOLDER + 'hr_neighbors.csv', 'w')

# configure influxDB
influxClient = influxdb.client.InfluxDBClient(
    host        = 'localhost',
    port        = '8086',
    database    = 'realms'
)

# query influxDB
query       =   "SELECT * FROM SOL_TYPE_DUST_NOTIF_HRNEIGHBORS"
query       +=  " WHERE site='" + context.SITE + "'"
query       +=  " AND time > '" + context.STARTDATE + "'"
query       +=  " AND time < '" + context.STOPDATE + "' GROUP BY mac"
json_list   = tools.influxdb_to_json(influxClient.query(query).raw)

# write json to file
out_file.write("time,mac,neighborMac,neighborFlag,rssi,numTxPackets,numTxFailures,numRxPackets,mote_board,ngbr_board,distance\n")
for obj in json_list:

    # get time, position and board type
    evt_time  = tools.iso_to_epoch(obj["timestamp"])
    mote_info = tools.get_mote_info(df_snapshot, obj["mac"], evt_time)

    for key, nghbr in obj["value"]["neighbors"].iteritems():

        # init
        distance = -1

        # get neighbor information
        nghbr_info = tools.get_mote_info(df_snapshot, nghbr["neighborId"], evt_time)
        if nghbr_info["lat"] is not None and mote_info["lat"] is not None:
            distance = tools.distance_on_unit_sphere(
                mote_info["lat"],
                mote_info["long"],
                nghbr_info["lat"],
                nghbr_info["long"]
            )

        # write event
        if nghbr_info["mac"] != "":
            out_file.write(
                str(evt_time) + ',' +
                str(obj["mac"]) + ',' +
                str(nghbr_info["mac"]) + ',' +
                str(nghbr["neighborFlag"]) + ',' +
                str(nghbr["rssi"]) + ',' +
                str(nghbr["numTxPackets"]) + ',' +
                str(nghbr["numTxFailures"]) + ',' +
                str(nghbr["numRxPackets"]) + ',' +
                str(mote_info["board"]) + ',' +
                str(nghbr_info["board"]) + ',' +
                str(distance) +
                '\n'
            )
