#!/usr/bin/env python3
"""Reuse reviewed Base-event Korean for exact-hash DLC event sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
DEFAULT_CATALOG = WORKSTREAM / "private" / "catalog.private.v1.json"
DEFAULT_DONOR = (
    REPO
    / "workstreams"
    / "base_ev_strdata_jp_switch_v13_transfer_v1"
    / "public"
    / "ev_strdata_ko_base_jp_switch_v13_transfer_13045.v1.json"
)
DEFAULT_OUTPUT = WORKSTREAM / "translations.wave05.exact_event_reuse.v1.json"

OVERLAY_SCHEMA = "nobu16.kr.dlc-translation-overlay.v1"
ESC_RE = re.compile(r"\x1bC[A-Z]")
RUNTIME_TOKEN_RE = re.compile(r"\[(?:bm?|[A-Za-z]+)\d+\]")
PRINTF_RE = re.compile(
    r"%(?:\d+\$)?[-+#0 ']*\d*(?:\.\d+)?(?:hh|h|ll|l|j|z|t|L)?[diuoxXfFeEgGaAcspn%]"
)
SOURCE_SCRIPT_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]")

# Six donor translations are semantically retained but reflowed for the
# authoritative static-patch-007 30px/912px/four-line DLC event baseline.
MANUAL_REFLOWS = {
    "jp-e75558e6a4214946784d": (
        "이에 \x1bCB호조가\x1bCZ는 \x1bCC기타신\x1bCZ을 넘겨주는 조건으로\n"
        "\x1bCB우에스기가\x1bCZ와 화목하고,\n"
        "전군을 \x1bCB[bs1871]가\x1bCZ로 돌렸다."
    ),
    "jp-52b7771f68e277bd7aab": (
        "자아, 이제 남은 일은\n"
        "쳐들어올 \x1bCB호조\x1bCZ를 막는 것뿐.\n"
        "\x1bCA[bs1871]\x1bCZ 님도 따르게 된 \x1bCB사나다\x1bCZ를\n"
        "내버려 두지는 못할 터."
    ),
    "jp-86f66added77b459d582": (
        "\x1bCC스루가\x1bCZ의 \x1bCB[bs1871]\x1bCZ, \x1bCC사가미\x1bCZ의 \x1bCB호조\x1bCZ,\n"
        "\x1bCC에치고\x1bCZ의 \x1bCB우에스기\x1bCZ.\n"
        "세 세력이 뒤엉켜 나라를 다투게 될 것은 필정."
    ),
    "jp-c326865d81db84a02b6b": (
        "\x1bCA[bs754]히데요시\x1bCZ가 \x1bCC야마자키\x1bCZ 전투에서\n"
        "\x1bCA아케치 미쓰히데\x1bCZ를 쓰러뜨리자,\n"
        "\x1bCB오다가\x1bCZ의 앞날에 이목이 집중된다."
    ),
    "jp-fb782ab5f61336ad6f59": (
        "이후로는 나를 신경 쓰지 말고\n"
        "\x1bCA[bs754]\x1bCZ 님에게 항복하시오.\n"
        "나를 생각해 주는 마음은 기쁘지만,\n"
        "그 마음 때문에 길을 그르치는 일이 없도록……"
    ),
    "jp-676b92d0dda3b91f2a87": (
        "\x1bCA[bm1871]\x1bCZ는 \x1bCA히데요시\x1bCZ가\n"
        "다른 세력을 끌어들이리라 예상하고,\n"
        "스스로도 \x1bCA히데요시\x1bCZ에게 반감을 품은 세력에\n"
        "공동 전선을 펼 것을 제안한다."
    ),
}


class ReuseError(ValueError):
    """Raised when an exact-hash donor or authored-wave invariant differs."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ReuseError(f"JSON root must be an object: {path}")
    return value


def protected_tokens(text: str) -> list[str]:
    found: list[tuple[int, str]] = []
    for pattern in (ESC_RE, RUNTIME_TOKEN_RE, PRINTF_RE):
        found.extend((match.start(), match.group(0)) for match in pattern.finditer(text))
    return [value for _, value in sorted(found)]


