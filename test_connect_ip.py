import socket
import sys

# Candidate IP from previous DNS query (Cloudflare IP)
ip = "172.64.34.193" 
port = 6543

print(f"Testing connection to {ip}:{port}...")
try:
    sock = socket.create_connection((ip, port), timeout=5)
    print("SUCCESS: Connection established!")
    sock.close()
except Exception as e:
    print(f"FAILURE: {e}")
