import time
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from netmiko import Netmiko

import threading

"""
Modules necessary to run the full program:
    pip install selenium
    pip install netmiko
"""


#Meaning of output:
# "yes" the device is definitely in solarwinds
# "maybe" not enough information to tell--check manually? perhaps the device 
    #hostname was written incorrectly, or the interface description is incorrect.
    #or the device is just not there. 
# "no" definitely not in solarwinds. 


# CONFIGURATION:
###############################################################################
#
# Setup the webdriver location (check selenium documentation for how, and how to get the driver)
chrome_loc = 'C:\\Users\\jeffrey.chen\\Downloads\\code\\modules\\_selenium_chrome\\chromedriver.exe'

#Input Network_Inventory_Template_v1.3.2  (as a csv file):
data_file_name = "agg_data.csv"
#Output file name (csv file):
output_data_file_name = "result_agg_v4.csv"

#DELAY (probably don't have to change unless on slow connection)
delay_time = 11

#Leave 'manual_checking' as False.
manual_checking = False

#Login_check to check if switches can be readily logged in to be configured. 
#NOTE: Highly recommended to leave as "True" for at least one run. 
login_check = False
#fill out the username and password if you are doing the "login_check"
user_user = "jeffrey.chen"
user_pw = ""

access = {
    "host": "",
    "username": user_user,
    "password": user_pw,
    "device_type": "cisco_ios"
}
#
################################################################################



catalyst_switches = [["Mgmt IP", "Hostname", "Solarwinds?", "Can login?"]]
with open(data_file_name, newline='') as f:
    reader = csv.reader(f)
    for row in reader:
        if(row[0] == "Catalyst Switch"):
            #"convert_to_list" to be ["Mgmt IP", "HostName", "in solarwinds?", 
            #                                                   "login able?""]
            convert_to_list = [ row[2] ]
            convert_to_list.append( row[1] )
            convert_to_list.append("in solarwinds?")

            if login_check:
                convert_to_list.append("can login?")
            catalyst_switches.append(convert_to_list)
total_switches = len(catalyst_switches)
print(f"{total_switches} total switches!")



