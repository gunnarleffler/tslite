#!/usr/local/bin/python
''' tslite - Light and portable time series library
v2.0.0
22 April 2022
Author: Gunnar Leffler
'''

import sys, os, time, datetime, struct, math, re, json
import dateutil.parser as dateparser
from functools import wraps

##Load optional libraries
try:
  import numpy as np
  from math import factorial  ## Factorial not in Jython 2.5.x math module
except:
  _NUMPY_AVAILABLE = False
else:
  _NUMPY_AVAILABLE = True

try:
  import sqlite3
except:
  _SQLITE3_AVAILABLE = False
else:
  _SQLITE3_AVAILABLE = True


def requires_numpy(f):
  """ Initial stab at the requires_numpy function - raises a warning """
  @wraps(f)
  def wrapper(*args, **kwargs):
    if _NUMPY_AVAILABLE:
      return f(*args, **kwargs)
    else:
      raise Warning("Numpy not available.  Cannot call %s" % f.__name__)
      return f(*args, **kwargs)

  return wrapper


def requires_SQLITE3(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    if _SQLITE3_AVAILABLE:
      return f(*args, **kwargs)
    else:
      raise Warning("SQLITE3 not availible  Cannot call %s" % f.__name__)
      return f(*args, **kwargs)

  return wrapper


def requires_heclib(f):
  @wraps(f)
  def wrapper(*args, **kwargs):
    if _HECLIB_AVAILABLE:
      return f(*args, **kwargs)
    else:
      raise Warning("HEC/Jython not available.  Cannot call %s" % f.__name__)
      return f(*args, **kwargs)

  return wrapper


class timeseries:

  def __init__(self, data=None):
    '''"overloaded" timeseries constructor
        expects data to be tuple of (datetime obj, observation value)
    '''
    self.status = "OK"
    #Data is a nested list with the following structure [datetime, float value,``]
    self.data = []
    self.decimals = 3
    if data != None:
      #set internal data member to data and filter out blanks
      for row in data:
        if len(row) > 1:
          if row[1] != None:
            self.safeinsert(row[0], row[1])

  #========================================================================
  # IO and data manipulation methods
  #========================================================================

  def __str__(self):
    '''Equivalent to toString() in other languages
     returns a tab delineated timeseries'''
    output = ""
    template = "%s\t%.3f\n"
    for line in self.data:
      try:
        output += template % (line[0].strftime("%d-%b-%Y %H%M"), line[1])
      except:
        output += "%s\t\t\n" % line[0].strftime("%d-%b-%Y %H%M")
    return output

  def __getitem__(self, idx):
    ''' returns (gets) a timeslice from self.data from supplied index.
        Example : ts[1] would return [datetime,value]'''
    if idx >= len(self.data):
      return [None, None]
    return self.data[idx]

  def __len__(self):
    return (len(self.data))

  def __eq__(self, other, precision=6):
    '''Checks to see if a timeseries is equal to another
       you can specify how many decimal places to check.
       default is six decimals"
    '''
    fmt = '.' + str(precision) + 'f'
    if other == None:
      return False
    if len(self.data) == 0 and len(other.data) == 0:
      return True
    if len(self.data) != len(other.data):
      return False
    for i in range(len(self.data)):
      if format(self.data[i][1], fmt) != format(other.data[i][1], fmt):
        return False
    return True

  def toDict(self):
    '''Turns self.data into a dictionary for efficiency purposes'''
    output = {}
    for i in range(len(self.data)):
      output[self.data[i][0]] = i
    return output

  def timestamps(self):
    output = []
    for i in range(len(self.data)):
      output.append(self.data[i][0])
    return output

  def values(self):
    output = []
    for i in range(len(self.data)):
      output.append(self.data[i][1])
    return output

  def toPlot(self):
    '''Format timeseries for plotting by returning:
       x: Timestamps
       y: Values
       Matplotlib Example: plt.plot(*timeseries.toPlot())
    '''
    return self.timestamps(), list(self.values())

  def saveTSV(self, path):
    '''Outputs the timeseries to a tab separated file'''
    f = open(path, "w")
    f.write(str(self))
    f.close()

  def loadTSV(self, path):
    '''Reads a timeseries from a tsv file. Hash (#) can be used as comments
       Format <Datetime>\t<value>
       This method mutates the object, and also returns a pointer to self.
    '''
    lines = (line.rstrip("\n") for line in open(path, "r"))
    return self.fromTSV(lines)

  def fromTSV(self, lines):
    '''reads a timeseries from a TSV string 
       This method mutates the object, and also returns a pointer to self.
    '''
    count = 0
    for s in lines:
      count += 1
      s = re.sub(r'#.*', '', s)  # Strip comments
      if re.match(r'\S', s):  # Ignore blank lines
        tokens = s.split("\t")
        try:
          if len(tokens) > 1:
            self.safeinsert(tokens[0], float(tokens[1]))
        except:
          self.status = "Error Parsing line %u" % (count)
    return self

  def saveBinary(self, path):
    '''Outputs the timeseries to a binary file'''
    f = open(path, "wb")
    f.write(self.toBinary())
    f.close()

  def toBinary(self):
    '''Outputs the timeseries to a binary bytearray
       Uses doubles for time and 
    '''
    o = bytearray()
    for line in self.data:
      a, b = (time.mktime(line[0].timetuple()), line[1])
      o.extend(struct.pack("dd", a, b))
    return o

  def loadBinary(self, path):
    '''Reads the timeseries from a binary file and inserts values into self'''
    buf = bytearray(os.path.getsize(path))
    with open(path, "rb") as f:
      f.readinto(buf)
      self.fromBinary(buf)
    f.close()
    return self

  def fromBinary(self, buf):
    '''Reads the timeseries from a binary buffer'''
    size = struct.calcsize("dd")
    buflen = len(buf)
    if buflen >= size:
      i = 0
      while i < buflen:
        d = struct.unpack("dd", buf[i:i + size])
        self.insert(datetime.datetime.fromtimestamp(d[0]), d[1])
        i += size
    return self

  def loadBinaryV1(self, path):
    '''Reads the timeseries from a binary file and inserts values into self'''
    buf = bytearray(os.path.getsize(path))
    with open(path, "rb") as f:
      f.readinto(buf)
      self.fromBinaryV1(buf)
    f.close()
    return self

  def fromBinaryV1(self, buf):
    '''Reads the timeseries from a binary buffer'''
    size = struct.calcsize("iff")
    buflen = len(buf)
    if buflen >= size:
      i = 0
      while i < buflen:
        d = struct.unpack("iff", buf[i:i + size])
        self.insert(datetime.datetime.fromtimestamp(d[0]), d[1])
        i += size
    return self


  @requires_SQLITE3
  def SQLITE3connect(self, dbPath):
    '''
    Get a SQLITE 3 database connection
    dbPath - path to the database file  
    '''
    #initialize with Default Configuration
    self.status = "OK"
    #Database Cursors
    dbconn = None
    try:
      dbconn = sqlite3.connect(dbPath)
      if not dbconn:
        self.status = f"\nCould not connect to {dbPath}\n"
    except Exception as e:
      self.status = f"\nCould not connect to {dbPath}\n {str (e)}"
    return dbconn

  @requires_SQLITE3
  def SQLITE3disconnect(self, dbconn):
    '''Disconnect from a SQLITE3 database connection '''
    dbconn.close()

  @requires_SQLITE3
  def loadSQLITE3(self, conn, tsid, start_time=None, end_time=None):
    '''loads a timeseries from a SQLITE3 database
    Reads a time series from the database#
    conn - SQLITE3 connection
    tsid - string LOC_PARAM
    start_time - datetime
    end_time - datetime
    Timestamps are stored in milliseconds after the unix epoch
    '''
    cur = conn.cursor()
    ts = timeseries()
    sqltxt = "SELECT * FROM " + tsid
    if start_time != None and end_time != None:
      start = time.mktime(start_time.timetuple()*1000)
      end = time.mktime(end_time.timetuple()*1000)
      sqltxt += " WHERE timestamp >= " + str(
          start) + " AND timestamp <= " + str(end)
    try:
      cur.execute(sqltxt)
      rows = cur.fetchall()
      for d in rows:
        ts.insert(datetime.datetime.fromtimestamp(d[0]/1000), d[1])
    except Exception as e:
      self.status = "\nCould not read %s\n" % tsid
      self.status += "\n%s" + str(e)
    cur.close()
    return ts

  @requires_SQLITE3
  def loadSQLITE3v1(self, conn, tsid, start_time=None, end_time=None):
    '''loads a timeseries from a SQLITE3 database from version 1 tables
    Reads a time series from the database#
    conn - SQLITE3 connection
    tsid - string LOC_PARAM
    start_time - datetime
    end_time - datetime
    in v1 Timestamps are stored in seconds after the unix epoch
    '''
    cur = conn.cursor()
    ts = timeseries()
    sqltxt = "SELECT * FROM " + tsid
    if start_time != None and end_time != None:
      start = time.mktime(start_time.timetuple())
      end = time.mktime(end_time.timetuple())
      sqltxt += " WHERE timestamp >= " + str(
          start) + " AND timestamp <= " + str(end)
    try:
      cur.execute(sqltxt)
      rows = cur.fetchall()
      for d in rows:
        ts.insert(datetime.datetime.fromtimestamp(d[0]), d[1])
    except Exception as e:
      self.status = "\nCould not read %s\n" % tsid
      self.status += "\n%s" + str(e)
    cur.close()
    return ts


  @requires_SQLITE3
  def saveSQLITE3(self, conn, tsid, replace_table=False):
    '''saves a timeseries from to SQLITE3 database
    Reads a time series from the database#
    conn - SQLITE3 connection
    tsid - string LOC_PARAM
    replace_table = False - Set to true to replace the ts in the database
    Timestamps are stored in milliseconds after the unix epoch
    '''
    tsid = tsid.upper()
    try:
      cur = conn.cursor()
      if replace_table == True:
        cur.execute("CREATE TABLE IF NOT EXISTS {}(timestamp INTEGER PRIMARY KEY, val REAL)".format(tsid))
        cur.execute("DROP TABLE {}".format(tsid))
      cur.execute("CREATE TABLE IF NOT EXISTS {}(timestamp INTEGER PRIMARY KEY, val REAL)".format(tsid))
      for line in self.data:
        sqltxt = "INSERT OR REPLACE INTO {} VALUES(?, ?)".format(tsid)
        cur.execute(sqltxt,(int(time.mktime(line[0].timetuple()) * 1000), line[1]))
      conn.commit()
      cur.close()
    except Exception as e:
      self.status = "\nCould not store " + tsid
      self.status += "\n%s" % str(e)

  def getStatus(self):
    '''exceptions get dropped into self.status
       This method gets status message of object and resets self.status to "OK" '''
    s = self.status
    self.status = "OK"
    return s

  def findValue(self, timestamp):
    '''  returns a value at a given timestamp
    returns None type if not found'''
    idx = self.findIndex(timestamp)
    if idx != -1:
      return self.data[idx][1]
    else:
      return None

  def findIndex(self, key):
    '''  returns the index of a given timestamp
    returns -1 if not found'''
    imin = 0
    imax = len(self.data) - 1
    while (imax >= imin):
      imid = imin + ((imax - imin) // 2)
      if (self.data[imid][0] == key):
        return imid
      elif (self.data[imid][0] < key):
        imin = imid + 1  #change min index to search upper subarray
      else:
        imax = imid - 1
        #change max index to search lower subarray
    return -1  # Key not found

  def findClosestIndex(self, key):
    '''  returns the index of a given timestamp
    returns closest index if not found'''
    imin = 0
    imax = len(self.data) - 1
    while (imax >= imin):
      imid = imin + ((imax - imin) // 2)
      if (self.data[imid][0] == key):
        return imid
      elif (self.data[imid][0] < key):
        imin = imid + 1  #change min index to search upper subarray
      else:
        imax = imid - 1
        #change max index to search lower subarray
    return imid  # Key not found

  def safeinsert(self, datestamp, value):
    '''takes raw input and attempts to make it work'''
    if isinstance(datestamp, str):
      datestamp = dateparser.parse(datestamp, fuzzy=True)
    self.insert(datestamp, float(value))

  def insert(self, datestamp, value, quality=0):
    '''Inserts a timestamp, value into the timseries.
       this module assumes that datetimes are in acending order, as such please use this method when adding data'''
    l = len(self.data)
    if l == 0:
      self.data.append([datestamp, value])
      return
    if datestamp > self.data[-1][0]:
      self.data.append([datestamp, value])
      return
    i = self.findClosestIndex(datestamp)
    if datestamp == self.data[i][0]:
      self.data[i] = [datestamp, value]
      return
    i -= 2
    if i < 0:
      i = 0
    while i < l:
      if datestamp < self.data[i][0]:
        self.data.insert(i, [datestamp, value])
        return
      i += 1
    self.data.append([datestamp, value])

  def truncate(self, precision):
    '''Truncates values in timeseries to a given number of decimal places
    '''
    fmt = f'.{str(precision)}f'
    output = timeseries()
    for slice in self.data:
      output.insert(slice[0], float(format(slice[1], fmt)))
    return output

  def round(self, precision):
    '''Rounds values in timeseries to a given number of decimal places
    '''
    output = timeseries()
    for slice in self.data:
      output.insert(slice[0], round(slice[1], precision))
    return output

  def merge(self, other):
    '''Merges another timeseries into self, retruns resultant timeseries'''
    output = timeseries(self.data)
    for line in other.data:
      output.insert(line[0], line[1])
    return output

  def diff(self, other):
    '''Returns the differences between self and timeseries other governs'''
    output = timeseries()
    for slice in self.data:
      i = other.findIndex(slice[0])
      if i == -1:
        continue
      oslice = other.data[i]
      if format(slice[1], '.6f') != format(oslice[1], '.6f'):
        output.insert(oslice[0], oslice[1])
    for slice in other.data:
      i = self.findIndex(slice[0])
      if i == -1:
        output.insert(slice[0], slice[1])
    return output

  def toHTML(self, css="", thead=""):
    '''like __str__ only it outputs a HTML table'''
    output = "<table " + css + ">"
    output += thead
    for line in self.data:
      try:
        output += "<tr><td>%s</td><td>&nbsp;&nbsp;%.2f</td></tr>" % (
            line[0].strftime("%d-%b-%Y %H%M"), line[1])
      except:
        output += "<tr><td>%s</td><td> </td></tr>" % line[0].strftime(
            "%d-%b-%Y %H%M")
    return output + "</table>"

  def toJS(self, var, timefmt="%m/%d/%Y %k:%M:%S"):
    '''returns self as a JS array'''
    return "var %s = %s;\n" % (var, self.toJSON(timefmt=timefmt))

  def toJSON(self, timefmt="%m/%d/%Y %k:%M:%S"):
    '''returns self as a JSON object'''
    output = []
    for line in self.data:
      try:
        output.append('  ["%s",%.2f]' % (line[0].strftime(timefmt), line[1]))
      except:
        output.append('  ["%s", undefined]' % line[0].strftime(timefmt))
    return "[\n%s\n]" % ",\n".join(output)

  def fromJSON(self,s):
    ts = timeseries()
    try:
      j = json.loads(s)
      ts = timeseries(j)
    except Exception as e:
      self.status = str(e)
    return ts

  def minDate(self, timefmt="%m/%d/%Y %k:%M:%S"):
    try:
      return self.data[0][0].strftime(timefmt)
    except:
      return ""

  #========================================================================
  # computational methods
  #========================================================================

  def interpolateValue(self, x0, y0, x1, y1, x):
    '''interpolate values'''
    m = (y1 - y0) / (x1 - x0)
    output = y0 + (x - x0) * m
    return output

  def interpolate(self, interval):
    '''interpolates timeseries based on a given interval of type timedelta
    returns a timeseries object
    '''
    interval = self.TD(interval)
    _data = []
    try:
      for i in range(0, len(self.data) - 1):
        startTime = self.data[i][0]
        deltaT = (self.data[i + 1][0] - startTime)
        steps = int(deltaT.total_seconds() / interval.total_seconds())
        
        for j in range(0, steps):
          value = self.interpolateValue(0, self.data[i][1],
                                        deltaT.total_seconds(),
                                        self.data[i + 1][1],
                                        j * interval.total_seconds())
          _data.append([startTime + (interval * j), value])
    except Exception as e:
      self.status = str(e)
    return timeseries(_data)

  def average(self, interval):
    '''averages timeseries based on a given interval of type timedelta
       returns a timeseries object
    '''
    interval = self.TD(interval)
    _data = []
    if self.data == []:
      return timeseries()
    try:
      i = 0
      count = len(self.data)
      endTime = self.data[i][0]
      while i < count:
        startTime = endTime
        endTime = startTime + interval
        n = 0
        sum = 0
        while self.data[i][0] < endTime:
          sum += self.data[i][1]
          n += 1
          i += 1
          if i >= count:
            break
        if n != 0:
          _data.append([endTime, sum / n])
    except Exception as e:
      self.status = str(e)
    return timeseries(_data)

  def globalAverage(self):
    '''averages entire timeseries returns a timeslice'''
    if len(self.data) != 0:
      interval = self.data[-1][0] - self.data[0][0]
      return self.average(interval).data[0]
    return None

  def globalMax(self):
    '''finds the max of a timeseries returns a timeslice'''
    if len(self.data) != 0:
      interval = self.data[-1][0] - self.data[0][0]
      return self.maxmin(interval, lambda x, y: x > y).data[0]
    return None

  def globalMin(self):
    '''averages minimum of a timeseries returns a timeslice'''
    if len(self.data) != 0:
      interval = self.data[-1][0] - self.data[0][0]
      return self.maxmin(interval, lambda x, y: x < y).data[0]
    return None

  def linreg(self):
    ''' returns a tuple of linear regression cooeficinets (m,b,r)
        for a line defined as y = mx+b
        m - slope
        b - slope intercept
        r - correlation coeeficient
        NOTE: x is in seconds past the epoch
    '''
    sumx = 0.0  #sum of x
    sumx2 = 0.0  #sum of x**2
    sumxy = 0.0  #sum of x * y
    sumy = 0.0  #sum of y
    sumy2 = 0.0  #sum of y**2
    n = 0
    for tmslice in self.data:
      if tmslice[1] != None:
        x = time.mktime(tmslice[0].timetuple())
        y = tmslice[1]
        sumx += x
        sumx2 += x**2
        sumxy += x * y
        sumy += y
        sumy2 += y**2
        n += 1
    denom = (n * sumx2 - (sumx**2))
    if (denom == 0):  # singular matrix. can't solve the problem.
      return (0, 0, 0)
    m = (n * sumxy - sumx * sumy) / denom
    b = (sumy * sumx2 - sumx * sumxy) / denom
    #compute correlation coeff     
    r = (sumxy - sumx * sumy / n) / math.sqrt(
        (sumx2 - (sumx**2) / n) * (sumy2 - (sumy**2) / n))
    return (m, b, r)

  def trendline(self):
    '''trendline performs a least squares regression on self. 
      Return a timeseries that contains the best fit values for each timeslice '''
    output = timeseries()
    coeff = self.linreg()
    m = coeff[0]
    b = coeff[1]
    for slice in self.data:
      x = time.mktime(slice[0].timetuple())
      output.insert(slice[0], m * x + b)
    return output

  def variance(self):
    '''returns the variance of the timeseries as a timeslice'''
    ss = 0
    mu = self.globalAverage()
    if mu != None:
      n = 0
      for t in self.data:
        n += 1
        ss += math.pow(t[1] - mu[1], 2)
      return [mu[0], ss / n, 0]
    return None

  def stddev(self):
    '''returns the standard deviation of a timeseries as a timeslice'''
    s = self.variance()
    if s != None:
      s[1] = math.sqrt(s[1])
    return s

  def movingstddev(self, interval):
    '''Returns a moving standard deviaton over specified interval.  
       returns a timeseries object'''
    output = timeseries()
    interval = self.TD(interval)
    if self.data != [] and interval.total_seconds != 0:
      pointer = self.data[0][0]
      while pointer < self.data[-1][0]:
        stddev = self.subSlice(pointer, pointer + interval).stddev()
        output.data.append(stddev)
        pointer += interval
    return output

  def subSlice(self, starttime, endtime):
    '''returns a timeseries betweeen the specified start and end datetimes'''
    output = timeseries()
    if self.data == []:
      return output
    if 1 == 1:
      pos = self.findClosestIndex(starttime)
      a = pos - 2  #subtract a few to be sure
      if a < 0:
        a = 0
      while a < len(self.data):
        line = self.data[a]
        if line[0] > endtime:
          break
        if line[0] >= starttime:
          output.insert(line[0], line[1])
        a += 1
    return output

  def getWY(self, WY):
    '''Gets a water year'''
    starttime = datetime.datetime(year=WY - 1, month=10, day=1)
    endtime = datetime.datetime(year=WY, month=9, day=30)
    return self.subSlice(starttime, endtime)

  def averageWY(self):
    '''averages each element in the timeseries in previous water years
    returns a timeseries object
    '''

    def toWY(t):
      output = t.year
      if t.month > 9:
        output += 1
      return output

    def fromWY(year, month):
      output = year
      if month > 9:
        output -= 1
      return output

    def inWY(WY, t):
      if t.month < 10 and WY == t.year:
        return True
      if t.month > 9 and WY == (t.year + 1):
        return True
      return False

    _data = []
    if self.data == []:
      return timeseries()
    dd = self.toDict()
    try:
      i = 0
      startWY = toWY(self.data[0][0])
      endWY = toWY(self.data[-1][0])
      count = len(self.data)
      #advance to the latest WY      
      while i < count and not inWY(endWY, self.data[i][0]):
        i += 1
      #average current timeslice
      while i < count:
        sum = 0
        t = self.data[i][0]
        n = 0
        for WY in range(startWY, endWY + 1):
          try:
            t2 = datetime.datetime(
                year=fromWY(WY, t.month),
                month=t.month,
                day=t.day,
                hour=t.hour,
                minute=t.minute)
            if t2 in dd:
              val = self.data[dd[t2]][1]
              n += 1
              sum += val
          except:
            pass
        if n != 0:
          _data.append([t, sum / n])
        i += 1
    except Exception as e:
      self.status = str(e)
    return timeseries(_data)

  def runningTotal(self, override_startTime=None):
    '''Creates a timeseries containing a running total (partial sum)
     returns a timeseries object'''
    output = timeseries()
    sum = 0
    for row in self.data:
      sum += row[1]
      output.insert (row[0],sum)
    return output

  def accumulate(self, interval, override_startTime=None):
    '''accumulates timeseries based on a given interval of type timedelta
     returns a timeseries object'''
    interval = self.TD(interval)
    _data = []
    if self.data == []:
      return timeseries()
    try:
      i = 0
      count = len(self.data)
      if override_startTime != None:
        endTime = override_startTime
      else:
        endTime = self.data[i][0]
      while i < count:
        startTime = endTime
        endTime = startTime + interval
        
        n = 0
        sum = 0
        while self.data[i][0] < endTime:
          sum += self.data[i][1]
          n += 1
          i += 1
          if i >= count:
            break
        if n != 0:
          _data.append([endTime, sum])
    except Exception as e:
      self.status = str(e)
    return timeseries(_data)

  def accumulateWY(self, interval, incrTS, offset=datetime.timedelta(days=0)):
    '''
    accumulates input timeseries and adds to self on an interval of type timedelta
    this resets every wateryear
    self is assumed to be an accumulated timeseries 
    returns a timeseries object
    '''
    interval = self.TD(interval)
    lastResetYear = 0
    output = timeseries()  #output timeseries, don't want to mutate self
    if incrTS.data == []:
      return self
    if self.data == []:
      output.data = [incrTS.data[0]]
    else:
      output.data = self.data
    try:
      #advance to the first timeslice in the incremental timeseries that is
      #greater than or equal the last time in self
      i = 0
      count = len(incrTS.data)
      endTime = output.data[-1][0]
      while i < count:
        if incrTS.data[i][0] >= endTime:
          break
        i += 1
      t = timeseries()
      t.data = incrTS.data[i:]
      t = t.accumulate(interval, override_startTime=endTime)
      #loop through accumulated timeseries and accumulate timeslices onto output
      total = output.data[-1][1]
      for slice in t.data:
        if slice[0].day == 1 and slice[0].month == 10 and (
            slice[0].hour + slice[0].minute / 60.0) >= (
                (offset.seconds + interval.seconds
                ) / 3600.0) and lastResetYear != slice[0].year:
          total = 0
          lastResetYear = slice[0].year
        total += slice[1]
        output.insert(slice[0], total)
        #print "%s\t %f\t %f" %(str(slice[0]),slice[1],total)
    except Exception as e:
      self.status = str(e)
    return output.timeshift(interval * -1)

  def firstdifference(self):
    return self.simpledelta()

  def simpledelta(self):
    '''calculates the delta between successive, results are in the same units as the time series
     returns a timeseries object'''
    output = timeseries()
    if len(self.data) < 2:
      return output
    try:
      for i in range(1, len(self.data)):
        d = self.data[i][1] - self.data[i - 1][1]
        output.insert(self.data[i][0], d)
    except Exception as e:
      self.status = str(e)
    return output

  def maxmin(self, interval, cmp):
    '''returns a max or a min based for a given interval of type datetime
       returns a timeseries object
    '''
    interval = self.TD(interval)
    _data = []
    if self.data == []:
      return timeseries()
    try:
      i = 0
      count = len(self.data)
      endTime = self.data[i][0]
      while i < count:
        startTime = endTime
        endTime = startTime + interval
        n = 0
        probe = self.data[i][1]
        while self.data[i][0] < endTime:
          if cmp(self.data[i][1], probe):
            probe = self.data[i][1]
          i += 1
          if i >= count:
            break
        _data.append([endTime, probe])
    except Exception as e:
      self.status = str(e)
    return timeseries(_data)

  @requires_numpy
  def savitzky_golay(self, window_size, order, deriv=0, rate=1):
    '''Savitzky-Golay Smoothing filter using numpy
       window_size: number of items in window integer
       order: polynomial order
       deriv: defaults to 0
       rate : defaults to 1
    '''
    try:
      window_size = np.abs(np.int(window_size))
      order = np.abs(np.int(order))
    except ValueError:
      raise ValueError("SGFilter:window size and order must be of type int")

    if window_size % 2 != 1 or window_size < 1:
      raise TypeError("SGFilter:window size must be positive number")
    if window_size < order + 2:
      raise TypeError(
          "SGFilter:window size is too small for the polynomials order")

    y = []

    _data = self.data

    for x in range(0, len(_data) - 1):
      yy = _data[x][1]
      y.append(yy)

    order_range = list(range(order + 1))
    half_window = (window_size - 1) // 2

    # precompute coefficients
    b = np.mat([[k**i for i in order_range]
                for k in range(-half_window, half_window + 1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)

    # pad the signal at the extremes with values taken from the signal itself
    #firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )

    firstvals = []
    v = y[0]

    for i in range(half_window):
      firstvals.append(v)

    #lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    lastvals = []
    v = (y[len(y) - 1:])[0]

    for i in range(half_window):
      lastvals.append(v)

    y = np.concatenate((firstvals, y, lastvals))

    tsd = np.convolve(m[::-1], y, mode='same')
    # remove the appended/padded values at beginning/end of data
    tsd = tsd[(window_size - 1) / 2:len(tsd) - (window_size - 1) / 2]

    _data = []
    for x in range(0, len(self.data) - 1):
      _data.append([self.data[x][0], tsd[x], 0])

    return timeseries(_data)

  @requires_numpy
  def remove_stddev_outliers(self, threshold=1.5):
    '''Remove Outliers using Standard Deviation'''
    good = []
    _data = []
    a = []

    # get the slice of values from timeseries
    # y = np.array(self.data)
    # a = y[:,1]
    for rec in self.data:
      a.append(rec[1])

    avg = np.average(a)

    # pad the first element with average
    a = [avg] + a
    out = [None] * len(a)
    good.append(a[0])

    std = np.std(a)
    stdm = std * threshold

    for n in range(1, len(a)):
      dev = abs(a[n] - good[-1])

      if dev < stdm:
        good.append(a[n])
        out[n] = a[n]
      else:
        out[n] = None

    # remove the first (avg) element
    out = out[1:]

    # replace the values, only non nulls
    # these will get interpolated later
    for x in range(0, len(self.data)):
      if out[x] != None:
        _data.append([self.data[x][0], out[x]])

    return timeseries(_data)

  def rollingaverage(self, interval):
    '''averages timeseries based on a given interval of type timedelta. Moving average looking forward. 
       returns a timeseries object'''
    interval = self.TD(interval)
    _data = []
    if self.data == []:
      return timeseries()
    try:
      i = 0
      count = len(self.data)
      while i < count:
        startTime = self.data[i][0]
        endTime = startTime + interval
        if endTime > self.data[-1][0]:
          break
        n = 0
        sum = 0
        while self.data[i + n][0] <= endTime:
          sum += self.data[i + n][1]
          n += 1
          if i + n >= count:
            break
        if n != 0:
          _data.append([endTime, sum / n])
        i += 1
    except Exception as e:
      self.status = str(e)
    return timeseries(_data)

  def movingaverage(self, interval):
    '''averages timeseries based on a given interval of type timedelta. This differs from rollingaverage because it looks backwards. 
       returns a timeseries object'''
    interval = self.TD(interval)
    _data = []
    if self.data == []:
      return timeseries()
    try:
      i = len(self.data) - 1
      while i >= 0:
        endTime = self.data[i][0]
        startTime = endTime - interval
        if startTime < self.data[0][0]:
          break
        
        n = 0
        sum = 0
        while self.data[i - n][0] >= startTime:
          sum += self.data[i - n][1]
          n += 1
          if i - n < 0:
            break
        if n != 0:
          _data.append([endTime, sum / n])
        i -= 1
    except Exception as e:
      self.status = str(e)
    return timeseries(_data)

  def centerMovingAverage(self, interval):
    '''averages timeseries based on a given interval of type timedelta 
      returns a timeseries object containing center moving average'''
    interval = self.TD(interval)
    _data = []
    if self.data == []:
      return timeseries()
    try:
      i = 0
      interval = interval
      count = len(self.data)
      while i < count:
        startTime = self.data[i][0] - interval / 2
        endTime = startTime + interval
        if startTime > self.data[-1][0]:
          break
        if startTime < self.data[0][0]:
          startTime = self.data[0][0]
        if endTime > self.data[-1][0]:
          endTime = self.data[-1][0]
        n = 0
        sum = 0
        while self.data[i + n][0] <= endTime:
          sum += self.data[i + n][1]
          n += 1
          if i + n >= count:
            break
        if n != 0:
          _data.append([self.data[i][0], sum / n])
        i += 1
    except Exception as e:
      self.status = str(e)
    return timeseries(_data)

  def percent(self, denom):
    '''Calculates the percentage of two timeseries
       numerator : self
       denominator : denom
       returns a timeseries object of percentages
    '''
    _data = []
    denom_data = {}
    try:
      #turn denominator data into a dictionary and filter out zeros (no division by 0 allowed!)
      for line in denom.data:
        if line[1] != 0:
          denom_data[line[0]] = line
      for line in self.data:
        key = line[0]
        if key in denom_data:
          _data.append([line[0], 100 * float(line[1] / denom_data[key][1])])
    except Exception as e:
      self.status = str(e)
      return timeseries()
    return timeseries(_data)

  def snap(self, interval, buffer, starttime=None):
    ''' Snaps a timeseries 
        interval: interval at which time series is snapped
        buffer : lookahead and lookback
        returns a snapped timeseries '''
    output = timeseries()
    interval = self.TD(interval)
    buffer = self.TD(buffer)
    if self.data == []:
      return output
    try:
      if buffer > interval / 2:
        buffer = interval / 2
      #setup the initial start and end  time
      endtime = self.data[-1][0]
      if starttime != None:
        t = starttime
      else:
        t = self.data[0][0]
      pos = 0
      while pos < len(self.data) and t <= endtime:
        a = pos
        curdiff = abs(self.data[a][0] - t).seconds
        while pos < len(self.data) and self.data[pos][0] <= t + buffer:
          newdiff = abs(self.data[pos][0] - t).seconds
          if (curdiff > newdiff):
            curdiff = newdiff
            a = pos
          pos += 1
        if self.data[a][0] >= t - buffer and self.data[a][0] <= t + buffer:
          output.data.append([t, self.data[a][1]])
        t += interval
    except Exception as e:
      self.status = str(e)
      return timeseries()
    return output

  def filldown(self, interval, starttime=None, offset=None, _endtime=None):
    '''fills timeslices in timeseries from the previous value until a new value is detected
       if start time is specified, It will fill with zeroes on the interval until a value is found
       if a timezone offset is passed, it will fill to the offset
       returns a timeseries object
    '''
    interval = self.TD(interval)
    ts = timeseries()
    if self.data == []:
      return ts()
    try:
      #setup the initial start time and value
      val = 0
      i = 0
      endtime = self.data[-1][0]
      if _endtime != None:
        endtime = _endtime
      if offset != None:
        if endtime.hour < offset.seconds / 3600:
          endtime = datetime.datetime(
              year=endtime.year, day=endtime.day, month=endtime.month) + offset
          #endtime += offset
        else:
          endtime = datetime.datetime(
              year=endtime.year, day=endtime.day, month=endtime.month)
          endtime += offset + datetime.timedelta(days=1)
      if starttime != None:
        t = starttime
      else:
        t = self.data[0][0]
        val = self.data[0][1]
      while t <= endtime and i < len(self.data):
        while self.data[i][0] <= t:
          val = self.data[i][1]
          i += 1
          if i == len(self.data):  #fill to the end time
            while t < endtime:
              ts.insert(t, val)
              t += interval
            break
        ts.insert(t, val)
        t += interval
    except Exception as e:
      self.status = str(e)
      return timeseries()
    return ts

  def fillMissing(self, interval, value, starttime=None, endtime=None):
    '''fills values in a timeseries on a specified interval if they are not present.
       Useful for marking missing values in timeseries
       returns a timeseries object
    '''
    interval = self.TD(interval)
    ts = timeseries()
    if self.data == [] and (starttime == None or endtime == None):
      return ts
    if starttime == None:
      t = self.data[0][0]
    else:
      t = starttime
    if endtime == None:
      endtime = self.data[-1][0]
    try:
      i = 0
      while t < endtime:
        idx = self.findIndex(t)
        if idx == -1:
          ts.insert(t, value)
        t += interval
        try:
          while self.data[i][0] <= t:
            ts.insert(self.data[i][0], self.data[i][1])
            i += 1
        except:
          pass
    except Exception as e:
      self.status = str(e)
      return timeseries()
    return ts

  def timeshift(self, tdelta):
    ''' Shifts each timestamp a given time interval
        tdelta: timedelta to shift
        returns a timeseries object '''
    _data = []
    if self.data == []:
      return timeseries()
    try:
      for line in self.data:
        _data.append([line[0] + tdelta, line[1]])
    except Exception as e:
      self.status = str(e)
      return timeseries()
    return timeseries(_data)

  def subtract(self, operand):
    '''Subtracts an operand timeseries or constant from self'''
    return self.operation(lambda x, y: x - y, operand)

  def add(self, operand):
    '''Subtracts an operand timeseries or constant from self'''
    return self.operation(lambda x, y: x + y, operand)

  def mul(self, operand):
    '''multiplies an operand timeseries or constant to self'''
    return self.operation(lambda x, y: x * y, operand)

  def div(self, operand):
    '''divides an self by an operand timeseries or constant'''
    return self.operation(lambda x, y: x / y, operand)

  def operation(self, op, operand):
    '''Performs an operation on self
       op: lambda function to perform eg lambda x,y: x+y
       operand: could be a timeseries or a float
       returns a timeseries object
    '''
    _data = []
    if self.data == []:
      return timeseries()
    try:
      if type(operand) is float or type(operand) is int:
        for line in self.data:
          _data.append([line[0], op(line[1], operand)])
      else:
        for line in self.data:
          val = operand.findValue(line[0])
          if val != None:
            _data.append([line[0], op(line[1], val)])
    except Exception as e:
      self.status = str(e)
      return timeseries()
    return timeseries(_data)


  def cull(self, op, operand):
    ''' culls data from self
        op: lambda function to perform
            example: lambda x,y: x > y 
            would return values in this timeseries that are greater than y
        operand: could be a timeseries or a float
        returns a timeseries object
    '''
    _data = []
    if self.data == []:
      return timeseries()
    try:
      if type(operand) is float or type(operand) is int:
        for line in self.data:
          if op(line[1], operand):
            _data.append(line)
      else:
        for line in self.data:
          val = operand.findValue(line[0])
          if val != None:
            if op(line[1], val):
              _data.append(line)
    except Exception as e:
      self.status = str(e)
      return timeseries()
    return timeseries(_data)

  def cullValues(self, value):
    '''
    DEPRECATED: Culls data from timeseries equal to scalar
    '''
    return self.cull(lambda x, y: x != y, float(value))

  def cullAbove(self, operand):
    '''Culls values from self above operand
       operand: accepts timeseries or a scalar
       returns a timeseries object
    '''
    return self.cull (lambda x, y: x < y,operand)

  def cullBelow(self, operand):
    '''Culls values from self below to input
       operand: accepts timeseries or a scalar
       returns a timeseries object
    '''
    return self.cull (lambda x, y: x > y,operand)

  def cullEqual(self, operand):
    '''Culls values from self that are equal to input
       operand: accepts timeseries or a scalar
       returns a timeseries object
    '''
    return self.cull (lambda x, y: x != y, operand)

  def cut(self, other):
    ''' cuts a timeseries from self where datetimes intersect with
        other. 
        returns a timeseries object
    '''
    output = timeseries()
    if self.data == []:
      return timeseries()
    try:
      for line in other.data:
        val = self.findValue(line[0])
        if val != None:
          output.insert(line[0], line[1])
    except Exception as e:
      self.status = str(e)
      return timeseries()
    return output

  #This takes a relative time and turns it into a timedelta
  #eg input 7d6h9m
  def TD(self, input):
    '''TD takes a relative time and turns it into a timedelta
    input format: 1w7d6h9m16s
    '''
    if not isinstance(input, str):
      return input
    output = datetime.timedelta(seconds=0)
    t = ""
    try:
      for c in input:
        if c == "w":
          output += datetime.timedelta(weeks=float(t))
          t = ""
        elif c == "Y":
          output += datetime.timedelta(days=float(t) * 365)
          t = ""
        elif c == "d":
          output += datetime.timedelta(days=float(t))
          t = ""
        elif c == "h":
          output += datetime.timedelta(hours=float(t))
          t = ""
        elif c == "m":
          output += datetime.timedelta(minutes=float(t))
          t = ""
        elif c == "s":
          output += datetime.timedelta(seconds=float(t))
          t = ""
        else:
          if c != " ":
            t += c
    except:
      self.status = "Could not parse" + input + " into a time interval"
    return output

  def parseTimedelta(self, input):
    return self.TD(input)


class rdb:
  #construtor rewrites a path to a RDB file
  def __init__(self, path):
    #initialize with Default Configuration
    self.status = "OK"
    #format = INDEP   SHIFT   DEP     STOR
    self.data = []
    if path:
      self.loadRDB(path)

  def __str__(self):
    output = "INDEP	SHIFT	DEP	STOR\n16N	16N	16N	1S\n"
    for line in self.data:
      output += "{}\n".format("\t".join(line))
    return output

  def loadRDB(self, path):
    self.path = path
    try:
      self.data = self.parseRDB(open(path, "r"))
    except Exception as e:
      self.status = "\n{}".format(str(e))

  def parseRDB(self, stream):
    output = []
    try:
      for line in stream:
        if (not "#" in line) and (len(line) > 1):
          output.append(line.strip().split("\t"))
    except Exception as e:
      self.status = "\n%s" % str(e)
    return output[2:]

  def saveRDB(self, path):
    open(path, "w").write(str(self))

  #interpolate values
  #This may be changed to a higher order interpolation in the future
  def interpolateValue(self, x0, y0, x1, y1, x):
    m = (y1 - y0) / (x1 - x0)
    output = y0 + (x - x0) * m
    return output

  def rate(self, indep):
    """ Rate a single value based on linear interpolation. """
    data = self.data
    index = len(data) - 2
    for i in range(len(data) - 1):
      if indep < float(data[i + 1][0]):
        index = i
        break
    return self.interpolateValue(
        float(data[index][0]),
        float(data[index][2]),
        float(data[index + 1][0]), float(data[index + 1][2]), indep)

  def reverseRate(self, indep):
    """ Reverse rate a single value based on linear interpolation
        This switches the domain and range of the RDB and rates it. 
    """
    data = self.data
    index = len(data) - 2
    for i in range(len(data) - 1):
      if indep < float(data[i + 1][2]):
        index = i
        break
    return self.interpolateValue(
        float(data[index][2]),
        float(data[index][0]),
        float(data[index + 1][2]), float(data[index + 1][0]), indep)

  rate2 = reverseRate  ## backwards compatibility

  def makeRating(self, indepTS, depTS, precision=2, factor=1):
    """ Creates a rating table based on two timeseries
        precision is for how many decimal places to consider
        factor to adjust dependent variable (kcfs->cfs, fudge factor, etc)"""
    self.data = []
    fmt = '.' + str(precision) + 'f'
    ratingMap = {}
    for t in indepTS.timestamps():
      indep = indepTS.findValue(t)
      dep = depTS.findValue(t)
      if dep != None and indep != None:
        key = float(format(indep, fmt))
        if key in ratingMap:
          ratingMap[key].append(dep * factor)
        else:
          ratingMap[key] = [dep * factor]
    keys = sorted(ratingMap.keys())
    for key in keys:
      indep = sum(ratingMap[key]) / float(len(ratingMap[key]))
      self.data.append([format(key, fmt), "0.00", format(indep, fmt), ""])

  def rateTS(self, ts):
    """ Generates a new time series with rated values from another """
    output = []
    for line in ts.data:
      output.append([line[0], self.rate(line[1])])
    return timeseries(output)

  def reverseRateTS(self, ts):
    """ Generates a new time series with reverse-rated values from another """
    output = []
    for line in ts.data:
      output.append([line[0], self.rate2(line[1])])
    return timeseries(output)

  rateTS2 = reverseRateTS  ## backwards compatibility


class tablegrid:
  #construtor rewrites a path to a RDB file
  def __init__(self, path):
    #initialize with Default Configuration
    self.status = "OK"
    self.path = None
    self.data = self.loadTable(path)

  def loadTable(self, path):
    output = []
    try:
      self.path = path
      input = open(path, "r")
      for line in input:
        if (not "#" in line) and (len(line) > 1):
          row2 = []
          if "," in line:
            row1 = line.strip().split(",")
          else:
            row1 = line.strip().split("\t")
          for n in row1:
            row2.append(
                float(n))  #Iterate and convert entries to floating point number
          output.append(row2)
    except Exception as e:
      self.status = "\n%s" % str(e)
    return output

  def tableLookup(self, arr, colval, rowval):
    #Seek the coordinates
    output = 0
    x = 0
    y = 0
    maxcols = len(arr[0]) - 1
    maxrows = len(arr) - 1
    x = maxcols - 1  #default to end of list if not found
    y = maxrows - 1
    i = 1
    while (i < maxcols):  #seeking coordinates for column values
      if arr[0][i + 1] > colval:
        x = i
        i = maxcols  #exit loop
      i += 1
    i = 1
    while (i < maxrows):  #seeking coorinate for row values
      if arr[i + 1][0] > rowval:
        y = i
        i = maxrows  #exit loop
      i += 1
    if ((x == maxcols) or (y == maxrows)):
      output = arr[y][x]
    else:
      output = self.bilinear(arr[0][x], arr[y][0], arr[0][x + 1], arr[y + 1][0],
                             arr[y][x], arr[y + 1][x], arr[y][x + 1],
                             arr[y + 1][x + 1], colval, rowval)
    return output

  def bilinear(self, x1, y1, x2, y2, fQ11, fQ12, fQ21, fQ22, x, y):
    retval = (fQ11 / ((x2 - x1) * (y2 - y1))) * (x2 - x) * (y2 - y) + (fQ21 / (
        (x2 - x1) * (y2 - y1))) * (x - x1) * (y2 - y) + (fQ12 / (
            (x2 - x1) * (y2 - y1))) * (x2 - x) * (y - y1) + (fQ22 / (
                (x2 - x1) * (y2 - y1))) * (x - x1) * (y - y1)
    return retval

  #this takes 2 timseries objects and rates them
  def rateTS(self, cols, rows):
    output = []
    for line in cols.data:
      rowval = rows.findValue(line[0])
      if rowval != None:
        output.append(
            [line[0], self.tableLookup(self.data, line[1], rowval)])
    return timeseries(output)


#Alias so we don't break backward compatibility
timeSeries = timeseries
