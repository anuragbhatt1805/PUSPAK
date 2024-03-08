from geopy import distance as geopy_distance
from Core.weather import get_weather_details as gwd
import dronekit
import math, time

class Drone:

    def __log(self, message):
        print(message)

    def __init__(self, connect):
        try:
            self.vehicle = dronekit.connect(connect, wait_ready=True)
            self.vehicle.wait_ready('autopilot_version')
            self.commands = self.vehicle.commands
            self.commands.wait_ready()
            self.target_loc = None
        except Exception as e:
            self.__log(str(e))

    def get_base_info(self):
        return {
            'status':self.vehicle.system_status.__str__(),
            'version': self.vehicle.version.__str__(),
            'gps' : self.get_gps_coordinates(),
            'battery' : self.get_battery_info(),
        }

    def get_gps_coordinates(self):
        return {
            "lat": self.vehicle.location.global_relative_frame.lat,
            "lon": self.vehicle.location.global_relative_frame.lon,
            "alt": self.vehicle.location.global_relative_frame.alt
        }

    def get_battery_info(self):
        return {
            "voltage" : self.vehicle.battery.voltage,
            "current" : self.vehicle.battery.current,
            "level" : self.vehicle.battery.level
        }

    def get_speed(self):
        return {
            "ground_speed": self.vehicle.groundspeed,
            "airspeed": self.vehicle.airspeed,
            "velocity": {
                "vx": self.vehicle.velocity[0],
                "vy": self.vehicle.velocity[1],
                "vz": self.vehicle.velocity[2]
            }
        }

    def get_home_location(self):
        if self.vehicle.home_location is None:
            return None
        return {
            "lat": self.vehicle.home_location.lat,
            "lon": self.vehicle.home_location.lon,
            "alt": self.vehicle.home_location.alt
        }

    def set_home_location_to_current(self):
        self.vehicle.home_location = dronekit.LocationGlobal(
            self.vehicle.location.global_relative_frame.lat,
            self.vehicle.location.global_relative_frame.lon,
            self.vehicle.location.global_relative_frame.alt
        )
        return self.get_home_location()

    def set_home_location(self, lat:float, lon:float):
        self.vehicle.home_location = dronekit.LocationGlobal(lat, lon, self.vehicle.location.global_frame.alt)
        return self.get_home_location()

    def takeoff(self, altitude:float=5.0):
        while not self.vehicle.is_armable:
            self.__log("Waiting for vehicle to initialise...")
            time.sleep(1)
        self.vehicle.mode = dronekit.VehicleMode("GUIDED")
        while not self.vehicle.mode.name == "GUIDED":
            self.__log("Waiting for drone to enter GUIDED mode...")
            time.sleep(1)
        self.vehicle.armed = True
        while not self.vehicle.armed:
            self.__log("Waiting for vehicle to arm...")
            time.sleep(1)
        self.vehicle.simple_takeoff(altitude)
        while self.vehicle.location.global_relative_frame.alt <= altitude*0.95:
            time.sleep(1)
        self.__log("Reached target altitude")
        return {
            "status" : self.vehicle.system_status.__str__(),
            "mode" : self.vehicle.mode.name,
            "gps" : self.get_gps_coordinates(),
        }

    def land(self):
        self.vehicle.mode = dronekit.VehicleMode("LAND")
        while not self.vehicle.mode.name == "LAND":
            self.__log("Waiting for drone to enter LAND mode...")
            time.sleep(1)
        while self.vehicle.location.global_relative_frame.alt > 0.2:
            time.sleep(1)
        self.__log("Landed")
        return {
            "status" : self.vehicle.system_status.__str__(),
            "target" : "LANDING",
            "mode" : self.vehicle.mode.name,
            "gps" : self.get_gps_coordinates(),
        }

    def return_home(self):
        self.vehicle.mode = dronekit.VehicleMode("RTL")
        while not self.vehicle.mode.name == "RTL":
            self.__log("Waiting for drone to enter RTL mode...")
            time.sleep(1)
        return {
            "status" : self.vehicle.system_status.__str__(),
            "target" : "HOME",
            "mode" : self.vehicle.mode.name,
            "gps" : self.get_gps_coordinates(),
        }

    def raise_altitude(self, altitude:float):
        self.vehicle.simple_goto(
            dronekit.LocationGlobalRelative(
                self.vehicle.location.global_relative_frame.lat,
                self.vehicle.location.global_relative_frame.lon,
                altitude
            )
        )
        while self.vehicle.location.global_relative_frame.alt <= altitude*0.95:
            time.sleep(1)
        if self.target_loc is not None and self.distance_to_target()["distance"] >= 0.3:
            self.goto_location(self.target_loc.lat, self.target_loc.lon, self.target_loc.alt)
        return {
            "status" : self.vehicle.system_status.__str__(),
            "mode" : self.vehicle.mode.name,
            "gps" : self.get_gps_coordinates(),
        }

    def goto_location(self, lat:float, lon:float, alt:float=10):
        self.target_loc = dronekit.LocationGlobalRelative(lat, lon, alt)
        self.vehicle.simple_goto(self.target_loc)
        return {
            "status" : self.vehicle.system_status.__str__(),
            "mode" : self.vehicle.mode.name,
            "gps" : self.get_gps_coordinates(),
        }

    def get_distance(self, initial:dronekit.LocationGlobalRelative, final:dronekit.LocationGlobalRelative):
        if initial is None or final is None:
            return 0
        return geopy_distance.distance(
            (initial.lat, initial.lon),
            (final.lat, final.lon)
        ).m

    def get_direction(self, initial:dronekit.LocationGlobalRelative, final:dronekit.LocationGlobalRelative):
        dLon = math.radians(final.lon) - math.radians(initial.lon)
        dlat = math.radians(final.lat) - math.radians(initial.lat)
        angle = math.atan2(dLon, dlat)
        return math.degrees(angle)

    def distance_to_target(self):
        temp = self.get_distance(self.vehicle.location.global_relative_frame, self.target_loc)
        if temp < 0.3:
            self.target_loc = None
        return {
            "status" : self.vehicle.system_status.__str__(),
            "mode" : self.vehicle.mode.name,
            "gps" : self.get_gps_coordinates(),
            "distance" : temp,
            "direction" : self.vehicle.heading
        }

    def distance_to_home(self):
        return {
            "status" : self.vehicle.system_status.__str__(),
            "mode" : self.vehicle.mode.name,
            "gps" : self.get_gps_coordinates(),
            "distance" : self.get_distance(
                self.vehicle.location.global_relative_frame,
                dronekit.LocationGlobalRelative(
                    self.vehicle.home_location.lat,
                    self.vehicle.home_location.lon,
                    self.vehicle.location.global_relative_frame.alt
                )
            ),
            "direction" : self.vehicle.heading
        }

    def get_weather_details(self):
        return gwd(
            lat=self.vehicle.location.global_relative_frame.lat,
            lon=self.vehicle.location.global_relative_frame.lon
        )

    def close(self):
        self.vehicle.close()



if __name__ == "__main__":
    ############################################################
    import dronekit_sitl
    sitl = dronekit_sitl.start_default(lat=13.036906, lon=77.616992)
    connection = sitl.connection_string()
    ############################################################
    drone = Drone(connect=connection)
    print(drone.get_base_info())
    print()
    print(drone.get_gps_coordinates())
    print()
    print(drone.get_battery_info())
    print()
    print(drone.get_speed())
    print()
    print(drone.get_home_location())
    print()
    print(drone.set_home_location_to_current())
    print()
    print(drone.takeoff(10))
    print("\n=======================\n")
    print(drone.goto_location(13.038, 77.620, 10))
    print("\n=======================\n")
    while drone.distance_to_target()["distance"] >= 0.3:
        time.sleep(1)
        print(drone.distance_to_target())
        print()
        print(drone.get_speed())
    print("\n=======================\n")
    print(drone.return_home())
    print("\n=======================\n")
    while drone.distance_to_home()["distance"] >= 0.3:
        time.sleep(1)
        print(drone.distance_to_home())
        print()
        print(drone.get_speed())
    print("\n=======================\n")
    print(drone.land())