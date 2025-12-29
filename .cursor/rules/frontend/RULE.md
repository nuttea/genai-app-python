# Frontend Development Rules (Streamlit)

## Scope
**Paths**: `frontend/streamlit/**/*.py`, `frontend/streamlit/pyproject.toml`

## Streamlit Architecture

### Project Structure
```
frontend/streamlit/
├── app.py                # Main page (landing/home)
├── pages/                # Multi-page app pages
│   └── 1_🗳️_Vote_Extractor.py
├── pyproject.toml        # Poetry dependencies
└── Dockerfile            # Production container
```

### Page Structure Template

```python
import streamlit as st
import httpx
from typing import Optional

# Page config (first Streamlit command)
st.set_page_config(
    page_title="Page Title",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "key" not in st.session_state:
    st.session_state.key = default_value

# Helper functions
def fetch_data() -> Optional[dict]:
    """Fetch data from backend API."""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{API_BASE_URL}/endpoint")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        st.error(f"Failed to fetch data: {e}")
        return None

# Main UI
st.title("🎯 Page Title")
st.write("Description of what this page does.")

# Use columns for layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Input")
    user_input = st.text_input("Enter something")

with col2:
    st.subheader("Output")
    if user_input:
        with st.spinner("Processing..."):
            result = fetch_data()
            if result:
                st.success("Success!")
                st.json(result)
```

## Code Standards

### Session State Management

```python
# ✅ Good - Initialize in one place, use consistently
if "results" not in st.session_state:
    st.session_state.results = None
if "processing" not in st.session_state:
    st.session_state.processing = False

# Update state
st.session_state.results = new_results
st.session_state.processing = True

# ❌ Bad - Direct attribute access without initialization
st.session_state.results = new_results  # May error if not initialized
```

### Caching

```python
# ✅ Good - Cache expensive operations
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_models() -> list[dict]:
    """Fetch available models from backend."""
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{API_BASE_URL}/models")
        return response.json()

@st.cache_resource
def get_http_client() -> httpx.Client:
    """Get HTTP client (singleton)."""
    return httpx.Client(timeout=30.0)

# ❌ Bad - No caching for expensive operations
def fetch_models() -> list[dict]:
    response = httpx.get(f"{API_BASE_URL}/models")
    return response.json()
```

### Error Handling

```python
# ✅ Good - User-friendly errors with context
try:
    result = process_data(data)
    st.success("✅ Processing complete!")
except httpx.TimeoutException:
    st.error("⏱️ Request timed out. Please try again.")
except httpx.HTTPStatusError as e:
    st.error(f"❌ Server error: {e.response.status_code}\n\nDetails: {e.response.text}")
except Exception as e:
    st.error(f"❌ Unexpected error: {str(e)}")
    st.exception(e)  # Show full traceback in development

# ❌ Bad - Generic error messages
try:
    result = process_data(data)
except Exception as e:
    st.error("Error occurred")
```

### Loading States

```python
# ✅ Good - Show progress for long operations
with st.spinner("Processing your request..."):
    result = slow_operation()

# or with progress bar
progress_bar = st.progress(0)
for i, item in enumerate(items):
    process_item(item)
    progress_bar.progress((i + 1) / len(items))
st.success("Complete!")

# ❌ Bad - No feedback
result = slow_operation()
```

### File Uploads

```python
# ✅ Good - Validate and provide feedback
uploaded_files = st.file_uploader(
    "Upload images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    help="Select one or more image files"
)

if uploaded_files:
    st.info(f"📎 {len(uploaded_files)} file(s) selected")
    
    # Validate file sizes
    total_size = sum(file.size for file in uploaded_files)
    max_size = 30 * 1024 * 1024  # 30MB
    
    if total_size > max_size:
        st.error(f"❌ Total size exceeds {max_size // (1024*1024)}MB limit")
    else:
        st.success(f"✅ Total size: {total_size / (1024*1024):.2f}MB")

# ❌ Bad - No validation
uploaded_files = st.file_uploader("Upload files")
if uploaded_files:
    process_files(uploaded_files)
```

### Sidebar Configuration

```python
# ✅ Good - Organized sidebar with sections
with st.sidebar:
    st.title("⚙️ Settings")
    
    with st.expander("🔧 Advanced Options", expanded=False):
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.0,
            step=0.1,
            help="Higher = more creative, Lower = more deterministic"
        )
        
        max_tokens = st.number_input(
            "Max Output Tokens",
            min_value=1024,
            max_value=65536,
            value=16384,
            step=1024
        )
    
    if st.button("🔄 Reset to Defaults"):
        st.session_state.clear()
        st.rerun()

# ❌ Bad - Cluttered sidebar
st.sidebar.slider("Temperature", 0.0, 2.0, 0.0)
st.sidebar.number_input("Max Tokens", 1024, 65536, 16384)
```

