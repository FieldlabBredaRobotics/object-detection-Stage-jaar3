import requests

url = "http://127.0.0.1:5000/process_natural_language"
payload = {"text": "Ik zoek mijn telefoon"}
response = requests.post(url, json=payload)
print(response.json())
