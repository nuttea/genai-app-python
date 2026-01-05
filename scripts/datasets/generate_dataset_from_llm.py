#!/usr/bin/env python3
"""
Generate a local dataset by extracting vote data from images using the LLM API.

This script:
1. Discovers images for specified form sets
2. Calls the vote extraction API for each form set
3. Saves the extracted data as ground truth in a dataset JSON file
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import httpx
from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Configuration
IMAGES_DIR = PROJECT_ROOT / "assets" / "ss5-18-images"
DATASET_DIR = PROJECT_ROOT / "datasets" / "vote-extraction"
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def discover_images(form_pattern: str = None) -> Dict[str, List[Path]]:
    """
    Discover and group images by form set.
    
    Args:
        form_pattern: Filter form sets by pattern (e.g., "บางบำหรุ")
        
    Returns:
        Dictionary mapping form set names to lists of image paths
    """
    if not IMAGES_DIR.exists():
        logger.error(f"Images directory not found: {IMAGES_DIR}")
        return {}

    form_sets = {}
    
    for img_path in sorted(IMAGES_DIR.glob("*.jpg")):
        # Extract form set name (everything before _page)
        name = img_path.stem.split("_page")[0]
        
        # Filter by pattern if provided
        if form_pattern and form_pattern not in name:
            continue
            
        if name not in form_sets:
            form_sets[name] = []
        form_sets[name].append(img_path)
    
    # Sort images within each form set
    for name in form_sets:
        form_sets[name].sort()
    
    return form_sets


async def extract_from_api(
    image_paths: List[Path],
    timeout: float = 120.0,
) -> Dict[str, Any] | None:
    """
    Call the vote extraction API to extract data from images.
    
    Args:
        image_paths: List of image file paths
        timeout: Request timeout in seconds
        
    Returns:
        Extracted data or None if failed
    """
    url = f"{API_BASE_URL}/api/v1/vote-extraction/extract"
    headers = {}
    
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    
    # Prepare files for upload
    files = []
    for img_path in image_paths:
        files.append(
            ("files", (img_path.name, open(img_path, "rb"), "image/jpeg"))
        )
    
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            logger.info(f"Calling API: {url} with {len(files)} images")
            response = await client.post(url, files=files, headers=headers)
            
            # Close file handles
            for _, (_, f, _) in files:
                f.close()
            
            if response.status_code != 200:
                logger.error(
                    f"API error {response.status_code}: {response.text}"
                )
                return None
            
            result = response.json()
            logger.info(f"✅ Extraction successful: {result.get('reports_extracted', 0)} reports")
            return result
            
    except Exception as e:
        logger.error(f"Failed to call API: {e}")
        # Close file handles on error
        for _, (_, f, _) in files:
            try:
                f.close()
            except:
                pass
        return None


def convert_to_ground_truth(extraction_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert extraction API result to ground truth format.
    
    Args:
        extraction_result: Result from the vote extraction API
        
    Returns:
        Ground truth data in the dataset format
    """
    # The API returns a structure like:
    # {
    #   "success": true,
    #   "data": [...],  # List of ElectionFormData
    #   "pages_processed": 6,
    #   "reports_extracted": 1
    # }
    
    if not extraction_result.get("success"):
        return None
    
    data_list = extraction_result.get("data", [])
    
    if not data_list:
        return None
    
    # For now, take the first report (most forms have 1 report per set)
    # If there are multiple, we might need to handle this differently
    data = data_list[0]
    
    # Convert to ground truth format
    ground_truth = {
        "form_info": data.get("form_info", {}),
        "voter_statistics": data.get("voter_statistics", {}),
        "ballot_statistics": data.get("ballot_statistics", {}),
        "vote_results": data.get("vote_results", []),
        "notes": "Auto-generated from LLM extraction. Please review and correct.",
    }
    
    return ground_truth


