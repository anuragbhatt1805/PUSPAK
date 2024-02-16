import dronekit_sitl
import time

sitl = dronekit_sitl.start_default(lat=13.036906, lon=77.616992)
connection = sitl.connection_string()

print(connection)


from Drone.main import Drone
drone = Drone(connection)

while True:
    print("___MENU___")
    print("1. Infomation")
    print("2. TakeOff")
    print("3. Land")
    print("0. Exit")

    id = int(input("Enter menu: "))
    if id == 1:
        data = drone.get_base_info()
        print(data["version"])
        print(data["capabilities"])
        print(data["global_l"])
        print(data["global_r"])
        print(data["local_l"])
        print(data["home_l"])
        print(data["gps"])
        print(data["mode"])
        print(data["armed"])

    elif id == 2:
        drone.take_off()

    elif id == 3:
        drone.land_in()

    elif id == 0:
        break
drone.exit()
# time.sleep(30)
sitl.stop()