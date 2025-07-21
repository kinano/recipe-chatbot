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
    """Generate queries requiring specific recipe knowledge and salient facts."""

    queries = []
    query_metadata = []

    # 1. Extreme cooking time knowledge queries
    for recipe in complex_recipes[:25]:
        minutes = recipe["minutes"]
        recipe_id = recipe["id"]

        if minutes > 480:  # Over 8 hours
            time_queries = [
                f"recipes that take more than 8 hours to cook",
                f"extremely long cooking time recipes over {minutes//60} hours",
                f"all day cooking projects requiring {minutes} minutes",
                f"recipes with cooking time exceeding 8 hours",
            ]
        elif minutes > 240:  # Over 4 hours
            time_queries = [
                f"recipes that take over 4 hours to make",
                f"long cooking time recipes requiring {minutes//60} hours",
                f"slow cooking recipes taking {minutes} minutes",
            ]
        elif minutes <= 5:
            time_queries = [
                f"ultra quick {minutes} minute recipes",
                f"recipes ready in under 5 minutes",
                f"fastest recipes taking only {minutes} minutes",
            ]
        else:
            continue

        for tq in time_queries[:2]:
            queries.append(tq)
            query_metadata.append(
                {
                    "query": tq,
                    "type": "extreme_cooking_time_knowledge",
                    "cooking_time_minutes": minutes,
                    "complexity_level": "time_intensive",
                    "expected_document_ids": [recipe_id],
                }
            )

    # 2. Specialty ingredient knowledge queries
    for recipe in complex_recipes:
        if recipe["specialty_ingredients"]:
            recipe_id = recipe["id"]

            for ing in recipe["specialty_ingredients"][:3]:
                ing_queries = [
                    f"recipes using {ing}",
                    f"how to cook with {ing}",
                    f"specialty dishes featuring {ing}",
                    f"gourmet recipes with {ing}",
                    f"what cuisine uses {ing}",
                ]

                for iq in ing_queries[:3]:
                    queries.append(iq)
                    query_metadata.append(
                        {
                            "query": iq,
                            "type": "specialty_ingredient_knowledge",
                            "specialty_ingredient": ing,
                            "complexity_level": "rare_ingredient",
                            "expected_document_ids": [recipe_id],
                        }
                    )

    # 3. Advanced cooking technique queries
    for recipe in complex_recipes:
        if recipe["advanced_techniques"]:
            recipe_id = recipe["id"]

            for technique in recipe["advanced_techniques"][:2]:
                tech_queries = [
                    f"recipes using {technique} technique",
                    f"how to {technique} in professional cooking",
                    f"advanced {technique} cooking methods",
                    f"dishes requiring {technique} skills",
                    f"{technique} technique in recipe preparation",
                ]

                for tq in tech_queries[:2]:
                    queries.append(tq)
                    query_metadata.append(
                        {
                            "query": tq,
                            "type": "advanced_technique_knowledge",
                            "technique": technique,
                            "complexity_level": "professional_skill",
                            "expected_document_ids": [recipe_id],
                        }
                    )

    # 4. High complexity recipe queries
    for recipe in complex_recipes[:15]:
        recipe_id = recipe["id"]
        ing_count = len(recipe["ingredients"])

        if ing_count > 20:
            complexity_queries = [
                f"recipes with over 20 ingredients",
                f"extremely complex recipes requiring {ing_count} ingredients",
                f"elaborate dishes with extensive ingredient lists",
                f"most complex recipes in professional cooking",
            ]
        elif ing_count > 15:
            complexity_queries = [
                f"recipes with over 15 ingredients",
                f"complex recipes requiring {ing_count} different ingredients",
            ]
        else:
            continue

        for cq in complexity_queries[:2]:
            queries.append(cq)
            query_metadata.append(
                {
                    "query": cq,
                    "type": "recipe_complexity_knowledge",
                    "ingredient_count": ing_count,
                    "complexity_level": "very_high_complexity",
                    "expected_document_ids": [recipe_id],
                }
            )

    # 5. Cultural cuisine expertise queries
    for recipe in complex_recipes:
        if recipe["cultural_tags"]:
            recipe_id = recipe["id"]

            for tag in recipe["cultural_tags"][:1]:
                culture_queries = [
                    f"authentic {tag} recipes",
                    f"traditional {tag} cooking techniques",
                    f"genuine {tag} cuisine dishes",
                    f"classic {tag} recipe methods",
                    f"expert {tag} cooking knowledge",
                ]

                for cul_q in culture_queries[:2]:
                    queries.append(cul_q)
                    query_metadata.append(
                        {
                            "query": cul_q,
                            "type": "cultural_cuisine_expertise",
                            "cultural_tag": tag,
                            "complexity_level": "cultural_authenticity",
                            "expected_document_ids": [recipe_id],
                        }
                    )

    # 6. Specific recipe name knowledge
    for recipe in complex_recipes[:20]:
        recipe_id = recipe["id"]
        name = recipe["name"]
        words = name.split()

        if len(words) >= 4:
            name_queries = [
                f"recipe for {' '.join(words[:3])}",
                f"how to make {' '.join(words[:4])}",
                f"ingredients needed for {' '.join(words[:3])}",
                f"cooking instructions for {' '.join(words[:3])}",
                f"preparation steps for {' '.join(words[:2])}",
            ]

            for nq in name_queries[:2]:
                queries.append(nq)
                query_metadata.append(
                    {
                        "query": nq,
                        "type": "specific_recipe_knowledge",
                        "full_recipe_name": name,
                        "complexity_level": "specific_dish_expertise",
                        "expected_document_ids": [recipe_id],
                    }
                )

    # 7. Multi-step procedure knowledge
    for recipe in complex_recipes:
        if len(recipe["steps"]) > 20:
            recipe_id = recipe["id"]
            step_count = len(recipe["steps"])

            procedure_queries = [
                f"recipes with over 20 detailed cooking steps",
                f"complex multi-step cooking procedures",
                f"elaborate recipes requiring {step_count} steps",
                f"detailed cooking processes with many stages",
            ]

            for pq in procedure_queries[:2]:
                queries.append(pq)
                query_metadata.append(
                    {
                        "query": pq,
                        "type": "cooking_procedure_expertise",
                        "step_count": step_count,
                        "complexity_level": "multi_stage_process",
                        "expected_document_ids": [recipe_id],
                    }
                )

    # 8. Combined complexity expertise queries
    for recipe in complex_recipes[:10]:
        recipe_id = recipe["id"]
        salient_facts = recipe["salient_facts"]

        if len(salient_facts) >= 3:
            expert_queries = [
                f"most challenging recipes requiring expert knowledge",
                f"professional chef level cooking complexity",
                f"recipes combining multiple advanced techniques",
                f"expert-level culinary knowledge requirements",
                f"master chef complexity recipe challenges",
            ]

            for eq in expert_queries[:2]:
                queries.append(eq)
                query_metadata.append(
                    {
                        "query": eq,
                        "type": "expert_culinary_knowledge",
                        "salient_facts": salient_facts,
                        "complexity_level": "master_chef_level",
                        "expected_document_ids": [recipe_id],
                    }
                )

    # 9. Nutritional and dietary knowledge queries
    nutrition_queries = [
        "high calorie complex recipes",
        "recipes with detailed nutritional information",
        "gourmet recipes with nutritional complexity",
        "elaborate dishes with specific dietary considerations",
        "complex recipes with precise nutrition data",
        "recipes requiring nutritional calculations",
        "dietary-specific complex cooking",
        "sophisticated recipes with nutrition focus",
    ]

    for nq in nutrition_queries:
        queries.append(nq)
        query_metadata.append(
            {
                "query": nq,
                "type": "nutritional_knowledge",
                "complexity_level": "dietary_expertise",
                "expected_document_ids": [r["id"] for r in complex_recipes[:3]],
            }
        )

    # 10. Equipment and technique expertise queries
    equipment_queries = [
        "recipes requiring specialized cooking equipment",
        "professional kitchen technique recipes",
        "advanced cooking tool requirements",
        "restaurant-grade cooking methods",
        "complex recipes needing special tools",
        "professional chef equipment recipes",
        "sophisticated cooking apparatus requirements",
        "high-end kitchen technique recipes",
        "specialized appliance cooking methods",
        "commercial kitchen recipe techniques",
    ]

    for eq in equipment_queries:
        queries.append(eq)
        query_metadata.append(
            {
                "query": eq,
                "type": "equipment_expertise",
                "complexity_level": "professional_equipment",
                "expected_document_ids": [r["id"] for r in complex_recipes[:3]],
            }
        )

    # 11. Additional complexity-based queries to reach 200
    additional_queries = []
    for recipe in complex_recipes[:30]:
        recipe_id = recipe["id"]
        name = recipe["name"]
        ing_count = recipe.get("n_ingredients", 0)
        step_count = recipe.get("n_steps", 0)
        minutes = recipe.get("minutes", 0)
        
        # Generate varied queries based on different aspects
        if ing_count > 10:
            additional_queries.append({
                "query": f"complex recipes with {ing_count} ingredients like {' '.join(name.split()[:2])}",
                "type": "recipe_complexity_knowledge",
                "complexity_level": "ingredient_complexity",
                "expected_document_ids": [recipe_id]
            })
        
        if step_count > 10:
            additional_queries.append({
                "query": f"multi-step recipes requiring {step_count} detailed steps",
                "type": "cooking_procedure_expertise", 
                "complexity_level": "procedural_complexity",
                "expected_document_ids": [recipe_id]
            })
            
        if minutes > 60:
            additional_queries.append({
                "query": f"time-intensive recipes taking {minutes} minutes to complete",
                "type": "extreme_cooking_time_knowledge",
                "complexity_level": "time_complexity", 
                "expected_document_ids": [recipe_id]
            })
    
    # Add additional queries to main list
    for aq in additional_queries:
        queries.append(aq["query"])
        query_metadata.append({
            "query": aq["query"],
            "type": aq["type"],
            "complexity_level": aq["complexity_level"],
            "expected_document_ids": aq["expected_document_ids"]
        })

    # 12. Final padding queries to ensure we reach 200
    padding_queries = [
        "extremely complex gourmet recipes",
        "master chef level recipe challenges",
        "sophisticated culinary technique requirements", 
        "professional cooking complexity standards",
        "advanced recipe preparation methods",
        "expert-level cooking knowledge needed",
        "complex recipe execution skills",
        "high-complexity culinary challenges"
    ]
    
    for pq in padding_queries:
        queries.append(pq)
        query_metadata.append({
            "query": pq,
            "type": "expert_culinary_knowledge",
            "complexity_level": "master_chef_level",
            "expected_document_ids": [r["id"] for r in complex_recipes[:3]]
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
