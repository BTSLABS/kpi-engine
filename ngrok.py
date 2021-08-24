import json
import requests
from configurator import get_conf

r = requests.get('http://localhost:4040/api/tunnels')
ngrok_conf = r.json()

ngrok_endpoint = ngrok_conf['tunnels'][0]['public_url']

url = "https://webexapis.com/v1/webhooks"

payload={}
headers = {
  'Authorization': 'Bearer ' + get_conf('webexapi_token')
}

response = requests.request("GET", url, headers=headers, data=payload)

webex_webhook = response.json()
webex_webhook_id = webex_webhook['items'][0]['id']

url = "https://webexapis.com/v1/webhooks/" + webex_webhook_id

payload = json.dumps({
  "targetUrl": ngrok_endpoint
})
headers = {
  'Authorization': 'Bearer ' + get_conf('webexapi_token'),
  'Content-Type': 'application/json'
}

response = requests.request("PUT", url, headers=headers, data=payload)

