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

    def receive(self, request):
        """
            request = {
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

            request = {
                "method" : "POST"
                "query" : [
                        "take_off",
                        "return_home",
                        "land",
                        "set_home_location",
                        "goto_location",
                        "raise_altitude",
                    ]
                "data" : {
                    "lat" : 13.038,
                    "lon" : 77.620,
                    "alt" : 10
                }
            }
        """
        request = json.loads(request)
        if request["method"] == "GET":
            if "get_home" == request["query"]:
                self.return_json(info=self.drone.get_home_location())

            elif "get_battery" == request["query"]:
                self.return_json(info=self.drone.get_battery_info())

            elif "get_weather" == request["query"]:
                self.return_json(info=self.drone.get_weather_details())

            elif "get_info" == request["query"]:
                self.return_json(info=self.drone.get_base_info())

            elif "get_location" == request["query"]:
                self.return_json(info=self.drone.get_gps_coordinates())

            elif "get_speed" == request["query"]:
                self.return_json(info=self.drone.get_speed())

            elif "get_direction" == request["query"]:
                self.return_json(info=self.drone.get_direction())

            elif "get_distance_home" == request["query"]:
                self.return_json(info=self.drone.distance_to_home())

            elif "get_distance_target" == request["query"]:
                self.return_json(info=self.drone.distance_to_target())

            else:
                self.send_error()


        elif request["method"] == "POST":
            if "take_off" == request["query"]:
                if "data" in request:
                    self.return_json(info=self.drone.takeoff(
                        altitude=float(request["data"]["alt"])
                    ))
                else:
                    self.return_json(info=self.drone.takeoff())

            elif "return_home" == request["query"]:
                self.return_json(info=self.drone.return_home())

            elif "land" == request["query"]:
                self.return_json(info=self.drone.land())

            elif "set_home_location" == request["query"]:
                if "data" in request:
                    self.return_json(info=self.drone.set_home_location(
                        lat=float(request["data"]["lat"]),
                        lon=float(request["data"]["lon"])
                    ))
                else:
                    self.return_json(info=self.drone.set_home_location_to_current())

            elif "goto_location" == request["query"]:
                if "alt" in request["data"]:
                    self.return_json(info=self.drone.goto_location(
                        lat=request["data"]["lat"],
                        lon=request["data"]["lon"],
                        alt=request["data"]["alt"]
                    ))
                else:
                    self.return_json(info=self.drone.goto_location(
                        lat=request["data"]["lat"],
                        lon=request["data"]["lon"]
                    ))

            elif "raise_altitude" == request["query"]:
                self.return_json(info=self.drone.raise_altitude(
                    alt=float(request["data"]["alt"])
                ))