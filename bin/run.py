import sys
sys.path.insert(0, "/home/ubuntu/ddos/support")
import joblib
import os
import subprocess
import json
import api
from scipy.stats import entropy
from sklearn import preprocessing
import numpy as np
import pandas as pd
from pandas.errors import EmptyDataError

import paramiko,time



username = "ubuntu"
password = "root1234"
port = 22
# get all instancces details
# print("==================================================")
#print("get all instancces details")


instances = api.instance_details()
with open("/home/ubuntu/ddos/support/instance_details.json", "w") as outfile:
    json.dump(instances, outfile)
# print("==================================================\n\n\n")


# connect to neutron
print("==================================================")
print("Connecting to neutron")
neutron_ssh = paramiko.SSHClient()
neutron_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
neutron_ssh.connect("192.168.23.82", port, username, password)
neutron_sftp = neutron_ssh.open_sftp()

#print("Send instance details file to neutron and run main file\n\n")
# send instance detaisl to neutron
neutron_sftp.put('/home/ubuntu/ddos/support/instance_details.json','/home/ubuntu/instance_details.json')
print("==================================================")
print("Getting captured csv file from neutron node\n")
ent1=[]
while True:
    
    # rum main_file to collect data from neutron
    stdin, stdout, stderr = neutron_ssh.exec_command('sudo python3 /home/ubuntu/minor/main_file.py')
    stderr.readlines()
    stdout.readlines()
    #for line in stderr.readlines():
    #    print(line)
    #for line in stdout.readlines():
    #    print(line)
    
    neutron_sftp.get("/home/ubuntu/minor/support/capture.csv","/home/ubuntu/ddos/support/csv/neutron_capture.csv")

    ips_list = []
    for i in instances:
        ips_list.append(i)
    ips = pd.Series(ips_list)


    dest = []

    # if (os.stat("/home/ubuntu/ddos/support/csv/neutron_capture.csv").st_size == 0):
    #     #print("File Size Zero at neutron level")
    #     continue
    # else:
    #print("Inside Else")
    try:
        data = pd.read_csv("/home/ubuntu/ddos/support/csv/neutron_capture.csv", delimiter='\t')
        data = data.dropna()
        dest_ip = data[data.columns[1]]
        for ip in data[data.columns[1]]:
            for i in ips.iteritems():
                if(ip == i[1]):
                    octet = ip.split('.')
                    dest.append(octet[3])
        if( len(dest) != 0):
            pd_series = pd.Series(dest)
            #print("+++++++++ length of pnadsseries is :",len(pd_series))
            counts = pd_series.value_counts()
            #print(type(counts))
            print("ip   count")
            print(counts)
            ent = entropy(counts)
            dict1 = {"ent": ent}
            d2 = {}
            s = counts.size
            for i in range(s):
                d = {counts.index[i]: counts.values[i].astype(str)}
                d2.update(d)
                #print("Index is " + counts.index[i] +" value " + counts.values[i].astype(str))
            dict1.update({"ips": d2})
            #print(type(counts))
            #print(ent)
            counts.empty
            data.empty

        # after calculating entropy get entroy file

            print("Calculating entropy value\n")
            print("Entropy Value is ", dict1["ent"])
            
            if((ent <= 0.85) and (len(dict1['ips'])!=0)):
                #for k in dict1['ips']:
                 #   print(k)                
                maximum = max(zip(dict1['ips'].values(), dict1['ips'].keys()))[1]
                # set attack ip
                nodes = api.node_details()
                attack_ip = "100.100.24." + (str(maximum))
                attack_compute_node = instances[attack_ip]['host']
                attack_compute_node_ip = nodes[attack_compute_node]['ip']
                print("\nAttack on compute node:"+attack_compute_node )
                #print("Setting attack ip success /n")

                # export attack_ip instance details to local
                with open("/home/ubuntu/ddos/support/attack_ip_details.json", "w") as outfile:
                    json.dump(instances[attack_ip], outfile)

                # close neutron ssh connections

                #print("==================================================\n\n\n")

                # get all node details(controller,compute,neturon)
                

                # After Finding Entropy To invoke

                # Connect to attak compute node
                print("==================================================")
                print("Connecting to attack compute node")
                
                print("Invoking Machine Learning on ", attack_compute_node)
                # print(attack_compute_node)
                attack_ssh = paramiko.SSHClient()
                attack_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                attack_ssh.connect(attack_compute_node_ip, port, username, password)
                attack_sftp = attack_ssh.open_sftp()
                #print("Connection to attack node successful")
                subprocess.run

                # send attack ip details to attack compute node
                attack_sftp.put('/home/ubuntu/ddos/support/attack_ip_details.json','/home/ubuntu/attack_ip_details.json')

                # run main file in attack compute node and get captured data
                #print("Executing main file in attack compute node and Collecting Data ")
                stdin, stdout, stderr = attack_ssh.exec_command('sudo python3 /home/ubuntu/minor/main_file.py')
                stderr.readlines()
                stdout.readlines()
                #for line in stderr.readlines():
                #    print(line)
                #for line in stdout.readlines():
                #    print(line)
                #print("Collecting Data Completed")
                attack_sftp.get("/home/captures.pcap","/home/ubuntu/ddos/support/captures.pcap")
                #print("Pcap file retreived successfully from attack compute node\n")
                #print("Convert pcap to csv using CICFlowMeter")
                subprocess.run(["./cfm", "/home/ubuntu/ddos/support/captures.pcap","/home/ubuntu/ddos/support/csv/"])
                #print("Convet to csv success")
                f = os.listdir("/home/ubuntu/ddos/support/csv")
                f = f[0]

                if (os.stat("/home/ubuntu/ddos/support/csv/" + f).st_size == 0):
                    #print("File Size Zero at compute level")
                    continue
                else:
                    print("\n\nApplying Ml")
                    label_encoder = preprocessing.LabelEncoder()

                    data = pd.read_csv("/home/ubuntu/ddos/support/csv/"+f)
                    # print(data)               
                    test = data.loc[:, ['Flow ID', 'Src IP', 'Dst IP', 'Flow Duration', 'Tot Bwd Pkts', 'Flow Pkts/s', 'Flow IAT Mean', 'Flow IAT Max','Flow IAT Min', 'Bwd IAT Tot', 'Bwd IAT Mean', 'Bwd Pkts/s', 'Subflow Bwd Pkts', 'Init Fwd Win Byts', 'Init Bwd Win Byts']]
                    test['Flow ID'] = label_encoder.fit_transform(test['Flow ID'])
                    test['Flow ID'].unique()
                    test['Src IP'] = label_encoder.fit_transform(test['Src IP'])
                    test['Src IP'].unique()
                    test['Dst IP'] = label_encoder.fit_transform(test['Dst IP'])
                    test['Dst IP'].unique()
                    model = joblib.load("/home/ubuntu/ddos/support/LR.joblib")
                    #print(test)
                    result = model.predict(test.values)
                    value = list(set(result))
                    #print(value)
                    if(len(value) == 2):
                        print("\nDDoS Attack confirmed.....!\n\n\n")
                        time.sleep(2)
                    else:
                        if(value[0] == 0):
                            print("\nNo attack...!\n\n\n")
                        else:
                            print("\nDDoS Attack confirmed....!\n\n\n")
                            time.sleep(2)

                    # close attack compute node ssh connection
		                 
            else:
                #os.system('clear')
                print("\n\n============================  Traffic is normal. No Malicious traffic detected  ============================\n\n")
            
        else:
            continue
            
    except EmptyDataError:
        continue
    # print(data)
    
print(ent1)    
#attack_sftp.close()
#attack_ssh.close()
neutron_sftp.close()
neutron_ssh.close()
