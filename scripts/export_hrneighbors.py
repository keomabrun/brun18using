import influxdb
import tools
import context
import pandas as pd

# ======================= Main ================================================

# open input file
df_snapshot = pd.read_csv("../data/snapshot.csv")

# open output file
out_file = open('../data/hr_neighbors.csv', 'w')

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
print query
json_list   = tools.influxdb_to_json(influxClient.query(query).raw)

# write json to file
out_file.write("time,mac,neighborMac,neighborFlag,rssi,numTxPackets,numTxFailures,numRxPackets,mote_board,ngbr_board,distance\n")
out_file.close()
out_file = open('../data/hr_neighbors.csv', 'a')
for obj in json_list:

    # init
    nghbr_mac = ""
    prev_nbrId = ""
    prev_evt_time = -1 # has to differ from evt_time
    nghbr_lat = 0
    nghbr_long = 0
    prev_nghbr_lat = 0
    prev_nghbr_long = -1 # has to differ from nghbr_long

    # get time, position and board type
    evt_time            = tools.iso_to_epoch(obj["timestamp"])
    mote_lat, mote_long, mote_board = tools.get_mote_info(df_snapshot, obj["mac"], evt_time)
    if mote_board is None:
        mote_board = ""

    for key, nghbr in obj["value"]["neighbors"].iteritems():

        # init
        distance = -1

        # get neighbor information
        nghbr_lat, nghbr_long, nghbr_board = tools.get_mote_info(df_snapshot, nghbr["neighborId"], evt_time)
        if nghbr_lat is not None and mote_lat is not None:
            distance = tools.distance_on_unit_sphere(
                mote_lat,
                mote_long,
                nghbr_lat,
                nghbr_long
            )

        if nghbr_board is None:
            nghbr_board = ""

        # write event
        if nghbr_mac is not None:
            out_file.write(
                str(evt_time)+','+\
                str(obj["mac"])+','+\
                str(nghbr_mac)+','+\
                str(nghbr["neighborFlag"])+','+\
                str(nghbr["rssi"])+','+\
                str(nghbr["numTxPackets"])+','+\
                str(nghbr["numTxFailures"])+','+\
                str(nghbr["numRxPackets"])+','+\
                mote_board+','+\
                nghbr_board+','+\
                str(distance)+\
                '\n'
            )
