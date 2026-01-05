"""
Dataset Manager - Interactive Ground Truth Annotation

This Streamlit app provides a user-friendly interface for:
- Browsing Thai election form images
- Adding/editing ground truth data
- Saving datasets to local JSON
- Pushing datasets to Datadog LLMObs

Usage:
    streamlit run frontend/streamlit/pages/2_📊_Dataset_Manager.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
import streamlit as st
from PIL import Image

# Add project root to path
# In Docker: /app, Locally: project root
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# If we're at filesystem root, we're in Docker - use /app instead
if PROJECT_ROOT == Path("/"):
    PROJECT_ROOT = Path("/app")

sys.path.insert(0, str(PROJECT_ROOT))

# Configuration
IMAGES_DIR = PROJECT_ROOT / "assets" / "ss5-18-images"
DATASET_DIR = PROJECT_ROOT / "datasets" / "vote-extraction"

# Create dataset directory with proper error handling
try:
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
except (PermissionError, OSError) as e:
    # If we can't create in project root, use /tmp (always writable in Docker)
    import tempfile

    DATASET_DIR = Path(tempfile.gettempdir()) / "datasets" / "vote-extraction"
    DATASET_DIR.mkdir(parents=True, exist_ok=True)

    # Log the fallback
    import logging

    logger = logging.getLogger(__name__)
    logger.warning(
        f"Could not create datasets in {PROJECT_ROOT / 'datasets'}: {e}. "
        f"Using temporary directory: {DATASET_DIR}"
    )

# Datadog API configuration
DD_API_KEY = os.getenv("DD_API_KEY")
DD_APP_KEY = os.getenv("DD_APP_KEY")
DD_SITE = os.getenv("DD_SITE", "datadoghq.com")

# Page config
st.set_page_config(
    page_title="Dataset Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Display paths for debugging
import logging

logger = logging.getLogger(__name__)
logger.info(f"PROJECT_ROOT: {PROJECT_ROOT}")
logger.info(f"IMAGES_DIR: {IMAGES_DIR}")
logger.info(f"DATASET_DIR: {DATASET_DIR}")

# Custom CSS
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "dataset" not in st.session_state:
    st.session_state.dataset = None
if "current_record_idx" not in st.session_state:
    st.session_state.current_record_idx = 0
if "ground_truth" not in st.session_state:
    st.session_state.ground_truth = {}


def discover_images() -> List[Path]:
    """Discover all image files."""
    if not IMAGES_DIR.exists():
        return []
    return sorted(list(IMAGES_DIR.glob("*.jpg")) + list(IMAGES_DIR.glob("*.png")))


def group_images_by_form() -> Dict[str, List[Path]]:
    """Group images by form set (6 pages per set)."""
    images = discover_images()
    form_sets = {}

    for img_path in images:
        form_name = (
            img_path.stem.rsplit("_page", 1)[0] if "_page" in img_path.stem else img_path.stem
        )

        if form_name not in form_sets:
            form_sets[form_name] = []
        form_sets[form_name].append(img_path)

    return form_sets


def load_dataset(file_path: Path) -> Dict[str, Any]:
    """Load dataset from JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_dataset(dataset: Dict[str, Any], filename: str = None) -> Path:
    """Save dataset to JSON file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vote-extraction-dataset_{timestamp}.json"

    filepath = DATASET_DIR / filename

    # Update metadata
    dataset["metadata"]["num_records"] = len(dataset["records"])
    dataset["metadata"]["total_pages"] = sum(r["input"]["num_pages"] for r in dataset["records"])
    dataset["metadata"]["updated_at"] = datetime.now().isoformat()

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)

    # Create/update latest symlink
    latest_link = DATASET_DIR / "vote-extraction-dataset_latest.json"
    if latest_link.exists():
        latest_link.unlink()
    latest_link.symlink_to(filename)

    return filepath


def validate_ground_truth(ground_truth: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate ground truth data matching ElectionFormData schema."""
    errors = []

    # Check form_info
    form_info = ground_truth.get("form_info", {})
    if not form_info:
        errors.append("Missing form_info")
    else:
        required = ["district", "polling_station_number"]
        for field in required:
            if not form_info.get(field):
                errors.append(f"Missing required field 'form_info.{field}'")

    # Check ballot statistics
    ballot_stats = ground_truth.get("ballot_statistics", {})
    if not ballot_stats:
        errors.append("Missing ballot_statistics")
    else:
        # Validate ballot math if fields are present
        ballots_used = ballot_stats.get("ballots_used", 0)
        good = ballot_stats.get("good_ballots", 0)
        bad = ballot_stats.get("bad_ballots", 0)
        no_vote = ballot_stats.get("no_vote_ballots", 0)

        expected_used = good + bad + no_vote
        if ballots_used > 0 and ballots_used != expected_used:
            errors.append(
                f"Ballot math error: good({good}) + bad({bad}) + no_vote({no_vote}) = {expected_used} ≠ ballots_used({ballots_used})"
            )

    # Check vote results
    vote_results = ground_truth.get("vote_results", [])
    if not vote_results:
        errors.append("Missing or empty vote_results")
    else:
        for i, result in enumerate(vote_results):
            # Check required fields
            if "number" not in result:
                errors.append(f"Missing 'number' in vote_results[{i}]")
            elif not isinstance(result["number"], int):
                errors.append(f"'number' must be an integer in vote_results[{i}]")

            if "vote_count" not in result:
                errors.append(f"Missing 'vote_count' in vote_results[{i}]")
            elif not isinstance(result["vote_count"], int):
                errors.append(f"'vote_count' must be an integer in vote_results[{i}]")

            # Check that either candidate_name or party_name exists
            if not result.get("candidate_name") and not result.get("party_name"):
                errors.append(
                    f"Missing both 'candidate_name' and 'party_name' in vote_results[{i}]"
                )

    return len(errors) == 0, errors


