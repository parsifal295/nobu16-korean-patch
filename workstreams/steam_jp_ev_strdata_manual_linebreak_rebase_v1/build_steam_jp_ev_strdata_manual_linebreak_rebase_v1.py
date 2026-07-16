#!/usr/bin/env python3
"""Build a private, four-coordinate hard-break rebase for Steam JP ev_strdata.

The current installed file is read-only input.  This builder never writes into
the Steam tree: its only output is a single private candidate below ``tmp``.
It does not copy legacy manual translation payloads; each target is derived
solely from the currently pinned cell by replacing each hard-break token with
one ASCII space.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


RESOURCE = Path("MSG") / "JP" / "ev_strdata.bin"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
TMP_ROOT = REPO / "tmp"
DEFAULT_OUTPUT_ROOT = TMP_ROOT / "steam_jp_ev_strdata_manual_linebreak_rebase_v1" / "candidate"
VERIFICATION_PATH = WORKSTREAM / "verification.v1.json"
SCHEMA = "nobu16.kr.steam-jp-ev-strdata-manual-linebreak-current-rebase-verification.v1"
MANIFEST_SCHEMA = "nobu16.kr.steam-jp-ev-strdata-manual-linebreak-current-rebase-build-manifest.v1"
LINE_BREAK_RE = re.compile(r"\r\n|\r|\n")
HEX64_RE = re.compile(r"[0-9A-F]{64}")


class RebaseError(ValueError):
    """A pinned source, coordinate contract, or candidate diverged."""


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def spec(value: bytes) -> dict[str, Any]:
    return {"size": len(value), "sha256": sha256(value)}


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16-le"))


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise RebaseError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def id_hash(values: Sequence[int]) -> str:
    return sha256(",".join(str(value) for value in sorted(values)).encode("ascii"))


def linebreaks(value: str) -> tuple[str, ...]:
    return tuple(common.message_invariants(value)["line_breaks"])


def protected_signature(value: str) -> dict[str, Any]:
    invariant = common.message_invariants(value)
    return {
        "printf": invariant["printf"],
        "unknown_percent_count": invariant["unknown_percent_count"],
        "esc": invariant["esc"],
        "controls": invariant["controls"],
        "pua": invariant["pua"],
    }


def replace_hard_breaks(value: str) -> str:
    return LINE_BREAK_RE.sub(" ", value)


def assert_linebreak_only(before: str, after: str, label: str) -> None:
    require(after, replace_hard_breaks(before), f"{label} exact hard-break replacement")
    require(linebreaks(after), (), f"{label} target line-break vector")
    require(protected_signature(after), protected_signature(before), f"{label} protected signature")
    before_invariant = common.message_invariants(before)
    after_invariant = common.message_invariants(after)
    require(after_invariant["leading_whitespace"], before_invariant["leading_whitespace"], f"{label} leading whitespace")
    require(after_invariant["trailing_whitespace"], before_invariant["trailing_whitespace"], f"{label} trailing whitespace")
    mismatches = common.invariant_mismatches(before, after)
    if not mismatches or any(not item.startswith("line_breaks:") for item in mismatches):
        raise RebaseError(f"{label} changed a non-line-break invariant")


def read_json(path: Path) -> tuple[dict[str, Any], bytes]:
    try:
        blob = path.read_bytes()
        value = json.loads(blob.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RebaseError(f"cannot read JSON artifact: {path}") from exc
    if not isinstance(value, dict):
        raise RebaseError(f"JSON root is not an object: {path}")
    return value, blob


def require_spec(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise RebaseError(f"{label} spec is absent")
    size = value.get("size")
    digest = value.get("sha256")
    if not isinstance(size, int) or size < 1 or not isinstance(digest, str) or HEX64_RE.fullmatch(digest) is None:
        raise RebaseError(f"{label} spec is invalid")
    return {"size": size, "sha256": digest}


def load_contract(path: Path = VERIFICATION_PATH) -> tuple[dict[str, Any], bytes]:
    contract, blob = read_json(path)
    require(contract.get("schema"), SCHEMA, "verification schema")
    require(contract.get("resource"), RESOURCE.as_posix(), "verification resource")
    source = contract.get("source")
    candidate = contract.get("candidate")
    operation = contract.get("operation")
    if not isinstance(source, Mapping) or not isinstance(candidate, Mapping) or not isinstance(operation, Mapping):
        raise RebaseError("verification contract section is absent")
    require_spec(source.get("packed"), "source packed")
    require_spec(source.get("raw"), "source raw")
    require_spec(candidate.get("packed"), "candidate packed")
    require_spec(candidate.get("raw"), "candidate raw")
    if not isinstance(source.get("string_count"), int) or source["string_count"] < 1:
        raise RebaseError("source string count is invalid")
    entries = operation.get("coordinates")
    if not isinstance(entries, list) or len(entries) != 4:
        raise RebaseError("coordinate count differs")
    ids: list[int] = []
    token_count = 0
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise RebaseError("coordinate entry is invalid")
        entry_id = entry.get("id")
        if not isinstance(entry_id, int) or entry_id < 0 or entry_id in ids:
            raise RebaseError("coordinate ID is invalid")
        ids.append(entry_id)
        for key in ("current_utf16le_sha256", "target_utf16le_sha256"):
            if not isinstance(entry.get(key), str) or HEX64_RE.fullmatch(entry[key]) is None:
                raise RebaseError(f"coordinate {entry_id} {key} is invalid")
        for key in ("current_linebreak_vector", "target_linebreak_vector"):
            vector = entry.get(key)
            if not isinstance(vector, list) or not all(isinstance(item, str) for item in vector):
                raise RebaseError(f"coordinate {entry_id} {key} is invalid")
        for key in ("current_protected_signature", "target_protected_signature"):
            if not isinstance(entry.get(key), Mapping):
                raise RebaseError(f"coordinate {entry_id} {key} is invalid")
        token_count += len(entry["current_linebreak_vector"])
    require(ids, sorted(ids), "coordinate ordering")
    require(operation.get("coordinate_ids_sha256"), id_hash(ids), "coordinate ID hash")
    require(operation.get("hard_break_token_count"), token_count, "hard-break token count")
    if token_count < 1:
        raise RebaseError("hard-break token count is empty")
    return contract, blob


def candidate_from_current(steam_root: Path, contract: Mapping[str, Any]) -> tuple[bytes, bytes, dict[str, Any]]:
    source_path = steam_root / RESOURCE
    if not source_path.is_file():
        raise RebaseError(f"missing Steam input: {source_path}")
    packed = source_path.read_bytes()
    source = contract["source"]
    require(spec(packed), require_spec(source["packed"], "source packed"), "current packed source")
    header, raw = decompress_wrapper(packed)
    require(spec(raw), require_spec(source["raw"], "source raw"), "current raw source")
    table = parse_message_table(raw)
    require(table.string_count, source["string_count"], "current string count")
    require(rebuild_message_table(table, table.texts), raw, "current raw parse/rebuild")

    entries = contract["operation"]["coordinates"]
    replacements: dict[int, str] = {}
    changed_ids: list[int] = []
    for entry in entries:
        entry_id = entry["id"]
        if entry_id >= table.string_count:
            raise RebaseError(f"coordinate outside table: {entry_id}")
        before = table.texts[entry_id]
        require(text_hash(before), entry["current_utf16le_sha256"], f"current cell hash {entry_id}")
        require(list(linebreaks(before)), entry["current_linebreak_vector"], f"current line-break vector {entry_id}")
        require(protected_signature(before), entry["current_protected_signature"], f"current protected signature {entry_id}")
        after = replace_hard_breaks(before)
        assert_linebreak_only(before, after, f"current cell {entry_id}")
        require(text_hash(after), entry["target_utf16le_sha256"], f"target cell hash {entry_id}")
        require(list(linebreaks(after)), entry["target_linebreak_vector"], f"target line-break vector {entry_id}")
        require(protected_signature(after), entry["target_protected_signature"], f"target protected signature {entry_id}")
        replacements[entry_id] = after
        changed_ids.append(entry_id)

    final_texts = [replacements.get(index, value) for index, value in enumerate(table.texts)]
    candidate_raw = rebuild_message_table(table, final_texts)
    candidate = recompress_wrapper(candidate_raw, header)
    candidate_header, roundtrip_raw = decompress_wrapper(candidate)
    require(candidate_header.prefix, header.prefix, "candidate wrapper prefix")
    require(roundtrip_raw, candidate_raw, "candidate wrapper round-trip")
    candidate_table = parse_message_table(candidate_raw)
    require(candidate_table.texts, tuple(final_texts), "candidate text round-trip")
    require(rebuild_message_table(candidate_table, candidate_table.texts), candidate_raw, "candidate raw parse/rebuild")
    observed_changed = [
        entry_id
        for entry_id, (before, after) in enumerate(zip(table.texts, candidate_table.texts))
        if before != after
    ]
    require(observed_changed, changed_ids, "candidate changed coordinate domain")
    require(
        sum(len(linebreaks(table.texts[entry_id])) for entry_id in observed_changed),
        contract["operation"]["hard_break_token_count"],
        "candidate replaced hard-break token count",
    )
    expected_candidate = contract["candidate"]
    require(spec(candidate), require_spec(expected_candidate["packed"], "candidate packed"), "candidate packed output")
    require(spec(candidate_raw), require_spec(expected_candidate["raw"], "candidate raw"), "candidate raw output")
    report = {
        "source": {"packed": spec(packed), "raw": spec(raw), "string_count": table.string_count},
        "candidate": {"packed": spec(candidate), "raw": spec(candidate_raw)},
        "changed_ids": observed_changed,
        "changed_ids_sha256": id_hash(observed_changed),
        "hard_break_tokens_replaced": contract["operation"]["hard_break_token_count"],
        "checks": {
            "source_pins": "OK",
            "four_current_cell_hashes": "OK",
            "four_linebreak_vectors": "OK",
            "four_protected_signatures": "OK",
            "linebreak_only_transforms": "OK",
            "changed_coordinate_domain": "OK",
            "wrapper_roundtrip": "OK",
            "candidate_pins": "OK",
        },
    }
    return candidate, candidate_raw, report


def private_output_root(value: Path) -> Path:
    output = value.resolve()
    allowed = TMP_ROOT.resolve()
    try:
        output.relative_to(allowed)
    except ValueError as exc:
        raise RebaseError("candidate output must stay below KR_PATCH_WORK/tmp") from exc
    if output == allowed:
        raise RebaseError("KR_PATCH_WORK/tmp cannot be the candidate root")
    return output


def atomic_write(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(value)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def manifest(contract_blob: bytes, report: Mapping[str, Any], candidate_path: Path) -> dict[str, Any]:
    return {
        "schema": MANIFEST_SCHEMA,
        "resource": RESOURCE.as_posix(),
        "candidate_relative_path": RESOURCE.as_posix(),
        "candidate_path": str(candidate_path),
        "verification": {
            "relative_path": str(VERIFICATION_PATH.relative_to(REPO)).replace("\\", "/"),
            "sha256": sha256(contract_blob),
        },
        "source": report["source"],
        "candidate": report["candidate"],
        "changed_ids": report["changed_ids"],
        "changed_ids_sha256": report["changed_ids_sha256"],
        "hard_break_tokens_replaced": report["hard_break_tokens_replaced"],
        "checks": report["checks"],
        "scope": {
            "candidate_private_only": True,
            "steam_install_written": False,
            "font_resources_touched": False,
            "other_resources_touched": False,
        },
    }


def verify(steam_root: Path) -> dict[str, Any]:
    contract, _blob = load_contract()
    _candidate, _raw, report = candidate_from_current(steam_root, contract)
    return report


def build(steam_root: Path, output_root: Path) -> dict[str, Any]:
    contract, contract_blob = load_contract()
    candidate, _raw, report = candidate_from_current(steam_root, contract)
    output = private_output_root(output_root)
    target = output / RESOURCE
    atomic_write(target, candidate)
    require(target.read_bytes(), candidate, "written private candidate")
    build_manifest = manifest(contract_blob, report, target)
    atomic_write(output / "build_manifest.v1.json", canonical_json_bytes(build_manifest))
    return {
        "candidate_path": str(target),
        "manifest_path": str(output / "build_manifest.v1.json"),
        "candidate_sha256": report["candidate"]["packed"]["sha256"],
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "build"))
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "verify":
            print(json.dumps(verify(args.steam_root), ensure_ascii=False, sort_keys=True))
        else:
            print(json.dumps(build(args.steam_root, args.output_root), ensure_ascii=False, sort_keys=True))
    except RebaseError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
