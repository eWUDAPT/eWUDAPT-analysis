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
  import errno
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

