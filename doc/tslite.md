  ------------ ---------------------------------------------------------------------------------------
   \           [index](.)\
   \           [/home/gunnar/projects/tslite/tslite.py](file:/home/gunnar/projects/tslite/tslite.py)
  **tslite**   
  ------------ ---------------------------------------------------------------------------------------

`tslite - Light and portable time series library v1.8.2 20 May 2019 Author: Gunnar Leffler`

 \
**Modules**

`      `

 

  ------------------------------------------ -------------------------- ------------------------ --
  [dateutil.parser](dateutil.parser.html)\   [os](os.html)\             [struct](struct.html)\   
  [datetime](datetime.html)\                 [re](re.html)\             [sys](sys.html)\         
  [math](math.html)\                         [sqlite3](sqlite3.html)\   [time](time.html)\       
                                                                                                 
  ------------------------------------------ -------------------------- ------------------------ --

 \
**Classes**

`      `

 

[rdb](tslite.html#rdb)

[tablegrid](tslite.html#tablegrid)

[timeseries](tslite.html#timeseries)

 \
[class **rdb**]()

`   `

 

Methods defined here:\

[**\_\_init\_\_**]()(self, path)
:   `#construtor rewrites a path to a RDB file`

[**\_\_str\_\_**]()(self)

[**interpolateValue**]()(self, x0, y0, x1, y1, x)
:   `#interpolate values #This may be changed to a higher order interpolation in the future`

[**loadRDB**]()(self, path)

[**makeRating**]()(self, indepTS, depTS, precision=2, factor=1)
:   `Creates a rating table based on two timeseries precision is for how many decimal places to consider factor to adjust dependent variable (kcfs->cfs, fudge factor, etc)`

[**parseRDB**]()(self, stream)

[**rate**]()(self, indep)
:   `Rate a single value based on linear interpolation.`

[**rate2**]() = [reverseRate](#rdb-reverseRate)(self, indep)

[**rateTS**]()(self, ts)
:   `Generates a new time series with rated values from another`

[**rateTS2**]() = [reverseRateTS](#rdb-reverseRateTS)(self, ts)

[**reverseRate**]()(self, indep)
:   `Reverse rate a single value based on linear interpolation This switches the domain and range of the RDB and rates it.`

<!-- -->

[**reverseRateTS**]()(self, ts)
:   `Generates a new time series with reverse-rated values from another`

[**saveRDB**]()(self, path)

 \
[class **tablegrid**]()

`   `

 

Methods defined here:\

[**\_\_init\_\_**]()(self, path)
:   `#construtor rewrites a path to a RDB file`

[**bilinear**]()(self, x1, y1, x2, y2, fQ11, fQ12, fQ21, fQ22, x, y)

[**loadTable**]()(self, path)

[**rateTS**]()(self, cols, rows)
:   `#this takes 2 timseries objects and rates them`

[**tableLookup**]()(self, arr, colval, rowval)

 \
**timeSeries** = [class timeseries]()

`   `

 

Methods defined here:\

[**SQLITE3connect**]()(\*args, \*\*kwargs)
:   `Get a SQLITE 3 database connection dbPath - path to the database file`

<!-- -->

[**SQLITE3disconnect**]()(\*args, \*\*kwargs)
:   `Disconnect from a SQLITE3 database connection`

<!-- -->

[**TD**]()(self, input)
:   `TD takes a relative time and turns it into a timedelta input format: 1w7d6h9m`

<!-- -->

[**\_\_eq\_\_**]()(self, other, precision=6)
:   `Checks to see if a timeseries is equal to another you can specify how many decimal places to check. default is six decimals"`

<!-- -->

[**\_\_getitem\_\_**]()(self, idx)
:   `returns (gets) a timeslice from self.data from supplied index. Example : ts[1] would return [datetime,value,quality]`

<!-- -->

[**\_\_init\_\_**]()(self, data=None)
:   `"overloaded" timeseries constructor expects data to be tuple of datetime obj, observation value (typically float), and a quality flag)`

[**\_\_len\_\_**]()(self)

[**\_\_str\_\_**]()(self)
:   `Equivalent to toString() in other languages returns a tab delineated timeseries`

<!-- -->

[**accumulate**]()(self, interval, override\_startTime=None)
:   `accumulates timeseries based on a given interval of type timedelta returns a timeseries object`

<!-- -->

[**accumulateWY**]()(self, interval, incrTS, offset=datetime.timedelta(0))
:   `accumulates input timeseries and adds to self on an interval of type timedelta this resets every wateryear self is assumed to be an accumulated timeseries  returns a timeseries object`

<!-- -->

[**add**]()(self, operand)
:   `Subtracts an operand timeseries or constant from self`

<!-- -->

[**average**]()(self, interval)
:   `averages timeseries based on a given interval of type timedelta returns a timeseries object`

<!-- -->

[**averageWY**]()(self)
:   `averages each element in the timeseries in previous water years returns a timeseries object`

<!-- -->

[**centerMovingAverage**]()(self, interval)
:   `averages timeseries based on a given interval of type timedelta  returns a timeseries object containing center moving average`

<!-- -->

[**cull**]()(self, op, operand)
:   `culls data from self op: lambda function to perform eg lambda x,y: x>y operand: could be a timeseries or a float returns a timeseries object`

[**cullvalues**]()(self, value)

[**cut**]()(self, other)
:   `cuts a timeseries from self where datetimes intersect with other.  returns a timeseries object`

<!-- -->

[**diff**]()(self, other)
:   `Returns the differences between self and timeseries other governs`

<!-- -->

[**div**]()(self, operand)
:   `divides an self by an operand timeseries or constant`

<!-- -->

[**fillMissing**]()(self, interval, value, starttime=None, endtime=None)
:   `fills values in a timeseries on a specified interval if they are not present. Useful for marking missing values in timeseries returns a timeseries object`

<!-- -->

[**filldown**]()(self, interval, starttime=None, offset=None, \_endtime=None)
:   `fills timeslices in timeseries from the previous value until a new value is detected if start time is specified, It will fill with zeroes on the interval until a value is found if a timezone offset is passed, it will fill to the offset returns a timeseries object`

<!-- -->

[**findClosestIndex**]()(self, key)
:   `returns the index of a given timestamp returns closest index if not found`

<!-- -->

[**findIndex**]()(self, key)
:   `returns the index of a given timestamp returns -1 if not found`

<!-- -->

[**findValue**]()(self, timestamp)
:   `returns a value at a given timestamp returns None type if not found`

[**firstdifference**]()(self)

[**fromBinary**]()(self, buf)
:   `Reads the timeseries from a binary buffer`

<!-- -->

[**fromTSV**]()(self, lines)
:   `reads a timeseries from a TSV string  This method mutates the object, and also returns a pointer to self.`

<!-- -->

[**getStatus**]()(self)
:   `exceptions get dropped into self.status This method gets status message of object and resets self.status to "OK"`

<!-- -->

[**getWY**]()(self, WY)
:   `Gets a water year`

<!-- -->

[**globalAverage**]()(self)
:   `averages entire timeseries returns a timeslice`

<!-- -->

[**globalMax**]()(self)
:   `finds the max of a timeseries returns a timeslice`

<!-- -->

[**globalMin**]()(self)
:   `averages minimum of a timeseries returns a timeslice`

<!-- -->

[**insert**]()(self, datestamp, value, quality=0)
:   `Inserts a timestamp, value and quality into the timseries. this module assumes that datetimes are in acending order, as such please use this method when adding data`

<!-- -->

[**interpolate**]()(self, interval)
:   `interpolates timeseries based on a given interval of type timedelta returns a timeseries object`

<!-- -->

[**interpolateValue**]()(self, x0, y0, x1, y1, x)
:   `interpolate values`

<!-- -->

[**linreg**]()(self)
:   `returns a tuple of linear regression cooeficinets (m,b,r) for a line defined as y = mx+b m - slope b - slope intercept r - correlation coeeficient NOTE: x is in seconds past the epoch`

<!-- -->

[**loadBinary**]()(self, path)
:   `Reads the timeseries from a binary file and inserts values into self`

<!-- -->

[**loadSQLITE3**]()(\*args, \*\*kwargs)
:   `loads a timeseries from a SQLITE3 database Reads a time series from the database# conn - SQLITE3 connection tsid - string LOC_PARAM start_time - datetime end_time - datetime`

<!-- -->

[**loadTSV**]()(self, path)
:   `Reads a timeseries from a tsv file. Hash (#) can be used as comments Format <Datetime>        <value> <quality> if quality is not present,  will defualt to 0 This method mutates the object, and also returns a pointer to self.`

<!-- -->

[**maxmin**]()(self, interval, cmp)
:   `returns a max or a min based for a given interval of type datetime returns a timeseries object`

<!-- -->

[**merge**]()(self, other)
:   `Merges another timeseries into self, retruns resultant timeseries`

[**minDate**]()(self, timefmt='%m/%d/%Y %k:%M:%S')

[**movingaverage**]()(self, interval)
:   `averages timeseries based on a given interval of type timedelta. This differs from rollingaverage because it looks backwards.  returns a timeseries object`

<!-- -->

[**movingstddev**]()(self, interval)
:   `Returns a moving standard deviaton over specified interval.   returns a timeseries object`

<!-- -->

[**mul**]()(self, operand)
:   `multiplies an operand timeseries or constant to self`

<!-- -->

[**operation**]()(self, op, operand)
:   `Performs an operation on self op: lambda function to perform eg lambda x,y: x+y operand: could be a timeseries or a float returns a timeseries object`

[**parseTimedelta**]()(self, input)

[**percent**]()(self, denom)
:   `Calculates the percentage of two timeseries numerator : self denominator : denom returns a timeseries object of percentages`

<!-- -->

[**remove\_stddev\_outliers**]()(\*args, \*\*kwargs)
:   `Remove Outliers using Standard Deviation`

<!-- -->

[**rollingaverage**]()(self, interval)
:   `averages timeseries based on a given interval of type timedelta. Moving average looking forward.  returns a timeseries object`

<!-- -->

[**round**]()(self, precision)
:   `Rounds values in timeseries to a given number of decimal places`

<!-- -->

[**runningTotal**]()(self, override\_startTime=None)
:   `Creates a timeseries containing a running total (partial sum) returns a timeseries object`

<!-- -->

[**safeinsert**]()(self, datestamp, value, quality=0)
:   `takes raw input and attempts to make it work`

<!-- -->

[**saveBinary**]()(self, path)
:   `Outputs the timeseries to a binary file`

<!-- -->

[**saveSQLITE3**]()(\*args, \*\*kwargs)
:   `saves a timeseries from to SQLITE3 database Reads a time series from the database# conn - SQLITE3 connection tsid - string LOC_PARAM replace_table = False - Set to true to replace the ts in the database`

<!-- -->

[**saveTSV**]()(self, path)
:   `Outputs the timeseries to a tab separated file`

<!-- -->

[**savitzky\_golay**]()(\*args, \*\*kwargs)
:   `Savitzky-Golay Smoothing filter using numpy window_size: number of items in window integer order: polynomial order deriv: defaults to 0 rate : defaults to 1`

<!-- -->

[**simpledelta**]()(self)
:   `calculates the delta between successive, results are in the same units as the time series returns a timeseries object`

<!-- -->

[**snap**]()(self, interval, buffer, starttime=None)
:   `Snaps a timeseries  interval: interval at which time series is snapped buffer : lookahead and lookback returns a snapped timeseries`

<!-- -->

[**stddev**]()(self)
:   `returns the standard deviation of a timeseries as a timeslice`

<!-- -->

[**subSlice**]()(self, starttime, endtime)
:   `returns a timeseries betweeen the specified start and end datetimes`

<!-- -->

[**subtract**]()(self, operand)
:   `Subtracts an operand timeseries or constant from self`

<!-- -->

[**timeshift**]()(self, tdelta)
:   `Shifts each timestamp a given time interval tdelta: timedelta to shift returns a timeseries object`

[**timestamps**]()(self)

[**toBinary**]()(self)
:   `Outputs the timeseries to a binary bytearray`

<!-- -->

[**toDict**]()(self)
:   `Turns self.data into a dictionary for efficiency purposes`

<!-- -->

[**toHTML**]()(self, css='', thead='')
:   `like __str__ only it outputs a HTML table`

<!-- -->

[**toJS**]()(self, var, timefmt='%m/%d/%Y %k:%M:%S')
:   `returns self as a JS array`

<!-- -->

[**toJSON**]()(self, timefmt='%m/%d/%Y %k:%M:%S')
:   `returns self as a JSON object`

<!-- -->

[**toPlot**]()(self)
:   `Format timeseries for plotting by returning: x: Timestamps y: Values Matplotlib Example: plt.plot(*timeseries.toPlot())`

<!-- -->

[**trendline**]()(self)
:   `trendline performs a least squares regression on self. It returns a timeseries that contains the best fit values for each timeslice`

<!-- -->

[**truncate**]()(self, precision)
:   `Truncates values in timeseries to a given number of decimal places`

[**values**]()(self)

[**variance**]()(self)
:   `returns the variance of the timeseries as a timeslice`

 \
[class **timeseries**]()

`   `

 

Methods defined here:\

[**SQLITE3connect**]()(\*args, \*\*kwargs)
:   `Get a SQLITE 3 database connection dbPath - path to the database file`

<!-- -->

[**SQLITE3disconnect**]()(\*args, \*\*kwargs)
:   `Disconnect from a SQLITE3 database connection`

<!-- -->

[**TD**]()(self, input)
:   `TD takes a relative time and turns it into a timedelta input format: 1w7d6h9m`

<!-- -->

[**\_\_eq\_\_**]()(self, other, precision=6)
:   `Checks to see if a timeseries is equal to another you can specify how many decimal places to check. default is six decimals"`

<!-- -->

[**\_\_getitem\_\_**]()(self, idx)
:   `returns (gets) a timeslice from self.data from supplied index. Example : ts[1] would return [datetime,value,quality]`

<!-- -->

[**\_\_init\_\_**]()(self, data=None)
:   `"overloaded" timeseries constructor expects data to be tuple of datetime obj, observation value (typically float), and a quality flag)`

[**\_\_len\_\_**]()(self)

[**\_\_str\_\_**]()(self)
:   `Equivalent to toString() in other languages returns a tab delineated timeseries`

<!-- -->

[**accumulate**]()(self, interval, override\_startTime=None)
:   `accumulates timeseries based on a given interval of type timedelta returns a timeseries object`

<!-- -->

[**accumulateWY**]()(self, interval, incrTS, offset=datetime.timedelta(0))
:   `accumulates input timeseries and adds to self on an interval of type timedelta this resets every wateryear self is assumed to be an accumulated timeseries  returns a timeseries object`

<!-- -->

[**add**]()(self, operand)
:   `Subtracts an operand timeseries or constant from self`

<!-- -->

[**average**]()(self, interval)
:   `averages timeseries based on a given interval of type timedelta returns a timeseries object`

<!-- -->

[**averageWY**]()(self)
:   `averages each element in the timeseries in previous water years returns a timeseries object`

<!-- -->

[**centerMovingAverage**]()(self, interval)
:   `averages timeseries based on a given interval of type timedelta  returns a timeseries object containing center moving average`

<!-- -->

[**cull**]()(self, op, operand)
:   `culls data from self op: lambda function to perform eg lambda x,y: x>y operand: could be a timeseries or a float returns a timeseries object`

[**cullvalues**]()(self, value)

[**cut**]()(self, other)
:   `cuts a timeseries from self where datetimes intersect with other.  returns a timeseries object`

<!-- -->

[**diff**]()(self, other)
:   `Returns the differences between self and timeseries other governs`

<!-- -->

[**div**]()(self, operand)
:   `divides an self by an operand timeseries or constant`

<!-- -->

[**fillMissing**]()(self, interval, value, starttime=None, endtime=None)
:   `fills values in a timeseries on a specified interval if they are not present. Useful for marking missing values in timeseries returns a timeseries object`

<!-- -->

[**filldown**]()(self, interval, starttime=None, offset=None, \_endtime=None)
:   `fills timeslices in timeseries from the previous value until a new value is detected if start time is specified, It will fill with zeroes on the interval until a value is found if a timezone offset is passed, it will fill to the offset returns a timeseries object`

<!-- -->

[**findClosestIndex**]()(self, key)
:   `returns the index of a given timestamp returns closest index if not found`

<!-- -->

[**findIndex**]()(self, key)
:   `returns the index of a given timestamp returns -1 if not found`

<!-- -->

[**findValue**]()(self, timestamp)
:   `returns a value at a given timestamp returns None type if not found`

[**firstdifference**]()(self)

[**fromBinary**]()(self, buf)
:   `Reads the timeseries from a binary buffer`

<!-- -->

[**fromTSV**]()(self, lines)
:   `reads a timeseries from a TSV string  This method mutates the object, and also returns a pointer to self.`

<!-- -->

[**getStatus**]()(self)
:   `exceptions get dropped into self.status This method gets status message of object and resets self.status to "OK"`

<!-- -->

[**getWY**]()(self, WY)
:   `Gets a water year`

<!-- -->

[**globalAverage**]()(self)
:   `averages entire timeseries returns a timeslice`

<!-- -->

[**globalMax**]()(self)
:   `finds the max of a timeseries returns a timeslice`

<!-- -->

[**globalMin**]()(self)
:   `averages minimum of a timeseries returns a timeslice`

<!-- -->

[**insert**]()(self, datestamp, value, quality=0)
:   `Inserts a timestamp, value and quality into the timseries. this module assumes that datetimes are in acending order, as such please use this method when adding data`

<!-- -->

[**interpolate**]()(self, interval)
:   `interpolates timeseries based on a given interval of type timedelta returns a timeseries object`

<!-- -->

[**interpolateValue**]()(self, x0, y0, x1, y1, x)
:   `interpolate values`

<!-- -->

[**linreg**]()(self)
:   `returns a tuple of linear regression cooeficinets (m,b,r) for a line defined as y = mx+b m - slope b - slope intercept r - correlation coeeficient NOTE: x is in seconds past the epoch`

<!-- -->

[**loadBinary**]()(self, path)
:   `Reads the timeseries from a binary file and inserts values into self`

<!-- -->

[**loadSQLITE3**]()(\*args, \*\*kwargs)
:   `loads a timeseries from a SQLITE3 database Reads a time series from the database# conn - SQLITE3 connection tsid - string LOC_PARAM start_time - datetime end_time - datetime`

<!-- -->

[**loadTSV**]()(self, path)
:   `Reads a timeseries from a tsv file. Hash (#) can be used as comments Format <Datetime>        <value> <quality> if quality is not present,  will defualt to 0 This method mutates the object, and also returns a pointer to self.`

<!-- -->

[**maxmin**]()(self, interval, cmp)
:   `returns a max or a min based for a given interval of type datetime returns a timeseries object`

<!-- -->

[**merge**]()(self, other)
:   `Merges another timeseries into self, retruns resultant timeseries`

[**minDate**]()(self, timefmt='%m/%d/%Y %k:%M:%S')

[**movingaverage**]()(self, interval)
:   `averages timeseries based on a given interval of type timedelta. This differs from rollingaverage because it looks backwards.  returns a timeseries object`

<!-- -->

[**movingstddev**]()(self, interval)
:   `Returns a moving standard deviaton over specified interval.   returns a timeseries object`

<!-- -->

[**mul**]()(self, operand)
:   `multiplies an operand timeseries or constant to self`

<!-- -->

[**operation**]()(self, op, operand)
:   `Performs an operation on self op: lambda function to perform eg lambda x,y: x+y operand: could be a timeseries or a float returns a timeseries object`

[**parseTimedelta**]()(self, input)

[**percent**]()(self, denom)
:   `Calculates the percentage of two timeseries numerator : self denominator : denom returns a timeseries object of percentages`

<!-- -->

[**remove\_stddev\_outliers**]()(\*args, \*\*kwargs)
:   `Remove Outliers using Standard Deviation`

<!-- -->

[**rollingaverage**]()(self, interval)
:   `averages timeseries based on a given interval of type timedelta. Moving average looking forward.  returns a timeseries object`

<!-- -->

[**round**]()(self, precision)
:   `Rounds values in timeseries to a given number of decimal places`

<!-- -->

[**runningTotal**]()(self, override\_startTime=None)
:   `Creates a timeseries containing a running total (partial sum) returns a timeseries object`

<!-- -->

[**safeinsert**]()(self, datestamp, value, quality=0)
:   `takes raw input and attempts to make it work`

<!-- -->

[**saveBinary**]()(self, path)
:   `Outputs the timeseries to a binary file`

<!-- -->

[**saveSQLITE3**]()(\*args, \*\*kwargs)
:   `saves a timeseries from to SQLITE3 database Reads a time series from the database# conn - SQLITE3 connection tsid - string LOC_PARAM replace_table = False - Set to true to replace the ts in the database`

<!-- -->

[**saveTSV**]()(self, path)
:   `Outputs the timeseries to a tab separated file`

<!-- -->

[**savitzky\_golay**]()(\*args, \*\*kwargs)
:   `Savitzky-Golay Smoothing filter using numpy window_size: number of items in window integer order: polynomial order deriv: defaults to 0 rate : defaults to 1`

<!-- -->

[**simpledelta**]()(self)
:   `calculates the delta between successive, results are in the same units as the time series returns a timeseries object`

<!-- -->

[**snap**]()(self, interval, buffer, starttime=None)
:   `Snaps a timeseries  interval: interval at which time series is snapped buffer : lookahead and lookback returns a snapped timeseries`

<!-- -->

[**stddev**]()(self)
:   `returns the standard deviation of a timeseries as a timeslice`

<!-- -->

[**subSlice**]()(self, starttime, endtime)
:   `returns a timeseries betweeen the specified start and end datetimes`

<!-- -->

[**subtract**]()(self, operand)
:   `Subtracts an operand timeseries or constant from self`

<!-- -->

[**timeshift**]()(self, tdelta)
:   `Shifts each timestamp a given time interval tdelta: timedelta to shift returns a timeseries object`

[**timestamps**]()(self)

[**toBinary**]()(self)
:   `Outputs the timeseries to a binary bytearray`

<!-- -->

[**toDict**]()(self)
:   `Turns self.data into a dictionary for efficiency purposes`

<!-- -->

[**toHTML**]()(self, css='', thead='')
:   `like __str__ only it outputs a HTML table`

<!-- -->

[**toJS**]()(self, var, timefmt='%m/%d/%Y %k:%M:%S')
:   `returns self as a JS array`

<!-- -->

[**toJSON**]()(self, timefmt='%m/%d/%Y %k:%M:%S')
:   `returns self as a JSON object`

<!-- -->

[**toPlot**]()(self)
:   `Format timeseries for plotting by returning: x: Timestamps y: Values Matplotlib Example: plt.plot(*timeseries.toPlot())`

<!-- -->

[**trendline**]()(self)
:   `trendline performs a least squares regression on self. It returns a timeseries that contains the best fit values for each timeslice`

<!-- -->

[**truncate**]()(self, precision)
:   `Truncates values in timeseries to a given number of decimal places`

[**values**]()(self)

[**variance**]()(self)
:   `returns the variance of the timeseries as a timeslice`

 \
**Functions**

`      `

 

[**requires\_SQLITE3**]()(f)

[**requires\_heclib**]()(f)

[**requires\_numpy**]()(f)
:   `Initial stab at the requires_numpy function - raises a warning`


