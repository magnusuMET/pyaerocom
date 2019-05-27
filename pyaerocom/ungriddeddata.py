#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
from datetime import datetime
from collections import OrderedDict as od
import fnmatch
import pandas as pd
from pyaerocom import logger, const, print_log
from pyaerocom.exceptions import (DataExtractionError, VarNotAvailableError,
                                  TimeMatchError, DataCoverageError,
                                  MetaDataError, StationNotFoundError,
                                  DataUnitError)
from pyaerocom import StationData

from pyaerocom.mathutils import in_range
from pyaerocom.helpers import (same_meta_dict, 
                               start_stop_str,
                               start_stop, merge_station_data)
from pyaerocom.metastandards import StationMetaData

class UngriddedData(object):
    """Class representing ungridded data
    
    The data is organised in a 2-dimensional numpy array where the first index 
    (rows) axis corresponds to individual measurements (i.e. one timestamp of 
    one variable) and along the second dimension (containing 11 columns) the 
    actual values are stored (in column 6) along with additional information,
    such as metadata index (can be used as key in :attr:`metadata` to access
    additional information related to this measurement), timestamp, latitude, 
    longitude, altitude of instrument, variable index and, in case of 3D 
    data (e.g. LIDAR profiles), also the altitude corresponding to the data 
    value.
        
    Note
    ----
    
    That said, let's look at two examples.
    
    **Example 1**: Suppose you load 3 variables from 5 files, each of which 
    contains 30 timestamps. This corresponds to a total of 3*5*30=450 data 
    points and hence, the shape of the underlying numpy array will be 450x11.
    
    **Example 2**: 3 variables, 5 files, 30 timestamps, but each variable 
    is height resolved, containing 100 altitudes => 3*5*30*100=4500 data points, 
    thus, the final shape will be 4500x11.
    
    TODO
    ----
    Include unit attribute for each variable (in pyaerocom.io package: make
    sure to include units during ungridded read, if available)
    
    Attributes
    ----------
    _data : ndarray
        (private) numpy array of dtype np.float64 initially of shape (10000,8)
        data point array
    metadata : dict
        dictionary containing meta information about the data. Keys are 
        floating point numbers corresponding to each station, values are 
        corresponding dictionaries containing station information.
    mata_idx : dict
        dictionary containing index mapping for each station and variable. Keys
        correspond to metadata key (float -> station, see :attr:`metadata`) and 
        values are dictionaries containing keys specifying variable name and 
        corresponding values are arrays or lists, specifying indices (rows) of 
        these station / variable information in :attr:`_data`.
    var_idx : dict
        mapping of variable name (keys, e.g. od550aer) to numerical variable 
        index of this variable in data numpy array (in column specified by
        :attr:`_VARINDEX`)
        
    Parameters
    ----------
    num_points : :obj:`int`, optional
        inital number of total datapoints (number of rows in 2D dataarray)
    add_cols : :obj:`list`, optional
        list of additional index column names of 2D datarray.
        
    """
    #: version of class (for caching)
    __version__ = '0.19'
    
    #: inital total number of rows in dataarray
    _ROWNO = 10000
    #: default number of rows that are dynamically added if total number of 
    #: data rows is reached.
    _CHUNKSIZE = 1000
    
    #: The following indices specify what the individual rows of the datarray
    #: are reserved for. These may be expanded when creating an instance of 
    #: this class by providing a list of additional index names.
    _METADATAKEYINDEX = 0
    _TIMEINDEX = 1
    _LATINDEX = 2
    _LONINDEX = 3
    _ALTITUDEINDEX = 4 # altitude of measurement device
    _VARINDEX = 5
    _DATAINDEX = 6
    _DATAHEIGHTINDEX = 7
    _DATAERRINDEX = 8 # col where errors can be stored
    _DATAFLAGINDEX = 9 # can be used to store flags
    _STOPTIMEINDEX = 10 # can be used to store stop time of acq. 
    _TRASHINDEX = 11 #index where invalid data can be moved to (e.g. when outliers are removed)
    
    # The following number denotes the kept precision after the decimal dot of
    # the location (e.g denotes lat = 300.12345)
    # used to code lat and long in a single number for a uniqueness test
    _LOCATION_PRECISION = 5
    _LAT_OFFSET = np.float(90.)
    
    STANDARD_META_KEYS = list(StationMetaData().keys())
    def __init__(self, num_points=None, add_cols=None):
        
        self._index = self._init_index(add_cols)
        if num_points is None:
            num_points = self._ROWNO
            
        
        #keep private, this is not supposed to be used by the user
        self._data = np.ones([num_points, self._COLNO]) * np.nan

        self.metadata = od()
        self.data_revision = od()
        self.meta_idx = od()
        self.var_idx = od()
        
        self.filter_hist = od()
    
    @property
    def index(self):
        return self._index
    
    def _init_index(self, add_cols=None):
        """Init index mapping for columns in dataarray"""
        idx = od(metadata       = self._METADATAKEYINDEX,
                 time           = self._TIMEINDEX,
                 stoptime       = self._STOPTIMEINDEX,
                 latitude       = self._LATINDEX,
                 longitude      = self._LONINDEX,
                 altitude       = self._ALTITUDEINDEX,
                 varidx         = self._VARINDEX,
                 data           = self._DATAINDEX,
                 dataerr        = self._DATAERRINDEX,
                 dataaltitude   = self._DATAHEIGHTINDEX,
                 dataflag       = self._DATAFLAGINDEX,
                 trash          = self._TRASHINDEX)
        
        next_idx = max(idx.values()) + 1
        if add_cols is not None:
            if not isinstance(add_cols, (list, tuple)):
                raise ValueError('Invalid input for add_cols. Need list or tuple')
            for name in add_cols:
                if name in idx:
                    raise ValueError('Cannot add new index with name {} since '
                                     'this index already exists at column '
                                     'position {}'.format(name, idx[name]))
                idx[name] = next_idx
                next_idx += 1
        return idx
    
    @property
    def _COLNO(self):
        return len(self._index)
    
    def copy(self):
        """Make a copy of this object
        
        Returns
        -------
        UngriddedData
            copy of this object
            
        Raises
        ------
        MemoryError
            if copy is too big to fit into memory together with existing 
            instance
        """
        from copy import deepcopy
        new = UngriddedData()
        new._data = np.copy(self._data)
        new.metadata = deepcopy(self.metadata)
        new.data_revision = self.data_revision
        new.meta_idx = deepcopy(self.meta_idx)
        new.var_idx = deepcopy(self.var_idx)
        new.filter_hist = deepcopy(self.filter_hist)
        return new
        
    @property
    def contains_vars(self):
        """List of all variables in this dataset"""
        return [k for k in self.var_idx.keys()]
    
    @property
    def contains_datasets(self):
        """List of all datasets in this object"""
        datasets = []
        for info in self.metadata.values():
            ds = info['data_id']
            if not ds in datasets:
                datasets.append(ds)
        return datasets
    
    @property
    def contains_instruments(self):
        """List of all instruments in this object"""
        instruments = []
        for info in self.metadata.values():
            try:
                instr = info['instrument_name']
                if instr is not None and not instr in instruments:
                    instruments.append(instr)
            except:
                pass
        return instruments        
    
    @property
    def shape(self):
        """Shape of data array"""
        return self._data.shape
    
    @property
    def is_empty(self):
        """Boolean specifying whether this object contains data or not"""
        return True if len(self.metadata) == 0 else False
    
    @property
    def is_filtered(self):
        """Boolean specifying whether this data object has been filtered
        
        Note
        ----
        Details about applied filtering can be found in :attr:`filter_hist`
        """
        if len(self.filter_hist) > 0:
            return True
        return False
    
    @property
    def longitude(self):
        """Longitudes of stations"""
        vals = []
        for v in self.metadata.values():
            try:
                vals.append(v['longitude'])
            except:
                vals.append(np.nan)
        return vals

    @longitude.setter
    def longitude(self, value):
        raise AttributeError("Station longitudes cannot be changed")

    @property
    def latitude(self):
        """Latitudes of stations"""
        vals = []
        for v in self.metadata.values():
            try:
                vals.append(v['latitude'])
            except:
                vals.append(np.nan)
        return vals

    @latitude.setter
    def latitude(self, value):
        raise AttributeError("Station latitudes cannot be changed")
        
    @property
    def altitude(self):
        """Altitudes of stations"""
        vals = []
        for v in self.metadata.values():
            try:
                vals.append(v['altitude'])
            except:
                vals.append(np.nan)
        return vals

    @altitude.setter
    def altitude(self, value):
        raise AttributeError("Station altitudes cannot be changed")
        
    @property
    def station_name(self):
        """Latitudes of data"""
        vals = []
        for v in self.metadata.values():
            try:
                vals.append(v['station_name'])
            except:
                vals.append(np.nan)
        return vals

    @station_name.setter
    def station_name(self, value):
        raise AttributeError("Station names cannot be changed")
    
    @property
    def unique_station_names(self):
        """List of unique station names"""
        return sorted(list(dict.fromkeys(self.station_name)))
    
    @property
    def time(self):
        """Time dimension of data"""
        raise NotImplementedError

    @time.setter
    def time(self, value):
        raise AttributeError("Time array cannot be changed")
        
    def last_filter_applied(self):
        """Returns the last filter that was applied to this dataset
        
        To see all filters, check out :attr:`filter_hist`
        """
        if not self.is_filtered:
            raise AttributeError('No filters were applied so far')
        return self.filter_hist[max(self.filter_hist.keys())]
    
    def add_chunk(self, size=None):
        """Extend the size of the data array
        
        Parameters
        ----------
        size : :obj:`int`, optional
            number of additional rows. If None (default) or smaller than 
            minimum chunksize specified in attribute ``_CHUNKSIZE``, then the
            latter is used.
        """
        if size is None or size < self._CHUNKSIZE:
            size = self._CHUNKSIZE
        chunk = np.empty([size, self._COLNO])*np.nan
        self._data = np.append(self._data, chunk, axis=0)
        self._ROWNO += size
        logger.info("adding chunk, new array size ({})".format(self._data.shape))                
    
    def _find_station_indices(self, station_pattern):
        """Find indices of all metadata blocks matching input station name
        
        Parameters
        ----------
        station_pattern : str
            station name or wildcard pattern
        
        Returns
        -------
        list
           list containing all metadata indices that match the input station
           name or pattern
           
        Raises
        ------
        StationNotFoundError
            if no such station exists in this data object
        """
        idx = []
        for i, meta in self.metadata.items():
            if fnmatch.fnmatch(meta['station_name'], station_pattern):
                idx.append(i)
        if len(idx) == 0:
            raise StationNotFoundError('No station available in UngriddedData '
                                       'that matches name or pattern {}'
                                       .format(station_pattern))
        return idx
    
    def find_station_meta_indices(self, station_name_or_pattern):
        """Find indices of all metadata blocks matching input station name
        
        You may also use wildcard pattern as input (e.g. *Potenza*)
        
        Parameters
        ----------
        station_pattern : str
            station name or wildcard pattern
        
        Returns
        -------
        list
           list containing all metadata indices that match the input station
           name or pattern
           
        Raises
        ------
        StationNotFoundError
            if no such station exists in this data object
        """
        return self._find_station_indices(station_name_or_pattern)
    
    # TODO: see docstring
    def to_station_data(self, meta_idx, vars_to_convert=None, start=None, 
                        stop=None, freq=None,  
                        merge_if_multi=True, merge_pref_attr=None, 
                        merge_sort_by_largest=True, insert_nans=False):
        """Convert data from one station to :class:`StationData`
        
        Todo
        ----
        - Review for retrieval of profile data (e.g. Lidar data)
        
        Parameters
        ----------
        meta_idx : float
            index of station or name of station.
        vars_to_convert : :obj:`list` or :obj:`str`, optional
            variables that are supposed to be converted. If None, use all 
            variables that are available for this station
        start
            start time, optional (if not None, input must be convertible into
            pandas.Timestamp)
        stop 
            stop time, optional (if not None, input must be convertible into
            pandas.Timestamp)
        freq : str
            pandas frequency string (e.g. 'D' for daily, 'M' for month end) or
            valid pyaerocom ts_type
        interp_nans : bool
            if True, all NaN values in the time series for each 
            variable are interpolated using linear interpolation
        min_coverage_interp : float
            required coverage fraction for interpolation (default is 0.68, i.e.
            roughly corresponding to 1 sigma)
        merge_if_multi : bool
            if True and if data request results in multiple instances of 
            StationData objects, then these are attempted to be merged into one 
            :class:`StationData` object using :func:`merge_station_data`
        merge_pref_attr 
            only relevant for merging of multiple matches: preferred attribute 
            that is used to sort the individual StationData objects by relevance.
            Needs to be available in each of the individual StationData objects.
            For details cf. :attr:`pref_attr` in docstring of 
            :func:`merge_station_data`. Example could be `revision_date`. If 
            None, then the stations will be sorted based on the number of 
            available data points (if :attr:`merge_sort_by_largest` is True, 
            which is default).
        merge_sort_by_largest : bool
            only relevant for merging of multiple matches: cf. prev. attr. and
            docstring of :func:`merge_station_data` method.
        insert_nans : bool
            if True, then the retrieved :class:`StationData` objects are filled
            with NaNs 
        
        Returns
        -------
        StationData or list
            StationData object(s) containing results. list is only returned if 
            input for meta_idx is station name and multiple matches are 
            detected for that station (e.g. data from different instruments), 
            else single instance of StationData. All variable time series are
            inserted as pandas Series
        """
        if isinstance(vars_to_convert, str):
            vars_to_convert = [vars_to_convert]
        elif vars_to_convert is None:
            vars_to_convert = self.contains_vars
            if len(vars_to_convert) == 0:
                raise DataCoverageError('UngriddedData object does not contain '
                                        'any variables')
        if start is None and stop is None:
            start = pd.Timestamp('1970')
            stop = pd.Timestamp('2200')
        else:
            start, stop = start_stop(start, stop)
            
        if isinstance(meta_idx, str):
            # user asks explicitely for station name, find all meta indices
            # that match this station
            meta_idx = self._find_station_indices(meta_idx)
        if not isinstance(meta_idx, list):
            meta_idx = [meta_idx]
        
        stats = []    
        start, stop = np.datetime64(start), np.datetime64(stop)
        
        for idx in meta_idx:
            try:
                stat = self._metablock_to_stationdata(idx, 
                                                      vars_to_convert,  
                                                      start, stop)
                stats.append(stat)
            except (VarNotAvailableError, TimeMatchError) as e:
                logger.info('Skipping meta index {}. Reason: {}'
                            .format(idx, repr(e)))
        if merge_if_multi and len(stats) > 1:
            if len(vars_to_convert) > 1:
                raise NotImplementedError('Cannot yet merge multiple stations '
                                          'with multiple variables.')
            if merge_pref_attr is None: 
                merge_pref_attr = self._try_infer_stat_merge_pref_attr(stats)
            merged = merge_station_data(stats, vars_to_convert,
                                        pref_attr=merge_pref_attr,
                                        sort_by_largest=merge_sort_by_largest,
                                        fill_missing_nan=False) #done below
            stats = [merged]
        for stat in stats:
            for var in vars_to_convert:
                if freq is not None:
                    stat.resample_timeseries(var, freq, inplace=True) # this does also insert NaNs, thus elif in next
                elif insert_nans:
                    stat.insert_nans_timeseries(var)
        if len(stats) == 0:
            raise DataCoverageError('{} data could not be retrieved for meta '
                                    ' index (or station name) {}'
                                    .format(vars_to_convert, meta_idx))
        elif len(stats) == 1:
            # return StationData object and not list 
            return stats[0]
        return stats
      
    def _try_infer_stat_merge_pref_attr(self, stats):
        """Checks if a preferred attribute for handling of overlaps can be inferred
        
        Parameters
        ----------
        stats : list
            list of :class:`StationData` objects
        
        Returns
        -------
        str
            preferred merge attribute parameter, if applicable, else None
        """
        data_id = None
        pref_attr = None
        for stat in stats:
            if not 'data_id' in stat:
                return None
            elif data_id is None:
                data_id = stat['data_id']
                from pyaerocom.metastandards import DataSource
                s = DataSource(data_id=data_id) # reads default data source info that may contain preferred meta attribute
                pref_attr = s.stat_merge_pref_attr
                if pref_attr is None:
                    return None
            elif not stat['data_id'] == data_id: #station data objects contain different data sources
                return None
        return pref_attr
    
    ### TODO: check if both `variables` and `var_info` attrs are required in 
    ### metdatda blocks
    def _metablock_to_stationdata(self, meta_idx, vars_to_convert, 
                                  start=None, stop=None):
        """Convert one metadata index to StationData (helper method)
        
        
        See :func:`to_station_data` for input parameters
        """
        # may or may not be defined in metadata block
        check_keys = ['instrument_name', 'filename', 'revision_date',
                      'station_name_orig']
        sd = StationData()
        
        val = self.metadata[meta_idx]
        
        # TODO: make sure in reading classes that data_revision is assigned
        # to each metadata block and not only in self.data_revision
        rev = None
        if 'data_revision' in val:
            rev = val['data_revision']
        else:
            try:
                rev = self.data_revision[val['data_id']]
            except:
                print_log.warning('Data revision could not be accessed in '
                                  'UngriddedData')
        sd.data_revision = rev
        if not 'variables' in val or val['variables'] in (None, []):
            raise VarNotAvailableError('Metablock does not contain variable '
                                       'information')
        for k in check_keys:
            if k in val:
                sd[k] = val[k]
            
        for k in self.STANDARD_META_KEYS:
            if k in val:
                sd[k] = val[k]
        if 'ts_type' in val:
            sd['ts_type_src'] = val['ts_type']
            
        # assign station coordinates explicitely
        for ck in sd.STANDARD_COORD_KEYS:
            if ck in val:
                sd.station_coords[ck] = val[ck]
        
        if vars_to_convert is None:
            vars_to_convert = val['variables']
        vars_to_convert = np.intersect1d(vars_to_convert, val['variables']) 
        if not len(vars_to_convert) >= 1:
            raise VarNotAvailableError('None of the input variables matches, '
                                       'or station does not contain data. {}'
                                       .format(val['variables']))
        #_data = self._get_subset(meta_idx)
        
        for var in vars_to_convert:
            
            # get indices of this variable
            var_idx = self.meta_idx[meta_idx][var]
            
            # vector of timestamps corresponding to this variable
            dtime = self._data[var_idx, 
                               self._TIMEINDEX].astype('datetime64[s]')
            
            # get subset
            subset = self._data[var_idx]
            
            # make sure to extract only valid timestamps
            if start is None:
                start = dtime.min()
            if stop is None:
                stop = dtime.max()
            
            # create access mask for valid time stamps
            tmask = np.logical_and(dtime >= start, 
                                   dtime <= stop)
            
            # make sure there is some valid data
            if tmask.sum() == 0:
                raise TimeMatchError('No data available for station {} ({}) in '
                                     'time interval {} - {}'
                                     .format(sd['station_name'],
                                             sd['data_id'],
                                             start, stop))
                
            dtime = dtime[tmask]
            subset = subset[tmask]
            
            vals = subset[:, self._DATAINDEX]
            vals_err = subset[:, self._DATAERRINDEX]
            altitude =  subset[:, self._DATAHEIGHTINDEX]
                
            data = pd.Series(vals, dtime)
            if not data.index.is_monotonic:
                data = data.sort_index()
            sd.data_err[var] = vals_err
        
            sd['dtime'] = data.index.values
            sd[var] = data
            
            # check if there is information about altitude (then relevant 3D
            # variables and parameters are included too)
            if 'var_info' in val:
                vi = val['var_info']
            else:
                vi = {}
            if not np.isnan(altitude).all():
                if 'altitude' in vi:
                    sd.var_info['altitude'] = vi['altitude']
                sd.altitude = altitude
            if var in vi:
                sd.var_info[var] = vi[var]
            else:
                sd.var_info[var] = od()
        
            if len(data.index) == len(data.index.unique()):
                sd.var_info[var]['overlap'] = False  
            else:
                sd.var_info[var]['overlap'] = True
        
        return sd
    
    def to_station_data_all(self, vars_to_convert=None, start=None, stop=None, 
                            freq=None, by_station_name=True, **kwargs):
        """Convert all data to :class:`StationData` objects
        
        Creates one instance of :class:`StationData` for each metadata block in 
        this object.

        Parameters
        ----------
        vars_to_convert : :obj:`list` or :obj:`str`, optional
            variables that are supposed to be converted. If None, use all 
            variables that are available for this station
        start
            start time, optional (if not None, input must be convertible into
            pandas.Timestamp)
        stop 
            stop time, optional (if not None, input must be convertible into
            pandas.Timestamp)
        freq : str
            pandas frequency string (e.g. 'D' for daily, 'M' for month end)
            or valid pyaerocom ts_type (e.g. 'hourly', 'monthly').
        by_station_name : bool
            if True, then iter over unique_station_name (and merge multiple 
            matches if applicable), else, iter over metadata index
        **kwargs
            additional keyword args passed to :func:`to_station_data` (e.g.
            `merge_if_multi, merge_pref_attr, merge_sort_by_largest, 
            insert_nans`)

        Returns
        -------
        dict
            4-element dictionary containing following key / value pairs:
                
                - stats: list of :class:`StationData` objects
                - station_name: list of corresponding station names
                - latitude: list of latitude coordinates
                - longitude: list of longitude coordinates
                
        """
        out_data = {'stats' : [],
                    'station_name' : [],
                    'latitude'     : [],
                    'longitude'    : []}
        
        if by_station_name:
            _iter = self.unique_station_names
        else:
            _iter = range(len(self.metadata))
        for idx in _iter:
            try:
                data = self.to_station_data(idx, vars_to_convert, start, 
                                            stop, freq,
                                            merge_if_multi=True)
                
                out_data['latitude'].append(data['latitude'])
                out_data['longitude'].append(data['longitude'])
                out_data['station_name'].append(data['station_name'])
                out_data['stats'].append(data)
                
            # catch the exceptions that are acceptable
            except (VarNotAvailableError, TimeMatchError, 
                    DataCoverageError) as e:
                logger.warning('Failed to convert to StationData '
                               'Error: {}'.format(repr(e)))
        return out_data
    
