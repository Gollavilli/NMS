#Importing necessary libraries
import time
import paramiko
import connexion
import re
from hcparser import dextractor
from userdevices import get_node
from asr5000 import asr5000_obj
#-------------------------------

#Turning on debug - to be removed later
DEBUG = True
#------------------

# constructing ping commands with parameters
PING_COMMAND_2000 = r'ping 172.25.2.240 size 2000'
PING_COMMAND_5000 = r'ping 172.25.2.240 size 5000'
#-------------------------------------------


version_string = None
# Displaying the Format Structure from end point of view

# Checks the Configuration Register
def show_version_i_config(output,response):
    value = dextractor.extract_version(output.split("\n"))
    config_ = value.get("configuration","")
    R = value.get('R',1)
    response["configregister"] = {"message":"configuration register = %s"%(config_,),"R":R}


# Checks the Version for the device
def show_version(output,response):
    global version_string
    version_string =  dextractor.extract_version(output.split("\n"))
    R = version_string.get('R',1)
    response["iosversion"] = {"message":version_string.get("version",""),"R":R}


# Checks the CPU Utilization for the device
def show_process_cpu(output,response):
    resp = dextractor.extract_utilization(output)
    one_second = resp.get("five_seconds","")
    one_minute = resp.get("one_minute","")
    five_minutes = resp.get("five_minutes","")
    cpu_utilization = {"cpuutilization": "1s = %s; 1m = %s; 5m= %s"%(one_second,one_minute,five_minutes)}
    response.update(cpu_utilization)

# Checks the Environment and the following alarm's for the device
def show_environment(output,response):
    total_alarms = dextractor.extract_alarms(output)
    total_num = total_alarms.get("total_alarms","")
    R = total_alarms.get('R',1)
    response["environmental"] = {"message":"Total alarms = %s"%(total_num,),"R":R}


# Checks the Buffers and looks for any Misses in each Buffer Module
def show_buffers(output,response):
    total_buffer = 0
    buffers = dextractor.extract_buffers(output.split("\n"))
    for key in buffers:
        total_buffer += int(buffers[key])
    R = buffers.get('R',1)
    response["buffers"] = {"message":"Max Buffer misses = %s"%(str(total_buffer),),"R":R}


# Checks the Platform and specifies every slot is OK or not.
def show_platform(output,response):
    not_ok_count = 0
    devices = dextractor.extract_show_platform()#output.split("\n")
    if devices.has_key('R'):
        R = devices.pop('R')
    else:
        R = 1
    for key in devices:
        if "ok" not in devices[key]:
            not_ok_count += 1
    response["platform"] = {"message":"not ok slots = %s"%(str(not_ok_count),),"R":R}

# Checks the Interface Counter's Count
def show_interfaces(output,response):
    value = dextractor.count_interfaces(output.split("\n"))
    val_ = value.get("count_interfaces","")
    R = value.get('R', 1)
    response["interfacecounters"] = {"message":val_,"R":R}

# Checks the Memory available at the Device
def show_memory_statistics(output,response):
    value = dextractor.extract_memory_statistics()#output.split("\n")
    R = value.get('R',1)
    free_mem = "Free memory = %s"%(value.get("Free(b)",""))
    response["freememory"] = {"message": free_mem,"R":R}

# Checks the Interface states and looks for status of the device
def show_ip_interface_brief(output,response):
    resp = dextractor.extract_show_brief()
    down_devices = 0
    if resp.has_key('R'):
        R = resp.pop('R')
    else:
        R = 1
    for key in resp:
        value = resp[key].lower()
        if not ( value == "up" ):
            if not (value == "administratively down"):
                down_devices += 1
    response["interfacestates"] = {"message":"down neighbors = %s"%(str(down_devices),),"R":R}

# Checks the BFD's Sessions for the all the neighbors associated to the device
def show_bfd_neighbor(output,response):
    down_neighbours = 0
    resp = dextractor.extract_bfd_neighbour()#output.split("\n")
    if resp.has_key('R'):
        R = resp.pop('R')
    else:
        R = 1
    for key in resp:
        up_down = resp[key]
        if not (up_down == "Up"):
            down_neighbours += 1
    response["bfdsession"] = {"message":"down neighbors = %s"%(down_neighbours,),"R":R}


# Checks the MPLS Neighbor's for the device and their associated IP_addresses.
def show_mpls_ldp_neighbor(output,response):
    resp = dextractor.extract_mlps_ldp_neighbour()#output.split("\n")
    R = resp.get('R',1)
    response["mplsneighbors"] = {"message":"mpls ldp neighbors = %s"%(resp.get("count",""),),"R":R}

