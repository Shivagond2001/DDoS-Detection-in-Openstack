#main_file.py
from sys import exit
#system.path.insert(0,"/home/ubuntu/minor/support/")
import pandas as pd
import math
from scipy.stats import entropy
import os,json,subprocess

def capture():
    print("Capture Initiated")
    interfaces = os.listdir('/sys/class/net/')
    st = ["timeout"]
    st.append("3")
    st.append("tcpdump")
    ofile="/home/captures.pcap"
    st.append("-i")
    st.append("gre_sys")
    st.append("-G 3")
    st.append("port not 22")
    st.append("-w")
    st.append(ofile);
    p =subprocess.run(st);
    ffile = "/home/ubuntu/minor/support/capture.csv";
    with open(ffile,"w") as outfile:
            subprocess.run(["tshark", "-r",ofile,"-T","fields","-e","ip.src","-e","ip.dst"],stdout= outfile)

#load details of all instances from cloud
with open("/home/ubuntu/instance_details.json") as inst:
    instances=json.load(inst)
capture()


