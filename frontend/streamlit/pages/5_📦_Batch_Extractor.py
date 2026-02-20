"""Batch Extractor - Process multiple SS5/18 PDFs from BigQuery.

Filter by province and constituency path, then batch-extract with Gemini.
"""

import json
import os
import sys
import time
from datetime import datetime

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.bigquery_client import query_pdf_files
from utils.config import get_config
from utils.datadog_rum import init_datadog_rum
from utils.gemini_extractor import MODEL_OPTIONS, extract_from_drive
from utils.models import get_number_value, validate_extraction

# Configuration
GEMINI_API_KEY = get_config("GEMINI_API_KEY")
GOOGLE_CLOUD_PROJECT = get_config("GOOGLE_CLOUD_PROJECT")

st.set_page_config(
    page_title="Batch Extractor",
    page_icon="📦",
    layout="wide",
)

rum_enabled = init_datadog_rum()

# Session state initialization
for key, default in {
    "batch_search_results": None,
    "batch_results": None,
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

# --- Sidebar: Model Configuration ---
with st.sidebar:
    st.header("⚙️ Model Configuration")

    model_name = st.selectbox(
        "Gemini Model",
        options=MODEL_OPTIONS,
        index=0,
        help="Select the Gemini model for extraction",
        key="batch_model",
    )

    with st.expander("🔧 Advanced Parameters"):
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1,
            help="Lower = more deterministic",
            key="batch_temp",
        )
        max_tokens = st.number_input(
            "Max Tokens",
            min_value=1024,
            max_value=65536,
            value=8192,
            step=512,
            key="batch_max_tokens",
        )
        delay_seconds = st.slider(
            "Delay between requests (seconds)",
            min_value=0.0,
            max_value=5.0,
            value=0.5,
            step=0.5,
            help="Delay between API calls to avoid rate limiting",
            key="batch_delay",
        )

    # Show batch stats in sidebar when results exist
    if st.session_state.batch_results:
        results = st.session_state.batch_results
        successful = sum(1 for r in results if r.get("success"))
        failed = len(results) - successful
        total_tokens = sum(
            r.get("usage_metadata", {}).get("total_token_count", 0)
            for r in results
            if r.get("success")
        )

        st.markdown("---")
        st.header("📊 Batch Stats")
        st.metric("Total Files", len(results))
        st.metric("Successful", successful)
        st.metric("Failed", failed)
        st.metric("Total Tokens", f"{total_tokens:,}")

# --- Page Header ---
st.title("📦 Batch Extractor")
st.markdown(
    "Process multiple SS5/18 PDFs from BigQuery in batch. "
    "Filter by province and constituency path."
)

with st.expander("📖 How to use", expanded=False):
    st.markdown(
        """
        ### Instructions:

        1. **Filter files**: Enter province name and/or constituency path
        2. **Review**: Check the file list before starting
        3. **Start batch**: Click "Start Batch Extraction"
        4. **Monitor**: Watch the progress bar as files are processed
        5. **Download**: Save results as JSON or CSV

        ### Filter Examples:

        **Province (จังหวัด):**
        - `พิจิตร` - Phichit province
        - `แพร่` - Phrae province
        - `กรุงเทพมหานคร` - Bangkok

        **Path (เขตเลือกตั้ง):**
        - `เขตเลือกตั้งที่ 1` - Constituency 1
        - `เขตเลือกตั้งที่ 3/อำเภอโพธิ์ประทับช้าง` - Constituency 3, specific district
        - `นอกเขต` - Out-of-area votes

        **Path structure:** `เขตเลือกตั้งที่ X/อำเภอYYY/ตำบลZZZ/หน่วยเลือกตั้งที่ N/สส5ทับ18.pdf`
        """
    )

st.markdown("---")

# =====================================================================
# STEP 1: Filter Files
# =====================================================================
st.subheader("🔍 Step 1: Filter Files")

col1, col2 = st.columns(2)

with col1:
    province_filter = st.text_input(
        "จังหวัด (Province)",
        value="",
        placeholder="เช่น พิจิตร, แพร่",
        help=(
            "Filter by exact province name. Examples: "
            "พิจิตร, แพร่, กรุงเทพมหานคร, เชียงใหม่, นครราชสีมา"
        ),
        key="batch_province",
    )

with col2:
    path_filter = st.text_input(
        "เขตเลือกตั้ง (Constituency in path)",
        value="",
        placeholder="เช่น เขตเลือกตั้งที่ 1",
        help=(
            "Filter files whose path contains this text. Examples:\n"
            "- เขตเลือกตั้งที่ 1\n"
            "- เขตเลือกตั้งที่ 3/อำเภอโพธิ์ประทับช้าง\n"
            "- นอกเขต"
        ),
        key="batch_path",
    )

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    min_size_kb = st.number_input(
        "Min size (KB)", value=50.0, min_value=0.0, step=10.0, key="batch_min_size"
    )
