#
#   Script for generating test suit html report.
#   Author: Subhajit Dey
#   Last Updated: 11/06/2019
#

import sys,glob
import json,traceback,os,csv,time,datetime
import SimpleHTTPServer
import SocketServer

PORT = 8000

Handler = SimpleHTTPServer.SimpleHTTPRequestHandler



json_data = []
scanned_files = []
scanned_tc = []
process_files = []
scanned_dates = []
scanned_buildes = []


# Reads scan_data.json file and loads previously scanned files information and test case information
def loadScanInfo():
    global scanned_files,scanned_tc,process_files,json_data,scanned_dates

    rfile=open('scan_data.json','r')
    json_data = json.load(rfile)
    
    for files in json_data["scanned_files"]:
        scanned_files.append(str(files))
    for tcase in json_data["testcases"]:
        scanned_tc.append(str(tcase))
    for sdates in json_data["scanned_dates"]:
        scanned_dates.append(str(sdates))
    for brelease in json_data["scanned_builds"]:
        scanned_buildes.append(str(brelease))
    
    #print scanned_buildes

    #print scanned_dates
    #sorted_dates = scanned_dates
    #sorted_dates.sort(key=lambda x: time.mktime(time.strptime(x,"%Y-%m-%d")))
    #print sorted_dates
    

def loadNewFiles():
    global scanned_files,scanned_tc,process_files,json_data,scanned_dates,scanned_buildes

    allfiles = glob.glob("*.csv")
    for filename in allfiles:
        if filename not in scanned_files:
            process_files.append(filename)
            scanned_files.append(filename)

def sortDates(timestamps):
    _timestamps = [datetime.datetime.strptime(ts, "%Y-%m-%d") for ts in timestamps]
    _timestamps.sort()
    return [datetime.datetime.strftime(ts, "%Y-%m-%d") for ts in _timestamps]


def loadData():
    rfile=open('data.json','r')
    return json.load(rfile)

def getBuildInfo(arg):
    tmp = ["","", ""]
    df=b= False
    max_date = "1970-01-01"
    for row in arg:
        d = row[0].replace('"','').split(",")
        if len(str(d[11])) > 0 :
            tmp[0] = str(d[11].split("T")[0])
            df = True
        
        if len(d[10]) > 0 :
            tmp[1] =  d[10].split("-")[3]
            b = True

    #    if df and b : 
    #        break
        if len(str(d[12])) > 0 :
            if datetime.datetime.strptime(max_date, '%Y-%m-%d')  < datetime.datetime.strptime(str(d[12].split("T")[0]), '%Y-%m-%d'):
                max_date = str(d[12].split("T")[0])
    tmp[2] = max_date
    return tmp


def processFiles():    
    global scanned_dates,scanned_buildes

    raw_data = loadData()
    for files in process_files:
        print files
        #with open(files, 'r') as fin:
         #   data = fin.read().splitlines(True)
        #with open(files, 'w') as fout:
         #   fout.writelines(data[1:])
        with open(files,"rU") as f:
            data =list( csv.reader(f,dialect=csv.excel_tab))
            #print data
            data.pop(0)
            proxy_data = getBuildInfo(data)
            if len(proxy_data[0]) > 0 and len(proxy_data[1]) > 0 :
                for row in data:
                    d = row[0].replace('"','').split(",")
                    #print d
                    testcase = d[2].split(".")[0].split("_")
                    if len(testcase) > 2:
                        testcase.pop(0)
                    if len(str(d[11])) > 0 :
                        #date = str(d[11].split("T")[0])
                        tcase = "_".join(testcase)
                        build = d[10].split("-")[3]
                    else :
                        #date = proxy_data[0]
                        tcase = "_".join(testcase)
                        build = proxy_data[1]
                    
                    date = proxy_data[2]
                    
                    #print scanned_buildes
                    if build not in raw_data :
                        raw_data[build] = {}
                        raw_data[build]["tc_dates"] = []
                        raw_data[build]["tc"] = {}                             
                        scanned_buildes.append(build)
                    

                    if date not in raw_data[build]["tc_dates"]:
                        raw_data[build]["tc_dates"].append(date)
                        raw_data[build]["tc_dates"] = sortDates(raw_data[build]["tc_dates"])
                    
                    if tcase not in raw_data[build]["tc"] :
                        raw_data[build]["tc"][tcase] = {}    
                        #print tcase
                        scanned_tc.append(tcase)               
                        
                    raw_data[build]["tc"][tcase][date] = {}

                    if date not in scanned_dates :
                        scanned_dates.append(date)
                        
                    raw_data[build]["tc"][tcase][date]["id"] = d[0]
                    raw_data[build]["tc"][tcase][date]["t"] = d[5]                 
                    raw_data[build]["tc"][tcase][date]["p"] = d[6]
                    raw_data[build]["tc"][tcase][date]["f"] = d[7]
                    raw_data[build]["tc"][tcase][date]["r"] = d[4]
                    raw_data[build]["tc"][tcase][date]["s"] = d[3]
                    raw_data[build]["tc"][tcase][date]["sid"] = files.split("_")[1]

    
    wfile = open ("data.json","w")
    json.dump(raw_data,wfile)    

def updateScanInfo():
    global scanned_files,scanned_tc,process_files,json_data,scanned_dates

    json_data["scanned_files"] = scanned_files
    json_data["testcases"] = scanned_tc
    json_data["scanned_dates"] = scanned_dates
    json_data["scanned_builds"] = scanned_buildes
    wfile = open ("scan_data.json","w")
    json.dump(json_data,wfile)

def main():
    loadScanInfo()
    loadNewFiles()
    processFiles()
    updateScanInfo()    
    httpd = SocketServer.TCPServer(("10.163.68.83", PORT), Handler)

    print "http://http://10.163.18.129:"+str(PORT)
    httpd.serve_forever()

if __name__ == '__main__':
    if len(sys.argv) != 1:
        print 'Usage: python report_gen.py '
        os._exit(1)
    try:
        main()
    except Exception, e:
        print str(e)
        traceback.print_exc()
        os._exit(1)
