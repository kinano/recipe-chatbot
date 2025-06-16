import csv
import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Optional
from litellm import completion
from dotenv import load_dotenv
import argparse

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
1. DIETARY FOCUS: Prioritize adherence to dietary restrictions while allowing reasonable flexibility.
2. CLEAR VIOLATIONS: Fail recipes with obvious violations of core dietary principles.
3. CONTEXT AWARENESS: Consider recipe context, substitutions, and overall dietary alignment.
4. BALANCED JUDGMENT: Be thorough but not overly punitive for minor or borderline cases.

DIETARY RESTRICTION GUIDELINES:
- Low-carb: Fail if contains obvious high-carb staples (bread, pasta, rice, potatoes, sugar, desserts)
- Vegan: Fail if contains animal products (meat, dairy, eggs, honey, gelatin)
- Vegetarian: Fail if contains meat or fish (dairy and eggs are acceptable)
- Gluten-free: Fail if contains wheat, barley, rye, or clearly gluten-containing ingredients
- Keto: Fail if high in carbs or contains carb-heavy ingredients without keto alternatives
- Paleo: Fail if contains grains, legumes, dairy, or highly processed foods
- Whole30: Fail if contains grains, legumes, dairy, sugar, or processed ingredients
- Diabetic-friendly: Fail if high in sugar or refined carbs without diabetic-appropriate substitutions

EVALUATION APPROACH:
- PASS if the recipe generally complies with the dietary restriction
- FAIL for clear violations of the dietary restriction's core principles
- Consider whether substitutions or alternatives are suggested
- Allow reasonable serving suggestions that don't compromise the main dish
- Balance strictness with practical dietary adherence

IMPORTANT: You must respond with a valid JSON object in the following format:
{
    "llm_judge_label": "PASS" or "FAIL",
    "reason": "detailed explanation of your judgement",
    "confidence": "low", "medium", or "high"
}

