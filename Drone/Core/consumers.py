from channels.generic.websocket import WebsocketConsumer
from Core.droneClass import Drone
import json, time

############################################################
import dronekit_sitl

############################################################

class DroneConsumer(WebsocketConsumer):

    sitl = dronekit_sitl.start_default(lat=13.036906, lon=77.616992)
    connection = sitl.connection_string()

    def return_json(self, info, status="OK"):
        info = {
            "status": status,
            "data": info
        }
        self.send(text_data=json.dumps(info))

    def send_error(self):
        self.return_json(info="INVALID QUERY", status="ERROR")

    def connect(self):
        self.accept()
        self.return_json(info={"connection":"ESTABLISHED", "drone":"WAITING"})
        self.drone = Drone(connect=self.connection)
        self.return_json(info=self.drone.get_base_info())
        self.return_json(info={
            "status":"HOME_SETTING",
            "drone": self.drone.set_home_location_to_current()
        })

    def disconnect(self, close_code):
        # self.return_json(info={
        #     "connection": "LOST",
        #     "drone":"HOME RETURN AND LAND"
        # })

        self.drone.return_home()
        while self.drone.distance_to_home()["distance"] >= 0.3:
            time.sleep(1)
        self.drone.land()
        self.drone.close()

    def receive(self, text_data):
        """
            text_data = {
                "method" : "GET"
                "query" : [
                        "get_home",
                        "get_battery",
                        "get_weather",
                        "get_info",
                        "get_location",
                        "get_speed",
                        "get_direction",
                        "get_distance_home",
                        "get_distance_target",
                    ]
            }

            text_data = {
                "method" : "POST"
                "query" : [
                        "take_off",
                        "return_home",
                        "land",
                        "set_home_location",
                        "goto_location",
                        "raise_altitude",
                        "get_weather_details_location",
                    ]
                "data" : {
                    "lat" : 13.038,
                    "lon" : 77.620,
                    "alt" : 10
                }
            }
        """
        text_data = json.loads(text_data)
        if text_data["method"] == "GET":
            if "get_home" == text_data["query"]:
                self.return_json(info=self.drone.get_home_location())

            elif "get_battery" == text_data["query"]:
                self.return_json(info=self.drone.get_battery_info())

            elif "get_weather" == text_data["query"]:
                self.return_json(info=self.drone.get_weather_details())

            elif "get_info" == text_data["query"]:
                self.return_json(info=self.drone.get_base_info())

            elif "get_location" == text_data["query"]:
                self.return_json(info=self.drone.get_gps_coordinates())

            elif "get_speed" == text_data["query"]:
                self.return_json(info=self.drone.get_speed())

            elif "get_direction" == text_data["query"]:
                self.return_json(info=self.drone.get_direction())

            elif "get_distance_home" == text_data["query"]:
                self.return_json(info=self.drone.distance_to_home())

            elif "get_distance_target" == text_data["query"]:
                self.return_json(info=self.drone.distance_to_target())

            else:
                self.send_error()


        elif text_data["method"] == "POST":
            if "take_off" == text_data["query"]:
                if "data" in text_data:
                    self.return_json(info=self.drone.takeoff(
                        altitude=float(text_data["data"]["alt"])
                    ))
                else:
                    self.return_json(info=self.drone.takeoff())

            elif "return_home" == text_data["query"]:
                self.return_json(info=self.drone.return_home())

            elif "land" == text_data["query"]:
                self.return_json(info=self.drone.land())

            elif "set_home_location" == text_data["query"]:
                if "data" in text_data:
                    self.return_json(info=self.drone.set_home_location(
                        lat=float(text_data["data"]["lat"]),
                        lon=float(text_data["data"]["lon"])
                    ))
                else:
                    self.return_json(info=self.drone.set_home_location_to_current())
                    
            elif "get_weather_details_location" == text_data["query"]:
                if "data" in text_data:
                    self.return_json(info=self.drone.get_weather_details_data(
                        lat=float(text_data["data"]["lat"]),
                        lon=float(text_data["data"]["lon"])
                    ))
                else:
                    self.return_json(info=self.drone.set_home_location_to_current())

            elif "goto_location" == text_data["query"]:
                if "alt" in text_data["data"]:
                    self.return_json(info=self.drone.goto_location(
                        lat=text_data["data"]["lat"],
                        lon=text_data["data"]["lon"],
                        alt=text_data["data"]["alt"]
                    ))
                else:
                    self.return_json(info=self.drone.goto_location(
                        lat=text_data["data"]["lat"],
                        lon=text_data["data"]["lon"]
                    ))

            elif "raise_altitude" == text_data["query"]:
                self.return_json(info=self.drone.raise_altitude(
                    alt=float(text_data["data"]["alt"])
                ))
