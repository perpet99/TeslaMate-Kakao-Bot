


import time
import json

class TeslaLib:
    def get_zero_powers(self):
        """Return a list of values in power_list that are zero."""
        return [p for p in self.power_list if p == 0]
    def __init__(self):
        self.power_list = []
        self.location_list= []
        self.power_last_update_time = time.time()
        self.location_last_update_time = time.time()
        self.isDriving = False
        self.power = 0
        self.location = None
        self.isDriving = True
        self.update_time = time.time()
        
    def updatePower(self, power):
        now = time.time()
        self.power = power
        if self.location == None:
            return
        
        if now - self.power_last_update_time >= 1:
            self.power_list.append(power)
            self.location_list.append(self.location)
            self.power_last_update_time = now
            
        
            
        
    def updateLocation(self, location):
        
        data = json.loads(location)
        self.location = data
        
        # now = time.time()
        # if now - self.location_last_update_time >= 1:
        #     self.location_list.append(location)
        #     self.location_last_update_time = now
            
        
    def update(self):
        now = time.time()
        # if now - self.power_last_update_time < 60*5:
        if now - self.power_last_update_time < 10:
            return
        self.power_last_update_time = now
        
        if len(self.power_list) == 0:
            self.isDriving = False
            return
        
        p = sum(self.power_list)    
        self.power_list.clear()
        
        if p == 0:
            self.isDriving = False
        else:
            self.isDriving = True
        return
                
            
    def getPathUrlNClear(self):
        str =''
        for item in self.location_list:
            latitude = item["latitude"]
            longitude = item["longitude"]
            str += f"/{latitude},{longitude}"
        self.location_list.clear()
        
        return "https://www.google.com/maps/dir" + str
