"""Thai Election Form Vote Extractor page."""

import json
import os
import sys

import httpx
import pandas as pd
import streamlit as st
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from components.feedback import (
    render_feedback_with_comment,
    render_star_rating,
    render_thumbs_feedback,
)
from utils.datadog_rum import init_datadog_rum


def get_config(key: str, default: str = "") -> str:
    """
    Get configuration from environment or secrets, with graceful fallback.

    Priority:
    1. Environment variable (Cloud Run, Docker Compose)
    2. Streamlit secrets.toml (local development)
    3. Default value

    Args:
        key: Configuration key name
        default: Default value if not found

    Returns:
        Configuration value
    """
    # First try environment variable
    env_value = os.getenv(key)
    if env_value:
        return env_value

    # Then try secrets.toml (for local development)
    try:
        return st.secrets.get(key, default)
    except Exception:
        # No secrets file (normal for Cloud Run deployment)
        return default


# Configuration - prioritize environment variable over secrets
API_BASE_URL = get_config("API_BASE_URL", "http://localhost:8000")
API_KEY = get_config("API_KEY", "")
API_ENDPOINT = f"{API_BASE_URL}/api/v1/vote-extraction/extract"

st.set_page_config(
    page_title="Vote Extractor",
    page_icon="🗳️",
    layout="wide",
)

# Initialize Datadog RUM for this page
rum_enabled = init_datadog_rum()

# Initialize session state for persisting extraction results
if "extraction_result" not in st.session_state:
    st.session_state.extraction_result = None
if "uploaded_file_names" not in st.session_state:
    st.session_state.uploaded_file_names = []


def display_multi_report_summary(data_list):
    """Display summary table for multiple reports."""
    st.info(f"📄 Extracted {len(data_list)} reports")

    with st.expander("📊 All Reports Summary", expanded=True):
        summary_data = []
        for idx, report in enumerate(data_list):
            form_info = report.get("form_info", {})
            vote_count = len(report.get("vote_results", []))
            summary_data.append(
                {
                    "Report": f"#{idx + 1}",
                    "District": form_info.get("district", "N/A"),
                    "Station": form_info.get("polling_station_number", "N/A"),
                    "Candidates/Parties": vote_count,
                    "Form Type": form_info.get("form_type", "N/A"),
                }
            )
        st.dataframe(summary_data)


def select_report_to_display(data_list):
    """Allow user to select which report to view."""
    # Use session state to remember selected report
    if "selected_report_idx" not in st.session_state:
        st.session_state.selected_report_idx = 0

    report_idx = st.selectbox(
        "Select Report to View Details",
        range(len(data_list)),
        index=st.session_state.selected_report_idx,
        format_func=lambda x: (
            f"Report #{x + 1} - "
            f"{data_list[x].get('form_info', {}).get('district', 'Unknown')} "
            f"Station {data_list[x].get('form_info', {}).get('polling_station_number', 'N/A')}"
        ),
        key="report_selector",
    )

    # Update session state
    st.session_state.selected_report_idx = report_idx

    data = data_list[report_idx]
    st.markdown(f"### Viewing Report #{report_idx + 1}")
    return data, report_idx


def display_report_data(data, data_list, report_idx):
    """Display detailed report data in tabs."""
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📋 Summary", "📊 Vote Results", "📦 Ballot Statistics", "🔍 Raw JSON"]
    )

    display_form_info_tab(tab1, data)
    display_vote_results_tab(tab2, data)
    display_ballot_stats_tab(tab3, data)
    display_raw_json_tab(tab4, data, data_list, report_idx)


def display_form_info_tab(tab, data):
    """Display form information tab."""
    with tab:
        st.markdown("### Form Information")
        form_info = data.get("form_info", {})

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Province", form_info.get("province", "N/A"))
            st.metric("District", form_info.get("district", "N/A"))
            if form_info.get("sub_district"):
                st.metric("Sub-district", form_info.get("sub_district", "N/A"))

        with col2:
            st.metric("Polling Station", form_info.get("polling_station_number", "N/A"))
            st.metric("Constituency", form_info.get("constituency_number", "N/A"))
            st.metric("Form Type", form_info.get("form_type", "N/A"))

        with col3:
            st.metric("Date", form_info.get("date", "N/A"))


