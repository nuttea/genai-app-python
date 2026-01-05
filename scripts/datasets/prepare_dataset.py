#!/usr/bin/env python3
"""
Prepare Vote Extraction Dataset for Datadog LLM Experiments

This script creates a curated dataset from Thai election form images,
saves it locally as JSON, and optionally pushes it to Datadog.

Usage:
    python prepare_dataset.py --help
    python prepare_dataset.py --local-only
    python prepare_dataset.py --push-to-datadog
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from PIL import Image

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configuration
DATASET_NAME = "vote-extraction-thai-elections-v1"
DATASET_DESCRIPTION = "Thai election forms from Bangkok districts (6-page sets)"
PROJECT_NAME = "vote-extraction-project"

IMAGES_DIR = PROJECT_ROOT / "assets" / "ss5-18-images"
DATASET_OUTPUT_DIR = PROJECT_ROOT / "datasets" / "vote-extraction"
DATASET_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Ground truth data
# TODO: Replace with actual verified ground truth from manual review
GROUND_TRUTH = {
    "บางบำหรุ1": {
        "form_type": "ss5_18",
        "province": "Bangkok",
        "district": "Bang Phlat",
        "polling_station": "1",
        "ballot_statistics": {
            "total_votes": 520,
            "valid_ballots": 495,
            "invalid_ballots": 25,
        },
        "vote_results": [
            {"candidate_number": 1, "candidate_name": "Candidate A", "votes": 245},
            {"candidate_number": 2, "candidate_name": "Candidate B", "votes": 250},
        ],
        "notes": "Example ground truth - verify with actual form data",
    },
    # Add more ground truth as you verify forms
}


class DatasetBuilder:
    """Build dataset from images and ground truth."""

    def __init__(self, images_dir: Path, ground_truth: Dict[str, Any]):
        self.images_dir = images_dir
        self.ground_truth = ground_truth
        self.image_files = self._discover_images()

    def _discover_images(self) -> List[Path]:
        """Discover all image files."""
        images = sorted(
            list(self.images_dir.glob("*.jpg")) + list(self.images_dir.glob("*.png"))
        )
        print(f"✅ Found {len(images)} images in {self.images_dir}")
        return images

    def _group_by_form_set(self) -> Dict[str, List[Path]]:
        """Group images by form set (6 pages per set)."""
        form_sets = {}

        for img_path in self.image_files:
            # Extract form set name
            form_name = (
                img_path.stem.rsplit("_page", 1)[0]
                if "_page" in img_path.stem
                else img_path.stem
            )

            if form_name not in form_sets:
                form_sets[form_name] = []
            form_sets[form_name].append(img_path)

        return form_sets

    def build_records(self) -> List[Dict[str, Any]]:
        """Build dataset records."""
        records = []
        form_sets = self._group_by_form_set()

        print(f"\n📊 Building dataset records...")
        print("=" * 80)

        for form_name, images in sorted(form_sets.items()):
            # Check if we have ground truth
            if form_name not in self.ground_truth:
                print(f"⚠️  Skipping {form_name} - no ground truth defined")
                continue

            ground_truth = self.ground_truth[form_name]

            # Sort images by page number
            sorted_images = sorted(images, key=lambda p: p.name)

            record = {
                "id": form_name,
                "input": {
                    "form_set_name": form_name,
                    "image_paths": [
                        str(img.relative_to(PROJECT_ROOT)) for img in sorted_images
                    ],
                    "num_pages": len(sorted_images),
                    "form_type": ground_truth.get("form_type", "ss5_18"),
                    "province": ground_truth.get("province"),
                    "district": ground_truth.get("district"),
                },
                "expected_output": {
                    "ballot_statistics": ground_truth["ballot_statistics"],
                    "vote_results": ground_truth["vote_results"],
                },
                "metadata": {
                    "polling_station": ground_truth.get("polling_station"),
                    "notes": ground_truth.get("notes"),
                    "verified_by": "manual_review",
                    "verification_date": datetime.now().isoformat(),
                },
            }

            records.append(record)
            print(f"✅ Created record for {form_name} ({len(sorted_images)} pages)")

        print("=" * 80)
        print(f"✅ Built {len(records)} dataset records\n")
        return records


class DatasetValidator:
    """Validate dataset quality."""

    @staticmethod
    def validate_record(record: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate a single record."""
        errors = []

        # Check required fields
        if "id" not in record:
            errors.append("Missing 'id' field")
        if "input" not in record:
            errors.append("Missing 'input' field")
        if "expected_output" not in record:
            errors.append("Missing 'expected_output' field")

        # Validate input
        input_data = record.get("input", {})
        if not input_data.get("image_paths"):
            errors.append("Missing or empty 'image_paths' in input")
        else:
            # Check if files exist
            for img_path in input_data["image_paths"]:
                full_path = PROJECT_ROOT / img_path
                if not full_path.exists():
                    errors.append(f"Image file not found: {img_path}")

        # Validate expected output
        expected = record.get("expected_output", {})

        # Check ballot statistics
        ballot_stats = expected.get("ballot_statistics", {})
        if not ballot_stats:
            errors.append("Missing 'ballot_statistics' in expected_output")
        else:
            required_fields = ["total_votes", "valid_ballots", "invalid_ballots"]
            for field in required_fields:
                if field not in ballot_stats:
                    errors.append(f"Missing '{field}' in ballot_statistics")
                elif not isinstance(ballot_stats.get(field), int):
                    errors.append(f"'{field}' must be an integer")

            # Validate ballot math
            total = ballot_stats.get("total_votes", 0)
            valid = ballot_stats.get("valid_ballots", 0)
            invalid = ballot_stats.get("invalid_ballots", 0)

            if valid + invalid != total:
                errors.append(
                    f"Ballot math error: valid({valid}) + invalid({invalid}) != total({total})"
                )

        # Check vote results
        vote_results = expected.get("vote_results", [])
        if not vote_results:
            errors.append("Missing or empty 'vote_results' in expected_output")

        return len(errors) == 0, errors

    def validate_all(self, records: List[Dict[str, Any]]) -> bool:
        """Validate all records."""
        print(f"\n🔍 Validating {len(records)} records...")
        print("=" * 80)

        all_valid = True
        for i, record in enumerate(records, 1):
            is_valid, errors = self.validate_record(record)

            if is_valid:
                print(f"✅ Record {i}/{len(records)}: {record['id']} - Valid")
            else:
                print(f"❌ Record {i}/{len(records)}: {record['id']} - Invalid")
                for error in errors:
                    print(f"   - {error}")
                all_valid = False

        print("=" * 80)
        if all_valid:
            print("✅ All records are valid!\n")
        else:
            print("❌ Some records have validation errors\n")

        return all_valid