def push_dataset_to_datadog(dataset: Dict[str, Any]) -> tuple[bool, str]:
    """
    Push dataset to Datadog LLMObs using the Python SDK.

    Uses LLMObs.create_dataset() to create a new dataset with records.
    See: https://docs.datadoghq.com/llm_observability/experiments/
    """
    if not DD_API_KEY or not DD_APP_KEY:
        return False, "⚠️ Datadog API keys not configured"

    try:
        # Import ddtrace LLMObs
        from ddtrace.llmobs import LLMObs

        # Initialize LLMObs if not already enabled
        # Note: DD_API_KEY and DD_SITE should be set in environment
        if not os.getenv("DD_LLMOBS_ENABLED"):
            os.environ["DD_LLMOBS_ENABLED"] = "1"
            os.environ["DD_LLMOBS_AGENTLESS_ENABLED"] = "1"

        # Enable LLMObs with project name
        LLMObs.enable(
            ml_app="vote-extractor",
            api_key=DD_API_KEY,
            site=DD_SITE,
            agentless_enabled=True,
        )

        # Prepare dataset metadata
        dataset_name = dataset["metadata"]["name"]
        description = dataset["metadata"].get("description", "")

        # Transform records to Datadog SDK format
        # SDK expects: input_data, expected_output, metadata (all optional but input_data required)
        records = []
        for record in dataset["records"]:
            sdk_record = {
                "input_data": record["input"],  # Required
                "expected_output": record.get("ground_truth", {}),  # Optional
                "metadata": {  # Optional
                    "record_id": record["id"],
                    "pages_processed": record.get("pages_processed", 0),
                    "created_at": record.get("created_at", ""),
                },
            }
            records.append(sdk_record)

        # Create dataset using SDK
        dataset_obj = LLMObs.create_dataset(
            dataset_name=dataset_name,
            project_name="vote-extraction-project",
            description=description,
            records=records,
        )

        # Get dataset URL
        dataset_url = (
            dataset_obj.url
            if hasattr(dataset_obj, "url")
            else f"https://app.{DD_SITE}/llm/experiments"
        )

        success_msg = f"""
✅ **Dataset Created Successfully!**

**Name**: {dataset_name}
**Records**: {len(records)}
**Pages**: {sum(r.get('pages_processed', 0) for r in dataset['records'])}

---

### 🔗 View in Datadog:
[Open Dataset in Datadog LLMObs]({dataset_url})

---

### 📊 What's Next?
1. **View Dataset**: Click the link above to see your dataset in Datadog
2. **Run Experiments**: Use this dataset to evaluate your LLM models
3. **Compare Results**: Analyze predictions against ground truth
4. **Create More Datasets**: Process more election forms using the Dataset Manager

---

### ℹ️ Dataset Versioning:
- Datasets are automatically versioned
- Current version: `{dataset_obj.current_version if hasattr(dataset_obj, 'current_version') else 0}`
- Version retention: 90 days for previous versions
        """

        return True, success_msg.strip()

    except ImportError:
        return False, "❌ ddtrace library not installed. Install with: `pip install ddtrace`"
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        return (
            False,
            f"❌ Error pushing to Datadog:\n\n{str(e)}\n\n**Details**:\n```\n{error_details}\n```",
        )