EXAMPLES:
[
  {
    "user_query": "I'm flexitarian leaning vegan",
    "dietary_restriction": "vegan",
    "application_response": "Great choice! Here's a flavorful and nutritious recipe for **Chickpea and Spinach Curry**. It’s vegan, hearty, and perfect for a cozy dinner for two.

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

Enjoy your vibrant Chickpea and Spinach Curry—nutritious, comforting, and perfect for a flexitarian, vegan-friendly meal!",
    "llm_judge_label": "pass",
    "reason": "The recipe for Chickpea and Spinach Curry adheres to the vegan dietary restriction. All ingredients listed are plant-based, including olive oil, onion, garlic, ginger, spices, chickpeas, diced tomatoes, coconut milk, spinach, and cilantro. The recipe does not include any animal products such as meat, dairy, eggs, or honey. The preparation methods also do not introduce any non-vegan elements. The suggestion to serve with rice or naan is appropriate as long as the naan is vegan, which is not specified but can be assumed given the context.",
    "confidence": "high"
  },
  {
    "user_query": "I want to make a birthday cake but I'm diabetic. Something that still tastes good?",
    "dietary_restriction": "diabetic-friendly",
    "application_response": "Absolutely! I recommend making a **Low-Carb Almond Flour Birthday Cake**. It's moist, flavorful, and suitable for diabetics since it uses almond flour and natural sweeteners. Here's a detailed recipe for a 2-layer cake that serves 8 slices.

### Ingredients:
- 2 cups almond flour
- 1/2 cup erythritol or monk fruit sweetener (granular form)
- 1 teaspoon baking powder
- 1/2 teaspoon salt
- 4 large eggs
- 1/2 cup unsweetened almond milk
- 1/4 cup melted coconut oil or butter
- 1 teaspoon vanilla extract
- Optional: fresh berries for decoration

### For the frosting:
- 1 cup cream cheese, softened
- 1/2 cup unsweetened whipped heavy cream
- 2 tbsp erythritol or monk fruit sweetener
- 1 teaspoon vanilla extract

---

### Instructions:

**1. Preheat your oven:**  
Set it to 350°F (175°C). Grease two 8-inch round cake pans with butter or coconut oil and line the bottoms with parchment paper for easy removal.

**2. Mix dry ingredients:**  
In a large bowl, whisk together almond flour, erythritol, baking powder, and salt until well combined.

**3. Combine wet ingredients:**  
In another bowl, beat the eggs lightly. Add almond milk, melted coconut oil, and vanilla extract. Whisk until smooth.

**4. Mix everything:**  
Pour the wet ingredients into the dry ingredients. Stir gently until the batter is uniform and smooth. Do not overmix.

**5. Bake:**  
Divide the batter evenly between the two prepared pans. Tap the pans lightly to remove air bubbles. Place in the oven and bake for 20-25 minutes, or until a toothpick inserted into the center comes out clean.

**6. Cool:**  
Remove from the oven and cool in the pans for 10 minutes, then transfer to a wire rack to cool completely.

**7. Make the frosting:**  
In a bowl, beat the softened cream cheese until smooth. Add erythritol and vanilla, then beat again. In a separate bowl, whip the heavy cream until soft peaks form. Gently fold the whipped cream into the cream cheese mixture until well combined.

**8. Assemble the cake:**  
Place one cake layer on a serving plate. Spread a generous layer of frosting on top. Place the second layer on top and frost the top and sides of the cake.

**9. Decorate:**  
Optional: Garnish with fresh berries or sugar-free sprinkles.

**10. Serve:**  
Slice into 8 pieces and enjoy a delicious, diabetic-friendly birthday cake!

Would you like tips on decorating or a specific flavor variation?",
    "llm_judge_label": "pass",
    "reason": "The recipe for the Low-Carb Almond Flour Birthday Cake is designed to be diabetic-friendly. It uses almond flour, which is low in carbohydrates and has a low glycemic index, making it suitable for managing blood sugar levels. The sweeteners used, erythritol or monk fruit, are both low-glycemic and do not significantly impact blood sugar, which is ideal for diabetics. The recipe avoids high-sugar ingredients and uses unsweetened almond milk and unsweetened whipped heavy cream, further reducing the carbohydrate content. The use of cream cheese and coconut oil or butter provides healthy fats, which can help in moderating blood sugar spikes. Overall, the recipe adheres to the diabetic-friendly dietary restriction by focusing on low-glycemic ingredients and controlled carbohydrate content.",
    "confidence": "high"
  },
  {
    "user_query": "I avoid processed foods but I'm lazy",
    "dietary_restriction": "paleo",
    "application_response": "Great! How about a simple, wholesome Spaghetti Aglio e Olio? It’s quick, requires minimal ingredients, and is free of processed foods. Perfect for a lazy day!

### Spaghetti Aglio e Olio (Serves 2)

#### Ingredients:
- 200g (7 oz) spaghetti
- 4 cloves garlic, thinly sliced
- 1/4 cup extra virgin olive oil
- 1/2 teaspoon chili flakes (optional, for a bit of heat)
- Salt, to taste
- Fresh parsley, chopped (about 2 tablespoons)
- Freshly ground black pepper
- Grated Parmesan cheese (optional, but not processed if you have good quality)

#### Instructions:

1. **Cook the Pasta:** Bring a large pot of salted water to a boil. Add the spaghetti and cook according to the package instructions until al dente (about 8-10 minutes). Once cooked, reserve 1/4 cup of pasta water and then drain the pasta.

2. **Prepare the Flavored Oil:** While the pasta cooks, heat the olive oil in a large skillet over medium heat. Add the sliced garlic and chili flakes (if using). Sauté gently, stirring constantly, for about 2-3 minutes until the garlic turns golden and fragrant. Be careful not to burn it, as burnt garlic becomes bitter.

3. **Combine Pasta and Flavored Oil:** Add the drained spaghetti directly into the skillet with the garlic oil. Toss well to coat all strands. If it seems dry, add a splash of the reserved pasta water to loosen it up.

4. **Finish and Serve:** Remove from heat. Stir in chopped parsley, a pinch of salt, and freshly ground black pepper to taste. If you like, sprinkle with some grated Parmesan cheese and give it another toss.

5. **Plate and Enjoy:** Serve immediately with a fresh salad or some crusty bread on the side.

This dish is all about flavor with minimal effort—perfect for a lazy but wholesome meal!",
    "llm_judge_label": "fail",
    "reason": "This recipe fails paleo requirements due to fundamental incompatibility. Spaghetti is wheat-based (grains prohibited), Parmesan is dairy (not allowed), and crusty bread suggestion adds more grain violations. While the recipe avoids processed foods as requested, it doesn't address the core paleo restriction against grains and dairy.",
    "confidence": "high"
  },
  {
    "user_query": "Need a quick breakfast but I'm gluten-free",
    "dietary_restriction": "gluten-free", 
    "application_response": "Here's a perfect Gluten-Free Avocado Toast! Use gluten-free bread, mashed avocado, salt, pepper, and lemon juice. Top with everything bagel seasoning and enjoy with a side of regular toast for your family.",
    "llm_judge_label": "fail",
    "reason": "The main recipe is gluten-free compliant using gluten-free bread and naturally gluten-free ingredients. However, suggesting 'regular toast for your family' introduces cross-contamination concerns and doesn't fully support the gluten-free dining experience.",
    "confidence": "medium"
  },
  {
    "user_query": "I want something low-carb for lunch",
    "dietary_restriction": "low-carb",
    "application_response": "Try this delicious Grilled Chicken Salad! Mix grilled chicken breast, mixed greens, cucumber, tomatoes, avocado, and olive oil dressing. Serve with a small side of quinoa for extra protein.",
    "llm_judge_label": "pass",
    "reason": "The main components (chicken, vegetables, avocado, olive oil) are low-carb friendly. While quinoa contains some carbs, it's suggested as a small side and provides protein, making this a reasonable low-carb meal overall.",
    "confidence": "medium"
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

EVALUATION REQUIREMENTS:
- The user has a {dietary_restriction} dietary restriction that should be respected
- Review ingredients for clear violations of the dietary restriction
- Consider the overall recipe alignment with dietary goals
- Evaluate whether substitutions or modifications are suggested
- Balance strictness with practical dietary adherence

BALANCED EVALUATION APPROACH:
1. Identify the main ingredients and their dietary compliance
2. Check for obvious violations of the {dietary_restriction} restriction
3. Consider whether the recipe offers appropriate alternatives or substitutions
4. Evaluate serving suggestions for major conflicts with the restriction
5. PASS if the recipe generally supports the dietary restriction despite minor issues
6. FAIL only if there are clear, significant violations of core dietary principles

Based on this information, please provide your evaluation in the following JSON format:
{{
    "llm_judge_label": "pass" or "fail",
    "reason": "detailed explanation of dietary compliance assessment and key factors in decision",
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
                temperature=0.3,
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

    def process_csv_file(self, input_file: str, output_dir: str = "results") -> str:
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
