from typing import List
from backend.utils import get_agent_response_with_metadata, RecipeRequest

dimensions = [
    "available_ingredients",
    "party_size",
    "dietary_restrictions",
    "cuisine_type",
    "available_kitchen_equipment",
    "meal_prep_time",
]

available_ingredients_examples = [
    "chicken",
    "beef",
    "pork",
    "fish",
    "vegetables",
    "fruits",
    "grains",
    "dairy",
]

party_size_examples = ["1", "2", "3", "4", "5", "6", "7", "8", "9+"]
dietary_restrictions_examples = [
    "vegan",
    "vegetarian",
    "gluten-free",
    "dairy-free",
    "halal",
    "kosher",
    "shellfish-free",
    "peanut-free",
    "tree-nut-free",
    "soy-free",
    "egg-free",
    "gluten-free",
    "dairy-free",
]

cuisine_type_examples = [
    "American",
    "Italian",
    "Mexican",
    "Japanese",
    "Chinese",
    "Indian",
    "Thai",
    "Mediterranean",
    "French",
    "Greek",
    "Spanish",
    "Korean",
    "Vietnamese",
    "Indian",
]

available_kitchen_equipment_examples = [
    "oven",
    "stove",
    "microwave",
    "refrigerator",
    "freezer",
    "blender",
    "food processor",
]

meal_prep_time_examples = [
    "10 minutes",
    "30 minutes",
    "1 hour",
    "2 hours",
    "3 hours",
    "4 hours",
    "5 hours",
]

