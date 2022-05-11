#main_file.py
import pandas as pd
import math
from scipy.stats import entropy
import os,glob,json
import subprocess



with open("/home/ubuntu/attack_ip_details.json") as inst:
    attack_ip_details=json.load(inst)
with open("/home/captures.pcap", "w") as ofile1:
    print("Capturing Initiated")
    ofile = "/home/captures.pcap"
    st=["dumpcap"]
    sel= [];
    st.append("-i")
    st.append(attack_ip_details['port'])
    st.append("-a")
    st.append("duration:3")
    st.append("-w")
    st.append(ofile);
    st.append("-P");
    print("Pcap file creation success")
    print("Running dumpcap")
    subprocess.run(st)



print("Capture Complete")

