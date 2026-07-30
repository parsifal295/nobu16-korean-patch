#!/usr/bin/env python3
"""Build the private W65 title-label correction overlay from W64.

W65 retains every W64 event reflow and changes only four static PK dialogue
literals.  The PC Japanese source is ``内府`` in each case; the existing
phonetic rendering ``나이후`` is corrected to the Korean historical office
title ``내대신``.  No runtime token, control byte, line break, font, Steam
file, Git state, network state, or public release is touched by this builder.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate"
W64_BUILDER = (
    REPO
    / "workstreams"
    / "pc_private_union_composite_wave64_v1"
    / "build_pc_private_union_composite_wave64_v1.py"
)


class Wave65Error(RuntimeError):
    """Raised when a pinned W64 input or W65 output contract drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave65Error(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise Wave65Error(f"cannot import module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


w64 = load_module("pc_private_union_wave64_for_wave65", W64_BUILDER)
w63 = w64.w63
w62 = w64.w62
w61 = w64.w61
w60 = w64.w60

BASE = w64.BASE
PK = w64.PK
MSGDATA = w64.MSGDATA
MSGEV = w64.MSGEV
ALL_RESOURCES = (BASE, PK, MSGDATA, MSGEV)


@dataclass(frozen=True)
class TitleTarget:
    coordinate: tuple[int, int, int]
    current_ko: str
    target_ko: str
    direct_pc_jp: str
    expected_widths_px: tuple[int, ...]
    rationale: str

    @property
    def coordinate_text(self) -> str:
        return ":".join(str(value) for value in self.coordinate)


@dataclass(frozen=True)
class Bundle:
    outputs: Mapping[str, bytes]
    profiles: Mapping[str, Any]
    title_effective: Mapping[tuple[int, int, int], str]
    title_classifications: Mapping[str, tuple[tuple[int, int, int], ...]]
    title_rows: tuple[Mapping[str, Any], ...]
    final_record_counts: Mapping[str, int]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


TITLE_TARGETS = (
    TitleTarget(
        (17, 274, 1),
        "나이후",
        "내대신",
        "内府",
        (144,),
        "도쿠가와 이에야스를 가리키는 内府는 음역이 아니라 관직명 내대신으로 표기한다.",
    ),
    TitleTarget(
        (17, 276, 1),
        "나이후",
        "내대신",
        "内府",
        (144,),
        "도쿠가와 이에야스를 가리키는 内府는 음역이 아니라 관직명 내대신으로 표기한다.",
    ),
    TitleTarget(
        (17, 357, 0),
        "나이후",
        "내대신",
        "内府",
        (144,),
        "도쿠가와 이에야스를 가리키는 内府는 음역이 아니라 관직명 내대신으로 표기한다.",
    ),
    TitleTarget(
        (17, 405, 1),
        "나이후",
        "내대신",
        "内府",
        (144,),
        "도쿠가와 이에야스를 가리키는 内府는 음역이 아니라 관직명 내대신으로 표기한다.",
    ),
)
EXPECTED_TARGET_COORDINATES = tuple(target.coordinate for target in TITLE_TARGETS)
EXPECTED_TITLE_CLASSES = {"fresh": 4, "already": 0, "override": 0}
EXPECTED_FINAL_RECORD_COUNTS = {BASE: 109, PK: 285, MSGDATA: 4, MSGEV: 196}
EXPECTED_FINAL_TOTAL_RECORDS = 594
EXPECTED_FINAL_PROFILE_DICTS: dict[str, dict[str, Any]] | None = {
    BASE: {
        "raw_sha256": "7DA010184830AC83600F6DC301BBF134D6F8CAC9A5CE3818BDB4A3246E2F4A63",
        "raw_size": 1498548,
        "sha256": "02C8B0F0A175B85BDE223355620124DF5DC07B20FE804D26212E10C307D7C099",
        "size": 1504450,
    },
    PK: {
        "raw_sha256": "6A724C42495DFC2D2584E9F071A1E54D69F6F26AB3219F6AD309A1FE47CCB36F",
        "raw_size": 1799448,
        "sha256": "322CE9D88461D8E0D7320FD4BB53FC890403F65C9E6C1BC23C91B73E0213CFB5",
        "size": 1806530,
    },
    MSGDATA: {
        "raw_sha256": "9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC",
        "raw_size": 495032,
        "sha256": "34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215",
        "size": 496999,
    },
    MSGEV: {
        "raw_sha256": "27A3D7FFFF43E3E805B5F5AF90F708E35710C6284EC4DFBA9D465C998C9BE94F",
        "raw_size": 990844,
        "sha256": "48E06CF0CA5CA39D261E376D35B9A96B4A91BB7EE52A188D5F1400354A6FFEA4",
        "size": 994755,
    },
}


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(value: Any) -> dict[str, Any]:
    return w62.profile_dict(value)


def require_private(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave65Error(f"private candidate escapes tmp root: {resolved}") from exc
    return resolved


def parse_msggame(blob: bytes, label: str) -> Any:
    return w63.parse_msggame(blob, label)


def literal_at(archive: Any, coordinate: tuple[int, int, int], label: str) -> str:
    return w61.literal_at(archive, coordinate, label)


def title_target_map() -> dict[tuple[int, int, int], TitleTarget]:
    mapped = {target.coordinate: target for target in TITLE_TARGETS}
    require(len(mapped) == len(TITLE_TARGETS), "duplicate W65 title target")
    require(tuple(mapped) == EXPECTED_TARGET_COORDINATES, "W65 title target order or scope drift")
    return mapped


def overlay_pk(
    w64_blob: bytes,
) -> tuple[
    bytes,
    dict[tuple[int, int, int], str],
    dict[str, tuple[tuple[int, int, int], ...]],
    tuple[Mapping[str, Any], ...],
]:
    before = parse_msggame(w64_blob, "W64 PK")
    direct_jp = w61.load_direct_jp(PK)
    font = w64.layout.load_font()
    effective: dict[tuple[int, int, int], str] = {}
    classes: dict[str, list[tuple[int, int, int]]] = {"fresh": [], "already": [], "override": []}
    rows: list[Mapping[str, Any]] = []
    for coordinate, target in title_target_map().items():
        current = literal_at(before, coordinate, "W64 PK")
        source_jp = literal_at(direct_jp, coordinate, "pristine PC JP PK")
        require(source_jp == target.direct_pc_jp, f"direct PC JP title witness drift: {coordinate}")
        require(
            w61.literal_signature(current) == w61.literal_signature(target.target_ko),
            f"manual LF/control drift: {coordinate}",
        )
        source_widths = w64.layout.line_widths(current, font)
        target_widths = w64.layout.line_widths(target.target_ko, font)
        require(source_widths == target.expected_widths_px, f"source width drift: {coordinate}: {source_widths}")
        require(target_widths == target.expected_widths_px, f"target width drift: {coordinate}: {target_widths}")
        if current == target.target_ko:
            classes["already"].append(coordinate)
        elif current == target.current_ko:
            classes["fresh"].append(coordinate)
            effective[coordinate] = target.target_ko
        else:
            classes["override"].append(coordinate)
        rows.append({
            "coordinate": target.coordinate_text,
            "w64_current_ko": current,
            "target_ko": target.target_ko,
            "direct_pc_jp": source_jp,
            "w64_current_ko_utf16le_sha256": text_hash(current),
            "target_ko_utf16le_sha256": text_hash(target.target_ko),
            "direct_pc_jp_utf16le_sha256": text_hash(source_jp),
            "source_line_widths_px": list(source_widths),
            "target_line_widths_px": list(target_widths),
            "literal_signature": {
                "manual_lf_count": w61.literal_signature(current)[0],
                "control_codepoints": list(w61.literal_signature(current)[1]),
            },
            "rationale": target.rationale,
        })
    frozen = {name: tuple(values) for name, values in classes.items()}
    require(
        {name: len(values) for name, values in frozen.items()} == EXPECTED_TITLE_CLASSES,
        f"W65 title classification drift: {frozen}",
    )
    output = w63.w59.rebuild_packed_with_literals(w64_blob, effective)
    after = parse_msggame(output, "W65 PK")
    w63.w59.assert_same_literal_topology_and_skeleton("W64-to-W65 PK", before, after)
    before_records = w63.w59.archive_records(before)
    after_records = w63.w59.archive_records(after)
    before_literals = w63.w59.literal_texts(before)
    after_literals = w63.w59.literal_texts(after)
    require(
        {coordinate for coordinate in before_literals if before_literals[coordinate] != after_literals[coordinate]} == set(effective),
        "W65 title literal scope drift",
    )
    require(
        {key for key in before_records if before_records[key].data != after_records[key].data}
        == {(block, record) for block, record, _literal in effective},
        "W65 title record scope drift",
    )
    return output, effective, frozen, tuple(rows)


def prepare(*, require_output_profiles: bool) -> Bundle:
    base = w64.prepare(require_output_profiles=True)
    w64.verify_private_candidate(base)
    pk_output, title_effective, title_classifications, title_rows = overlay_pk(base.outputs[PK])
    outputs = {
        BASE: base.outputs[BASE],
        PK: pk_output,
        MSGDATA: base.outputs[MSGDATA],
        MSGEV: base.outputs[MSGEV],
    }
    profiles = {resource: w61.profile(blob) for resource, blob in outputs.items()}
    w45 = w62.load_w45_backups()
    w45_pk = parse_msggame(w45[PK], "W45 PK")
    w64_pk = parse_msggame(base.outputs[PK], "W64 PK")
    w65_pk = parse_msggame(pk_output, "W65 PK")
    w45_literals = w63.w59.literal_texts(w45_pk)
    w64_literals = w63.w59.literal_texts(w64_pk)
    w65_literals = w63.w59.literal_texts(w65_pk)
    w64_changed = {coordinate for coordinate in w45_literals if w45_literals[coordinate] != w64_literals[coordinate]}
    w65_changed = {coordinate for coordinate in w45_literals if w45_literals[coordinate] != w65_literals[coordinate]}
    require(w64_changed.isdisjoint(title_effective), "W65 title correction overlaps W64 PK history")
    require(w65_changed == w64_changed | set(title_effective), "W65 W45 title retention drift")
    base_records, _base_literals = w60.msggame_counts(w45[BASE], outputs[BASE])
    pk_records, _pk_literals = w60.msggame_counts(w45[PK], outputs[PK])
    final_counts = {
        BASE: base_records,
        PK: pk_records,
        MSGDATA: 4,
        MSGEV: w60.event_count(w45[MSGEV], outputs[MSGEV]),
    }
    if require_output_profiles:
        require(EXPECTED_FINAL_PROFILE_DICTS is not None, "W65 output profile constants are not pinned")
        require(
            {resource: profile_dict(profile) for resource, profile in profiles.items()} == EXPECTED_FINAL_PROFILE_DICTS,
            "W65 output profile drift",
        )
        require(final_counts == EXPECTED_FINAL_RECORD_COUNTS, "W65 final record count drift")
        require(sum(final_counts.values()) == EXPECTED_FINAL_TOTAL_RECORDS, "W65 final total drift")
    audit = {
        "schema": "nobu16.kr.pc-private-union-composite-wave65-audit.v1",
        "candidate_only": True,
        "source_policy": {
            "platform": "W64 Steam-PC Korean candidate and pristine PC Japanese only",
            "switch_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "base_w64": {resource: profile_dict(w61.profile(base.outputs[resource])) for resource in ALL_RESOURCES},
        "direct_pc_jp_resource": PK,
        "approved_title_coordinates": [target.coordinate_text for target in TITLE_TARGETS],
        "title_rows": list(title_rows),
        "w45_to_w64_changed_pk_literal_coordinates": [":".join(str(value) for value in coordinate) for coordinate in sorted(w64_changed)],
        "w64_to_w65_changed_pk_literal_coordinates": [":".join(str(value) for value in coordinate) for coordinate in sorted(title_effective)],
        "w45_to_w65_changed_pk_literal_coordinates": [":".join(str(value) for value in coordinate) for coordinate in sorted(w65_changed)],
        "w64_w65_pk_literal_overlap_coordinates": [":".join(str(value) for value in coordinate) for coordinate in sorted(w64_changed & set(title_effective))],
        "final_record_counts": final_counts,
        "final_total_records": sum(final_counts.values()),
        "outputs": {resource: profile_dict(profiles[resource]) for resource in ALL_RESOURCES},
    }
    audit["title_classifications"] = {
        name: [":".join(str(value) for value in coordinate) for coordinate in values]
        for name, values in title_classifications.items()
    }
    manifest = {
        "schema": "nobu16.kr.pc-private-union-composite-wave65-manifest.v1",
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "relative": resource,
                "output": profile_dict(profiles[resource]),
                "changed_record_count": final_counts[resource],
            }
            for resource in ALL_RESOURCES
        },
        "final_total_records": sum(final_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }
    return Bundle(
        outputs,
        profiles,
        title_effective,
        title_classifications,
        title_rows,
        final_counts,
        audit,
        manifest,
    )


def write_candidate(bundle: Bundle) -> Path:
    output = require_private(CANDIDATE_ROOT)
    require(not output.exists(), f"W65 candidate already exists: {output}")
    staging = require_private(TMP_ROOT / ".candidate.staging")
    require(not staging.exists(), f"W65 candidate staging already exists: {staging}")
    staging.mkdir(parents=True)
    try:
        for relative, blob in bundle.outputs.items():
            path = staging / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blob)
        (staging / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (staging / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return output


def verify_private_candidate(bundle: Bundle | None = None) -> dict[str, Any]:
    bundle = bundle or prepare(require_output_profiles=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), f"W65 candidate missing: {root}")
    expected_files = {"audit.v1.json", "candidate_manifest.v1.json", *ALL_RESOURCES}
    actual_files = {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"W65 candidate file scope drift: {sorted(actual_files)}")
    for relative, blob in bundle.outputs.items():
        require((root / relative).read_bytes() == blob, f"W65 candidate differs: {relative}")
    require((root / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "W65 audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "W65 manifest differs")
    return {
        "candidate_root": root.relative_to(REPO).as_posix(),
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "build_pc_private_union_composite_wave65_v1.py",
        WORKSTREAM / "test_pc_private_union_composite_wave65_v1.py",
        WORKSTREAM / "README_KO.md",
    ):
        require(path.is_file(), f"W65 authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"W65 trailing whitespace: {path.name}:{number}")


def command_profile() -> int:
    bundle = prepare(require_output_profiles=False)
    print(json.dumps({
        "profiles": {resource: profile_dict(value) for resource, value in bundle.profiles.items()},
        "title_classifications": {
            name: [":".join(str(value) for value in coordinate) for coordinate in values]
            for name, values in bundle.title_classifications.items()
        },
        "approved_title_coordinates": [target.coordinate_text for target in TITLE_TARGETS],
        "final_record_counts": bundle.final_record_counts,
        "final_total_records": sum(bundle.final_record_counts.values()),
    }, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        return command_profile()
    if command == "build":
        bundle = prepare(require_output_profiles=True)
        write_candidate(bundle)
        print(json.dumps(verify_private_candidate(bundle), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if command == "verify-private":
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    bundle = prepare(require_output_profiles=True)
    source_whitespace_check()
    result = verify_private_candidate(bundle)
    result["private_authoring_whitespace_check"] = "passed"
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
