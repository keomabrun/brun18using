# ======================= Imports =============================================

# standard
import time
import calendar
import math
import pandas as pd

# external
import flatdict

# ======================= Defines =============================================

SNAPSHOT_PATH   = "../data/snapshot.csv"

# ======================= Main ================================================


def influxdb_to_json(sol_influxdb):
    """
    Converts an Influxdb query reply into a list of dicts.

    :param dict sol_influxdb: the result of a database query (such as SELECT * FROM)
    :return: a list of JSON SOL objects
    :rtype: list

    """

    # verify influxdb data
    if not ("series" in sol_influxdb):
        raise ValueError("Influxdb data not recognized")

    # init
    json_list = []

    # remove unused headers
    for series in sol_influxdb["series"]:
        for val in series['values']:
            # convert to dict
            d_influxdb = dict(zip(series['columns'], val))

            # remove null values
            for key in d_influxdb.keys():
                if d_influxdb[key] is None:
                    del d_influxdb[key]

            # unflat dict
            obj_value = flatdict.FlatDict(d_influxdb).as_dict()

            # parse specific objects
            if series['name'] == "SOL_TYPE_DUST_NOTIF_HRNEIGHBORS":
                if "neighbors" not in obj_value:
                    continue
                for i in range(0, len(obj_value["neighbors"])+1):
                    ngbr_id = str(i)

                    # new HR_NGBR parsing
                    if ngbr_id in obj_value["neighbors"]:
                        if obj_value["neighbors"][ngbr_id]["neighborFlag"] is None:
                            del obj_value["neighbors"][ngbr_id]

                    # old HR_NGBR parsing
                    if ngbr_id in obj_value:
                        if obj_value[ngbr_id]["neighborFlag"] is not None:
                            obj_value["neighbors"][ngbr_id] = obj_value[ngbr_id]
                        del obj_value[ngbr_id]

            if series['name'] == "SOL_TYPE_DUST_SNAPSHOT":
                if "mote" not in obj_value:
                    continue
                obj_value["motes"] = []
                for i in range(0, len(obj_value["mote"])+1):
                    mote_id = str(i)

                    if mote_id in obj_value["mote"]:
                        obj_value["motes"].append(obj_value["mote"][mote_id])
                        del obj_value["mote"][mote_id]

            # time is not passed in the "value" field
            del obj_value["time"]

            # create final dict
            jdic = {
                'type'      : series['name'],
                'mac'       : series['tags']['mac'],
                'value'     : obj_value,
                'timestamp' : d_influxdb['time'],
            }
            json_list.append(jdic)
    return json_list


def iso_to_epoch(iso_time):
    return calendar.timegm(time.strptime(iso_time, '%Y-%m-%dT%H:%M:%SZ'))


def get_mote_info(df_snapshot, mote_name, timestamp):
    mote_id = ""
    mote_mac = ""
    mote_lat = -1
    mote_long = -1
    mote_board = ""
    mote_name_type = ""

    if isinstance(mote_name, int):
        mote_name_type = "id"
        mote_id = mote_name
    else:
        mote_name_type = "mac"
        mote_mac = mote_name

    res = df_snapshot[(df_snapshot[mote_name_type] == mote_name) & (df_snapshot["time"] < timestamp)]
    if not res.empty:
        last_row = res.iloc[-1]
        if pd.notnull(last_row["lat"]):
            mote_lat = last_row["lat"]
        if pd.notnull(last_row["long"]):
            mote_long = last_row["long"]
        if pd.notnull(last_row["board"]):
            mote_board = last_row["board"]
        if pd.notnull(last_row["id"]):
            mote_id = last_row["id"]
        if pd.notnull(last_row["mac"]):
            mote_mac = last_row["mac"]

    mote = {
        "id": mote_id,
        "mac": mote_mac,
        "lat": mote_lat,
        "long": mote_long,
        "board": mote_board
    }

    return mote


def distance_on_unit_sphere(lat1, long1, lat2, long2):
    """
    Code from John Cook.
    http://www.johndcook.com/blog/python_longitude_latitude/
    """

    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians

    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos(cos)

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    return arc*6371*1000  # in meters
