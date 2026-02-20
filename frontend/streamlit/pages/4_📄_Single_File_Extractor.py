"""Single File Extractor - BigQuery + Google Drive.

Query BigQuery for SS5/18 PDF files, select one, extract with Gemini,
and view the PDF side-by-side with structured results.
"""

import json
import os
import sys
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.bigquery_client import get_distinct_provinces, query_pdf_files
from utils.config import get_config
from utils.datadog_rum import init_datadog_rum
from utils.gemini_extractor import (
    MODEL_OPTIONS,
    build_drive_preview_url,
    extract_from_drive,
)
from utils.models import (
    ElectionFormData,
    get_number_value,
    get_thai_text,
    validate_extraction,
)

# Configuration
GEMINI_API_KEY = get_config("GEMINI_API_KEY")
GOOGLE_CLOUD_PROJECT = get_config("GOOGLE_CLOUD_PROJECT")

st.set_page_config(
    page_title="Single File Extractor",
    page_icon="📄",
    layout="wide",
)

rum_enabled = init_datadog_rum()

# Session state initialization
for key, default in {
    "sf_search_results": None,
    "sf_extraction_result": None,
    "sf_usage_metadata": None,
    "sf_selected_idx": 0,
    "sf_file_id": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Check required configuration ---
config_ok = True
if not GEMINI_API_KEY:
    st.error(
        "GEMINI_API_KEY is not configured. "
        "Set it in your `.env` file or Streamlit `secrets.toml`."
    )
    config_ok = False
if not GOOGLE_CLOUD_PROJECT:
    st.error(
        "GOOGLE_CLOUD_PROJECT is not configured. "
        "Set it in your `.env` file or Streamlit `secrets.toml`."
    )
    config_ok = False
if not config_ok:
    st.stop()

# --- Debug info (development only) ---
DD_ENV = os.getenv("DD_ENV", "development")
if DD_ENV == "development":
    with st.sidebar:
        with st.expander("🔧 Debug Info", expanded=False):
            st.text(f"Project: {GOOGLE_CLOUD_PROJECT}")
            st.text(f"API Key: {'***' + GEMINI_API_KEY[-4:] if len(GEMINI_API_KEY) > 4 else 'set'}")
            st.text(f"Environment: {DD_ENV}")

# --- Sidebar: Model Configuration ---
with st.sidebar:
    st.header("⚙️ Model Configuration")

    model_name = st.selectbox(
        "Gemini Model",
        options=MODEL_OPTIONS,
        index=0,
        help="Select the Gemini model for extraction",
    )

    with st.expander("🔧 Advanced Parameters"):
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1,
            help="Lower = more deterministic",
        )
        max_tokens = st.number_input(
            "Max Tokens",
            min_value=1024,
            max_value=65536,
            value=8192,
            step=512,
        )

# --- Page Header ---
st.title("📄 Single File Extractor")
st.markdown(
    "Query BigQuery for SS5/18 PDF files, extract data with Gemini, "
    "and preview the PDF side-by-side with results."
)

with st.expander("📖 How to use", expanded=False):
    st.markdown(
        """
        ### Instructions:

        1. **Search files**: Enter filters (province, path) and click Search
        2. **Select a file**: Choose a file from the results table
        3. **Extract data**: Click "Extract Data" to run Gemini extraction
        4. **Review**: Compare the PDF preview with extracted results
        5. **Save**: Download the result JSON for later use

        ### Requirements:
        - Google Drive files must be accessible (shared with link)
        - `GEMINI_API_KEY` and `GOOGLE_CLOUD_PROJECT` must be configured
        - BigQuery access requires `gcloud auth application-default login`
        """
    )

st.markdown("---")

# =====================================================================
# STEP 1: Search Files
# =====================================================================
st.subheader("🔍 Step 1: Search Files")

col_province, col_path = st.columns(2)

with col_province:
    province_filter = st.text_input(
        "จังหวัด (Province)",
        value="",
        placeholder="เช่น พิจิตร, แพร่, กรุงเทพมหานคร",
        help="Filter by exact province name. Leave empty for all provinces.",
    )

with col_path:
    path_filter = st.text_input(
        "เขตเลือกตั้ง (Path filter)",
        value="",
        placeholder="เช่น เขตเลือกตั้งที่ 1",
        help=(
            "Filter files whose path contains this text. "
            "Path structure: เขตเลือกตั้งที่ X/อำเภอYYY/ตำบลZZZ/หน่วยเลือกตั้งที่ N/สส5ทับ18.pdf"
        ),
    )

