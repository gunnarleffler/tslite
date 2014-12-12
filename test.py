#!/usr/bin/env python
import datetime,sys,os
import tslite
import dateutil.parser

def result (text,cond):
  if cond == True:
    print (text + " ... OK")
  else:
    print (text + " ... FAIL")

#Begin tslite tests
print ("Testing tslite")
t = tslite.timeseries().loadBinary("test/test.dat")
result ("Load Binary Data",(len(t.data) > 0))
t.saveBinary("test/test2.dat")
result ("Save Binary Data",t.status == "OK")
conn = tslite.timeseries().SQLITE3connect("test/test.db") 
result ("SQLITE3 connection", conn != None)
#t.saveSQLITE3 (conn,"saveSQLITE3")
result ("Save to SQLITE3 database", t.status == "OK")
probe = tslite.timeseries().loadSQLITE3(conn,"saveSQLITE3")
result ("Load from SQLITE3 database", t == probe)
t2 = t.snap(t.TD("1d"),t.TD("12h"))
probe = tslite.timeseries().loadSQLITE3(conn,"snap")
result ("snap",probe==t2)
t2 = t.snap2(t.TD("1d"),t.TD("6h"))
result ("snap2",probe==t2)
t2 = t.snap(t.TD("1d"),t.TD("6h"),starttime=datetime.datetime(year=2014,month=1,day=5))
t2.saveSQLITE3(conn,"hardsnap")
probe = tslite.timeseries().loadSQLITE3(conn,"hardsnap")
result ("hardsnap",probe==t2)
print "variance ... "
print probe.variance()
print "standard deviation ... "
print probe.stddev()
print "linear regression ... "
print t2.linreg()
print t2.trendline()
