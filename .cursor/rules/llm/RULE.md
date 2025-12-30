# LLM Integration Rules

## Scope
**Paths**: `**/services/**/*llm*.py`, `**/services/**/*genai*.py`, `**/services/vote_extraction_service.py`

## Vertex AI / Gemini Configuration

### Model Selection

#### Default Model
- **Production**: `gemini-2.5-flash`
- **Reason**: Fast, cost-effective, 1M context, 65K output
- **Temperature**: `0.0` for structured extraction (deterministic)

#### Available Models
```python
RECOMMENDED_MODELS = {
    "gemini-2.5-flash": {  # ← DEFAULT
        "context": 1_048_576,
        "output": 65_536,
        "use_case": "Fast structured extraction"
    },
    "gemini-2.5-pro": {
        "context": 1_048_576,
        "output": 65_536,
        "use_case": "Complex reasoning, high accuracy"
    },
    "gemini-2.0-flash": {
        "context": 1_048_576,
        "output": 8_192,
        "use_case": "Budget-friendly option"
    }
}
```

### Token Configuration

#### Default Limits
```python
DEFAULT_MAX_TOKENS = 16384  # Handles 5-6 pages
MAXIMUM_TOKENS = 65536      # Gemini 2.5 Flash limit
MINIMUM_TOKENS = 1024       # Safety minimum
```

#### Capacity Guidelines
| Document Size | Recommended max_tokens |
|--------------|----------------------|
| 1-2 pages | 8,192 |
| 3-4 pages | 16,384 (default) |
| 5-6 pages | 16,384 - 24,576 |
| 7-10 pages | 24,576 - 32,768 |
| 11+ pages | 32,768 - 65,536 |

### Client Initialization

```python
# ✅ Good - Proper Vertex AI client
from google import genai
from google.genai import types

def get_client() -> genai.Client:
    """Get configured Vertex AI client."""
    return genai.Client(
        vertexai=True,
        project=settings.google_cloud_project,
        location=settings.vertex_ai_location
    )

# ❌ Bad - Using Google AI API in production
client = genai.Client(api_key=api_key)  # Wrong for Vertex AI
```

### Generation Pattern

```python
# ✅ Good - Structured output with schema
async def generate_structured_output(
    images: list[bytes],
    schema: dict,
    model: str = "gemini-2.5-flash",
    temperature: float = 0.0,
    max_tokens: int = 16384
) -> dict:
    """Generate structured output from images."""

    client = get_client()

    # Prepare content
    content_parts = [
        types.Part.from_text("Extract structured data from these images."),
        *[types.Part.from_bytes(data=img, mime_type="image/jpeg") for img in images]
    ]

    # Generate with schema
    response = client.models.generate_content(
        model=model,
        contents=content_parts,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,  # ← IMPORTANT: Forces JSON
            temperature=temperature,
            max_output_tokens=max_tokens,
            top_p=0.95,
            top_k=40
        )
    )

    # Parse response
    if not response.text:
        raise ValueError("Empty response from model")

    try:
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON from model: {e}")
        logger.error(f"Response text: {response.text[:500]}")
        raise ValueError(f"Model returned invalid JSON: {e}")

# ❌ Bad - No schema, unpredictable output
response = client.models.generate_content(
    model=model,
    contents=prompt
)
return response.text  # Might not be valid JSON
```

### Schema Definition

```python
# ✅ Good - Detailed schema with descriptions
ELECTION_DATA_SCHEMA = {
    "type": "object",
    "properties": {
        "reports": {
            "type": "array",
            "description": "List of election reports extracted from pages",
            "items": {
                "type": "object",
                "properties": {
                    "province": {
                        "type": "string",
                        "description": "Province name in Thai"
                    },
                    "district": {
                        "type": "string",
                        "description": "District name in Thai"
                    },
                    "vote_results": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "candidate_number": {"type": "integer"},
                                "candidate_name": {"type": "string"},
                                "votes": {"type": "integer"}
                            },
                            "required": ["candidate_number", "candidate_name", "votes"]
                        }
                    }
                },
                "required": ["province", "district", "vote_results"]
            }
        }
    },
    "required": ["reports"]
}

# ❌ Bad - Vague schema
schema = {
    "type": "object",
    "properties": {
        "data": {"type": "array"}
    }
}
```

### Error Handling

