import urllib.request
import json
try:
    url = "http://127.0.0.1:8000/predict/30"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Body:", response.read().decode('utf-8')[:500])
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code)
    print("Body:", e.read().decode('utf-8'))
except Exception as e:
    print("Error:", e)
