import urllib.request
import urllib.error
import json

data = json.dumps({
    'email': 'noureqomohamed13@gmail.com' # Or any email you want to test
}).encode('utf-8')

req = urllib.request.Request(
    'http://localhost:8000/admin/test-email',
    data=data,
    headers={'Content-Type': 'application/json'}
)

try:
    res = urllib.request.urlopen(req)
    print("SUCCESS:", res.read().decode())
except urllib.error.HTTPError as e:
    print("ERROR:", e.code, e.read().decode())
except urllib.error.URLError as e:
    print("ERROR: Could not connect to the server. Is it running?")
