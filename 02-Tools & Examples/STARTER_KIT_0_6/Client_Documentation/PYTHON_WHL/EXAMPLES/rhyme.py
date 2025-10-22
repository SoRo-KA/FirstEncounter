"""
This module defines a robot skill for finding rhyming words.

The main asynchronous function `fetch_rhymes` allows users to input a word and optionally specify a maximum number
of rhymes to retrieve. It queries the Datamuse API for rhyming words, then has the robot react visually and respond
with the rhymes found. If no rhymes are available or the request fails, an appropriate response is returned.
"""

import requests
from pymirokai.decorators.skill import skill, ParameterDescription
from pymirokai.enums.enums import AccessLevel, FaceAnim
from pymirokai.robot import Robot


@skill(
    access_level=AccessLevel.USER,  # Defines access level for the skill
    verbal_descriptions={
        "en": ["find rhymes", "words that rhyme", "rhyme finder"],
        "fr": ["trouver des rimes", "mots qui riment", "rime"],
    },
    parameters=[
        ParameterDescription(name="word", description="The word to find rhymes for."),
        ParameterDescription(name="max_results", description="Maximum number of rhymes to retrieve."),
    ],
)
async def fetch_rhymes(robot: Robot, word: str, max_results: int = 5, timeout: int = 5) -> dict:
    """Fetch words that rhyme with the given input word.

    Args:
        word (str): The word to find rhymes for.
        max_results (int, optional): The maximum number of rhyming words to retrieve. Defaults to 5.
        timeout (int, optional): The timeout duration for the API request in seconds. Defaults to 5.

    Returns:
        dict: A dictionary containing the response output.
    """
    try:
        # Fetch rhymes from the Datamuse API
        url = f"https://api.datamuse.com/words?rel_rhy={word}&max={max_results}"
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()

        rhyme_data = response.json()

        if rhyme_data:
            rhymes = [entry["word"] for entry in rhyme_data]
            answer = f"Words that rhyme with '{word}': {', '.join(rhymes)}"
        else:
            answer = f"No rhymes found for '{word}'."

    except requests.RequestException:
        answer = "Couldn't fetch rhymes at this moment."

    await robot.play_face_reaction(FaceAnim.HAPPY_BIG_SMILE).completed()
    return {"llm_output": answer}