async def generate_dataset(
    form_names: List[str],
    dataset_name: str = "vote-extraction-llm-generated",
    version: str = "v1",
) -> Dict[str, Any]:
    """
    Generate a dataset by extracting data from specified form sets.
    
    Args:
        form_names: List of form set names to process
        dataset_name: Name of the dataset
        version: Dataset version
        
    Returns:
        Complete dataset structure
    """
    logger.info(f"🚀 Starting dataset generation for {len(form_names)} form sets")
    
    # Discover all images
    all_form_sets = discover_images()
    logger.info(f"📸 Discovered {len(all_form_sets)} form sets")
    
    # Filter to requested forms
    form_sets_to_process = {
        name: paths for name, paths in all_form_sets.items()
        if name in form_names
    }
    
    if not form_sets_to_process:
        logger.error(f"❌ No images found for requested form sets")
        return None
    
    logger.info(f"📝 Processing {len(form_sets_to_process)} form sets: {list(form_sets_to_process.keys())}")
    
    # Initialize dataset
    dataset = {
        "metadata": {
            "name": dataset_name,
            "version": version,
            "description": f"Auto-generated from LLM extraction on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "created_at": datetime.now().isoformat(),
            "num_records": 0,
            "total_pages": 0,
            "generation_method": "llm_api",
            "api_base_url": API_BASE_URL,
        },
        "records": [],
    }
    
    # Process each form set
    success_count = 0
    fail_count = 0
    
    for idx, (form_name, image_paths) in enumerate(form_sets_to_process.items(), 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing [{idx}/{len(form_sets_to_process)}]: {form_name}")
        logger.info(f"Images: {len(image_paths)} pages")
        logger.info(f"{'='*60}")
        
        # Extract data from API
        extraction_result = await extract_from_api(image_paths)
        
        if not extraction_result:
            logger.warning(f"⚠️ Failed to extract data for {form_name}")
            fail_count += 1
            continue
        
        # Convert to ground truth
        ground_truth = convert_to_ground_truth(extraction_result)
        
        if not ground_truth:
            logger.warning(f"⚠️ Failed to convert extraction result for {form_name}")
            fail_count += 1
            continue
        
        # Create record
        record = {
            "id": form_name,
            "input": {
                "form_set_name": form_name,
                "image_paths": [str(p) for p in image_paths],
                "num_pages": len(image_paths),
            },
            "ground_truth": ground_truth,
            "pages_processed": len(image_paths),
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "extraction_metadata": {
                "api_response": extraction_result,
                "needs_review": True,
            },
        }
        
        dataset["records"].append(record)
        dataset["metadata"]["num_records"] = len(dataset["records"])
        dataset["metadata"]["total_pages"] += len(image_paths)
        
        success_count += 1
        logger.info(f"✅ Successfully processed {form_name}")
        
        # Small delay between requests to avoid overwhelming the API
        await asyncio.sleep(1)
    
    # Final summary
    logger.info(f"\n{'='*60}")
    logger.info(f"📊 Generation Complete")
    logger.info(f"{'='*60}")
    logger.info(f"✅ Success: {success_count}/{len(form_sets_to_process)}")
    logger.info(f"❌ Failed: {fail_count}/{len(form_sets_to_process)}")
    logger.info(f"📄 Total records: {dataset['metadata']['num_records']}")
    logger.info(f"📸 Total pages: {dataset['metadata']['total_pages']}")
    
    return dataset


def save_dataset(dataset: Dict[str, Any], output_filename: str = None) -> Path:
    """
    Save dataset to JSON file.
    
    Args:
        dataset: Dataset structure
        output_filename: Optional custom filename
        
    Returns:
        Path to saved file
    """
    # Ensure dataset directory exists
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    if not output_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"{dataset['metadata']['name']}_{timestamp}.json"
    
    output_path = DATASET_DIR / output_filename
    
    # Save to file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    logger.info(f"\n💾 Dataset saved to: {output_path}")
    logger.info(f"📁 File size: {output_path.stat().st_size / 1024:.1f} KB")
    
    return output_path


async def main():
    """Main entry point."""
    logger.info("🎯 Dataset Generation from LLM API")
    logger.info(f"API Base URL: {API_BASE_URL}")
    logger.info(f"Images Directory: {IMAGES_DIR}")
    logger.info(f"Dataset Directory: {DATASET_DIR}")
    
    # Define form sets to process
    form_names = [
        "บางบำหรุ1",
        "บางบำหรุ2",
        "บางบำหรุ3",
        "บางบำหรุ4",
        "บางบำหรุ5",
        "บางบำหรุ6",
        "บางบำหรุ7",
        "บางบำหรุ8",
        "บางบำหรุ9",
        "บางบำหรุ10",
    ]
    
    logger.info(f"\n📋 Target forms: {', '.join(form_names)}")
    
    # Generate dataset
    dataset = await generate_dataset(
        form_names=form_names,
        dataset_name="vote-extraction-bangbamru-1-10",
        version="v1-llm-generated",
    )
    
    if not dataset:
        logger.error("❌ Failed to generate dataset")
        return 1
    
    # Save dataset
    output_path = save_dataset(dataset)
    
    logger.info(f"\n{'='*60}")
    logger.info("✅ Dataset generation complete!")
    logger.info(f"{'='*60}")
    logger.info(f"\n📖 Next steps:")
    logger.info(f"1. Open the Dataset Manager in Streamlit")
    logger.info(f"2. Load the dataset: {output_path.name}")
    logger.info(f"3. Review and correct the auto-generated ground truth")
    logger.info(f"4. Push to Datadog when ready")
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

