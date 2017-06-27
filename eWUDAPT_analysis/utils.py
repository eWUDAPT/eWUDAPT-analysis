import os

def load_netcdf_definition(json):
  import yaml
  '''
  load json file and return a dictionary of the netCDF file definition
  '''
  with open(json, 'r') as stream:
    return yaml.load(stream)

def define_inst_mod_ver(filepath):
  '''
  extract institute, model, version from filename/filepath
  '''
  check_file_exists(filepath)
  filename = os.path.basename(filepath)
  institute, model, version = filename.replace(
    'gabls_urban_scm_', '').replace('.nc', '').split('_')
  return institute, model, version

def check_file_exists(filepath):
  '''
  check if file exists
  '''
  pass
