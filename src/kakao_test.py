import requests

def send_discord_message(webhook_url, message):
    data = {
        "content": message  # 디스코드 채널에 표시될 메시지
    }
    response = requests.post(webhook_url, json=data)
    print(f"응답 코드: {response.status_code}")



send_discord_message("https://perpet.synology.me:5050/kakao/440451876599205",'똑똑')