from getpass import getpass
import csv
from netmiko import Netmiko

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Change these:
username = "jeffrey.chen"
csv_file_name = "ngm_radio_device_group_joshua.csv" #csv file
configlet_file_name = "./gst_test.txt" #txt file
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


pw = getpass()

access = {
    "host": "10.0.0.0",
    "username": username,
    "password": pw,
    "secret": pw,
    "device_type": "cisco_ios", #use "cisco_ios_telnet" if telnetting.
    "global_delay_factor": 3
}

mgmt_ips = list()
with open(csv_file_name, newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        if row[1] != "Mgmt IP":
            mgmt_ips.append( (row[1], row[0]) )

failed = list()

for ip in mgmt_ips:
    access['host'] = ip[0]
    try: #try to login
        print(f"Configuring {access['host']}... ", end= "")
        net_connect = Netmiko(**access)
        print("logged in... ", end= "")
    
    except:
        failed.append(ip)
        print("failed to login!")
        continue
    
    try: #try to configure 
        net_connect.enable()  #not always necessary
        #print()
        (net_connect.send_config_from_file(configlet_file_name)) #can "print()"
        (net_connect.save_config()) # can "print()"
        print("successfully configured!")
    except:
        failed.append(ip)
        print("failed to configure!")
    net_connect.disconnect()

print("Failed for: " )
for failed_ip in failed:
    print(f"{failed_ip[0]},  {failed_ip[1]}")
