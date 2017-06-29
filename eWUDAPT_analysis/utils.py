import os
import numpy as np
import glob
import yaml
import errno
from netCDF4 import Dataset

def load_netcdf_definition(json):
  '''
  load json file and return a dictionary of the netCDF file definition
  '''
  with open(json, 'r') as stream:
    return yaml.load(stream)

def define_inst_mod_ver(filepath):
  '''
  extract institute, model, version from filename/list of filenames
  '''
  if len(filepath) == 1:
    try:
      institute, model, version = get_inst_mod_ver(filepath)
    except AttributeError:
      institute, model, version = get_inst_mod_ver(filepath[0])    
  elif len(filepath) > 1:
    # list of files
    for filename in filepath:
      inst, mod, ver = get_inst_mod_ver(filename)
      try:
        institute += inst
        model += mod
        version += ver
      except NameError:
        institute = inst
        model = mod
        version = ver
  else:
    raise IOError('No filepath: ' + filepath + ' defined')
  return institute, model, version

def get_inst_mod_ver(filepath):
  '''
  extract institute, model, version from filename
  '''
  check_file_exists(filepath)
  filename = os.path.basename(filepath)
  inst, mod, ver = filename.replace(
    'gabls_urban_scm_', '').replace('.nc', '').split('_')
  return inst, mod, ver

def check_file_exists(filename, boolean=False):
  '''
  check if file exists and is readable, else raise IOError
  '''
  try:
      with open(filename) as file:
          if boolean:
            return True
          else:
            pass  # file exists and is readable, nothing else to do
  except IOError as e:
    if boolean:
      return False
    else:
      # file does not exist OR no read permissions
      raise # re-raise exception

def create_directory(path):
  '''
  Create a directory if it does not exist yet
  '''
  try:
    os.makedirs(path)
  except OSError as e:
    if e.errno != errno.EEXIST:  # directory already exists, no problem
      raise # re-raise exception if a different error occured

def get_variable_information(ncdf_definition, varname):
  '''
  retrieve variable information from loaded json dictionary
  '''
  varinfo = next(item for item in ncdf_definition['variables']
                 if item['name'] == varname)
  return varinfo

def get_dimension_information(ncdf_definition, dimname):
  '''
  retrieve dimension information from loaded json dictionary
  '''
  diminfo = next(item for item in ncdf_definition['dimensions']
                 if item['name'] == dimname)
  return diminfo

def get_filenames(path):
  '''
  return a list of netCDF filenames in path
  '''
  # get list of files with .nc extension in directory
  filelist = glob.glob(os.path.join(path, '*.nc'))
  boolean = np.zeros(np.shape(filelist), dtype=bool)
  # verify that these are indeed readable netCDF files
  for idx, filename in enumerate(filelist):
    try:
      ncfile = Dataset(filename, 'r')
      ncfile.close()
      # this is indeed a readable netCDF file
      boolean[idx] = True
    except IOError:
      # not a readable netCDF file
      boolean[idx] = False
  # return list of netCDF files
  return np.array(filelist)[boolean]

