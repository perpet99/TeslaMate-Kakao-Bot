import requests
from teslaLib import TeslaLib

# def send_discord_message(webhook_url, message):
#     data = {
#         "content": message  # 디스코드 채널에 표시될 메시지
#     }
#     response = requests.post(webhook_url, json=data)
#     print(f"응답 코드: {response.status_code}")



# send_discord_message("https://perpet.synology.me:5050/kakao/xxxxxxx",'똑똑')


import time


# teslaLib = TeslaLib()

# time.sleep(2)

# teslaLib.updatePower(0)


# teslaLib.updateLocation('{"latitude":37.623855,"longitude":127.15779}')
# teslaLib.updateLocation('{"latitude":37.623855,"longitude":127.15779}')

# teslaLib.updatePower(0)

# time.sleep(2)

# teslaLib.updatePower(0)

# print(teslaLib.location_list)


# def generate_google_maps_link(origin, destination, waypoints=None):
#     base_url = "https://www.google.com/maps/dir/?api=1"
#     origin_param = f"&origin={origin[0]},{origin[1]}"
#     destination_param = f"&destination={destination[0]},{destination[1]}"
    
#     waypoints_param = ""
#     if waypoints:
#         waypoints_str = "|".join([f"{wp[0]},{wp[1]}" for wp in waypoints])
#         waypoints_param = f"&waypoints={waypoints_str}"
    
#     full_url = f"{base_url}{origin_param}{destination_param}{waypoints_param}&travelmode=driving"
#     return full_url

# # 예시 좌표
# origin = (37.5665, 126.9780)  # 서울
# destination = (35.1796, 129.0756)  # 부산
# waypoints = [(36.3504, 127.3845), (35.8714, 128.6014)]  # 대전, 대구

# link = generate_google_maps_link(origin, destination, waypoints)
# print("구글 지도 경로 링크:", link)


print(float("202.333"))

teslaLib = TeslaLib()

# time.sleep(2)

teslaLib.dbInit([])

teslaLib.isDriving = True
teslaLib.updateLocation('{"latitude":37.623855,"longitude":127.15779}',-1)
teslaLib.addHome()
teslaLib.updateLocation('{"latitude":37.623855,"longitude":227.15779}',-1)
teslaLib.addHome()
teslaLib.updateLocation('{"latitude":37.623855,"longitude":327.15779}',-1)
teslaLib.addHome()

print(teslaLib.db)

print(teslaLib.updateHome())

print(teslaLib.db)

# print(teslaLib.db)

# print(teslaLib.getHomeListDescription())

# teslaLib.removeHome(1)

# print(teslaLib.getHomeListDescription())

# print(teslaLib.isDriving)

# # teslaLib.update(0)

# print(teslaLib.isDriving)

# print(teslaLib.location_list)

# path = teslaLib.getPathUrlNClear()

# print(path)

# import math

# def get_distance_km(lat1, lon1, lat2, lon2):
#     R = 6371  # 지구 반지름 (km)

#     def to_rad(deg):
#         return deg * math.pi / 180

#     d_lat = to_rad(lat2 - lat1)
#     d_lon = to_rad(lon2 - lon1)

#     a = math.sin(d_lat / 2) ** 2 + \
#         math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) * \
#         math.sin(d_lon / 2) ** 2

#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
#     distance = R * c

#     return round(distance, 3)  # 소수점 3자리

# # 사용 예시
# dist = get_distance_km(37.5665, 126.9780, 35.1796, 129.0756)
# print(f"두 지점 간 거리는 {dist}km 입니다.")

# teslaLib.updateLocation('{"latitude":37.5665,"longitude":126.9780}')
# teslaLib.updatePower(1,0)
# teslaLib.update(0)
# teslaLib.updateLocation('{"latitude":35.1796,"longitude":129.0756}')
# teslaLib.updatePower(1,0)
# teslaLib.update(0)
# teslaLib.updateLocation('{"latitude":35.1796,"longitude":127.3845}')
# teslaLib.updatePower(1,0)
# teslaLib.update(0)
# teslaLib.updateLocation('{"latitude":35.8714,"longitude":128.6014}')
# teslaLib.updatePower(1,0)
# teslaLib.update(0)

# link = teslaLib.getPathUrlNClear2()

# print("구글 지도 경로 링크:", link)

# teslaLib.updatePower(0)

# time.sleep(2)

# teslaLib.updatePower(0)
