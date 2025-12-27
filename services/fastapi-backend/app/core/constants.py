"""Application constants."""

# Timeouts (seconds)
GEMINI_API_TIMEOUT = 120  # 2 minutes for Gemini calls
VERTEX_AI_TIMEOUT = 60  # 1 minute for other Vertex AI calls
DEFAULT_API_TIMEOUT = 30  # 30 seconds default

# File limits (bytes)
MAX_FILE_SIZE_MB = 10  # 10MB per file
MAX_TOTAL_SIZE_MB = 30  # 30MB total (Cloud Run limit is 32MB)
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MAX_TOTAL_SIZE_BYTES = MAX_TOTAL_SIZE_MB * 1024 * 1024

# Input validation
MAX_PROMPT_LENGTH = 10000  # 10K characters
MAX_MESSAGES_COUNT = 100  # Maximum messages in conversation
MAX_FILENAME_LENGTH = 255  # Maximum filename length

# Rate limits (per minute)
RATE_LIMIT_VOTE_EXTRACTION = "10/minute"
RATE_LIMIT_CHAT = "30/minute"
RATE_LIMIT_GENERATE = "30/minute"
RATE_LIMIT_HEALTH = "100/minute"

# Rate limits (per hour)
RATE_LIMIT_VOTE_EXTRACTION_HOURLY = "100/hour"
RATE_LIMIT_CHAT_HOURLY = "500/hour"
RATE_LIMIT_GENERATE_HOURLY = "500/hour"

# Allowed file types
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png"}

# Schema
SCHEMA_HASH_LENGTH = 8

# Extraction
EXTRACTION_TIMEOUT_SECONDS = 120

