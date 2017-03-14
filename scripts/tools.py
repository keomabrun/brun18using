# ======================= Imports =============================================

# standard
import time
import calendar
import csv
import math

# external
import flatdict

# ======================= Defines =============================================

MOTECREATE_PATH = "../data/motecreate.csv"
SNAPSHOT_PATH   = "../data/snapshot.csv"

# ======================= Main ================================================

def influxdb_to_json(sol_influxdb):
    """
    Converts an Influxdb query reply into a list of dicts.

    :param sol_influxdb dict: the result of a database query (sush as SELECT * FROM)
    :return: a list of JSON SOL objects
    :rtype: list

    """

    # verify influxdb data
    if not ("series" in sol_influxdb):
        raise ValueError("Influxdb data not recognized")

    # init
    json_list = []

    # remove unused headers
    for serie in sol_influxdb["series"]:
        for val in serie['values']:
            # convert to dict
            d_influxdb = dict(zip(serie['columns'], val))

            # remove null values
            for key in d_influxdb.keys():
                if d_influxdb[key] is None:
                    del d_influxdb[key]

            # unflat dict
            obj_value = flatdict.FlatDict(d_influxdb).as_dict()

            # parse specific objects
            if serie['name'] == "SOL_TYPE_DUST_NOTIF_HRNEIGHBORS":
                if "neighbors" not in obj_value:
                    continue
                for i in range(0,len(obj_value["neighbors"])+1):
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

            if serie['name'] == "SOL_TYPE_DUST_SNAPSHOT":
                if "mote" not in obj_value:
                    continue
                obj_value["motes"] = []
                for i in range(0,len(obj_value["mote"])+1):
                    mote_id = str(i)

                    if mote_id in obj_value["mote"]:
                        obj_value["motes"].append(obj_value["mote"][mote_id])
                        del obj_value["mote"][mote_id]

            # time is not passed in the "value" field
            del obj_value["time"]

            # create final dict
            jdic = {
                'type'      : serie['name'],
                'mac'       : serie['tags']['mac'],
                'value'     : obj_value,
                'timestamp' : d_influxdb['time'],
            }
            json_list.append(jdic)
    return json_list

def iso_to_epoch(iso_time):
    return calendar.timegm(time.strptime(iso_time, '%Y-%m-%dT%H:%M:%SZ'))

def mac_to_id(mac, time):
    line = 1
    moteid = None
    with open(MOTECREATE_PATH) as csvfile:
        createmote_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        event_list = list(createmote_reader)

        while line < len(event_list):
            event = event_list[line]
            if int(event[0]) > time or line == len(event_list)-1:
                break
            if event[1] == mac:
                moteid = int(event[2])
            line += 1
    return moteid

def id_to_mac(mote_id, time, safe=False):
    mote_mac = None
    mote_board = None
    infile = MOTECREATE_PATH

    if safe:
        infile = SNAPSHOT_PATH

    with open(infile) as csvfile:
        createmote_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        event_list = list(createmote_reader)[1:]

        for event in reversed(event_list):
            if int(event[2]) == mote_id:
                if int(event[0]) < time:
                    mote_mac = event[1]
                    if event[5] != "":
                        mote_board = event[5]
                    break
    return mote_mac, mote_board

def mac_to_position(mote_mac, time, safe=False):
    mote_lat    = None
    mote_long   = None
    infile      = MOTECREATE_PATH

    if safe:
        infile = SNAPSHOT_PATH

    with open(infile) as csvfile:
        createmote_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        event_list = list(createmote_reader)[1:]

        for event in reversed(event_list):
            if event[1] == mote_mac:
                if int(event[0]) < time:
                    if event[3] != "":
                        mote_lat = float(event[3])
                    if event[4] != "":
                        mote_long = float(event[4])
                    break

    return mote_lat, mote_long

def mac_to_board(mote_mac, time, safe=False):
    mote_board = None
    infile = MOTECREATE_PATH

    if safe:
        infile = SNAPSHOT_PATH

    with open(infile) as csvfile:
        createmote_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        event_list = list(createmote_reader)[1:]

        for event in reversed(event_list):
            if event[1] == mote_mac:
                if int(event[0]) < time:
                    if event[5] != "":
                        mote_board = event[5]
                    break

    return mote_board

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
    return arc*6371*1000 # in meters
