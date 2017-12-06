from healthcheck import SESSION
# Displaying the Format Structure from end point of view

# Checks the Configuration Register
def show_version_i_config(output, response):
    value = dextractor.check_version_i_config()#output.split("\n")
    config_ = value.get("configuration", "")
    R = value.get('R', 1)
    response["configregister"] = {"message": "configuration register = %s" % (config_,), "R": R}


# Checks the Version for the device
def show_version(output, response):
    global version_string
    version_string = dextractor.extract_version(output.split("\n"))
    R = version_string.get('R', 1)
    response[  "iosversion"] = {"message": version_string.get("version", ""), "R": R}


# Checks the CPU Utilization for the device
def show_process_cpu(output, response):
    resp = dextractor.extract_utilization(output)
    one_second = resp.get("five_seconds", "")
    one_minute = resp.get("one_minute", "")
    five_minutes = resp.get("five_minutes", "")
    R= resp.get('R',1)
    cpu_utilization = "1s = %s; 1m = %s; 5m= %s" % (one_second, one_minute, five_minutes)
    response["cpuutilization"]={"message":cpu_utilization ,"R":R}
    #response.update(cpu_utilization)


# Checks the Environment and the following alarm's for the device
def show_environment(output, response):
    total_alarms = dextractor.extract_alarms()#output.split("\n")
    total_num = total_alarms.get("total_alarms", "")
    R = total_alarms.get('R', 1)
    response["environmental"] = {"message": "Total alarms = %s" % (total_num,), "R": R}


def show_logging(output, response):
    resp = dextractor.extract_show_logging(output.split("\n"))  # output.split("\n")
    if resp:
        response["logentries"] = resp


# Checks the Buffers and looks for any Misses in each Buffer Module
def show_buffers(output, response):
    total_buffer = 0
    buffers = dextractor.extract_buffers(output.split("\n"))
    for key in buffers:
        total_buffer += int(buffers[key])
    R = buffers.get('R', 1)
    response["buffers"] = {"message": "Max Buffer misses = %s" % (str(total_buffer),), "R": R}


# Checks the Platform and specifies every slot is OK or not.
def show_platform(output, response):
    not_ok_count = 0
    devices = dextractor.extract_show_platform(output.split("\n"))  # output.split("\n")
    if devices.has_key('R'):
        R = devices.pop('R')
    else:
        R = 1
    for key in devices:
        if "ok" not in devices[key]:
            not_ok_count += 1
    response["platform"] = {"message": "not ok slots = %s" % (str(not_ok_count),), "R": R}


# Checks the Interface Counter's Count
def show_interfaces(output, response):
    value = dextractor.count_interfaces(output.split("\n"))
    val_ = value.get("count_interfaces", "")
    R = value.get('R', 1)
    response["interfacecounters"] = {"count": val_, "R": R}


# Checks the Memory available at the Device
def show_memory_statistics(output, response):
    value = dextractor.extract_memory_statistics()  # output.split("\n")
    R = value.get('R', 1)
    free_mem = "Free memory = %s" % (value.get("Free(b)", ""))
    response["freememory"] = {"message": free_mem, "R": R}


# Checks the Interface states and looks for status of the device
def show_ip_interface_brief(output, response):
    resp = dextractor.extract_show_brief(output.split("\n"))
    down_devices = 0
    if resp.has_key('R'):
        R = resp.pop('R')
    else:
        R = 1
    for key in resp:
        value = resp[key].lower()
        if not (value == "up"):
            down_devices += 1
    response["interfacestates"] = {"message": "up neighbors = %s" % (str(down_devices),), "R": R}


# Checks the BFD's Sessions for the all the neighbors associated to the device
def show_bfd_neighbor(output, response):
    down_neighbours = 0
    resp = dextractor.extract_bfd_neighbour(output.split("\n"))  # output.split("\n")
    if resp.has_key('R'):
        R = resp.pop('R')
    else:
        R = 1
    for key in resp:
        up_down = resp[key]
        if not (up_down == "Up"):
            down_neighbours += 1
    response["bfdsession"] = {"message": "down neighbors = %s" % (down_neighbours,), "R": R}


# Checks the MPLS Neighbor's for the device and their associated IP_addresses.
def show_mpls_ldp_neighbor(output, response):
    resp = dextractor.extract_mlps_ldp_neighbour(output.split("\n"))  # output.split("\n")
    R = resp.get('R', 1)
    response["mplsneighbors"] = {"message": "mpls ldp neighbors = %s" % (resp.get("count", ""),), "R": R}


# Checks the MPLS states for the given device.
def show_mpls_interfaces(output, response):
    resp = dextractor.extract_mlps_interfaces(output.split("\n"))  # output.split("\n")
    devices_down = 0
    if resp.has_key('R'):
        R = resp.pop('R')
    else:
        R = 1
    for key in resp:
        device = resp[key]
        ip = device.get("ip", "")
        operational = device.get("operational", "")
        if (ip and operational):
            if not (((ip == "Yes") or (ip == "Yes(ldp)")) and (operational == "Yes")):
                devices_down += 1
    response["mplsinterfaces"] = {"message": "count of failed interfaces = %s" % (str(devices_down),), "R": R}


