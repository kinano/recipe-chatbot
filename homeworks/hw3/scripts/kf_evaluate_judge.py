#!/usr/bin/env python3
"""
Script to evaluate LLM judge performance using the judgy library.

This script calculates key metrics for judge evaluation:
- Raw pass rate (p_obs) from the judge
- Corrected true success rate (θ̂)
- 95% Confidence Interval (CI) for θ
- Brief interpretation of results

Usage:
    python kf_evaluate_judge.py <csv_file_with_judge_results>
"""

import logging
import argparse
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from judgy import estimate_success_rate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class JudgePerformanceEvaluator:
    """Evaluates LLM judge performance using the judgy library."""

    def __init__(self):
        pass

    def load_data(self, csv_file: str) -> pd.DataFrame:
        """Load judge results from CSV file."""
        logger.info(f"Loading data from {csv_file}")

        try:
            df = pd.read_csv(csv_file)
            logger.info(f"Loaded {len(df)} rows")

            # Check required columns
            required_cols = ["label", "llm_judge_label"]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")

            # Remove rows with missing values in key columns
            initial_len = len(df)
            df = df.dropna(subset=required_cols)
            if len(df) < initial_len:
                logger.info(f"Removed {initial_len - len(df)} rows with missing values")

            return df

        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def prepare_data_for_judgy(self, df: pd.DataFrame) -> Tuple[List[bool], List[bool]]:
        """Convert data to format expected by judgy library."""

        # Convert labels to boolean (True = pass, False = fail)
        true_labels = (df["label"].str.lower() == "pass").tolist()
        judge_labels = (df["llm_judge_label"].str.lower() == "pass").tolist()

        logger.info(
            f"Ground truth distribution: {sum(true_labels)} pass, {len(true_labels) - sum(true_labels)} fail"
        )
        logger.info(
            f"Judge prediction distribution: {sum(judge_labels)} pass, {len(judge_labels) - sum(judge_labels)} fail"
        )

        return true_labels, judge_labels

    def calculate_metrics(
        self, true_labels: List[bool], judge_labels: List[bool]
    ) -> Dict:
        """Calculate judge performance metrics using judgy."""

        logger.info("Calculating judge performance metrics...")

        # Raw pass rate (p_obs) - what the judge observed
        p_obs = sum(judge_labels) / len(judge_labels)

        # Calculate confusion matrix components
        tp = sum(t and j for t, j in zip(true_labels, judge_labels))  # True positives
        tn = sum(
            not t and not j for t, j in zip(true_labels, judge_labels)
        )  # True negatives
        fp = sum(
            not t and j for t, j in zip(true_labels, judge_labels)
        )  # False positives
        fn = sum(
            t and not j for t, j in zip(true_labels, judge_labels)
        )  # False negatives

        # Judge accuracy metrics
        accuracy = (tp + tn) / len(true_labels)
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0
        )

        # Calculate TPR and TNR for judgy
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0  # True Positive Rate (Sensitivity)
        tnr = tn / (tn + fp) if (tn + fp) > 0 else 0  # True Negative Rate (Specificity)

        logger.info(f"Judge performance - TPR: {tpr:.4f}, TNR: {tnr:.4f}")

        # Use judgy to estimate corrected success rate
        try:
            # Convert boolean labels to 0/1 for judgy
            test_labels = [int(label) for label in true_labels]
            test_preds = [int(pred) for pred in judge_labels]

            # For this evaluation, we'll treat all data as "unlabeled" predictions
            # since we want to estimate the corrected success rate
            unlabeled_preds = test_preds.copy()

            # Estimate the corrected true success rate (θ̂) and confidence interval
            theta_hat, ci_lower, ci_upper = estimate_success_rate(
                test_labels=test_labels,
                test_preds=test_preds,
                unlabeled_preds=unlabeled_preds,
                confidence_level=0.95,
            )

            logger.info(f"Corrected true success rate (θ̂): {theta_hat:.4f}")
            logger.info(f"95% CI: [{ci_lower:.4f}, {ci_upper:.4f}]")

        except Exception as e:
            logger.warning(f"Error calculating corrected metrics with judgy: {str(e)}")
            # Fallback to basic calculation
            theta_hat = sum(true_labels) / len(true_labels)  # Actual ground truth rate
            ci_lower = theta_hat - 1.96 * np.sqrt(
                theta_hat * (1 - theta_hat) / len(true_labels)
            )
            ci_upper = theta_hat + 1.96 * np.sqrt(
                theta_hat * (1 - theta_hat) / len(true_labels)
            )
            logger.info(
                f"Using fallback calculation - θ̂: {theta_hat:.4f}, CI: [{ci_lower:.4f}, {ci_upper:.4f}]"
            )

        return {
            "p_obs": p_obs,
            "theta_hat": theta_hat,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "tpr": tpr,
            "tnr": tnr,
            "tp": tp,
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "total_samples": len(true_labels),
        }

    def interpret_results(self, metrics: Dict) -> str:
        """Provide interpretation of the results."""

        interpretation = []

        # Recipe Bot adherence assessment
        theta_hat = metrics["theta_hat"]
        ci_lower = metrics["ci_lower"]
        ci_upper = metrics["ci_upper"]
        p_obs = metrics["p_obs"]

        interpretation.append("=== RECIPE BOT DIETARY ADHERENCE ASSESSMENT ===\n")

        # Success rate interpretation
        interpretation.append(f"Raw Pass Rate (p_obs): {p_obs:.1%}")
        interpretation.append(f"Corrected True Success Rate (θ̂): {theta_hat:.1%}")
        interpretation.append(
            f"95% Confidence Interval: [{ci_lower:.1%}, {ci_upper:.1%}]\n"
        )

        # Adherence quality assessment
        if theta_hat >= 0.9:
            adherence_quality = "EXCELLENT"
            adherence_desc = (
                "The Recipe Bot is adhering very well to dietary preferences"
            )
        elif theta_hat >= 0.8:
            adherence_quality = "GOOD"
            adherence_desc = "The Recipe Bot is adhering well to dietary preferences"
        elif theta_hat >= 0.7:
            adherence_quality = "MODERATE"
            adherence_desc = (
                "The Recipe Bot shows moderate adherence to dietary preferences"
            )
        elif theta_hat >= 0.6:
            adherence_quality = "FAIR"
            adherence_desc = (
                "The Recipe Bot shows fair adherence to dietary preferences"
            )
        else:
            adherence_quality = "POOR"
            adherence_desc = (
                "The Recipe Bot shows poor adherence to dietary preferences"
            )

        interpretation.append(f"Adherence Quality: {adherence_quality}")
        interpretation.append(f"{adherence_desc}.\n")

        # Confidence assessment
        ci_width = ci_upper - ci_lower
        if ci_width <= 0.05:
            confidence_level = "VERY HIGH"
            confidence_desc = "very confident in this assessment"
        elif ci_width <= 0.10:
            confidence_level = "HIGH"
            confidence_desc = "confident in this assessment"
        elif ci_width <= 0.15:
            confidence_level = "MODERATE"
            confidence_desc = "moderately confident in this assessment"
        else:
            confidence_level = "LOW"
            confidence_desc = (
                "have low confidence in this assessment due to wide confidence interval"
            )

        interpretation.append(f"Confidence Level: {confidence_level}")
        interpretation.append(f"We {confidence_desc} (CI width: {ci_width:.1%}).\n")

        # Judge performance assessment
        interpretation.append("=== JUDGE PERFORMANCE ASSESSMENT ===\n")
        interpretation.append(f"Judge Accuracy: {metrics['accuracy']:.1%}")
        interpretation.append(f"Judge Precision: {metrics['precision']:.1%}")
        interpretation.append(f"Judge Recall (TPR): {metrics['recall']:.1%}")
        interpretation.append(f"Judge Specificity (TNR): {metrics['tnr']:.1%}")
        interpretation.append(f"Judge F1-Score: {metrics['f1']:.3f}\n")

        # Detailed breakdown
        interpretation.append("=== DETAILED BREAKDOWN ===\n")
        interpretation.append(f"Total Samples: {metrics['total_samples']}")
        interpretation.append(f"True Positives: {metrics['tp']}")
        interpretation.append(f"True Negatives: {metrics['tn']}")
        interpretation.append(f"False Positives: {metrics['fp']}")
        interpretation.append(f"False Negatives: {metrics['fn']}")

        return "\n".join(interpretation)

    def evaluate(self, csv_file: str) -> None:
        """Main evaluation function."""

        # Load data
        df = self.load_data(csv_file)

        # Prepare data for judgy
        true_labels, judge_labels = self.prepare_data_for_judgy(df)

        # Calculate metrics
        metrics = self.calculate_metrics(true_labels, judge_labels)

        # Generate interpretation
        interpretation = self.interpret_results(metrics)

        # Print results
        print("\n" + "=" * 60)
        print("JUDGE EVALUATION RESULTS")
        print("=" * 60)
        print(interpretation)
        print("=" * 60 + "\n")


def main():
    """Command line interface for judge evaluation."""
    parser = argparse.ArgumentParser(
        description="Evaluate LLM judge performance using judgy library"
    )
    parser.add_argument(
        "csv_file",
        help="Path to CSV file with judge results (must have 'label' and 'llm_judge_label' columns)",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Set debug logging if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")

    try:
        evaluator = JudgePerformanceEvaluator()
        evaluator.evaluate(args.csv_file)
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
