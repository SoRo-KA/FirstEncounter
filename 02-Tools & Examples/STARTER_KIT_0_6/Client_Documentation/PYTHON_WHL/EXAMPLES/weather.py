"""
This module provides a robot skill for reporting current weather conditions and 48-hour forecasts for a given location.

The main skill, `get_weather`, retrieves weather data for a specified location (city name or ZIP code) using the
Open-Meteo API. Users can request either the current weather or an hourly forecast, and select between metric or
imperial units. The response includes temperature, weather description, wind speed/direction, and precipitation data.

The module includes helper functions for formatting weather codes, time strings, and wind directions, as well as for
converting units. Data is formatted for both verbal presentation by the robot and optional logging/printing.
"""

import logging
import requests

from datetime import datetime
from typing import Dict

from pymirokai.decorators.skill import skill, ParameterDescription
from pymirokai.enums.enums import AccessLevel, FaceAnim
from pymirokai.robot import Robot

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,  # You can adjust the logging level to DEBUG, WARNING, ERROR, etc.
    format="%(asctime)s - %(levelname)s - %(message)s",
)


@skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": ["weather"],
        "fr": ["météo"],
    },
    parameters=[
        ParameterDescription(
            name="location", description="The name of the location to fetch weather data for (city or ZIP code)"
        ),
        ParameterDescription(
            name="forecast",
            description=(
                "Whether to fetch the weather forecast for the next 48h "
                "(default is False, which fetches current weather)"
            ),
        ),
        ParameterDescription(
            name="is_metric", description="Whether to fetch data in metric (True) or imperial (False) units"
        ),
    ],
)
async def get_weather(
    robot: Robot,
    location: str,
    forecast: bool = False,
    is_metric: bool = True,
    print_data: bool = False,
    timeout: int = 5,
) -> dict:
    """
    Fetch the current weather or 48-hour weather forecast for a given location.

    Args:
        location (str): The name of the location to fetch weather data for (city or ZIP code).
        forecast (bool): Whether to fetch the weather forecast (default is False, which fetches current weather).
        is_metric (bool): Whether to fetch data in metric (True) or imperial (False) units.
        timeout (int): The timeout for the request in seconds (default is 5).

    Returns:
        None: Logs the weather data.
    """
    await robot.move_ears_to_target(0.2).completed()
    await robot.play_face_reaction(FaceAnim.PERPLEXED).completed()
    # Fetch coordinates directly inside the function
    response = requests.get(
        f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json",
        timeout=timeout,
    )
    results = response.json().get("results", [])
    if not results:
        logging.error("Invalid location!")
        return
    latitude, longitude = results[0]["latitude"], results[0]["longitude"]

    # Build URL directly inside the function, incorporating the unit system
    units = "metric" if is_metric else "imperial"
    fc = "hourly=temperature_2m,precipitation,weathercode,windspeed_10m,winddirection_10m"
    url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&"
        f"{fc if forecast else 'current_weather=true'}&"
        f"timezone=auto&units={units}"
    )
    logging.debug(f"Fetching {'48-hour forecast' if forecast else 'current weather'} for {location}...\n")

    try:
        # Fetch and process data directly inside the function
        data = requests.get(url, timeout=timeout).json()
        weather_data = {"location": location, "units": units}

        if "current_weather" in data:
            weather_data.update(
                {
                    "current": {
                        "temperature": data["current_weather"]["temperature"],
                        "weather": get_weather_description(data["current_weather"]["weathercode"]),
                        "windspeed": data["current_weather"]["windspeed"],
                        "winddirection": get_wind_direction(data["current_weather"]["winddirection"]),
                        "precipitation": data["current_weather"].get("precipitation", "N/A"),
                    }
                }
            )

        if forecast and "hourly" in data:
            weather_data["forecast"] = [
                {
                    "time": format_time(time),
                    "temperature": temp,
                    "weather": get_weather_description(code),
                    "windspeed": wind_speed,
                    "winddirection": get_wind_direction(wind_direction),
                    "precipitation": prec if prec else "N/A",
                }
                for time, temp, code, wind_speed, wind_direction, prec in zip(
                    data["hourly"]["time"],
                    data["hourly"]["temperature_2m"],
                    data["hourly"]["weathercode"],
                    data["hourly"]["windspeed_10m"],
                    data["hourly"]["winddirection_10m"],
                    data["hourly"].get("precipitation", [""] * len(data["hourly"]["time"])),
                )
            ]

        readable_weather_data = {"llm_output": format_weather_data(weather_data)}
        if print_data:
            logging.info(readable_weather_data)

        await robot.soft_coo().completed()
        await robot.move_ears_to_target(0.7).completed()
        await robot.play_face_reaction(FaceAnim.HAPPY_BIG_SMILE).completed()
        await robot.reset_ears().completed()

        return readable_weather_data

    except requests.RequestException as e:
        await robot.reset_ears().started()
        await robot.play_face_reaction(FaceAnim.SADNESS).completed()
        logging.error(f"Error occurred: {e}")
        return {}