def display_vote_results_tab(tab, data):
    """Display vote results tab."""
    with tab:
        form_type = data.get("form_info", {}).get("form_type", "")
        st.markdown(f"### Vote Results Table ({form_type})")
        vote_results = data.get("vote_results", [])

        if not vote_results:
            st.info("No vote results found")
            return

        # Prepare data for display based on form type
        display_results = []
        for r in vote_results:
            display_row = {"number": r.get("number")}

            # Handle names based on form type
            if form_type == "PartyList":
                # PartyList: Only show party_name
                party_name = r.get("party_name", "")
                display_row["party_name"] = (
                    party_name if party_name not in ("null", "None", "", None) else "N/A"
                )
            elif form_type == "Constituency":
                # Constituency: Show both candidate and party
                candidate_name = r.get("candidate_name", "")
                party_name = r.get("party_name", "")
                display_row["candidate_name"] = (
                    candidate_name if candidate_name not in ("null", "None", "", None) else "N/A"
                )
                display_row["party_name"] = (
                    party_name if party_name not in ("null", "None", "", None) else "N/A"
                )
            else:
                # Unknown form type - show whatever is available
                candidate_name = r.get("candidate_name", "")
                party_name = r.get("party_name", "")
                if candidate_name not in ("null", "None", "", None):
                    display_row["candidate_name"] = candidate_name
                if party_name not in ("null", "None", "", None):
                    display_row["party_name"] = party_name

            display_row["vote_count"] = r.get("vote_count", 0)
            display_row["vote_count_text"] = r.get("vote_count_text", "")
            display_results.append(display_row)

        # Display table
        st.dataframe(display_results)

        # Summary statistics
        total_votes = sum(r["vote_count"] for r in vote_results)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Votes Counted", f"{total_votes:,}")
        with col2:
            st.metric("Total Candidates/Parties", len(vote_results))

        # Download as CSV
        df = pd.DataFrame(display_results)
        csv = df.to_csv(index=False, encoding="utf-8-sig")  # utf-8-sig for Thai characters
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=f"vote_results_{form_type.lower()}.csv",
            mime="text/csv",
        )


def display_ballot_stats_tab(tab, data):
    """Display ballot statistics tab."""
    with tab:
        st.markdown("### Ballot Statistics")
        ballot_stats = data.get("ballot_statistics")

        if not ballot_stats:
            st.info("No ballot statistics found")
            return

        # Show allocated and remaining if available
        has_allocation_info = ballot_stats.get("ballots_allocated") or ballot_stats.get(
            "ballots_remaining"
        )
        if has_allocation_info:
            st.markdown("#### Ballot Allocation")
            col1, col2 = st.columns(2)
            with col1:
                allocated = ballot_stats.get("ballots_allocated", 0)
                if allocated:
                    st.metric(
                        "Ballots Allocated",
                        f"{allocated:,}",
                        help="Total ballots given to this station",
                    )
            with col2:
                remaining = ballot_stats.get("ballots_remaining", 0)
                if remaining:
                    st.metric("Ballots Remaining", f"{remaining:,}", help="Unused ballots")
            st.markdown("---")
            st.markdown("#### Ballot Usage")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Ballots Used",
                f"{ballot_stats.get('ballots_used', 0):,}",
                help="Total number of ballots used",
            )

        with col2:
            st.metric(
                "Valid Ballots",
                f"{ballot_stats.get('good_ballots', 0):,}",
                help="Number of valid ballots",
            )

        with col3:
            st.metric(
                "Void Ballots",
                f"{ballot_stats.get('bad_ballots', 0):,}",
                help="Number of spoiled/void ballots",
            )

        with col4:
            st.metric(
                "No Vote",
                f"{ballot_stats.get('no_vote_ballots', 0):,}",
                help="Number of no-vote ballots",
            )

        # Validation check
        total_accounted = (
            ballot_stats.get("good_ballots", 0)
            + ballot_stats.get("bad_ballots", 0)
            + ballot_stats.get("no_vote_ballots", 0)
        )
        ballots_used = ballot_stats.get("ballots_used", 0)

        if total_accounted == ballots_used:
            st.success("✅ Ballot counts match (Valid + Void + No Vote = Total Used)")
        else:
            st.error(
                f"❌ Ballot count mismatch: "
                f"Total Used ({ballots_used}) ≠ Sum ({total_accounted})"
            )


