from __future__ import annotations

import argparse
import dataclasses
import json
import sys

from . import fetch


def _die(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    sys.exit(1)


def _result_for(url: str):
    result = fetch(url)
    if not result.ok:
        print(
            f"warning: fetch did not fully succeed (signals: {', '.join(result.failure_signals)})",
            file=sys.stderr,
        )
    return result


# --- subcommand handlers ---

def _cmd_html(args: argparse.Namespace) -> None:
    print(_result_for(args.url).html)


def _cmd_content(args: argparse.Namespace) -> None:
    print(_result_for(args.url).content)


def _cmd_markdown(args: argparse.Namespace) -> None:
    print(_result_for(args.url).markdown)


def _cmd_metadata(args: argparse.Namespace) -> None:
    result = _result_for(args.url)
    print(json.dumps(dataclasses.asdict(result.metadata), indent=2, ensure_ascii=False))


def _cmd_fetch(args: argparse.Namespace) -> None:
    result = _result_for(args.url)
    data: dict = {
        "url": result.url,
        "method": result.method,
        "ok": result.ok,
        "failure_signals": result.failure_signals,
        "metadata": dataclasses.asdict(result.metadata),
        "markdown": result.markdown,
    }
    if args.include_html:
        data["html"] = result.html
    if args.include_content:
        data["content"] = result.content
    print(json.dumps(data, indent=2, ensure_ascii=False))


# --- parser ---

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ezdl2",
        description="Fetch web pages with automatic HTTP-to-browser fallback.",
    )
    sub = parser.add_subparsers(dest="command", metavar="<command>")
    sub.required = True

    url_help = "URL of the page to fetch"

    p_html = sub.add_parser("html", help="Print the raw fetched HTML")
    p_html.add_argument("url", help=url_help)
    p_html.set_defaults(func=_cmd_html)

    p_content = sub.add_parser("content", help="Print the extracted main-content HTML")
    p_content.add_argument("url", help=url_help)
    p_content.set_defaults(func=_cmd_content)

    p_markdown = sub.add_parser("markdown", help="Print the page as clean markdown")
    p_markdown.add_argument("url", help=url_help)
    p_markdown.set_defaults(func=_cmd_markdown)

    p_meta = sub.add_parser("metadata", help="Print page metadata as JSON")
    p_meta.add_argument("url", help=url_help)
    p_meta.set_defaults(func=_cmd_metadata)

    p_fetch = sub.add_parser(
        "fetch",
        help="Fetch and print a JSON envelope with metadata + markdown",
    )
    p_fetch.add_argument("url", help=url_help)
    p_fetch.add_argument(
        "--include-html",
        action="store_true",
        help="Include raw HTML in the JSON output",
    )
    p_fetch.add_argument(
        "--include-content",
        action="store_true",
        help="Include extracted content HTML in the JSON output",
    )
    p_fetch.set_defaults(func=_cmd_fetch)

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:
        _die(str(exc))


if __name__ == "__main__":
    main()