def get_weather_description(code: int) -> str:
    """
    Convert a weather code into a human-readable description.

    Args:
        code (int): The weather code returned by the Open-Meteo API.

    Returns:
        str: A description of the weather corresponding to the given code.
    """
    descriptions = {
        0: "Clear",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Cloudy",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Heavy drizzle",
        56: "Light freezing drizzle",
        57: "Heavy freezing drizzle",
        61: "Light rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Light snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Light rain showers",
        81: "Moderate rain showers",
        82: "Heavy rain showers",
        85: "Light snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with light hail",
        99: "Thunderstorm with heavy hail",
    }
    return descriptions.get(code, "Unknown")


def format_time(utc_time: str) -> str:
    """
    Convert a UTC time string to a human-readable format.

    Args:
        utc_time (str): The time in UTC format, e.g., '2025-01-23T00:00'.

    Returns:
        str: A human-readable formatted time string, e.g., '2025-01-23 00:00:00'.
    """
    # If the string doesn't contain seconds, add ":00"
    if len(utc_time) == 16:  # Format: '2025-01-23T00:00'
        utc_time += ":00"
    return datetime.strptime(utc_time.rstrip("Z"), "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")


def get_wind_direction(degrees: float) -> str:
    """
    Convert wind direction in degrees to a human-readable cardinal direction.

    Args:
        degrees (float): The wind direction in degrees (0° to 360°).

    Returns:
        str: A human-readable wind direction (e.g., "North", "South-East").
    """
    directions = [
        ("North", 0),
        ("North-East", 45),
        ("East", 90),
        ("South-East", 135),
        ("South", 180),
        ("South-West", 225),
        ("West", 270),
        ("North-West", 315),
    ]

    # Find the closest cardinal direction
    closest_direction = min(directions, key=lambda x: abs(degrees - x[1]))
    return closest_direction[0]


def convert_wind_speed_to_imperial(wind_speed_metric: float) -> float:
    """
    Convert wind speed from kilometers per hour (km/h) to miles per hour (mph).

    Args:
        wind_speed_metric (float): Wind speed in km/h.

    Returns:
        float: Wind speed in mph.
    """
    return wind_speed_metric * 0.621371


def format_weather_data(weather_data: Dict) -> str:
    """
    Format the weather data into a human-readable string.

    Args:
        weather_data (Dict): The weather data to be formatted, containing current weather and/or forecast information.

    Returns:
        str: The formatted weather data.
    """
    result = ""

    if "current" in weather_data:
        result += (
            f"Current Weather in {weather_data['location']} "
            f"({'Metric' if weather_data['units'] == 'metric' else 'Imperial'} units):\n"
        )

        # Temperature conversion for Imperial
        temp_unit = "°C" if weather_data["units"] == "metric" else "°F"
        temp_value = weather_data["current"]["temperature"]
        if weather_data["units"] == "imperial":
            temp_value = (temp_value * 9 / 5) + 32  # Celsius to Fahrenheit

        result += f"Temperature: {temp_value:.2f}{temp_unit}\n"
        result += f"Weather: {weather_data['current']['weather']}\n"

        # Wind speed conversion for Imperial
        wind_speed_unit = "km/h" if weather_data["units"] == "metric" else "mph"
        wind_speed_value = weather_data["current"]["windspeed"]
        if weather_data["units"] == "imperial":
            wind_speed_value = convert_wind_speed_to_imperial(wind_speed_value)

        result += f"Wind Speed: {wind_speed_value:.2f} {wind_speed_unit}\n"
        result += f"Wind Direction: {weather_data['current']['winddirection']}\n"
        result += f"Precipitation: {weather_data['current']['precipitation']} mm\n"

    if "forecast" in weather_data:
        result += "\n48-Hour Forecast:\n"
        for entry in weather_data["forecast"]:
            # Temperature conversion for Imperial
            temp_value = entry["temperature"]
            if weather_data["units"] == "imperial":
                temp_value = (temp_value * 9 / 5) + 32  # Celsius to Fahrenheit

            # Wind speed conversion for Imperial
            wind_speed_value = entry["windspeed"]
            if weather_data["units"] == "imperial":
                wind_speed_value = convert_wind_speed_to_imperial(wind_speed_value)

            result += (
                f"{entry['time']}: Temp: {temp_value:.2f}°{'C' if weather_data['units'] == 'metric' else 'F'}, "
                f"Weather: {entry['weather']}, Wind Speed: {wind_speed_value:.2f} "
                f"{'km/h' if weather_data['units'] == 'metric' else 'mph'}, "
                f"Wind Direction: {entry['winddirection']}, Precipitation: {entry['precipitation']} mm\n"
            )

    return result


if __name__ == "__main__":
    location = input("Enter the location (city name): ")
    forecast_input = input("Do you want the forecast? (y/n): ").strip().lower() == "y"

    get_weather(location, forecast=forecast_input, is_metric=True, print_data=True)
