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
missstrs = ["","NA"]

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

def ClausiusClapeyron(rh,t,p):
    if(rh == missval or t == missval or p == missval):
        return missval
    return rh*numpy.exp(17.67*t/(t + 273.16 - 29.65))/(0.263*p)

def potentialtemp(t,p):
    if(t == missval or p == missval):
        return missval
    return t*(10000./p)**0.286

def main(filename):
    parser = argparse.ArgumentParser(description = "Processing tool for observations")
    parser.add_argument("filename",metavar = "FILE",type = str,help = "Observation csv file")
    args = parser.parse_args()
    coldict = {}
    wind_speed_index = -1
    wind_dir_index = -1
    u,v,rh = [],[],[]
    rh_index = -1
    with open(args.filename,"r") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader,[])
        colindex = 0
        for key in header:
            if(key.lower() in parlist):
                coldict[colindex] = (parlist[key.lower()],[])
            elif(key.lower() == "ws"):
                wind_speed_index = colindex
            elif(key.lower() == "dir"):
                wind_dir_index = colindex
            elif(key.lower() == "rh"):
                rh_index = colindex
            colindex += 1
        for line in reader:
            if(wind_speed_index != -1 and wind_dir_index != -1):
                ws,wd = line[wind_speed_index],line[wind_dir_index]
                if(ws in missstrs or wd in missstrs):
                    u.append(missval)
                    v.append(missval)
                else:
                    vabs = float(ws)
                    angle = numpy.deg2rad(90.0 - float(wd))
                    u.append(numpy.cos(angle)*vabs)
                    v.append(numpy.sin(angle)*vabs)
            if(rh_index != -1):
                h = line[rh_index]
                rh.append(missval if h in missstrs else float(h))
            for index in coldict:
                if(coldict[index][0].lower() == "time"):
                    coldict[index][1].append(dateutil.parser.parse(line[index]))
                else:
                    if(line[index] in missstrs):
                        coldict[index][1].append(missval)
                    else:
                        coldict[index][1].append(float(line[index]))
    vardict = {}
    for col in coldict.values():
        if(col[0] == "pf"):
            hPatoPa = numpy.vectorize(lambda x:(x if x == missval else 100.*x))
            vardict[col[0]] = hPatoPa(numpy.array(col[1]))
        elif(col[0] == "t"):
            degCtoK = numpy.vectorize(lambda x:(x if x == missval else x + 273.16))
            vardict[col[0]] = degCtoK(numpy.array(col[1]))
        else:
            vardict[col[0]] = numpy.array(col[1])
    if(u):
        vardict["u"] = numpy.array(u,dtype = float)
    if(v):
        vardict["v"] = numpy.array(v,dtype = float)
    if(rh):
        rharr = numpy.array(rh,dtype = float)
        mapping = numpy.vectorize(ClausiusClapeyron)
        vardict["q"] = mapping(rharr,vardict["pf"],vardict["pf"])
    mapping = numpy.vectorize(potentialtemp)
    vardict["th"] = mapping(vardict["t"],vardict["pf"])

    root = netCDF4.Dataset("obs.nc",'w',format = "NETCDF4")
    root.description = "Observation data"
    root.createDimension("levf",1)
    root.createDimension("levh",1)
    ntimes = len(vardict["time"])
    root.createDimension("time",ntimes)
    reqvars = read_drq("data_request.json")
    for rqv in reqvars:
        varname = rqv["name"]
        if(varname in vardict or varname in ["zf","zh"]):
            ncvar = root.createVariable(varname,"f8",rqv["dimensions"])
            ncvar.long_name = rqv["long_name"]
            ncvar.units = rqv["unit"]
            ncvar.fill_value = missval
            ncvar.missing_value = missval
            numdata = vardict.get(varname,[])
            if(varname == "time"):
                numdata = netCDF4.date2num(vardict[varname],units = rqv["unit"],calendar="gregorian")
            elif(varname == "zf"):
                numdata = numpy.repeat([49.5],ntimes)
            elif(varname == "zh"):
                numdata = numpy.repeat([0.],ntimes)
            ncvar[:] = numdata
    root.close()

if __name__ == "__main__":
    main(sys.argv[1:])