# Checks the MPLS states for the given device.
def show_mpls_interfaces(output,response):
    resp = dextractor.extract_mlps_interfaces()#output.split("\n")
    devices_down = 0
    if resp.has_key('R'):
        R = resp.pop('R')
    else:
        R = 1
    for key in resp:
        device = resp[key]
        ip = device.get("ip","")
        operational = device.get("operational","")
        if (ip and operational):
            if not ( ((ip =="Yes") or (ip=="Yes(ldp)")) and (operational=="Yes")):
                devices_down += 1
    response["mplsinterfaces"] = {"message":"count of failed interfaces = %s"%(str(devices_down),),"R":R}

# Checks for the given device version matches the specified boot statement.
def show_running_config_i_boot(output,response):
    global version_string
    R = 1
    flag = dextractor.extract_show_running_config(output.split("\n"),version_string).get("type_match",False)
    if flag:
        statement = "Boot statement matches Version"
        R = 0
    else:
        statement = "Boot statement does not matches Version"
    response["bootstatement"] = {"message":statement,"R":R}

# Checks the count for BGPv6 Routes
def show_ip_bgp_v6_vrf_lte(output,response):
    ifaces = dextractor.extract_bgpv6_routes()#output.split("\n")
    cnt = None
    if ifaces.has_key('R'):
        R = ifaces.pop('R')
    else:
        R = 1
    if ifaces.keys():
        cnt = len(ifaces.keys())
    response["bgpvsixroutes"] = {"message":cnt,"R":R}

# Checks the BGPv4 Routes for the device
def show_ip_bgp_v4_vrf_1xrtt(output,response):
    ifaces = dextractor.extract_bgpv4_1xrtt()#output.split("\n")
    cnt = None
    if ifaces.has_key('R'):
        R = ifaces.pop('R')
    else:
        R = 1
    if ifaces.keys():
        cnt = len(ifaces.keys())
    response["1xrtt"]={"count":cnt,"R":R}

# Checks the BGPv4 Routes for the device
def show_ip_bgp_v4_ran(output,response):
    ifaces = dextractor.extract_bgpv4_ran()#output.split("\n")
    cnt = None
    if ifaces.has_key('R'):
        R = ifaces.pop('R')
    else:
        R = 1
    if ifaces.keys():
        cnt = len(ifaces.keys())
    response["ran"]={"count":cnt,"R":R}

# Checks the BGPv4 Routes for the device
def show_ip_bgp_v4_cell_mgmt(output,response):
    ifaces = dextractor.extract_bgpv4_cell_mgmt()#output.split("\n")
    cnt = None
    if ifaces.has_key('R'):
        R = ifaces.pop('R')
    else:
        R = 1
    if ifaces.keys():
        cnt = len(ifaces.keys())
    response["cell_mgmt"]={"message":cnt,"R":R}

def show_xconnect_all(output,response):
    resp = dextractor.xconect_all()#output.split("\n")
    #print resp
    response["xconnect"] = resp

def bgp_v4_neighbour(output,response):
    resp = dextractor.bgpv4_neighbour()#output.split("\n")
    response["bgpvfourneighbors"] = resp

def bgp_v6_neighbour(output,response):
    resp = dextractor.bgpv6_neighbour()#output.split("\n")
    response["bgpvsixneighbors"] = resp

def show_logging(output,response):
    resp=dextractor.extract_show_logging()
    response ["Log Entries"]= resp
#-------------------------------------

def asr5000_show_clock(output,response):
    resp = asr5000_obj.extract_show_clock()#output.split("\n")
    response["show_clock"] = resp.get("show_clock","")

def asr5000_show_system_uptime(output,response):
    resp = asr5000_obj.extract_show_system_uptime()#output.split("\n")
    response["show_system_uptime"] = resp.get("show_system_uptime","")

def asr5000_show_version_grep_img_ver(output,response):
    resp = asr5000_obj.extract_show_version_grep_image_version()#output.split("\n")
    response["show_version_grep_image_version"] = resp.get("show_version_grep_image_version","")

def asr5000_show_srp_info_grep_chassis_state(output,response):
    resp = asr5000_obj.show_srp_info_grep_chassis_state()#output.split("\n")
    response["show_srp_info_grep_chassis_state"] = resp.get("show_srp_info_grep_chassis_state","")

def asr5000_show_hd_raid_grep_degrad(output,response):
    resp = asr5000_obj.show_hd_raid_grep_degrade()#output.split("\n")
    response["show_hd_raid_grep_degrad"] = resp.get("show_hd_raid_grep_degrade", "")

