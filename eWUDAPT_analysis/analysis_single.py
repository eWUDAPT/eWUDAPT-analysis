from eWUDAPT_analysis.utils import *
from pylab import *
from netCDF4 import Dataset


class analysis_single:
  def __init__(self, args, json):
    self.filename = args.filename
    self.ncdf_definition = load_netcdf_definition(json)
    self.institute, self.model, self.version = define_inst_mod_ver(args.filename)
    self.plot_time_series()

  def plot_time_series(self):
    '''
    create time series plots'
    '''
    vars = ['ldw', 'lup', 'qdw', 'qup', 'tsk', 'g', 'shf', 'lhf', 'qf',
            'ustar', 'hpbl', 't2m', 'q2m', 'u10m', 'v10m', 'cc']
    for var in vars:
      try:
        outputfig = ('time_series_' + self.institute + '_' + self.model + '_' + self.version + '_' + var + '.png')
        ncfile = Dataset(self.filename, 'r')
        val = ncfile.variables[var][:]
        time = ncfile.variables['time'][:]
        plot(time, val)
        show()
      except KeyError:
        pass