with col_s2:
    max_size_mb = st.number_input(
        "Max size (MB)", value=50.0, min_value=0.1, step=5.0, key="batch_max_size"
    )
with col_s3:
    limit = st.number_input(
        "Max files",
        value=20,
        min_value=1,
        max_value=200,
        step=5,
        key="batch_limit",
        help="Maximum number of files to process",
    )

search_button = st.button(
    "🔍 Search Files", type="primary", use_container_width=True, key="batch_search_btn"
)

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
            st.session_state.batch_search_results = results
            st.session_state.batch_results = None  # Clear previous batch results

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
# STEP 2: Review & Start Batch
# =====================================================================
if st.session_state.batch_search_results:
    files = st.session_state.batch_search_results

    st.markdown("---")
    st.subheader(f"📋 Step 2: Review Files ({len(files)} files)")

    # Summary
    if files:
        provinces = set(f["province_name"] for f in files)
        total_size_mb = sum(f["size_mb"] for f in files)
        st.info(
            f"**{len(files)}** files from **{len(provinces)}** province(s) | "
            f"Total size: **{total_size_mb:.1f} MB**"
        )

    # Display file table
    df = pd.DataFrame(files)
    st.dataframe(
        df[["province_name", "path", "size_kb", "file_id"]],
        use_container_width=True,
        hide_index=True,
    )

    # Start batch button
    start_batch = st.button(
        f"🚀 Start Batch Extraction ({len(files)} files)",
        type="primary",
        use_container_width=True,
        key="start_batch_btn",
    )

    # =====================================================================
    # STEP 3: Processing
    # =====================================================================
    if start_batch:
        st.markdown("---")
        st.subheader("⏳ Step 3: Processing")

        total = len(files)
        progress_bar = st.progress(0, text="Starting batch extraction...")
        status_container = st.empty()

        all_results = []
        successful = 0
        failed = 0
        total_tokens = 0

        for i, file_info in enumerate(files):
            filename = (
                file_info["path"].split("/")[-1] if "/" in file_info["path"] else file_info["path"]
            )
            progress_bar.progress(
                (i + 1) / total,
                text=f"Processing {i + 1}/{total}: {filename}",
            )

            try:
                result, usage = extract_from_drive(
                    api_key=GEMINI_API_KEY,
                    file_id=file_info["file_id"],
                    model=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

                # Validate each report
                validations = []
                for report in result:
                    is_valid, errors, warnings = validate_extraction(report)
                    validations.append(
                        {
                            "is_valid": is_valid,
                            "errors": errors,
                            "warnings": warnings,
                        }
                    )

                all_results.append(
                    {
                        "file_info": file_info,
                        "success": True,
                        "data": result,
                        "validations": validations,
                        "usage_metadata": usage,
                        "reports_count": len(result),
                    }
                )
                successful += 1
                total_tokens += usage.get("total_token_count", 0)

            except Exception as e:
                all_results.append(
                    {
                        "file_info": file_info,
                        "success": False,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }
                )
                failed += 1

            # Update running status
            status_container.markdown(
                f"**Progress:** {i + 1}/{total} | "
                f"**Success:** {successful} | **Failed:** {failed} | "
                f"**Tokens:** {total_tokens:,}"
            )

            # Delay between requests
            if delay_seconds > 0 and i < total - 1:
                time.sleep(delay_seconds)

        progress_bar.progress(1.0, text="Batch extraction complete!")
        st.session_state.batch_results = all_results
        st.rerun()

# =====================================================================
# STEP 4: Results
# =====================================================================
if st.session_state.batch_results:
    results = st.session_state.batch_results

    st.markdown("---")
    st.subheader("📊 Results")

    # Summary metrics
    successful = sum(1 for r in results if r.get("success"))
    failed = len(results) - successful
    total_reports = sum(r.get("reports_count", 0) for r in results if r.get("success"))
    total_tokens = sum(
        r.get("usage_metadata", {}).get("total_token_count", 0) for r in results if r.get("success")
    )
    total_input = sum(
        r.get("usage_metadata", {}).get("prompt_token_count", 0)
        for r in results
        if r.get("success")
    )
    total_output = sum(
        r.get("usage_metadata", {}).get("candidates_token_count", 0)
        for r in results
        if r.get("success")
    )

    # Validation stats
    all_validations = [v for r in results if r.get("success") for v in r.get("validations", [])]
    valid_count = sum(1 for v in all_validations if v.get("is_valid"))
    invalid_count = len(all_validations) - valid_count

    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    with mc1:
        st.metric("Total Files", len(results))
    with mc2:
        st.metric("Successful", successful)
    with mc3:
        st.metric("Failed", failed)
    with mc4:
        st.metric("Reports Extracted", total_reports)
    with mc5:
        st.metric(
            "Valid Reports",
            f"{valid_count}/{valid_count + invalid_count}" if all_validations else "N/A",
        )

    # Token usage summary
    if total_tokens > 0:
        st.markdown("**Token Usage**")
        tc1, tc2, tc3 = st.columns(3)
        with tc1:
            st.metric("Input Tokens", f"{total_input:,}")
        with tc2:
            st.metric("Output Tokens", f"{total_output:,}")
        with tc3:
            st.metric("Total Tokens", f"{total_tokens:,}")

    # Results table
    st.markdown("**Per-File Results**")
    summary_data = []
    for r in results:
        fi = r.get("file_info", {})
        filename = fi.get("path", "Unknown")
        if "/" in filename:
            filename = filename.split("/")[-1]

        row = {
            "File": filename,
            "Province": fi.get("province_name", "N/A"),
            "Size (KB)": fi.get("size_kb", 0),
            "Status": "Success" if r.get("success") else "Failed",
            "Reports": r.get("reports_count", 0),
        }

        if r.get("success"):
            vals = r.get("validations", [])
            valid = sum(1 for v in vals if v.get("is_valid"))
            row["Valid"] = f"{valid}/{len(vals)}" if vals else "N/A"
            row["Tokens"] = r.get("usage_metadata", {}).get("total_token_count", 0)
        else:
            row["Valid"] = "-"
            row["Tokens"] = 0
            row["Error"] = r.get("error", "")[:50]

        summary_data.append(row)

    df_summary = pd.DataFrame(summary_data)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

    # Expandable details per file
    st.markdown("**Detailed Results**")
    for i, r in enumerate(results):
        fi = r.get("file_info", {})
        filename = (
            fi.get("path", "Unknown").split("/")[-1]
            if "/" in fi.get("path", "")
            else fi.get("path", "Unknown")
        )
        status = "Success" if r.get("success") else "Failed"

        with st.expander(f"#{i + 1} {filename} [{status}]", expanded=False):
            if r.get("success"):
                # Show extraction summary
                for j, report in enumerate(r.get("data", [])):
                    form_info = report.get("form_info", {})
                    votes = report.get("vote_results", [])
                    total = sum(get_number_value(v.get("vote_count")) for v in votes)

                    st.markdown(
                        f"**Report {j + 1}:** "
                        f"{form_info.get('form_type', 'N/A')} | "
                        f"{form_info.get('district', 'N/A')} | "
                        f"Station {form_info.get('polling_station_number', 'N/A')} | "
                        f"{len(votes)} entries | Total: {total:,}"
                    )

                # Validation
                for j, v in enumerate(r.get("validations", [])):
                    if v.get("is_valid"):
                        st.success(f"Report {j + 1}: Validation passed")
                    else:
                        for err in v.get("errors", []):
                            st.error(f"Report {j + 1}: {err}")
                    for warn in v.get("warnings", []):
                        st.warning(f"Report {j + 1}: {warn}")

                # Raw JSON
                st.json(r.get("data", []))
            else:
                st.error(f"Error: {r.get('error', 'Unknown')}")
                st.text(f"Error type: {r.get('error_type', 'N/A')}")

    # --- Downloads ---
    st.markdown("---")
    st.markdown("#### 💾 Download Results")

    # Build output data
    output_data = {
        "metadata": {
            "model": model_name,
            "timestamp": datetime.now().isoformat(),
            "total_files": len(results),
            "successful": successful,
            "failed": failed,
            "total_reports": total_reports,
            "filters": {
                "province": province_filter.strip() or None,
                "path_contains": path_filter.strip() or None,
            },
        },
        "usage_summary": {
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_tokens,
        },
        "results": results,
    }

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        json_str = json.dumps(output_data, indent=2, ensure_ascii=False)
        st.download_button(
            "📥 Download All Results (JSON)",
            data=json_str,
            file_name=f"batch_results_{len(results)}files.json",
            mime="application/json",
            use_container_width=True,
        )

    with col_dl2:
        csv_data = df_summary.to_csv(index=False, encoding="utf-8-sig")
        st.download_button(
            "📥 Download Summary (CSV)",
            data=csv_data,
            file_name=f"batch_summary_{len(results)}files.csv",
            mime="text/csv",
            use_container_width=True,
        )

    # Clear results button
    if st.button("🗑️ Clear Results", key="clear_batch"):
        st.session_state.batch_results = None
        st.session_state.batch_search_results = None
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 12px;'>
        SS5/18 Batch Extractor | BigQuery + Google Drive + Gemini
    </div>
    """,
    unsafe_allow_html=True,
)
