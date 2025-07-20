# Claude Development Notes

## Repository Setup

This repository uses **uv** for Python package management and dependency resolution.

### Important: Always use uv for this project

- **Package Installation**: `uv pip install -e .`
- **Dependency Management**: `uv pip install <package>`
- **Virtual Environment**: `uv venv` to create, `source .venv/bin/activate` to activate
- **Running Scripts**: Ensure virtual environment is activated or use `uv run`

### Testing Requirements

- All tests must be run using the uv environment
- Install dependencies: `uv pip install -e .`
- Run tests with the activated virtual environment
- Check for available test commands in package.json/pyproject.toml

### Development Workflow

1. Always check if uv virtual environment is activated
2. Install dependencies using uv
3. Run linting/type checking if available
4. Test changes before committing

### Key Files

- `pyproject.toml` - Project dependencies and configuration
- `homeworks/hw4/data/processed_recipes.json` - Recipe dataset (200 recipes with complex structure)
- `homeworks/hw4/scripts/` - Analysis and utility scripts

### Recipe Data Structure

The processed_recipes.json contains 200 recipes with:
- `id`, `name`, `description`
- `ingredients` (list), `n_ingredients` (count)
- `steps` (list), `n_steps` (count) 
- `minutes` (cooking time), `tags`, `nutrition`
- `full_text` (searchable content)

Complex recipes defined as having:
- ≥10 ingredients OR ≥120 minutes OR ≥15 steps