# See new implementation (changed on 6/3/19 by J. Gliss)
# =============================================================================
#     def to_station_data_all(self, vars_to_convert=None, start=None, stop=None, 
#                                 freq=None, include_stats_nodata=True, **kwargs):
#         """Convert all data to :class:`StationData` objects
#         
#         Creates one instance of :class:`StationData` for each metadata block in 
#         this object. For datasets like Aeronet, this corresponds to one
# 
#         Parameters
#         ----------
#         vars_to_convert : :obj:`list` or :obj:`str`, optional
#             variables that are supposed to be converted. If None, use all 
#             variables that are available for this station
#         start
#             start time, optional (if not None, input must be convertible into
#             pandas.Timestamp)
#         stop 
#             stop time, optional (if not None, input must be convertible into
#             pandas.Timestamp)
#         freq : str
#             pandas frequency string (e.g. 'D' for daily, 'M' for month end)
#             or valid pyaerocom ts_type (e.g. 'hourly', 'monthly').
#         
#         **kwargs
#             additional keyword args passed to :func:`to_station_data` (e.g.
#             `merge_if_multi, merge_pref_attr, merge_sort_by_largest, 
#             insert_nans`)
# 
#         Returns
#         -------
#         list 
#             list containing loaded instances of :class:`StationData` for each
#             station in :attr:`metadata`, where :func:`to_station_data` was 
#             successful, and ``None`` entries for meta data indices where 
#             :func:`to_station_data` failed (e.g. because no temporal match, 
#             etc.)
# 
#         """
#         out_data = []
#         for index in self.metadata:
#             try:
#                 data = self.to_station_data(index, vars_to_convert, start, 
#                                             stop, freq)
#                 
#                 out_data.append(data)
#             # catch the exceptions that are acceptable
#             except (VarNotAvailableError, TimeMatchError, 
#                     DataCoverageError) as e:
#                 logger.warning('Failed to convert to StationData '
#                                'Error: {}'.format(repr(e)))
#                 # append None to make sure indices of stations are 
#                 # preserved in output array
#                 if include_stats_nodata:
#                     out_data.append(None)
#         return out_data
# =============================================================================
    
    # TODO: check more general cases (i.e. no need to convert to StationData
    # if no time conversion is required)
    def get_variable_data(self, variables, start=None, stop=None,
                          ts_type=None, **kwargs):
        """Extract all data points of a certain variable
        
        Parameters
        ----------
        vars_to_extract : :obj:`str` or :obj:`list`
            all variables that are supposed to be accessed
        """
        if isinstance(variables, str):
            variables = [variables]
        all_stations = self.to_station_data_all(variables, start, stop, 
                                                freq=ts_type, **kwargs)
        result = {}
        num_stats = {}
        for var in variables:
            result[var] = []
            num_stats[var] = 0
        for stat_data in all_stations:
            if stat_data is not None:
                num_points = len(stat_data.dtime)
                for var in variables:
                    if var in stat_data:
                        num_stats[var] += 1
                        result[var].extend(stat_data[var])
                    else:
                        result[var].extend([np.nan]*num_points)
        result['num_stats'] = num_stats
        return result
                     
        
    def _check_filter_match(self, meta, str_f, list_f, range_f):
        """Helper method that checks if station meta item matches filters
        
        Note
        ----
        This method is used in :func:`apply_filter`
        """
        for k, v in str_f.items():
            if not meta[k] == v:
                return False
        for k, v in list_f.items():
            if not meta[k] in v:
                return False
        for k, v in range_f.items():
            if not in_range(meta[k], v[0], v[1]):
                return False
        return True
    
    def _init_meta_filters(self, **filter_attributes):
        """Init filter dictionary for :func:`apply_filter_meta`
        
        Parameters
        ----------
        **filter_attributes
            valid meta keywords that are supposed to be filtered and the 
            corresponding filter values (or value ranges)
            Only valid meta keywords are considered (e.g. data_id,
            longitude, latitude, altitude, ts_type)
            
        Returns
        -------
        tuple
            3-element tuple containing
            
            - dict: string match filters for metakeys \
              (e.g. dict['data_id'] = 'AeronetSunV2Lev2.daily')
            - dict: in-list match filters for metakeys \
              (e.g. dict['station_name'] = ['stat1', 'stat2', 'stat3'])
            - dict: in-range dictionary for metakeys \
              (e.g. dict['longitude'] = [-30, 30])
            
        """
        # initiate filters that are checked
        valid_keys = self.metadata[0].keys()
        str_f = {}
        list_f = {}
        range_f = {}
        for key, val in filter_attributes.items():
            if not key in valid_keys:
                raise IOError('Invalid input parameter for filtering: {}. '
                              'Please choose from {}'.format(key, valid_keys))
            
            if isinstance(val, str):
                str_f[key] = val
            elif isinstance(val, (list, np.ndarray, tuple)): 
                if all([isinstance(x, str) for x in val]):
                    list_f[key] = val
                elif len(val) == 2:
                    try:
                        low, high = float(val[0]), float(val[1])
                        range_f[key] = [low, high]
                    except:
                        raise IOError('Failed to convert input ({}) specifying '
                                      'value range of {} into floating point '
                                      'numbers'.format(list(val), key))
        return (str_f, list_f, range_f)
    
    def check_unit(self, var_name, unit=None):
        """Check if variable unit corresponds to AeroCom unit
        
        Parameters
        ----------
        var_name : str
            variable name for which unit is to be checked
        unit : :obj:`str`, optional
            unit to be checked, if None, AeroCom default unit is used
        
        Raises
        ------
        MetaDataError
            if unit information is not accessible for input variable name
        """
        from pyaerocom.helpers import unit_conversion_fac
        if unit is None:
            unit = const.VARS[var_name].units
            
        units =  []
        for i, meta in self.metadata.items():
            if var_name in meta['var_info']:
                try:
                    u = meta['var_info'][var_name]['unit']
                    if not u in units:
                        units.append(u)
                except KeyError:
                    add_str = ''
                    if 'unit' in meta['var_info'][var_name]:
                        add_str = ('Corresponding var_info dict contains '
                                   'attr. "unit", which is deprecated, please '
                                   'check corresponding reading routine. ')
                    raise MetaDataError('Failed to access unit information for '
                                        'variable {} in metadata block {}'
                                        .format(var_name, i))
        if len(units) == 0 and str(unit) != '1':
            raise MetaDataError('Failed to access unit information for '
                                'variable {}. Expected unit {}'
                                .format(var_name, unit))
        for u in units:
            if not unit_conversion_fac(u, unit) == 1:
                raise MetaDataError('Invalid unit {} detected (expected {})'
                                    .format(u, unit))
    
    # TODO: check, confirm and remove Beta version note in docstring   
    def remove_outliers(self, var_name, inplace=False, low=None, high=None,
                        unit_ref=None, move_to_trash=True):
        """Method that can be used to remove outliers from data
        
        Parameters
        ----------
        var_name : str
            variable name
        inplace : bool
            if True, the outliers will be removed in this object, otherwise
            a new oject will be created and returned
        low : float
            lower end of valid range for input variable. If None, then the 
            corresponding value from the default settings for this variable 
            are used (cf. minimum attribute of `available variables 
            <https://pyaerocom.met.no/config_files.html#variables>`__)
        high : float
            upper end of valid range for input variable. If None, then the 
            corresponding value from the default settings for this variable 
            are used (cf. maximum attribute of `available variables 
            <https://pyaerocom.met.no/config_files.html#variables>`__)
        unit_ref : str
            reference unit for assessment of input outlier ranges: all data 
            needs to be in that unit, else an Exception will be raised
        move_to_trash : bool
            if True, then all detected outliers will be moved to the trash 
            column of this data object (i.e. column no. specified at
            :attr:`UngriddedData._TRASHINDEX`).
            
        Returns
        -------
        UngriddedData
            ungridded data object that has all outliers for this variable 
            removed.
            
        Raises
        ------
        ValueError
            if input :attr:`move_to_trash` is True and in case for some of the
            measurements there is already data in the trash.
        Uni
            
        """
        if inplace:
            new = self
        else:
            new = self.copy()
        try:
            self.check_unit(var_name, unit=unit_ref)
        except MetaDataError as e:
            raise MetaDataError('Cannot remove outliers for variable {}. Found '
                                'invalid units. Error: {}'
                                .format(var_name, repr(e)))
            
        if low is None:
            low = const.VARS[var_name].minimum
            print_log.info('Setting {} outlier lower lim: {:.2f}'.format(var_name, low))
        if high is None:
            high = const.VARS[var_name].maximum
            print_log.info('Setting {} outlier upper lim: {:.2f}'.format(var_name, high))
        var_idx = new.var_idx[var_name]
        var_mask = self._data[:, new._VARINDEX] == var_idx
        
        all_data =  self._data[:, self._DATAINDEX]
        invalid_mask = np.logical_or(all_data<low, all_data>high)
        
        mask = invalid_mask * var_mask
        invalid_vals = new._data[mask, new._DATAINDEX]
        new._data[mask, new._DATAINDEX] = np.nan
        
        # check if trash is empty and put outliers into trash
        trash = new._data[mask, new._TRASHINDEX]
        if np.isnan(trash).sum() == len(trash): #trash is empty
            new._data[mask, new._TRASHINDEX] = invalid_vals
        else:
            raise ValueError('Trash is not empty for some of the datapoints. '
                             'Please empty trash first using method '
                             ':func:`empty_trash` or deactivate input arg '
                             ':attr:`move_to_trash`')
        
        info = ('Removed {} outliers from {} data (range: {}-{}, in trash: {})'
                .format(len(invalid_vals), var_name, low, high, move_to_trash))
        
        new._add_to_filter_history(info)
        return new
            
    def _add_to_filter_history(self, info):
        """Add info to :attr:`filter_hist`
        
        Key is current system time string
        
        Parameter
        ---------
        info
            information to be appended to filter history
        """
        time_str = datetime.now().strftime('%Y%m%d%H%M%S')
        self.filter_hist[int(time_str)] = info
        
    def empty_trash(self):
        """Set all values in trash column to NaN"""
        self._data[:, self._TRASHINDEX] = np.nan
      
    @property
    def station_coordinates(self):
        """dictionary with station coordinates
        
        Returns
        -------
        dict
            dictionary containing station coordinates (latitude, longitude, 
            altitude -> values) for all stations (keys) where these parameters 
            are accessible.
        """
        d = {'station_name' : [],
             'latitude'     : [],
             'longitude'    : [],
             'altitude'     : []}
        
        for i, meta in self.metadata.items():
            if not 'station_name' in meta:
                print_log.warning('Skipping meta-block {}: station_name is not '
                                  'defined'.format(i))
                continue
            elif not all(name in meta for name in const.STANDARD_COORD_NAMES):
                print_log.warning('Skipping meta-block {} (station {}): '
                                  'one or more of the coordinates is not '
                                  'defined'.format(i, meta['station_name']))
                continue
            
            stat = meta['station_name']
            
            if stat in d['station_name']:
                continue
            d['station_name'].append(stat)
            for k in const.STANDARD_COORD_NAMES:
                d[k].append(meta[k])
        return d
               
    def _find_meta_matches(self, *filters):
        """Find meta matches for input attributes
            
        Returns
        -------
        list
            list of metadata indices that match input filter
        """
        meta_matches = []
        totnum = 0
        for meta_idx, meta in self.metadata.items():
            if self._check_filter_match(meta, *filters):
                meta_matches.append(meta_idx)
                for var in meta['variables']:
                    totnum += len(self.meta_idx[meta_idx][var])
                
        return (meta_matches, totnum)
                    
    def filter_by_meta(self, **filter_attributes):
        """Flexible method to filter these data based on input meta specs
        
        Parameters
        ----------
        **filter_attributes
            valid meta keywords that are supposed to be filtered and the 
            corresponding filter values (or value ranges)
            Only valid meta keywords are considered (e.g. data_id,
            longitude, latitude, altitude, ts_type)
            
        Returns
        -------
        UngriddedData
            filtered ungridded data object
        
        Raises
        ------
        NotImplementedError
            if attempt variables are supposed to be filtered (not yet possible)
        IOError
            if any of the input keys are not valid meta key
            
        Example
        -------
        >>> import pyaerocom as pya
        >>> r = pya.io.ReadUngridded(['AeronetSunV2Lev2.daily', 
                                      'AeronetSunV3Lev2.daily'], 'od550aer')
        >>> data = r.read()
        >>> data_filtered = data.filter_by_meta(data_id='AeronetSunV2Lev2.daily',
        ...                                     longitude=[-30, 30],
        ...                                     latitude=[20, 70],
        ...                                     altitude=[0, 1000])
        """
        
        meta_idx_new = 0.0
        data_idx_new = 0
    
        
        if 'variables' in filter_attributes:
            raise NotImplementedError('Cannot yet filter by variables')
            
        filters = self._init_meta_filters(**filter_attributes)

        meta_matches, totnum_new = self._find_meta_matches(*filters)
        new = UngriddedData(num_points=totnum_new)
        for meta_idx in meta_matches:
            meta = self.metadata[meta_idx]
            new.metadata[meta_idx_new] = meta
            new.meta_idx[meta_idx_new] = od()
            for var in meta['variables']:
                indices = self.meta_idx[meta_idx][var]
                totnum = len(indices)

                stop = data_idx_new + totnum
                
                new._data[data_idx_new:stop, :] = self._data[indices, :]
                new.meta_idx[meta_idx_new][var] = np.arange(data_idx_new,
                                                            stop)
                new.var_idx[var] = self.var_idx[var]
                data_idx_new += totnum
            
            meta_idx_new += 1

        if meta_idx_new == 0 or data_idx_new == 0:
            raise DataExtractionError('Filtering results in empty data object')
        new._data = new._data[:data_idx_new]
        
        # write history of filtering applied 
        new.filter_hist.update(self.filter_hist)
        time_str = datetime.now().strftime('%Y%m%d%H%M%S')
        new.filter_hist[int(time_str)] = filter_attributes
        new.data_revision.update(self.data_revision)
        
        return new
    
    
    def extract_dataset(self, data_id):
        """Extract single dataset into new instance of :class:`UngriddedData`
        
        Calls :func:`filter_by_meta`.
        
        Parameters
        -----------
        data_id : str
            ID of dataset
        
        Returns
        -------
        UngriddedData
            new instance of ungridded data containing only data from specified
            input network
        """
        logger.info('Extracting dataset {} from data object'.format(data_id))
        return self.filter_by_meta(data_id=data_id)

    def _station_to_json_trends(self, var_name, station_name, 
                                freq, **kwargs):
        """Convert station data to json file for trends interface
        
        Parameters
        ----------
        var_name : str
            variable name (e.g. od550aer)
        station_name : str
            name (or wildcard pattern) that specifies station
        freq : str
            temporal resolution
        **kwargs
            further input arguments that are passed to :func:`to_station_data`
        """
        raise NotImplementedError
        if not isinstance(station_name, str):
            raise ValueError('Require station name (or pattern) as string')
        stat = self.to_station_data(station_name, var_name, freq=freq, **kwargs)
        
        
    def code_lat_lon_in_float(self):
        """method to code lat and lon in a single number so that we can use np.unique to
        determine single locations"""

        # multiply lons with 10 ** (three times the needed) precision and add the lats muliplied with 1E(precision) to it
        self.coded_loc = self._data[:, self._LONINDEX] * 10 ** (3 * self._LOCATION_PRECISION) + (
                self._data[:, self._LATINDEX] + self._LAT_OFFSET) * (10 ** self._LOCATION_PRECISION)
        return self.coded_loc
    
    def decode_lat_lon_from_float(self):
        """method to decode lat and lon from a single number calculated by code_lat_lon_in_float
        """

        lons = np.trunc(self.coded_loc / 10 ** (2 * self._LOCATION_PRECISION)) / 10 ** self._LOCATION_PRECISION
        lats = (self.coded_loc - np.trunc(self.coded_loc / 10 ** (2 * self._LOCATION_PRECISION)) * 10 ** (
                2 * self._LOCATION_PRECISION)) / (10 ** self._LOCATION_PRECISION) - self._LAT_OFFSET

        return lats, lons
            
    def _find_common_meta(self, ignore_keys=None):
        """Searches all metadata dictionaries that are the same
        
        Parameters
        ----------
        ignore_keys : list
            list containing meta keys that are supposed to be ignored
            
        Returns
        -------
        tuple
            2-element tuple containing
            
            - list containing lists with common meta indices
            - list containing corresponding meta dictionaries
        """
        if ignore_keys is None:
            ignore_keys = []
        meta_registered = []
        same_indices = []
        for meta_key, meta in self.metadata.items():
            found = False
            for idx, meta_reg in enumerate(meta_registered):
                try:
                    if same_meta_dict(meta_reg, meta, ignore_keys=ignore_keys):
                        same_indices[idx].append(meta_key)
                        found = True
                except:
                    print()
            if not found:
                meta_registered.append(meta)
                same_indices.append([meta_key])
        
        return same_indices
    
    def merge_common_meta(self, ignore_keys=None):
        """Merge all meta entries that are the same
        
        Note
        ----
        If there is an overlap in time between the data, the blocks are not
        merged
            
        Todo
        ----
        Keep mapping of ``var_info`` (if defined in ``metadata``) to data 
        points (e.g. EBAS), since the data sources may be at different 
        wavelengths.
        
        Parameters
        ----------
        ignore_keys : list
            list containing meta keys that are supposed to be ignored
            
        Returns
        -------
        UngriddedData
            merged data object
        """
        if ignore_keys is None:
            ignore_keys = []
        sh = self.shape
        lst_meta_idx = self._find_common_meta(ignore_keys)
        new = UngriddedData(num_points=self.shape[0])
        didx = 0
        for i, idx_lst in enumerate(lst_meta_idx):
            _meta_check = od()
            # write metadata of first index that matches
            _meta_check.update(self.metadata[idx_lst[0]])
            _meta_idx_new = od()
            for j, meta_idx in enumerate(idx_lst):
                if j > 0: # don't check first against first
                    meta = self.metadata[meta_idx]
                    if not same_meta_dict(meta, _meta_check,  
                                          ignore_keys=ignore_keys):
                        raise ValueError('Unexpected error. Please debug or '
                                         'contact jonasg@met.no')
                    for k in ignore_keys:
                        if k in meta:
                            if not k in _meta_check:
                                _meta_check[k] = meta[k]
                            else:
                                if not isinstance(_meta_check[k], list):
                                    _meta_check[k] = [_meta_check[k]]
                                if not meta[k] in _meta_check[k]:
                                    _meta_check[k].append(meta[k])
                           
                data_var_idx = self.meta_idx[meta_idx]
                for var, data_idx in data_var_idx.items():
                    num = len(data_idx)
                    stop = didx + num
                    new._data[didx:stop, :] = self._data[data_idx]
                    new._data[didx:stop, 0] = i
                    if not var in _meta_idx_new:
                        _meta_idx_new[var] = np.arange(didx, stop)
                    else:
                        _idx = np.append(_meta_idx_new[var], np.arange(didx, stop))
                        _meta_idx_new[var] = _idx
                    didx += num
            
            new.meta_idx[i] = _meta_idx_new
            new.metadata[i] = _meta_check
        new.var_idx.update(self.var_idx)
        #new.unit = self.unit
        new.filter_hist.update(self.filter_hist)
        if not new.shape == sh:
            raise Exception('FATAL: Mismatch in shape between initial and '
                            'and final object. Developers: please check')
        return new
        
    def merge(self, other, new_obj=True):
        """Merge another data object with this one
        
        Parameters
        -----------
        other : UngriddedData
            other data object
        new_obj : bool
            if True, this object remains unchanged and the merged data objects
            are returned in a new instance of :class:`UngriddedData`. If False, 
            then this object is modified
        
        Returns
        -------
        UngriddedData
            merged data object
            
        Raises
        -------
        ValueError
            if input object is not an instance of :class:`UngriddedData`
        """
        if not isinstance(other, UngriddedData):
            raise ValueError("Invalid input, need instance of UngriddedData, "
                             "got: {}".format(type(other)))
        if new_obj:
            obj = self.copy()
        else:
            obj = self
        
        if obj.is_empty:
            obj._data = other._data
            obj.metadata = other.metadata
            #obj.unit = other.unit
            obj.data_revision = other.data_revision
            obj.meta_idx = other.meta_idx
            obj.var_idx = other.var_idx
        else:
            # get offset in metadata index
            meta_offset = max([x for x in obj.metadata.keys()]) + 1
            data_offset = obj.shape[0]

            # add this offset to indices of meta dictionary in input data object
            for meta_idx_other, meta_other in other.metadata.items():
                meta_idx = meta_offset + meta_idx_other
                obj.metadata[meta_idx] = meta_other
                _idx_map = od()
                for var_name, indices in other.meta_idx[meta_idx_other].items():
                    _idx_map[var_name] = np.asarray(indices) + data_offset
                obj.meta_idx[meta_idx] = _idx_map
            
            for var, idx in other.var_idx.items():
                if var in obj.var_idx: #variable already exists in this object
                    if not idx == obj.var_idx[var]:
                        other.change_var_idx(var, obj.var_idx[var])