def display_raw_json_tab(tab, data, data_list, report_idx):
    """Display raw JSON tab."""
    with tab:
        st.markdown("### Complete Extracted Data (JSON)")
        st.json(data)

        col1, col2 = st.columns(2)

        with col1:
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            st.download_button(
                label="📥 Download This Report (JSON)",
                data=json_str,
                file_name=f"vote_data_report_{report_idx + 1 if len(data_list) > 1 else 1}.json",
                mime="application/json",
            )

        with col2:
            if len(data_list) > 1:
                all_json = json.dumps(data_list, indent=2, ensure_ascii=False)
                st.download_button(
                    label="📥 Download All Reports (JSON)",
                    data=all_json,
                    file_name="vote_data_all_reports.json",
                    mime="application/json",
                )


# Debug info (only show in development)
DD_ENV = os.getenv("DD_ENV", "development")
if DD_ENV == "development":
    with st.sidebar:
        with st.expander("🔧 Debug Info - Vote Extractor", expanded=False):
            st.text(f"API URL: {API_BASE_URL}")
            st.text(f"API Key: {'***' + API_KEY[-4:] if API_KEY else 'Not set'}")
            st.text(f"Environment: {os.getenv('DD_ENV', 'development')}")

            # RUM status
            rum_client = os.getenv("DD_RUM_CLIENT_TOKEN", "")
            rum_app_id = os.getenv("DD_RUM_APPLICATION_ID", "")
            rum_enabled = bool(rum_client and rum_app_id)
            st.text(f"RUM Enabled: {rum_enabled}")
            if rum_enabled:
                st.text(f"RUM Token: {rum_client[:10]}...")
                st.text(f"RUM App: {rum_app_id[:8]}...")


# Page header
st.title("🗳️ Thai Election Form Vote Extractor")
st.markdown(
    """
    Extract structured data from Thai election documents (Form S.S. 5/18).
    Upload multiple pages of the same report to get consolidated results.
    """
)

# Instructions
with st.expander("📖 How to use", expanded=False):
    st.markdown(
        """
        ### Instructions:

        1. **Prepare your images**: Scan or photograph election form pages (JPG or PNG format)
        2. **Upload files**: Click "Browse files" and select all pages of the same report
        3. **Extract data**: Click "Extract Vote Data" button
        4. **Review results**: View extracted data in JSON format

        ### Supported Formats:
        - Image types: JPG, JPEG, PNG
        - Multiple pages: Yes (will be consolidated into single report)
        - Form types: Constituency (candidates) and PartyList (parties)

        ### What gets extracted:
        - **Form Information**: Date, Province, District, Polling Station, etc.
        - **Ballot Statistics**: Total ballots used, valid, void, and no-vote counts
        - **Vote Results**: Complete table of candidates/parties with vote counts
        """
    )

st.markdown("---")