def selenium_function(catalyst_switches, start, level):
    driver = webdriver.Chrome(chrome_loc)

    #access the website
    driver.get('https://usaslcnet3.goldbar.barrick.com/ui/search?q=10.12.90.4')

    #initialize variables
    start_time = time.time()

    count = 0 #using a separate counter here for clarity. 

    time.sleep(delay_time)

    #(1, total_switches)
    for i in range(start, total_switches, level): #iterate through each ip_address. 
        count += 1
        time.sleep(1) # brief pause to let page finish loading. 
        if start == 1:
            time_elapsed = (time.time() - start_time)
            per_switch_time = time_elapsed/count
            remaining_time = (total_switches-i)*per_switch_time/(level)
            print(f"Progress: {round((i / (total_switches-1))*100, 1)}%, time remaining: {round(remaining_time/60)} min, time elapsed: {round(time_elapsed/60)} min.")
        
        if (count % 24 == 0): #recommended to leave this below about 46. 
            print("Reloading the client")
            driver.quit()
            time.sleep(1)
            driver = webdriver.Chrome('C:\\Users\\jeffrey.chen\\Downloads\\code\\modules\\_selenium_chrome\\chromedriver.exe')
            time.sleep(1)
            driver.get('https://usaslcnet3.goldbar.barrick.com/ui/search?q=10.12.90.4')
            time.sleep(22) #wait for the page to load properly before searching. 


        #intialize switch variables:
        catalyst_switch = catalyst_switches[i]
        ip_address = catalyst_switch[0]  #"10.12.1.112"
        device_name = catalyst_switch[1]  #"USAGSTSW112"

        # Use selenium to load up the x_paht of the searchbar. I wasn't able to find the precise
        #x_path of the searchbar, so this is a way to brute force the search_bar. 
        # Obviously, this code could be improved with the "true" x_path of the search_bar. 
        def loader():
            for x in ["F","H","E","J","K","G","I","A","B","C","D","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]:
                try:
                    searchbar = driver.find_element_by_xpath(f'//*[(@id = "search_00{x}_Input")]')
                    return searchbar
                except:
                    pass

        #try:
        #    searchbar = driver.find_element_by_xpath(f'//*[(@id = "search_00G_Input")]')
        #    
        #except:
        #    searchbar = driver.find_element_by_xpath(f'//*[(@id = "search_00E_Input")]')
        searchbar = loader()
        for i in range(15):
            searchbar.send_keys(Keys.BACKSPACE)
        searchbar.send_keys(ip_address)
        time.sleep(1)
        searchbar.send_keys(Keys.ENTER)
        time.sleep(delay_time)



        if login_check:
            #INTERJECTION:
            try:
                access['host'] = ip_address
                net_connect = Netmiko(**access)
                catalyst_switch[3] = "Success"
            except:
                catalyst_switch[3] = "Fail"
        
        #for efficiency, as "driver.page_source" is absurdly large and .count iterates through everything
        #  Additionally this prevents longer duplicates from interferring with the count 
        device_name_page_count = driver.page_source.count(device_name + '"') #if the host name is not highlighted
        device_name_page_count += driver.page_source.count(device_name + '<') #if the host name is highlighted
        device_name_page_count += driver.page_source.count(device_name + '.') # .barrickgold or anything

        ##########
        #  REMOVE THIS LINE IF TRUNK LINKS ARE NOT VALID. 
        device_name_page_count += driver.page_source.count(device_name + ' ') #trunks count, assuming the naming convention makes some sense. 
        

        try_search_count = driver.page_source.count('type="no-result" additional-text="' + ip_address + '"')

        if (device_name_page_count >= 1):
            #in solarwinds
            catalyst_switch[2] = "Yes"
        else:
            if (try_search_count == 0):
                if manual_checking:
                    t_response = input("Please check the page. If something isn't okay, type 'no': ")
                    if (t_response == 'no'):
                        catalyst_switch[2] = "No"
                        print(f"didn't find {ip_address}")
                    else:
                        catalyst_switch[2] = "Yes"
                else: #//@assert(manual_checking == false)
                    catalyst_switch[2] = "Maybe"
                    
            #Otherwise, it definitely is not in the page.
            else:
                #//@assert("Try searching for" in driver.page_source)
                catalyst_switch[2] = "No"

    #exit the window
    driver.quit()
    return

    #column for data analysis (need to return these probably)
    


num_threads = 5

t1 = threading.Thread(target=selenium_function, args=(catalyst_switches,1,num_threads,))
t2 = threading.Thread(target=selenium_function, args=(catalyst_switches,2,num_threads,))
t3 = threading.Thread(target=selenium_function, args=(catalyst_switches,3,num_threads,))
t4 = threading.Thread(target=selenium_function, args=(catalyst_switches,4,num_threads,))
t5 = threading.Thread(target=selenium_function, args=(catalyst_switches,5,num_threads,))
#t6 = threading.Thread(target=selenium_function, args=(catalyst_switches,6,num_threads,))
#t7 = threading.Thread(target=selenium_function, args=(catalyst_switches,7,num_threads,))
#t8 = threading.Thread(target=selenium_function, args=(catalyst_switches,8,num_threads,))
#t9 = threading.Thread(target=selenium_function, args=(catalyst_switches,9,num_threads,))
#t10 = threading.Thread(target=selenium_function, args=(catalyst_switches,10,num_threads,))

t1.start()
t2.start()
t3.start()
t4.start()
t5.start()
#t6.start()
#t7.start()
#t8.start()
#t9.start()
#t10.start()

t1.join()
t2.join()
t3.join()
t4.join()
t5.join()
#t6.join()
#t7.join()
#t8.join()
#t9.join()
#t10.join()

#comment the rest out and just use this if you don't want multithreading. 
#selenium_function(catalyst_switches, 1, 1)

print("\nProcessing data! May take a significant portion of time. ")
#["Mgmt IP", "HostName", "in solarwinds?","login able?""]

if login_check:
    access["host"] = "10.12.1.1"
    net_connect = Netmiko(**access)

in_solarwinds = 0
loginable = 0
for i in range(len(catalyst_switches)):

    row = catalyst_switches[i]
    if row[2] == "Yes":
        in_solarwinds += 1
    if login_check:
        if row[3] == "Success":
            loginable += 1
        else:
            if ("0/3" in net_connect.send_command(f"ping {row[0]} repeat 3 timeout 1")):
                row[3] = "Fail + no Ping"
                print(f"{i} of {total_switches}")


catalyst_switches.append(["Statistics:", "", "%in solarwinds", "%loginable"])
catalyst_switches.append(["", "", f"{in_solarwinds/(total_switches-1)}", 
                       f"{loginable/(total_switches-1)}"])


#store the contents of the processed data into "output_data_file_name"
with open(output_data_file_name, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(catalyst_switches)

print(f"\nDone! Saved in {output_data_file_name}")