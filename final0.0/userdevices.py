import MySQLdb

db = MySQLdb.connect( host="localhost",
                                user="root",
                                passwd="root",
                                db="dbname"    )

cursor  = db.cursor()

def return_result(cursor):
    result = []
    for res in cursor.fetchall():
        result.append(res)
    return result

COMMAND_MAPPER = {'ios': [ 'show processes cpu',
                                    'show memory statistics',
                                    'show buffers',
                                    'show version',
                                    'show running-config | i boot',
                                    'show version | i Config',
                                    'show environment',
                                    'show platform',
                                    'show bfd neighbor',
                                    'show ip interface brief',
                                    'show interfaces',
                                    'show mpls interfaces',
                                    'show mpls ldp neighbor',
                                    'show ip bgp vnpv4 all summary',
                                    'show ip bgp vpnv6 unicast all summary',
                                    'show ip bgp vpnv6 unicast vrf LTE',
                                    'show ip bgp vpnv4 vrf 1XRTT',
                                    'show ip bgp vpnv4 vrf RAN',
                                    'show ip bgp vpnv4 vrf CELL_MGMT',
                                    'ping 172.25.2.240 size 2000',
                                    'ping 172.25.2.240 size 5000',
                                    'show logging',
                                    'show xconnect all',
                                    'show hw-module subslot 0/0 transceiver 1 idprom detail' ],

                'asr5000' : [   'show clock',
                                'show system uptime',
                                'show version | grep "Image Version"',
                                'show srp info | grep "Chassis State"',
                                'show hd raid | grep "Degrad"',
                                'show context',
                                'show service all',
                                'show card hardware | grep Prog',
                                'show card info | grep "Card Lock"',
                                'show session recovery status verbose',
                                'show resource | grep License',
                                'show license info | grep "License Status"',
                                'show srp checkpoint statistics | grep Sessmgrs',
                                'show srp info',
                                'show card table | grep -E -v "Active|Standby|None"',
                                'show diameter peers full | grep "Total peers"',
                                'show crash list',
                                'show rct stats',
                                'show task resources | grep diamproxy',
                                'show task resources | grep sessmg',
                                'show task resources | grep -v good',
                                'show alarm outstanding'
                            ]
            }


def get_node(id_,device_type):
    global cursor
    cursor.execute( "select * from nodes where id=%s;" %(str(id_),))
    node = return_result(cursor)
    if node:
        node = node[0]
        if node:
            ip_addr = node[7]
            uname = node[2]
            psswrd = node[3]
            node_id = node[0]
            packet = {'ip_addr': ip_addr,
                      'username': uname,
                      'password': psswrd,
                      'command': COMMAND_MAPPER.get(device_type,[]) }
            node = packet
    return {"devices" :[node]}
