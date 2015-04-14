import socket


def valid_ip(ip_addr):
    try:
        socket.inet_aton(ip_addr)
    except socket.error:
        raise ValueError("Invalid IP Address")
    return ip_addr
