from multiprocessing import Pool
import os
import subprocess
from enum import StrEnum

# Globals

class Namespaces(StrEnum):
    SERVER = 'srv_ns'
    CLIENT = 'cli_ns'

class Interfaces(StrEnum):
    SERVER = 'srv_ve'
    CLIENT = 'cli_ve'

class IP_Adresses(StrEnum):
    SERVER = '10.0.0.1'
    CLIENT = '10.0.0.2'

class MAC_Adresses(StrEnum):
    SERVER = '00:00:00:00:00:02'
    CLIENT = '00:00:00:00:00:01'

def run_subprocess(command, working_dir='.', expected_returncode=0, debug=False, timeout=15):
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=working_dir,
        timeout=timeout
    )
    if debug:
        print(command)
        print(result.stdout)
    if(result.stderr):
        print(result.stderr)
    assert result.returncode == expected_returncode
    return result.stdout.decode('utf-8')

def change_network_settings(
    packet_loss: str = "0", 
    delay: str = "1",
    client_rate: str = "1000000",
    server_rate: str = "1000000",
    init_cnwd_size: str = "10",
    mtu_bytes: str = "1500",
    ):
    """
    Change the network's virtualised network parameters before a test batch.

    Keyword arguments:
    packet_loss     -- the percentage rate of bidirectional packet loss.
    delay           -- delay in milliseconds, applied bi-direcitonally (i.e. RTT/2)
    client_rate     -- client transmission bandwidth
    server_rate     -- server transmission bandwidth
    init_cnwd_size  -- initial TCP Congestion window size in packets
    mtu_bytes       -- network MTU size in bytes
    """
    # qdisc commands to change virtual network performance
    qdisc_client_command_prefix = [
        'ip', 'netns', 'exec', Namespaces.CLIENT,
        'tc', 'qdisc', 'change',
        'dev', Interfaces.CLIENT
    ]

    qdisc_server_command_prefix = [
        'ip', 'netns', 'exec', Namespaces.SERVER,
        'tc', 'qdisc', 'change',
        'dev', Interfaces.SERVER
    ]
    
    qdisc_shared_command = [
        'root', 'netem', 
        'limit', '100000',
        'delay', f'{delay}',
        'loss', f'{packet_loss}%'
    ]

    qdisc_client_command = (
        qdisc_client_command_prefix +
        qdisc_shared_command +
        ['rate', f'{client_rate}mbit']
    )

    qdisc_server_command = (
        qdisc_server_command_prefix +
        qdisc_shared_command +
        ['rate', f'{server_rate}mbit']
    )
# ip-route commands to change network prameters

#    ip_route_client_prefix = [
#        'ip', 'netns', 'exec', Namespaces.CLIENT,
#        'ip', 'route', 'change',
#        'dev', Interfaces.CLIENT
#    ]
#
#    ip_route_server_prefix = [
#        'ip', 'netns', 'exec', Namespaces.SERVER,
#        'ip', 'route', 'change',
#        'dev', Interfaces.SERVER
#    ]
#
#    ip_route_shared_command = [
#        '10.0.0.0/24', 
#        'initcwnd', f'{init_cnwd_size}',
#        'mtu', 'lock', f'{mtu_bytes}' # mtu lock prevents dynamic mtu scaling
#    ]
#    ip_route_client_command = (
#        ip_route_client_prefix +
#        ip_route_shared_command
#    )
#
#    ip_route_server_command = (
#        ip_route_server_prefix +
#        ip_route_shared_command
#    )

    # execute commands
    run_subprocess(qdisc_client_command)
    run_subprocess(qdisc_server_command)
    #run_subprocess(ip_route_client_command)
    #run_subprocess(ip_route_server_command)

    

def change_qdisc(ns, dev, pkt_loss, delay, jitter, duplicate, corrupt, reorder, rate):

    command = [
        'ip', 'netns', 'exec', ns,
        'tc', 'qdisc', 'change',
        'dev', dev, 'root', 'netem',
        'limit', '1000'
    ]

    if pkt_loss != 0:
        command.append('loss')
        command.append('{0}%'.format(pkt_loss))

    if duplicate != 0:
        command.append('duplicate')
        command.append('{0}%'.format(duplicate))

    if corrupt != 0:
        command.append('corrupt')
        command.append('{0}%'.format(corrupt))

    if reorder != 0:
        command.append('reorder')
        command.append('{0}%'.format(reorder))

    command.append('delay')
    command.append(delay)

    if jitter != 0:
        command.append(jitter)
        # command.append('25%')

    command.append('rate')
    command.append('{0}mbit'.format(rate))

    print(" > " + " ".join(command))
    run_subprocess(command)

def get_rtt_ms():
    command = [
        'ip', 'netns', 'exec', 'cli_ns',
        'ping', '10.0.0.1', '-c', '10'
    ]

    print(" > " + " ".join(command))
    result = run_subprocess(command)

    result_fmt = result.splitlines()[-1].split("/")
    return result_fmt[4].replace(".", "p")
