"""
Streamlit page for running LLM experiments with Datadog LLMObs.
"""

import json
import os
from typing import Any, Dict, List

import httpx
import streamlit as st

# Page config
st.set_page_config(
    page_title="Run Experiments - Vote Extractor",
    page_icon="🧪",
    layout="wide",
)

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")

st.title("🧪 Run Model Experiments")
st.markdown(
    """
Run experiments with multiple model configurations using Datadog LLMObs.
This will test different models on your dataset and track results in Datadog.
"""
)

# Initialize session state
if "experiment_results" not in st.session_state:
    st.session_state.experiment_results = None
if "model_configs" not in st.session_state:
    st.session_state.model_configs = [
        {
            "model": "gemini-2.5-flash",
            "temperature": 0.0,
            "name_suffix": "baseline",
            "metadata": {},
        }
    ]

# Configuration Section
st.header("📋 Configuration")

col1, col2 = st.columns(2)

with col1:
    st.subheader("LLMObs Settings")

    ml_app = st.text_input(
        "ML App Name",
        value="vote-extractor",
        help="Name of your ML application in Datadog",
    )

    site = st.selectbox(
        "Datadog Site",
        options=["datadoghq.com", "datadoghq.eu", "us3.datadoghq.com", "us5.datadoghq.com"],
        index=0,
        help="Your Datadog site domain",
    )

    project_name = st.text_input(
        "Project Name",
        value="vote-extraction-project",
        help="Project name in Datadog LLMObs",
    )

    agentless_enabled = st.checkbox(
        "Agentless Mode",
        value=True,
        help="Enable agentless mode for LLMObs",
    )

with col2:
    st.subheader("Dataset Settings")

    dataset_name = st.text_input(
        "Dataset Name",
        value="vote-extraction-bangbamru-1-10",
        help="Name of the dataset in Datadog",
    )

    dataset_version = st.number_input(
        "Dataset Version",
        min_value=0,
        value=0,
        help="Dataset version (0 = latest)",
    )
    if dataset_version == 0:
        dataset_version = None

    st.subheader("Experiment Settings")

    sample_size = st.number_input(
        "Sample Size",
        min_value=1,
        value=10,
        help="Number of samples to test (use smaller number for faster results)",
    )

    jobs = st.number_input(
        "Parallel Jobs",
        min_value=1,
        max_value=10,
        value=2,
        help="Number of parallel jobs for experiments",
    )

    raise_errors = st.checkbox(
        "Raise Errors",
        value=True,
        help="Stop on first error (uncheck to continue on errors)",
    )

# Model Configurations Section
st.header("🤖 Model Configurations")

st.markdown(
    """
Add multiple model configurations to compare. Each will run as a separate experiment.
"""
)

# Display existing configurations
for idx, config in enumerate(st.session_state.model_configs):
    with st.expander(
        f"Model {idx + 1}: {config['model']} (T={config['temperature']})", expanded=idx == 0
    ):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            model = st.selectbox(
                "Model",
                options=[
                    "gemini-2.5-flash",
                    "gemini-2.5-flash-lite",
                    "gemini-2.0-flash-exp",
                    "gemini-1.5-flash",
                    "gemini-1.5-pro",
                ],
                index=[
                    "gemini-2.5-flash",
                    "gemini-2.5-flash-lite",
                    "gemini-2.0-flash-exp",
                    "gemini-1.5-flash",
                    "gemini-1.5-pro",
                ].index(config["model"]),
                key=f"model_{idx}",
            )

        with col2:
            temperature = st.number_input(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=config["temperature"],
                step=0.1,
                key=f"temp_{idx}",
            )

        with col3:
            name_suffix = st.text_input(
                "Name Suffix",
                value=config.get("name_suffix", ""),
                key=f"suffix_{idx}",
                help="Optional custom name for this experiment",
            )

        # Metadata
        metadata_str = st.text_area(
            "Metadata (JSON)",
            value=json.dumps(config.get("metadata", {}), indent=2),
            height=100,
            key=f"metadata_{idx}",
            help="Additional tags/metadata as JSON",
        )

        try:
            metadata = json.loads(metadata_str) if metadata_str.strip() else {}
        except json.JSONDecodeError:
            st.error("Invalid JSON in metadata")
            metadata = {}

        # Update config
        st.session_state.model_configs[idx] = {
            "model": model,
            "temperature": temperature,
            "name_suffix": name_suffix,
            "metadata": metadata,
        }

        # Remove button
        if len(st.session_state.model_configs) > 1:
            if st.button(f"🗑️ Remove Model {idx + 1}", key=f"remove_{idx}"):
                st.session_state.model_configs.pop(idx)
                st.rerun()

