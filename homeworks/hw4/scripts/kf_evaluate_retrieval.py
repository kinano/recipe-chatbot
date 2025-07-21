#!/usr/bin/env python3
"""
Knowledge-Intensive Retrieval Evaluation for HW4

Evaluates BM25 retrieval performance on knowledge-intensive synthetic queries.
Calculates standard IR metrics: Recall@1, Recall@3, Recall@5, and MRR.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from tqdm import tqdm
import statistics

from backend.retrieval import create_retriever, RecipeRetriever


@dataclass
class QueryResult:
    """Results for a single query evaluation."""
    query: str
    query_type: str
    complexity_level: str
    expected_recipe_ids: List[int]
    retrieved_recipe_ids: List[int]
    retrieved_ranks: Dict[int, int]  # recipe_id -> rank
    recall_at_1: float
    recall_at_3: float
    recall_at_5: float
    recall_at_10: float
    reciprocal_rank: float
    found_any: bool
    best_rank: Optional[int]  # Best rank among expected recipes, None if not found
    bm25_scores: List[float]  # BM25 scores for retrieved recipes


@dataclass
class EvaluationMetrics:
    """Overall evaluation metrics."""
    total_queries: int
    recall_at_1: float
    recall_at_3: float
    recall_at_5: float
    recall_at_10: float
    mean_reciprocal_rank: float
    queries_found: int
    queries_not_found: int
    success_rate: float
    average_rank_when_found: float
    median_rank_when_found: float


class RetrievalEvaluator:
    """Evaluates retrieval performance on knowledge-intensive queries."""
    
    def __init__(self, retriever: RecipeRetriever):
        self.retriever = retriever
        self.results: List[QueryResult] = []
    
    def load_queries(self, queries_path: Path) -> Dict[str, Any]:
        """Load knowledge-intensive queries from JSON file."""
        print(f"Loading queries from {queries_path}")
        
        with open(queries_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        print(f"Loaded {len(data['queries'])} queries with {len(data['query_metadata'])} metadata entries")
        return data
    
    def evaluate_single_query(self, query: str, expected_ids: List[int], 
                            query_type: str, complexity_level: str, 
                            top_k: int = 10) -> QueryResult:
        """Evaluate retrieval for a single query."""
        
        # Retrieve results
        retrieved_recipes = self.retriever.retrieve_bm25(query, top_k=top_k)
        retrieved_ids = [recipe['id'] for recipe in retrieved_recipes]
        bm25_scores = [recipe['bm25_score'] for recipe in retrieved_recipes]
        
        # Find ranks of expected recipes
        retrieved_ranks = {}
        found_ids = []
        
        for expected_id in expected_ids:
            if expected_id in retrieved_ids:
                rank = retrieved_ids.index(expected_id) + 1  # 1-indexed
                retrieved_ranks[expected_id] = rank
                found_ids.append(expected_id)
        
        # Calculate metrics
        recall_at_1 = 1.0 if any(rid in retrieved_ids[:1] for rid in expected_ids) else 0.0
        recall_at_3 = 1.0 if any(rid in retrieved_ids[:3] for rid in expected_ids) else 0.0
        recall_at_5 = 1.0 if any(rid in retrieved_ids[:5] for rid in expected_ids) else 0.0
        recall_at_10 = 1.0 if any(rid in retrieved_ids[:10] for rid in expected_ids) else 0.0
        
        # Calculate reciprocal rank and best rank
        reciprocal_rank = 0.0
        best_rank = None
        if retrieved_ranks:
            best_rank = min(retrieved_ranks.values())
            reciprocal_rank = 1.0 / best_rank
        
        found_any = len(found_ids) > 0
        
        return QueryResult(
            query=query,
            query_type=query_type,
            complexity_level=complexity_level,
            expected_recipe_ids=expected_ids,
            retrieved_recipe_ids=retrieved_ids,
            retrieved_ranks=retrieved_ranks,
            recall_at_1=recall_at_1,
            recall_at_3=recall_at_3,
            recall_at_5=recall_at_5,
            recall_at_10=recall_at_10,
            reciprocal_rank=reciprocal_rank,
            found_any=found_any,
            best_rank=best_rank,
            bm25_scores=bm25_scores
        )
    
    def evaluate_all_queries(self, queries_data: Dict[str, Any], top_k: int = 10) -> None:
        """Evaluate all queries and store results."""
        queries = queries_data['queries']
        query_metadata = queries_data['query_metadata']
        
        print(f"Evaluating {len(queries)} queries...")
        
        self.results = []
        
        for i, query_meta in enumerate(tqdm(query_metadata, desc="Evaluating queries")):
            query = query_meta['query']
            expected_ids = query_meta.get('expected_document_ids', [])
            query_type = query_meta.get('type', 'unknown')
            complexity_level = query_meta.get('complexity_level', 'unknown')
            
            if not expected_ids:
                print(f"Warning: Query '{query}' has no expected document IDs")
                continue
            
            result = self.evaluate_single_query(
                query, expected_ids, query_type, complexity_level, top_k
            )
            self.results.append(result)
    
    def calculate_metrics(self) -> EvaluationMetrics:
        """Calculate overall evaluation metrics."""
        if not self.results:
            raise ValueError("No evaluation results available. Run evaluate_all_queries() first.")
        
        total_queries = len(self.results)
        queries_found = sum(1 for r in self.results if r.found_any)
        queries_not_found = total_queries - queries_found
        
        # Calculate averages
        recall_at_1 = statistics.mean(r.recall_at_1 for r in self.results)
        recall_at_3 = statistics.mean(r.recall_at_3 for r in self.results)
        recall_at_5 = statistics.mean(r.recall_at_5 for r in self.results)
        recall_at_10 = statistics.mean(r.recall_at_10 for r in self.results)
        mean_reciprocal_rank = statistics.mean(r.reciprocal_rank for r in self.results)
        success_rate = queries_found / total_queries if total_queries > 0 else 0.0
        
        # Calculate rank statistics for found queries only
        found_ranks = [r.best_rank for r in self.results if r.best_rank is not None]
        average_rank_when_found = statistics.mean(found_ranks) if found_ranks else 0.0
        median_rank_when_found = statistics.median(found_ranks) if found_ranks else 0.0
        
        return EvaluationMetrics(
            total_queries=total_queries,
            recall_at_1=recall_at_1,
            recall_at_3=recall_at_3,
            recall_at_5=recall_at_5,
            recall_at_10=recall_at_10,
            mean_reciprocal_rank=mean_reciprocal_rank,
            queries_found=queries_found,
            queries_not_found=queries_not_found,
            success_rate=success_rate,
            average_rank_when_found=average_rank_when_found,
            median_rank_when_found=median_rank_when_found
        )
    
    def get_metrics_by_type(self) -> Dict[str, Dict[str, float]]:
        """Calculate metrics broken down by query type."""
        type_results = {}
        
        for result in self.results:
            query_type = result.query_type
            if query_type not in type_results:
                type_results[query_type] = []
            type_results[query_type].append(result)
        
        metrics_by_type = {}
        for query_type, results in type_results.items():
            if results:
                found_ranks = [r.best_rank for r in results if r.best_rank is not None]
                metrics_by_type[query_type] = {
                    'count': len(results),
                    'recall_at_1': statistics.mean(r.recall_at_1 for r in results),
                    'recall_at_3': statistics.mean(r.recall_at_3 for r in results),
                    'recall_at_5': statistics.mean(r.recall_at_5 for r in results),
                    'recall_at_10': statistics.mean(r.recall_at_10 for r in results),
                    'mean_reciprocal_rank': statistics.mean(r.reciprocal_rank for r in results),
                    'success_rate': sum(1 for r in results if r.found_any) / len(results),
                    'average_rank_when_found': statistics.mean(found_ranks) if found_ranks else 0.0,
                    'median_rank_when_found': statistics.median(found_ranks) if found_ranks else 0.0
                }
        
        return metrics_by_type
    
    def get_metrics_by_complexity(self) -> Dict[str, Dict[str, float]]:
        """Calculate metrics broken down by complexity level."""
        complexity_results = {}
        
        for result in self.results:
            complexity = result.complexity_level
            if complexity not in complexity_results:
                complexity_results[complexity] = []
            complexity_results[complexity].append(result)
        
        metrics_by_complexity = {}
        for complexity, results in complexity_results.items():
            if results:
                found_ranks = [r.best_rank for r in results if r.best_rank is not None]
                metrics_by_complexity[complexity] = {
                    'count': len(results),
                    'recall_at_1': statistics.mean(r.recall_at_1 for r in results),
                    'recall_at_3': statistics.mean(r.recall_at_3 for r in results),
                    'recall_at_5': statistics.mean(r.recall_at_5 for r in results),
                    'recall_at_10': statistics.mean(r.recall_at_10 for r in results),
                    'mean_reciprocal_rank': statistics.mean(r.reciprocal_rank for r in results),
                    'success_rate': sum(1 for r in results if r.found_any) / len(results),
                    'average_rank_when_found': statistics.mean(found_ranks) if found_ranks else 0.0,
                    'median_rank_when_found': statistics.median(found_ranks) if found_ranks else 0.0
                }
        
        return metrics_by_complexity
    
    def save_results(self, output_path: Path) -> None:
        """Save evaluation results to JSON file."""
        print(f"Saving results to {output_path}")
        
        # Calculate overall metrics
        overall_metrics = self.calculate_metrics()
        metrics_by_type = self.get_metrics_by_type()
        metrics_by_complexity = self.get_metrics_by_complexity()
        
        # Prepare detailed results
        detailed_results = []
        for result in self.results:
            detailed_results.append({
                'query': result.query,
                'query_type': result.query_type,
                'complexity_level': result.complexity_level,
                'expected_recipe_ids': result.expected_recipe_ids,
                'retrieved_recipe_ids': result.retrieved_recipe_ids[:10],  # Limit output size
                'found_recipe_ranks': result.retrieved_ranks,
                'target_rank': result.best_rank,  # Best rank among expected recipes
                'recall_1': result.recall_at_1,
                'recall_3': result.recall_at_3,
                'recall_5': result.recall_at_5,
                'recall_10': result.recall_at_10,
                'reciprocal_rank': result.reciprocal_rank,
                'bm25_scores': result.bm25_scores[:10],  # Limit to top 10 scores
                'found_any': result.found_any
            })
        
        # Compile final output
        output_data = {
            'evaluation_metadata': {
                'total_queries_evaluated': overall_metrics.total_queries,
                'evaluation_method': 'bm25_knowledge_intensive',
                'top_k_retrieved': 10,
                'timestamp': None,  # Could add actual timestamp if needed
            },
            'overall_metrics': {
                'recall_at_1': round(overall_metrics.recall_at_1, 4),
                'recall_at_3': round(overall_metrics.recall_at_3, 4),
                'recall_at_5': round(overall_metrics.recall_at_5, 4),
                'recall_at_10': round(overall_metrics.recall_at_10, 4),
                'mean_reciprocal_rank': round(overall_metrics.mean_reciprocal_rank, 4),
                'total_queries': overall_metrics.total_queries,
                'queries_found': overall_metrics.queries_found,
                'queries_not_found': overall_metrics.queries_not_found,
                'average_rank_when_found': round(overall_metrics.average_rank_when_found, 4),
                'median_rank_when_found': round(overall_metrics.median_rank_when_found, 4)
            },
            'metrics_by_query_type': {
                query_type: {
                    k: round(v, 4) if isinstance(v, float) else v
                    for k, v in metrics.items()
                }
                for query_type, metrics in metrics_by_type.items()
            },
            'metrics_by_complexity_level': {
                complexity: {
                    k: round(v, 4) if isinstance(v, float) else v
                    for k, v in metrics.items()
                }
                for complexity, metrics in metrics_by_complexity.items()
            },
            'detailed_results': detailed_results
        }
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(output_data, file, indent=2, ensure_ascii=False)
        
        print(f"Results saved successfully to {output_path}")


def main():
    """Main evaluation pipeline."""
    # Setup paths
    recipes_path = Path("homeworks/hw4/data/processed_recipes.json")
    index_path = Path("homeworks/hw4/data/bm25_index.pkl")
    queries_path = Path("homeworks/hw4/data/knowledge_intensive_queries.json")
    results_path = Path("homeworks/hw4/results/kf_retrieval_results_baseline.json")
    
    # Check required files
    if not recipes_path.exists():
        print(f"Error: Processed recipes not found at {recipes_path}")
        print("Run the recipe processing script first")
        return
    
    if not queries_path.exists():
        print(f"Error: Knowledge-intensive queries not found at {queries_path}")
        print("Run kf_generate_synthetic_queries_v2.py first")
        return
    
    # Initialize retriever
    print("Initializing BM25 retriever...")
    retriever = create_retriever(recipes_path, index_path)
    
    # Initialize evaluator
    evaluator = RetrievalEvaluator(retriever)
    
    # Load queries
    queries_data = evaluator.load_queries(queries_path)
    
    # Run evaluation
    evaluator.evaluate_all_queries(queries_data, top_k=10)
    
    # Calculate and display metrics
    overall_metrics = evaluator.calculate_metrics()
    
    print(f"\n--- Knowledge-Intensive Retrieval Evaluation Results ---")
    print(f"Total queries evaluated: {overall_metrics.total_queries}")
    print(f"Queries found: {overall_metrics.queries_found}")
    print(f"Queries not found: {overall_metrics.queries_not_found}")
    print(f"Success rate: {overall_metrics.success_rate:.3f}")
    print(f"\nRecall Metrics:")
    print(f"  Recall@1: {overall_metrics.recall_at_1:.4f}")
    print(f"  Recall@3: {overall_metrics.recall_at_3:.4f}")
    print(f"  Recall@5: {overall_metrics.recall_at_5:.4f}")
    print(f"  Recall@10: {overall_metrics.recall_at_10:.4f}")
    print(f"  Mean Reciprocal Rank: {overall_metrics.mean_reciprocal_rank:.4f}")
    print(f"  Average Rank When Found: {overall_metrics.average_rank_when_found:.4f}")
    print(f"  Median Rank When Found: {overall_metrics.median_rank_when_found:.1f}")
    
    # Show breakdown by query type
    metrics_by_type = evaluator.get_metrics_by_type()
    print(f"\n--- Metrics by Query Type ---")
    for query_type, metrics in metrics_by_type.items():
        print(f"\n{query_type} (n={metrics['count']}):")
        print(f"  Recall@1: {metrics['recall_at_1']:.4f}")
        print(f"  Recall@3: {metrics['recall_at_3']:.4f}")
        print(f"  Recall@5: {metrics['recall_at_5']:.4f}")
        print(f"  Recall@10: {metrics['recall_at_10']:.4f}")
        print(f"  MRR: {metrics['mean_reciprocal_rank']:.4f}")
        print(f"  Success Rate: {metrics['success_rate']:.4f}")
        print(f"  Avg Rank When Found: {metrics['average_rank_when_found']:.4f}")
        print(f"  Median Rank When Found: {metrics['median_rank_when_found']:.1f}")
    
    # Save results
    evaluator.save_results(results_path)
    
    print(f"\nEvaluation completed. Results saved to {results_path}")


if __name__ == "__main__":
    main()