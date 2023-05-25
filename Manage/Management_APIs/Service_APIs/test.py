import requests
url = "https://api.smartbot.vn/v2/ekyc/cards/file?get_thumb=false"

payload = {}
files=[
  ('img1',('BLX_TRUOC.jpg',open('/C:/Users/ADMIN/Desktop/API_GW/DODO/BLX_NHẶT/ĐINH THỊ THU HƯƠNG/BLX_TRUOC.jpg','rb'),'image/jpeg')),
  ('img2',('BLX_SAU.jpg',open('/C:/Users/ADMIN/Desktop/API_GW/DODO/BLX_NHẶT/ĐINH THỊ THU HƯƠNG/BLX_SAU.jpg','rb'),'image/jpeg'))
]
headers = {
  'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYWl0cm9uZ2p0aHVhYW5mIiwiZXhwIjoxNjg0NDc1NjQ5fQ.Wgbp6OSJHCazN9vFdY5yUEKF-PE-qzJ1YKxR0z59p2E'
}
def abc():
  response = requests.request("POST", url, headers=headers, data=payload, files=files)

  print("======================={}============".format())
  print(response.json())
  print("\n")


