"""
main.py — Application entry point for the Clinic Lead Generation Agent.

Usage:
    python main.py
    python main.py --locations London Dubai --types "Dental Clinic" "Skin Clinic" --max 50
    python main.py --interactive
"""
import argparse
import json
import sys

from app.agent.agent import ClinicLeadAgent
from app.schemas.request import ClinicSearchRequest
from app.utils.constants import CLINIC_TYPES, TARGET_LOCATIONS
from app.utils.logger import get_logger

logger = get_logger("main")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Clinic Lead Generation AI Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python main.py
  python main.py --locations London Dubai --max 50
  python main.py --locations Islamabad Karachi --types "Dental Clinic" "Skin Clinic"
  python main.py --min-rating 4.0 --automation Manual
  python main.py --interactive

Supported locations:
  {json.dumps(TARGET_LOCATIONS, indent=4)}
        """,
    )
    parser.add_argument(
        "--locations", nargs="+", default=[],
        help="Cities or countries to search (default: all supported)"
    )
    parser.add_argument(
        "--types", nargs="+", default=CLINIC_TYPES,
        help="Clinic types to search for"
    )
    parser.add_argument(
        "--max", type=int, default=100,
        help="Maximum number of leads to collect (default: 100)"
    )
    parser.add_argument(
        "--min-rating", type=float, default=None,
        help="Minimum Google rating filter (e.g. 4.0)"
    )
    parser.add_argument(
        "--automation", type=str, default=None,
        choices=["Manual", "Semi Automated", "Automated"],
        help="Filter by automation status"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Save results to a JSON file (e.g. outputs/leads.json)"
    )
    parser.add_argument(
        "--interactive", action="store_true",
        help="Start interactive chat mode"
    )
    return parser.parse_args()


def run_search(args) -> None:
    """Run a single lead generation search."""
    request = ClinicSearchRequest(
        locations=args.locations,
        clinic_types=args.types,
        max_results=args.max,
        min_rating=args.min_rating,
        automation_filter=args.automation,
    )

    logger.info("Initialising ClinicLeadAgent...")
    agent = ClinicLeadAgent()
    response = agent.run(request)

    # Print summary
    print("\n" + "="*60)
    print(f"  Run ID    : {response.run_id}")
    print(f"  Status    : {'✅ Success' if response.success else '❌ Failed'}")
    print(f"  Leads     : {response.total_found}")
    print(f"  Summary   : {response.summary}")
    if response.errors:
        print(f"  Errors    : {len(response.errors)}")
        for e in response.errors[:5]:
            print(f"    - {e}")
    print("="*60 + "\n")

    # Print first 5 leads as a preview
    for i, lead in enumerate(response.leads[:5]):
        print(f"  [{i+1}] {lead.clinic_name} | {lead.city}, {lead.country}")
        print(f"       Type: {lead.clinic_type} | Rating: {lead.google_rating}")
        print(f"       Phone: {lead.phone_number} | Automation: {lead.automation_status}")
        print(f"       Priority: {lead.lead_priority}")
        print()

    # Save to file if requested
    if args.output:
        import os
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(
                [lead.model_dump() for lead in response.leads],
                f, indent=2, ensure_ascii=False, default=str,
            )
        logger.info("Results saved to %s", args.output)
        print(f"Results saved to: {args.output}")


def run_interactive() -> None:
    """Interactive chat mode for multi-turn queries."""
    print("\n" + "="*60)
    print("  Clinic Lead Generation Agent — Interactive Mode")
    print("  Type 'quit' to exit, 'run' to start a search.")
    print("="*60 + "\n")

    agent = ClinicLeadAgent()
    base_request = ClinicSearchRequest()

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break
        if user_input.lower() == "run":
            response = agent.run(base_request)
            print(f"\nAgent: {response.summary}")
            print(f"Collected {response.total_found} leads.\n")
            continue

        reply = agent.chat(user_input, base_request=base_request)
        print(f"\nAgent: {reply}\n")


def main():
    args = parse_args()
    if args.interactive:
        run_interactive()
    else:
        run_search(args)


if __name__ == "__main__":
    main()
