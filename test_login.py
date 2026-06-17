import urllib.request
import json
import ssl

try:
    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/v1/auth/login', 
        data=json.dumps({'login': 'admin@test.com', 'password': 'admin123', 'db': 'edu_demo_new'}).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    res = urllib.request.urlopen(req)
    print(res.read())
except urllib.error.HTTPError as e:
    print(e.read())
except Exception as e:
    print(e)