# Add model button
if st.button("➕ Add Model Configuration"):
    st.session_state.model_configs.append(
        {
            "model": "gemini-2.5-flash",
            "temperature": 0.0,
            "name_suffix": f"config-{len(st.session_state.model_configs) + 1}",
            "metadata": {},
        }
    )
    st.rerun()

# Quick Presets
st.subheader("⚡ Quick Presets")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🎯 Baseline Comparison"):
        st.session_state.model_configs = [
            {
                "model": "gemini-2.5-flash",
                "temperature": 0.0,
                "name_suffix": "baseline",
                "metadata": {"purpose": "baseline"},
            },
            {
                "model": "gemini-2.5-flash-lite",
                "temperature": 0.0,
                "name_suffix": "lite",
                "metadata": {"purpose": "cost-optimization"},
            },
        ]
        st.rerun()

with col2:
    if st.button("🌡️ Temperature Test"):
        st.session_state.model_configs = [
            {
                "model": "gemini-2.5-flash",
                "temperature": 0.0,
                "name_suffix": "t0.0",
                "metadata": {"test": "temperature"},
            },
            {
                "model": "gemini-2.5-flash",
                "temperature": 0.1,
                "name_suffix": "t0.1",
                "metadata": {"test": "temperature"},
            },
            {
                "model": "gemini-2.5-flash",
                "temperature": 0.2,
                "name_suffix": "t0.2",
                "metadata": {"test": "temperature"},
            },
        ]
        st.rerun()

with col3:
    if st.button("🚀 Quick CI Test"):
        st.session_state.model_configs = [
            {
                "model": "gemini-2.5-flash-lite",
                "temperature": 0.0,
                "name_suffix": "ci-lite",
                "metadata": {"purpose": "ci-test"},
            },
            {
                "model": "gemini-2.5-flash",
                "temperature": 0.0,
                "name_suffix": "ci-flash",
                "metadata": {"purpose": "ci-test"},
            },
        ]
        st.rerun()

with col4:
    if st.button("🔄 Reset to Default"):
        st.session_state.model_configs = [
            {
                "model": "gemini-2.5-flash",
                "temperature": 0.0,
                "name_suffix": "baseline",
                "metadata": {},
            }
        ]
        st.rerun()

# Run Experiments Section
st.header("🚀 Run Experiments")

st.markdown(
    f"""
**Summary**: Will run **{len(st.session_state.model_configs)} experiment(s)** on **{sample_size} samples** from dataset `{dataset_name}`.

**Note**: Experiments will be tracked in Datadog LLMObs. You can view results in the Datadog dashboard.
"""
)

# Check API key
if not API_KEY:
    st.warning(
        "⚠️ API key not configured. Set `API_KEY` in your `.env` file to authenticate with the backend."
    )

# Run button
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    run_sync = st.button(
        "▶️ Run Experiments (Sync)",
        type="primary",
        use_container_width=True,
        help="Run experiments and wait for results (may take several minutes)",
    )

with col2:
    run_async = st.button(
        "⏱️ Run Experiments (Async)",
        use_container_width=True,
        help="Start experiments in background and return immediately",
    )