### API Calls

```python
# ✅ Good - Proper timeout and error handling
def call_backend_api(endpoint: str, data: dict) -> Optional[dict]:
    """Call backend API with error handling."""
    try:
        with httpx.Client(
            base_url=API_BASE_URL,
            timeout=30.0,
            headers={"X-API-Key": API_KEY}
        ) as client:
            response = client.post(endpoint, json=data)
            response.raise_for_status()
            return response.json()
    except httpx.TimeoutException:
        st.error("Request timed out")
        return None
    except httpx.HTTPStatusError as e:
        st.error(f"Server error: {e.response.status_code}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None

# ❌ Bad - No timeout, poor error handling
def call_backend_api(endpoint: str, data: dict):
    response = httpx.post(f"{API_BASE_URL}{endpoint}", json=data)
    return response.json()
```

### Layout Best Practices

```python
# ✅ Good - Responsive layout with columns
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.subheader("Main Content")
    st.write("Primary information here")

with col2:
    st.metric("Success Rate", "95%", "+2%")

with col3:
    st.metric("Avg Time", "2.3s", "-0.1s")

# Tabs for organized content
tab1, tab2, tab3 = st.tabs(["📊 Results", "📄 Raw Data", "⚙️ Config"])

with tab1:
    st.plotly_chart(figure)

with tab2:
    st.json(raw_data)

with tab3:
    st.code(config, language="json")

# ❌ Bad - Everything in single column
st.subheader("Content")
st.write("Everything")
st.metric("Metric", "Value")
st.json(data)
```

### Datadog RUM Integration

```python
# ✅ Good - Add RUM script in page header
def add_datadog_rum():
    """Add Datadog RUM script to page."""
    DD_RUM_APPLICATION_ID = st.secrets.get("DD_RUM_APPLICATION_ID")
    DD_RUM_CLIENT_TOKEN = st.secrets.get("DD_RUM_CLIENT_TOKEN")
    
    if DD_RUM_APPLICATION_ID and DD_RUM_CLIENT_TOKEN:
        rum_script = f"""
        <script>
        (function(h,o,u,n,d) {{
            h=h[d]=h[d]||{{q:[],onReady:function(c){{h.q.push(c)}}}}
            d=o.createElement(u);d.async=1;d.src=n
            n=o.getElementsByTagName(u)[0];n.parentNode.insertBefore(d,n)
        }})(window,document,'script','https://www.datadoghq-browser-agent.com/us1/v5/datadog-rum.js','DD_RUM')
        window.DD_RUM.onReady(function() {{
            window.DD_RUM.init({{
                clientToken: '{DD_RUM_CLIENT_TOKEN}',
                applicationId: '{DD_RUM_APPLICATION_ID}',
                site: 'datadoghq.com',
                service: 'streamlit-frontend',
                env: 'production',
                sessionSampleRate: 100,
                sessionReplaySampleRate: 20,
                trackUserInteractions: true,
                trackResources: true,
                trackLongTasks: true,
            }})
        }})
        </script>
        """
        st.components.v1.html(rum_script, height=0)

# Add at the start of your app
add_datadog_rum()
```

## Common Patterns

### Form Submission

```python
# ✅ Good - Form with validation
with st.form("my_form"):
    st.write("Fill out the form")
    
    name = st.text_input("Name")
    email = st.text_input("Email")
    
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        if not name or not email:
            st.error("Please fill all fields")
        elif "@" not in email:
            st.error("Invalid email")
        else:
            st.success("Form submitted!")
            process_submission(name, email)
```

### Download Results

```python
# ✅ Good - Provide download button
import json

if results:
    st.download_button(
        label="📥 Download JSON",
        data=json.dumps(results, indent=2),
        file_name="results.json",
        mime="application/json"
    )
```

## Don't

- ❌ Don't use `st.experimental_*` - use stable APIs
- ❌ Don't forget to initialize session state before use
- ❌ Don't skip error handling on API calls
- ❌ Don't use `st.write()` for everything - use specific components
- ❌ Don't forget loading states for long operations
- ❌ Don't ignore mobile responsiveness
- ❌ Don't hardcode API URLs - use environment variables
- ❌ Don't forget to add `st.set_page_config()` at the top

