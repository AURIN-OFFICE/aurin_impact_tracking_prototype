"""
CLI entry point for AURIN data capture.

Runs the same capture pipeline as the Streamlit "Refresh Data" button,
without requiring the web UI.

Usage:
    uv run capture [options]
    python cli.py [options]

Examples:
    uv run capture --api-key <KEY> --from-date 2020-01-01 --to-date 2024-12-31
    uv run capture                   # reads DIMENSIONS_API_KEY from .env / env
"""
import argparse
import os
import sys

from dotenv import load_dotenv

from data import AurinDatabase, DataCapture, CaptureError


def _progress(fraction: float, label: str) -> None:
    pct = int(fraction * 100)
    print(f"[{pct:3d}%] {label}", flush=True)


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="capture",
        description="Fetch AURIN data from the Dimensions API and store it in the local SQLite cache.",
    )
    parser.add_argument(
        "-k", "--api-key",
        default=os.getenv("DIMENSIONS_API_KEY", ""),
        help="Dimensions API key (defaults to DIMENSIONS_API_KEY env var)",
    )
    parser.add_argument(
        "-f", "--from-date",
        default=None,
        metavar="YYYY-MM-DD",
        help="Only include records on or after this date (optional)",
    )
    parser.add_argument(
        "-t", "--to-date",
        default=None,
        metavar="YYYY-MM-DD",
        help="Only include records on or before this date (optional)",
    )
    parser.add_argument(
        "-e", "--endpoint",
        default="https://app.dimensions.ai",
        help="Dimensions API endpoint URL",
    )

    args = parser.parse_args()

    if not args.api_key:
        parser.error(
            "No API key supplied. Pass --api-key or set the DIMENSIONS_API_KEY environment variable."
        )

    db = AurinDatabase()
    capture = DataCapture(
        api_key=args.api_key,
        from_date=args.from_date,
        to_date=args.to_date,
        endpoint=args.endpoint,
    )

    try:
        capture.capture_all(db, progress_callback=_progress)
        _progress(1.0, "Capture complete.")
    except CaptureError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()
