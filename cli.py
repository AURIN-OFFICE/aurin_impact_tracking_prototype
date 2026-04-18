"""
CLI entry point for AURIN data capture.

Usage:
    uv run capture [options]
    python cli.py [options]

Examples:
    uv run capture                                          # capture all sources
    uv run capture --source dimensions --api-key <KEY>
    uv run capture --source media
    uv run capture --source all --from-date 2020-01-01 --to-date 2024-12-31
"""
import argparse
import os
import sys

from dotenv import load_dotenv

from data import AurinDatabase, DataCapture, CaptureError, MediaCapture, MediaCaptureError


def _progress(fraction: float, label: str) -> None:
    pct = int(fraction * 100)
    print(f"[{pct:3d}%] {label}", flush=True)


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="capture",
        description="Fetch AURIN data and store it in the local SQLite cache.",
    )
    parser.add_argument(
        "-s", "--source",
        choices=["all", "dimensions", "media"],
        default="all",
        help="Data source to capture: 'dimensions', 'media', or 'all' (default: all)",
    )
    parser.add_argument(
        "-k", "--api-key",
        default=os.getenv("DIMENSIONS_API_KEY", ""),
        help="Dimensions API key (defaults to DIMENSIONS_API_KEY env var); required for 'dimensions' and 'all'",
    )
    parser.add_argument(
        "-f", "--from-date",
        default=None,
        metavar="YYYY-MM-DD",
        help="Only include Dimensions records on or after this date (optional)",
    )
    parser.add_argument(
        "-t", "--to-date",
        default=None,
        metavar="YYYY-MM-DD",
        help="Only include Dimensions records on or before this date (optional)",
    )
    parser.add_argument(
        "-e", "--endpoint",
        default="https://app.dimensions.ai",
        help="Dimensions API endpoint URL",
    )

    args = parser.parse_args()

    needs_dimensions = args.source in ("dimensions", "all")
    if needs_dimensions and not args.api_key:
        parser.error(
            "No API key supplied for Dimensions. Pass --api-key or set the DIMENSIONS_API_KEY environment variable."
        )

    db = AurinDatabase()

    if needs_dimensions:
        capture = DataCapture(
            api_key=args.api_key,
            from_date=args.from_date,
            to_date=args.to_date,
            endpoint=args.endpoint,
        )
        try:
            capture.capture_all(db, progress_callback=_progress)
            _progress(1.0, "Dimensions capture complete.")
        except CaptureError as e:
            print(f"ERROR (dimensions): {e}", file=sys.stderr)
            sys.exit(2)
        except Exception as e:
            print(f"UNEXPECTED ERROR (dimensions): {e}", file=sys.stderr)
            sys.exit(3)

    if args.source in ("media", "all"):
        media_capture = MediaCapture()
        try:
            total = media_capture.capture_all(db, progress_callback=_progress)
            _progress(1.0, f"Media capture complete — {total} total mentions stored.")
        except MediaCaptureError as e:
            print(f"ERROR (media): {e}", file=sys.stderr)
            sys.exit(2)
        except Exception as e:
            print(f"UNEXPECTED ERROR (media): {e}", file=sys.stderr)
            sys.exit(3)


if __name__ == "__main__":
    main()
