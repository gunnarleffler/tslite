#!/usr/bin/env python
import datetime,sys,os,io
import tslite, json, zlib
import dateutil.parser

def result (text,cond):
  if cond == True:
    print " %s ... %sOK%s" % (text,bcolors.OKGREEN,bcolors.ENDC)
  else:
    print " %s ... %sFAIL!%s" % (text,bcolors.FAIL,bcolors.ENDC)

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#Begin tslite tests
print ("Testing tslite")
t = tslite.timeseries().loadBinary("test/test.dat")
result ("Load Binary Data",(len(t.data) > 0))

t.saveBinary("test/test2.dat")
result ("Save Binary Data",t.status == "OK")

print " compressing timeseries of length %d..." % (len(t))
b = t.toBinary()
z = zlib.compress(buffer(b),9)
print " %d bytes, %d bytes compressed" % (len(b),len(z))
b = zlib.decompress(z)
probe = tslite.timeseries().fromBinary(b)
print " decompressed %d lines" % (len(probe))
result ("Binary compression in memory", t == probe)

conn = tslite.timeseries().SQLITE3connect("test/test.db") 
result ("SQLITE3 connection", conn != None)

#t.saveSQLITE3 (conn,"saveSQLITE3")
result ("Save to SQLITE3 database", t.status == "OK")

probe = tslite.timeseries().loadSQLITE3(conn,"saveSQLITE3")
result ("Load from SQLITE3 database", t == probe)

t2 = t.snap("1d","6h")
probe = tslite.timeseries().loadSQLITE3(conn,"snap")
result ("snap",probe==t2)

t2 = t.snap(t.TD("1d"),t.TD("6h"),starttime=datetime.datetime(year=2014,month=1,day=5))
#t2.saveSQLITE3(conn,"hardsnap", replace_table = True)
probe = tslite.timeseries().loadSQLITE3(conn,"hardsnap")
result ("hardsnap",probe==t2)

result("variance",probe.variance() == [datetime.datetime(2014, 2, 6, 0, 0), 1393.0345078122862, 0])

result("standard deviation", 
 probe.stddev()==[datetime.datetime(2014, 2, 6, 0, 0), 37.32337749738475, 0])

result ("linear regression coefficients",
 t2.linreg()==(-2.7476210178105947e-05, 39016.59750278894, -0.5874889488864309))

probe = tslite.timeseries().loadSQLITE3(conn,"trendline")
result ("linear regression trendline", t2.trendline() == probe)

t3 = t2.cull(lambda x,y: x>y,800.0)
probe=tslite.timeseries().loadTSV("test/cull.tsv")
result ("cull", t3.__eq__(probe, precision = 2))

r = t2.centerMovingAverage(t.TD("5d"))
t3 = t2.cull(lambda x,y: x>y,r)
probe=tslite.timeseries().loadTSV("test/TScull.tsv")
result ("TS cull", t3.__eq__(probe, precision = 2))

t1 = t2.cut(t3)
result ("cut", t1.__eq__(probe, precision = 2))

t1 = t.movingstddev("1d")
probe=tslite.timeseries().loadTSV("test/movingSTDDEV.tsv")
result ("Moving Standard Deviation", t1.__eq__(probe, precision = 2))

probe = open("test/test.json","r").read()
result ("toJSON", t1.toJSON() == probe);
#t1.saveTSV("test/round.tsv")
probe=tslite.timeseries().loadTSV("test/round.tsv")
result ("round", t1.round(2) == probe);

probe=tslite.timeseries().loadTSV("test/truncate.tsv")
result ("truncate", t1.truncate(2) == probe);