col_size1, col_size2, col_limit = st.columns(3)
with col_size1:
    min_size_kb = st.number_input("Min size (KB)", value=50.0, min_value=0.0, step=10.0)
with col_size2:
    max_size_mb = st.number_input("Max size (MB)", value=50.0, min_value=0.1, step=5.0)
with col_limit:
    limit = st.number_input("Max results", value=50, min_value=1, max_value=500, step=10)

search_button = st.button("🔍 Search Files", type="primary", use_container_width=True)

if search_button:
    with st.spinner("Querying BigQuery..."):
        try:
            results = query_pdf_files(
                project_id=GOOGLE_CLOUD_PROJECT,
                limit=limit,
                province=province_filter.strip() or None,
                path_contains=path_filter.strip() or None,
                min_size_kb=min_size_kb,
                max_size_mb=max_size_mb,
            )
            st.session_state.sf_search_results = results
            # Clear previous extraction when new search
            st.session_state.sf_extraction_result = None
            st.session_state.sf_usage_metadata = None
            st.session_state.sf_file_id = None

            if results:
                st.success(f"Found {len(results)} file(s)")
            else:
                st.warning("No files found matching your filters.")
        except Exception as e:
            st.error(f"BigQuery query failed: {e}")
            with st.expander("Technical Details"):
                st.exception(e)
            st.info(
                "Possible causes:\n"
                "- GOOGLE_CLOUD_PROJECT is incorrect\n"
                "- Application Default Credentials not configured\n"
                "- Run `gcloud auth application-default login` to authenticate"
            )

