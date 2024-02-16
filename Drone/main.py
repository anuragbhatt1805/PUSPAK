from dronekit import connect, VehicleMode
import time, math

class Drone():
    drone_modes = {
        "AUTO":"AUTO",
        "GUIDED":"GUIDED",
        "LAND":"LAND"
    }
    
    def __init__(self, connection, baudrate:int = None) -> None:
        if baudrate != None:
            self.__vehicle = connect(connection, wait_ready=True, timeout=100, baud=baudrate)
        else:
            self.__vehicle = connect(connection, wait_ready=True, timeout=100)
        self.__vehicle.wait_ready('autopilot_version')
        self.__cmds = self.__vehicle.commands

    def get_home_location(self):
        while not self.__vehicle.home_location:
            self.__cmds.download()
            self.__cmds.wait_ready()
            if not self.__vehicle.home_location:
                print(" Waiting for home location ...")
                time.sleep(1)
        return self.__vehicle.home_location

    def set_home_location(self, **location):
        """
            _summary_: To set home location of drone

            _params_:
                'lat' : Latitude of location
                'lon' : Longitude of location
                'alt' : Altitude from ground level
        """
        try:
            self.__vehicle.home_location.lat = location["lat"]
            self.__vehicle.home_location.lon = location["lon"]
            if "alt" in location.keys():
                self.__vehicle.home_location.alt = location["alt"]
        except:
            self.__vehicle.home_location = self.__vehicle.location.global_relative_frame

    def get_base_info(self) -> dict:
        result = dict()
        result["version"] = self.__vehicle.version
        result["capabilities"] = self.__vehicle.capabilities.ftp
        result["global_l"] = self.__vehicle.location.global_frame
        result["global_r"] = self.__vehicle.location.global_relative_frame
        result["local_l"] = self.__vehicle.location.local_frame
        result["gps"] = self.__vehicle.gps_0
        result["home_l"] = self.get_home_location()
        result["mode"] = self.__vehicle.mode.name
        result["armed"] = self.__vehicle.armed
        return result

    def _is_drone_armed(self) -> bool:
        while not self.__vehicle.is_armable:
            print("Waiting for vehicle to become armable...")
            time.sleep(1)
        return self.__vehicle.is_armable

    def _arm_drone(self, arm=True) -> bool:
        self.__vehicle.armed = arm
        while self.__vehicle.armed != arm:
            print("Waiting for propellers to arm...")
            time.sleep(1)
        self._log("Drone is Armed")
        return self.__vehicle.armed

    def get_drone_mode(self) -> str:
        print(self.__vehicle.mode.name)
        return self.__vehicle.mode.name

    def set_drone_mode(self, mode):
        if not mode:
            raise Exception("Please provide a valid mode")
        if self._is_drone_armed():
            if self.get_drone_mode == self.drone_modes["GUIDED"]:
                return True
            else:
                print(self.get_drone_mode)
                self.__vehicle.mode = VehicleMode(self.drone_modes["GUIDED"])
                while self.get_drone_mode != self.drone_modes["GUIDED"]:
                    print("Waiting for drone to enter GUIDED mode...")
                    time.sleep(1)
                self._log(f"Drone is shifted to {self.drone_modes['GUIDED']} mode")
                return self._arm_drone()

    def take_off(self, altitude=2):
        SMOOTH_TAKEOFF_THRUST = 0.6
        self.set_drone_mode(self.drone_modes["GUIDED"])
        self.__vehicle.simple_takeoff(altitude)
        current_alt = self.__vehicle.location.global_relative_frame.alt
        while (current_alt < altitude):
            current_alt = self.__vehicle.location.global_relative_frame.alt
            self._log(f"Current: {current_alt}")
            time.sleep(1)
        self._log(f"Current: {current_alt}")
        return None
            
    #     target_alt = altitude
    #     while True:
    #         current_altitude = self.__vehicle.location.global_relative_frame.alt
    #         self._log(f"Altitude: {current_altitude}  Desired: {target_alt}")
    #         if current_altitude >= target_alt*0.95:
    #             self._log("Reached target altitude")
    #             break
    #         elif current_altitude >= target_alt*0.6:
    #             thrust = SMOOTH_TAKEOFF_THRUST
    #         self.__set_attitude(thrust = thrust)
    #         time.sleep(0.2)

    # def __send_attitude_target(self, roll_angle = 0.0, pitch_angle = 0.0,
    #                         yaw_angle = None, yaw_rate = 0.0, use_yaw_rate = False,
    #                         thrust = 0.5):
    #     if yaw_angle is None:
    #         yaw_angle = self.__vehicle.attitude.yaw
    #     msg = self.__vehicle.message_factory.set_attitude_target_encode(
    #         0, 1, 1,
    #         0b00000000 if use_yaw_rate else 0b00000100,
    #         self.__to_quaternion(roll_angle, pitch_angle, yaw_angle),
    #         0, 0,
    #         math.radians(yaw_rate), 
    #         thrust 
    #     )
    #     self.__vehicle.send_mavlink(msg)

    # def __set_attitude(self, roll_angle = 0.0, pitch_angle = 0.0,
    #                 yaw_angle = None, yaw_rate = 0.0, use_yaw_rate = False,
    #                 thrust = 0.5, duration = 0):
    #     self.__send_attitude_target(roll_angle, pitch_angle,
    #                         yaw_angle, yaw_rate, False,
    #                         thrust)
    #     start = time.time()
    #     while time.time() - start < duration:
    #         self.__send_attitude_target(roll_angle, pitch_angle,
    #                             yaw_angle, yaw_rate, False,
    #                             thrust)
    #         time.sleep(0.1)
    #     self.__send_attitude_target(0, 0,
    #                         0, 0, True,
    #                         thrust)

    # def __to_quaternion(self, roll = 0.0, pitch = 0.0, yaw = 0.0):
    #     t0 = math.cos(math.radians(yaw * 0.5))
    #     t1 = math.sin(math.radians(yaw * 0.5))
    #     t2 = math.cos(math.radians(roll * 0.5))
    #     t3 = math.sin(math.radians(roll * 0.5))
    #     t4 = math.cos(math.radians(pitch * 0.5))
    #     t5 = math.sin(math.radians(pitch * 0.5))

    #     w = t0 * t2 * t4 + t1 * t3 * t5
    #     x = t0 * t3 * t4 - t1 * t2 * t5
    #     y = t0 * t2 * t5 + t1 * t3 * t4
    #     z = t1 * t2 * t4 - t0 * t3 * t5

    #     return [w, x, y, z]

    def land_in(self):
        self.__vehicle.mode = VehicleMode(self.drone_modes['AUTO'])
        time.sleep(1)

    async def change_altitude(self, altitude):
        pass

    async def increase_altitude(self):
        pass

    async def decrease_altitude(self):
        pass

    async def rotate(self, degree):
        pass

    async def traverse(self, lat, lon):
        pass

    async def get_drone_velocity(self):
        pass

    async def increase_drone_velocity(self):
        pass

    async def decrase_drone_velocity(self):
        pass

    async def get_battery_health(self):
        pass

    async def get_current_location(self):
        pass

    async def track(self):
        pass

    async def get_distance_travelled_from_boot(self):
        pass

    async def get_total_distance_travelled(self):
        pass

    def _log(self, message):
        print(message)

    def exit(self):
        self.__vehicle.close()