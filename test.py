#!/usr/bin/env python
import datetime, sys, os, io
import tslite, json, zlib, lzma
import dateutil.parser


def result(text, cond):
  if cond == True:
    print(" %s ... %sOK%s" % (text, bcolors.OKGREEN, bcolors.ENDC))
  else:
    print(" %s ... %sFAIL!%s" % (text, bcolors.FAIL, bcolors.ENDC))


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
print("Testing tslite")
#Binary IO
#----------------------------------------------------------------
t = tslite.timeseries().loadBinaryV1("test/testv1.dat")
result("Load v1 Binary Data", (len(t.data) > 0))

t.saveBinary("test/test.dat")
result("Save Binary Data", t.status == "OK")

probe = tslite.timeseries().loadBinary("test/test.dat")
result("Load Binary Data", t == probe)

print(" zlib compressing timeseries of length %d..." % (len(t)))
b = t.toBinary()
z = zlib.compress(memoryview(b), 9)
print(" %d bytes, %d bytes compressed" % (len(b), len(z)))
b = zlib.decompress(z)
probe = tslite.timeseries().fromBinary(b)
print(" decompressed %d lines" % (len(probe)))
result("zlib Binary compression in memory", t == probe)

#LZMA compression
#https://docs.python.org/3/library/lzma.html
print(" lzma compressing timeseries of length %d..." % (len(t)))
b = t.toBinary()
z = lzma.compress(b, filters = [{"id": lzma.FILTER_LZMA2, "preset": 9}])
print(" %d bytes, %d bytes compressed" % (len(b), len(z)))
b =  lzma.decompress(z)
probe = tslite.timeseries().fromBinary(b)
print(" decompressed %d lines" % (len(probe)))
result("lzma Binary compression in memory", t == probe)

with open("test/test.xz", "wb") as f:
  f.write(z)

with lzma.open("test/test.xz") as f:
  probe = tslite.timeseries().fromBinary(f.read())
result("lzma Binary compression on disk", t == probe)

#SQLITE3 IO
#----------------------------------------------------------------
conn = tslite.timeseries().SQLITE3connect("test/test.db")
result("SQLITE3 connection", conn != None)

t.saveSQLITE3 (conn,"saveSQLITE3", replace_table = True)
result("Save to SQLITE3 database", t.status == "OK")

#save a reasonable set of test data
# 6hr and daily data
#t2 = t.snap(t.TD("6h"),t.TD("3h"),starttime=datetime.datetime(year=2014, month=1, day=5))
#t2.saveSQLITE3 (conn,"test6hr", replace_table = True)
#t2 = t.snap(t.TD("1d"),t.TD("12h"),starttime=datetime.datetime(year=2014, month=1, day=5))
#t2.saveSQLITE3 (conn,"testdaily", replace_table = True)

probe = tslite.timeseries().loadSQLITE3(conn, "saveSQLITE3")
result("Load from SQLITE3 database", t == probe)

#Snap
#----------------------------------------------------------------
t2 = t.snap("1d", "6h")
probe = tslite.timeseries().loadSQLITE3 (conn, "snap")
result("snap", probe == t2)

#Hardsnap
#----------------------------------------------------------------
t2 = t.snap(t.TD("1d"),t.TD("6h"),starttime=datetime.datetime(year=2014, month=1, day=5))
#t2.saveSQLITE3 (conn,"hardsnap", replace_table = True)
probe = tslite.timeseries().loadSQLITE3(conn, "hardsnap")
result("hardsnap", probe == t2)

#Variance
#----------------------------------------------------------------
result(
    "variance",
    probe.variance() == [datetime.datetime(2014, 2, 6, 0, 0), 1574.489562817637, 0])

#Standard deviation
#----------------------------------------------------------------
result(
    "standard deviation",
    probe.stddev() == [datetime.datetime(2014, 2, 6, 0, 0), 39.67983824081995, 0])

#Linear Regression Coefficients
#----------------------------------------------------------------
result(
    "linear regression coefficients",
    probe.linreg() == (-3.2215856195371914e-05, 45607.98076509822, -0.668228372287951))

#trendline
#----------------------------------------------------------------
probe = tslite.timeseries().loadSQLITE3(conn, "trendline")
t2 = tslite.timeseries().loadSQLITE3 (conn, "test6hr")
result("linear regression trendline", t2.trendline() == probe)
print (t2,probe)


#cull
#----------------------------------------------------------------
t = tslite.timeseries().loadSQLITE3 (conn, "testdaily")
t2 = t.cull(lambda x, y: x > y, 800.0)
probe = tslite.timeseries().loadTSV("test/cull.tsv")
result("cull below a constant (in this case 800)", t2.__eq__(probe, precision=2))

#centerMovingAverage
#----------------------------------------------------------------
r = t2.centerMovingAverage(t.TD("5d"))
t3 = t2.cull(lambda x, y: x > y, r)
#t2.saveTSV("test/cull.tsv")
probe = tslite.timeseries().loadTSV("test/TScull.tsv")
result("TS cull", t3.__eq__(probe, precision=2))

#cut
#----------------------------------------------------------------
t1 = t2.cut(t3)
result("cut", t1.__eq__(probe, precision=2))

#Moving Standard Deviation
#----------------------------------------------------------------
t1 = t.movingstddev("1d")
probe = tslite.timeseries().loadTSV("test/movingSTDDEV.tsv")
result("Moving Standard Deviation", t1.__eq__(probe, precision=2))

#toJSON
#----------------------------------------------------------------
probe = open("test/test.json", "r").read()
result("toJSON", t1.toJSON() == probe)

#Round
#----------------------------------------------------------------
probe = tslite.timeseries().loadTSV("test/round.tsv")
result("round", t1.round(2) == probe)

#Truncate
#----------------------------------------------------------------
probe = tslite.timeseries().loadTSV("test/truncate.tsv")
result("truncate", t1.truncate(2) == probe)

#First Difference
#----------------------------------------------------------------
t = tslite.timeseries().loadSQLITE3(conn, "test").firstdifference()
#t.saveSQLITE3(conn,"firstdifference", replace_table = True)
probe = tslite.timeseries().loadSQLITE3(conn, "firstdifference")
result("first difference (simpledelta)", t == probe)

#To Plot
#----------------------------------------------------------------
x, y = t.toPlot()
t = tslite.timeseries()
for i in range(len(x)):
  t.insert(x[i], y[i])
result("toPlot", t == probe)

#runningTotal
#----------------------------------------------------------------
t1 = tslite.timeseries().loadTSV("test/inflow.tsv")
probe = tslite.timeseries().loadTSV("test/runningTotal.tsv")
result("runningTotal", t1.runningTotal() == probe)
