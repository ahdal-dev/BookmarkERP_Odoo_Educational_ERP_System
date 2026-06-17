import requests

url = "http://127.0.0.1:8069/web/session/authenticate"
payload = {
    "jsonrpc": "2.0",
    "params": {
        "db": "edu_demo_new",
        "login": "admin",
        "password": "admin"
    }
}
response = requests.post(url, json=payload)
print(response.json())