def authored_source_ids(output: Path) -> set[str]:
    result: set[str] = set()
    for path in sorted(WORKSTREAM.glob("translations.wave*.v1.json")):
        if path.resolve() == output.resolve():
            continue
        document = read_json(path)
        entries = document.get("entries")
        if not isinstance(entries, list):
            raise ReuseError(f"authored overlay entries are absent: {path}")
        for entry in entries:
            source_id = entry.get("source_id") if isinstance(entry, dict) else None
            if not isinstance(source_id, str):
                raise ReuseError(f"authored overlay source ID differs: {path}")
            result.add(source_id)
    return result


def build_overlay(
    catalog: dict[str, Any], donor: dict[str, Any], output: Path
) -> dict[str, Any]:
    donor_by_hash: dict[str, set[str]] = defaultdict(set)
    for entry in donor.get("entries", []):
        if not isinstance(entry, dict):
            raise ReuseError("donor entry shape differs")
        source_hash = entry.get("source_jp_utf16le_sha256")
        korean = entry.get("ko")
        if not isinstance(source_hash, str) or not isinstance(korean, str) or not korean:
            raise ReuseError("donor source hash or Korean text differs")
        donor_by_hash[source_hash.lower()].add(korean)
    conflicts = {key: value for key, value in donor_by_hash.items() if len(value) != 1}
    if conflicts:
        raise ReuseError(f"exact source hash has conflicting donor Korean: {len(conflicts)}")
    resolved_donor = {key: next(iter(value)) for key, value in donor_by_hash.items()}

    already_authored = authored_source_ids(output)
    sources = {value["source_id"]: value for value in catalog["sources"]}
    selected: list[dict[str, Any]] = []
    for placement in catalog["placements"]:
        if placement["family"] != "evm" or placement["source_id"] in already_authored:
            continue
        if placement["jp_utf16le_sha256"] in resolved_donor:
            selected.append(placement)
    if not selected:
        raise ReuseError("exact event donor selected zero DLC placements")

    selected_source_ids = {value["source_id"] for value in selected}
    unknown_reflows = set(MANUAL_REFLOWS) - selected_source_ids
    if unknown_reflows:
        raise ReuseError(f"manual reflow is outside exact selection: {sorted(unknown_reflows)}")
    entries: list[dict[str, str]] = []
    for source_id in sorted(selected_source_ids):
        source = sources[source_id]
        donor_ko = resolved_donor[source["jp_utf16le_sha256"]]
        korean = MANUAL_REFLOWS.get(source_id, donor_ko)
        if SOURCE_SCRIPT_RE.search(korean):
            raise ReuseError(f"source script remains in exact donor: {source_id}")
        if protected_tokens(korean) != protected_tokens(source["jp"]):
            raise ReuseError(f"protected token sequence differs in donor: {source_id}")
        entries.append({"source_id": source_id, "ko": korean})

    return {
        "schema": OVERLAY_SCHEMA,
        "wave": "wave05_exact_event_reuse",
        "status": "exact_hash_reuse_static_validation_pending_runtime_qa",
        "scope": {
            "placement_ids": sorted(value["placement_id"] for value in selected)
        },
        "policy": {
            "base_language": "JP",
            "crosscheck_languages": ["SC", "TC", "EN"],
            "contains_commercial_source_text": False,
            "coordinate_override_supported": True,
            "event_layout_baseline": "static_patch_007_30px_912px_4lines",
            "reuse_gate": "exact_full_jp_utf16le_sha256",
        },
        "provenance": {
            "donor": DEFAULT_DONOR.relative_to(REPO).as_posix(),
            "donor_sha256": sha256(canonical_json(donor)),
            "private_catalog_sha256": sha256(canonical_json(catalog)),
            "manual_layout_only_reflows": sorted(MANUAL_REFLOWS),
        },
        "entries": entries,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--donor", type=Path, default=DEFAULT_DONOR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--validate", action="store_true")
    args = parser.parse_args(argv)

    catalog = read_json(args.catalog)
    donor = read_json(args.donor)
    overlay = build_overlay(catalog, donor, args.output)
    blob = canonical_json(overlay)
    if args.write:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(blob)
    elif not args.output.is_file() or args.output.read_bytes() != blob:
        raise ReuseError(f"exact reuse overlay drifted: {args.output}")
    print(
        json.dumps(
            {
                "entries": len(overlay["entries"]),
                "target_placements": len(overlay["scope"]["placement_ids"]),
                "manual_layout_reflows": len(MANUAL_REFLOWS),
                "steam_writes": 0,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