# Sidebar: LLM Configuration
with st.sidebar:
    st.header("⚙️ LLM Configuration")
    st.caption("Optional: Customize the AI model used for extraction")

    # Fetch available models from backend
    try:
        with httpx.Client(timeout=10.0) as client:  # 10 second timeout
            models_response = client.get(f"{API_BASE_URL}/api/v1/vote-extraction/models")
            models_config = models_response.json()
    except Exception as e:
        st.warning(f"Could not fetch models from API: {str(e)}")
        # Fallback to static list of common models
        models_config = {
            "providers": [
                {
                    "name": "vertex_ai",
                    "display_name": "Google Vertex AI",
                    "models": [
                        {
                            "name": "gemini-2.5-flash",
                            "display_name": "Gemini 2.5 Flash",
                            "context_window": 1048576,
                            "max_output_tokens": 8192,
                        },
                        {
                            "name": "gemini-2.0-flash-exp",
                            "display_name": "Gemini 2.0 Flash (Experimental)",
                            "context_window": 1048576,
                            "max_output_tokens": 8192,
                        },
                        {
                            "name": "gemini-1.5-flash-002",
                            "display_name": "Gemini 1.5 Flash",
                            "context_window": 1048576,
                            "max_output_tokens": 8192,
                        },
                        {
                            "name": "gemini-1.5-pro-002",
                            "display_name": "Gemini 1.5 Pro",
                            "context_window": 2097152,
                            "max_output_tokens": 8192,
                        },
                    ],
                    "default_model": "gemini-2.5-flash",
                    "supported": True,
                }
            ],
            "default_config": {
                "provider": "vertex_ai",
                "model": "gemini-2.5-flash",
                "temperature": 0.0,
                "max_tokens": 8192,
                "top_p": 0.95,
                "top_k": 40,
            },
        }

    use_custom_config = st.checkbox(
        "Use custom model configuration",
        value=False,
        help="Enable to customize provider, model, and parameters",
    )

    llm_config = None
    if use_custom_config:
        # Get supported providers
        supported_providers = [
            p for p in models_config.get("providers", []) if p.get("supported", False)
        ]

        if supported_providers:
            # Provider selection
            provider_options = {p["display_name"]: p["name"] for p in supported_providers}
            selected_provider_display = st.selectbox(
                "Provider", options=list(provider_options.keys()), help="Select the LLM provider"
            )
            selected_provider = provider_options[selected_provider_display]

            # Get provider details
            provider_data = next(
                (p for p in supported_providers if p["name"] == selected_provider), None
            )

            if provider_data:
                # Model selection
                model_options = {
                    m["display_name"]: m["name"] for m in provider_data.get("models", [])
                }
                selected_model_display = st.selectbox(
                    "Model",
                    options=list(model_options.keys()),
                    help="Select the specific model to use",
                )
                selected_model = model_options[selected_model_display]

                # Get model details for default values
                model_data = next(
                    (m for m in provider_data["models"] if m["name"] == selected_model), {}
                )

                # Advanced parameters in expander
                with st.expander("🔧 Advanced Parameters"):
                    temperature = st.slider(
                        "Temperature",
                        min_value=0.0,
                        max_value=2.0,
                        value=0.0,
                        step=0.1,
                        help="Lower = more deterministic, Higher = more creative",
                    )

                    max_tokens = st.number_input(
                        "Max Tokens",
                        min_value=1024,
                        max_value=model_data.get("max_output_tokens", 8192),
                        value=8192,
                        step=512,
                        help="Maximum number of tokens to generate",
                    )

                    top_p = st.slider(
                        "Top P",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.95,
                        step=0.05,
                        help="Nucleus sampling parameter",
                    )

                    top_k = st.number_input(
                        "Top K",
                        min_value=1,
                        max_value=100,
                        value=40,
                        step=1,
                        help="Top-k sampling parameter (Vertex AI)",
                    )

                # Build LLM config
                llm_config = {
                    "provider": selected_provider,
                    "model": selected_model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": top_p,
                    "top_k": top_k,
                }

                st.success(f"✅ Using: {selected_model_display}")
        else:
            st.warning("No supported providers available")
    else:
        default_config = models_config.get("default_config", {})
        st.info(
            f"Using default: {default_config.get('model', 'gemini-2.5-flash')}\n\n"
            f"Temperature: {default_config.get('temperature', 0.0)}"
        )

st.markdown("---")

# File uploader
st.subheader("📤 Upload Election Form Images")
st.caption("⚠️ Limits: 10MB per file, 30MB total upload size")

uploaded_files = st.file_uploader(
    "Choose image files (multiple pages supported)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    help="Upload all pages of the same election report. Maximum 10MB per file, 30MB total.",
)

