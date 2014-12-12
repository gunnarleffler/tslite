#This shell file builds documentation and the python3 version
cd ..
cp tslite.py tslite3.py
2to3 -n -W -v -w tslite3.py
#-------------------------
pydoc -w tslite
cat tslite.html | pandoc -f html -t markdown -o doc/tslite.md
rm tslite.html
