from openstack import connection
import paramiko
import re
import socket
controller_ip = "192.168.23.81"
username = "ubuntu"
password = "root1234"
port = 22

auth_args = {
	    'auth_url' : 'http://'+ controller_ip+':5000/identity/v3',
	    'project_name' : 'admin',
	    'username' : 'admin',
	    'password' : 'admin_pass',
	    'user_domain_id' : 'default',
	    'project_domain_id' : 'default',
	}
conn = connection.Connection(**auth_args)
	
def node_details():
	controller_ssh=paramiko.SSHClient()
	controller_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	controller_ssh.connect(controller_ip,port,username,password)
	controller_sftp_client = controller_ssh.open_sftp()
	nodes_file = controller_sftp_client.open('/etc/hosts')
	nodes ={}
	for line in nodes_file.readlines():
		if("compute" in line or "controller" in line or "neutron" in line ):
			line=line.split()
			#print(line)
			lines = {line[2]:{"ip":line[0],"host_name":line[1]}}
			nodes.update(lines)
	nodes_file.close()
	controller_sftp_client.close()
	controller_ssh.close()
	return nodes
	
def instance_details():
	nodes = node_details()
	lst = list(conn.compute.servers(details=True, all_projects=False))
	instances = {}

	for l in lst:
		if "net1" in l.addresses:
			ip = l.addresses['net1'][0]['addr']
			s = l.hypervisor_hostname
			s= s.split(".")
			details= {"name":l.name,"host":s[0],"inst_name":l.instance_name,"public_ip":l.addresses['net1'][1]['addr']}
			final = {ip:details}
			instances.update(final)
		
	
	#for all instances
	for inst in instances:
		cmd='virsh domiflist '+  instances[inst]['inst_name']
		for node in nodes:
			#print("for node "+node)
			if(node == instances[inst]["host"]):
				ssh = paramiko.SSHClient()
				ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				ssh.connect(nodes[node]['ip'],port,username,password)
				#print("SSH Connection Successfull")
				stdin,stdout,stderr=ssh.exec_command(cmd)
				out = stdout.read().decode('UTF-8')
				#print(out)
				if (not out.isspace()):
					out = (out.split("\n"))[2]
					out = re.split(' +',out)
					instances[inst]['port'] = out[2]
					#print(out)
				stdout.close()
				ssh.close()
	#print(instances)
	return instances;
"""	
node = node_details()
instance= instance_details()

for k in node:
	print(node[k]['ip'])
	print(node[k]['host_name'])
	print("\n\n")
	
print("==========================")
for k in instance:
	print(instance[k]['name'])
	print(instance[k]['host'])
	print(instance[k]['inst_name'])
	print(instance[k]['public_ip'])
	print(instance[k]['port'])
	print("\n")

"""
