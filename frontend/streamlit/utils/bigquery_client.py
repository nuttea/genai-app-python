"""BigQuery client for querying SS5/18 PDF file metadata."""

import streamlit as st
from google.cloud import bigquery

# Default BigQuery table
BQ_TABLE = "sourceinth.vote69_ect.raw_files"


@st.cache_resource
def get_bq_client(project_id: str) -> bigquery.Client:
    """Get cached BigQuery client instance."""
    return bigquery.Client(project=project_id)


def query_pdf_files(
    project_id: str,
    limit: int = 100,
    province: str | None = None,
    path_contains: str | None = None,
    min_size_kb: float = 50.0,
    max_size_mb: float = 50.0,
) -> list[dict]:
    """
    Query BigQuery for PDF files from the raw_files table.

    Args:
        project_id: GCP project ID
        limit: Maximum number of files to return
        province: Filter by province_name (exact match)
        path_contains: Filter by substring in path (e.g. "เขตเลือกตั้งที่ 1")
        min_size_kb: Minimum file size in KB
        max_size_mb: Maximum file size in MB

    Returns:
        List of file metadata dicts
    """
    client = get_bq_client(project_id)

    conditions = ["mime_type = 'application/pdf'"]
    query_params = []

    min_bytes = int(min_size_kb * 1024)
    conditions.append(f"size >= {min_bytes}")

    if max_size_mb:
        max_bytes = int(max_size_mb * 1024 * 1024)
        conditions.append(f"size <= {max_bytes}")

    if province:
        conditions.append("province_name = @province")
        query_params.append(bigquery.ScalarQueryParameter("province", "STRING", province))

    if path_contains:
        conditions.append("path LIKE @path_pattern")
        query_params.append(
            bigquery.ScalarQueryParameter("path_pattern", "STRING", f"%{path_contains}%")
        )

    where_clause = " AND ".join(conditions)

    query = f"""
    SELECT file_id, path, mime_type, folder_id, province_name, size, mod_time
    FROM `{BQ_TABLE}`
    WHERE {where_clause}
    ORDER BY path ASC
    LIMIT {limit}
    """

    job_config = bigquery.QueryJobConfig(query_parameters=query_params)
    query_job = client.query(query, job_config=job_config)
    results = query_job.result()

    files = []
    for row in results:
        files.append(
            {
                "file_id": row.file_id,
                "path": row.path,
                "mime_type": row.mime_type,
                "folder_id": row.folder_id,
                "province_name": row.province_name,
                "size": row.size,
                "size_mb": round(row.size / (1024 * 1024), 3) if row.size else 0,
                "size_kb": round(row.size / 1024, 1) if row.size else 0,
                "mod_time": str(row.mod_time) if row.mod_time else None,
            }
        )

    return files


def get_distinct_provinces(project_id: str) -> list[str]:
    """Query distinct province names for filtering."""
    client = get_bq_client(project_id)
    query = f"""
    SELECT DISTINCT province_name
    FROM `{BQ_TABLE}`
    WHERE province_name IS NOT NULL
    ORDER BY province_name
    """
    results = client.query(query).result()
    return [row.province_name for row in results]
