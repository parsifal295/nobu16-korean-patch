#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anyio
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


DEFAULT_GHIDRA = "http://127.0.0.1:8080/"


@dataclass
class ProbeConfig:
    win_python: str
    bridge_py: str
    ghidra_server: str
    import_limit: int
    search_limit: int
    search_queries: list[str]


def extract_text_list(call_result: Any) -> list[str]:
    out: list[str] = []
    for item in getattr(call_result, "content", []):
        text = getattr(item, "text", None)
        if text is not None:
            out.append(text)
    return out


def looks_interesting(name: str) -> bool:
    lower = name.lower()
    needles = [
        "msg",
        "lang",
        "text",
        "font",
        "wide",
        "multi",
        "read",
        "file",
        "draw",
        "ui",
    ]
    return any(n in lower for n in needles)


async def run_probe(cfg: ProbeConfig) -> dict[str, Any]:
    params = StdioServerParameters(
        command=cfg.win_python,
        args=[cfg.bridge_py, "--ghidra-server", cfg.ghidra_server],
        env={},
    )

    payload: dict[str, Any] = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "config": asdict(cfg),
    }

    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            init = await session.initialize()
            payload["server"] = {
                "name": init.serverInfo.name,
                "version": init.serverInfo.version,
            }

            tools = await session.list_tools()
            payload["tools"] = [t.name for t in tools.tools]

            imports_res = await session.call_tool(
                "list_imports", {"offset": 0, "limit": cfg.import_limit}
            )
            imports = extract_text_list(imports_res)
            payload["imports"] = imports
            payload["imports_hit"] = [
                x
                for x in imports
                if any(
                    k in x.lower()
                    for k in [
                        "multibytetowidechar",
                        "widechartomultibyte",
                        "drawtext",
                        "textout",
                        "createfont",
                        "fopen",
                        "fread",
                        "createfile",
                        "readfile",
                    ]
                )
            ]

            search_results: dict[str, list[str]] = {}
            for q in cfg.search_queries:
                res = await session.call_tool(
                    "search_functions_by_name",
                    {"query": q, "offset": 0, "limit": cfg.search_limit},
                )
                search_results[q] = extract_text_list(res)

            payload["search"] = search_results

            merged: list[str] = []
            seen = set()
            for q in cfg.search_queries:
                for name in search_results.get(q, []):
                    if name in seen:
                        continue
                    if not looks_interesting(name):
                        continue
                    merged.append(name)
                    seen.add(name)
            payload["interesting_functions"] = merged[:100]

    return payload


def write_markdown(path: Path, data: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append("# Ghidra MCP Probe Report")
    lines.append("")
    lines.append(f"- timestamp_utc: {data.get('timestamp_utc')}")
    lines.append(
        f"- server: {data.get('server', {}).get('name')} {data.get('server', {}).get('version')}"
    )
    lines.append(f"- tools: {len(data.get('tools', []))}")
    lines.append("")

    lines.append("## API Import Hits")
    lines.append("")
    hits = data.get("imports_hit", [])
    if hits:
        for h in hits:
            lines.append(f"- {h}")
    else:
        lines.append("- (none in fetched window)")
    lines.append("")

    lines.append("## Interesting Function Name Hits")
    lines.append("")
    funcs = data.get("interesting_functions", [])
    if funcs:
        for f in funcs[:80]:
            lines.append(f"- {f}")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Search Samples")
    lines.append("")
    for q, names in data.get("search", {}).items():
        lines.append(f"### query: {q}")
        if names:
            for n in names[:20]:
                lines.append(f"- {n}")
        else:
            lines.append("- (empty)")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Probe Ghidra through ghidra-mcp and save results.")
    p.add_argument("--win-python", default=sys.executable)
    p.add_argument("--bridge-py", required=True)
    p.add_argument("--ghidra-server", default=DEFAULT_GHIDRA)
    p.add_argument("--import-limit", type=int, default=400)
    p.add_argument("--search-limit", type=int, default=120)
    p.add_argument(
        "--search-query",
        action="append",
        default=["msg", "text", "font", "wide", "lang", "read", "file", "ui"],
    )
    p.add_argument("--out-json", required=True)
    p.add_argument("--out-md", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    cfg = ProbeConfig(
        win_python=args.win_python,
        bridge_py=args.bridge_py,
        ghidra_server=args.ghidra_server,
        import_limit=args.import_limit,
        search_limit=args.search_limit,
        search_queries=args.search_query,
    )

    data = anyio.run(run_probe, cfg)

    out_json = Path(args.out_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    write_markdown(Path(args.out_md), data)

    print(f"server={data.get('server', {}).get('name')} {data.get('server', {}).get('version')}")
    print(f"tools={len(data.get('tools', []))}")
    print(f"imports_hit={len(data.get('imports_hit', []))}")
    print(f"interesting_functions={len(data.get('interesting_functions', []))}")
    print(f"json={out_json}")
    print(f"md={args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
