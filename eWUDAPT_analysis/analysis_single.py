from eWUDAPT_analysis.utils import *
from pylab import *
from netCDF4 import Dataset, num2date
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class analysis_single:
  def __init__(self, args, json):
    self.filename = args.filename
    self.outputdir = args.outputdir
    self.ncdf_definition = load_netcdf_definition(json)
    self.institute, self.model, self.version = define_inst_mod_ver(args.filename)
    create_directory(self.outputdir)
    self.create_plots()

  def create_plots(self):
    '''
    create plots
    '''
    # loop through all variables
    for variable in self.ncdf_definition['variables']:
      if 'time' in variable['dimensions']:
        # create time series plot of surface/first level
        self.plot_time_series(variable)
      if (len(set(['levf', 'levh', 'levs']) & set(variable['dimensions']))==1):
        dimname = sorted(set(['levf', 'levh', 'levs']) & set(variable['dimensions']))[0]
        # found a vertical dimension -> create vertical profile
        if variable['name'] not in ['zf', 'zh', 'zs']:
          # don't plot height in meters
          self.plot_vertical_profile(variable, dimname)

  def plot_time_series(self, variable):
    '''
    create time series plots'
    '''
    try:
      outputfig = ('time_series_' + self.institute + '_' + self.model + '_' +
                   self.version + '_' + variable["name"] + '.png')
      outputfile = os.path.join(self.outputdir, outputfig)
      ncfile = Dataset(self.filename, 'r')
      time = ncfile.variables['time']
      try:
        dt = [num2date(step, units=time.units, calendar=time.calendar)
              for step in time[:]]
      except AttributeError:
        # fallback
        dt = [num2date(step, units='seconds since 2006-07-01 12:00:00',
                       calendar='gregorian') for step in time[:]]
      if (len(variable['dimensions'])==1):
        # plot time series, 1D variable
        val = ncfile.variables[variable['name']][:]
      elif (len(variable['dimensions'])==2):
        # plot first level, 2D variable
        # TODO: add info to title on level
        val = ncfile.variables[variable['name']][:]
        if (len(np.shape(val)) == len(variable['dimensions'])):
          if np.shape(val)[0] == np.shape(time)[0]:
            val = val[:,0]
          elif np.shape(val)[1] == np.shape(time)[0]:
            val = val[0,:]
          else: 
            pass
        else:
          return
      else:
        raise Exception('Variable ' + variable['name'] +
                        'contains more than two dimensions')
      # create the plot
      plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y %H:%M'))
      plt.gca().xaxis.set_major_locator(mdates.HourLocator(byhour=range(0,24,3)))
      plt.plot(dt, val)
      plt.gcf().autofmt_xdate()
      plt.xlabel('time')
      plt.ylabel(variable["long_name"] + ' [' + variable["unit"] + ']')
      plt.savefig(outputfile)
      plt.close()
      # close netCDF file
      ncfile.close()
      return  # TODO: savefig
    except KeyError:
      pass

  def plot_vertical_profile(self, variable, dimname):
    '''
    create vertical profile plots at 0, 6, 12, 18h
    '''
    try:
      ncfile = Dataset(self.filename, 'r')
      time = ncfile.variables['time']
      try:
        dt = [num2date(step, units=time.units, calendar=time.calendar)
              for step in time[:]]
      except AttributeError:
        # fallback
        dt = [num2date(step, units='seconds since 2006-07-01 12:00:00',
                       calendar='gregorian') for step in time[:]]
      # define timesteps at which vertical profiles are plotted
      dt_profiles = np.arange(dt[0], dt[-1],np.timedelta64(6,'h'),
                              dtype='datetime64').astype(datetime.datetime)
      for dt_profile in dt_profiles:
        try:
          idx = dt.index(dt_profile)
        except ValueError:
          continue
        if (len(variable['dimensions'])==1):
          # plot static vertical profile, 1D variable
          val = ncfile.variables[variable['name']][:]
        elif (len(variable['dimensions'])==2):
          # plot vertical profile every 6 hours, 2D variable
          # TODO: add info to title on level
          val = ncfile.variables[variable['name']][:]
          if (len(np.shape(val)) == len(variable['dimensions'])):
            if np.shape(val)[0] == np.shape(time)[0]:
              val = val[idx, :]
            elif np.shape(val)[1] == np.shape(time)[0]:
              val = val[: idx]
            else: 
              pass
          else:
            return
        else:
          raise Exception('Variable ' + variable['name'] +
                          'contains more than two dimensions')
        if (dimname=='levf'):
          dimvar = 'zf'
        elif (dimname=='levh'):
          dimvar = 'zh'
        elif (dimname=='levs'):
          dimvar = 'zs'
        levels = ncfile.variables[dimvar]
        # create the plot
        if dimvar != 'zs':
          plt.plot(val, levels[idx, :])
        else:
          plt.plot(val, levels[:])        
        diminfo = get_dimension_information(self.ncdf_definition, dimname)
        timestr = dt_profile.strftime('%Y-%m-%d %H:%M')
        timestrplot = dt_profile.strftime('%Y-%m-%d_%H:%M')        
        outputfig = ('vert_profile_' + self.institute + '_' + self.model + '_' +
                     self.version + '_' + variable["name"] + timestrplot + '.png')
        outputfile = os.path.join(self.outputdir, outputfig)
        plt.title(variable['long_name'] + ' at ' + timestr)
        plt.xlabel(variable["long_name"] + ' [' + variable["unit"] + ']')
        plt.ylabel(levels.long_name + ' [' + levels.units + ']')
        plt.savefig(outputfile)
        plt.close()
      # close netCDF file
      ncfile.close()
      return  # TODO: savefig
    except KeyError:
      pass

