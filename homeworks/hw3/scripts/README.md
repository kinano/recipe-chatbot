# Recipe Dietary Judge

This script evaluates recipe responses against dietary restrictions using Ollama LLM models as a judge, through the litellm interface.

## Setup

1. Install Ollama:

   - Visit [ollama.ai](https://ollama.ai/) and follow the installation instructions for your platform
   - After installation, start the Ollama service
   - Pull the model you want to use:
     ```bash
     ollama pull llama2  # or any other model you prefer
     ```

2. Environment Setup:
   - The script uses the project's existing `.env` file
   - Set your model in the `.env` file using the existing `MODEL_NAME` variable:
     ```bash
     # .env
     MODEL_NAME=ollama/llama2  # or your preferred model
     ```
   - The script will use this model by default
   - You can override it using the `--model` argument when running the script
   - All required Python dependencies are managed in the project's `pyproject.toml`
   - Install dependencies using uv:
     ```bash
     uv sync  # Install exact dependencies from pyproject.toml
     ```

## Usage

Run the script using `uv run` with the `.env` file:

```bash
# Basic usage with .env file
uv run --env-file .env python kf_develop_judge.py ../data/kf_dev_set.csv --output-dir ../data/llm_eval_runs/

# Override model from .env
uv run --env-file .env python kf_develop_judge.py ../data/kf_dev_set.csv --model ollama/llama3:latest

# Enable debug logging
uv run --env-file .env python kf_develop_judge.py ../data/kf_dev_set.csv --debug
```

Optional arguments:

- `--model`: Override the model specified in .env (e.g., `--model ollama/mistral`)

Example with custom model:

```bash
uv run python scripts/kf_develop_judge.py data/kf_dev_set.csv --model ollama/llama3
```

## Input CSV Format

The input CSV file should have the following columns:

- `query`: The user's recipe request
- `dietary_restriction`: The dietary restriction to evaluate against
- `response`: The recipe response to evaluate
- `label`: (Optional) Ground truth label
- `error`: (Optional) Error information
- `trace_id`: (Optional) Trace identifier
- `query_id`: (Optional) Query identifier

## Output

The script generates a timestamped CSV file in the output directory with the following additional columns:

- `llm_judge_label`: "pass" or "fail"
- `reason`: Detailed explanation of the judgement
- `confidence`: "low", "medium", or "high"

## Available Models

To see all available models in Ollama:

```bash
ollama list
```

To pull a new model:

```bash
ollama pull <model_name>
```

Note:

- When using the script, prefix the model name with "ollama/" (e.g., "ollama/llama2")
- Set your preferred model in the project's `.env` file using the existing `MODEL_NAME` variable
- You can override the model for individual runs using the `--model` argument

## Dependencies

All dependencies are managed in the project's `pyproject.toml`.

## Iterations (with Claude)

https://claude.ai/artifacts/99123cd4-0a07-46b1-8498-09be82db1f84
