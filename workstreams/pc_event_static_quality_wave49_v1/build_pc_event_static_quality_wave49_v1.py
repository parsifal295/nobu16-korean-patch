#!/usr/bin/env python3
"""Build a private-only, static-safe Steam PC event candidate for Wave 49.

The candidate starts from the already-applied W45 Korean PK event table and
contains only the 33 audited edits whose manual line breaks, control tokens,
and tag topology remain unchanged.  It cannot apply files to Steam, run a
transaction, use Git, contact a network service, or create a release.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TOOLS = REPO / "tools"
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_DIRNAME = "candidate"
STEAM_PK_EVENT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgev.bin")
LEGACY_PC_JP_EVENT = Path(
    r"F:\Games\NOBU16\KR_PATCH_BACKUP\file_only_transaction"
    r"\jp-runtime-wave05-20260715-v1\originals\MSG_PK\JP\msgev.bin"
)
STEAM_JP_MAPPING = (
    REPO
    / "workstreams"
    / "steam_jp_common_messages_v1"
    / "public"
    / "msgev_ko_steam_jp_native.v1.json"
)
WIDTH_UTILITY = (
    REPO
    / "workstreams"
    / "pc_event_quality_wave31_static_v1"
    / "build_pc_event_quality_wave31_static_v1.py"
)

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-static-quality-wave49.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-event-static-quality-wave49-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-event-static-quality-wave49-manifest.v1"
PK_MAX_LINE_PX = 912
INPUT_RECORD_COUNT = 17_916
LEGACY_JP_RECORD_COUNT = 17_910
WIDTH_UTILITY_SHA256 = "71F88ECA04D74BEB2A31B56A27889E6B59FF217A673582AF0FE0AFAB15390A7A"
STEAM_JP_MAPPING_SHA256 = "47742330C4375A6BB6AC19ED0F7E8040CF57E22EF39BEDEE7FF4959520B1575C"
RECORD_BINDING_SHA256 = "67A9FD94D8DC6F9B1F486496AA5A4AB19DDBEB834CE9A897AB8292F11698975E"


class Wave49Error(RuntimeError):
    """Raised when a pinned input, source record, or private output drifts."""


@dataclass(frozen=True)
class Profile:
    size: int
    sha256: str
    raw_size: int
    raw_sha256: str


@dataclass(frozen=True)
class Change:
    entry_id: int
    legacy_jp_id: int
    replacements: tuple[tuple[str, str, int], ...]
    pc_jp_anchors: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class TableResource:
    packed: bytes
    header: Any
    raw: bytes
    table: Any


@dataclass(frozen=True)
class CandidateBundle:
    packed: bytes
    raw: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


W45_INPUT_PROFILE = Profile(
    994_739,
    "01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE",
    990_828,
    "F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC",
)
W49_OUTPUT_PROFILE = Profile(
    994_751,
    "AC9C0F7FE72ADA6FA4604C1359A3FFA155BB5C166A590C3FC77BAD7C390CC90B",
    990_840,
    "F43E2742C8D9CDAA59861C5FC9011C68C3807641D97AFDAF46AFE2521BB9AA86",
)
LEGACY_PC_JP_PROFILE = Profile(
    555_784,
    "03426B59D32EB628021DE43BC02FF82B56B04D97C25CE37F735630EA7C4E2002",
    890_428,
    "4A916CA6837C4F8FC2D8B6254ECBEF26339558D2DDFEBF5A1637F8426F5918DE",
)


# These are the only 33 content changes in this builder.  Each source anchor
# is checked against the pinned PC Japanese record after legacy->Steam mapping.
CHANGES = (
    Change(3240, 3240, (("의형", "처남", 1),), ("義兄",), "義兄 관계 호칭을 처남으로 정정"),
    Change(3897, 3897, (("오키쓰네", "오키츠네", 1),), ("興経",), "興経 / PC EN Okitsune 표기 통일"),
    Change(3949, 3949, (("이노에", "이노우에", 1),), ("井上",), "井上元兼 / PC EN Inoue 표기 정정"),
    Change(3951, 3951, (("이노에", "이노우에", 1),), ("井上",), "井上党 / PC EN Inoue 표기 정정"),
    Change(3953, 3953, (("이노에", "이노우에", 1),), ("井上",), "井上元兼 / PC EN Inoue 표기 정정"),
    Change(3954, 3954, (("이노에", "이노우에", 1),), ("井上",), "井上元兼 / PC EN Inoue 표기 정정"),
    Change(3957, 3957, (("이노에", "이노우에", 1),), ("井上",), "井上党 / PC EN Inoue 표기 정정"),
    Change(6235, 6235, (("의형", "처남", 1),), ("義兄",), "義兄 관계 호칭을 처남으로 정정"),
    Change(6343, 6343, (("시키산성", "시기산성", 1),), ("信貴山城",), "信貴山城 / PC EN Shigisan 표기 정정"),
    Change(6419, 6419, (("제 의형도", "제 매형도", 1),), ("義兄",), "私の義兄 관계 호칭을 매형으로 정정"),
    Change(6724, 6724, (("고쓰키성", "고즈키성", 1),), ("上月城",), "上月城 / PC EN Kozuki 표기 정정"),
    Change(6863, 6863, (("닛신사이", "짓신사이", 1),), ("日新斎",), "日新斎 / PC EN Jisshinsai 표기 통일"),
    Change(6911, 6911, (("닛신사이", "짓신사이", 1),), ("日新斎",), "日新斎 / PC EN Jisshinsai 표기 통일"),
    Change(6913, 6913, (("닛신사이", "짓신사이", 1),), ("日新斎",), "日新斎 / PC EN Jisshinsai 표기 통일"),
    Change(6925, 6925, (("닛신사이", "짓신사이", 1),), ("日新斎",), "日新斎 / PC EN Jisshinsai 표기 통일"),
    Change(6929, 6929, (("닛신사이", "짓신사이", 1),), ("日新斎",), "日新斎 / PC EN Jisshinsai 표기 통일"),
    Change(7033, 7033, (("닛신사이", "짓신사이", 2),), ("日新斎",), "日新斎 / PC EN Jisshinsai 표기 통일(2회)"),
    Change(7332, 7332, (("마쓰주마루", "쇼주마루", 1),), ("松寿丸",), "松寿丸 / PC EN Shojumaru 표기 정정"),
    Change(
        7525,
        7525,
        (("두 사람은 의형제 사이가 되어 있었다.", "두 사람은 인척 관계였다.", 1),),
        ("義兄弟",),
        "義兄弟를 결의형제가 아닌 인척 관계로 정정",
    ),
    Change(7559, 7559, (("오후네", "오센", 1),), ("お船",), "お船 / PC EN Osen 및 현재 PC 표기 통일"),
    Change(7562, 7562, (("오후네", "오센", 1),), ("お船",), "お船 / PC EN Osen 및 현재 PC 표기 통일"),
    Change(7577, 7577, (("오후네", "오센", 1),), ("お船",), "お船 / PC EN Osen 및 현재 PC 표기 통일"),
    Change(7940, 7940, (("[bs754]", "[bs754]히데요시", 1),), ("秀吉",), "[bs754] 뒤 literal 秀吉 누락 복원"),
    Change(7985, 7985, (("[bs754]", "[bs754]히데요시", 1),), ("秀吉",), "[bs754] 뒤 literal 秀吉 누락 복원"),
    Change(8026, 8026, (("갚을", "갚은", 1),), ("主君の仇を討った",), "과거 완료 시제를 갚은으로 정정"),
    Change(8032, 8032, (("산포시", "산보시", 1),), ("三法師",), "三法師 / PC EN Sanboshi 표기 정정"),
    Change(8615, 8615, (("니로 구란도", "니이로 구란도", 1),), ("新納蔵人",), "新納蔵人 / PC EN Niiro 표기 정정"),
    Change(8626, 8626, (("니로 구란도", "니이로 구란도", 1),), ("新納蔵人",), "新納蔵人 / PC EN Niiro 표기 정정"),
    Change(9148, 9148, (("마스히데", "야스히데", 1),), ("賦秀",), "賦秀 / PC EN Yasuhide 표기 정정"),
    Change(
        9447,
        9447,
        (("요시히로 시게타네", "요시히로 시게타다", 1), ("요시히로 아키타네", "요시히로 아키타다", 1)),
        ("吉弘鎮理", "吉弘鑑理"),
        "吉弘鎮理·鑑理 / PC EN Shigetada·Akitada 표기 정정",
    ),
    Change(9470, 9470, (("도키 요리아키", "도키 요리노리", 1),), ("土岐頼芸",), "土岐頼芸 / PC EN Yorinori 표기 정정"),
    Change(9491, 9491, (("닛신사이", "짓신사이", 1),), ("日新斎",), "日新斎 / PC EN Jisshinsai 표기 통일"),
    Change(9540, 9540, (("아난히메", "오나미히메", 1),), ("阿南姫",), "阿南姫 / PC EN Onamihime 표기 정정"),
)


# These audited rows are deliberately absent.  They must not be silently
# promoted into this static bundle.
SEMANTIC_OR_REFLOW_HOLD = (
    3956,
    5273,
    5564,
    5654,
    5790,
    5794,
    5870,
    6408,
    6558,
    6584,
    6783,
    7236,
    7312,
    8162,
    8726,
    9340,
    9347,
    9423,
    9874,
    10595,
    10961,
    10963,
    10966,
    10967,
    11003,
)
TAG_INTERNAL_LINEBREAK_HOLD = (
    3202,
    3237,
    3477,
    3832,
    3896,
    3900,
    3919,
    3934,
    3960,
    4011,
    4020,
    4057,
    4140,
    4257,
    4323,
    4436,
    4726,
    4737,
    4792,
    4880,
    4895,
    5182,
    5297,
    5302,
    5817,
    5857,
    5884,
    6300,
    6396,
    6501,
    7735,
    7779,
    8138,
    8451,
    8510,
    8704,
    8723,
    9131,
    9137,
    9359,
    9795,
    9806,
    10045,
    10534,
    10800,
    10803,
)
COLOR_ESCAPE_QA_HOLD = (
    9887,
    9916,
    9998,
    10032,
    10274,
    10276,
    10288,
    10299,
    10325,
    10381,
    10386,
    10450,
    10483,
    10484,
    10499,
    10513,
    10566,
    10625,
    10630,
    10788,
    10815,
    10854,
    10934,
    10940,
    10943,
)
NON_EVENT_PERSON_NAME_HOLD = (291, 292, 293)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave49Error(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(profile: Profile) -> dict[str, Any]:
    return {
        "size": profile.size,
        "sha256": profile.sha256,
        "raw_size": profile.raw_size,
        "raw_sha256": profile.raw_sha256,
    }


def require_profile(packed: bytes, raw: bytes, profile: Profile, label: str) -> None:
    require(len(packed) == profile.size, f"{label} packed size differs")
    require(sha256_bytes(packed) == profile.sha256, f"{label} packed SHA-256 differs")
    require(len(raw) == profile.raw_size, f"{label} raw size differs")
    require(sha256_bytes(raw) == profile.raw_sha256, f"{label} raw SHA-256 differs")


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave49Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_width_utility() -> Any:
    require(WIDTH_UTILITY.is_file(), "width utility is absent")
    require(sha256_path(WIDTH_UTILITY) == WIDTH_UTILITY_SHA256, "width utility hash differs")
    spec = importlib.util.spec_from_file_location("wave49_width_utility", WIDTH_UTILITY)
    if spec is None or spec.loader is None:
        raise Wave49Error("cannot load width utility")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_table(
    path: Path,
    profile: Profile,
    record_count: int,
    label: str,
    *,
    require_packed_round_trip: bool,
) -> TableResource:
    require(path.is_file(), f"{label} is absent: {path}")
    packed = path.read_bytes()
    header, raw = decompress_wrapper(packed)
    require_profile(packed, raw, profile, label)
    table = parse_message_table(raw)
    require(len(table.texts) == record_count, f"{label} record count differs")
    require(rebuild_message_table(table, table.texts) == raw, f"{label} raw table round-trip differs")
    if require_packed_round_trip:
        require(recompress_wrapper(raw, header) == packed, f"{label} packed round-trip differs")
    return TableResource(packed, header, raw, table)


def load_legacy_to_steam_map() -> dict[int, int]:
    require(STEAM_JP_MAPPING.is_file(), "legacy->Steam mapping is absent")
    require(sha256_path(STEAM_JP_MAPPING) == STEAM_JP_MAPPING_SHA256, "legacy->Steam mapping hash differs")
    try:
        payload = json.loads(STEAM_JP_MAPPING.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Wave49Error("legacy->Steam mapping is invalid") from exc
    mapping: dict[int, int] = {}
    for block in payload["equal_hash_blocks"]:
        for offset in range(block["length"]):
            mapping[block["steam_start_id"] + offset] = block["legacy_start_id"] + offset
    for entry in payload["entries"]:
        mapping[entry["id"]] = entry["legacy_jp_id"]
    require(len(mapping) == 17_746, "legacy->Steam mapping entry count differs")
    return mapping


def derive_target(change: Change, before: str) -> str:
    target = before
    for old, new, expected_count in change.replacements:
        require(
            target.count(old) == expected_count,
            f"{change.entry_id} expected {expected_count} occurrence(s) of {old!r}",
        )
        target = target.replace(old, new)
    return target


def hold_sets() -> dict[str, list[int]]:
    return {
        "semantic_or_reflow": list(SEMANTIC_OR_REFLOW_HOLD),
        "tag_internal_linebreak": list(TAG_INTERNAL_LINEBREAK_HOLD),
        "color_escape_real_game_qa": list(COLOR_ESCAPE_QA_HOLD),
        "non_event_person_name": list(NON_EVENT_PERSON_NAME_HOLD),
    }


def prepare_candidate() -> CandidateBundle:
    width = load_width_utility()
    current = load_table(
        STEAM_PK_EVENT,
        W45_INPUT_PROFILE,
        INPUT_RECORD_COUNT,
        "W45 Steam PK input",
        require_packed_round_trip=True,
    )
    pc_jp = load_table(
        LEGACY_PC_JP_EVENT,
        LEGACY_PC_JP_PROFILE,
        LEGACY_JP_RECORD_COUNT,
        "legacy PC JP evidence",
        require_packed_round_trip=False,
    )
    mapping = load_legacy_to_steam_map()
    advance, font = width.load_event_font()
    targets = list(current.table.texts)
    records: list[dict[str, Any]] = []

    change_ids = [change.entry_id for change in CHANGES]
    require(len(CHANGES) == 33, "static change count differs")
    require(len(set(change_ids)) == len(change_ids), "duplicate static change ID")
    excluded_ids = set().union(*[set(values) for values in hold_sets().values()])
    require(not (set(change_ids) & excluded_ids), "held ID entered static candidate")

    for change in CHANGES:
        require(change.entry_id in mapping, f"{change.entry_id} has no legacy JP mapping")
        legacy_jp_id = mapping[change.entry_id]
        require(legacy_jp_id == change.legacy_jp_id, f"{change.entry_id} legacy JP coordinate differs")
        before = current.table.texts[change.entry_id]
        pc_jp_text = pc_jp.table.texts[legacy_jp_id]
        for anchor in change.pc_jp_anchors:
            require(anchor in pc_jp_text, f"{change.entry_id} lacks PC JP anchor {anchor!r}")
        target = derive_target(change, before)
        require(
            width.protected_signature(before) == width.protected_signature(target),
            f"{change.entry_id} changes runtime tokens, tags, or manual LF topology",
        )
        widths = width.line_widths(target, advance)
        require(1 <= len(widths) <= 3, f"{change.entry_id} line count is outside 1..3")
        require(max(widths) <= PK_MAX_LINE_PX, f"{change.entry_id} exceeds {PK_MAX_LINE_PX}px")
        targets[change.entry_id] = target
        records.append(
            {
                "id": change.entry_id,
                "legacy_jp_id": legacy_jp_id,
                "current_utf16le_sha256": text_hash(before),
                "target_utf16le_sha256": text_hash(target),
                "pc_jp_utf16le_sha256": text_hash(pc_jp_text),
                "target_line_widths_px": list(widths),
                "replacements": [
                    {"old": old, "new": new, "expected_count": expected_count}
                    for old, new, expected_count in change.replacements
                ],
                "pc_jp_anchors": list(change.pc_jp_anchors),
                "rationale": change.rationale,
            }
        )

    record_binding = [
        {
            key: record[key]
            for key in (
                "id",
                "legacy_jp_id",
                "current_utf16le_sha256",
                "target_utf16le_sha256",
                "pc_jp_utf16le_sha256",
                "target_line_widths_px",
                "replacements",
                "pc_jp_anchors",
            )
        }
        for record in records
    ]
    require(
        sha256_bytes(canonical_json(record_binding)) == RECORD_BINDING_SHA256,
        "per-record current/target/JP/width binding differs",
    )

    candidate_raw = rebuild_message_table(current.table, tuple(targets))
    candidate_packed = recompress_wrapper(candidate_raw, current.header)
    require_profile(candidate_packed, candidate_raw, W49_OUTPUT_PROFILE, "W49 candidate output")
    header, decoded = decompress_wrapper(candidate_packed)
    candidate_table = parse_message_table(decoded)
    require(rebuild_message_table(candidate_table, candidate_table.texts) == decoded, "candidate raw round-trip differs")
    require(recompress_wrapper(decoded, header) == candidate_packed, "candidate packed round-trip differs")
    changed_ids = [
        index
        for index, (before, after) in enumerate(zip(current.table.texts, candidate_table.texts))
        if before != after
    ]
    require(changed_ids == sorted(change_ids), "candidate changed ID scope differs")

    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "pc_jp_legacy_evidence_only": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_apply_or_transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "input": {
            "relative": "MSG_PK/JP/msgev.bin",
            **profile_dict(W45_INPUT_PROFILE),
        },
        "pc_jp_evidence": {
            "path": str(LEGACY_PC_JP_EVENT),
            **profile_dict(LEGACY_PC_JP_PROFILE),
            "legacy_to_steam_mapping_sha256": STEAM_JP_MAPPING_SHA256,
        },
        "font": dict(font),
        "pk_max_line_px": PK_MAX_LINE_PX,
        "record_binding_sha256": RECORD_BINDING_SHA256,
        "target": {
            "relative": "MSG_PK/JP/msgev.bin",
            **profile_dict(W49_OUTPUT_PROFILE),
        },
        "changed_record_count": len(CHANGES),
        "changed_ids": change_ids,
        "holds_excluded": hold_sets(),
        "records": records,
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resource": {
            "relative": "MSG_PK/JP/msgev.bin",
            "input": profile_dict(W45_INPUT_PROFILE),
            "output": profile_dict(W49_OUTPUT_PROFILE),
            "changed_ids": change_ids,
        },
        "changed_record_count": len(CHANGES),
        "record_binding_sha256": RECORD_BINDING_SHA256,
        "holds_excluded": hold_sets(),
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(candidate_packed, candidate_raw, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / CANDIDATE_DIRNAME, "candidate output")
    require(not output.exists(), f"candidate output already exists: {output}")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        resource_path = stage / "MSG_PK" / "JP" / "msgev.bin"
        resource_path.parent.mkdir(parents=True, exist_ok=True)
        resource_path.write_bytes(bundle.packed)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "candidate_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / CANDIDATE_DIRNAME, "candidate output")
    require(output.is_dir(), "private candidate is absent")
    expected_files = {
        "MSG_PK/JP/msgev.bin",
        "audit.v1.json",
        "candidate_manifest.v1.json",
    }
    actual_files = {
        path.relative_to(output).as_posix()
        for path in output.rglob("*")
        if path.is_file()
    }
    require(actual_files == expected_files, "private candidate file set differs")
    require(
        (output / "MSG_PK" / "JP" / "msgev.bin").read_bytes() == bundle.packed,
        "private event candidate differs",
    )
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require(
        (output / "candidate_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest),
        "private manifest differs",
    )
    return {
        "candidate_root": output.relative_to(REPO).as_posix(),
        "changed_record_count": len(CHANGES),
        "candidate_sha256": W49_OUTPUT_PROFILE.sha256,
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {
            "candidate_root": output.relative_to(REPO).as_posix(),
            "changed_record_count": len(CHANGES),
            "candidate_sha256": W49_OUTPUT_PROFILE.sha256,
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