# ============================================================================
# Main App
# ============================================================================

st.title("📊 Dataset Manager")
st.markdown("Interactive tool for managing vote extraction datasets with ground truth annotation")

# Show warning if using temporary storage
if "/tmp" in str(DATASET_DIR) or "/var/tmp" in str(DATASET_DIR):
    st.warning(
        "⚠️ **Temporary Storage Mode**: Datasets are saved to `/tmp` and will be lost when the container restarts. "
        "To persist data, configure volume mounting in `docker-compose.yml`. "
        "See the 📁 Storage Paths section in the sidebar for details."
    )

# Sidebar
with st.sidebar:
    st.header("Dataset Management")

    # Dataset operations
    operation = st.radio(
        "Choose operation:",
        ["📝 Create/Edit Dataset", "📁 Load Existing Dataset", "📤 Push to Datadog"],
    )

    st.markdown("---")

    # Show dataset info if loaded
    if st.session_state.dataset:
        st.metric("Records", len(st.session_state.dataset["records"]))
        st.metric(
            "Total Pages",
            sum(r["input"]["num_pages"] for r in st.session_state.dataset["records"]),
        )
    else:
        st.info("No dataset loaded")

    st.markdown("---")

    # Show storage paths
    with st.expander("📁 Storage Paths", expanded=False):
        st.code(f"Images: {IMAGES_DIR}", language="text")
        st.code(f"Datasets: {DATASET_DIR}", language="text")

        # Check if paths exist
        if IMAGES_DIR.exists():
            st.success("✅ Images directory found")
        else:
            st.warning(f"⚠️ Images directory not found: {IMAGES_DIR}")

        # Warn if using temporary directory
        if "/tmp" in str(DATASET_DIR) or "/var/tmp" in str(DATASET_DIR):
            st.warning("⚠️ Using temporary directory (data will be lost on restart)")
            st.info(
                "**To persist datasets**: Mount a volume to `/app/datasets` in docker-compose.yml:\n"
                "```yaml\n"
                "volumes:\n"
                "  - ./datasets:/app/datasets\n"
                "```"
            )
        else:
            st.success(f"✅ Datasets directory ready")

    st.markdown("---")

    # Quick stats
    st.subheader("Available Images")
    images = discover_images()
    form_sets = group_images_by_form()
    st.metric("Total Images", len(images))
    st.metric("Form Sets", len(form_sets))

