#!/usr/bin/env python3
"""
Interactive labeling script for trace data.
Displays unlabeled traces and allows human annotation.
"""

import csv
import random
import os
import sys
from typing import List, Dict

def load_csv_data(file_path: str) -> List[Dict]:
    """Load CSV data into a list of dictionaries."""
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_csv_data(file_path: str, data: List[Dict], fieldnames: List[str]):
    """Save data back to CSV file."""
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def display_trace(row: Dict, index: int, total: int):
    """Display a trace in a human-readable format."""
    print("\n" + "="*80)
    print(f"TRACE {index + 1} of {total} | ID: {row['trace_id']}")
    print("="*80)
    print(f"QUERY: {row['query']}")
    print(f"\nDIETARY RESTRICTION: {row['dietary_restriction']}")
    print(f"\nRESPONSE:")
    # Wrap long responses for better readability
    response = row['response']
    if len(response) > 500:
        print(response[:500] + "... [TRUNCATED]")
        print(f"\n[Full response is {len(response)} characters long]")
    else:
        print(response)
    print("="*80)

def get_user_label() -> str:
    """Get label input from user with validation."""
    while True:
        choice = input("\nEnter label (pass/fail) or 'q' to quit, 's' to skip: ").strip().lower()
        if choice in ['pass', 'fail', 'p', 'f']:
            return 'pass' if choice in ['pass', 'p'] else 'fail'
        elif choice in ['q', 'quit']:
            return 'quit'
        elif choice in ['s', 'skip']:
            return 'skip'
        else:
            print("Invalid input. Please enter 'pass', 'fail', 'skip', or 'quit'")

def main():
    file_path = "/Users/kinan/dev/recipe-chatbot/homeworks/hw3/data/kf_labeled_traces.csv"
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found!")
        sys.exit(1)
    
    print("Loading data...")
    data = load_csv_data(file_path)
    fieldnames = list(data[0].keys()) if data else []
    
    # Filter unlabeled rows
    unlabeled_rows = []
    for i, row in enumerate(data):
        if not row['label'] or row['label'].strip() == '':
            unlabeled_rows.append((i, row))
    
    print(f"Found {len(unlabeled_rows)} unlabeled traces out of {len(data)} total traces")
    
    if len(unlabeled_rows) == 0:
        print("No unlabeled traces found!")
        return
    
    # Randomly select up to 200 rows
    sample_size = min(200, len(unlabeled_rows))
    selected_rows = random.sample(unlabeled_rows, sample_size)
    
    print(f"Randomly selected {sample_size} traces for labeling")
    print("\nInstructions:")
    print("- Review each trace and determine if it's a 'pass' or 'fail'")
    print("- Enter 'pass' or 'p' for good responses")
    print("- Enter 'fail' or 'f' for bad responses") 
    print("- Enter 'skip' or 's' to skip a trace")
    print("- Enter 'quit' or 'q' to exit and save progress")
    
    labeled_count = 0
    
    for i, (original_index, row) in enumerate(selected_rows):
        display_trace(row, i, sample_size)
        
        label = get_user_label()
        
        if label == 'quit':
            break
        elif label == 'skip':
            continue
        else:
            # Update the label in the original data
            data[original_index]['label'] = label
            labeled_count += 1
            print(f"✓ Labeled as: {label}")
    
    if labeled_count > 0:
        print(f"\nSaving {labeled_count} new labels to file...")
        save_csv_data(file_path, data, fieldnames)
        print("✓ File saved successfully!")
    else:
        print("\nNo labels were added.")
    
    print(f"\nSession complete. Labeled {labeled_count} traces.")

if __name__ == "__main__":
    main()