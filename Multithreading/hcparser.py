import re
from quantulum import parser
from check_limits import config as limit_config

CONFIG_KEY_IOS = 'ios'

class DataExractor:

    SHOW_LOGGING_TEMPLATE 		= r'show logging'
    BUFFER_LOGGING_TEMPLATE 	= r'Buffer logging: level debugging, (.+?) messages logged, xml disabled,'
    TRAP_LOGGING_TEMPLATE		= r'Trap logging: level informational, (.+?) message lines logged'
    SHOW_LDP_NEIGHBOUR_TEMPLATE = r'show mpls ldp neighbor'
    PEER_LDP_TEMPLATE			= r'Peer LDP Ident'
    SHOW_MLPS_TEMPLATE 			= r'show mpls interfaces'
    SHOW_MLPS_START_TEMPLATE	= r'Interface IP Tunnel BGP Static Operational'
    SHOW_BRIEF_TEMPLATE 		= r'show ip int brief'
    SHOW_BRIEF_START_TEMPLATE	= r'Interface IP-Address OK? Method Status Protocol'
    SHOW_BFD_NEIGHBOUR_TEMPLATE	= r'show bfd neighbor'
    SHOW_BFD_NEIGHBOUR_START_TEMPLATE = r'NeighAddr LD/RD RH/RS State Int'
    SHOW_PLATFORM_TEMPLATE	= r'show platform'
    SHOW_PLATFORM_END_TEMPLATE = r'Slot CPLD Version Firmware Version'
    SHOW_RUNNING_CONFIG_TEMPLATE	= r'show running-config | i boot'
    SHOW_VERSION_TEMPLATE 	= r'show version'
    SHOW_VERSION_I_CONFIG_TEMPLATE 	= r'show version | i Config'
    SHOW_VERSION_NUMBER_TEMPLATE = r'Version (.+?), RELEASE SOFTWARE (.+?)'
    SHOW_VERSION_CONFIG_TEMPLATE = r'0x[0-9A-F]+'
    SHOW_VERSION_TYPE_TEMPLATE	= r'(.+?) ((.+?)) processor ((.+?)) with (.+?)/(.+?) bytes of memory.'
    UTILIZATION_TEMPLATE 	= r'CPU utilization for five seconds: (.+?)/(.+?); one minute: (.+?); five minutes: (.+?)'
    MISSES_TEMPLATE			= r'(.+?) hits, (.+?) misses, (.+?) trims, (.+?) created'
    CRITICAL_ALARM_TEMPLATE = r'Number of Critical alarms:  (.+?)'
    MAJOR_ALARM_TEMPLATE 	= r'Number of Major alarms:     (.+?)'
    MINOR_ALARM_TEMPLATE 	= r'Number of Minor alarms:     (.+?)'
    MEMORY_STATISTICS_TEMPLATE 	= r'(.+?)show memory statistics'
    SHOW_BUFFERS_TEMPLATE 		= r'(.+?)show buffers'
    SHOW_BUFFERS_MISS_TEMPLATE_A 	= r'(.+?) hits, (.+?) misses, (.+?) created'
    SHOW_BUFFERS_MISS_TEMPLATE_B 	= r'(.+?) hits, (.+?) misses, (.+?) trims, (.+?) created'
    SHOW_BUFFERS_MISS_TEMPLATE_C 	= r'(.+?) hits in cache, (.+?) misses in cache'
    SHOW_INTERFACES_TEMPLATE 		= r'show interfaces'
    COUNT_INTERFACES_TEMPLATE 		= r'(.+?) is (.+?), line protocol is (.+?)'
    SUCCESS_RATE_TEMPLATE 			= r'Success rate is (.+?) percent (.+?), round-trip min/avg/max = (.+?) ms'
    SHOW_BGPV6_ROUTES 				= r'show ip bgp vpnv6 unicast vrf LTE'
    BGPV6_ROUTES_TEMPLATE_A 		= r'(.+?)::(.+?) ::(.+?):(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    BGPV6_ROUTES_TEMPLATE_B 		= r'(.+?) ::(.+?):(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    SHOW_BGPV4_1XRTT 				= r'show ip bgp vpnv4 vrf 1XRTT'
    SHOW_BGPV4_RAN 					= r'show ip bgp vpnv4 vrf RAN'
    SHOW_BGPV4_CELL_MGMT 			= r'show ip bgp vpnv4 vrf CELL_MGMT'
    SHOW_XCONNECT_ALL = r'show xconnect all'
    SHOW_INTERFACES_THRESHOLD 		= 1
    SHOW_LOGGING_THRESHOLD 			= 1
    XCONNECT_FILTER_TEMPLATE = r'(.+?)=(.+?) (.+?)=(.+?) (.+?)=(.+?) (.+?)=(.+?)'
    BGPV4_NEIGHBOURS = r'show ip bgp vpnv4 all summary'
    BGPV6_NEIGHBOURS = r'show ip bgp vpnv6 unicast all summary'
    BGPVN_NEIGHBOURS_TEMPLATE = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) (.+?) (.+?) (.+?) (.+?) (.+?) (.+?) (.+?) (.+?)'
    SHOW_INVENTORY = r'show inventory'
    TRANCIEVER_TEMPLATE = r'subslot (.\d{0,3})/(.\d{0,3}) transceiver (.\d{0,3})'
    TRANCIEVER_RETURN_TEMPLATE = 'subslot %s/%s transceiver %s'

    IDPROM_DETAIL = None
    STATUS = None

    def index_processor(self,Q,P):
        indexes = []
        index_to_use = None
        for idx,line in enumerate(P):
            if Q in line:
                indexes.append([idx,line])

        for match in indexes:
            string = match[-1]
            index = match[0]

            test_mts = string.replace(Q,'').replace('\r\n','').strip().split('#')
            if len(test_mts)==2:
                if test_mts[-1] == '':
                    index_to_use =  index
                    break
        return index_to_use

    def segment_extract(self,SEGMENT,string_to_search):
        # Fetch only section lines
        regex = re.compile(SEGMENT)
        line_data = []
        found = False
        first_occurence = True
        for line in string_to_search:
            if regex.search(line) or found:
                found = True
                if not first_occurence:
                    if(line.find("#") != -1 ):
                        break
                    else:
                        line_x = line.strip()
                        line_x = " ".join(line_x.split())
                        line_data.append(line_x)
                first_occurence = False
        return line_data

    def extract_2000_5000(self, command, string_to_search=open('hc.txt').readlines()):
        line_data = self.segment_extract(command, string_to_search)
        return_dict = {"sucess": None}
        result = 1
        for line in line_data:
            m = re.search(DataExractor.SUCCESS_RATE_TEMPLATE, line)
            if m:
                return_dict["sucess"] = m.group(2)
                result = 0

        return_dict.update({'R':result})
        return return_dict

    def count_interfaces(self, string_to_search=open('hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.SHOW_INTERFACES_TEMPLATE, string_to_search)
        cleaned_data = "\n".join(_ for _ in line_data)
        m = re.findall(DataExractor.COUNT_INTERFACES_TEMPLATE, cleaned_data)
        if m:
        	if len(m) >= limit_config.get(CONFIG_KEY_IOS,'SHOW_INTERFACES_THRESHOLD'):
        		return {"count_interfaces":len(m),'R':0}
        	else:
        		return {"count_interfaces":len(m),'R':1}
        return {"count_interfaces":None,'R':1}

    def extract_show_logging(self,string_to_search= open('hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.SHOW_LOGGING_TEMPLATE,string_to_search)
        return_dict = {}
        for line in line_data:
            if line:
            	m = re.search(DataExractor.BUFFER_LOGGING_TEMPLATE,line)
                if m:
                	buffer_logging_count = int(m.group(1))
                	if buffer_logging_count < limit_config.get(CONFIG_KEY_IOS,'SHOW_LOGGING_THRESHOLD'):
                		return_dict["buffer_logging"] = {'value':buffer_logging_count,'R':0}
                	else:
                		return_dict["buffer_logging"] = {'value':buffer_logging_count,'R':1}
            	m = re.search(DataExractor.TRAP_LOGGING_TEMPLATE,line)
                if m:
                	trap_logging_count = int(m.group(1))
                	if trap_logging_count < limit_config.get(CONFIG_KEY_IOS,'SHOW_LOGGING_THRESHOLD'):
                		return_dict["trap_logging"] = {'value':trap_logging_count,'R':0}
                	else:
                		return_dict["trap_logging"] = {'value':trap_logging_count,'R':1}
        return return_dict



    def extract_mlps_ldp_neighbour(self,string_to_search= open('hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.SHOW_LDP_NEIGHBOUR_TEMPLATE,string_to_search)
        count = 0
        result = 1
        for line in line_data:
            if line:
                if DataExractor.PEER_LDP_TEMPLATE in line:
                    count += 1
                    result = 0
        return {"count": count,"R":result}


    def extract_mlps_interfaces(self,string_to_search= open('hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.SHOW_MLPS_TEMPLATE,string_to_search)
        start = False
        return_dict = {}
        id_index = None
        operational_index = None
        cleaned_lines = []
        for idx,line in enumerate(line_data):
            tindex = 0
            sp_line = line.split()
            for token in sp_line:
                if token == "(ldp)":
                    sp_line[tindex-1] += sp_line[tindex]
                    del sp_line[tindex]
                tindex += 1
            cleaned_lines.append(" ".join(_ for _ in sp_line))

        for line in cleaned_lines:
            if start:
                if line:
                    device 		= line.split()[0]
                    ip_status 	= line.split()[id_index]
                    operational_status = line.split()[operational_index]
                    return_dict[device] = {"ip":ip_status, "operational":operational_status}
            if line == DataExractor.SHOW_MLPS_START_TEMPLATE:
                for idx,label in enumerate(line.split()):
                    if label == "IP":
                        id_index = idx
                    if label == "Operational":
                        operational_index = idx
                start = True
        if len(return_dict.keys()) >= limit_config.get(CONFIG_KEY_IOS,'SHOW_MLPS_INTERFACES'):
        	return_dict.update({'R':0})
        else:
        	return_dict.update({'R':1})
        return return_dict

    def extract_show_brief(self,string_to_search= open('hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.SHOW_BRIEF_TEMPLATE,string_to_search)
        start = False
        return_dict = {}
        result = 0
        for line in line_data:
            if start:
                if line:
                    if 'down' in line:
                        result = 1
                    device = line.split()[0]
                    status = line.split()[4]
                    if status == "administratively":
                        status += " " + line.split()[5]
                    return_dict[device] = status
            if line == DataExractor.SHOW_BRIEF_START_TEMPLATE:
                start = True
        return_dict.update({'R':result})
        return return_dict

    def extract_bfd_neighbour(self,string_to_search= open('hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.SHOW_BFD_NEIGHBOUR_TEMPLATE,string_to_search)
        start = False
        return_dict = {}
        result = 0
        for line in line_data:
            if start:
                if line:
                    addr = line.split()[0]
                    state = line.split()[3]
                    return_dict[addr] = state
                    if 'down' in state.lower():
                    	result = 1
            if line == DataExractor.SHOW_BFD_NEIGHBOUR_START_TEMPLATE:
                start = True

        return_dict.update({'R':result})
        return return_dict



    def extract_show_platform(self,string_to_search= open('hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.SHOW_PLATFORM_TEMPLATE,string_to_search)
        start_label = "---------------------"
        start = False
        cleaned_data = []
        for line in line_data:
            if line and len(line.split())>2:
                if start:
                    if line == DataExractor.SHOW_PLATFORM_END_TEMPLATE:
                        break
                    cleaned_data.append(line)
                else:
                    if line.split()[2] == start_label:
                        start = True
        return_dict = {}
        bdevice = 0
        formatted_line = []
        for line in cleaned_data:
            fx = []
            temp = None
            ix = 0
            for i,x in enumerate(line.split()):
                if(ix >= len(line.split())):
                    break
                if "," in x:
                    val = line.split()[ix] + line.split()[ix+1]
                    ix += 2
                else:
                    val = line.split()[ix]
                    ix += 1
                fx.append(val)
            formatted_line.append(fx)

        tcount = len(formatted_line)
        okcount = 0
        for line in formatted_line:
            if 'ok' in line:
                okcount += 1
            if len(line) == 3:
                return_dict["blank_device_%s"%(bdevice,)] = line[1]
                bdevice += 1
            else:
                return_dict[line[1]] = line[2]
        if okcount == tcount:
            return_dict.update({'R':0})
        else:
            return_dict.update({'R': 1})
        return return_dict



    def extract_version(self,string_to_search = open('hc.txt').readlines()):
        return_dict = {}
        result = 1
        index_to_use = self.index_processor(DataExractor.SHOW_VERSION_TEMPLATE,string_to_search)
        line_data = self.segment_extract(DataExractor.SHOW_VERSION_TEMPLATE,string_to_search)
        for line in line_data:
            m = re.search(DataExractor.SHOW_VERSION_NUMBER_TEMPLATE,line)
            if m:
                return_dict["version"] = m.group(1)
                result = 0
            m = re.findall(DataExractor.SHOW_VERSION_CONFIG_TEMPLATE, line, re.I)
            if m:
                return_dict["configuration"] = m[0]
                result = 0
            m = re.search(DataExractor.SHOW_VERSION_TYPE_TEMPLATE,line)
            if m:
                type_ =  m.group(2).split("-")[:2]
                type_ =  "".join(type_).lower()
                return_dict["type"] = type_
                result = 0
        return_dict.update({'R':result})
        return return_dict

    def extract_show_running_config(self,string_to_search= open('hc.txt').readlines(),version_to_search={}):
        return_dict = {"type_match":False}
        line_data = self.segment_extract(DataExractor.SHOW_RUNNING_CONFIG_TEMPLATE,string_to_search)
        type_ = version_to_search
        for line in line_data:
            if type_["type"] in line:
                return_dict["type_match"] = True
        return return_dict


    def extract_utilization(self,string_to_search= open('hc.txt').read()):
        """
        To extract the utilization percentages
        CPU utilization for five seconds:     'CPU utilization for five seconds: '
        (.+?)                    match any value i.e., alpha-numeric + special characters
            one minute: 'one minute:'
            (.+?)                    match any value i.e., alpha-numeric + special characters
                five minutes: 'five minutes'
                    (.+?)                    match any value i.e., alpha-numeric + special characters

        """
        m = re.search(DataExractor.UTILIZATION_TEMPLATE,string_to_search)
        five_min_val = m.group(4)
        R = 1
        try:
            fval = int(five_min_val)
            if fval < 70:
                R=0
        except Exception as e:
            R=1
        return {"five_seconds":str(m.group(1)+ "/" + m.group(2)),
                "one_minute":str(m.group(3)),
                "five_minutes":str(m.group(4)),
                "R":R}

    def extract_alarms(self,string_to_search= open('hc.txt').read()):
        critical = re.search(DataExractor.CRITICAL_ALARM_TEMPLATE,string_to_search)
        major = re.search(DataExractor.MAJOR_ALARM_TEMPLATE,string_to_search)
        minor = re.search(DataExractor.MINOR_ALARM_TEMPLATE,string_to_search)
        number_of_minor =  None
        number_of_major = None
        number_of_critical = None
        try:
            if critical:
                number_of_critical = int(critical.group(1))

            if major:
                number_of_major = int(major.group(1))
            if minor:
                number_of_minor = int(minor.group(1))
            if (( number_of_critical is None) or (number_of_major is None) or (number_of_minor is None)):
                return {"total_alarms":None}
            total = number_of_critical+number_of_major+number_of_minor
            if total == 0:
                return {"total_alarms":total,"R":0}
        except ValueError as e:
            print("[x] Invalid convert from char/char* to int")
        return {"total_alarms":total,"R":1}

    def extract_memory_statistics(self,string_to_search= open('hc.txt').readlines()):
        # Fetch only section lines
        regex = re.compile(DataExractor.MEMORY_STATISTICS_TEMPLATE)
        line_data = []
        found = False
        first_occurence = True
        for line in string_to_search:
            if regex.search(line) or found:
                found = True
                if not first_occurence:
                    if(line.find("#") != -1 ):
                        break
                    else:
                        line_x = line.strip()
                        line_x = " ".join(line_x.split())
                        line_data.append(line_x.split(" "))
                first_occurence = False
        # Extraction Logic
        label_index_to_use = None
        line_index_to_use = None
        for ix,line in enumerate(line_data):
            for iy, inner_line in enumerate(line):
                if inner_line == "Free(b)":
                    label_index_to_use = iy
                    line_index_to_use = ix
        try:
            value = line_data[line_index_to_use+1][label_index_to_use+1]
            value = int(value)
            if value > 1073741824:
                return {"Free(b)":value ,"R":0}
            return {"Free(b)": value, "R": 1}
        except:
            return {"Free(b)":None,"R":1}

    def extract_buffers(self,string_to_search= open('hc.txt').readlines()):
        return_dict = {}
        line_data = self.segment_extract(DataExractor.SHOW_BUFFERS_TEMPLATE,string_to_search)
        ix = 0
        for line in line_data:
            m = re.search(DataExractor.SHOW_BUFFERS_MISS_TEMPLATE_A,line)
            if m:
                return_dict[ix] = m.group(2)
                ix += 1
            else:
                m = re.search(DataExractor.SHOW_BUFFERS_MISS_TEMPLATE_B,line)
                if m:
                    return_dict[ix] = m.group(2)
                    ix += 1
                else:
                    m = re.search(DataExractor.SHOW_BUFFERS_MISS_TEMPLATE_C,line)
                    if m:
                        return_dict[ix] = m.group(2)
                        ix += 1
        total_misses =  sum([int(_) for _ in return_dict.values()])
        if total_misses <= 300:
            return_dict.update({'R':0})
        else:
            return_dict.update({'R': 1})
        return return_dict

    def extract_bgpv6_routes(self, string_to_search=open('./hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.SHOW_BGPV6_ROUTES, string_to_search)
        return_dict = {}
        cnt = 0
        for line in line_data:
            m = re.search(DataExractor.BGPV6_ROUTES_TEMPLATE_A, line)
            if m:
                key_ = m.group(1) + "::" + m.group(2)
                value_ = "::" + m.group(3) + ":" + m.group(4)
                return_dict[key_] = value_
                cnt += 1

            if ('*>i' in line) or ('*>' in line):
                key_, value_ = line.split(' ')
                return_dict[key_] = value_
                cnt += 1

        if cnt > 2:
            return_dict.update({'R':0})
        else:
            return_dict.update({'R': 1})
        return return_dict

    def extract_bgpv4_1xrtt(self, string_to_search=open('./hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.SHOW_BGPV4_1XRTT, string_to_search)
        return_dict = {}
        cnt = 0
        for line in line_data:
            if ('*mi' in line):
                data = line.split(' ')
                key_ = data[0] + ' ' + data[1]
                value_ = data[2]
                return_dict[key_] = value_
                cnt += 1

            if ('*>i' in line) or ('*>' in line):
                data = line.split(' ')
                key_ = data[0]
                value_ = data[1]
                return_dict[key_] = value_
                cnt += 1
        if cnt > 2:
            return_dict.update({'R':0})
        else:
            return_dict.update({'R': 0})
        return return_dict

    def extract_bgpv4_ran(self, string_to_search=open('./hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.SHOW_BGPV4_RAN, string_to_search)
        return_dict = {}
        cnt = 0
        for line in line_data:
            if ('*mi' in line):
                data = line.split(' ')
                key_ = data[0] + ' ' + data[1]
                value_ = data[2]
                return_dict[key_] = value_
                cnt += 1

            if ('*>i' in line) or ('*>' in line):
                data = line.split(' ')
                key_ = data[0]
                value_ = data[1]
                return_dict[key_] = value_
                cnt += 1

        if cnt > 2:
            return_dict.update({'R':0})
        else:
            return_dict.update({'R': 0})
        return return_dict

    def extract_bgpv4_cell_mgmt(self, string_to_search=open('./hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.SHOW_BGPV4_CELL_MGMT, string_to_search)
        return_dict = {}
        cnt = 0
        for line in line_data:
            if ('*mi' in line):
                data = line.split(' ')
                key_ = data[0] + ' ' + data[1]
                value_ = data[2]
                return_dict[key_] = value_
                cnt += 1

            if ('*>i' in line) or ('*>' in line):
                data = line.split(' ')
                key_ = data[0]
                value_ = data[1]
                return_dict[key_] = value_
                cnt += 1

        if cnt > 2:
            return_dict.update({'R':0})
        else:
            return_dict.update({'R': 0})
        return return_dict

    def xconect_all(self, string_to_search=open('./hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.SHOW_XCONNECT_ALL, string_to_search)
        cnt = 0
        total_lines =  len(line_data)
        for line in line_data:
            if ('LEGEND' not in line):
                m = re.search(DataExractor.XCONNECT_FILTER_TEMPLATE, line)
                if not m:
                    if 'UP' in line:
                        cnt += 1
        if cnt == total_lines:
            return {"count":cnt,"R":0}
        return {"count": cnt, "R": 1}

    def bgpv4_neighbour(self, string_to_search=open('./hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.BGPV4_NEIGHBOURS, string_to_search)
        neighbours = []
        for line in line_data:
            m = re.search(DataExractor.BGPVN_NEIGHBOURS_TEMPLATE, line)
            if m:
                neighbours.append(m.groups())
        if len(neighbours) >= 2:
            return {"neighbours":len(neighbours),"R":0}
        return {"neighbours": len(neighbours), "R": 1}

    def bgpv6_neighbour(self, string_to_search=open('./hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.BGPV6_NEIGHBOURS, string_to_search)
        neighbours = []
        for line in line_data:
            m = re.search(DataExractor.BGPVN_NEIGHBOURS_TEMPLATE, line)
            if m:
                neighbours.append(m.groups())

        if len(neighbours) >= 2:
            return {"neighbours":len(neighbours),"R":0}
        return {"neighbours": len(neighbours), "R": 1}

    def check_version_i_config(self, string_to_search=open('./hc.txt').readlines()):
        index_to_use = self.index_processor(DataExractor.SHOW_VERSION_I_CONFIG_TEMPLATE,string_to_search)
        line_data = self.segment_extract(DataExractor.SHOW_VERSION_I_CONFIG_TEMPLATE, string_to_search[index_to_use:])
        configuration_self = self.extract_version()
        return_dict = {}
        config = configuration_self.get('configuration',None)
        if config is None:
            return_dict["R"] = 1
        for line in line_data:
            if config:
                if line:
                    m = re.findall(DataExractor.SHOW_VERSION_CONFIG_TEMPLATE, line, re.I)
                    if m:
                        return_dict["configuration"] = m[0]
                        return_dict["R"] = 0
        return return_dict

    def extract_show_inventory(self, string_to_search=open('./hc.txt').readlines()):
        line_data = self.segment_extract(DataExractor.SHOW_INVENTORY, string_to_search)
        return_list = []
        for line in line_data:
            m = re.search(DataExractor.TRANCIEVER_TEMPLATE,line)
            if m:
                return_list.append(DataExractor.TRANCIEVER_RETURN_TEMPLATE%(str(m.group(1)),str(m.group(2)),str(m.group(3))))
        self.IDPROM_DETAIL = return_list

    def form_command_idprom_detail(self, string_to_search=open('./hc.txt').readlines()):
        if self.IDPROM_DETAIL:
            commands = []
            commands_2 = []
            for tranciever in self.IDPROM_DETAIL:
                command_1 = "show hw-module " + tranciever + " idprom detail"
                commands.append(command_1)
                command_2 = "show hw-module " + tranciever + " status"
                commands_2.append(command_2)
            self.IDPROM_DETAIL = commands
            self.STATUS = commands_2

    def extract_idprom_details(self, string_to_search=open('./hc.txt').readlines(), query=None):
        return_dict = {}
        if query:
            if '$' in query:
                query = query.replace('$','show hw-mod')
            line_data =  self.segment_extract(query, string_to_search)
            key,value = None,None
            for line in line_data:
                if line:
                    if '=' in line:
                        key,value = line.split('=')
                        key = key.strip()
                        return_dict[key] = [value]
                    else:
                        if key:
                            return_dict[key].append(line)
        return return_dict

    def extract_tranciever_status(self, string_to_search=open('./hc.txt').readlines(), query=None):
        return_dict = {}
        if query:
            if '$' in query:
                query = query.replace('$','show hw-mod')
            line_data =  self.segment_extract(query, string_to_search)
            key,value = None,None
            for line in line_data:
                if line:
                    if '=' in line:
                        key,value = line.split('=')
                        key = key.strip()
                        return_dict[key] = [value]
                    else:
                        if key:
                            return_dict[key].append(line)
        return return_dict

    def extract_value_from_utext(self,value):
        return parser.parse(value)

    def temperature_range_check(self,data,result):
        # Temperature range check START
        response = {"module_temperature": {"R": 1}}
        high_temp_value, low_temp_value = None, None
        high_temp = data.get('High temperature warning threshold', None)
        if high_temp:
            value = self.extract_value_from_utext(high_temp[0])[-1]
            high_temp_value = int(value.value)
        low_temp = data.get('Low temperature warning threshold', None)
        if low_temp:
            value = self.extract_value_from_utext(low_temp[0])[-1]
            low_temp_value = int(value.value)
        query_temp = result.get('Module temperature', None)
        if query_temp:
            query_temp = query_temp[-1]
            value = self.extract_value_from_utext(query_temp)[-1]
            query_temp = value.value
            if high_temp_value and low_temp_value:
                if low_temp_value <= query_temp <= high_temp_value:
                    response["module_temperature"]["R"] = 0
        return response
        # Temperature range check END

    def supply_voltage_range_check(self,data,result):
        # Supply voltage range check START
        response = {"supply_voltage":{"R":1}}
        high_voltage_value, low_voltage_value = None, None
        high_voltage = data.get('High voltage warning threshold', None)
        if high_voltage:
            value = dextractor.extract_value_from_utext(high_voltage[0])[-1]
            high_voltage_value = int(value.value)
        low_voltage = data.get('Low voltage warning threshold', None)
        if low_voltage:
            value = dextractor.extract_value_from_utext(low_voltage[0])[-1]
            low_voltage_value = int(value.value)
        query_voltage = result.get('Transceiver Tx supply voltage', None)
        if query_voltage:
            query_voltage = query_voltage[-1]
            value = dextractor.extract_value_from_utext(query_voltage)[-1]
            query_voltage = value.value
            if high_voltage_value and low_voltage_value:
                if low_voltage_value <= query_voltage <= high_voltage_value:
                    response["supply_voltage"]["R"] = 0
        return response
        # Supply voltage range check END

    def tranciever_bias_current(self,data,result):
        response = {"supply_voltage":{"R":1}}
        tranciever_b_current_high_value, tranciever_b_current_low_value = None, None
        tranciever_b_current_high = data.get('High laser bias current warning threshold', None)
        if tranciever_b_current_high:
            value = dextractor.extract_value_from_utext(tranciever_b_current_high[0])[-1]
            tranciever_b_current_high_value = int(value.value)
        tranciever_b_current_low = data.get('Low laser bias current warning threshold', None)
        if tranciever_b_current_low:
            value = dextractor.extract_value_from_utext(tranciever_b_current_low[0])[-1]
            tranciever_b_current_low_value = int(value.value)
        query_current = result.get('Transceiver Tx bias current', None)
        if query_current:
            query_current = query_current[-1]
            value = dextractor.extract_value_from_utext(query_current)[-1]
            query_current = value.value
        # Write logic uA -> mA
        return response

    def tranciever_bias_current(self,data,result):
        response = {"tranciever_bias_current":{"R":1}}
        tranciever_b_current_high_value, tranciever_b_current_low_value = None, None
        tranciever_b_current_high = data.get('High laser bias current warning threshold', None)
        if tranciever_b_current_high:
            value = dextractor.extract_value_from_utext(tranciever_b_current_high[0])[-1]
            tranciever_b_current_high_value = int(value.value)
        tranciever_b_current_low = data.get('Low laser bias current warning threshold', None)
        if tranciever_b_current_low:
            value = dextractor.extract_value_from_utext(tranciever_b_current_low[0])[-1]
            tranciever_b_current_low_value = int(value.value)
        query_current = result.get('Transceiver Tx bias current', None)
        if query_current:
            query_current = query_current[-1]
            value = dextractor.extract_value_from_utext(query_current)[-1]
            query_current = value.value
        # Write logic uA -> mA
        return response

    def tx_power(self,data,result):
        response = {"tx_power":{"R":1}}
        tx_power_high_value, tx_power_low_value = None, None
        tx_power_high = data.get('High transmit power warning threshold', None)
        if tx_power_high:
            value = dextractor.extract_value_from_utext(tx_power_high[0])[-1]
            tx_power_high_value = int(value.value)
        tx_power_low = data.get('Low transmit power warning threshold ', None)
        if tx_power_low:
            value = dextractor.extract_value_from_utext(tx_power_low[0])[-1]
            tx_power_low_value = int(value.value)
        query_tx_power = result.get('Transceiver Tx power', None)
        if query_tx_power:
            query_tx_power = query_tx_power[-1]
            value = dextractor.extract_value_from_utext(query_tx_power)[-1]
            query_tx_power = value.value
            if tx_power_high_value and tx_power_low_value:
                if tx_power_low_value <= query_tx_power <= tx_power_high_value:
                    response["tx_power"]["R"] = 0
        return response

    def rx_power(self,data,result):
        response = {"rx_power":{"R":1}}
        rx_power_high_value, rx_power_low_value = None, None
        rx_power_high = data.get('High receive power warning threshold', None)
        if rx_power_high:
            value = dextractor.extract_value_from_utext(rx_power_high[0])[-1]
            rx_power_high_value = int(value.value)
        rx_power_low = data.get('Low receive power warning threshold ', None)
        if rx_power_low:
            value = dextractor.extract_value_from_utext(rx_power_low[0])[-1]
            rx_power_low_value = int(value.value)
        query_rx_power = result.get('Transceiver Rx optical power', None)
        if query_rx_power:
            query_rx_power = query_rx_power[-1]
            value = dextractor.extract_value_from_utext(query_rx_power)[-1]
            query_rx_power = value.value
            if rx_power_high_value and rx_power_low_value:
                if rx_power_low_value <= query_rx_power <= rx_power_high_value:
                    response["rx_power"]["R"] = 0 
        return response

    def ping_extract(self,string_to_search=open('./hc.txt').readlines()):
        bfd_neighbour = self.extract_bfd_neighbour(string_to_search)
        bfd_neighbour.pop('R')
        return_dict = {}
        PING_COMMAND = r'ping %s size %s'
        if bfd_neighbour:
            for key in bfd_neighbour:
                command_2000 = PING_COMMAND%(str(key),'2000')
                command_5000 = PING_COMMAND%(str(key),'5000')
                return_dict[key] = [command_2000,command_5000]
        return return_dict


dextractor = DataExractor()
print dextractor.extract_alarms()










