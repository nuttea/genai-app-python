---
name: dd-llmobs-experiments
description: Create and run Datadog LLM Observability Experiments for evaluating LLM pipelines. Use when the user wants to create datasets, define evaluators, run experiments, or analyze experiment results using the ddtrace LLMObs SDK. Also use when the user mentions LLM evaluation, LLM testing, experiment datasets, or Datadog LLMObs experiments.
---

# Datadog LLMObs Experiments

Run systematic evaluations of LLM pipelines using Datadog's Experiments SDK (`ddtrace.llmobs`).

An experiment consists of three key components:
- **Dataset**: A collection of records with `input_data` and optional `expected_output`.
- **Task**: A function that takes an input and generates a response.
- **Evaluators**: Functions that compare the model's output against the expected output and return a score.

Reference: [DataDog/llm-observability/experiments/notebooks](https://github.com/DataDog/llm-observability/tree/main/experiments/notebooks)

## Prerequisites

- `ddtrace >= 4.3.0`
- Datadog API key (`DD_API_KEY`) and Application key (`DD_APPLICATION_KEY`)
- Site: `us3.datadoghq.com` (this project's Datadog site)

## Quick Start

```python
import os
from dotenv import load_dotenv
load_dotenv(override=True)

from ddtrace.llmobs import LLMObs, EvaluatorResult

LLMObs.enable(
    api_key=os.getenv("DD_API_KEY"),
    app_key=os.getenv("DD_APPLICATION_KEY"),
    site="us3.datadoghq.com",
    project_name="vote-extraction-project",
    ml_app="vote-extraction-app",
)
```

## Step 1: Create a Dataset

Each record has `input_data` (required), `expected_output` (optional), and `metadata` (optional).

```python
dataset = LLMObs.create_dataset(
    dataset_name="capitals-of-the-world",
    description="inputs and outputs describing capitals of the world",
    records=[
        {
            "input_data": {"question": "What is the capital of China?"},
            "expected_output": "Beijing",
            "metadata": {"difficulty": "easy"},
        },
        {
            "input_data": {"question": "Which city serves as the capital of South Africa?"},
            "expected_output": "Pretoria",
            "metadata": {"difficulty": "medium"},
        },
    ],
)

dataset.url          # view in Datadog UI
dataset.as_dataframe()  # view as pandas DataFrame
```

`create_dataset` automatically pushes records to Datadog. Dataset names must be unique.

### Pull an existing dataset

```python
dataset = LLMObs.pull_dataset(dataset_name="capitals-of-the-world")
```

### Modify records locally, then push

```python
dataset.append({"input_data": {"question": "Capital of Canada?"}, "expected_output": "Ottawa"})
dataset.update(0, {"input_data": {"question": "Updated?"}, "expected_output": "Updated"})
dataset.delete(1)
dataset.push()  # sync changes to Datadog
```

### Create from CSV

```python
dataset = LLMObs.create_dataset_from_csv(
    csv_path="./data/taskmaster.csv",
    dataset_name="taskmaster-mini",
    input_data_columns=["prompt", "topics"],
    expected_output_columns=["labels"],
)
```

For detailed dataset management (versioning, updating records, exporting), see [references/datasets.md](references/datasets.md).

## Step 2: Define a Task

The task function receives `input_data` (from each dataset record) and `config` (from experiment definition). It returns the model's output.

```python
from typing import Dict, Any

def generate_capital(input_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    response = llm_client.generate(
        model=config["model"],
        prompt=input_data["question"],
        temperature=config["temperature"],
    )
    return response.text
```

You can return any type (str, dict, list). For structured outputs, return a dict:

```python
def classify_topic(input_data: Dict[str, Any], config: Dict[str, Any]) -> dict:
    # ... LLM call ...
    return {"response": "True", "confidence": 0.95}
```

### Tip: Test on a single sample first

```python
sample = dataset[0]["input_data"]
output = generate_capital(sample, {"model": "gemini-2.5-flash", "temperature": 0})
print(output)
```

## Step 3: Define Evaluators

Evaluators receive `input_data`, `output_data` (task output), and `expected_output` (ground truth). They run row-wise against each dataset record.

### Simple evaluators (return bool, float, or str)

```python
def exact_match(input_data, output_data, expected_output):
    return expected_output == output_data

def contains_answer(input_data, output_data, expected_output):
    return expected_output in output_data
```

### Rich evaluators (return EvaluatorResult)

`EvaluatorResult` captures reasoning, assessment, and tags:

```python
from ddtrace.llmobs import EvaluatorResult

def contains_answer(input_data, output_data, expected_output):
    found = expected_output in output_data
    string_index = output_data.find(expected_output)
    reasoning = f"found at index {string_index}" if found else "not found"
    return EvaluatorResult(
        value=found,
        reasoning=reasoning,
        assessment="pass" if found else "fail",
        tags={"task": "contains_answer"},
    )
```

### Summary evaluators (aggregate across entire dataset)

Summary evaluators run after all row-level evaluators. They receive lists of all inputs, outputs, expected outputs, and evaluator results.

```python
def num_exact_matches(inputs, outputs, expected_outputs, evaluators_results):
    return evaluators_results["exact_match"].count(True)
```

For more patterns (class-based, LLM-as-a-judge, categorical), see [references/evaluators.md](references/evaluators.md).

## Step 4: Create and Run Experiment

```python
experiment = LLMObs.experiment(
    name="generate-capital-with-config",
    dataset=dataset,
    task=generate_capital,
    evaluators=[exact_match, contains_answer],
    summary_evaluators=[num_exact_matches],     # optional
    config={"model": "gemini-2.5-flash", "temperature": 0},
    description="basic experiment with config",
)

results = experiment.run(jobs=5)  # parallel execution
print(experiment.url)             # view results in Datadog
```

### Run options

```python
results = experiment.run()                    # sequential
results = experiment.run(jobs=5)              # 5 parallel workers
results = experiment.run(sample_size=10)      # subset only
results = experiment.run(raise_errors=True)   # stop on first error (useful for debugging)
```

**Tip**: Use `raise_errors=True` when debugging to immediately surface errors.

## Iterating: Refine the Task, Reuse Evaluators

The power of experiments is comparing runs. Keep evaluators the same and change the task or config to see what improves results.

**Run 1** -- naive prompt (LLM answers in full sentences, `exact_match` fails):

```python
def generate_capital(input_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    response = llm_call(model=config["model"], prompt=input_data["question"], temperature=config["temperature"])
    return response.text

experiment = LLMObs.experiment(
    name="capital-naive-prompt",
    dataset=dataset, task=generate_capital,
    evaluators=[exact_match, contains_answer],
    config={"model": "gemini-2.5-flash", "temperature": 0},
)
experiment.run(jobs=5)
```

**Run 2** -- refined prompt with system message + few-shot (forces one-word answer, `exact_match` passes):

```python
def generate_capital_one_word(input_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    response = llm_call(
        model=config["model"],
        messages=[
            {"role": "system", "content": "Respond only with the capital name, nothing else."},
            {"role": "user", "content": "What is the capital of France?"},
            {"role": "assistant", "content": "Paris"},
            {"role": "user", "content": input_data["question"]},
        ],
        temperature=config["temperature"],
    )
    return response.text

experiment = LLMObs.experiment(
    name="capital-one-word-prompt",
    dataset=dataset, task=generate_capital_one_word,
    evaluators=[exact_match, contains_answer],
    summary_evaluators=[num_exact_matches],
    config={"model": "gemini-2.5-flash", "temperature": 0},
)
experiment.run(jobs=5)
```

Compare both runs in the Datadog Experiments UI to see how prompt refinement improved accuracy.

## Full End-to-End Example

This mirrors the [official Datadog notebook](https://github.com/DataDog/llm-observability/blob/main/experiments/notebooks/01-basic-experiments.ipynb):

```python
import os
from dotenv import load_dotenv
load_dotenv(override=True)

from typing import Dict, Any
from ddtrace.llmobs import LLMObs, EvaluatorResult

# 1. Initialize
LLMObs.enable(
    api_key=os.getenv("DD_API_KEY"),
    app_key=os.getenv("DD_APPLICATION_KEY"),
    site="us3.datadoghq.com",
    project_name="vote-extraction-project",
    ml_app="vote-extraction-app",
)

# 2. Pull or create dataset
dataset = LLMObs.pull_dataset(dataset_name="my-dataset")

# 3. Define task
def my_task(input_data: Dict[str, Any], config: Dict[str, Any]) -> str:
    # Your LLM call here
    return llm_response

# 4. Define evaluators
def exact_match(input_data, output_data, expected_output):
    return expected_output == output_data

def contains_answer(input_data, output_data, expected_output):
    found = expected_output in str(output_data)
    return EvaluatorResult(
        value=found,
        reasoning="found" if found else "not found",
        assessment="pass" if found else "fail",
    )

def num_exact_matches(inputs, outputs, expected_outputs, evaluators_results):
    return evaluators_results["exact_match"].count(True)

# 5. Create and run experiment
experiment = LLMObs.experiment(
    name="my-experiment",
    dataset=dataset,
    task=my_task,
    evaluators=[exact_match, contains_answer],
    summary_evaluators=[num_exact_matches],
    config={"model": "gemini-2.5-flash", "temperature": 0},
    description="experiment description",
)

results = experiment.run(jobs=5)
print(experiment.url)
```

## Analyzing Results

Results are available in the Datadog Experiments UI at `experiment.url`.

| Search type | Syntax |
|---|---|
| Evaluation (bool) | `@evaluation.external.exact_match.value:true` |
| Evaluation (score) | `@evaluation.external.overlap.value:>=0.5` |
| Evaluation (categorical) | `@evaluation.external.quality.value:excellent` |
| Duration | `@duration:>=5s` |
| Token count | `@trace.total_tokens:>10000` |
| Input field | `@meta.input.question:"capital of France"` |
| Output field | `@meta.output.answer:"Paris"` |
| Metadata | `@meta.metadata.difficulty:hard` |

## Project-Specific Notes

- **Datadog site**: `us3.datadoghq.com`
- **Default project**: `vote-extraction-project`
- **Default model**: `gemini-2.5-flash` (temperature `0.0` for extraction)
- **Env vars**: `DD_API_KEY`, `DD_APPLICATION_KEY`, `DD_SITE`
- **Key URLs**:
  - API keys: `https://us3.datadoghq.com/organization-settings/api-keys`
  - App keys: `https://us3.datadoghq.com/organization-settings/application-keys`
  - Experiments UI: `https://us3.datadoghq.com/llm/experiments`

## References

- [Evaluator patterns and examples](references/evaluators.md)
- [Dataset management guide](references/datasets.md)
- [Official notebooks: DataDog/llm-observability](https://github.com/DataDog/llm-observability/tree/main/experiments/notebooks)
- [Datadog Docs: Setup](https://docs.datadoghq.com/llm_observability/experiments/setup)
- [Datadog Docs: Datasets](https://docs.datadoghq.com/llm_observability/experiments/datasets)
- [Datadog Docs: Analyzing Results](https://docs.datadoghq.com/llm_observability/experiments/analyzing_results)
