# minimal_jarvis

Minimal AI assistant system inspired by OpenJarvis.

## Installation

```bash
pip install -e .[dev]
```

## Usage

```python
from minimal_jarvis import Jarvis

jarvis = Jarvis(model="llama2", tools=["calculator", "shell"])
result = jarvis.ask("What is 2+2? Then list files in the current directory.")
print(result)
```

## CLI

```bash
python cli.py ask "What is 2+2?"
```
