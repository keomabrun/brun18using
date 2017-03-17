# ======================= Imports =============================================

import influxdb
import tools
import context

# ======================= Main ================================================

# open output file
out_file = open('../data/snapshot.csv', 'w')

# configure influxDB
influxClient = influxdb.client.InfluxDBClient(
    host        = 'localhost',
    port        = '8086',
    database    = 'realms'
)

# query influxDB
query       =   "SELECT * FROM SOL_TYPE_DUST_SNAPSHOT"
query       +=  " WHERE site='" + context.SITE + "'"
query       +=  " AND time > '" + context.STARTDATE + "'"
query       +=  " AND time < '" + context.STOPDATE + "'"
query       +=  " GROUP BY mac"
json_list   = tools.influxdb_to_json(influxClient.query(query).raw)

# write json to file
out_file.write('time,mac,id,lat,long,board\n')
for obj in json_list:
    for mote in obj["value"]["motes"]:
        # query for latitude and longitude
        latitude = ""
        longitude = ""
        board = ""
        query   = "SELECT temperature,latitude,longitude,board FROM SOL_TYPE_DUST_OAP_TEMPSAMPLE"
        query  += " WHERE time < '" + obj["timestamp"] + "'"
        query  += " and mac='" + mote["macAddress"] + "'"
        query  += " and site='" + context.SITE + "'"
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

        timestamp = tools.iso_to_epoch(obj["timestamp"])
        out_file.write(
            str(timestamp) + ',' +
            mote["macAddress"] + ',' +
            str(mote["moteId"]) + ',' +
            str(latitude) + ',' +
            str(longitude) + ',' +
            board +
            '\n'
        )