def asr5000_show_context(output,response):
    resp = asr5000_obj.extract_show_context()#output.split("\n")
    response["show_context"] = resp

def asr5000_show_service_all(output,response):
    resp = asr5000_obj.extract_show_service_all()#output.split("\n")
    response["show_service_all"] = resp

def asr5000_show_card_hardware_grep_prog(output,response):
    resp = asr5000_obj.extract_show_card_hardware_grep_prog()#output.split("\n")
    response["show_card_hardware_grep_prog"] = resp

def asr5000_show_card_info_grep_card_lock(output,response):
    resp = asr5000_obj.extract_show_card_info_grep_card_lock()#output.split("\n")
    response["show_card_info_grep_card_lock"] = resp

def asr5000_session_recovery_status_verbose(output,response):
    resp = asr5000_obj.extract_show_session_recovery_status_verbose()#output.split("\n")
    response["show_session_recovery_status_verbose"] = resp

def asr5000_show_resource_grep_license(output,response):
    resp = asr5000_obj.extract_show_resource_grep_license()#output.split("\n")
    response["show_resource_grep_license"] = resp

def asr5000_show_license_info_grep_license_status(output,response):
    resp = asr5000_obj.extract_show_license_info_grep_license_status()  # output.split("\n")
    response["show_license_info_grep_license_status"] = resp

def asr5000_show_srp_checkpoint_statistics_grep_sessmgrs(output,response):
    resp = asr5000_obj.extract_show_srp_checkpoint_statistics_grep_sessmgrs()  # output.split("\n")
    response["show_srp_checkpoint_statistics_grep_sessmgrs("] = resp

def asr5000_show_srp_info(output,response):
    resp = asr5000_obj.extract_show_srp_info()  # output.split("\n")
    response["show_srp_info"] = resp

def asr5000_show_card_table_grep_act_stdby(output,response):
    resp = asr5000_obj.extract_show_card_table_grep()  # output.split("\n")
    response["show_card_table_grep"] = resp

def asr5000_show_diameter_peers_full_grep_total_peers(output,response):
    resp = asr5000_obj.extract_show_diameter_peers()  # output.split("\n")
    response["show_diameter_peers"] = resp

def asr5000_show_crash_list(output,response):
    resp = asr5000_obj.extract_show_crash_list()  # output.split("\n")
    response["show_crash_list"] = resp

def asr5000_show_rct_stats(output,response):
    resp = asr5000_obj.extract_show_rct_status()  # output.split("\n")
    response["show_rct_status"] = resp

def asr5000_show_task_resources_grep_diamproxy(output,response):
    resp = asr5000_obj.extract_show_task_diamproxy()  # output.split("\n")
    response["show_task_resources_grep_diamproxy"] = resp

def asr5000_show_task_resources_grep_sessmg(output,response):
    resp = asr5000_obj.extract_show_task_sessmg()  # output.split("\n")
    response["show_task_resources_grep_sessmg"] = resp

def asr5000_show_task_resources_grep_v_good(output,response):
    resp = asr5000_obj.extract_show_task_resource_grep_v_good()
    response['show_task_resource_grep_v_good'] = resp

def asr5000_show_alarm_outstanding(output,response):
    resp = asr5000_obj.extract_show_alarm_outstanding()
    response['show_alarm_outstanding'] = resp