# Check if files have changed (to clear old results)
current_file_names = [f.name for f in uploaded_files] if uploaded_files else []
if current_file_names != st.session_state.uploaded_file_names:
    st.session_state.uploaded_file_names = current_file_names
    st.session_state.extraction_result = None  # Clear old results when new files uploaded

# Display uploaded images preview
if uploaded_files:
    # Calculate total size
    total_size_bytes = sum(len(f.getvalue()) for f in uploaded_files)
    total_size_mb = total_size_bytes / (1024 * 1024)

    # Check size limits
    if total_size_mb > 30:
        st.error(
            f"❌ Total upload size ({total_size_mb:.1f}MB) exceeds 30MB limit. Please reduce file sizes or number of files."
        )
    elif total_size_mb > 25:
        st.warning(f"⚠️ Total upload size ({total_size_mb:.1f}MB) is close to the 30MB limit.")
    else:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded ({total_size_mb:.1f}MB total)")

    # Reset file pointers after reading
    for f in uploaded_files:
        f.seek(0)

    # Show thumbnails
    with st.expander("🖼️ Preview uploaded images", expanded=True):
        cols = st.columns(min(len(uploaded_files), 4))
        for idx, file in enumerate(uploaded_files):
            with cols[idx % 4]:
                image = Image.open(file)
                st.image(image, caption=f"Page {idx + 1}: {file.name}")
                file.seek(0)  # Reset file pointer for later reading

    # Show clear results button if results exist
    if st.session_state.extraction_result:
        if st.button("🗑️ Clear Previous Results", type="secondary"):
            st.session_state.extraction_result = None
            st.session_state.selected_report_idx = 0
            st.rerun()

st.markdown("---")

# Extract button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    extract_button = st.button(
        "🚀 Extract Vote Data",
        type="primary",
        disabled=not uploaded_files,
        use_container_width=True,
    )


def process_extraction(uploaded_files, llm_config=None):
    """Process extraction and display results."""
    # Prepare files for upload
    files = []
    for uploaded_file in uploaded_files:
        files.append(("files", (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)))

    # Prepare headers with API key if available
    headers: dict[str, str] = {}
    if API_KEY:
        headers["X-API-Key"] = API_KEY

    # Prepare data with optional LLM config
    data = {}
    if llm_config:
        data["llm_config_json"] = json.dumps(llm_config)

    # Call API
    with httpx.Client(timeout=120.0) as client:
        response = client.post(API_ENDPOINT, files=files, headers=headers, data=data)
        response.raise_for_status()
        return response.json()


