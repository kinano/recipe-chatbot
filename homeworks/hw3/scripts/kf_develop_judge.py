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

    SYSTEM_PROMPT = """You are an expert recipe evaluator and dietary restriction specialist. Your role is to evaluate whether recipe responses appropriately address dietary restrictions.

EVALUATION PRINCIPLES:
1. Be on the cautious side - only fail recipes that clearly violate dietary restrictions.
2. Consider context and intent - evaluate the query and response to determine whether the user's dietary needs are respected.
3. Account for common ingredient flexibility and substitutions.
4. Focus on major violations, not minor technicalities.

DIETARY RESTRICTION GUIDELINES:
- Low-carb: Focus on obviously high-carb ingredients (bread, pasta, rice, potatoes, sugar, candy, chocolate).
- Vegan: Strictly no animal products (meat, dairy, eggs, honey)
- Vegetarian: No meat/fish, but dairy and eggs are acceptable
- Gluten-free: No wheat, barley, rye, or gluten-containing ingredients
- Keto: Very low carb (under 20-30g), high fat
- Paleo: No grains, legumes, dairy, processed foods
- Whole30: No grains, legumes, dairy, sugar, processed foods for 30 days

EVALUATION APPROACH:
- PASS if the recipe meets both the dietary restriction and the user's expressed constraints (e.g. I do not like vegetables).
- FAIL when there are violations of the stated dietary restriction
- Consider whether the application suggested substitutions that meet the restriction.

IMPORTANT: You must respond with a valid JSON object in the following format:
{
    "llm_judge_label": "pass" or "fail",
    "reason": "detailed explanation of your judgement",
    "confidence": "low", "medium", or "high"
}

EXAMPLES OF GOOD EVALUATION:

Example 1 - Low-carb query:
User Query: "I want something light but filling"
Dietary Restriction: "low-carb"
Recipe Response: Contains quinoa (high-carb grain)
Correct Evaluation: FAIL - Quinoa is a clear high-carb violation for low-carb diet

Example 2 - Vegan query:
User Query: "I'm flexitarian leaning vegan"
Dietary Restriction: "vegan"
Recipe Response: All ingredients are plant-based (chickpeas, spinach, coconut milk, etc.)
Correct Evaluation: PASS - Recipe is fully vegan-compliant

Example 3 - Borderline case:
User Query: "I need gluten-free options"
Dietary Restriction: "gluten-free"
Recipe Response: Uses oats (potentially cross-contaminated but often acceptable)
Correct Evaluation: FAIL - Oats are generally not acceptable for gluten-free diets unless specifically noted.

Example 4 - Good faith attempt:
User Query: "I'm trying to eat keto"
Dietary Restriction: "keto"
Recipe Response: Suggests cauliflower rice instead of regular rice, includes high-fat ingredients
Correct Evaluation: PASS - Shows clear attempt to accommodate keto requirements

Example 5 - Good adherence to user constraints:
User Query: "I am pescatarian and I hate fish"
Dietary Restriction: "pescatarian"
Recipe Response: Uses fish
Correct Evaluation: FAIL - User has expressed a constraint against fish.

Example 6 - Good adherence to user constraints:
User Query: "I am pescatarian and I hate fish"
Dietary Restriction: "pescatarian"
Recipe Response: Uses shellfish
Correct Evaluation: PASS - User has expressed a constraint against fish and the application respected that.
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

EVALUATION CONTEXT:
- The user has a {dietary_restriction} dietary restriction
- Evaluate if the recipe response reasonably accommodates this restriction
- Fail for violations

Based on this information, please provide your evaluation in the following JSON format:
{{
    "llm_judge_label": "pass" or "fail",
    "reason": "detailed explanation of your judgement focusing on specific ingredients or aspects that led to your decision",
    "confidence": "low", "medium", or "high"
}}
"""

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
