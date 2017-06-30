#!/usr/bin/env python

import sys
import os
import netCDF4
import numpy
import json
import re
import copy
import logging
import argparse

log = logging.getLogger(__name__)
logging.basicConfig(level = logging.DEBUG)

fill_value = -9999.
reqdims = []
reqvars = []

# Main function.
def convert(gridfile,datafile,outputfile):
    if(not reqdims or not reqvars):
        read_drq("data_request.json")
    levels = parse_grid(gridfile)
    variables = parse_variables(datafile,levels)
    timdim = reqdims[0]
    timdim["nvals"] = len(variables[0]["values"])
    write_nc(outputfile,variables,[timdim] + levels)


# Static reader function of the data request
def read_drq(filename):
    global reqdims,reqvars
    with open(filename) as jsonfile:
        data = json.load(jsonfile)
        reqdims = data["dimensions"]
        reqvars = data["variables"]


# Parse static variables
def parse_grid(filename):
    f = open(filename,'r')
    lines = (l for l in f.readlines() if not l.strip().startswith('#'))
    dims = next(lines).split()
    converters = {}
    for i in range(len(dims)):
        converters[i] = lambda s:int(s.strip() or 0)
    numdata = numpy.loadtxt(lines,dtype = "int",converters = converters).transpose()
    result = copy.copy(reqdims[1:])
    for dim in result:
        dimname = dim["name"]
        dim["nvals"] = numdata[dims.index(dimname)] if dimname in dims else 0
    return result


# Parse dynamic variables
def parse_variables(datafile,levels):
    variables = []
    lev_index_key = "level_index"
    f = open(datafile,'r')
    lines = (l for l in f.readlines() if not l.strip().startswith('#'))
    varnames = next(lines).split()
    if(varnames[0].lower() not in ["time","times"]):
        log.error("First column in data file is not recognized as time stamps...aborting")
        return variables
    converters = {}
    for i in range(1,len(varnames) - 1):
        converters[i] = lambda s:float(s.strip() or 0)
    numdata = numpy.loadtxt(lines,skiprows = 0,converters = converters).transpose()
# Create time variable
    reqtimvar = [v for v in reqvars if v["name"] == "time"][0]
    variables.append(copy.copy(reqtimvar))
    times = numdata[0,:]
    variables[0]["values"] = times
# Create variable-column dictionary
    colindex = 0
    for varname in varnames[1:]:
        colindex += 1
        lev = 0
        if('_' in varname):
            colstr = varname.split('_')
            varname = colstr[0]
            lev = int(colstr[1]) if len(colstr) > 1 else 1
        log.info("Processing column %d: variable %s at level %d" % (colindex,varname,lev))
        existingvars = [v for v in variables if v.get("name",None) == varname]
        if(len(existingvars) > 1):
            log.error("Multiple variable columns found for %s...skipping column %d" % (varname,colindex))
        if(any(existingvars)):
            existingvars[0][lev_index_key][lev - 1] = colindex
        else:
            reqvarlist = [v for v in reqvars if v["name"] == varname]
            if(any(reqvarlist)):
                reqvar = reqvarlist[0]
                vardict = copy.copy(reqvar)
                variables.append(vardict)
                vardict[lev_index_key] = [colindex]
                for level in levels:
                    levdim = level.get("name",None)
                    if levdim in vardict["dimensions"]:
                        vardict[lev_index_key] = [-1] * level.get("nvals",0)
                        vardict[lev_index_key][lev - 1] = colindex
                        break
# Extract data from entire block
    for variable in variables[1:]:
        lev_indices = variable[lev_index_key]
        if(-1 in lev_indices):
            log.error("Could not find a data column for variable %s at column %d" % (variable["name"],lev_indices.index(-1)))
        variable["values"] = numdata[lev_indices,:]
    return variables


# Write variables to netcdf
def write_nc(filename,variables,dimensions):
    root = netCDF4.Dataset(filename,'w',format = "NETCDF4")
    #root.description = data_descr
    # Make dimensions
    for d in dimensions:
        root.createDimension(d["name"],d["nvals"])
    # make variables
    for v in variables:
        dims = v.get("dimensions",[])
        ncvar = root.createVariable(v["name"],"f8",dims)
        ncvar.units = v["unit"]
        ncvar.long_name = v["long_name"]
        ncvar.fill_value = fill_value
        ncvar.missing_value = missval
        if(len(dims) == 1):
            ncvar[:] = v["values"][:]
        elif(len(dims) == 2):
            ncvar[:,:] = v["values"][:,:]
    root.close()

def main(args):
    parser = argparse.ArgumentParser(description = "Conversion tool for single-column model ascii output o netcdf")
    parser.add_argument("datafile",metavar = "FILE",type = str,help = "Model output ascii file")
    parser.add_argument("gridfile",metavar = "FILE",type = str,help = "Model vertical levels ascii file")
    args = parser.parse_args()
    datafile = args.datafile
    if(not os.path.isfile(datafile)):
        log.error("Input file %s does not exist")
        return
    levelfile = args.gridfile
    if(not os.path.isfile(levelfile)):
        log.error("Input file %s does not exist")
        return
    outputfile = "output.nc"
    convert(levelfile,datafile,outputfile)

if __name__ == "__main__":
    main(sys.argv[1:])