def display_extraction_results(result):
    """Display extraction results."""
    st.markdown("---")
    st.subheader("📊 Extraction Results")

    if not result.get("success"):
        st.error(f"❌ Extraction failed: {result.get('error', 'Unknown error')}")
        st.info(
            f"Processed {result['pages_processed']} page(s), extracted {result.get('reports_extracted', 0)} report(s)"
        )
        return

    # Success - show results
    reports_extracted = result.get("reports_extracted", 0)
    st.success(
        f"✅ Successfully extracted {reports_extracted} report(s) from {result['pages_processed']} page(s)"
    )

    if result.get("error"):
        st.warning(f"⚠️ {result['error']}")

    data_list = result.get("data", [])
    if not data_list:
        st.info("No data extracted")
        return

    # Select and display report
    if len(data_list) > 1:
        display_multi_report_summary(data_list)
        data, report_idx = select_report_to_display(data_list)
    else:
        data = data_list[0]
        report_idx = 0

    display_report_data(data, data_list, report_idx)

    # Add feedback section if span context is available
    span_context = result.get("span_context")
    if span_context and span_context.get("span_id") and span_context.get("trace_id"):
        st.markdown("---")
        st.header("💬 Feedback & Trace Information")

        # Display span context for debugging/transparency
        with st.expander("🔍 Trace Context (for Datadog LLMObs)", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input(
                    "Span ID (hex)",
                    value=span_context["span_id"],
                    disabled=True,
                    help="Unique identifier for this specific operation (64-bit hexadecimal)",
                )
            with col2:
                st.text_input(
                    "Trace ID (hex)",
                    value=span_context["trace_id"],
                    disabled=True,
                    help="Unique identifier for the entire request trace (128-bit hexadecimal)",
                )

            # Create Datadog trace link
            # Datadog US1 site format: https://app.datadoghq.com/apm/trace/{trace_id}
            trace_id = span_context["trace_id"]
            datadog_url = f"https://app.datadoghq.com/apm/trace/{trace_id}"

            st.markdown(
                f"🔗 **[View this trace in Datadog LLMObs]({datadog_url})**",
                unsafe_allow_html=False,
            )

            st.info(
                "💡 **Trace Context**: These hexadecimal IDs link your feedback to the specific AI operation "
                "in Datadog, enabling precise performance tracking and quality monitoring. "
                "Click the link above to view the full trace with spans, metrics, and evaluations."
            )

        # Feedback options in tabs
        tab1, tab2, tab3 = st.tabs(
            ["⭐ Rating + Comment", "👍 Quick Thumbs", "💭 Star Rating Only"]
        )

        with tab1:
            st.markdown("**Rate this extraction and optionally add a comment**")
            render_feedback_with_comment(
                span_id=span_context["span_id"],
                trace_id=span_context["trace_id"],
                ml_app="vote-extraction-app",
                feature="vote-extraction",
                key_suffix=f"vote_extraction_full_{report_idx}",
                session_id=st.session_state.get("session_id"),
            )

        with tab2:
            st.markdown("**Quick feedback: Was this extraction helpful?**")
            render_thumbs_feedback(
                span_id=span_context["span_id"],
                trace_id=span_context["trace_id"],
                ml_app="vote-extraction-app",
                feature="vote-extraction",
                key_suffix=f"vote_extraction_thumbs_{report_idx}",
                session_id=st.session_state.get("session_id"),
            )

        with tab3:
            st.markdown("**Rate the accuracy of this extraction**")
            render_star_rating(
                span_id=span_context["span_id"],
                trace_id=span_context["trace_id"],
                ml_app="vote-extraction-app",
                feature="vote-extraction",
                key_suffix=f"vote_extraction_rating_{report_idx}",
                session_id=st.session_state.get("session_id"),
            )
    else:
        # No span context - feedback not available
        pass


# Process extraction
if extract_button and uploaded_files:
    with st.spinner("🔄 Processing images and extracting data..."):
        try:
            result = process_extraction(uploaded_files, llm_config)
            # Store result in session state
            st.session_state.extraction_result = result
        except httpx.ConnectError as e:
            st.error("❌ Cannot connect to the backend API server")
            st.error(f"API URL: {API_BASE_URL}")
            st.info(
                """
                **Possible causes:**
                1. The FastAPI backend is not running
                2. Wrong API URL configuration
                3. Network connectivity issues

                **Solutions:**
                - Check if FastAPI backend is running: `docker-compose ps`
                - Verify API URL in configuration
                - Restart services: `docker-compose restart`
                """
            )
            with st.expander("🔍 Technical Details"):
                st.exception(e)

        except httpx.TimeoutException:
            st.error(
                "⏱️ Request timed out. The images may be too large or the server is busy. Please try again."
            )

        except httpx.HTTPStatusError as e:
            st.error(f"❌ Server error: {e.response.status_code}")
            try:
                error_detail = e.response.json().get("detail", str(e))
                st.error(f"Details: {error_detail}")
            except Exception:
                st.error(f"Details: {str(e)}")

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            with st.expander("🔍 Technical Details"):
                st.exception(e)

# Display results from session state (persists across reruns)
if st.session_state.extraction_result:
    display_extraction_results(st.session_state.extraction_result)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px;'>
        💡 Tip: For best results, ensure images are clear and properly oriented.<br>
        The system supports multi-page documents and will consolidate all pages into a single report.
    </div>
    """,
    unsafe_allow_html=True,
)
