import requests

def get_weather(lat, lon):
    URL = "https://api.weatherapi.com/v1/current.json"
    KEY = "0f2c982dc90c4c779dc63839242002"
    params = {
        "key": KEY,
        "q": f"{lat},{lon}"
    }
    response = requests.get(URL, params=params)
    return response.json()

def get_weather_details(lat, lon):
    data = get_weather(lat, lon)
    return {
        "last_updated": data["current"]["last_updated"],
        "temp": data["current"]["temp_c"],
        "feels_like": data["current"]["feelslike_f"],
        "condition": data["current"]["condition"]["text"],
        "humidity": data["current"]["humidity"],
        "speed": data["current"]["wind_kph"],
        "degree": data["current"]["wind_degree"]
    }

if __name__ == "__main__":
    print(get_weather_details(lat=13.036906, lon=77.616992))