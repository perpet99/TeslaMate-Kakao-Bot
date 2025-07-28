


import time
import json

import math

def get_distance_km(lat1, lon1, lat2, lon2):
    R = 6371  # 지구 반지름 (km)

    def to_rad(deg):
        return deg * math.pi / 180

    d_lat = to_rad(lat2 - lat1)
    d_lon = to_rad(lon2 - lon1)

    a = math.sin(d_lat / 2) ** 2 + \
        math.cos(to_rad(lat1)) * math.cos(to_rad(lat2)) * \
        math.sin(d_lon / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return round(distance, 3)  # 소수점 3자리

# 사용 예시
# dist = get_distance_km(37.5665, 126.9780, 35.1796, 129.0756)
# print(f"두 지점 간 거리는 {dist}km 입니다.")

class TeslaLib:
    def get_zero_powers(self):
        """Return a list of values in power_list that are zero."""
        return [p for p in self.power_list if p == 0]
    def __init__(self):
        self.power_list = []
        self.location_list= []
        self.power_last_update_time = time.time()
        self.location_last_update_time = time.time()
        self.update_time = time.time()
        self.isDriving = False
        self.power = 0
        self.location = None
        self.db = None    
    
    
    
    def getHomeListDescription(self):
        str = ""
        for i,item in enumerate(self.db["home"]):
            latitude = item["latitude"]
            longitude = item["longitude"]
            str += f"홈위치({i}) https://www.google.com/maps/dir/{latitude},{longitude}\n"
        return str
        
    
    def addHome(self):
        if self.location == None :
             return False
        # Ensure home is always stored as dict, not string
        if isinstance(self.location, str):
            self.db["home"].append(json.loads(self.location))
        else:
            self.db["home"].append(self.location)
        return True
        
    def removeHome(self,index):
        try:
            del self.db["home"][index]
            return True
        except Exception as e:
            print(f"{e}")
        return False
             
    
    def updatePower(self, power,sec):
        now = time.time()
        self.power = power
        if self.location == None:
            return
        
        # if now - self.power_last_update_time < 30:
        if now - self.power_last_update_time < sec:
            return
        
        self.power_list.append(power)
        self.location_list.append(self.location)
        self.power_last_update_time = now
            
        
    def updateLocation(self, location, sec):
        if self.isDriving == False:
            return
        now = time.time()
        if now - self.power_last_update_time < sec:
            return
        self.location = location
        self.power_last_update_time = now
        data = json.loads(location)
        self.location_list.append(data)
        
        # self.location = data
        # now = time.time()
        # if now - self.location_last_update_time >= 1:
        #     self.location_list.append(location)
        #     self.location_last_update_time = now
            
        
    # def update(self,sec):
    #     now = time.time()
    #     # if now - self.power_last_update_time < 60*3:
    #     if now - self.power_last_update_time < sec:
    #         return
    #     self.power_last_update_time = now
        
    #     if len(self.power_list) == 0:
    #         self.isDriving = False
    #         return
        
    #     p = sum(self.power_list)    
    #     self.power_list.clear()
        
    #     if p == 0:
    #         self.isDriving = False
    #     else:
    #         self.isDriving = True
    #     return
                
    
    def generate_google_maps_link(self, origin, destination, waypoints):
        base_url = "https://www.google.com/maps/dir/?api=1"
        origin_param = f"&origin={origin["latitude"]},{origin["longitude"]}"
        destination_param = f"&destination={destination["latitude"]},{destination["longitude"]}"
        
        waypoints_param = ""
        if waypoints:
            waypoints_str = "|".join([f"{wp["latitude"]},{wp["longitude"]}" for wp in waypoints])
            waypoints_param = f"&waypoints={waypoints_str}"
        
        full_url = f"{base_url}{origin_param}{destination_param}{waypoints_param}&travelmode=driving"
        return full_url

    def getPathUrlNClear2(self):
        length = len(self.location_list)
        if length < 2:
            return ""
        
        url = self.generate_google_maps_link( self.location_list[0], self.location_list[length-1], self.location_list[1:-1])
        
        self.location_list.clear()
        return url
        
    def dbInit(self,events):
        self.db = {"events":events,"home":[]}
        
    def getPathUrlNClear(self):
        str =''
        for item in self.location_list:
            latitude = item["latitude"]
            longitude = item["longitude"]
            str += f"/{latitude},{longitude}"
        self.location_list.clear()
        
        return "https://www.google.com/maps/dir" + str


