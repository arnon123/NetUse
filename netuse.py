import psutil
import socket
from datetime import datetime
from known_port_numbers import *

global log_file

def my_print(msg):
    print(msg)
    if log_file:
        with open(log_file, 'a') as f:
            f.write(msg + '\n')

def getProcInfo(connection):
    processInfo = ''
    if connection.pid:
        try:
            process = psutil.Process(connection.pid)
            processInfo = process.name()
        except psutil.NoSuchProcess:
            processInfo = 'No proc name'
    return processInfo, connection.pid

def display_network_info():
    # Display active TCP connections
    my_print("Active TCP Connections: (kind='tcp')")
    for conn in psutil.net_connections(kind='tcp'):
        if(conn.status=='ESTABLISHED'):
            # Reverse DNS lookup
            if conn.raddr:
                remote_ip = conn.raddr.ip
                try:
                    remote_host = socket.gethostbyaddr(remote_ip)[0]
                except socket.herror:
                    remote_host = "Unknown"
            processInfo, pid = getProcInfo(conn)
            lport = TcpPorts.get(conn.laddr.port, '')
            rport = TcpPorts.get(conn.raddr.port, '')
            my_print(f"   {processInfo}({pid}) - {conn.laddr.ip}:{conn.laddr.port}{lport} -> {conn.raddr.ip}({remote_host}):{conn.raddr.port}{rport} [{conn.status}]")
        else:
            lport = TcpPorts.get(conn.laddr.port, '')
            my_print(f"   - {conn.laddr.ip}:{conn.laddr.port}{lport} -> [{conn.status}]")
            
    my_print("Active UDP Connections: (kind='udp')")
    for conn in psutil.net_connections(kind='udp'):
        if(conn.status=='ESTABLISHED'):
            if conn.raddr:
                remote_ip = conn.raddr.ip
                try:
                    remote_host = socket.gethostbyaddr(remote_ip)[0]
                except socket.herror:
                    remote_host = "Unknown"
            processInfo, pid = getProcInfo(conn)
            lport = UdpPorts.get(conn.laddr.port, '')
            rport = UdpPorts.get(conn.raddr.port, '')
            my_print(f"   {processInfo}({pid}) - {conn.laddr.ip}:{conn.laddr.port}{lport} -> {conn.raddr.ip}({remote_host}):{conn.raddr.port}{rport} [{conn.status}]")
        else:
            lport = UdpPorts.get(conn.laddr.port, '')
            my_print(f"   - {conn.laddr.ip}:{conn.laddr.port}{lport} -> [{conn.status}]")
            

    # Display listening ports
    my_print("\nListening Ports: (kind='inet')")
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == psutil.CONN_LISTEN:
            processInfo, pid = getProcInfo(conn)
            my_print(f"   {processInfo}({pid}) - {conn.laddr.ip}:{conn.laddr.port}")


    # Display network statistics
    net_stat = psutil.net_if_stats()
    my_print("\nNetwork Statistics:")
    for interface, stats in net_stat.items():
        my_print(f"   - Interface: {interface} isUp={stats.isup}")
        if not stats.isup:
            my_print("     - Interface is not up, statistics not available")
            continue

        if hasattr(stats, 'bytes_sent') and hasattr(stats, 'bytes_recv'):
            if stats.bytes_sent is not None:
                my_print(f"     - Bytes Sent: {stats.bytes_sent}")
            if stats.bytes_recv is not None:
                my_print(f"     - Bytes Received: {stats.bytes_recv}")

if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = f"network_info_{timestamp}.txt"
    display_network_info()