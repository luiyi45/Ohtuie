import http.client
import urllib.parse
import json

conn = http.client.HTTPConnection("127.0.0.1", 8000)
headers = {"Content-type": "application/x-www-form-urlencoded"}
params = urllib.parse.urlencode({"username": "admin@ohtuie.com", "password": "admin"})

try:
    print("Sending POST request to /api/v1/login/access-token")
    conn.request("POST", "/api/v1/login/access-token", params, headers)
    response = conn.getresponse()
    
    print(f"Status: {response.status}")
    print(f"Reason: {response.reason}")
    data = response.read().decode()
    print(f"Response: {data}")
    conn.close()
except Exception as e:
    print(f"Connection failed: {e}")
