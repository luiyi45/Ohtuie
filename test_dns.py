import socket
import sys

host = "db.tdfyugftewrrfzlxdgcl.supabase.co"
print(f"Resolving {host}...")
try:
    ip_list = socket.getaddrinfo(host, 5432)
    print(f"Success! IPs: {ip_list}")
except Exception as e:
    print(f"Failed: {e}")
    sys.exit(1)