```python
# ✅ Good - Comprehensive error handling
from google.api_core.exceptions import GoogleAPIError

try:
    response = await generate_with_retry(images, schema)
except json.JSONDecodeError as e:
    # Model returned invalid JSON (truncation?)
    logger.error(f"JSON parsing failed: {e}", extra={"response_length": len(response.text)})
    raise ValueError(f"Invalid JSON from model. May need higher max_tokens. Error: {e}")

except GoogleAPIError as e:
    # Vertex AI API error
    logger.error(f"Vertex AI error: {e}", extra={"error_code": e.code})
    raise HTTPException(status_code=503, detail=f"LLM service error: {str(e)}")

except ValueError as e:
    # Schema validation or empty response
    logger.error(f"Validation error: {e}")
    raise HTTPException(status_code=422, detail=str(e))

# ❌ Bad - Generic catch-all
try:
    response = generate(images)
    return json.loads(response.text)
except Exception as e:
    return {"error": str(e)}
```

### Retry Logic

```python
# ✅ Good - Exponential backoff with jitter
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def generate_with_retry(images: list[bytes], schema: dict) -> dict:
    """Generate with automatic retry on transient failures."""
    return await generate_structured_output(images, schema)

# ❌ Bad - No retry for transient failures
result = await generate_structured_output(images, schema)
```

### Datadog LLM Observability

```python
# ✅ Good - Full LLMObs integration
from ddtrace.llmobs import LLMObs

def annotate_llm_span(
    span,
    model_name: str,
    input_tokens: int,
    output_tokens: int,
    temperature: float
):
    """Annotate span with LLM metrics."""
    span.set_tag("llm.model_name", model_name)
    span.set_tag("llm.temperature", temperature)
    span.set_metric("llm.tokens.input", input_tokens)
    span.set_metric("llm.tokens.output", output_tokens)
    span.set_metric("llm.tokens.total", input_tokens + output_tokens)

# In your generation function
with tracer.trace("llm.generation", service="fastapi-backend") as span:
    annotate_llm_span(span, model, input_tokens, output_tokens, temperature)
    response = await generate(...)

# ❌ Bad - No observability
response = await generate(...)
```

### Prompt Engineering

```python
# ✅ Good - Clear, structured prompt
EXTRACTION_PROMPT = """
Extract structured election data from the provided images.

IMPORTANT RULES:
1. Extract ALL reports visible in the images
2. Use exact names from the forms (in Thai)
3. Ensure vote counts are numeric integers
4. Include all candidates even if votes = 0
5. Preserve the original order

Format the response according to the provided schema.
Return ONLY valid JSON, no markdown formatting.
"""

# ❌ Bad - Vague prompt
prompt = "Extract data from images"
```

## Common Patterns

### Image Processing

```python
# ✅ Good - Batch images in single request
def prepare_images(image_files: list[bytes]) -> list[types.Part]:
    """Prepare images for multi-page processing."""
    return [
        types.Part.from_bytes(data=img_data, mime_type="image/jpeg")
        for img_data in image_files
    ]

# Process all pages together
parts = [types.Part.from_text(PROMPT)] + prepare_images(images)
response = client.models.generate_content(model=model, contents=parts)

# ❌ Bad - Process images individually (slower, more expensive)
for image in images:
    response = client.models.generate_content(
        model=model,
        contents=[types.Part.from_bytes(image, "image/jpeg")]
    )
```

### Configuration Management

```python
# ✅ Good - Pydantic config model
from pydantic import BaseModel, Field

class LLMConfig(BaseModel):
    """LLM generation configuration."""
    provider: str = Field(default="vertex_ai")
    model: str = Field(default="gemini-2.5-flash")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    max_tokens: int = Field(default=16384, gt=0, le=65536)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    top_k: int = Field(default=40, gt=0)

# ❌ Bad - Dict with no validation
config = {
    "model": "gemini-2.5-flash",
    "temperature": 0.0
}
```

## Don't

- ❌ Don't use `temperature > 0.5` for structured extraction
- ❌ Don't ignore `max_tokens` limits (causes truncation)
- ❌ Don't forget `response_schema` for JSON output
- ❌ Don't process images individually (batch them)
- ❌ Don't skip error handling for JSON parsing
- ❌ Don't use Google AI API key in production (use Vertex AI)
- ❌ Don't forget LLMObs tracing for cost tracking
- ❌ Don't hardcode prompts (make them configurable)
