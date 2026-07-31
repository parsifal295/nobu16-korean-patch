#!/usr/bin/env python3
"""Build the source-free proposal-reference dialogue hotfix for v0.90.3.

The affected Base/PK records finish a translated ``참조해`` stem through a
shared runtime selector.  One Korean selector branch renders ``저것``, which
produces the nonsensical visible sentence ``필요 시 참조해저것``.  This
builder keeps the first, working speech-style selector and replaces the two
later selectors with byte-length-preserving empty literals.

Only isolated candidates below this worktree's ``tmp`` directory can be
written.  The builder never writes to a Steam installation or a release ZIP.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
WORKSPACE = REPO.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
DEFAULT_INPUT_ROOT = (
    WORKSPACE
    / "scratch"
    / "release-v0901-20260731"
    / "isolated-four-profile"
)
DEFAULT_OUTPUT_ROOT = TMP_ROOT / "candidate"
DEFAULT_MANIFEST_PATH = TMP_ROOT / "build_manifest.v1.json"
OVERLAY_PATH = WORKSTREAM / "public" / "proposal_reference_hotfix.v1.json"

MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
if str(MSGGAME_TOOLS) not in sys.path:
    sys.path.insert(0, str(MSGGAME_TOOLS))

from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
)


SCHEMA = "nobu16.kr.pc-dialogue-proposal-reference-hotfix-build.v1"
OVERLAY_SCHEMA = "nobu16.kr.pc-dialogue-proposal-reference-hotfix-overlay.v1"
EMPTY_LITERAL = LITERAL_START + LITERAL_END
RETURN = bytes.fromhex("050505")


@dataclass(frozen=True)
class ResourceSpec:
    relative_path: str
    coordinate: tuple[int, int]
    input_size: int
    input_sha256: str
    target_size: int
    target_sha256: str
    expected_literals: tuple[str, ...]
    expected_gaps_hex: tuple[str, ...]
    target_literals: tuple[str, ...]
    target_gaps_hex: tuple[str, ...]
    current_profile_render: str


SPECS = (
    ResourceSpec(
        relative_path="MSG/JP/msggame.bin",
        coordinate=(15, 2255),
        input_size=1_557_915,
        input_sha256=(
            "ADB73561AAA10A66364B3C09B2184BB29698186C808E0FE264C64B1DD2A5A4FE"
        ),
        target_size=1_557_915,
        target_sha256=(
            "A18DEBDDEF9A4262C59A5B57A08D1AC0F13B0AEFB56C7D6763EB1302FA5D363F"
        ),
        expected_literals=(
            "조금이나마 참고가 된다면 다행",
            "\n잊지 않도록 이 안을 건의해 두겠사오니\n필요하시다면",
            "참조해",
        ),
        expected_gaps_hex=(
            "",
            "01432C020000",
            "01438A040000",
            "014396010000050505",
        ),
        target_literals=(
            "조금이나마 참고가 된다면 다행",
            "\n잊지 않도록 건의하여 두었으니\n필요할 때 ",
            "참조해 보시오.",
        ),
        target_gaps_hex=(
            "",
            "01432C020000",
            EMPTY_LITERAL.hex().upper(),
            (EMPTY_LITERAL + RETURN).hex().upper(),
        ),
        current_profile_render=(
            "조금이나마 참고가 된다면 다행이오\n"
            "잊지 않도록 건의하여 두었으니\n"
            "필요할 때 참조해 보시오."
        ),
    ),
    ResourceSpec(
        relative_path="MSG_PK/JP/msggame.bin",
        coordinate=(15, 2286),
        input_size=1_815_549,
        input_sha256=(
            "1D7F1FB2086419BD1FC928012F3E0E3D0BA2C600809513188A3FFBA455F63EFF"
        ),
        target_size=1_815_549,
        target_sha256=(
            "EC0353AD7823010722954D87EC751570EC3453AF30B536B2DF11E1C0F27DE799"
        ),
        expected_literals=(
            "조금이나마 참고가 된다면 다행",
            "\n잊지 않도록 이 안을 건의해 두겠사오니\n필요 시 ",
            "참조해",
        ),
        expected_gaps_hex=(
            "",
            "014338020000",
            "014396040000",
            "01439C010000050505",
        ),
        target_literals=(
            "조금이나마 참고가 된다면 다행",
            "\n잊지 않도록 건의해 두었으니\n필요할 때 ",
            "참조해 보시오.",
        ),
        target_gaps_hex=(
            "",
            "014338020000",
            EMPTY_LITERAL.hex().upper(),
            (EMPTY_LITERAL + RETURN).hex().upper(),
        ),
        current_profile_render=(
            "조금이나마 참고가 된다면 다행이오\n"
            "잊지 않도록 건의해 두었으니\n"
            "필요할 때 참조해 보시오."
        ),
    ),
)


class ProposalReferenceHotfixError(RuntimeError):
    """An exact input, bytecode, or output contract differed."""


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def record_map(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    archive = parse_packed_msggame(packed).archive
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def split_record(record: MsgGameRecord) -> tuple[tuple[str, ...], tuple[str, ...]]:
    literals = parse_record_literals(record)
    texts = tuple(literal.text for literal in literals)
    gaps: list[str] = []
    cursor = 0
    for literal in literals:
        gaps.append(record.data[cursor : literal.marker_offset].hex().upper())
        cursor = literal.marker_end
    gaps.append(record.data[cursor:].hex().upper())
    return texts, tuple(gaps)


def build_record(literals: tuple[str, ...], gaps_hex: tuple[str, ...]) -> bytes:
    if len(gaps_hex) != len(literals) + 1:
        raise ProposalReferenceHotfixError("record gap/literal arity differs")
    output = bytearray()
    for gap_hex, literal in zip(gaps_hex, literals):
        output.extend(bytes.fromhex(gap_hex))
        output.extend(LITERAL_START)
        output.extend(literal.encode("utf-16le"))
        output.extend(LITERAL_END)
    output.extend(bytes.fromhex(gaps_hex[-1]))
    return bytes(output)


def verify_input(root: Path) -> dict[str, dict[str, object]]:
    root = root.resolve(strict=True)
    profile: dict[str, dict[str, object]] = {}
    for spec in SPECS:
        path = root / spec.relative_path
        if not path.is_file():
            raise ProposalReferenceHotfixError(
                f"missing input resource: {spec.relative_path}"
            )
        size = path.stat().st_size
        digest = sha256_path(path)
        if size != spec.input_size or digest != spec.input_sha256:
            raise ProposalReferenceHotfixError(
                f"input profile differs for {spec.relative_path}: "
                f"size={size}, sha256={digest}"
            )
        source = path.read_bytes()
        record = record_map(source)[spec.coordinate]
        literals, gaps = split_record(record)
        if literals != spec.expected_literals or gaps != spec.expected_gaps_hex:
            raise ProposalReferenceHotfixError(
                f"record preimage differs at {spec.relative_path} {spec.coordinate}"
            )
        profile[spec.relative_path] = {"size": size, "sha256": digest}
    return profile


def patch_resource(source: bytes, spec: ResourceSpec) -> tuple[bytes, dict[str, object]]:
    records = record_map(source)
    before_record = records[spec.coordinate]
    before_literals, before_gaps = split_record(before_record)
    if (
        before_literals != spec.expected_literals
        or before_gaps != spec.expected_gaps_hex
    ):
        raise ProposalReferenceHotfixError(
            f"record preimage differs at {spec.relative_path} {spec.coordinate}"
        )

    after_record = build_record(spec.target_literals, spec.target_gaps_hex)
    if len(after_record) != len(before_record.data):
        raise ProposalReferenceHotfixError(
            f"record size changed at {spec.relative_path}: "
            f"{len(before_record.data)} -> {len(after_record)}"
        )
    candidate = rebuild_packed_msggame(
        source,
        {spec.coordinate: after_record},
    )
    if len(candidate) != spec.target_size:
        raise ProposalReferenceHotfixError(
            f"target size differs for {spec.relative_path}: {len(candidate)}"
        )
    target_digest = sha256_bytes(candidate)
    if not spec.target_sha256.startswith("TO_FILL") and target_digest != spec.target_sha256:
        raise ProposalReferenceHotfixError(
            f"target hash differs for {spec.relative_path}: {target_digest}"
        )

    checked = record_map(candidate)[spec.coordinate]
    target_texts, target_gaps = split_record(checked)
    expected_texts = (
        spec.target_literals[0],
        spec.target_literals[1],
        "",
        spec.target_literals[2],
        "",
    )
    expected_gaps = (
        "",
        spec.target_gaps_hex[1],
        "",
        "",
        "",
        "050505",
    )
    if target_texts != expected_texts or target_gaps != expected_gaps:
        raise ProposalReferenceHotfixError(
            f"target record structure differs at {spec.relative_path}"
        )
    if checked.data.count(b"\x01\x43") != 1:
        raise ProposalReferenceHotfixError(
            f"target record did not retain exactly one speech-style selector"
        )

    report = {
        "coordinate": f"{spec.coordinate[0]}:{spec.coordinate[1]}",
        "input_size": len(source),
        "input_sha256": sha256_bytes(source),
        "target_size": len(candidate),
        "target_sha256": target_digest,
        "before_record_size": len(before_record.data),
        "before_record_sha256": sha256_bytes(before_record.data),
        "before_record_hex": before_record.data.hex().upper(),
        "after_record_size": len(after_record),
        "after_record_sha256": sha256_bytes(after_record),
        "after_record_hex": after_record.hex().upper(),
        "retained_selector_count": 1,
        "removed_selector_count": 2,
        "current_profile_render": spec.current_profile_render,
    }
    return candidate, report


def prepare_candidate(input_root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    input_profile = verify_input(input_root)
    output: dict[str, bytes] = {}
    resources: dict[str, dict[str, object]] = {}
    for spec in SPECS:
        source = (input_root / spec.relative_path).read_bytes()
        candidate, detail = patch_resource(source, spec)
        output[spec.relative_path] = candidate
        resources[spec.relative_path] = detail
    report = {
        "schema": SCHEMA,
        "status": "PASS",
        "input_root": str(input_root.resolve()),
        "input_profile": input_profile,
        "changed_resources": [spec.relative_path for spec in SPECS],
        "resources": resources,
        "visible_regression": {
            "before": "필요 시 참조해저것",
            "after": "필요할 때 참조해 보시오.",
        },
        "policy": {
            "steam_write_supported": False,
            "release_packaging_supported": False,
            "output_root_restricted_to_private_tmp": True,
        },
    }
    return output, report


def require_private_output(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    checked = path.resolve(strict=False)
    try:
        checked.relative_to(root)
    except ValueError as exc:
        raise ProposalReferenceHotfixError(
            f"{label} escapes private tmp root: {checked}"
        ) from exc
    if checked == root:
        raise ProposalReferenceHotfixError(f"{label} cannot be the tmp root")
    return checked


def build_candidate(
    input_root: Path,
    output_root: Path,
    manifest_path: Path,
) -> dict[str, Any]:
    output_root = require_private_output(output_root, "output root")
    manifest_path = require_private_output(manifest_path, "manifest path")
    if output_root.exists():
        shutil.rmtree(output_root)
    output, report = prepare_candidate(input_root)
    for relative, payload in output.items():
        target = output_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_bytes(canonical_json(report))
    return report


def expected_overlay(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": OVERLAY_SCHEMA,
        "status": "PASS",
        "visible_regression": report["visible_regression"],
        "changed_resources": {
            relative: {
                key: detail[key]
                for key in (
                    "coordinate",
                    "input_size",
                    "input_sha256",
                    "target_size",
                    "target_sha256",
                    "before_record_size",
                    "before_record_sha256",
                    "after_record_size",
                    "after_record_sha256",
                    "retained_selector_count",
                    "removed_selector_count",
                    "current_profile_render",
                )
            }
            for relative, detail in report["resources"].items()
        },
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_binary": False,
            "steam_write_supported": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("verify-input", "build", "print-overlay"),
    )
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH)
    args = parser.parse_args()

    if args.command == "verify-input":
        print(json.dumps(verify_input(args.input_root), ensure_ascii=False, indent=2))
        return 0
    if args.command == "build":
        report = build_candidate(
            args.input_root,
            args.output_root,
            args.manifest,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    _output, report = prepare_candidate(args.input_root)
    print(json.dumps(expected_overlay(report), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
