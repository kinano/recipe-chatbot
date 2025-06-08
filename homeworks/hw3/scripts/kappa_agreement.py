import numpy as np
from typing import List, Dict, Union
from collections import Counter


def calculate_cohens_kappa(
    annotator1_ratings: List[Union[str, int]], annotator2_ratings: List[Union[str, int]]
) -> float:
    """
    Calculate Cohen's Kappa coefficient for measuring inter-rater agreement between two annotators.

    Args:
        annotator1_ratings (List[Union[str, int]]): List of ratings from the first annotator
        annotator2_ratings (List[Union[str, int]]): List of ratings from the second annotator

    Returns:
        float: Cohen's Kappa coefficient between -1 and 1

    Raises:
        ValueError: If the input lists have different lengths or are empty

    Notes:
        - Kappa = 1 indicates perfect agreement
        - Kappa = 0 indicates agreement equivalent to chance
        - Kappa < 0 indicates agreement less than chance
        - Generally accepted interpretation:
            < 0: Poor agreement
            0.01-0.20: Slight agreement
            0.21-0.40: Fair agreement
            0.41-0.60: Moderate agreement
            0.61-0.80: Substantial agreement
            0.81-1.00: Almost perfect agreement
    """
    if len(annotator1_ratings) != len(annotator2_ratings):
        raise ValueError("Both annotators must rate the same number of items")

    if not annotator1_ratings or not annotator2_ratings:
        raise ValueError("Rating lists cannot be empty")

    # Get unique categories
    categories = set(annotator1_ratings + annotator2_ratings)
    n_categories = len(categories)
    n_items = len(annotator1_ratings)

    # Create confusion matrix
    confusion_matrix = np.zeros((n_categories, n_categories))
    category_to_idx = {cat: idx for idx, cat in enumerate(sorted(categories))}

    # Fill confusion matrix
    for a1, a2 in zip(annotator1_ratings, annotator2_ratings):
        i = category_to_idx[a1]
        j = category_to_idx[a2]
        confusion_matrix[i, j] += 1

    # Calculate observed agreement (Po)
    observed_agreement = np.sum(np.diag(confusion_matrix)) / n_items

    # Calculate expected agreement (Pe)
    row_marginals = np.sum(confusion_matrix, axis=1)
    col_marginals = np.sum(confusion_matrix, axis=0)
    expected_agreement = np.sum(row_marginals * col_marginals) / (n_items * n_items)

    # Calculate Cohen's Kappa
    if expected_agreement == 1:
        return 1.0  # Perfect agreement case

    kappa = (observed_agreement - expected_agreement) / (1 - expected_agreement)
    return float(kappa)


def interpret_kappa(kappa: float) -> str:
    """
    Interpret the Cohen's Kappa coefficient value.

    Args:
        kappa (float): Cohen's Kappa coefficient

    Returns:
        str: Interpretation of the kappa value
    """
    if kappa < 0:
        return "Poor agreement"
    elif kappa <= 0.20:
        return "Slight agreement"
    elif kappa <= 0.40:
        return "Fair agreement"
    elif kappa <= 0.60:
        return "Moderate agreement"
    elif kappa <= 0.80:
        return "Substantial agreement"
    else:
        return "Almost perfect agreement"


# Example usage
if __name__ == "__main__":
    # Example 1: Binary classification
    annotator1 = [1, 0, 1, 1, 0, 1, 0, 1]
    annotator2 = [1, 0, 1, 0, 0, 1, 1, 1]

    kappa = calculate_cohens_kappa(annotator1, annotator2)
    print(f"Cohen's Kappa: {kappa:.3f}")
    print(f"Interpretation: {interpret_kappa(kappa)}")

    # Example 2: Multiple categories
    annotator1_cats = ["A", "B", "A", "C", "B", "A", "C", "B"]
    annotator2_cats = ["A", "B", "A", "B", "B", "A", "C", "B"]

    kappa = calculate_cohens_kappa(annotator1_cats, annotator2_cats)
    print(f"\nCohen's Kappa (multiple categories): {kappa:.3f}")
    print(f"Interpretation: {interpret_kappa(kappa)}")
