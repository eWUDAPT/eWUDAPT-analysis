#!/usr/bin/env python

import sys
import netCDF4
import logging
import argparse
import numpy
import csv
import json
import dateutil.parser

log = logging.getLogger(__name__)
logging.basicConfig(level = logging.DEBUG)
missval = -9999.

parlist = { "time":"time",
            "kdn":"qdw",
            "kup":"qup",
            "ldn":"ldw",
            "lup":"lup",
            "qstar":"g",
            "qh":"shf",
            "qe":"lhf",
            "press":"pf",
            "ustar":"ustar",
            "tair":"t" }

# Static reader function of the data request
def read_drq(filename):
    with open(filename) as jsonfile:
        data = json.load(jsonfile)
        return data["variables"]

def main(filename):
    parser = argparse.ArgumentParser(description = "Processing tool for observations")
    parser.add_argument("filename",metavar = "FILE",type = str,help = "Observation csv file")
    args = parser.parse_args()
    coldict = {}
    with open(args.filename,"r") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader,[])
        colindex = 0
        for key in header:
            if(key.lower() in parlist):
                coldict[colindex] = (parlist[key.lower()],[])
            colindex += 1
        for line in reader:
            for index in coldict:
                if(coldict[index][0].lower() == "time"):
                    coldict[index][1].append(dateutil.parser.parse(line[index]))
                else:
                    if(len(line[index]) == 0 or line[index] == "NA"):
                        coldict[index][1].append(missval)
                    else:
                        coldict[index][1].append(float(line[index]))
    vardict = {}
    for v in coldict.values():
        vardict[v[0]] = numpy.array(v[1])

    root = netCDF4.Dataset("obs.nc",'w',format = "NETCDF4")
    root.description = "Observation data"
    root.createDimension("levf",1)
    root.createDimension("levh",1)
    ntimes = len(vardict["time"])
    root.createDimension("time",ntimes)
    reqvars = read_drq("data_request.json")
    for v in reqvars:
        varname = v["name"]
        if(varname in vardict or varname in ["zf","zh"]):
            ncvar = root.createVariable(varname,"f8",v["dimensions"])
            ncvar.long_name = v["long_name"]
            ncvar.units = v["unit"]
            ncvar.fill_value = missval
            numdata = vardict.get(varname,[])
            if(varname == "time"):
                numdata = netCDF4.date2num(vardict[varname],units = v["unit"],calendar="gregorian")
            elif(varname == "zf"):
                numdata = numpy.repeat([49.5],ntimes)
            elif(varname == "zh"):
                numdata = numpy.repeat([0.],ntimes)
            ncvar[:] = numdata

    root.close()

if __name__ == "__main__":
    main(sys.argv[1:])
