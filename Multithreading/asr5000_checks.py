# -------------------------------------

def asr5000_show_clock(output, response):
    resp = asr5000_obj.extract_show_clock()  # output.split("\n")
    
    response["show_clock"] = resp.get("show_clock", "")


def asr5000_show_system_uptime(output, response):
    resp = asr5000_obj.extract_show_system_uptime(output.split("\n"))  # output.split("\n")
    response["show_system_uptime"] = resp.get("show_system_uptime", "")


def asr5000_show_version_grep_img_ver(output, response):
    resp = asr5000_obj.extract_show_version_grep_image_version(output.split("\n"))  # output.split("\n")
    response["show_version_grep_image_version"] = resp.get("show_version_grep_image_version", "")


def asr5000_show_srp_info_grep_chassis_state(output, response):
    resp = asr5000_obj.show_srp_info_grep_chassis_state(output.split("\n"))  # output.split("\n")
    response["show_srp_info_grep_chassis_state"] = resp.get("show_srp_info_grep_chassis_state", "")


def asr5000_show_hd_raid_grep_degrad(output, response):
    resp = asr5000_obj.show_hd_raid_grep_degrade(output.split("\n"))  # output.split("\n")
    response["show_hd_raid_grep_degrad"] = resp.get("show_hd_raid_grep_degrade", "")


def asr5000_show_context(output, response):
    resp = asr5000_obj.extract_show_context(output.split("\n"))  # output.split("\n")
    response["show_context"] = resp


def asr5000_show_service_all(output, response):
    resp = asr5000_obj.extract_show_service_all()  # output.split("\n")
    response["show_service_all"] = resp


def asr5000_show_card_hardware_grep_prog(output, response):
    resp = asr5000_obj.extract_show_card_hardware_grep_prog(output.split("\n"))  # output.split("\n")
    response["show_card_hardware_grep_prog"] = resp


def asr5000_show_card_info_grep_card_lock(output, response):
    resp = asr5000_obj.extract_show_card_info_grep_card_lock(output.split("\n"))  # output.split("\n")
    response["show_card_info_grep_card_lock"] = resp


def asr5000_session_recovery_status_verbose(output, response):
    resp = asr5000_obj.extract_show_session_recovery_status_verbose()  # output.split("\n")
    response["show_session_recovery_status_verbose"] = resp


def asr5000_show_resource_grep_license(output, response):
    resp = asr5000_obj.extract_show_resource_grep_license(output.split("\n"))  # output.split("\n")
    response["show_resource_grep_license"] = resp


def asr5000_show_license_info_grep_license_status(output, response):
    resp = asr5000_obj.extract_show_license_info_grep_license_status(output.split("\n"))  # output.split("\n")
    response["show_license_info_grep_license_status"] = resp


def asr5000_show_srp_checkpoint_statistics_grep_sessmgrs(output, response):
    resp = asr5000_obj.extract_show_srp_checkpoint_statistics_grep_sessmgrs()  # output.split("\n")
    response["show_srp_checkpoint_statistics_grep_sessmgrs"] = resp


def asr5000_show_srp_info(output, response):
    resp = asr5000_obj.extract_show_srp_info(output.split("\n"))  # output.split("\n")
    response["show_srp_info"] = resp


def asr5000_show_card_table_grep_act_stdby(output, response):
    resp = asr5000_obj.extract_show_card_table_grep(output.split("\n"))  # output.split("\n")
    response["show_card_table_grep"] = resp


def asr5000_show_diameter_peers_full_grep_total_peers(output, response):
    resp = asr5000_obj.extract_show_diameter_peers(output.split("\n"))  # output.split("\n")
    response["show_diameter_peers"] = resp


def asr5000_show_crash_list(output, response):
    resp = asr5000_obj.extract_show_crash_list(output.split("\n"))  # output.split("\n")
    response["totalcrashes"] = resp


def asr5000_show_rct_stats(output, response):
    resp = asr5000_obj.extract_show_rct_status(output.split("\n"))  # output.split("\n")
    response["show_rct_status"] = resp


def asr5000_show_task_resources_grep_diamproxy(output, response):
    resp = asr5000_obj.extract_show_task_diamproxy(output.split("\n"))  # output.split("\n")
    response["diamproxy"] = resp


def asr5000_show_task_resources_grep_sessmg(output, response):
    resp = asr5000_obj.extract_show_task_sessmg(output.split("\n"))  # output.split("\n")
    response["show_task_resources_grep_sessmg"] = resp


def asr5000_show_task_resources_grep_v_good(output, response):
    resp = asr5000_obj.extract_show_task_resource_grep_v_good(output.split("\n"))
    response['show_task_resource_grep_v_good'] = resp


def asr5000_show_alarm_outstanding(output, response):
    resp = asr5000_obj.extract_show_alarm_outstanding(output.split("\n"))
    response['show_alarm_outstanding'] = resp
