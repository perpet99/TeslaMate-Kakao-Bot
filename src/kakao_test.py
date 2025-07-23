import requests
from teslaLib import TeslaLib

# def send_discord_message(webhook_url, message):
#     data = {
#         "content": message  # 디스코드 채널에 표시될 메시지
#     }
#     response = requests.post(webhook_url, json=data)
#     print(f"응답 코드: {response.status_code}")



# send_discord_message("https://perpet.synology.me:5050/kakao/440451876599205",'똑똑')


import time


teslaLib = TeslaLib()

time.sleep(2)

teslaLib.updatePower(0)


teslaLib.updateLocation('{"latitude":37.623855,"longitude":127.15779}')
teslaLib.updateLocation('{"latitude":37.623855,"longitude":127.15779}')

teslaLib.updatePower(0)

time.sleep(2)

teslaLib.updatePower(0)

print(teslaLib.location_list)

path = teslaLib.getPathUrlNClear()

print(path)