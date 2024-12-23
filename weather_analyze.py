import requests

def get_location_key_by_name(city_name: str, api_key: str):
    base_url = "http://dataservice.accuweather.com/locations/v1/cities/search"
    params = {
        "apikey": api_key,
        "q": city_name,
        "language": "en-us"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data:
            city_key = data[0].get("Key", "Not Found")
            return city_key
        else:
            return None
    except Exception:
        return None

def get_location_key_by_lat_lon(api_key: str, lat: str, lon: str):
    try:
        location_url = f"http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
        location_params = {
            "apikey": api_key,
            "q": f"{lat},{lon}"
        }

        location_response = requests.get(location_url, params=location_params)
        location_response.raise_for_status()

        location_data = location_response.json()
        location_key = location_data["Key"]
        return location_key

    except Exception:
        return None

def get_weather_parameters(api_key: str, location_key: str):
    weather_dict = {}

    try:
        weather_url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}"
        weather_params = {
            "apikey": api_key,
            "details": "true"
        }

        weather_response = requests.get(weather_url, params=weather_params)
        weather_response.raise_for_status()

        weather_data = weather_response.json()[0]

        temperature = weather_data["Temperature"]["Metric"]["Value"]  # Температура в °C
        humidity = weather_data["RelativeHumidity"]  # Влажность в %
        wind_speed = weather_data["Wind"]["Speed"]["Metric"]["Value"]  # Скорость ветра в м/с
        rain_probability = weather_data.get("PrecipitationProbability", 0)  # Вероятность дождя в %

        weather_dict['temperature'] = temperature
        weather_dict['humidity'] = humidity
        weather_dict['wind_speed'] = wind_speed
        weather_dict['rain_probability'] = rain_probability

        return weather_dict

    except Exception:
        return None


def check_bad_weather(weather_parameters: dict):
    if (weather_parameters['temperature'] > 35) or (weather_parameters['temperature'] < -20) or (weather_parameters['wind_speed'] > 20) or (weather_parameters['rain_probability'] > 70):
        return 'bad'
    else:
        return 'good'


def get_weather_forecast(api_key, location_key, days):
    try:
        if days != 1 and days != 5:
            raise ValueError("Количество дней должно быть 1 или 5.")

        url = f"http://dataservice.accuweather.com/forecasts/v1/daily/{days}day/{location_key}"

        params = {
            "apikey": api_key,
            "language": "ru-ru",
            "metric": "true"
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        forecast = []
        for daily_forecast in data.get("DailyForecasts", []):
            forecast.append({
                'date': daily_forecast['Date'],
                "max_temperature": daily_forecast["Temperature"]["Maximum"]["Value"],
                "min_temperature": daily_forecast["Temperature"]["Minimum"]["Value"],
                "precipitation_sum": daily_forecast.get("Day", {}).get("PrecipitationProbability", 0),
                "wind_speed": daily_forecast.get("Day", {}).get("Wind", {}).get("Speed", {}).get("Value", 0),
            })

        return forecast

    except Exception as e:
        return None