class DatasetSaver:
    """Save dataset locally."""

    @staticmethod
    def save(
        records: List[Dict[str, Any]], version: str = "v1", output_dir: Path = DATASET_OUTPUT_DIR
    ) -> Path:
        """Save dataset to local JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{DATASET_NAME}_{version}_{timestamp}.json"
        filepath = output_dir / filename

        # Create dataset with metadata
        dataset = {
            "metadata": {
                "name": DATASET_NAME,
                "version": version,
                "description": DATASET_DESCRIPTION,
                "created_at": datetime.now().isoformat(),
                "num_records": len(records),
                "total_pages": sum(r["input"]["num_pages"] for r in records),
            },
            "records": records,
        }

        # Save to file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(dataset, f, indent=2, ensure_ascii=False)

        print(f"✅ Dataset saved to: {filepath}")
        print(f"   Size: {filepath.stat().st_size / 1024:.2f} KB")

        # Create "latest" symlink
        latest_link = output_dir / f"{DATASET_NAME}_latest.json"
        if latest_link.exists():
            latest_link.unlink()

        latest_link.symlink_to(filename)
        print(f"✅ Latest version link: {latest_link}\n")

        return filepath


class DatadogDatasetManager:
    """Manage Datadog LLM Observability datasets."""

    def __init__(self, api_key: str, app_key: str, site: str = "datadoghq.com"):
        self.api_key = api_key
        self.app_key = app_key
        self.site = site
        self.base_url = f"https://api.{site}/api/v2/llm-obs/v1"
        self.headers = {
            "DD-API-KEY": api_key,
            "DD-APPLICATION-KEY": app_key,
            "Content-Type": "application/json",
        }

    def get_or_create_project(self, name: str, description: str) -> str:
        """Get existing project ID or create new one."""
        # List projects
        url = f"{self.base_url}/projects"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()

        projects = response.json().get("data", [])
        for project in projects:
            if project["attributes"]["name"] == name:
                project_id = project["id"]
                print(f"✅ Found existing project: {name} (ID: {project_id})")
                return project_id

        # Create new project
        print(f"Creating new project: {name}")
        payload = {
            "data": {
                "type": "project",
                "attributes": {"name": name, "description": description},
            }
        }

        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()

        project_id = response.json()["data"]["id"]
        print(f"✅ Created project: {name} (ID: {project_id})")
        return project_id

    def create_dataset(
        self, project_id: str, name: str, description: str, version: int = 1
    ) -> str:
        """Create a new dataset."""
        url = f"{self.base_url}/datasets"
        payload = {
            "data": {
                "type": "dataset",
                "attributes": {
                    "project_id": project_id,
                    "name": name,
                    "description": description,
                    "dataset_version": version,
                },
            }
        }

        response = requests.post(url, json=payload, headers=self.headers)
        response.raise_for_status()

        dataset_id = response.json()["data"]["id"]
        print(f"✅ Created dataset: {name} (ID: {dataset_id})")
        return dataset_id

    def add_records(self, dataset_id: str, records: List[Dict[str, Any]]) -> int:
        """Add multiple records to a dataset."""
        url = f"{self.base_url}/datasets/{dataset_id}/records"
        added = 0

        print(f"\n📤 Pushing {len(records)} records to Datadog...")
        print("=" * 80)

        for i, record in enumerate(records, 1):
            try:
                payload = {
                    "data": {
                        "type": "dataset_record",
                        "attributes": {
                            "input": record["input"],
                            "expected_output": record["expected_output"],
                        },
                    }
                }

                response = requests.post(url, json=payload, headers=self.headers)
                response.raise_for_status()

                print(f"✅ Added record {i}/{len(records)}: {record.get('id', i)}")
                added += 1

            except Exception as e:
                print(f"❌ Failed to add record {i}: {e}")

        print("=" * 80)
        print(f"✅ Successfully added {added}/{len(records)} records\n")
        return added


def print_statistics(records: List[Dict[str, Any]]):
    """Print dataset statistics."""
    print("\n📊 Dataset Statistics")
    print("=" * 80)

    total_records = len(records)
    total_pages = sum(r["input"]["num_pages"] for r in records)
    avg_pages = total_pages / total_records if total_records > 0 else 0

    print(f"Total Records: {total_records}")
    print(f"Total Pages: {total_pages}")
    print(f"Avg Pages per Record: {avg_pages:.1f}")

    # Vote statistics
    total_votes = sum(
        r["expected_output"]["ballot_statistics"]["total_votes"] for r in records
    )
    total_valid = sum(
        r["expected_output"]["ballot_statistics"]["valid_ballots"] for r in records
    )
    total_invalid = sum(
        r["expected_output"]["ballot_statistics"]["invalid_ballots"] for r in records
    )

    print(f"\nBallot Statistics:")
    print(f"  Total Votes: {total_votes:,}")
    print(f"  Valid Ballots: {total_valid:,} ({total_valid/total_votes*100:.1f}%)")
    print(f"  Invalid Ballots: {total_invalid:,} ({total_invalid/total_votes*100:.1f}%)")

    # Districts
    districts = set(
        r["input"].get("district") for r in records if r["input"].get("district")
    )
    if districts:
        print(f"\nGeographic Coverage:")
        print(f"  Districts: {len(districts)}")
        for district in sorted(districts):
            count = sum(1 for r in records if r["input"].get("district") == district)
            print(f"    - {district}: {count} forms")

    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare vote extraction dataset for Datadog LLM Experiments"
    )
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Only save dataset locally, don't push to Datadog",
    )
    parser.add_argument(
        "--push-to-datadog",
        action="store_true",
        help="Push dataset to Datadog after saving locally",
    )
    parser.add_argument(
        "--version", default="v1", help="Dataset version (default: v1)"
    )
    args = parser.parse_args()

    print("=" * 80)
    print("🔬 Vote Extraction Dataset Preparation")
    print("=" * 80)

    # Step 1: Build dataset
    builder = DatasetBuilder(IMAGES_DIR, GROUND_TRUTH)
    records = builder.build_records()

    if not records:
        print("❌ No records created. Add ground truth data first.")
        sys.exit(1)

    # Step 2: Validate
    validator = DatasetValidator()
    if not validator.validate_all(records):
        print("❌ Validation failed. Fix errors before proceeding.")
        sys.exit(1)

    # Step 3: Print statistics
    print_statistics(records)

    # Step 4: Save locally
    saver = DatasetSaver()
    dataset_file = saver.save(records, version=args.version)

    # Step 5: Push to Datadog (optional)
    if args.push_to_datadog:
        load_dotenv(PROJECT_ROOT / ".env")

        DD_API_KEY = os.getenv("DD_API_KEY")
        DD_APP_KEY = os.getenv("DD_APP_KEY")
        DD_SITE = os.getenv("DD_SITE", "datadoghq.com")

        if not DD_API_KEY or not DD_APP_KEY:
            print("❌ Error: DD_API_KEY and DD_APP_KEY must be set in .env file")
            sys.exit(1)

        try:
            print("\n🔗 Pushing to Datadog...")
            print("=" * 80)

            manager = DatadogDatasetManager(DD_API_KEY, DD_APP_KEY, DD_SITE)

            # Get or create project
            project_id = manager.get_or_create_project(
                PROJECT_NAME, "Testing vote extraction from Thai election forms"
            )

            # Create dataset
            dataset_id = manager.create_dataset(
                project_id, DATASET_NAME, DATASET_DESCRIPTION, version=1
            )

            # Add records
            added = manager.add_records(dataset_id, records)

            print("=" * 80)
            print(f"✅ Dataset pushed to Datadog!")
            print(f"\n🔗 View dataset:")
            print(f"   https://app.{DD_SITE}/llm/datasets/{dataset_id}")

        except Exception as e:
            print(f"❌ Error pushing to Datadog: {e}")
            sys.exit(1)

    print("\n✅ Dataset preparation complete!")
    print(f"   Local file: {dataset_file}")
    if args.push_to_datadog:
        print(f"   Datadog: https://app.{DD_SITE}/llm/experiments")


if __name__ == "__main__":
    main()

