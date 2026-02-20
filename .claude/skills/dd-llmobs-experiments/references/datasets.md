# Dataset Management Reference

Reference: [00-basic-datasets.ipynb](https://github.com/DataDog/llm-observability/blob/main/experiments/notebooks/00-basic-datasets.ipynb)

## Creating Datasets

### Manual Creation

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

dataset.url  # view in Datadog (may take a few seconds)
```

`create_dataset` automatically pushes records to Datadog. Dataset names must be unique.

### From CSV

```python
dataset = LLMObs.create_dataset_from_csv(
    csv_path="./data/taskmaster.csv",
    dataset_name="taskmaster-mini",
    input_data_columns=["prompt", "topics"],
    expected_output_columns=["labels"],
    metadata_columns=["difficulty"],        # optional
    csv_delimiter=",",                      # optional, defaults to comma
)
```

**CSV rules:**
- Must have a header row
- Max field size: 10MB
- Columns not listed in `input_data_columns` or `expected_output_columns` become metadata automatically

### From Datadog UI

Select **Add to Dataset** on any span page to add production data to a dataset.

## Pulling Datasets

```python
dataset = LLMObs.pull_dataset(dataset_name="capitals-of-the-world")

# Specific version
dataset = LLMObs.pull_dataset(dataset_name="capitals-of-the-world", version=3)

print(len(dataset))  # number of records
```

## Viewing Data

```python
dataset.as_dataframe()  # pandas DataFrame (requires pandas)

# DataFrame has MultiIndex columns:
#   input_data.question | expected_output | metadata.difficulty
```

## Modifying Records

Changes are local until `push()` is called.

### Access by index

```python
print(dataset[0])       # single record
print(dataset[1:5])     # slice
for record in dataset:  # iterate
    print(record["input_data"])
```

### Append

```python
dataset.append({
    "input_data": {"question": "Capital of Canada?"},
    "expected_output": "Ottawa",
    "metadata": {"difficulty": "easy"},
})
```

### Update

```python
dataset.update(1, {
    "input_data": {"question": "What's the capital city of Chad?"},
    "expected_output": "N'Djamena",
    "metadata": {"difficulty": "hard"},
})
```

### Delete

```python
dataset.delete(0)
```

### Push to Datadog

```python
dataset.push()
dataset.url  # view updated dataset
```

## Dataset Versioning

- Versions start at `0` and auto-increment
- New version created when: adding, updating (`input`/`expected_output`), or deleting records
- **No** new version for metadata-only changes or name/description updates
- `dataset.current_version` returns latest version number

### Retention

| Version type | Retention |
|---|---|
| Active (current) | 3 years |
| Previous | 90 days (resets on use) |

Previous versions used by an experiment reset their 90-day window.
