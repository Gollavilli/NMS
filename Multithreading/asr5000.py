import re

class ASR5000:

    SHOW_CLOCK_TEMPLATE 	= r'show clock'
    EXTRACT_CLOCK_TEMPLATE 	= r'(.+?) (.+?) (.+?) (.+?) UTC (.+?)'
    SHOW_SYSTEM_UPTIME 		= r'show system uptime'
    SHOW_SYSTEM_UPTIME_EXTRACT	= r'System uptime: (.+?) (.+?) (.+?)'
    SHOW_VERSION_GREP_IMAGE_VERSION_TEMPLATE 	= r'show version | grep "Image Version"'
    SHOW_VERSION_GREP_IMAGE_VERSION_EXTRACT 	= r'Image Version: 18.1.0'
    SHOW_SRP_INFO_GREP_CHASSIS_STATE_TEMPLATE	= r'show srp info | grep "Chassis State"'
    SHOW_SRP_INFO_GREP_CHASSIS_STATE_EXTRACT	= r'Chassis State: (.+?)'
    SHOW_HD_RAID_GREP_DEGRADE_TEMPLATE			= r'show hd raid | grep "Degrad"'
    SHOW_HD_RAID_GREP_DEGRADE_EXTRACT			= r'Degraded : (.+?)'
    SHOW_CONTEXT_TEMPLATE						= r'show context'
    SHOW_SERVICE_ALL_TEMPLATE					= r'show service all'
    SHOW_CARD_HARDWARE_GREP_PROG				= r'show card hardware | grep Prog'
    SHOW_CARD_INFO_GREP_CARD_LOCK				= r'show card info | grep "Card Lock"'
    SHOW_SESSION_RECOVERY_STARUS_VERBOSE 		= r'show session recovery status verbose'
    SHOW_RESOURCE_GREP_LICENSE					= r'show resource | grep License'
    SHOW_LICENSE_INFO_GREP_LICENSE_STATUS		= r'show license info | grep "License Status"'
    SHOW_SRP_CHECKPOINT_STATISTICS_GREP_SESSMGRS= r'show srp checkpoint statistics | grep Sessmgrs'
    SHOW_SRP_INFO 								= r'show srp info'
    SHOW_CARD_TABLE_GREP						= r'show card table | grep -E -v "Active|Standby|None"'
    SHOW_DIAMETER_PEERS							= r'show diameter peers full | grep "Total peers"'
    EXTRACT_DIAMETER_PEERS 						= r'Total peers matching specified criteria: (.+)'
    SHOW_CRASH_LIST 							= r'show crash list'
    EXTRACT_CRASH_LIST 							= r'Total Crashes : (.+?)'
    SHOW_RCT_STATUS 							= r'show rct stats'
    EXTRACT_RCT_MIGRATIONS 						= r'Migrations = (.+?)'
    SHOW_TASK_DIAMPROXY 						= r'show task resources | grep diamproxy'
    SHOW_TASK_SESSMG 							= r'show task resources | grep sessmg'
    SHOW_TASK_RESOURCE_GREP_V_GOOD 				= r'show task resources | grep -v good'
    SHOW_ALARM_OUTSTANDING						= r'show alarm outstanding'

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

    def segment_extract(self,SEGMENT,string_to_search,bounce=0):
        regex = re.compile(SEGMENT)
        line_data = []
        found = False
        first_occurence = True
        for line in string_to_search:
            if regex.search(line) or found:
                found = True
                if not first_occurence:
                    if(line.find("#") != -1 ):
                        if ( bounce == 0 ):
                            break
                        else:
                            bounce -= 1
                    else:
                        line_x = line.strip()
                        line_x = " ".join(line_x.split())
                        line_data.append(line_x)
                first_occurence = False
        return line_data

    def extract_show_clock(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_CLOCK_TEMPLATE,string_to_search)
        return_dict = {'show_clock':None}
        for line in line_data:
            m = re.search(ASR5000.EXTRACT_CLOCK_TEMPLATE,line)
            if m:
                
                return_dict['show_clock'] = line.strip()
                break
        return return_dict


    def extract_show_system_uptime(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_SYSTEM_UPTIME,string_to_search)
        return_dict = {'show_system_uptime':None}
        for line in line_data:
            m = re.search(ASR5000.SHOW_SYSTEM_UPTIME_EXTRACT,line)
            if m:
                return_dict['show_system_uptime'] = line.split(':')[-1].strip()
                break
        return return_dict

    def extract_show_version_grep_image_version(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_VERSION_GREP_IMAGE_VERSION_TEMPLATE,string_to_search)
        return_dict = {'show_version_grep_image_version':None}
        for line in line_data:
            m = re.search(ASR5000.SHOW_VERSION_GREP_IMAGE_VERSION_EXTRACT,line)
            if m:
                return_dict['show_version_grep_image_version'] = line.split()[-1].strip()
                break
        return return_dict


    def show_srp_info_grep_chassis_state(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        index_to_use = self.index_processor(ASR5000.SHOW_SRP_INFO_GREP_CHASSIS_STATE_TEMPLATE,string_to_search)
        line_data = self.segment_extract(ASR5000.SHOW_SRP_INFO_GREP_CHASSIS_STATE_TEMPLATE,string_to_search[index_to_use:])
        return_dict = {'show_srp_info_grep_chassis_state':None}
        for line in line_data:
            m = re.search(ASR5000.SHOW_SRP_INFO_GREP_CHASSIS_STATE_EXTRACT,line)
            if m:
                return_dict['show_srp_info_grep_chassis_state'] = line.split()[-1].strip()
                break
        return return_dict

    def show_hd_raid_grep_degrade(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_HD_RAID_GREP_DEGRADE_TEMPLATE,string_to_search)
        return_dict = {'show_hd_raid_grep_degrade':None}
        for line in line_data:
            m = re.search(ASR5000.SHOW_HD_RAID_GREP_DEGRADE_EXTRACT,line)
            if m:
                return_dict['show_hd_raid_grep_degrade'] = line.split()[-1].strip()
                break
        return return_dict

    def extract_show_context(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_CONTEXT_TEMPLATE,string_to_search)
        return_dict = {'active_count':0,'R':0}
        start_label = '---------'
        blk = True
        start = False
        total_lines = 0
        for line in line_data:
            if line:
                if start:
                    total_lines += 1
                    if 'Active' in line.split():
                        return_dict['active_count'] += 1
                if blk:
                    if start_label in line:
                        start = True
                        blk = False
        if not ((total_lines -return_dict['active_count']) == 0):
            return_dict['R'] = 1
        return return_dict

    def extract_show_service_all(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_SERVICE_ALL_TEMPLATE,string_to_search)
        start_label = '-----------'
        start = False
        cleaned_data = []
        ucid = {}
        usid = {}
        for line in line_data:
            if line:
                if start:
                    data = line.split()
                    if len(data) > 2:
                        try:
                            cid = int(data[0])
                            sid = int(data[1])
                            if cid in ucid:
                                ucid[cid] += 1
                            else:
                                ucid[cid] = 1


                            if sid in usid:
                                usid[sid] += 1
                            else:
                                usid[sid] = 1
                        except ValueError as e:
                            print '[x] Error occured for type conversion from ( assumend int as )char*->int'
                            pass
                else:
                    if line.split()[2] == start_label:
                        start = True
        return { 'count_unique_context_id':len(ucid),'count_unique_service_id':len(usid) }

    def extract_show_card_hardware_grep_prog(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_CARD_HARDWARE_GREP_PROG,string_to_search)
        return_dict = {'upto_date_count':0,'R':0}
        start = False
        blk = True
        total_lines = 0
        for line in line_data:
            if blk:
                if 'Card Programmables' in line:
                    start = True
                    blk = False
            if start:
                if line:
                    total_lines += 1
                    data_pre = [_.strip() for _ in line.split(':')]
                    if 'up to date' in data_pre:
                        return_dict['upto_date_count'] += 1
        if not (( total_lines - return_dict['upto_date_count'] ) == 0):
            return_dict['R'] = 1
        return return_dict

    def extract_show_card_info_grep_card_lock(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_CARD_INFO_GREP_CARD_LOCK,string_to_search)
        return_dict = {'locked_count':0,'unlocked_count':0}
        for line in line_data:
            if 'Locked' in line:
                return_dict['locked_count'] += 1
            if 'Unlocked' in line:
                return_dict['unlocked_count'] += 1
        return return_dict

    def extract_show_session_recovery_status_verbose(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_SESSION_RECOVERY_STARUS_VERBOSE,string_to_search)
        return_dict = {'overall_status':None}
        for line in line_data:
            if 'Overall Status' in line:
                return_dict['overall_status'] = line.split(':')[-1].strip()
                break
        return return_dict

    def extract_show_resource_grep_license(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_RESOURCE_GREP_LICENSE,string_to_search)
        start = False
        blk = True
        total_lines = 0
        return_dict = {'within_acceptable_limits_count':0 ,'R':0}
        for line in line_data:
            data_pre = [_.strip() for _ in line.split(':')]
            if blk:
                if 'License Status' in data_pre:
                    start = True
                    blk = False
            if start:
                if line:
                    total_lines += 1
                    if 'Within Acceptable Limits' in data_pre:
                        return_dict['within_acceptable_limits_count'] += 1
        if not (( total_lines - return_dict['within_acceptable_limits_count'] ) == 0):
            return_dict['R'] = 1
        return return_dict

    def extract_show_license_info_grep_license_status(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_LICENSE_INFO_GREP_LICENSE_STATUS,string_to_search)
        return_dict = {'license_status':None}
        for line in line_data:
            if 'License Status' in line:
                return_dict['license_status'] = line.replace('License Status','').strip()
                break
        return return_dict

    def extract_show_srp_checkpoint_statistics_grep_sessmgrs(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_SRP_CHECKPOINT_STATISTICS_GREP_SESSMGRS,string_to_search)
        return_dict = {'number_of_sessmgrs':None}
        for line in line_data:
            if 'Number of Sessmgrs' in line:
                return_dict['number_of_sessmgrs'] = line.split(':')[-1].strip()
                break
        return return_dict

    def extract_show_srp_info(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        index_to_use = self.index_processor(ASR5000.SHOW_SRP_INFO,string_to_search)
        line_data = self.segment_extract(ASR5000.SHOW_SRP_INFO,string_to_search[index_to_use:])
        return_dict = {'chassis_state':None}
        for line in line_data:
            if 'Chassis State' in line:
                data = line.split(':')
                if len(data) == 2:
                    return_dict['chassis_state'] = data[-1]
                    break
        return return_dict

    def extract_show_card_table_grep(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        index_to_use = self.index_processor(ASR5000.SHOW_CARD_TABLE_GREP,string_to_search)
        line_data = self.segment_extract(ASR5000.SHOW_CARD_TABLE_GREP,string_to_search[index_to_use:])
        match = '--------------------------------------'
        start = False
        blk = True
        return_dict = {'count':0}
        for line in line_data:
            data = line.split()
            if start:
                if line:
                    return_dict['count'] += 1
            if blk:
                if len(data) > 2:
                    if data[1] == match:
                        start = True
                        blk = False
        return return_dict

    def extract_show_diameter_peers(self, string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_DIAMETER_PEERS,string_to_search)
        for line in line_data:
            m = re.search(ASR5000.EXTRACT_DIAMETER_PEERS,line)
            if m:
                return { 'total_peers': m.group(1) }

    def extract_show_crash_list(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_CRASH_LIST,string_to_search,bounce=1)
        for line in line_data:
            m = re.search(ASR5000.EXTRACT_CRASH_LIST,line)
            if m:
                return {"total_crashes": m.group(1)}

    def extract_show_rct_status(self, string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_RCT_STATUS,string_to_search)
        return_dict = {}
        for line in line_data:
            m = re.search(ASR5000.EXTRACT_RCT_MIGRATIONS,line)
            if m:
                return {"migrations": m.group(1)}

    def extract_show_task_diamproxy(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        index_to_use = self.index_processor(ASR5000.SHOW_TASK_DIAMPROXY,string_to_search)
        line_data = self.segment_extract(ASR5000.SHOW_TASK_DIAMPROXY,string_to_search[index_to_use:])
        cnt = 0
        for line in line_data:
            if 'good' in line:
                cnt+=1
        return {"count": cnt}

    def extract_show_task_sessmg(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        index_to_use = self.index_processor(ASR5000.SHOW_TASK_SESSMG,string_to_search)
        line_data = self.segment_extract(ASR5000.SHOW_TASK_SESSMG,string_to_search[index_to_use:])
        cnt = 0
        dnt = 0
        e = 0
        for line in line_data:
            if line:
                e+=1
                if 'good' in line:
                    cnt+=1
        if e-cnt>1:
            return {'count':cnt,'status':'fail'}
        else:
            return {'count':cnt,'status':'pass'}

    def extract_show_task_resource_grep_v_good(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_TASK_RESOURCE_GREP_V_GOOD,string_to_search)
        match = '---------'
        start = False
        blk = True
        return_dict = {'count':0}
        for line in line_data:
            data = line.split()
            if start:
                if line:
                    return_dict['count'] += 1
            if blk:
                if len(data) > 2:
                    if data[1] == match:
                        start = True
                        blk = False
        if return_dict['count'] > 1:
            return_dict['R'] = 1
        else:
            return_dict['R'] = 0
        return return_dict

    def extract_show_alarm_outstanding(self,string_to_search=open('asr5000_health_check_outputs.txt').readlines()):
        line_data = self.segment_extract(ASR5000.SHOW_ALARM_OUTSTANDING,string_to_search)
        match = '----------'
        start = False
        blk = True
        return_dict = {'count':0}
        for line in line_data:
            data = line.split()
            if start:
                if line:
                    return_dict['count'] += 1
            if blk:
                if len(data) > 2:
                    if data[1] == match:
                        start = True
                        blk = False
        if return_dict['count'] > 1:
            return_dict['R'] = 1
        else:
            return_dict['R'] = 0
        return return_dict



asr5000_obj = ASR5000()
idx= asr5000_obj.index_processor('show task resources | grep sessmg',open('asr5000_health_check_outputs.txt').readlines())
asr5000_obj.segment_extract('show task resources | grep sessmg',string_to_search=open('asr5000_health_check_outputs.txt').readlines()[idx:])



