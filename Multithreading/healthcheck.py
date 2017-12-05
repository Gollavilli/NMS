 # Importing necessary libraries
import time
import paramiko
import connexion
import re
from multiprocessing import Process, Manager

# from paramiko.ssh_exception import NoValidConnectionsError

from hcparser import dextractor
from userdevices import get_node
from asr5000 import asr5000_obj

# Turning on debug - to be removed later
DEBUG = True
SESSION = None

PING_COMMAND_2000 = r'ping (.+?) size 2000'
PING_COMMAND_5000 = r'ping (.+?) size 5000'


version_string = None

from ios_checks import *
from asr5000_checks import *
from paramiko.ssh_exception import AuthenticationException
from socket import error as Serror
import json

from Queue import Queue
from threading import Thread


# Using Switch to compare which command is parsing
# Using Switch to compare which command is parsing
switch = {"ios": {"show processes cpu": show_process_cpu,
                  "show version": show_version,
                  "show version | i Config": show_version_i_config,
                  "show environment": show_environment,
                  "show buffers": show_buffers,
                  "show platform": show_platform,
                  "show interfaces": show_interfaces,
                  "show memory statistics": show_memory_statistics,
                  "show ip interface brief": show_ip_interface_brief,
                  "show bfd neighbor": show_bfd_neighbor,
                  "show mpls ldp neighbor": show_mpls_ldp_neighbor,
                  "show mpls interfaces": show_mpls_interfaces,
                  "show ip bgp vpnv4 all summary": bgp_v4_neighbour,
                  "show ip bgp vpnv6 unicast all summary": bgp_v6_neighbour,
                  "show logging": show_logging,
                  "show running-config | i boot": show_running_config_i_boot,
                  "show ip bgp vpnv6 unicast vrf LTE": show_ip_bgp_v6_vrf_lte,
                  "show ip bgp vpnv4 vrf 1XRTT": show_ip_bgp_v4_vrf_1xrtt,
                  "show ip bgp vpnv4 vrf RAN": show_ip_bgp_v4_ran,
                  "show xconnect all": show_xconnect_all,
                  "show ip bgp vpnv4 vrf CELL_MGMT": show_ip_bgp_v4_cell_mgmt,
                  "show inventory": show_inventory,
                  "show ping":show_ping     },
          "xos": {"show clock": asr5000_show_clock,
                  "show system uptime": asr5000_show_system_uptime,
                  'show version | grep "Image Version"': asr5000_show_version_grep_img_ver,
                  'show srp info | grep "Chassis State"': asr5000_show_srp_info_grep_chassis_state,
                  'show hd raid | grep "Degrad"': asr5000_show_hd_raid_grep_degrad,
                  'show context': asr5000_show_context,
                  'show service all': asr5000_show_service_all,
                  'show card hardware | grep Prog': asr5000_show_card_hardware_grep_prog,
                  'show card info | grep "Card Lock"': asr5000_show_card_info_grep_card_lock,
                  'show session recovery status verbose': asr5000_session_recovery_status_verbose,
                  'show resource | grep License': asr5000_show_resource_grep_license,
                  'show license info | grep "License Status"': asr5000_show_license_info_grep_license_status,
                  'show srp checkpoint statistics | grep Sessmgrs': asr5000_show_srp_checkpoint_statistics_grep_sessmgrs,
                  'show srp info': asr5000_show_srp_info,
                  'show card table | grep -E -v "Active|Standby|None"': asr5000_show_card_table_grep_act_stdby,
                  'show diameter peers full | grep "Total peers"': asr5000_show_diameter_peers_full_grep_total_peers,
                  'show crash list': asr5000_show_crash_list,
                  'show rct stats': asr5000_show_rct_stats,
                  'show task resources | grep diamproxy': asr5000_show_task_resources_grep_diamproxy,
                  'show task resources | grep sessmg': asr5000_show_task_resources_grep_sessmg,
                  'show task resources | grep -v good': asr5000_show_task_resources_grep_v_good,
                  'show alarm outstanding': asr5000_show_alarm_outstanding
                  }
          }

