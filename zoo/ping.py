import sys
import subprocess

mac_address = '00:13:f6:01:52:d6'

def ping():
    ping_response = subprocess.Popen(["ping", "-c2", "-W100", sys.argv[1]], stdout=subprocess.PIPE).stdout.read()
    ping_lines = ping_response.split('\n')[1:-5]
    return [ping_line.split()[3][:-1] for ping_line in ping_lines]


def macmap():
    ip_addresses = ping()
    arp_resps = subprocess.Popen(["arp", "-an"], stdout=subprocess.PIPE).stdout.read()
    mac_dict = {}
    for arp_resp in arp_resps.split('\n'):
        if len(arp_resp) > 4:
            ip  = arp_resp.split(' ')[1][1:-1]
            mac = arp_resp.split(' ')[3]
            mac_dict[mac] = ip
    return mac_dict

ping()
print(macmap()[mac_address])
