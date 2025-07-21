#!/usr/bin/env python3
"""
Enhanced script to generate knowledge-intensive synthetic queries for testing BM25 retriever.
Focuses on complex scenarios requiring specific recipe knowledge and salient facts.
"""

import json
from pathlib import Path
from typing import List, Dict, Any
import argparse


def load_recipes(recipes_path: str) -> List[Dict[str, Any]]:
    """Load recipes from JSON file."""
    with open(recipes_path, "r") as f:
        return json.load(f)


def analyze_recipe_complexity(recipes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Analyze recipes for complex knowledge patterns and salient facts."""
    complex_recipes = []

    for recipe in recipes:
        name = recipe.get("name", "")
        ingredients = recipe.get("ingredients", [])
        steps = recipe.get("steps", [])
        minutes = recipe.get("minutes", 0)
        tags = recipe.get("tags", [])
        description = recipe.get("description", "")
        recipe_id = recipe.get("id")

        # Identify salient facts
        salient_facts = []

        # Extreme cooking times
        if minutes > 480:  # Over 8 hours
            salient_facts.append(f"extremely_long_time_{minutes}")
        elif minutes > 240:  # Over 4 hours
            salient_facts.append(f"very_long_time_{minutes}")
        elif minutes <= 5:
            salient_facts.append(f"ultra_quick_{minutes}")

        # Unusual/specialty ingredients
        specialty_ingredients = []
        for ing in ingredients:
            ing_lower = ing.lower()
            if any(
                term in ing_lower
                for term in [
                    "kombu",
                    "seaweed",
                    "cardamom",
                    "saffron",
                    "truffle",
                    "duck",
                    "lamb",
                    "venison",
                    "xanthan",
                    "agar",
                    "tahini",
                    "miso",
                    "coconut milk",
                    "curry paste",
                    "fish sauce",
                    "worcestershire",
                    "anchovy",
                    "crab",
                    "black truffle",
                    "amish starter",
                ]
            ):
                specialty_ingredients.append(ing)
        if specialty_ingredients:
            salient_facts.append(f"specialty_ingredients")

        # Advanced techniques
        advanced_techniques = []
        for step in steps[:15]:
            step_lower = step.lower()
            techniques = [
                "confit",
                "sous vide",
                "flambé",
                "julienne",
                "brunoise",
                "emulsify",
                "tempering",
                "proving",
                "roux",
                "reduction",
                "caramelize",
                "deglaze",
                "fold",
                "whip",
                "roast",
                "braise",
            ]
            for tech in techniques:
                if tech in step_lower:
                    advanced_techniques.append(tech)
        if advanced_techniques:
            salient_facts.append(f"advanced_techniques")

        # High complexity indicators
        if len(ingredients) > 20:
            salient_facts.append(f"very_complex_{len(ingredients)}_ingredients")
        elif len(ingredients) > 15:
            salient_facts.append(f"complex_{len(ingredients)}_ingredients")

        if len(steps) > 25:
            salient_facts.append(f"many_steps_{len(steps)}")

        # Cultural/regional specificity
        cultural_tags = []
        for tag in tags:
            if any(
                culture in tag.lower()
                for culture in [
                    "french",
                    "italian",
                    "asian",
                    "indian",
                    "mexican",
                    "thai",
                    "moroccan",
                    "amish",
                    "cajun",
                    "chinese",
                    "japanese",
                    "korean",
                ]
            ):
                cultural_tags.append(tag)
        if cultural_tags:
            salient_facts.append(f"cultural_cuisine")

        if salient_facts:
            complex_recipes.append(
                {
                    "id": recipe_id,
                    "name": name,
                    "ingredients": ingredients,
                    "steps": steps,
                    "minutes": minutes,
                    "tags": tags,
                    "description": description,
                    "salient_facts": salient_facts,
                    "specialty_ingredients": specialty_ingredients,
                    "advanced_techniques": list(set(advanced_techniques)),
                    "cultural_tags": cultural_tags,
                    "complexity_score": len(salient_facts)
                    + (len(ingredients) / 10)
                    + (minutes / 100),
                }
            )

    # Sort by complexity score
    complex_recipes.sort(key=lambda x: x["complexity_score"], reverse=True)
    return complex_recipes


def generate_knowledge_intensive_queries(
    complex_recipes: List[Dict[str, Any]], num_queries: int = 200
) -> tuple[List[str], List[Dict[str, Any]]]:
    """Generate queries targeting specific recipe knowledge types."""

    queries = []
    query_metadata = []

    # 1. Appliance Settings Queries
    appliance_patterns = {
        "air fryer": ["air fryer", "air frying", "air-fry"],
        "oven": ["oven", "bake", "baking", "roast", "roasting"],
        "grill": ["grill", "grilling", "grilled"],
        "pressure cook": ["pressure cook", "pressure cooker", "instant pot"],
        "slow cook": ["slow cook", "slow cooker", "crockpot"],
        "microwave": ["microwave", "microwaving"],
        "broil": ["broil", "broiling", "broiler"],
        "sauté": ["sauté", "sautéing", "pan fry", "frying pan"]
    }
    
    for recipe in complex_recipes[:50]:
        recipe_id = recipe["id"]
        name = recipe["name"].lower()
        ingredients = [ing.lower() for ing in recipe.get("ingredients", [])]
        steps = [step.lower() for step in recipe.get("steps", [])]
        all_text = f"{name} {' '.join(ingredients)} {' '.join(steps)}"
        
        # Check for appliance mentions
        for appliance, patterns in appliance_patterns.items():
            if any(pattern in all_text for pattern in patterns):
                appliance_queries = [
                    f"What temperature for {appliance} {recipe['name'].split()[0] if recipe['name'] else 'recipe'}?",
                    f"How long to {appliance} {recipe['name'].split()[0] if recipe['name'] else 'food'}?",
                    f"{appliance.title()} settings for {recipe['name'].split()[0] if recipe['name'] else 'cooking'}?",
                    f"Best {appliance} temperature and time?",
                ]
                
                for aq in appliance_queries[:2]:
                    queries.append(aq)
                    query_metadata.append({
                        "query": aq,
                        "type": "appliance_settings",
                        "appliance": appliance,
                        "complexity_level": "equipment_specific",
                        "expected_document_ids": [recipe_id]
                    })
                break  # Only match one appliance per recipe

    # 2. Timing Specifics Queries
    timing_keywords = ["marinate", "rest", "rise", "chill", "steep", "simmer", "boil", "cook", "bake", "roast"]
    
    for recipe in complex_recipes[:50]:
        recipe_id = recipe["id"]
        steps = recipe.get("steps", [])
        name_words = recipe["name"].split()
        main_ingredient = name_words[0] if name_words else "food"
        
        # Look for timing mentions in recipe steps
        for step in steps:
            step_lower = step.lower()
            for keyword in timing_keywords:
                if keyword in step_lower and any(time_word in step_lower for time_word in ["minute", "hour", "overnight", "until"]):
                    timing_queries = [
                        f"How long to {keyword} {main_ingredient}?",
                        f"What's the {keyword} time for {main_ingredient}?",
                        f"How long should I {keyword} {main_ingredient}?",
                        f"Timing for {keyword}ing {main_ingredient}?"
                    ]
                    
                    for tq in timing_queries[:2]:
                        queries.append(tq)
                        query_metadata.append({
                            "query": tq,
                            "type": "timing_specifics",
                            "technique": keyword,
                            "complexity_level": "timing_precision",
                            "expected_document_ids": [recipe_id]
                        })
                    break  # Only one timing query per recipe
            else:
                continue
            break  # Found timing, move to next recipe

    # 3. Temperature Precision Queries
    protein_patterns = ["chicken", "beef", "pork", "turkey", "salmon", "fish", "steak", "lamb", "duck", "shrimp"]
    
    for recipe in complex_recipes[:50]:
        recipe_id = recipe["id"]
        name = recipe["name"].lower()
        ingredients = [ing.lower() for ing in recipe.get("ingredients", [])]
        steps = [step.lower() for step in recipe.get("steps", [])]
        all_text = f"{name} {' '.join(ingredients)} {' '.join(steps)}"
        
        # Find protein types in the recipe
        protein_found = None
        for protein in protein_patterns:
            if protein in all_text:
                protein_found = protein
                break
        
        # Generate temperature queries for any protein-containing recipe
        if protein_found:
            temp_queries = [
                f"What internal temp for medium-rare {protein_found}?",
                f"Cooking temperature for {protein_found}?",
                f"What temperature should {protein_found} reach?",
                f"Internal temperature for safe {protein_found}?"
            ]
            
            for temp_q in temp_queries[:2]:
                queries.append(temp_q)
                query_metadata.append({
                    "query": temp_q,
                    "type": "temperature_precision",
                    "protein": protein_found,
                    "complexity_level": "temp_precision",
                    "expected_document_ids": [recipe_id]
                })
                if len([q for q in query_metadata if q["type"] == "temperature_precision"]) >= 50:
                    break
            if len([q for q in query_metadata if q["type"] == "temperature_precision"]) >= 50:
                break

    # 4. Technique Details Queries
    technique_patterns = {
        "crispy": ["crispy", "crisp", "crunchy"],
        "tender": ["tender", "soft", "moist"],
        "caramelized": ["caramelize", "caramelized", "golden"],
        "seared": ["sear", "seared", "brown"],
        "flaky": ["flaky", "layers", "pastry"],
        "juicy": ["juicy", "moist", "succulent"]
    }
    
    for recipe in complex_recipes[:50]:
        recipe_id = recipe["id"]
        name = recipe["name"].lower()
        steps = [step.lower() for step in recipe.get("steps", [])]
        all_text = f"{name} {' '.join(steps)}"
        name_words = recipe["name"].split()
        main_dish = name_words[0] if name_words else "dish"
        
        # Check for technique mentions
        for technique, patterns in technique_patterns.items():
            if any(pattern in all_text for pattern in patterns):
                technique_queries = [
                    f"How to get {technique} {main_dish}?",
                    f"What makes {main_dish} {technique}?",
                    f"Technique for {technique} {main_dish}?",
                    f"How to achieve {technique} texture?"
                ]
                
                for tech_q in technique_queries[:2]:
                    queries.append(tech_q)
                    query_metadata.append({
                        "query": tech_q,
                        "type": "technique_details",
                        "technique": technique,
                        "complexity_level": "technique_mastery",
                        "expected_document_ids": [recipe_id]
                    })
                break  # Only one technique query per recipe

    # Add padding queries to reach target number
    current_count = len(queries)
    remaining = max(0, num_queries - current_count)
    
    if remaining > 0:
        # Generate additional queries from the four main types
        padding_appliance = [
            "Air fryer temperature for crispy vegetables?",
            "Oven settings for perfect roast?", 
            "Grill temperature for medium steaks?",
            "Pressure cooker timing for tender meat?",
            "Slow cooker settings for stews?"
        ]
        
        padding_timing = [
            "How long to marinate chicken for teriyaki?",
            "Rest time for bread dough?",
            "Simmer time for perfect sauce?", 
            "Chill time for setting desserts?",
            "Rise time for pizza dough?"
        ]
        
        padding_temperature = [
            "What internal temp for medium-rare steak?",
            "Safe cooking temperature for chicken?",
            "Perfect temperature for fish?",
            "Internal temp for pork tenderloin?",
            "Temperature for medium turkey?"
        ]
        
        padding_technique = [
            "How to get crispy skin on roasted chicken?",
            "Technique for tender braised meat?",
            "How to achieve caramelized onions?",
            "Method for flaky pastry?",
            "How to sear meat perfectly?"
        ]
        
        all_padding = padding_appliance + padding_timing + padding_temperature + padding_technique
        
        for i, padding_query in enumerate(all_padding[:remaining]):
            queries.append(padding_query)
            # Determine type based on which padding list it came from
            if i < len(padding_appliance):
                query_type = "appliance_settings"
                complexity = "equipment_specific"
            elif i < len(padding_appliance) + len(padding_timing):
                query_type = "timing_specifics"
                complexity = "timing_precision"
            elif i < len(padding_appliance) + len(padding_timing) + len(padding_temperature):
                query_type = "temperature_precision"
                complexity = "temp_precision"
            else:
                query_type = "technique_details"
                complexity = "technique_mastery"
                
            query_metadata.append({
                "query": padding_query,
                "type": query_type,
                "complexity_level": complexity,
                "expected_document_ids": [complex_recipes[0]["id"]] if complex_recipes else [1]
            })

    # Remove duplicates while preserving metadata
    seen_queries = set()
    unique_queries = []
    unique_metadata = []

    for query, metadata in zip(queries, query_metadata):
        if query not in seen_queries:
            seen_queries.add(query)
            unique_queries.append(query)
            unique_metadata.append(metadata)

    return unique_queries[:num_queries], unique_metadata[:num_queries]


def save_queries(
    queries: List[str], query_metadata: List[Dict[str, Any]], output_path: str
):
    """Save generated queries with knowledge evaluation data to file."""
    output_data = {
        "queries": queries,
        "query_metadata": query_metadata,
        "generation_metadata": {
            "total_queries": len(queries),
            "generation_method": "knowledge_intensive_salient_facts",
            "focus": "complex_recipe_expertise_evaluation",
            "query_types": list(set(q.get("type", "unknown") for q in query_metadata)),
        },
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=2)

    print(
        f"Generated {len(queries)} knowledge-intensive queries saved to {output_path}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate knowledge-intensive synthetic queries for recipe retrieval testing"
    )
    parser.add_argument(
        "--recipes-path",
        default="../data/processed_recipes.json",
        help="Path to processed recipes JSON file",
    )
    parser.add_argument(
        "--output-path",
        default="../data/knowledge_intensive_queries.json",
        help="Output path for generated queries",
    )
    parser.add_argument(
        "--num-queries", type=int, default=200, help="Number of queries to generate"
    )

    args = parser.parse_args()

    # Convert relative paths to absolute
    script_dir = Path(__file__).parent
    recipes_path = script_dir / args.recipes_path
    output_path = script_dir / args.output_path

    print(f"Loading recipes from {recipes_path}")
    recipes = load_recipes(recipes_path)
    print(f"Loaded {len(recipes)} recipes")

    print("Analyzing recipe complexity and salient facts...")
    complex_recipes = analyze_recipe_complexity(recipes)
    print(f"Found {len(complex_recipes)} recipes with complex knowledge requirements")

    print(f"Generating {args.num_queries} knowledge-intensive queries...")
    queries, query_metadata = generate_knowledge_intensive_queries(
        complex_recipes, args.num_queries
    )

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    save_queries(queries, query_metadata, output_path)

    print(
        f"\nGenerated {len(queries)} queries across {len(set(q.get('type', 'unknown') for q in query_metadata))} knowledge categories"
    )
    print("\nSample knowledge-intensive queries:")
    for i, query in enumerate(queries[:15], 1):
        print(f"{i:2d}. {query}")


if __name__ == "__main__":
    main()