switch_numeric = {"ios": {1: "show processes cpu",
                          2: "show version",
                          3: "show version | i Config",
                          4: "show environment",
                          5: "show buffers",
                          6: "show platform",
                          7: "show interfaces",
                          8: "show memory statistics",
                          9: "show ip interface brief",
                          10: "show bfd neighbor",
                          11: "show mpls ldp neighbor",
                          12: "show mpls interfaces",
                          13: "show ip bgp vpnv4 all summary",
                          14: "show ip bgp vpnv6 unicast all summary",
                          15: "show logging",
                          16: "show running-config | i boot",
                          17: "show ip bgp vpnv6 unicast vrf LTE",
                          18: "show ip bgp vpnv4 vrf 1XRTT",
                          19: "show ip bgp vpnv4 vrf RAN",
                          20: "show xconnect all",
                          21: "show ip bgp vpnv4 vrf CELL_MGMT",
                          22: "show ping"
                          },

                  "xos": {1: "show clock",
                          2: "show system uptime",
                          3: 'show version | grep "Image Version"',
                          4: 'show srp info | grep "Chassis State"',
                          5: 'show hd raid | grep "Degrad"',
                          6: 'show context',
                          7: 'show service all',
                          8: 'show card hardware | grep Prog',
                          9: 'show card info | grep "Card Lock"',
                          10: 'show session recovery status verbose',
                          11: 'show resource | grep License',
                          12: 'show license info | grep "License Status"',
                          13: 'show srp checkpoint statistics | grep Sessmgrs',
                          14: 'show srp info',
                          15: 'show card table | grep -E -v "Active|Standby|None"',
                          16: 'show diameter peers full | grep "Total peers"',
                          17: 'show crash list',
                          18: 'show rct stats',
                          19: 'show task resources | grep diamproxy',
                          20: 'show task resources | grep sessmg',
                          21: 'show task resources | grep -v good',
                          22: 'show alarm outstanding'
                          }
                  }


# ---------------------------------------

class ThreadWorker(Thread):
   def __init__(self, queue):
       Thread.__init__(self)
       self.queue = queue

   def run(self):
       while True:
           # Get the work from the queue and expand the tuple
           output, response, sw_func = self.queue.get()
           sw_func(output, response)
           self.queue.task_done()


# Get the node's list and pass the details to SSH for the given User_id
def perform_hc(device_type, device_id):
    switch_mapper = switch.get(device_type, None)
    if switch_mapper:
        nlist = get_node(device_id, device_type)
        if nlist:
            return ssh_post(nlist, switch_mapper, device_type)
    return {}


# ----------------------------------------

def perform_hc_full(device_type, device_id, command):
    switch_mapper = switch.get(device_type, None)
    nlist = get_node(device_id, device_type)
    command_string = switch_numeric.get(device_type, '').get(int(command), '')
    if command_string:
        nlist['devices'][0]['command'] = [command_string]
        if nlist:
            return [{command_string: ssh_post(nlist, switch_mapper, device_type, raw_=True)}]
    return {}


# Using the SSH Function
def ssh_post(data, switch_mapper, logic, raw_=False):
    # try:
    global SESSION
    # Using device details to execute HealthCheck's for each device from Device's list
    response = {}

    # 4-ThreadWorkers initialized
    queue = Queue()
    for x in range(4):
        worker = ThreadWorker(queue)
        worker.daemon = True
        worker.start()

    devices = data.get("devices")
    for device in devices:
        
        # start=time.time()
        ip_addr = device.get('ip_addr')
        commands = device.get('command')
        username = device.get('username')
        password = device.get('password')
        session = paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            session.connect(ip_addr, username=username, password=password)
        except (AuthenticationException, Serror) as e:
            if e.message:
                return {"error": True, "message": "[x] ERROR: " + e.message}
            else:
                return {"error": True, "message": "[x] ERROR: " + e.strerror}
        except (NoValidConnectionsError) as err:
            if err:
                return {"error": True, "Message": err}
        connection = session.invoke_shell()
        SESSION = connection
        time_dict = {}
        # From commands list each command is passed to the SSH Shell terminal
        if ip_addr:
            if commands:
                grouped_commands = None
                for index, command in enumerate(commands):
                    if type(command) == dict:
                        grouped_commands = commands.pop(index)
                    else:
                        start = time.time()
                        connection.send("terminal length 0")
                        connection.send("\n")
                        message = command
                        connection.send(message)
                        connection.send("\n")
                        time.sleep(1.0)
                        output = connection.recv(65535)
                        sw_func = switch_mapper.get(message, None)
                        if raw_:
                            if message == "show ping":
                                if sw_func:
                                    return sw_func(None,None,_raw=True)
                            return output.replace('\r\n', '<br>')

                        if sw_func:
                            #sw_func(output, response)
                            queue.put((output, response, sw_func))
                        end = time.time()
                        time_dict[message] = end - start

                if grouped_commands:
                    grouped_commands = grouped_commands.get('grouped')
                    for group in grouped_commands:
                        resp = {}
                        start = time.time()
                        for command in grouped_commands[group]:
                            connection.send("terminal length 0")
                            connection.send("\n")
                            message = command  # " ".join(command.split("-"))
                            connection.send(message)
                            connection.send("\n")
                            time.sleep(1.0)
                            output = connection.recv(65535)
                            sw_func = switch_mapper.get(message, None)
                            if sw_func:
                                #sw_func(output, resp)
                                queue.put((output, response, sw_func))
                        end = time.time()
                        time_dict[group] = end - start
                        response[group] = resp
    queue.join()
    return response
    # except NoValidConnectionsError as err:
    # return {"message": "connection failed"}


healthcheck = connexion.App(__name__)
healthcheck.add_api('healthcheck.yaml')

# application = app.app
if __name__ == '__main__':
    healthcheck.run(port=8080)