# =============================================================================
#                         raise AttributeError('Could not merge data objects. '
#                                              'Variable {} occurs in both '
#                                              'datasets but has different '
#                                              'variable index in data array'
#                                              .format(var))
# =============================================================================
                else: # variable does not yet exist
                    idx_exists = [v for v in obj.var_idx.values()]
                    if idx in idx_exists: 
                        # variable index is already assigned to another 
                        # variable and needs to be changed
                        new_idx = max(idx_exists)+1
                        other.change_var_idx(var, new_idx)
                        obj.var_idx[var] = new_idx
                    else:
                        obj.var_idx[var] = idx
            obj._data = np.vstack([obj._data, other._data])
            obj.data_revision.update(other.data_revision)
        obj.filter_hist.update(other.filter_hist)
        return obj
    
    def change_var_idx(self, var_name, new_idx):
        """Change index that is assigned to variable
        
        Each variable in this object has assigned a unique index that is
        stored in the dictionary :attr:`var_idx` and which is used internally
        to access data from a certain variable from the data array 
        :attr:`_data` (the indices are stored in the data column specified by
        :attr:`_VARINDEX`, cf. class header).
        
        This index thus needs to be unique for each variable and hence, may 
        need to be updated, when two instances of :class:`UngriddedData` are 
        merged (cf. :func:`merge`). 

        And the latter is exactrly what this function does.
        
        Parameters
        ----------
        var_name : str
            name of variable
        new_idx : int
            new index of variable
            
        Raises
        ------
        ValueError
            if input ``new_idx`` already exist in this object as a variable 
            index
        """
        if new_idx in self.var_idx.values():
            raise ValueError('Fatal: variable index cannot be assigned a new '
                             'index that is already assigned to one of the '
                             'variables in this object')
        cidx = self.var_idx[var_name]
        self.var_idx[var_name] = new_idx
        var_indices = np.where(self._data[:, self._VARINDEX]==cidx)
        self._data[var_indices, self._VARINDEX] = new_idx
        
    def append(self, other):
        """Append other instance of :class:`UngriddedData` to this object
        
        Note
        ----
        Calls :func:`merge(other, new_obj=False)`
        
        Parameters
        -----------
        other : UngriddedData
            other data object
        
        Returns
        -------
        UngriddedData
            merged data object
            
        Raises
        -------
        ValueError
            if input object is not an instance of :class:`UngriddedData`
            
        """
        return self.merge(other, new_obj=False)  
    
    def all_datapoints_var(self, var_name):
        """Get array of all data values of input variable
        
        Parameters
        ----------
        var_name : str
            variable name
            
        Returns
        -------
        ndarray
            1-d numpy array containing all values of this variable 
            
        Raises
        ------
        AttributeError
            if variable name is not available
        """
        if not var_name in self.var_idx:
            raise AttributeError('Variable {} not available in data'
                                 .format(var_name))
        idx = self.var_idx[var_name]
        mask = np.where(self._data[:, self._VARINDEX]==idx)[0]
        return self._data[mask, self._DATAINDEX]
    
    def num_obs_var_valid(self, var_name):
        """Number of valid observations of variable in this dataset
        
        Parameters
        ----------
        var_name : str
            name of variable
        
        Returns
        -------
        int
            number of valid observations (all values that are not NaN)
        """
        pass
    
    def find_common_stations(self, other, check_vars_available=None,
                             check_coordinates=True, 
                             max_diff_coords_km=0.1):
        """Search common stations between two UngriddedData objects
        
        This method loops over all stations that are stored within this 
        object (using :attr:`metadata`) and checks if the corresponding 
        station exists in a second instance of :class:`UngriddedData` that
        is provided. The check is performed on basis of the station name, and
        optionally, if desired, for each station name match, the lon lat 
        coordinates can be compared within a certain radius (defaul 0.1 km).
        
        Note
        ----
        This is a beta version and thus, to be treated with care.
        
        Parameters
        ----------
        other : UngriddedData
            other object of ungridded data 
        check_vars_available : :obj:`list` (or similar), optional
            list of variables that need to be available in stations of both 
            datasets
        check_coordinates : bool
            if True, check that lon and lat coordinates of station candidates
            match within a certain range, specified by input parameter
            ``max_diff_coords_km``
            
        Returns
        -------
        OrderedDict
            dictionary where keys are meta_indices of the common station in 
            this object and corresponding values are meta indices of the 
            station in the other object
            
        """
        if len(self.contains_datasets) > 1:
            raise NotImplementedError('This data object contains data from '
                                      'more than one dataset and thus may '
                                      'include multiple station matches for '
                                      'each station ID. This method, however '
                                      'is implemented such, that it checks '
                                      'only the first match for each station')
        elif len(other.contains_datasets) > 1:
            raise NotImplementedError('Other data object contains data from '
                                      'more than one dataset and thus may '
                                      'include multiple station matches for '
                                      'each station ID. This method, however '
                                      'is implemented such, that it checks '
                                      'only the first match for each station')
        _check_vars = False
        if check_vars_available is not None:
            _check_vars = True
            if isinstance(check_vars_available, str):
                check_vars_available = [check_vars_available]
            elif isinstance(check_vars_available, (tuple, np.ndarray)):
                check_vars_available = list(check_vars_available)
            if not isinstance(check_vars_available, list):
                raise ValueError('Invalid input for check_vars_available. Need '
                                 'str or list-like, got: {}'
                                 .format(check_vars_available))
        lat_len = 111.0 #approximate length of latitude degree in km
        station_map = od()
        stations_other = other.station_name
        for meta_idx, meta in self.metadata.items():
            name = meta['station_name']
            # bool that is used to accelerate things
            ok = True
            if _check_vars:
                for var in check_vars_available:
                    try:
                        if not var in meta['variables']:
                            logger.debug('No {} in data of station {}'
                                         '({})'.format(var, name, 
                                                       meta['data_id']))
                            ok = False
                    except: # attribute does not exist or is not iterable
                        ok = False
            if ok and name in stations_other:
                for meta_idx_other, meta_other in other.metadata.items():
                    if meta_other['station_name'] == name:
                        if _check_vars:
                            for var in check_vars_available:
                                try:
                                    if not var in meta_other['variables']:
                                        logger.debug('No {} in data of station'
                                                     ' {} ({})'.format(var, 
                                                     name, 
                                                     meta_other['data_id']))
                                        ok = False
                                except: # attribute does not exist or is not iterable
                                    ok = False
                        if ok and check_coordinates:
                            dlat = abs(meta['latitude']-meta_other['latitude'])
                            dlon = abs(meta['longitude']-meta_other['longitude'])
                            lon_fac = np.cos(np.deg2rad(meta['latitude']))
                            #compute distance between both station coords
                            dist = np.linalg.norm((dlat*lat_len, 
                                                   dlon*lat_len*lon_fac))
                            if dist > max_diff_coords_km:
                                logger.warning('Coordinate of station '
                                               '{} varies more than {} km '
                                               'between {} and {} data. '
                                               'Retrieved distance: {:.2f} km '
                                               .format(name, max_diff_coords_km,
                                                       meta['data_id'],
                                                       meta_other['data_id'],
                                                       dist))
                                ok = False
                        if ok: #match found
                            station_map[meta_idx] = meta_idx_other
                            logger.debug('Found station match {}'.format(name))
                            # no need to further iterate over the rest 
                            continue
                        
        return station_map
        
    # TODO: brute force at the moment, we need to rethink and define how to
    # work with time intervals and perform temporal merging.
    def find_common_data_points(self, other, var_name, sampling_freq='daily'):
        if not sampling_freq == 'daily':
            raise NotImplementedError('Currently only works with daily data')
        if not isinstance(other, UngriddedData):
            raise NotImplementedError('So far, common data points can only be '
                                      'retrieved between two instances of '
                                      'UngriddedData')
        #find all stations that are common
        common = self.find_common_stations(other, 
                                           check_vars_available=var_name,
                                           check_coordinates=True)
        if len(common) == 0:
            raise DataExtractionError('None of the stations in the two '
                                      'match')
        dates = []
        data_this_match = []
        data_other_match = []
        
        for idx_this, idx_other in common.items():
            data_idx_this = self.meta_idx[idx_this][var_name]
            data_idx_other = other.meta_idx[idx_other][var_name]
            
            # timestamps of variable match for station...
            dtimes_this = self._data[data_idx_this, self._TIMEINDEX]
            dtimes_other = other._data[data_idx_other, other._TIMEINDEX]
            # ... and corresponding data values of variable
            data_this = self._data[data_idx_this, self._DATAINDEX]
            data_other = other._data[data_idx_other, other._DATAINDEX]
            # round to daily resolution. looks too complicated, but is much 
            # faster than pandas combined with datetime 
            date_nums_this = (dtimes_this.astype('datetime64[s]').
                              astype('M8[D]').astype(int))
            date_nums_other = (dtimes_other.astype('datetime64[s]').
                               astype('M8[D]').astype(int))
            
            # TODO: loop over shorter array
            for idx, datenum in enumerate(date_nums_this):
                matches = np.where(date_nums_other==datenum)[0]
                if len(matches) == 1:
                    dates.append(datenum)
                    data_this_match.append(data_this[idx])
                    data_other_match.append(data_other[matches[0]])
        
        return (dates, data_this_match, data_other_match)
    
    def _meta_to_lists(self):
        meta = {k:[] for k in self.metadata[0].keys()}
        for meta_item in self.metadata.values():
            for k, v in meta.items():
                v.append(meta_item[k])
        return meta
            
    def get_timeseries(self, station_name, var_name, start=None, stop=None,
                      ts_type=None, insert_nans=True, **kwargs):
        """Get variable timeseries data for a certain station
        
        Parameters
        ----------
        station_name : :obj:`str` or :obj:`int`
            station name or index of station in metadata dict
        var_name : str
            name of variable to be retrieved
        start 
            start time (optional)
        stop 
            stop time (optional). If start time is provided and stop time not, 
            then only the corresponding year inferred from start time will be 
            considered
        ts_type : :obj:`str`, optional
            temporal resolution (can be pyaerocom ts_type or pandas freq. 
            string)
        **kwargs
            Additional keyword args passed to method :func:`to_station_data`
            
        Returns
        -------
        pandas.Series
            time series data
        """
        if 'merge_if_multi' in kwargs:
            if not kwargs.pop['merge_if_multi']:
                print_log.warning('Invalid input merge_if_multi=False'
                                  'setting it to True')
        stat = self.to_station_data(station_name, var_name, start, stop, 
                                    freq=ts_type, merge_if_multi=True,
                                    insert_nans=insert_nans,
                                    **kwargs)
        return stat.to_timeseries(var_name)
        
    
    def plot_station_timeseries(self, station_name, var_name, start=None, 
                                stop=None, ts_type=None,
                                insert_nans=True, ax=None, **kwargs):
        """Plot time series of station and variable
        
        Parameters
        ----------
        station_name : :obj:`str` or :obj:`int`
            station name or index of station in metadata dict
        var_name : str
            name of variable to be retrieved
        start 
            start time (optional)
        stop 
            stop time (optional). If start time is provided and stop time not, 
            then only the corresponding year inferred from start time will be 
            considered
        ts_type : :obj:`str`, optional
            temporal resolution
        
        **kwargs
            Addifional keyword args passed to method :func:`pandas.Series.plot`
            
        Returns
        -------
        axes
            matplotlib axes instance
            
        """
        if ax is None:
            import matplotlib.pyplot as plt
            from pyaerocom.plot.config import FIGSIZE_DEFAULT
            fig, ax = plt.subplots(figsize=FIGSIZE_DEFAULT)
        
        stat = self.to_station_data(station_name, var_name, start, stop, 
                                    freq=ts_type, merge_if_multi=True,
                                    insert_nans=insert_nans)
        #s = self.get_timeseries(station_name, var_name, start, stop, ts_type)
        #s.plot(ax=ax, **kwargs)
        ax = stat.plot_timeseries(var_name, ax=ax, **kwargs)
        return ax
        
    def plot_station_coordinates(self, var_name=None, 
                                 filter_name=None, start=None, 
                                 stop=None, ts_type=None, color='r', 
                                 marker='o', markersize=8, fontsize_base=10, 
                                 **kwargs):
        """Plot station coordinates on a map
        
        All input parameters are optional and may be used to add constraints 
        related to which stations are plotted. Default is all stations of all 
        times.
        
        Parameters
        ----------
        
        var_name : :obj:`str`, optional
            name of variable to be retrieved
        filter_name : :obj:`str`, optional
            name of filter (e.g. EUROPE-noMOUNTAINS)
        start 
            start time (optional)
        stop 
            stop time (optional). If start time is provided and stop time not, 
            then only the corresponding year inferred from start time will be 
            considered
        ts_type : :obj:`str`, optional
            temporal resolution
        color : str
            color of stations on map
        marker : str
            marker type of stations
        markersize : int
            size of station markers
        fontsize_base : int
            basic fontsize 
        **kwargs
            Addifional keyword args passed to 
            :func:`pyaerocom.plot.plot_coordinates`
            
        Returns
        -------
        axes
            matplotlib axes instance
            
        """
        
        from pyaerocom import Filter
        from pyaerocom.plot.plotcoordinates import plot_coordinates
        from pyaerocom.plot.mapping import set_map_ticks
    
        if len(self.contains_datasets) > 1:
            print_log.warning('UngriddedData object contains more than one '
                              'dataset ({}). Station coordinates will not be '
                              'distinguishable. You may want to apply a filter '
                              'first and plot them separately')
        
        f = Filter(filter_name) 
        if var_name is None:
            info_str = 'AllVars'
        else:
            if not isinstance(var_name, str):
                raise ValueError('Can only handle single variable (or all'
                                 '-> input var_name=None)')
            elif not var_name in self.contains_vars:
                raise ValueError('Input variable is not available in dataset '
                                 .format(var_name))
            info_str = var_name
    
        info_str += '_{}'.format(f.name)
        try:
            info_str += '_{}'.format(start_stop_str(start, stop, ts_type))
        except:
            info_str += '_AllTimes'
        if ts_type is not None:
            info_str += '_{}'.format(ts_type)
        
        if all([x is None for x in (var_name, filter_name, start, stop)]): #use all stations
            all_meta = self._meta_to_lists()
            lons, lats = all_meta['longitude'], all_meta['latitude']
            
        else:
            stat_data = self.to_station_data_all(var_name, start, stop, 
                                                 ts_type)
            
            if len(stat_data['stats']) == 0:
                raise DataCoverageError('No stations could be found for input '
                                        'specs (var, start, stop, freq)')
            lons = stat_data['longitude']    
            lats = stat_data['latitude']    
        if not 'label' in kwargs:
            kwargs['label'] = info_str
        ax = plot_coordinates(lons, lats,
                              color=color, marker=marker, 
                              markersize=markersize, 
                              fontsize_base=fontsize_base, **kwargs)
        region = f._region
        ax.set_xlim(region.lon_range_plot)
        ax.set_ylim(region.lat_range_plot)
    
        ax = set_map_ticks(ax, 
                           region.lon_ticks, 
                           region.lat_ticks)
        
        if 'title' in kwargs:
            title = kwargs['title']
        else:
            title = info_str
        ax.set_title(title, fontsize=fontsize_base+4)
        return ax
        
        
    def __contains__(self, key):
        """Check if input key (str) is valid dataset, variable, instrument or
        station name
        
        
        Parameters
        ----------
        key : str
            search key
            
        Returns
        -------
        bool
            True, if key can be found, False if not
        """
        
        if not isinstance(key, str):
            raise ValueError('Need string (e.g. variable name, station name, '
                             'instrument name')
        if key in self.contains_datasets:
            return True
        elif key in self.contains_vars:
            return True
        elif key in self.station_name:
            return True
        elif key in self.contains_instruments:
            return True
        return False
        
    def __repr__(self):
        return ('{} <networks: {}; vars: {}; instruments: {};'
                'No. of stations: {}'
                .format(type(self).__name__,self.contains_datasets,
                        self.contains_vars, self.contains_instruments,
                        len(self.metadata)))
        
    def __getitem__(self, key):
        return self.to_station_data(key, insert_nans=True)
    
    def __and__(self, other):
        """Merge this object with another using the logical ``and`` operator
        
        Example
        -------
        >>> from pyaerocom.io import ReadAeronetSdaV2
        >>> read = ReadAeronetSdaV2()
        
        >>> d0 = read.read(last_file=10)
        >>> d1 = read.read(first_file=10, last_file=20)
    
        >>> merged = d0 & d1
        
        >>> print(d0.shape, d1.shape, merged.shape)
        (7326, 11) (9894, 11) (17220, 11)
        """
        return self.merge(other, new_obj=True)
    
    def __str__(self):
        head = "Pyaerocom {}".format(type(self).__name__)
        s = "\n{}\n{}".format(head, len(head)*"-")
        s += ('\nContains networks: {}'
              '\nContains variables: {}'
              '\nContains instruments: {}'
              '\nTotal no. of meta-blocks: {}'.format(self.contains_datasets,
                                                   self.contains_vars,
                                                   self.contains_instruments,
                                                   len(self.metadata)))
        if self.is_filtered:
            s += '\nFilters that were applied:'
            for tstamp, f in self.filter_hist.items():
                if f:
                    s += '\n Filter time log: {}'.format(tstamp)
                    if isinstance(f, dict):
                        for key, val in f.items():
                            s += '\n\t{}: {}'.format(key, val)
                    else:
                        s += '\n\t{}'.format(f)
                    
        return s
   
    # DEPRECATED METHODS
    @property
    def vars_to_retrieve(self):
        logger.warning(DeprecationWarning("Attribute vars_to_retrieve is "
                                          "deprectated. Please use attr "
                                          "contains_vars instead"))
        return self.contains_vars
    
    def get_time_series(self, station, var_name, start=None, stop=None, 
                        ts_type=None, **kwargs):
        """Get time series of station variable
        
        Parameters
        ----------
        station : :obj:`str` or :obj:`int`
            station name or index of station in metadata dict
        var_name : str
            name of variable to be retrieved
        start 
            start time (optional)
        stop 
            stop time (optional). If start time is provided and stop time not, 
            then only the corresponding year inferred from start time will be 
            considered
        ts_type : :obj:`str`, optional
            temporal resolution
        **kwargs
            Additional keyword args passed to method :func:`to_station_data`
            
        Returns
        -------
        pandas.Series
            time series data
        """
        logger.warning(DeprecationWarning('Outdated method, please use to_timeseries'))
        
        data = self.to_station_data(station, var_name, 
                                     start, stop, freq=ts_type,
                                     **kwargs) 
        if not isinstance(data, StationData):
            raise NotImplementedError('Multiple matches found for {}. Cannot '
                                      'yet merge multiple instances '
                                      'of StationData into one single '
                                      'timeseries. Coming soon...'.format(station))
        return data.to_timeseries(var_name)
    
    # TODO: review docstring        
    def to_timeseries(self, station_name=None, start_date=None, end_date=None, 
                      freq=None):
        """Convert this object into individual pandas.Series objects

        Parameters
        ----------
        station_name : :obj:`tuple` or :obj:`str:`, optional
            station_name or list of station_names to return
        start_date, end_date : :obj:`str:`, optional
            date strings with start and end date to return
        freq : obj:`str:`, optional
            frequency to resample to using the pandas resample method
            us the offset aliases as noted in
            http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases

        Returns
        -------
        list or dictionary
            station_names is a string: dictionary with station data
            station_names is list or None: list of dictionaries with station data

        Example
        -------
        >>> import pyaerocom.io.readobsdata
        >>> obj = pyaerocom.io.readobsdata.ReadUngridded()
        >>> obj.read()
        >>> pdseries = obj.to_timeseries()
        >>> pdseriesmonthly = obj.to_timeseries(station_name='Avignon',start_date='2011-01-01', end_date='2012-12-31', freq='M')
        """
        from warnings import warn
        msg = ('This method name is deprecated, please use to_timeseries')
        warn(DeprecationWarning(msg))
        
        if station_name is None:
            stats = self.to_station_data_all(start=start_date, stop=end_date,
                                             freq=freq)
            stats['stats']
        if isinstance(station_name, str):
            station_name = [station_name]
        if isinstance(station_name, list):
            indices = []
            for meta_idx, info in self.metadata.items():
                if info['station_name'] in station_name:
                    indices.append(meta_idx)
            if len(indices) == 0:
                raise MetaDataError('No such station(s): {}'.format(station_name))
            elif len(indices) == 1:
                # return single dictionary, like before 
                # TODO: maybe change this after clarification
                return self.to_station_data(start=start_date, stop=end_date,
                                            freq=freq)
            else:
                out_data = []
                for meta_idx in indices:
                    try:
                        out_data.append(self.to_station_data(start=start_date, 
                                                             stop=end_date,
                                                             freq=freq))
                    except (VarNotAvailableError, TimeMatchError, 
                            DataCoverageError) as e:
                        logger.warning('Failed to convert to StationData '
                               'Error: {}'.format(repr(e)))
                return out_data
    
def reduce_array_closest(arr_nominal, arr_to_be_reduced):
    test = sorted(arr_to_be_reduced)
    closest_idx = []
    for num in sorted(arr_nominal):
        idx = np.argmin(abs(test - num))
        closest_idx.append(idx)
        test = test[(idx+1):]
    return closest_idx    
        
if __name__ == "__main__":
    
    import pyaerocom as pya


    data = pya.io.ReadUngridded().read('EBASMC',
                                       ['scatc550aer', 'absc550aer'],
                                       station_names='Puy*')

    data1 =  data.remove_outliers('scatc550aer')

    stat = data1.to_station_data('P*', 'scatc550aer',
                                  merge_if_multi=True,
                                  merge_pref_attr='revision_date')

    stat.plot_timeseries('scatc550aer', add_overlaps=True)
    data = pya.io.ReadUngridded().read('EBASMC', ['scatc550dryaer',
                               'absc550aer'])
    
    f = pya.Filter(altitude_filter='noMOUNTAINS')
    
    subset = f(data)
    
