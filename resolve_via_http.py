import urllib.request
import json
import socket

hostname = "db.tdfyugftewrrfzlxdgcl.supabase.co"
# Query for A record explicitly, then AAAA if needed
url = f"https://dns.google/resolve?name={hostname}"

try:
    print(f"Resolving {hostname} via Google DNS API...")
    with urllib.request.urlopen(url) as response:
        raw_data = response.read().decode()
        data = json.loads(raw_data)
        
    print(f"FULL API Response (Partial): {str(data)[:500]}...") # Print first 500 chars only to avoid truncation

    if "Answer" in data:
        for answer in data["Answer"]:
            name = answer.get("name")
            type_ = answer.get("type")
            data_ = answer.get("data")
            print(f"Record: Name={name}, Type={type_}, Data={data_}")
            
            if type_ == 1: # A
                print(f"FOUND IPv4: {data_}")
            elif type_ == 28: # AAAA
                print(f"FOUND IPv6: {data_}")
            elif type_ == 5: # CNAME
                print(f"FOUND CNAME: {data_}")
    else:
        print("No Answer section found for specific host.")
        
        # Try parent domain
        parent_host = hostname.replace("db.", "")
        url_parent = f"https://dns.google/resolve?name={parent_host}"
        print(f"Trying parent domain: {parent_host}...")
        with urllib.request.urlopen(url_parent) as response:
            data_parent = json.loads(response.read().decode())
        print(f"Parent API Response: {json.dumps(data_parent, indent=2)}")
        
except Exception as e:
    print(f"Failed to resolve via HTTP: {e}")
        
except Exception as e:
    print(f"Failed to resolve via HTTP: {e}")
