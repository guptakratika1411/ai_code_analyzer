import requests

url = "http://localhost:11434/api/generate"

payload = {
    "model": "llama3.2:3b",
    "prompt": "Can you suggest me some rules which get implement in static code review tools like Sonarcube",
    "stream": False
}

response = requests.post(url, json=payload)

print(response.json()["response"])