# Execute experiments
if run_sync or run_async:
    endpoint = "/run" if run_sync else "/run-async"

    # Prepare request
    request_data = {
        "ml_app": ml_app,
        "site": site,
        "agentless_enabled": agentless_enabled,
        "project_name": project_name,
        "dataset_name": dataset_name,
        "dataset_version": dataset_version,
        "model_configs": st.session_state.model_configs,
        "sample_size": sample_size,
        "jobs": jobs,
        "raise_errors": raise_errors,
    }

    # Show request preview
    with st.expander("📄 Request Preview"):
        st.json(request_data)

    # Make API call
    try:
        with st.spinner("Running experiments..." if run_sync else "Starting experiments..."):
            headers = {}
            if API_KEY:
                headers["X-API-Key"] = API_KEY

            with httpx.Client(timeout=600.0) as client:
                response = client.post(
                    f"{API_BASE_URL}/api/v1/experiments{endpoint}",
                    json=request_data,
                    headers=headers,
                )

                if response.status_code == 200:
                    result = response.json()
                    st.session_state.experiment_results = result

                    st.success(f"✅ {result.get('message', 'Experiments completed')}")

                    # Display results (sync only)
                    if run_sync:
                        st.header("📊 Results")

                        # Summary metrics
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric(
                                "Total Experiments",
                                result.get("total_experiments", 0),
                            )

                        with col2:
                            st.metric(
                                "Successful",
                                result.get("successful_experiments", 0),
                                delta_color="normal",
                            )

                        with col3:
                            st.metric(
                                "Failed",
                                result.get("failed_experiments", 0),
                                delta_color="inverse",
                            )

                        with col4:
                            st.metric("Dataset Size", result.get("dataset_size", 0))

                        # Comparison URL
                        if result.get("comparison_url"):
                            st.markdown(
                                f"""
**🔍 View in Datadog**: [Compare Experiments]({result['comparison_url']})
"""
                            )

                        # Individual experiment results
                        st.subheader("Experiment Details")

                        for exp in result.get("experiments", []):
                            status_icon = "✅" if exp["status"] == "success" else "❌"

                            with st.expander(
                                f"{status_icon} {exp['experiment_name']} - {exp['model']} (T={exp['temperature']})"
                            ):
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.markdown(f"**Status**: {exp['status']}")
                                    st.markdown(f"**Model**: {exp['model']}")
                                    st.markdown(f"**Temperature**: {exp['temperature']}")
                                    st.markdown(
                                        f"**Experiment URL**: [{exp['experiment_name']}]({exp['experiment_url']})"
                                    )

                                with col2:
                                    st.markdown(f"**Total Records**: {exp['total_records']}")
                                    st.markdown(f"**Successful**: {exp['successful_records']}")
                                    st.markdown(f"**Failed**: {exp['failed_records']}")

                                # Metrics
                                if exp.get("overall_accuracy") is not None:
                                    st.subheader("Metrics")
                                    mcol1, mcol2, mcol3 = st.columns(3)

                                    with mcol1:
                                        st.metric(
                                            "Overall Accuracy",
                                            f"{exp.get('overall_accuracy', 0):.2%}",
                                        )

                                    with mcol2:
                                        st.metric(
                                            "Success Rate",
                                            f"{exp.get('success_rate', 0):.2%}",
                                        )

                                    with mcol3:
                                        st.metric(
                                            "Avg Ballot Accuracy",
                                            f"{exp.get('avg_ballot_accuracy', 0):.2%}",
                                        )

                        # Export results
                        st.download_button(
                            label="📥 Download Results (JSON)",
                            data=json.dumps(result, indent=2),
                            file_name=f"experiment_results_{dataset_name}.json",
                            mime="application/json",
                        )

                elif response.status_code == 202:
                    result = response.json()
                    st.success(f"✅ {result.get('message', 'Experiments started')}")
                    st.info(
                        f"""
**Task ID**: {result.get('task_id', 'N/A')}

Experiments are running in the background. Check Datadog LLMObs dashboard for results.
"""
                    )

                else:
                    st.error(f"❌ Error {response.status_code}: {response.text}")

    except httpx.HTTPStatusError as e:
        st.error(f"❌ HTTP Error: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        st.error(f"❌ Request Error: {str(e)}")
        st.info("Make sure the FastAPI backend is running and accessible at the configured URL.")
    except Exception as e:
        st.error(f"❌ Unexpected Error: {str(e)}")

# Previous Results Section
if st.session_state.experiment_results:
    st.header("📜 Previous Results")

    result = st.session_state.experiment_results

    st.markdown(f"**Dataset**: {result.get('dataset_name', 'N/A')}")
    st.markdown(f"**Project**: {result.get('project_name', 'N/A')}")
    st.markdown(
        f"**Experiments**: {result.get('successful_experiments', 0)}/{result.get('total_experiments', 0)} successful"
    )

    if result.get("comparison_url"):
        st.markdown(f"**Comparison**: [View in Datadog]({result['comparison_url']})")

    if st.button("🗑️ Clear Previous Results"):
        st.session_state.experiment_results = None
        st.rerun()

# Help Section
with st.expander("ℹ️ Help"):
    st.markdown(
        """
### How to Use

1. **Configure LLMObs Settings**: Set your Datadog configuration (app name, site, project)
2. **Select Dataset**: Choose the dataset to test on
3. **Add Model Configurations**: Add one or more models to compare
4. **Adjust Experiment Settings**: Set sample size, parallel jobs, and error handling
5. **Run Experiments**: Click "Run Experiments" to start testing
6. **View Results**: See metrics and comparison URL after completion

### Quick Presets

- **Baseline Comparison**: Compare `gemini-2.5-flash` vs `gemini-2.5-flash-lite`
- **Temperature Test**: Test different temperatures on the same model
- **Quick CI Test**: Fast test with 2 models for CI/CD

### API Keys

Make sure to set the following environment variables:
- `DD_API_KEY`: Datadog API key for LLMObs
- `API_KEY`: FastAPI backend API key (for authentication)

### Datadog Integration

Results are automatically tracked in Datadog LLMObs. Use the comparison URL to view side-by-side results in the Datadog dashboard.
"""
    )
