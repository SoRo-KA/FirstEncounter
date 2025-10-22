import requests
from pymirokai.decorators.skill import custom_skill, ParameterDescription
from pymirokai.enums.enums import AccessLevel


@custom_skill(
    access_level=AccessLevel.USER,
    verbal_descriptions={
        "en": ["track flight", "flight status", "where is flight"],
        "fr": ["suivre vol", "statut vol", "où est le vol"],
    },
    parameters=[
        ParameterDescription(name="flight_number", description="Numéro de vol (ex: AF123)"),
    ],
)
async def track_flight(robot, flight_number: str, timeout: int = 5):
    """Fetch live flight status using AviationStack API.

    Args:
        robot: The Mirokai robot instance.
        flight_number (str): The flight number to look up.
        api_key (str): Your API key for AviationStack.
        timeout (int): HTTP timeout in seconds.
    """
    url = "http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": "a7075ba2b6f5c0c62d0bb9eb465b4451",
        "flight_iata": flight_number
    }

    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()

        if "data" in data and data["data"]:
            flight = data["data"][0]
            airline = flight["airline"]["name"]
            departure_airport = flight["departure"]["airport"]
            arrival_airport = flight["arrival"]["airport"]
            status = flight["flight_status"]

            answer = (
                f"Le vol {flight_number} de {airline} décolle de {departure_airport} "
                f"et arrive à {arrival_airport}. Statut actuel : {status}."
            )
        else:
            answer = f"Aucune information trouvée pour le vol {flight_number}."

    except requests.RequestException:
        answer = "Je n'arrive pas à récupérer les informations du vol pour le moment."

    await robot.say(answer).completed()