# Checks for the given device version matches the specified boot statement.
def show_running_config_i_boot(output, response):
    global version_string
    R = 1
    flag = dextractor.extract_show_running_config(output.split("\n"), version_to_search=version_string).get(
        "type_match", False)
    if flag:
        statement = "Boot statement matches Version"
        R = 0
    else:
        statement = "Boot statement does not matches Version"
    response["bootstatement"] = {"message": statement, "R": R}


# Checks the count for BGPv6 Routes
def show_ip_bgp_v6_vrf_lte(output, response):
    ifaces = dextractor.extract_bgpv6_routes()  # output.split("\n")
    cnt = None
    if ifaces.has_key('R'):
        R = ifaces.pop('R')
    else:
        R = 1
    if ifaces.keys():
        cnt = len(ifaces.keys())
    response["bgpvsixroutes"] = {"count": cnt, "R": R}


# Checks the BGPv4 Routes for the device
def show_ip_bgp_v4_vrf_1xrtt(output, response):
    ifaces = dextractor.extract_bgpv4_1xrtt()  # output.split("\n")
    cnt = None
    if ifaces.has_key('R'):
        R = ifaces.pop('R')
    else:
        R = 1
    if ifaces.keys():
        cnt = len(ifaces.keys())
    response["1xrtt"] = {"count": cnt, "R": R}


# Checks the BGPv4 Routes for the device
def show_ip_bgp_v4_ran(output, response):
    ifaces = dextractor.extract_bgpv4_ran()  # output.split("\n")
    cnt = None
    if ifaces.has_key('R'):
        R = ifaces.pop('R')
    else:
        R = 1
    if ifaces.keys():
        cnt = len(ifaces.keys())
    response["ran"] = {"count": cnt, "R": R}


# Checks the BGPv4 Routes for the device
def show_ip_bgp_v4_cell_mgmt(output, response):
    ifaces = dextractor.extract_bgpv4_cell_mgmt()  # output.split("\n")
    cnt = None
    if ifaces.has_key('R'):
        R = ifaces.pop('R')
    else:
        R = 1
    if ifaces.keys():
        cnt = len(ifaces.keys())
    response["cell_mgmt"] = {"count": cnt, "R": R}


def show_xconnect_all(output, response):
    resp = dextractor.xconect_all(output.split("\n"))
    response["xconnect"] = resp


def bgp_v4_neighbour(output, response):
    resp = dextractor.bgpv4_neighbour(output.split("\n"))  #
    response["bgpvfourneighbors"] = resp


def bgp_v6_neighbour(output, response):
    resp = dextractor.bgpv6_neighbour(output.split("\n"))
    response["bgpvsixneighbours"] = resp


def show_inventory(output, response):
    global SESSION
    if SESSION:
        connection = SESSION
        dextractor.extract_show_inventory(output.split("\n"))  # output.split("\n")
        dextractor.form_command_idprom_detail()
        map_dict = {}
        for cmd in dextractor.IDPROM_DETAIL:
            connection.send("terminal length 0")
            connection.send("\n")
            connection.send(cmd)
            connection.send("\n")
            time.sleep(1.0)
            output_intermediate = connection.recv(65535)
            result = dextractor.extract_idprom_details(query=cmd)  # output_intermediate.split("\n")
            if True:
                map_dict[cmd] = result
        for cmd in dextractor.STATUS:
            connection.send("terminal length 0")
            connection.send("\n")
            connection.send(cmd)
            connection.send("\n")
            time.sleep(1.0)
            iresp = {cmd: {}}
            output_intermediate = connection.recv(65535)
            result = dextractor.extract_tranciever_status(query=cmd)  # output_intermediate.split("\n")
            if result:
                key_to_check = cmd.replace('status', 'idprom detail')
                if map_dict.has_key(key_to_check):
                    data = map_dict.get(key_to_check, None)
                    if data:
                        resp = dextractor.temperature_range_check(data, result)
                        if resp:
                            iresp[cmd].update(resp)
                        resp = dextractor.supply_voltage_range_check(data, result)
                        if resp:
                            iresp[cmd].update(resp)
                        resp = dextractor.tx_power(data, result)
                        if resp:
                            iresp[cmd].update(resp)
                        resp = dextractor.rx_power(data, result)
                        if resp:
                            iresp[cmd].update(resp)
            response.update(iresp)

def show_ping(output,response,_raw=False):
    global SESSION
    connection = SESSION
    if not _raw :
        commands = dextractor.ping_extract()#output.split("\n")
    raw_output = {}
    for command in commands:
        if commands[command]:
            for cmd in commands[command]:
                message = cmd
                connection.send("terminal length 0")
                connection.send("\n")
                connection.send(cmd)
                connection.send("\n")
                time.sleep(1.0)
                output_intermediate = connection.recv(65535)
                if _raw:
                    raw_output[message] = output_intermediate.replace('\r\n', '<br>')

                resp = dextractor.extract_2000_5000(cmd)#output_intermediate.split("\n")
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
    if _raw:
        return raw_output