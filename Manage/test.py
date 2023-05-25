
import requests

api_key = "a505e7edfa2c4d968ab040070e2b61c6"
api_secret = "dd519189e98a1d0cf89781199f84f0e596319c1757b2877cea2ad95190f60eb7"
image_path = 'Manage/file/mat_trc.jpg'

response = requests.post(
  "https://cloud.computervision.com.vn/api/v2/ekyc/card?format_type=file&get_thumb=false",
  auth=(api_key, api_secret),
  files={'img': open(image_path, 'rb')})

print(response.json())
