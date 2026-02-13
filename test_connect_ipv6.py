import socket
import sys

# IPv6 address from user's nslookup
ip = "2600:1f1e:75b:4b15:a389:cb0c:53fe:d32" 
port = 5432

print(f"Testing connection to [{ip}]:{port}...")
try:
    # socket.AF_INET6 for IPv6
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.settimeout(5)
    sock.connect((ip, port))
    print("SUCCESS: Connection established via IPv6!")
    sock.close()
except Exception as e:
    print(f"FAILURE: {e}")
