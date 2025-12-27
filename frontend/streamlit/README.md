# Streamlit Frontend

Interactive web interface for the GenAI Application Platform built with Streamlit.

## Features

- **Multi-page Application**: Easy navigation with sidebar menu
- **Vote Extractor**: Upload and process Thai election forms (Form S.S. 5/18)
- **Real-time Processing**: See extraction results immediately
- **Multi-report Support**: Handle multiple reports in one upload
- **Data Export**: Download results as CSV or JSON
- **Responsive Design**: Works on desktop and mobile devices
- **API Key Integration**: Secure API communication

## Setup

### Prerequisites

- Python 3.11+
- Poetry (for dependency management)

### Install Poetry

```bash
# macOS/Linux
curl -sSL https://install.python-poetry.org | python3 -

# Or with pip
pip install poetry
```

### Local Development

1. **Install dependencies**:
   ```bash
   # With Poetry
   poetry install

   # Or activate Poetry shell
   poetry shell
   poetry install
   ```

2. **Configure secrets**:
   ```bash
   mkdir -p .streamlit
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # Edit secrets.toml with your API URL and API key
   ```

3. **Run the app**:
   ```bash
   # With Poetry
   poetry run streamlit run app.py

   # Or in Poetry shell
   poetry shell
   streamlit run app.py
   ```

4. **Access the app**:
   Open http://localhost:8501 in your browser

### Docker

```bash
# Build image (uses Poetry)
docker build -t streamlit-frontend .

# Run container
docker run -p 8501:8501 \
  -e API_BASE_URL=http://fastapi-backend:8000 \
  -e API_KEY=your-api-key \
  streamlit-frontend
```

Or use Docker Compose from project root:

```bash
docker-compose up streamlit-frontend
```

## Dependency Management with Poetry

### Add New Dependencies

```bash
# Add production dependency
poetry add package-name

# Add development dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Show dependencies
poetry show --tree
```

### Export to requirements.txt

```bash
# For Docker or pip-based deployments
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

## Project Structure

```
streamlit/
├── app.py                      # Main application entry point
├── pages/                      # Multi-page app pages
│   └── 1_🗳️_Vote_Extractor.py # Vote extraction page
├── .streamlit/                 # Streamlit configuration
│   ├── config.toml            # App configuration
│   └── secrets.toml.example   # Secrets template
├── pyproject.toml              # Poetry configuration
├── poetry.lock                 # Locked dependencies
├── requirements.txt            # Generated from Poetry (for Docker)
├── Dockerfile                  # Docker configuration
└── README.md                   # This file
```

## Configuration

### Secrets

Create `.streamlit/secrets.toml`:

```toml
# FastAPI Backend URL
API_BASE_URL = "http://localhost:8000"

# API Key (if backend requires authentication)
API_KEY = "your-api-key"
```

### Environment Variables

```bash
# Backend URL
export API_BASE_URL="http://localhost:8000"

# API Key
export API_KEY="your-api-key"
```

## Development

### Using Poetry

```bash
# Activate Poetry environment (Poetry 2.0+)
eval $(poetry env activate)

# Run app
streamlit run app.py

# Or run directly with poetry run
poetry run streamlit run app.py

# Run with auto-reload (default in Streamlit)
streamlit run app.py --server.fileWatcherType=auto

# Deactivate
deactivate
```

### Adding New Pages

1. Create a new file in `pages/` directory:
   ```python
   # pages/2_📊_New_Page.py
   import streamlit as st

   st.set_page_config(page_title="New Page", page_icon="📊")
   st.title("New Page")
   # Your page content
   ```

2. The page will automatically appear in the sidebar menu

## Troubleshooting

### "Connection refused" error

- Ensure the FastAPI backend is running
- Check `API_BASE_URL` in secrets.toml
- Verify network connectivity

### Images not processing

- Check image format (JPG, PNG only)
- Ensure images are not corrupted
- Check backend logs for errors

### Poetry Issues

```bash
# Clear Poetry cache
poetry cache clear pypi --all

# Reinstall dependencies
poetry install --sync

# Check Poetry environment
poetry env info
```

## Production Deployment

### Docker Compose

Included in main `docker-compose.yml`:

```yaml
streamlit-frontend:
  build: ./frontend/streamlit
  ports:
    - "8501:8501"
  environment:
    - API_BASE_URL=http://fastapi-backend:8000
    - API_KEY=${API_KEY}
```

### Cloud Run

```bash
cd ../../infra/cloud-run
./deploy-frontend.sh
```

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Multi-page Apps](https://docs.streamlit.io/library/get-started/multipage-apps)

---

**Built with ❤️ using Streamlit and Poetry**
