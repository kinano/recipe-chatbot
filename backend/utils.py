from __future__ import annotations
from collections import namedtuple
import logging
import os
from typing import Final, List, Dict

import litellm  # type: ignore
from dotenv import load_dotenv
from backend.instrumentation import start_instrumentation
from opentelemetry import trace as trace_api
from openinference.instrumentation import using_metadata


tracer = trace_api.get_tracer(__name__)

"""Utility helpers for the recipe chatbot backend.

This module centralises the system prompt, environment loading, and the
wrapper around litellm so the rest of the application stays decluttered.
"""

logger = logging.getLogger(__name__)
start_instrumentation(logger)

# Ensure the .env file is loaded as early as possible.
load_dotenv(override=False)

# --- Constants -------------------------------------------------------------------

SYSTEM_PROMPT: Final[
    str
] = """
You are a helpful chef that can answer recipe questions and help plan meals.
The user will ask your recommendations for recipes and give you some constraints such as available ingredients, cooking and cleaning time and the number of people they are cooking for. They may also list their allergies or dietary restrictions.
Make sure to avoid recommending recipes that are not possible to make with the given constraints. Recommend substitutes for ingredients that are not available or cause harm to the user.
For complex questions, think step by step.
Format your response using markdown as follows:
===================
## Title
### Ingredients
* List the ingredients required for the recipe.
### Instructions
1. List the instructions for the recipe as a numbered list.
### Tips, Notes or Variations
* List any tips, notes or variations for the recipe as a bulleted list.
===================
Examples

Prompt: Give me a spaghetti recipe for 2 people.
Response:

## Spaghetti Carbonara
### Ingredients
* 200g spaghetti
* 100g pancetta
* 2 eggs
* 50g parmesan
* Salt and pepper to taste

### Instructions
1. Cook the spaghetti in a large pot of boiling water until al dente.
2. While the spaghetti is cooking, heat a large skillet over medium heat.
3. Add the pancetta to the skillet and cook until it is crispy.
4. Add the eggs to the skillet and stir well.
5. Add the parmesan to the skillet and stir well.
6. Add the spaghetti to the skillet and stir well.
7. Serve the spaghetti with the pancetta, eggs and parmesan.

### Tips
* If you don't have pancetta, you can use bacon or ham.
* If you don't have parmesan, you can use cheese.
* If you don't have eggs, you can use a substitute.

===================
It is okay to ask clarifying questions to the user if you are not sure about the constraints or if you need more information.
"""

# Fetch configuration *after* we loaded the .env file.
MODEL_NAME: Final[str] = os.environ.get("MODEL_NAME", "gpt-4o-mini")

# Define the RecipeRequest namedtuple with all our dimensions
RecipeRequest = namedtuple(
    "RecipeRequest",
    [
        "party_size",
        "dietary_restrictions",
        "cuisine_type",
        "user_persona",
        "scenario",
        "natural_language_query",
    ],
)

# --- Agent wrapper ---------------------------------------------------------------


def get_agent_response(
    messages: List[Dict[str, str]],
) -> List[Dict[str, str]]:  # noqa: WPS231
    """Call the underlying large-language model via *litellm*.

    Parameters
    ----------
    messages:
        The full conversation history. Each item is a dict with "role" and "content".

    Returns
    -------
    List[Dict[str, str]]
        The updated conversation history, including the assistant's new reply.
    """

    # litellm is model-agnostic; we only need to supply the model name and key.
    # The first message is assumed to be the system prompt if not explicitly provided
    # or if the history is empty. We'll ensure the system prompt is always first.
    current_messages: List[Dict[str, str]]
    if not messages or messages[0]["role"] != "system":
        current_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    else:
        current_messages = messages

    completion = litellm.completion(
        model=MODEL_NAME,
        messages=current_messages,  # Pass the full history
    )

    assistant_reply_content: str = completion["choices"][0]["message"][
        "content"
    ].strip()  # type: ignore[index]

    # Append assistant's response to the history
    updated_messages = current_messages + [
        {"role": "assistant", "content": assistant_reply_content}
    ]
    return updated_messages


def get_agent_response_with_metadata(
    recipe_request: RecipeRequest,
) -> List[Dict[str, str]]:
    metadata = {
        "party_size": recipe_request.party_size,
        "dietary_restrictions": recipe_request.dietary_restrictions,
        "cuisine_type": recipe_request.cuisine_type,
        "natural_language_query": recipe_request.natural_language_query,
        "experiment": os.environ.get("EXPERIMENT", "N/A"),
        "scenario": recipe_request.scenario,
        "user_persona": recipe_request.user_persona,
    }
    with using_metadata(metadata):
        return get_agent_response(
            messages=[
                {"role": "user", "content": recipe_request.natural_language_query}
            ]
        )

    # # span.set_attribute("available_ingredients", recipe_request.available_ingredients)
    # # span.set_attribute("party_size", recipe_request.party_size)
    # # span.set_attribute("dietary_restrictions", recipe_request.dietary_restrictions)
    # # span.set_attribute("cuisine_type", recipe_request.cuisine_type)
    # # span.set_attribute(
    # #     "available_kitchen_equipment", recipe_request.available_kitchen_equipment
    # # )
    # # span.set_attribute("meal_prep_time", recipe_request.meal_prep_time)
    # # span.set_attribute("natural_language_query", recipe_request.natural_language_query)
    # return get_agent_response(
    #     messages=[{"role": "user", "content": recipe_request.natural_language_query}]
    # )