# List of realistic recipe combinations
# List of recipe requests with their natural language queries
recipe_requests: List[RecipeRequest] = [
    # Quick family dinner scenario
    RecipeRequest(
        available_ingredients=["chicken", "vegetables", "grains"],
        party_size="4",
        dietary_restrictions=["gluten-free"],
        cuisine_type="American",
        available_kitchen_equipment=["oven", "stove", "refrigerator"],
        meal_prep_time="30 minutes",
        natural_language_query="I need a quick dinner idea for my family of 4. We have chicken, some vegetables, and grains in the fridge. "
        "One of us is gluten-free, and we'd prefer something American-style. "
        "We have a basic kitchen with an oven, stove, and fridge. "
        "Something that takes about 30 minutes would be perfect!",
    ),
    # Vegetarian dinner party
    RecipeRequest(
        available_ingredients=["vegetables", "grains", "dairy"],
        party_size="6",
        dietary_restrictions=["vegetarian"],
        cuisine_type="Mediterranean",
        available_kitchen_equipment=["oven", "stove", "blender"],
        meal_prep_time="1 hour",
        natural_language_query="I'm hosting a dinner party for 6 people this weekend. "
        "I need a vegetarian Mediterranean recipe that will impress my guests. "
        "I have plenty of fresh vegetables, grains, and dairy products. "
        "My kitchen is well-equipped with an oven, stove, and blender. "
        "I can spend about an hour preparing the meal.",
    ),
    # Quick vegan lunch
    RecipeRequest(
        available_ingredients=["vegetables", "fruits", "grains"],
        party_size="1",
        dietary_restrictions=["vegan", "gluten-free"],
        cuisine_type="Thai",
        available_kitchen_equipment=["stove", "blender"],
        meal_prep_time="30 minutes",
        natural_language_query="I'm looking for a quick vegan and gluten-free lunch idea. "
        "I have some vegetables, fruits, and grains at home. "
        "I'd love something with Thai flavors if possible. "
        "I only have a stove and blender available, and I need it ready in 30 minutes or less.",
    ),
    # Kosher dinner party
    RecipeRequest(
        available_ingredients=["chicken", "vegetables", "grains"],
        party_size="8",
        dietary_restrictions=["kosher"],
        cuisine_type="Mediterranean",
        available_kitchen_equipment=["oven", "stove", "refrigerator"],
        meal_prep_time="2 hours",
        natural_language_query="I'm planning a kosher dinner for 8 people. "
        "I have chicken, vegetables, and grains available. "
        "I'd like to make something Mediterranean-style. "
        "I have a full kitchen with oven, stove, and fridge. "
        "I can spend a couple of hours preparing the meal.",
    ),
    # Quick Mexican lunch
    RecipeRequest(
        available_ingredients=["beef", "vegetables", "grains", "dairy"],
        party_size="2",
        dietary_restrictions=[],
        cuisine_type="Mexican",
        available_kitchen_equipment=["stove", "microwave"],
        meal_prep_time="30 minutes",
        natural_language_query="My partner and I want to make a quick Mexican lunch. "
        "We have ground beef, vegetables, grains, and some dairy products. "
        "We only have access to a stove and microwave right now. "
        "Something that takes about 30 minutes would be great!",
    ),
    # Allergen-free dinner
    RecipeRequest(
        available_ingredients=["chicken", "vegetables", "grains"],
        party_size="4",
        dietary_restrictions=["peanut-free", "tree-nut-free", "shellfish-free"],
        cuisine_type="American",
        available_kitchen_equipment=["oven", "stove", "refrigerator"],
        meal_prep_time="1 hour",
        natural_language_query="I need a family dinner recipe that's safe for my kids with allergies. "
        "It needs to be free of peanuts, tree nuts, and shellfish. "
        "We have chicken, vegetables, and grains available. "
        "Something American-style would be perfect. "
        "We have a full kitchen and can spend about an hour cooking.",
    ),
    # Vegan Indian feast
    RecipeRequest(
        available_ingredients=["vegetables", "grains", "fruits"],
        party_size="5",
        dietary_restrictions=["vegan"],
        cuisine_type="Indian",
        available_kitchen_equipment=["stove", "blender", "food processor"],
        meal_prep_time="2 hours",
        natural_language_query="I'm planning a vegan Indian feast for 5 people. "
        "I have lots of vegetables, grains, and fruits to work with. "
        "My kitchen is well-equipped with a stove, blender, and food processor. "
        "I'm willing to spend a couple of hours preparing something special!",
    ),
    # Quick Spanish tapas
    RecipeRequest(
        available_ingredients=["fish", "vegetables", "dairy"],
        party_size="3",
        dietary_restrictions=[],
        cuisine_type="Spanish",
        available_kitchen_equipment=["stove", "oven"],
        meal_prep_time="30 minutes",
        natural_language_query="I want to make some quick Spanish tapas for 3 people. "
        "I have some fish, vegetables, and dairy products. "
        "I have access to a stove and oven. "
        "Looking for something that can be ready in 30 minutes!",
    ),
    # Dairy-free dinner party
    RecipeRequest(
        available_ingredients=["chicken", "vegetables", "grains"],
        party_size="6",
        dietary_restrictions=["dairy-free"],
        cuisine_type="Thai",
        available_kitchen_equipment=["stove", "blender", "food processor"],
        meal_prep_time="1 hour",
        natural_language_query="I'm hosting a dinner party for 6 people, and one of my guests is lactose intolerant. "
        "I'd like to make a dairy-free Thai dish. "
        "I have chicken, vegetables, and grains available. "
        "My kitchen has a stove, blender, and food processor. "
        "I can spend about an hour preparing the meal.",
    ),
    # Family Vietnamese dinner
    RecipeRequest(
        available_ingredients=["pork", "vegetables", "grains"],
        party_size="4",
        dietary_restrictions=[],
        cuisine_type="Vietnamese",
        available_kitchen_equipment=["stove", "blender"],
        meal_prep_time="1 hour",
        natural_language_query="I want to make a Vietnamese dinner for my family of 4. "
        "We have pork, vegetables, and grains in the pantry. "
        "I have a stove and blender available. "
        "Something that takes about an hour to prepare would be perfect. "
        "Any suggestions for an authentic Vietnamese dish?",
    ),
]


if __name__ == "__main__":
    for recipe_request in recipe_requests:
        get_agent_response_with_metadata(recipe_request=recipe_request)
