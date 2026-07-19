#!/usr/bin/env python3
"""Build a private PC-only static dialogue correction candidate for Wave 32.

This workstream repairs sixteen remaining PK dialogue records whose equivalent
PC Base Japanese records already have a verified Korean correction.  Korean
targets are declared below; semantic evidence is PC JP/EN/SC/TC only.  The
builder never writes a Steam resource, stages Git, uses a network, or releases.
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
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_PATH = STEAM_ROOT / RESOURCE
W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave32-static-remainder.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave32-static-remainder-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave32-static-remainder-manifest.v1"
MAX_LINES = 3
MAX_LINE_PX = 912

INPUT_SIZE = 1_806_542
INPUT_SHA256 = "0BDE96CF07C97B0FF71EBB5C2032E62F313BA271BD772D5BC79A48E57356A0F9"
TARGET_SIZE = 1_806_498
TARGET_SHA256 = "37644F37ABDB03B16BA6D722C03A9BB4F899F7A684665F3DB55501E46180AA14"
TARGET_RAW_SIZE = 1_799_416
TARGET_RAW_SHA256 = "2ABF271A08660062468AEED9C743215A06F77B052F87B88FF955FA675C6A7F1A"

PC_SOURCES = {
    "BASE_JP": (
        Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    ),
    "PK_JP": (
        STEAM_ROOT
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msggame.bin",
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    ),
    "EN": (
        STEAM_ROOT / "MSG_PK" / "EN" / "msggame.bin",
        "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    ),
    "SC": (
        STEAM_ROOT / "MSG_PK" / "SC" / "msggame.bin",
        "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    ),
    "TC": (
        STEAM_ROOT / "MSG_PK" / "TC" / "msggame.bin",
        "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
    ),
}


class Wave32Error(RuntimeError):
    """Raised when a pinned input, source anchor, or candidate contract drifts."""


@dataclass(frozen=True)
class Change:
    name: str
    base_coordinate: tuple[int, int]
    pk_coordinate: tuple[int, int]
    target_literals: tuple[str, ...]
    current_record_sha256: str
    target_record_sha256: str
    target_record_size: int
    target_line_widths_px: tuple[int, ...]
    rationale: str


@dataclass(frozen=True)
class CandidateBundle:
    packed: bytes
    raw: bytes
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


# These Korean texts are project-authored targets.  PC JP/EN/SC/TC source text
# is never embedded or emitted by this workstream.
CHANGES = (
    Change(
        "troop_count_negation",
        (7, 2436),
        (7, 2482),
        ("라면\n병사가 어느 정도 필요한지 판단할 수 없", "\n직접 지시를"),
        "99D3A817A970E1FC6C0C86B0DDCA93AA5C153669C07B2FB9FAF3B51F6C020782",
        "8FB13B899D090DA206797C9BA292D05878F9CACA0FA8D4BEDE7382D77E75209E",
        79,
        (96, 912, 264),
        "필요 병력을 스스로 판단할 수 없다는 부정 의미를 복구한다.",
    ),
    Change(
        "diplomacy_negation",
        (15, 2249),
        (15, 2279),
        ("외교 관계상, 지금은 어느 인접 세력에도\n침공할 수 없어",),
        "AF56A4373BEC7CD2008AB5C555FD97CA9F4B2674BCE8F904EB57390DA680C0FB",
        "3E65F2CE97DD4CB0E403ED77181B7C0499331F11F7232B4E070CC5DB2D1C7145",
        71,
        (912, 336),
        "외교 관계로 침공할 수 없다는 부정 의미를 복구한다.",
    ),
    Change(
        "return_alive_surprise",
        (7, 399),
        (7, 403),
        ("살아서 돌아갈 수 있을 줄이야",),
        "0764C77A163AE285CB97F45D72D5B62394C2E4A2063196761F4794D1585AB590",
        "AD9C6170C546B73BB360D52C18BD630D2238699ED7B2CCAF7A1C18B230C1AE5A",
        41,
        (672,),
        "살아 돌아온 사실에 대한 놀람으로 화자 의미를 바로잡는다.",
    ),
    Change(
        "castle_fall_01",
        (7, 2135),
        (7, 2177),
        ("후원군이 닿기 전에\n함락해 버리는 게다",),
        "14AF6820F1B54698613B38917AF9143B55D3F442ABA9E61E5CD53D1E05FCE85A",
        "0D555470E3990D5DF6FE4DEE5F0EC81CF71D9FDE91E72BE2E4B1589B7DF8E5E3",
        51,
        (432, 432),
        "성 점령 전투 문맥에 맞춰 함락 용어를 쓴다.",
    ),
    Change(
        "castle_fall_02",
        (7, 2138),
        (7, 2180),
        ("후원군이 도착하기 전에\n함락하면 됩니다",),
        "FF596F22B00C8E04AD0969D1FCE737F8E4F7E3023EE1887FABE45394D4DDCBC6",
        "0C77B248E392B546C1D379035A6CD0154F50AF037E8487E214D2B1EDAFA43C5F",
        51,
        (528, 360),
        "성 점령 전투 문맥에 맞춰 함락 용어를 쓴다.",
    ),
    Change(
        "castle_fall_03",
        (7, 2140),
        (7, 2182),
        ("적이 다가오기 전에\n성을 함락하면 된다!",),
        "5C116FD4B5A4540FD8153F7E505115D5C4704A12B1DCD7D979E7DDD3D2CCD33E",
        "2FFF03791058915F583A27EA80A9CFD2207C76B2BD62D3CD3406735FD777D690",
        53,
        (432, 456),
        "성 점령 전투 문맥에 맞춰 함락 용어를 쓴다.",
    ),
    Change(
        "castle_fall_04",
        (7, 2144),
        (7, 2186),
        ("후원군이라니 성가시다\n성을 서둘러 함락해야 한다",),
        "A1AD5A429A24EAF5A4E06B0C51B2E270A9B3F1C5F3BD06944746C3AEAD835BEC",
        "EB28F530E1AFD6659A594F7AFE09D6EA0C6E4ABF1D2ECBCEEC1FAF1226346FDC",
        61,
        (504, 600),
        "성 점령 전투 문맥에 맞춰 함락 용어를 쓴다.",
    ),
    Change(
        "castle_fall_05",
        (7, 2147),
        (7, 2189),
        ("후원군이 오기 전에\n성을 함락하고 싶구나",),
        "4BB965F015435459CCB44F26CD7D24DA5F9C7B32B897106927C7DD6F1DAA9275",
        "DC2E1E7C5FBF943238662DB589D685BE8218CF06A90C66EF89BF1564038F76AA",
        53,
        (432, 480),
        "성 점령 전투 문맥에 맞춰 함락 용어를 쓴다.",
    ),
    Change(
        "castle_fall_06",
        (7, 2150),
        (7, 2192),
        ("적의 원군?\n어서 성을 함락합시다",),
        "46BAE366EFA79924A8202276F3E1ABFF22C64A04BCD73BB93ECA28A5B7F0CF1C",
        "6152DA11A5513534A95FAD69C70AFBF6DFD87F3816F783B4FB7557F2309D0DEC",
        45,
        (240, 480),
        "성 점령 전투 문맥에 맞춰 함락 용어를 쓴다.",
    ),
    Change(
        "castle_fall_07",
        (7, 2151),
        (7, 2193),
        ("후원군이라고?\n도착 전에 함락하자!",),
        "F6D084A0398D5A10A68AF79B3D164CBEFC026B51CF3EA5C728489A334B08B91E",
        "3D4C75823F0F759A63DBDB5EEB26CC6B6EB628A4B4A3DA402307EBD170C617CD",
        47,
        (312, 456),
        "성 점령 전투 문맥에 맞춰 함락 용어를 쓴다.",
    ),
    Change(
        "castle_fall_08",
        (7, 2170),
        (7, 2212),
        ("이런 작은 성쯤은\n금방 함락해 보이겠습니다",),
        "0BBF8FD4AA3A7AE3D241D6C068A32F3C3F59224785578C8D105B70C3C35DE83C",
        "267512D47CEAD7E886184658F79D596243EA2F9879800D6BB12F03A9BFE72FF8",
        55,
        (384, 576),
        "성 점령 전투 문맥에 맞춰 함락 용어를 쓴다.",
    ),
    Change(
        "castle_fall_09",
        (7, 2181),
        (7, 2223),
        ("포위보다 강공이\n더 빨리 함락하리라",),
        "A538B0C4F70179E0828033AE0C16F034FDF86056B19D1207B01A1A6F07380BF3",
        "1542DC02FD7795CB237DCB3C4D53B846D09B9190218B4C2CEFDEFEA2FC5CAAF5",
        47,
        (360, 432),
        "성 점령 전투 문맥에 맞춰 함락 용어를 쓴다.",
    ),
    Change(
        "castle_fall_10",
        (7, 2193),
        (7, 2235),
        ("이 성, 힘으로 밀어붙이는 편이\n빨리 함락할 수 있다고 봤다",),
        "E9D1D8B01D58CE26934C5061E266A1BF76CA9554BBCE903E41BF9CFFF0B55B14",
        "4126C9D906BD9934799A8CA7C426B1EA8229E623BA2ADCA8F5E99C37A7DCE403",
        75,
        (696, 624),
        "성 점령 전투 문맥에 맞춰 함락 용어를 쓴다.",
    ),
    Change(
        "castle_fall_11",
        (7, 2203),
        (7, 2245),
        ("후원군 병력도 대기하고 있다\n강공으로 함락해야 한다!",),
        "AA531421EF1ED88B981666A53D80353AD66C7BFC6B4D881EE390BD49B351CA9B",
        "EDF2393756041976915188771B46DCB9105422A5D0BE4BCD8313F34DD2ACE8B7",
        67,
        (648, 552),
        "성 점령 전투 문맥에 맞춰 함락 용어를 쓴다.",
    ),
    Change(
        "castle_fall_12",
        (7, 2277),
        (7, 2319),
        ("포위는 완료되었다\n성을 함락하면 끝이다",),
        "1D777D59B6133D57C3DD6946CFF9298851C832E2F0AAEFDA04B0AABF29295B49",
        "03F1CD76AEFAB30DE9742ABFDEADCFA8446C2A561E32448DE687629948A948A2",
        51,
        (408, 480),
        "성 점령 전투 문맥에 맞춰 함락 용어를 쓴다.",
    ),
    Change(
        "strategic_point_capture",
        (9, 3662),
        (9, 3934),
        ("전력은 호각이라 할 수 있겠습니다\n요지를 제압해 적의 사기를 떨어뜨리면\n승리가 보일 것입니다",),
        "3E1A61F82223D79795B86C9B5196C9CF555CC3911309F4F58962F759DA720ED1",
        "76E1289170BBF6554BA548FBEE2F83968DD92FE775C18DF8D3D96BC3D0538015",
        111,
        (768, 864, 480),
        "성 함락과 다른 요지 제압 의미를 분리한다.",
    ),
)

if len(CHANGES) != 16 or len({change.pk_coordinate for change in CHANGES}) != len(CHANGES):
    raise RuntimeError("Wave 32 must contain exactly sixteen unique PK records")


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave32Error(label)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def reject_switch(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    if any(part.casefold() == "switch" or "switch" in part.casefold() for part in resolved.parts):
        raise Wave32Error(f"Nintendo Switch path is forbidden: {label}")
    return resolved


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave32Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def load_w27() -> Any:
    if not W27_HELPER.is_file() or sha256_path(W27_HELPER) != W27_HELPER_SHA256:
        raise Wave32Error("pinned static-dialogue helper differs")
    spec = importlib.util.spec_from_file_location("wave32_static_dialogue_helper", W27_HELPER)
    if spec is None or spec.loader is None:
        raise Wave32Error("cannot load pinned static-dialogue helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()


def load_source_records() -> tuple[dict[str, Mapping[tuple[int, int], Any]], dict[str, str]]:
    records: dict[str, Mapping[tuple[int, int], Any]] = {}
    hashes: dict[str, str] = {}
    for language, (path, expected_hash) in PC_SOURCES.items():
        checked = reject_switch(path, f"PC {language} source")
        actual_hash = sha256_path(checked)
        require(actual_hash == expected_hash, f"PC {language} source profile differs")
        records[language] = W27.records_by_coordinate(checked.read_bytes())
        hashes[language] = actual_hash
    return records, hashes


def validate_source_anchor(change: Change, sources: Mapping[str, Mapping[tuple[int, int], Any]]) -> dict[str, Any]:
    base = sources["BASE_JP"].get(change.base_coordinate)
    pk = sources["PK_JP"].get(change.pk_coordinate)
    require(base is not None and pk is not None, f"{change.name} Japanese source record is absent")
    base_literals = W27.literal_texts(base)
    pk_literals = W27.literal_texts(pk)
    require(base_literals and pk_literals and base_literals[0] == pk_literals[0], f"{change.name} Base/PK Japanese anchor differs")
    contexts: dict[str, Any] = {}
    for language in ("EN", "SC", "TC"):
        record = sources[language].get(change.pk_coordinate)
        require(record is not None and W27.literal_texts(record), f"{change.name} PC {language} context is absent")
        contexts[language] = {
            "record_sha256": W27.sha256_bytes(record.data),
            "first_literal_utf16le_sha256": sha256_bytes(W27.literal_texts(record)[0].encode("utf-16le")),
        }
    return {
        "base_coordinate": f"{change.base_coordinate[0]}:{change.base_coordinate[1]}",
        "pk_coordinate": f"{change.pk_coordinate[0]}:{change.pk_coordinate[1]}",
        "base_jp_first_literal_utf16le_sha256": sha256_bytes(base_literals[0].encode("utf-16le")),
        "pk_jp_first_literal_utf16le_sha256": sha256_bytes(pk_literals[0].encode("utf-16le")),
        "pc_contexts": contexts,
    }


def validate_change(change: Change, before: Any, advance: Any) -> tuple[bytes, dict[str, Any]]:
    require(W27.sha256_bytes(before.data) == change.current_record_sha256, f"{change.name} current record differs")
    require(W27.literal_texts(before) != change.target_literals, f"{change.name} is already applied")
    require(len(W27.literal_texts(before)) == len(change.target_literals), f"{change.name} literal boundary differs")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"{change.name} record terminator differs")
    current_text = "".join(W27.literal_texts(before))
    target_text = "".join(change.target_literals)
    require(current_text.count("\n") == target_text.count("\n"), f"{change.name} manual line count differs")
    layout = W27.line_layout(change.target_literals, advance)
    require(tuple(layout["line_widths_px"]) == change.target_line_widths_px, f"{change.name} line widths differ")
    require(layout["line_count"] <= MAX_LINES and layout["max_width_px"] <= MAX_LINE_PX, f"{change.name} exceeds dialogue layout")
    require(not layout["wide_fallback_codepoints"], f"{change.name} uses a fallback glyph")
    rebuilt = W27.rebuild_static_record(before, change.target_literals)
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.sha256_bytes(after.data) == change.target_record_sha256, f"{change.name} target record differs")
    require(len(after.data) == change.target_record_size, f"{change.name} target record size differs")
    require(W27.literal_texts(after) == change.target_literals, f"{change.name} target literals differ")
    require(W27.opaque_spans(after) == W27.stripped_opaque_spans(before), f"{change.name} opaque bytecode differs")
    require(not W27.complete_0143_commands(W27.opaque_spans(after)), f"{change.name} static inflection command remains")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"{change.name} literal markers differ")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"{change.name} target terminator differs")
    return rebuilt, {
        "name": change.name,
        "pk_coordinate": f"{change.pk_coordinate[0]}:{change.pk_coordinate[1]}",
        "current_record_sha256": change.current_record_sha256,
        "target_record_sha256": change.target_record_sha256,
        "target_record_size": change.target_record_size,
        "target_line_widths_px": list(change.target_line_widths_px),
        "rationale": change.rationale,
        "removed_static_0143_command_count": len(W27.complete_0143_commands(W27.opaque_spans(before))),
    }


def prepare_candidate() -> CandidateBundle:
    input_path = reject_switch(RESOURCE_PATH, "current Steam PK dialogue")
    packed = input_path.read_bytes()
    require(len(packed) == INPUT_SIZE and sha256_bytes(packed) == INPUT_SHA256, "current Steam PK dialogue profile differs")
    W27.validate_raw_roundtrip(packed, "current Steam PK dialogue")
    current = W27.records_by_coordinate(packed)
    sources, source_hashes = load_source_records()
    advance, font = W27.load_font_advance()
    replacements: dict[tuple[int, int], bytes] = {}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        require(change.pk_coordinate not in replacements, f"duplicate PK coordinate: {change.name}")
        source = validate_source_anchor(change, sources)
        before = current.get(change.pk_coordinate)
        require(before is not None, f"current PK coordinate absent: {change.name}")
        replacement, row = validate_change(change, before, advance)
        replacements[change.pk_coordinate] = replacement
        row["pc_source_anchor"] = source
        rows.append(row)
    candidate = W27.rebuild_packed_msggame(packed, replacements)
    require(len(candidate) == TARGET_SIZE and sha256_bytes(candidate) == TARGET_SHA256, "target PK dialogue profile differs")
    W27.validate_raw_roundtrip(candidate, "Wave 32 private PK dialogue candidate")
    _header, raw = W27.decompress_wrapper(candidate)
    require(len(raw) == TARGET_RAW_SIZE and sha256_bytes(raw) == TARGET_RAW_SHA256, "target PK dialogue raw profile differs")
    after = W27.records_by_coordinate(candidate)
    changed = {coordinate for coordinate in current if current[coordinate].data != after[coordinate].data}
    expected = {change.pk_coordinate for change in CHANGES}
    require(set(current) == set(after) and changed == expected, "changed PK record scope differs")
    for change in CHANGES:
        record = after[change.pk_coordinate]
        require(W27.sha256_bytes(record.data) == change.target_record_sha256, f"output record differs: {change.name}")
        require(W27.literal_texts(record) == change.target_literals, f"output literals differ: {change.name}")
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "pc_jp_en_sc_tc_only": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
            "steam_transaction_capability": "absent",
            "git_operation": "absent",
            "network_operation": "absent",
            "release_operation": "absent",
        },
        "input": {"resource": RESOURCE, "size": INPUT_SIZE, "sha256": INPUT_SHA256},
        "target": {"resource": RESOURCE, "size": TARGET_SIZE, "sha256": TARGET_SHA256, "raw_size": TARGET_RAW_SIZE, "raw_sha256": TARGET_RAW_SHA256},
        "pc_source_packed_sha256": source_hashes,
        "font": font,
        "records": rows,
        "changed_record_count": len(rows),
        "changed_literal_count": sum(len(change.target_literals) for change in CHANGES),
    }
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {RESOURCE: {"input": {"size": INPUT_SIZE, "sha256": INPUT_SHA256}, "output": {"size": TARGET_SIZE, "sha256": TARGET_SHA256}, "changed_coordinates": [f"{change.pk_coordinate[0]}:{change.pk_coordinate[1]}" for change in CHANGES]}},
        "changed_record_count": len(CHANGES),
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "switch_korean_input": "forbidden",
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(candidate, raw, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    require_private(TMP_ROOT, "tmp root")
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        resource = stage / RESOURCE
        resource.parent.mkdir(parents=True, exist_ok=True)
        resource.write_bytes(bundle.packed)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "build_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        if output.exists():
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def verify_private() -> dict[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    resource = output / RESOURCE
    require(resource.is_file() and resource.read_bytes() == bundle.packed, "private candidate PK dialogue differs")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "build_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": len(CHANGES), "steam_game_resource_written": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private"))
    args = parser.parse_args(argv)
    if args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        print(json.dumps({"candidate_root": output.relative_to(REPO).as_posix(), "changed_record_count": len(CHANGES), "steam_game_resource_written": False}, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(json.dumps(verify_private(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