# Main content
if operation == "📝 Create/Edit Dataset":
    st.header("Create/Edit Dataset")

    # Dataset metadata
    with st.expander("📋 Dataset Metadata", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            dataset_name = st.text_input(
                "Dataset Name",
                value=(
                    st.session_state.dataset["metadata"]["name"]
                    if st.session_state.dataset
                    else "vote-extraction-dataset"
                ),
            )
            version = st.text_input(
                "Version",
                value=(
                    st.session_state.dataset["metadata"]["version"]
                    if st.session_state.dataset
                    else "v1"
                ),
            )

        with col2:
            description = st.text_area(
                "Description",
                value=(
                    st.session_state.dataset["metadata"].get("description", "")
                    if st.session_state.dataset
                    else "Thai election forms with ground truth"
                ),
                height=100,
            )

    # Form selection
    st.markdown("---")
    st.subheader("Select Form to Annotate")

    form_sets = group_images_by_form()
    form_names = list(form_sets.keys())

    if not form_names:
        st.error("❌ No images found")
        st.info(f"**Expected location**: `{IMAGES_DIR}`")
        st.markdown(
            """
        ### 📸 How to Add Images:
        
        1. **Local Development**:
           - Place images in `assets/ss5-18-images/`
           - Supported formats: `.jpg`, `.png`
        
        2. **Docker/Production**:
           - Mount volume: `-v /path/to/images:/app/assets/ss5-18-images`
           - Or copy images into container
        
        3. **Check Permissions**:
           - Ensure the app has read access to the images directory
        """
        )
        st.stop()

    selected_form = st.selectbox("Form Set", form_names)
    form_images = sorted(form_sets[selected_form])

    # Display images
    st.markdown(f"### 📸 Images for {selected_form} ({len(form_images)} pages)")

    # Show images in grid
    cols = st.columns(3)
    for i, img_path in enumerate(form_images):
        with cols[i % 3]:
            img = Image.open(img_path)
            st.image(img, caption=f"Page {i+1}: {img_path.name}", use_container_width=True)

    # Ground truth annotation
    st.markdown("---")
    st.subheader("📝 Ground Truth Annotation")

    with st.form(key="ground_truth_form"):
        # Form Info
        st.markdown("#### Form Information")
        col1, col2, col3 = st.columns(3)

        with col1:
            form_type = st.selectbox(
                "Form Type",
                ["Constituency", "PartyList"],
                index=0,
                help="Constituency: Individual candidates, PartyList: Political parties only",
            )
            province = st.text_input("Province", value="กรุงเทพมหานคร")
            district = st.text_input("District", value="", help="อำเภอ/เขต (e.g., บางกอกน้อย)")

        with col2:
            election_date = st.text_input(
                "Date", value="", help="Format: DD/MM/YYYY (e.g., 14/05/2566)"
            )
            sub_district = st.text_input("Sub-District", value="", help="ตำบล/แขวง (e.g., บางบำหรุ)")
            constituency_number = st.text_input("Constituency Number", value="", help="เขตเลือกตั้ง")

        with col3:
            polling_station_number = st.text_input(
                "Polling Station Number", value="", help="หน่วยเลือกตั้ง"
            )

        # Voter Statistics
        st.markdown("#### Voter Statistics")
        col1, col2 = st.columns(2)

        with col1:
            eligible_voters = st.number_input(
                "Eligible Voters", min_value=0, value=0, step=1, help="ผู้มีสิทธิเลือกตั้ง"
            )

        with col2:
            voters_present = st.number_input(
                "Voters Present", min_value=0, value=0, step=1, help="ผู้มาใช้สิทธิเลือกตั้ง"
            )

        # Ballot Statistics
        st.markdown("#### Ballot Statistics")
        col1, col2, col3 = st.columns(3)

        with col1:
            ballots_allocated = st.number_input(
                "Ballots Allocated", min_value=0, value=0, step=1, help="บัตรที่ได้รับ"
            )
            ballots_used = st.number_input(
                "Ballots Used", min_value=0, value=0, step=1, help="บัตรที่ใช้แล้ว"
            )

        with col2:
            good_ballots = st.number_input(
                "Good Ballots", min_value=0, value=0, step=1, help="บัตรดี"
            )
            bad_ballots = st.number_input(
                "Bad Ballots", min_value=0, value=0, step=1, help="บัตรเสีย"
            )

        with col3:
            no_vote_ballots = st.number_input(
                "No Vote Ballots", min_value=0, value=0, step=1, help="บัตรไม่ประสงค์ลงคะแนน"
            )
            ballots_remaining = st.number_input(
                "Ballots Remaining", min_value=0, value=0, step=1, help="บัตรคงเหลือ"
            )

        # Show validation
        if ballots_used > 0:
            expected_used = good_ballots + bad_ballots + no_vote_ballots
            if ballots_used == expected_used:
                st.success(
                    f"✅ Ballot math correct: {good_ballots} + {bad_ballots} + {no_vote_ballots} = {ballots_used}"
                )
            else:
                st.warning(
                    f"⚠️ Ballot math mismatch: {good_ballots} + {bad_ballots} + {no_vote_ballots} = {expected_used} ≠ {ballots_used}"
                )

        # Vote Results
        st.markdown("#### Vote Results")

        num_candidates = st.number_input(
            f"Number of {('Candidates' if form_type == 'Constituency' else 'Parties')}",
            min_value=1,
            max_value=100,
            value=2,
            help="Max 100 (PartyList forms can have up to 67 parties)",
        )

        vote_results = []
        for i in range(num_candidates):
            st.markdown(f"**{('Candidate' if form_type == 'Constituency' else 'Party')} #{i+1}**")
            col1, col2, col3, col4 = st.columns([1, 3, 3, 2])

            with col1:
                number = st.number_input(
                    "No.",
                    min_value=1,
                    value=i + 1,
                    key=f"number_{i}",
                    help="Candidate/Party number on ballot",
                )

            with col2:
                if form_type == "Constituency":
                    candidate_name = st.text_input(
                        "Candidate Name",
                        value="",
                        key=f"candidate_name_{i}",
                        help="Full name (e.g., นายจักรพันธ์ พรหมิมา)",
                    )
                else:
                    candidate_name = None

                party_name = st.text_input(
                    "Party Name",
                    value="",
                    key=f"party_name_{i}",
                    help="Political party (e.g., ภูมิใจไทย)",
                )

            with col3:
                vote_count = st.number_input(
                    "Vote Count",
                    min_value=0,
                    value=0,
                    step=1,
                    key=f"vote_count_{i}",
                    help="Numeric vote count",
                )

            with col4:
                vote_count_text = st.text_input(
                    "Thai Text",
                    value="",
                    key=f"vote_count_text_{i}",
                    help="Thai written (e.g., แปด, สามสิบเก้า)",
                )

            vote_results.append(
                {
                    "number": number,
                    "candidate_name": candidate_name if form_type == "Constituency" else None,
                    "party_name": party_name if party_name else None,
                    "vote_count": vote_count,
                    "vote_count_text": vote_count_text if vote_count_text else None,
                }
            )

        # Notes
        notes = st.text_area("Notes", placeholder="Any important observations...", height=100)

        # Submit button
        submitted = st.form_submit_button("💾 Save Ground Truth", type="primary")

        if submitted:
            # Build ground truth matching ElectionFormData schema
            ground_truth = {
                "form_info": {
                    "form_type": form_type,
                    "date": election_date if election_date else None,
                    "province": province if province else None,
                    "district": district,
                    "sub_district": sub_district if sub_district else None,
                    "constituency_number": constituency_number if constituency_number else None,
                    "polling_station_number": polling_station_number,
                },
                "voter_statistics": {
                    "eligible_voters": eligible_voters,
                    "voters_present": voters_present,
                },
                "ballot_statistics": {
                    "ballots_allocated": ballots_allocated,
                    "ballots_used": ballots_used,
                    "good_ballots": good_ballots,
                    "bad_ballots": bad_ballots,
                    "no_vote_ballots": no_vote_ballots,
                    "ballots_remaining": ballots_remaining,
                },
                "vote_results": vote_results,
                "notes": notes,
            }

            # Validate
            is_valid, errors = validate_ground_truth(ground_truth)

            if not is_valid:
                st.error("❌ Validation Failed:")
                for error in errors:
                    st.error(f"  - {error}")
            else:
                # Create or update dataset
                if not st.session_state.dataset:
                    st.session_state.dataset = {
                        "metadata": {
                            "name": dataset_name,
                            "version": version,
                            "description": description,
                            "created_at": datetime.now().isoformat(),
                            "num_records": 0,
                            "total_pages": 0,
                        },
                        "records": [],
                    }

                # Check if record exists
                record_exists = False
                for i, record in enumerate(st.session_state.dataset["records"]):
                    if record["id"] == selected_form:
                        # Update existing record
                        st.session_state.dataset["records"][i] = {
                            "id": selected_form,
                            "input": {
                                "form_set_name": selected_form,
                                "image_paths": [
                                    str(img.relative_to(PROJECT_ROOT)) for img in form_images
                                ],
                                "num_pages": len(form_images),
                                "form_type": form_type,
                                "province": province,
                                "district": district,
                            },
                            "expected_output": {
                                "ballot_statistics": ground_truth["ballot_statistics"],
                                "vote_results": ground_truth["vote_results"],
                            },
                            "metadata": {
                                "polling_station": polling_station,
                                "notes": notes,
                                "verified_by": "manual_review",
                                "verification_date": datetime.now().isoformat(),
                            },
                        }
                        record_exists = True
                        break

                if not record_exists:
                    # Add new record
                    st.session_state.dataset["records"].append(
                        {
                            "id": selected_form,
                            "input": {
                                "form_set_name": selected_form,
                                "image_paths": [
                                    str(img.relative_to(PROJECT_ROOT)) for img in form_images
                                ],
                                "num_pages": len(form_images),
                                "form_type": form_type,
                                "province": province,
                                "district": district,
                            },
                            "expected_output": {
                                "ballot_statistics": ground_truth["ballot_statistics"],
                                "vote_results": ground_truth["vote_results"],
                            },
                            "metadata": {
                                "polling_station": polling_station,
                                "notes": notes,
                                "verified_by": "manual_review",
                                "verification_date": datetime.now().isoformat(),
                            },
                        }
                    )

                # Save to file
                filepath = save_dataset(st.session_state.dataset)

                st.success(f"✅ Ground truth saved successfully!")
                st.info(f"📁 Saved to: `{filepath.relative_to(PROJECT_ROOT)}`")
                st.balloons()

elif operation == "📁 Load Existing Dataset":
    st.header("Load Existing Dataset")

    # Upload dataset from local machine
    st.subheader("📤 Upload Dataset from Local Machine")
    uploaded_file = st.file_uploader(
        "Upload a dataset JSON file",
        type=["json"],
        help="Upload a previously exported dataset JSON file",
    )

    if uploaded_file is not None:
        try:
            # Read and parse the uploaded JSON
            dataset_content = json.loads(uploaded_file.read())

            # Validate basic structure
            if "metadata" not in dataset_content or "records" not in dataset_content:
                st.error("❌ Invalid dataset format. Must contain 'metadata' and 'records' fields.")
            else:
                # Load into session state
                st.session_state.dataset = dataset_content

                # Optionally save to server storage
                col1, col2 = st.columns([3, 1])
                with col1:
                    save_name = st.text_input(
                        "Save as (optional):",
                        value=dataset_content["metadata"].get("name", "imported-dataset"),
                        key="upload_save_name",
                    )
                with col2:
                    st.write("")  # Spacer
                    st.write("")  # Spacer
                    if st.button("💾 Save to Server", key="save_uploaded"):
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"{save_name}_{timestamp}.json"
                        filepath = DATASET_DIR / filename

                        with open(filepath, "w", encoding="utf-8") as f:
                            json.dump(dataset_content, f, indent=2, ensure_ascii=False)

                        st.success(f"✅ Saved to server: {filename}")

                st.success(f"✅ Uploaded dataset: {dataset_content['metadata']['name']}")
                st.info(
                    f"📊 Records: {len(dataset_content['records'])} | Pages: {sum(r['input'].get('num_pages', 0) for r in dataset_content['records'])}"
                )

        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON file: {e}")
        except Exception as e:
            st.error(f"❌ Error loading file: {e}")

    st.markdown("---")

    # Load from server storage
    st.subheader("📂 Load from Server Storage")
    dataset_files = sorted(DATASET_DIR.glob("*.json"))

    if not dataset_files:
        st.warning("No dataset files found in `datasets/vote-extraction/`")
        st.info("Create a new dataset using the 'Create/Edit Dataset' tab")
    else:
        st.markdown(f"Found **{len(dataset_files)}** dataset files:")

        selected_file = st.selectbox(
            "Select dataset to load:",
            dataset_files,
            format_func=lambda x: f"{x.name} ({datetime.fromtimestamp(x.stat().st_mtime).strftime('%Y-%m-%d %H:%M')})",
        )

        if st.button("📂 Load Dataset", type="primary"):
            st.session_state.dataset = load_dataset(selected_file)
            st.success(f"✅ Loaded dataset: {st.session_state.dataset['metadata']['name']}")
            st.rerun()

    # Show current dataset
    if st.session_state.dataset:
        st.markdown("---")
        st.subheader("Current Dataset")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Name", st.session_state.dataset["metadata"]["name"])
        with col2:
            st.metric("Version", st.session_state.dataset["metadata"]["version"])
        with col3:
            st.metric("Records", len(st.session_state.dataset["records"]))
        with col4:
            st.metric(
                "Pages",
                sum(r["input"]["num_pages"] for r in st.session_state.dataset["records"]),
            )

        # Export/Download dataset to local machine
        st.markdown("### 💾 Export Dataset")
        st.markdown("Download the complete dataset (all fields) to your local machine")

        # Prepare export filename
        export_name = st.session_state.dataset["metadata"]["name"]
        export_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_filename = f"{export_name}_{export_timestamp}.json"

        # Convert dataset to JSON string
        dataset_json = json.dumps(st.session_state.dataset, indent=2, ensure_ascii=False)

        # Download button
        st.download_button(
            label="📥 Download Dataset (JSON)",
            data=dataset_json,
            file_name=export_filename,
            mime="application/json",
            help="Download the complete dataset with all fields to your local machine",
        )

        st.info(
            f"💡 **Export includes**: All metadata, records, input data, ground truth annotations, and custom fields.\n\n"
            f"**File**: `{export_filename}`"
        )

        # Show records
        with st.expander("📄 View Records", expanded=False):
            for i, record in enumerate(st.session_state.dataset["records"], 1):
                st.markdown(f"#### Record {i}: {record['id']}")
                st.json(record)

elif operation == "📤 Push to Datadog":
    st.header("Push Dataset to Datadog")

    st.info(
        "ℹ️ **SDK Method**: This tool uses `LLMObs.create_dataset()` from the ddtrace Python SDK to create datasets in Datadog LLM Observability."
    )

    if not st.session_state.dataset:
        st.warning("No dataset loaded. Create or load a dataset first.")
    else:
        st.markdown("### Dataset Summary")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Name", st.session_state.dataset["metadata"]["name"])
        with col2:
            st.metric("Records", len(st.session_state.dataset["records"]))
        with col3:
            st.metric(
                "Pages",
                sum(r["input"]["num_pages"] for r in st.session_state.dataset["records"]),
            )

        # API key check
        if not DD_API_KEY or not DD_APP_KEY:
            st.error("❌ Datadog API keys not configured")
            st.info(
                "**Required**: Set `DD_API_KEY` and `DD_APP_KEY` in your `.env` file and restart Streamlit\n\n"
                "These keys are required to push datasets using the Datadog SDK."
            )
        else:
            st.success("✅ Datadog API keys configured")

            # Push dataset to Datadog using SDK
            if st.button("🚀 Push to Datadog", type="primary"):
                with st.spinner("Creating dataset in Datadog..."):
                    success, result = push_dataset_to_datadog(st.session_state.dataset)

                    if success:
                        st.success("✅ Dataset created in Datadog!")
                        st.markdown(result)
                        st.balloons()
                    else:
                        st.error(result)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 2rem 0;'>
        <p>📚 See <a href='../../guides/llmobs/04_EXPERIMENTS_AND_DATASETS.md'>Guide 04: Experiments and Datasets</a> for more information</p>
        <p>💡 Need help? Check the <a href='../../notebooks/datasets/QUICKSTART.md'>Quick Start Guide</a></p>
    </div>
    """,
    unsafe_allow_html=True,
)
