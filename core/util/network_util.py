import socket


def get_hostname():
    return socket.gethostname()


def get_ip():
    hostname = get_hostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address