# =====================================================================
# STEP 2: Select File
# =====================================================================
if st.session_state.sf_search_results:
    results = st.session_state.sf_search_results

    st.markdown("---")
    st.subheader("📋 Step 2: Select File")

    # Display results table
    df = pd.DataFrame(results)
    st.dataframe(
        df[["province_name", "path", "size_kb", "file_id"]],
        use_container_width=True,
        hide_index=True,
    )

    # File selector
    selected_idx = st.selectbox(
        "Choose a file to extract",
        range(len(results)),
        index=st.session_state.sf_selected_idx,
        format_func=lambda i: (
            f"{results[i]['province_name']} | "
            f"{results[i]['path']} "
            f"({results[i]['size_kb']:.1f} KB)"
        ),
        key="sf_file_selector",
    )
    st.session_state.sf_selected_idx = selected_idx
    selected_file = results[selected_idx]

    # Show selected file info
    with st.expander("📄 Selected File Details", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Province", selected_file["province_name"])
        with col2:
            st.metric("Size", f"{selected_file['size_kb']:.1f} KB")
        with col3:
            st.metric("File ID", selected_file["file_id"][:16] + "...")
        st.text(f"Full path: {selected_file['path']}")
        st.text(f"Full file ID: {selected_file['file_id']}")

    # Extract button
    extract_button = st.button(
        "🚀 Extract Data",
        type="primary",
        use_container_width=True,
    )

    if extract_button:
        with st.spinner(f"Extracting with {model_name}..."):
            try:
                result, usage = extract_from_drive(
                    api_key=GEMINI_API_KEY,
                    file_id=selected_file["file_id"],
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                st.session_state.sf_extraction_result = result
                st.session_state.sf_usage_metadata = usage
                st.session_state.sf_file_id = selected_file["file_id"]
                st.success(f"Extracted {len(result)} report(s)")
            except Exception as e:
                st.error(f"Extraction failed: {e}")
                error_msg = str(e)
                if "403" in error_msg or "permission" in error_msg.lower():
                    st.info(
                        "The PDF file may not be publicly shared on Google Drive. "
                        "Ensure the file has 'Anyone with the link' access."
                    )
                elif "429" in error_msg or "quota" in error_msg.lower():
                    st.info("API rate limit exceeded. Please wait and try again.")
                with st.expander("Technical Details"):
                    st.exception(e)

# =====================================================================
# STEP 3: Results (side-by-side)
# =====================================================================
if st.session_state.sf_extraction_result is not None:
    result = st.session_state.sf_extraction_result
    usage = st.session_state.sf_usage_metadata
    file_id = st.session_state.sf_file_id

    # Find the selected file info
    selected_file = None
    if st.session_state.sf_search_results:
        for f in st.session_state.sf_search_results:
            if f["file_id"] == file_id:
                selected_file = f
                break

    st.markdown("---")
    st.subheader("📊 Step 3: Results")

    # Side-by-side layout
    col_pdf, col_results = st.columns([1, 1])

    with col_pdf:
        st.markdown("#### 📄 PDF Preview")
        preview_url = build_drive_preview_url(file_id)
        components.iframe(preview_url, height=700, scrolling=True)

    with col_results:
        st.markdown("#### 📊 Extraction Results")

        if not result:
            st.warning("No data extracted from this file.")
        else:
            # Report selector (if multiple reports)
            if len(result) > 1:
                report_idx = st.selectbox(
                    "Select Report",
                    range(len(result)),
                    format_func=lambda i: (
                        f"Report #{i + 1} - "
                        f"{result[i].get('form_info', {}).get('district', 'Unknown')}"
                    ),
                    key="sf_report_selector",
                )
            else:
                report_idx = 0

            data = result[report_idx]

            # Tabs for result display
            tab_summary, tab_votes, tab_validation, tab_usage, tab_json = st.tabs(
                ["📋 Summary", "📊 Votes", "✅ Validation", "📈 Usage", "🔍 JSON"]
            )

            # --- Summary Tab ---
            with tab_summary:
                form_info = data.get("form_info", {})
                st.markdown("**Form Information**")

                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Form Type", form_info.get("form_type", "N/A"))
                    st.metric("Province", form_info.get("province", "N/A"))
                    st.metric("District", form_info.get("district", "N/A"))
                    if form_info.get("sub_district"):
                        st.metric("Sub-district", form_info["sub_district"])

                with c2:
                    st.metric("Station", form_info.get("polling_station_number", "N/A"))
                    if form_info.get("constituency_number"):
                        st.metric("Constituency", form_info["constituency_number"])
                    if form_info.get("village_moo"):
                        st.metric("Village (หมู่)", form_info["village_moo"])
                    if form_info.get("date"):
                        st.metric("Date", form_info["date"])

                # Voter statistics
                voter_stats = data.get("voter_statistics")
                if voter_stats:
                    st.markdown("**Voter Statistics**")
                    vc1, vc2 = st.columns(2)
                    eligible = voter_stats.get("eligible_voters")
                    present = voter_stats.get("present_voters")
                    with vc1:
                        if eligible:
                            val = get_number_value(eligible)
                            thai = get_thai_text(eligible)
                            label = f"{val:,}" + (f" ({thai})" if thai else "")
                            st.metric("Eligible Voters", label)
                    with vc2:
                        if present:
                            val = get_number_value(present)
                            thai = get_thai_text(present)
                            label = f"{val:,}" + (f" ({thai})" if thai else "")
                            st.metric("Present Voters", label)

                # Ballot statistics
                ballot_stats = data.get("ballot_statistics")
                if ballot_stats:
                    st.markdown("**Ballot Statistics**")
                    bc1, bc2, bc3, bc4 = st.columns(4)
                    with bc1:
                        used = get_number_value(ballot_stats.get("ballots_used"))
                        st.metric("Ballots Used", f"{used:,}")
                    with bc2:
                        good = get_number_value(ballot_stats.get("good_ballots"))
                        st.metric("Valid Ballots", f"{good:,}")
                    with bc3:
                        bad = get_number_value(ballot_stats.get("bad_ballots"))
                        st.metric("Invalid Ballots", f"{bad:,}")
                    with bc4:
                        no_vote = get_number_value(ballot_stats.get("no_vote_ballots"))
                        st.metric("No Vote", f"{no_vote:,}")

                    # Quick ballot validation
                    if used > 0:
                        expected = good + bad + no_vote
                        if used == expected:
                            st.success(
                                f"Ballot validation passed ({used:,} = {good:,} + {bad:,} + {no_vote:,})"
                            )
                        else:
                            st.error(
                                f"Ballot mismatch: Used ({used:,}) != "
                                f"Good + Bad + NoVote ({expected:,})"
                            )

                # Officials
                officials = data.get("officials")
                if officials:
                    st.markdown(f"**Committee Members ({len(officials)})**")
                    for off in officials[:10]:
                        st.text(f"  {off.get('name', 'N/A')} - {off.get('position', 'N/A')}")

            # --- Vote Results Tab ---
            with tab_votes:
                form_type = data.get("form_info", {}).get("form_type", "")
                vote_results = data.get("vote_results", [])

                if not vote_results:
                    st.info("No vote results found")
                else:
                    st.markdown(f"**{len(vote_results)} entries ({form_type})**")

                    display_data = []
                    for v in vote_results:
                        vc_obj = v.get("vote_count")
                        row = {
                            "#": v.get("number"),
                            "Votes": get_number_value(vc_obj),
                            "Votes (Thai)": get_thai_text(vc_obj),
                        }
                        if form_type == "Constituency":
                            row["Candidate"] = v.get("candidate_name") or "-"
                        row["Party"] = v.get("party_name") or "-"
                        display_data.append(row)

                    df_votes = pd.DataFrame(display_data)
                    st.dataframe(df_votes, use_container_width=True, hide_index=True)

                    # Totals
                    total_calc = df_votes["Votes"].sum()
                    st.metric("Calculated Total", f"{total_calc:,}")

                    total_rec = data.get("total_votes_recorded")
                    if total_rec:
                        rec_val = get_number_value(total_rec)
                        rec_thai = get_thai_text(total_rec)
                        label = f"{rec_val:,}" + (f" ({rec_thai})" if rec_thai else "")
                        st.metric("Recorded Total", label)
                        if total_calc == rec_val:
                            st.success("Total validation passed")
                        else:
                            st.error(
                                f"Total mismatch: calculated {total_calc:,} != recorded {rec_val:,}"
                            )

                    # CSV download
                    csv = df_votes.to_csv(index=False, encoding="utf-8-sig")
                    st.download_button(
                        "📥 Download Votes CSV",
                        data=csv,
                        file_name=f"votes_{file_id[:8]}.csv",
                        mime="text/csv",
                    )

            # --- Validation Tab ---
            with tab_validation:
                is_valid, val_errors, val_warnings = validate_extraction(data)

                if is_valid and not val_warnings:
                    st.success("All validation checks passed!")
                elif is_valid:
                    st.success(f"No errors, but {len(val_warnings)} warning(s)")
                else:
                    st.error(f"{len(val_errors)} validation error(s)")

                if val_errors:
                    for err in val_errors:
                        st.error(f"  {err}")
                if val_warnings:
                    for warn in val_warnings:
                        st.warning(f"  {warn}")

                # Pydantic model validation
                st.markdown("**Pydantic Model Validation**")
                try:
                    ElectionFormData(**data)
                    st.success("Pydantic validation passed")
                except Exception as e:
                    st.error(f"Pydantic validation failed: {e}")

            # --- Usage Metadata Tab ---
            with tab_usage:
                if usage:
                    st.markdown("**Token Usage**")
                    uc1, uc2, uc3 = st.columns(3)
                    with uc1:
                        st.metric(
                            "Input Tokens",
                            f"{usage.get('prompt_token_count', 0):,}",
                        )
                    with uc2:
                        st.metric(
                            "Output Tokens",
                            f"{usage.get('candidates_token_count', 0):,}",
                        )
                    with uc3:
                        st.metric(
                            "Total Tokens",
                            f"{usage.get('total_token_count', 0):,}",
                        )

                    if usage.get("cached_content_token_count", 0) > 0:
                        st.metric(
                            "Cached Tokens",
                            f"{usage['cached_content_token_count']:,}",
                        )
                    if usage.get("thoughts_token_count", 0) > 0:
                        st.metric(
                            "Thoughts Tokens",
                            f"{usage['thoughts_token_count']:,}",
                        )

                    st.markdown("**Model Configuration**")
                    st.json(usage.get("generation_config", {}))
                    st.text(f"Model: {usage.get('model', 'N/A')}")
                else:
                    st.info("No usage metadata available")

            # --- Raw JSON Tab ---
            with tab_json:
                st.json(data)

        # --- Download full result ---
        st.markdown("---")
        st.markdown("#### 💾 Save Result")

        output_data = {
            "source_file": selected_file if selected_file else {"file_id": file_id},
            "extraction_metadata": {
                "model": usage.get("model") if usage else model_name,
                "timestamp": datetime.now().isoformat(),
                "reports_extracted": len(result),
            },
            "usage_metadata": usage,
            "extracted_data": result,
        }

        json_str = json.dumps(output_data, indent=2, ensure_ascii=False)

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                "📥 Download Full Result (JSON)",
                data=json_str,
                file_name=f"extracted_{file_id}.json",
                mime="application/json",
                use_container_width=True,
            )
        with col_dl2:
            # Download just the extracted data (for dataset use)
            data_only = json.dumps(result, indent=2, ensure_ascii=False)
            st.download_button(
                "📥 Download Data Only (JSON)",
                data=data_only,
                file_name=f"data_{file_id}.json",
                mime="application/json",
                use_container_width=True,
            )

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px;'>
        SS5/18 Single File Extractor | BigQuery + Google Drive + Gemini
    </div>
    """,
    unsafe_allow_html=True,
)