# Using Switch to compare which command is parsing
# Using Switch to compare which command is parsing
switch = {  "ios":{         "show processes cpu":show_process_cpu,
                            "show version": show_version,
                            "show version | i Config": show_version_i_config,
                            "show environment": show_environment,
                            "show buffers": show_buffers,
                            "show platform":show_platform,
                            "show interfaces":show_interfaces,
                            "show memory statistics":show_memory_statistics,
                            "show ip interface brief":show_ip_interface_brief,
                            "show bfd neighbor":show_bfd_neighbor,
                            "show mpls ldp neighbor":show_mpls_ldp_neighbor,
                            "show mpls interfaces":show_mpls_interfaces,
                            "show running-config | i boot":show_running_config_i_boot,
                            "show ip bgp vpnv6 unicast vrf LTE": show_ip_bgp_v6_vrf_lte,
                            "show ip bgp vpnv4 vrf 1XRTT":show_ip_bgp_v4_vrf_1xrtt,
                            "show ip bgp vpnv4 vrf RAN":show_ip_bgp_v4_ran,
                            "show ip bgp vpnv4 vrf CELL_MGMT":show_ip_bgp_v4_cell_mgmt,
                            "show xconnect all":show_xconnect_all,
                            "show ip bgp vnpv4 all summary": bgp_v4_neighbour,
                            "show ip bgp vpnv6 unicast all summary": bgp_v6_neighbour,
                            "show logging":show_logging},
            "asr5000":{     "show clock":asr5000_show_clock,
                            "show system uptime":asr5000_show_system_uptime,
                            'show version | grep "Image Version"':asr5000_show_version_grep_img_ver,
                            'show srp info | grep "Chassis State"':asr5000_show_srp_info_grep_chassis_state,
                            'show hd raid | grep "Degrad"':asr5000_show_hd_raid_grep_degrad,
                            'show context':asr5000_show_context,
                            'show service all':asr5000_show_service_all,
                            'show card hardware | grep Prog':asr5000_show_card_hardware_grep_prog,
                            'show card info | grep "Card Lock"':asr5000_show_card_info_grep_card_lock,
                            'show session recovery status verbose':asr5000_session_recovery_status_verbose,
                            'show resource | grep License':asr5000_show_resource_grep_license,
                            'show license info | grep "License Status"':asr5000_show_license_info_grep_license_status,
                            'show srp checkpoint statistics | grep Sessmgrs':asr5000_show_srp_checkpoint_statistics_grep_sessmgrs,
                            'show srp info':asr5000_show_srp_info,
                            'show card table | grep -E -v "Active|Standby|None"':asr5000_show_card_table_grep_act_stdby,
                            'show diameter peers full | grep "Total peers"':asr5000_show_diameter_peers_full_grep_total_peers,
                            'show crash list':asr5000_show_crash_list,
                            'show rct stats':asr5000_show_rct_stats,
                            'show task resources | grep diamproxy':asr5000_show_task_resources_grep_diamproxy,
                            'show task resources | grep sessmg':asr5000_show_task_resources_grep_sessmg,
                            'show task resources | grep -v good':asr5000_show_task_resources_grep_v_good,
                            'show alarm outstanding':asr5000_show_alarm_outstanding
          }
        }
#---------------------------------------


# Get the node's list and pass the details to SSH for the given User_id
def perform_hc(device_type,device_id):
    switch_mapper = switch.get(device_type,None)
    if switch_mapper:
        nlist = get_node(device_id,device_type)
        if nlist:
            return ssh_post(nlist,switch_mapper,device_type)
    return {}
#----------------------------------------

def perform_hc_full(device_type,device_id,command):
    switch_mapper = switch.get(device_type,None)
    nlist = get_node(device_id,device_type)
    nlist['devices'][0]['command']= [command.replace('-',' ')]#replace with demlimiter in the url
    if nlist:
        return [{command: ssh_post(nlist,switch_mapper,device_type,raw_=True)}]
    return {}


# Using the SSH Function
def ssh_post(data,switch_mapper,logic,raw_=False):
    # Using device details to execute HealthCheck's for each device from Device's list
    devices = data.get("devices")
    for device in devices:
        response = {}
        #start=time.time()
        ip_addr = device.get('ip_addr')
        commands = device.get('command')
        username = device.get('username')
        password = device.get('password')
        session = paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        session.connect(ip_addr, username=username, password=password)
        connection = session.invoke_shell()
        time_dict = {}
        # From commands list each command is passed to the SSH Shell terminal
        if ip_addr:
            if commands:
                   and in commands:
                    start = time.time()
                    connection.send("terminal length 0")
                    connection.send("\n")
                    message = command #" ".join(command.split("-"))
                    connection.send(message)
                    connection.send("\n")
                    time.sleep(0.6)
                    output = connection.recv(65535)
                    if raw_:
                        return output.replace('\r\n','<br>')

                    if( logic == 'ios'):
                        m = re.search(PING_COMMAND_2000,message)
                        if m:
                            resp = dextractor.extract_2000_5000(message)
                            twothsndbyteping = {"twothsndbyteping":"success rate = %s"%(resp.get("sucess",""),)}
                            response.update(twothsndbyteping)

                        m = re.search(PING_COMMAND_5000, message)
                        if m:
                            resp = dextractor.extract_2000_5000(message)
                            fivethsndbyteping = {"fivethsndbyteping": "success rate = %s" % (resp.get("sucess", ""),)}
                            response.update(fivethsndbyteping)

                    sw_func = switch_mapper.get(message,None)
                    if sw_func:
                        sw_func(output,response)
                    end=time.time()
                    time_dict[message] = end-start

    return response

healthcheck = connexion.App(__name__)
healthcheck.add_api('healthcheck.yaml')

#application = app.app
if __name__ == '__main__':
    healthcheck.run(port=8080)
