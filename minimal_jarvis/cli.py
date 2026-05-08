"""CLI for Minimal Jarvis."""

import argparse

from minimal_jarvis import Jarvis


def main() -> None:
    """Run CLI entry point."""
    parser = argparse.ArgumentParser(description="Minimal Jarvis CLI")
    subparsers = parser.add_subparsers(dest="command")

    ask_parser = subparsers.add_parser("ask", help="Ask Jarvis a question")
    ask_parser.add_argument("query", type=str)

    args = parser.parse_args()

    if args.command == "ask":
        jarvis = Jarvis()
        result = jarvis.ask(args.query)
        print(result)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
