import csv
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from litellm import completion
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Default model if not specified in .env
DEFAULT_MODEL = "ollama/llama3"


class RecipeDietaryJudge:
    """An LLM-based judge that evaluates recipe responses against dietary restrictions."""

    SYSTEM_PROMPT = """You are an expert recipe evaluator and dietary restriction specialist. Your role is to:
1. Analyze user queries requesting recipes with specific dietary restrictions
2. Evaluate the provided recipe responses to ensure they comply with the stated dietary restrictions
3. Make a clear judgement on whether the response meets or violates the dietary requirements
4. Provide detailed reasoning for your judgement
5. Assess your confidence in the judgement based on the quality and completeness of the information

You must be thorough in your analysis and consider:
- All explicitly stated dietary restrictions in the user query as well as the user's constraints expressed in the input query.
- Potential hidden ingredients that might violate restrictions
- The completeness and clarity of the recipe response
- Whether substitutions or alternatives are provided when needed

Your evaluation should be fair, consistent, and focused solely on dietary compliance.

IMPORTANT: You must respond with a valid JSON object in the following format:
{
    "llm_judge_label": "pass" or "fail",
    "reason": "detailed explanation of your judgement",
    "confidence": "low", "medium", or "high"
}

Examples:

[
  {
    "user query": "I want something light but filling",
    "expected_label": "fail",
    "application response": "I recommend trying a **Grilled Chicken and Vegetable Quinoa Salad**. It's light yet satisfying, packed with protein and fresh flavors. Here’s how to make it for two people:

    ### Ingredients:
    - 1/2 cup quinoa
    - 2 boneless, skinless chicken breasts
    - 1 small zucchini
    - 1 small red bell pepper
    - 1 tablespoon olive oil
    - 1 lemon (for juice)
    - Salt and pepper to taste
    - 1 teaspoon dried oregano or thyme (optional)
    - Fresh parsley (optional, for garnish)

    ### Instructions:

    1. **Cook the Quinoa:**
      - Rinse the quinoa under cold water using a fine mesh sieve.
      - In a small saucepan, combine 1/2 cup quinoa with 1 cup water and a pinch of salt.
      - Bring to a boil over medium-high heat, then reduce to low heat and cover.
      - Simmer for about 15 minutes, or until the water is absorbed and the quinoa is fluffy.
      - Remove from heat and let it sit, covered, for 5 minutes. Fluff with a fork and set aside.

    2. **Prepare the Vegetables:**
      - While quinoa is cooking, wash and slice the zucchini and red bell pepper into thin strips.
      - Toss the vegetables with 1/2 tablespoon olive oil, a pinch of salt, pepper, and optional dried herbs.

    3. **Grill the Chicken and Vegetables:**
      - Preheat your grill or grill pan over medium-high heat.
      - Season the chicken breasts with salt, pepper, and a little lemon juice.
      - Grill the chicken for about 6-7 minutes per side, or until fully cooked and juices run clear. Let rest for a few minutes, then slice into strips.
      - Grill the vegetables for about 3-4 minutes per side until tender and slightly charred.

    4. **Assemble the Salad:**
      - In a large bowl, combine the cooked quinoa, grilled vegetables, and sliced chicken.
      - Drizzle with the remaining olive oil and the juice of one lemon.
      - Toss gently to combine and adjust seasoning with salt and pepper if necessary.

    5. **Serve:**
      - Garnish with chopped fresh parsley if desired.
      - Serve immediately for a warm salad or chilled for a refreshing cold dish.

    This recipe yields two satisfying portions that are light but filling. Enjoy your wholesome, flavorful meal!",
    "reason: "The recipe includes quinoa, which is a grain and contains carbohydrates. For a low-carb diet, the carbohydrate content should be significantly reduced, typically under 50g per day. Quinoa is relatively high in carbohydrates, with about 39g of carbs per cup cooked. Even though the recipe uses only 1/2 cup of quinoa, it still contributes a significant amount of carbohydrates, which may not align with a low-carb dietary restriction. The rest of the ingredients, such as chicken and vegetables, are generally low in carbs, but the inclusion of quinoa makes the overall dish unsuitable for a strict low-carb diet."
  },
  {
    "user query": "I'm flexitarian leaning vegan",
    "expected_label": "pass",
    "application response": "Great choice! Here's a flavorful and nutritious recipe for **Chickpea and Spinach Curry**. It’s vegan, hearty, and perfect for a cozy dinner for two.

    ### Chickpea and Spinach Curry

    #### Ingredients:
    - 1 tablespoon olive oil
    - 1 medium onion, finely chopped
    - 3 cloves garlic, minced
    - 1-inch piece ginger, grated
    - 1 teaspoon ground cumin
    - 1 teaspoon ground coriander
    - 1/2 teaspoon turmeric
    - 1/2 teaspoon paprika
    - 1/4 teaspoon cayenne pepper (optional for heat)
    - 1 can (15 oz) chickpeas, drained and rinsed
    - 1 can (14 oz) diced tomatoes
    - 1 cup coconut milk (or any plant-based milk for a lighter version)
    - 4 cups fresh spinach, chopped
    - Salt and pepper to taste
    - Fresh cilantro for garnish (optional)
    - Cooked rice or naan for serving

    #### Instructions:

    1. **Sauté the Aromatics:**
      - Heat the olive oil in a large skillet or saucepan over medium heat.
      - Add the chopped onion and cook for about 5 minutes, until it becomes translucent and soft.
      - Stir in the minced garlic and grated ginger; cook for another 1 minute until fragrant.

    2. **Add Spices:**
      - Sprinkle in the cumin, coriander, turmeric, paprika, and cayenne (if using).
      - Stir well, letting the spices toast for about 30 seconds to activate their flavors.

    3. **Incorporate Chickpeas and Tomatoes:**
      - Add the drained chickpeas and diced tomatoes (including juices).
      - Mix everything thoroughly, and let it simmer for 10 minutes, allowing flavors to meld.

    4. **Pour in Coconut Milk:**
      - Stir in the coconut milk, bring to a gentle simmer, and cook for another 10 minutes until the sauce thickens slightly.
      - Season with salt and pepper to taste.

    5. **Add Spinach:**
      - Stir in the chopped spinach and cook for about 2-3 minutes until wilted.
      
    6. **Serve:**
      - Ladle the curry over cooked rice or serve with warm naan.
      - Garnish with fresh cilantro if desired.

    Enjoy your vibrant Chickpea and Spinach Curry—nutritious, comforting, and perfect for a flexitarian, vegan-friendly meal!"
  }
]
"""

    def __init__(self, model_name: Optional[str] = None):
        """Initialize the judge with the specified model.

        Args:
            model_name: Optional model name to override the one from .env file.
            If not provided, uses MODEL_NAME from .env or falls back to DEFAULT_MODEL.
        """
        # Get model name from parameter, .env, or default
        self.model_name = model_name or os.getenv("MODEL_NAME", DEFAULT_MODEL)
        logger.info(f"Initializing judge with model: {self.model_name}")

        # Test the model connection
        try:
            logger.info("Testing model connection...")
            # Simple test completion to verify model access
            completion(
                model=self.model_name,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5,
                timeout=30,  # Increased timeout for slower models
            )
            logger.info("Model connection successful")
        except Exception as e:
            logger.error(f"Failed to connect to model: {str(e)}")
            raise ValueError(
                f"Failed to connect to model '{self.model_name}'. "
                "Please ensure Ollama is running and the model is available. "
                f"Error: {str(e)}"
            )

    def evaluate_response(
        self, query: str, dietary_restriction: str, response: str
    ) -> Dict:
        """Evaluate a single recipe response against dietary restrictions."""
        logger.info(
            f"Evaluating response for dietary restriction: {dietary_restriction}"
        )
        logger.debug(f"Query: {query}")
        logger.debug(f"Response: {response}")

        prompt = f"""Please evaluate the following recipe request and response:

User Query: {query}
Dietary Restriction: {dietary_restriction}
Recipe Response: {response}

Based on this information, please provide your evaluation in the following JSON format:
{{
    "llm_judge_label": "pass" or "fail",
    "reason": "detailed explanation of your judgement",
    "confidence": "low", "medium", or "high"
}}

Focus on whether the recipe response properly addresses the dietary restriction."""

        try:
            logger.info("Sending request to model...")
            # Call model using litellm
            completion_response = completion(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
                max_tokens=1000,
            )

            # Extract the response text
            response_text = completion_response.choices[0].message.content
            logger.debug(f"Raw model response: {response_text}")

            # Try to parse the JSON response
            try:
                # Find JSON in the response (in case there's additional text)
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response_text[json_start:json_end]
                    evaluation = json.loads(json_str)
                    logger.info(
                        f"Evaluation result: {evaluation['llm_judge_label']} (confidence: {evaluation['confidence']})"
                    )
                    return evaluation
                else:
                    logger.error("No JSON object found in model response")
                    raise json.JSONDecodeError(
                        "No JSON object found in response", response_text, 0
                    )
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse model response as JSON: {str(e)}")
                # Fallback if the response isn't valid JSON
                return {
                    "llm_judge_label": "fail",
                    "reason": "Failed to parse LLM response as valid JSON",
                    "confidence": "low",
                }

        except Exception as e:
            logger.error(f"Error during evaluation: {str(e)}")
            return {
                "llm_judge_label": "fail",
                "reason": f"Error during evaluation: {str(e)}",
                "confidence": "low",
            }

    def process_csv_file(self, input_file: str, output_dir: str = "data") -> str:
        """Process a CSV file of recipe evaluations and generate output."""
        logger.info(f"Processing input file: {input_file}")

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Output directory: {output_dir}")

        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        output_file = os.path.join(output_dir, f"llm_as_judge_eval_run_{timestamp}.csv")
        logger.info(f"Output file will be: {output_file}")

        # Process input file
        with (
            open(input_file, "r") as infile,
            open(output_file, "w", newline="") as outfile,
        ):
            reader = csv.DictReader(infile)
            total_rows = sum(1 for _ in csv.DictReader(open(input_file, "r")))
            logger.info(f"Found {total_rows} rows to process")

            # Reset file pointer
            infile.seek(0)
            next(reader)  # Skip header

            fieldnames = reader.fieldnames + ["llm_judge_label", "reason", "confidence"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for i, row in enumerate(reader, 1):
                logger.info(f"Processing row {i}/{total_rows}")
                # Evaluate the response
                evaluation = self.evaluate_response(
                    query=row["query"],
                    dietary_restriction=row["dietary_restriction"],
                    response=row["response"],
                )

                # Add evaluation results to the row
                row.update(
                    {
                        "llm_judge_label": evaluation["llm_judge_label"],
                        "reason": evaluation["reason"],
                        "confidence": evaluation["confidence"],
                    }
                )

                writer.writerow(row)
                logger.info(f"Completed row {i}/{total_rows}")

        logger.info(f"Processing complete. Results written to: {output_file}")
        return output_file


def main():
    """Command line interface for the recipe dietary judge."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Evaluate recipe responses against dietary restrictions"
    )
    parser.add_argument("input_file", help="Path to input CSV file")
    parser.add_argument("--output-dir", help="Directory for output files")
    parser.add_argument(
        "--model",
        help=f"Model to use (default: from MODEL_NAME in .env or {DEFAULT_MODEL}). "
        'For Ollama models, prefix with "ollama/".',
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Set debug logging if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    try:
        logger.info("Starting recipe dietary judge")
        judge = RecipeDietaryJudge(model_name=args.model)
        output_file = judge.process_csv_file(args.input_file, args.output_dir)
        logger.info(f"Evaluation complete. Results written to: {output_file}")
    except ValueError as e:
        logger.error(f"Error: {str(e)}")
        print("\nPlease ensure you have Ollama installed and running:")
        print("1. Install Ollama from https://ollama.ai/")
        print("2. Start the Ollama service")
        print("3. Set MODEL_NAME in your .env file or use --model argument")
        model_name = args.model or os.getenv("MODEL_NAME", DEFAULT_MODEL)
        if model_name.startswith("ollama/"):
            print(f"4. Pull the model: ollama pull {model_name.replace('ollama/', '')}")
        exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    main()
