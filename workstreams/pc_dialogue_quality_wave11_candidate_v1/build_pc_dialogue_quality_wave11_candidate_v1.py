#!/usr/bin/env python3
"""Build the private PC-only Wave 11 terminology correction candidate.

Wave 11 corrects eight static PK msggame literal slots that rendered the
Japanese scenario-editor feature 国替 as 국가 변경 or 국체.  The feature changes
the placement of a clan, so the existing PC UI terminology 영지 변경 is used.

The builder consumes only the pinned Wave 9 private PK candidate and writes
only below this workstream's tmp directory.  It has no Steam writer, no
network operation, and never reads a Nintendo Switch Korean resource.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
MSGGAME_ROOT = REPO / "workstreams" / "msggame"
WAVE10_BUILDER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave10_candidate_v1"
    / "build_pc_dialogue_quality_wave10_candidate_v1.py"
)
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
WAVE9_INPUT_ROOT = (
    REPO / "tmp" / "pc_dialogue_runtime_wave9_candidate_v1" / "candidate-build-1"
)
DEFAULT_FONT_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_PK_JP_PATH = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP"
    r"\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals"
    r"\MSG_PK\JP\msggame.bin"
)
PK_EN_PATH = Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\EN\msggame.bin")

RESOURCE = "MSG_PK/JP/msggame.bin"
SCHEMA = "nobu16.kr.pc-dialogue-quality-wave11-candidate.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave11-audit.v1"
INPUT_SHA256 = "209B96CADE84D82810A8A79CA362DFA1B6665A8C601D3DB2C3DC0F96986E9930"
TARGET_SHA256 = "F4605CB25F7AEF97BFC9CB5444249E2420AD0639D44E7B903373C9B8B61D84A5"
PRISTINE_PK_JP_SHA256 = "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
PK_EN_SHA256 = "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916"
RECORD_TERMINATOR = b"\x05\x05\x05"
LITERAL_START = b"\x07\x07\x01"
LITERAL_END = b"\x07\x07\x02"
JP_FEATURE = "国替"
EN_FEATURE = "Switch Countries"


class Wave11Error(RuntimeError):
    """Raised when a source, format, or target contract changes."""


sys.path.insert(0, str(MSGGAME_ROOT))
from msggame_format import (  # noqa: E402
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_record_literals,
)


def load_wave10_metric() -> Any:
    if not WAVE10_BUILDER.is_file():
        raise Wave11Error(f"required PC font helper is absent: {WAVE10_BUILDER}")
    name = "_pc_dialogue_quality_wave11_wave10_metric"
    spec = importlib.util.spec_from_file_location(name, WAVE10_BUILDER)
    if spec is None or spec.loader is None:
        raise Wave11Error("cannot load the pinned PC font helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


WAVE10_METRIC = load_wave10_metric()


@dataclass(frozen=True)
class Change:
    block_id: int
    record_id: int
    literal_id: int
    current: str
    target: str
    input_record_sha256: str
    output_record_sha256: str
    input_opaque_spans_hex: tuple[str, ...]
    expected_record_line_widths_px: tuple[int, ...]

    @property
    def record_coordinate(self) -> tuple[int, int]:
        return (self.block_id, self.record_id)

    @property
    def literal_coordinate(self) -> tuple[int, int, int]:
        return (self.block_id, self.record_id, self.literal_id)

    @property
    def label(self) -> str:
        return f"{self.block_id}:{self.record_id}:{self.literal_id}"


CHANGES = (
    Change(
        3,
        57,
        0,
        "국가 변경 대상이 될 세력이 없습니다",
        "영지 변경 대상이 될 세력이 없습니다",
        "B0295F104393767219F8D98F84A275FA8EC9259A4831D21F76F58AFDF2B82960",
        "51D652FFB62F501B36D3A478AB47DBA15F453F0FE148696FD751374106AB39F2",
        ("", "050505"),
        (840,),
    ),
    Change(
        3,
        58,
        0,
        "모든 세력을 국가 변경 대상에서 제외",
        "모든 세력을 영지 변경 대상에서 제외",
        "1EA215EF5F4FD03221F09807ABC5F6D837F53C57670D1841F80D4D088F00A568",
        "FA4031049AAFE54F1F1CA0438CA628AE2BE9DB687A6D751A43C1BB8C4D5952B8",
        ("", "050505"),
        (840,),
    ),
    Change(
        3,
        59,
        0,
        "모든 세력을 국가 변경 대상으로 선택",
        "모든 세력을 영지 변경 대상으로 선택",
        "3D17B191F822203AC47E1A3BD3A073D63C65E749FB323DB01A7C03F378EFCBBD",
        "964ED5ACA4BB2E48A1A8A43CC8B503748F3C527ECA77CE0DB43B2FD0880F33DB",
        ("", "050505"),
        (840,),
    ),
    Change(
        3,
        60,
        0,
        "이 세력을 국가 변경 대상에서 제외",
        "이 세력을 영지 변경 대상에서 제외",
        "0E58AB86A736DB40B19E178A0CAB8A877D82521975CF743FAE8E2A8D31EA9D18",
        "53D2BD4710BC8A3BA95FC93291113C87F98781F74F25A9DBE84D4409453E19D6",
        ("", "050505"),
        (792,),
    ),
    Change(
        3,
        61,
        0,
        "이 세력을 국가 변경 대상으로 선택",
        "이 세력을 영지 변경 대상으로 선택",
        "34BCEC11CD92874A15E980DF2F5E319EE7BC38518176EDB8633B66C53E00C650",
        "D7F53BBF72E682E7FB6ED556E1071CC756AC1E73834518EBCDC79BD72926A951",
        ("", "050505"),
        (792,),
    ),
    Change(
        4,
        148,
        0,
        "《노부나가의 야망·신생 파워업키트》 발매!\n"
        "여러 추가 요소 중 일부를 소개합니다!\n"
        "한층 진화한 “군신일체의 전국 체험”을 즐겨 보십시오.\n\n"
        "·모든 성이 전용 전장이 되는 시리즈 최대 규모의 “공성전”\n"
        "·“군단 전략”과 “평정중”의 새로운 전략, 무장이 제안하는 교섭 “직담”\n"
        "·휴대 군량 보급 거점 등 성에 역할을 부여하는 “성 역할”\n"
        "·자유로운 편집 기능 “국가 변경”“신규 세력 생성”“실존 무장 편집”\n"
        "·“자동 지행”“이벤트 전투”, 새로운 시나리오와 정책 등 풍부한 콘텐츠",
        "《노부나가의 야망·신생 파워업키트》 발매!\n"
        "여러 추가 요소 중 일부를 소개합니다!\n"
        "한층 진화한 “군신일체의 전국 체험”을 즐겨 보십시오.\n\n"
        "·모든 성이 전용 전장이 되는 시리즈 최대 규모의 “공성전”\n"
        "·“군단 전략”과 “평정중”의 새로운 전략, 무장이 제안하는 교섭 “직담”\n"
        "·휴대 군량 보급 거점 등 성에 역할을 부여하는 “성 역할”\n"
        "·자유로운 편집 기능 “영지 변경”“신규 세력 생성”“실존 무장 편집”\n"
        "·“자동 지행”“이벤트 전투”, 새로운 시나리오와 정책 등 풍부한 콘텐츠",
        "0377E4ACC27D7A58462A758CD2C37AF52029F649D2FA2A6BE59E37D2B5420874",
        "93B0446F71DE23B5BAE97506ACE20D9C5EE7C3698E9278F19F5150D8D98022FD",
        ("", "050505"),
        (1008, 864, 1272, 0, 1392, 1752, 1368, 1680, 1704),
    ),
    Change(
        14,
        213,
        1,
        '\n"편집" 버튼에서 다음 항목을 설정할 수 있습니다.\n\n'
        " ·국가 변경  … 지정한 세력의 배치를 바꿉니다\n"
        "          ※국가를 변경해 시작하면 역사 이벤트가 발생하지 않습니다\n"
        " ·신세력 작성 … 등록 무장과 추가 무장을 다이묘로 삼아 새 세력을 만듭니다\n"
        " ·다이묘 변경 … 시나리오 시작 시 다이묘를 같은 세력의 다른 무장으로 바꿉니다",
        '\n"편집" 버튼에서 다음 항목을 설정할 수 있습니다.\n\n'
        " ·영지 변경  … 지정한 세력의 배치를 바꿉니다\n"
        "          ※영지를 변경해 시작하면 역사 이벤트가 발생하지 않습니다\n"
        " ·신세력 작성 … 등록 무장과 추가 무장을 다이묘로 삼아 새 세력을 만듭니다\n"
        " ·다이묘 변경 … 시나리오 시작 시 다이묘를 같은 세력의 다른 무장으로 바꿉니다",
        "0006FAA47976B6061A617FCDE5863D51AB91D2FA0CED552F3763DBF8A1C1CE8D",
        "A79EFC614F5DD852D31FD0CA0231DCDB920B134F6602642FAE5F3FC530EB98FE",
        ("1B4349", "1B435A", "050505"),
        (360, 1128, 0, 1104, 1584, 1776, 1872),
    ),
    Change(
        14,
        214,
        1,
        "\n「편집」 버튼에서 다음 항목을 설정할 수 있습니다.\n\n"
        " ·국체    … 지정한 세력의 배치를 변경\n"
        "          ※국체 후 게임을 시작하면 역사 이벤트 발생 불가\n"
        " ·무장 소속 변경… 무장의 소속 세력이나 낭인의 소재를 무작위로 변경\n"
        "          ※신세력 소속 무장은 변경 불가\n"
        " ·신세력 생성 … 등록 무장·추가 무장을 다이묘로 한 신세력 생성\n"
        " ·다이묘 변경 … 시나리오 시작 시 다이묘를 세력 소속의 다른 무장으로 변경",
        "\n「편집」 버튼에서 다음 항목을 설정할 수 있습니다.\n\n"
        " ·영지 변경 … 지정 세력의 배치를 변경\n"
        "          ※영지 변경 후 시작하면 역사 이벤트 발생 불가\n"
        " ·무장 소속 변경… 무장의 소속 세력이나 낭인의 소재를 무작위로 변경\n"
        "          ※신세력 소속 무장은 변경 불가\n"
        " ·신세력 생성 … 등록 무장·추가 무장을 다이묘로 한 신세력 생성\n"
        " ·다이묘 변경 … 시나리오 시작 시 다이묘를 세력 소속의 다른 무장으로 변경",
        "DAA64B85520D4F8E34582360B3D4889CD69EC270F4A3FD2F32B3DB6D71528557",
        "F63E730135EC9C98C08C556EB6F2C5ACF8AABB35788E21E8325913C9B274D0FA",
        ("1B4349", "1B435A", "050505"),
        (360, 1176, 0, 936, 1320, 1632, 960, 1536, 1776),
    ),
)


@dataclass(frozen=True)
class CandidateBundle:
    packed: bytes
    audit: dict[str, Any]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve()
    root = TMP_ROOT.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave11Error(f"{label} escapes private tmp root: {resolved}") from exc
    return resolved


def records_by_coordinate(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    return {
        (record.block_id, record.record_id): record
        for block in parse_packed_msggame(packed).archive.blocks
        for record in block.records
    }


def literals(record: MsgGameRecord) -> tuple[str, ...]:
    return tuple(item.text for item in parse_record_literals(record))


def opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    cursor = 0
    spans: list[bytes] = []
    for item in parse_record_literals(record):
        spans.append(record.data[cursor : item.marker_offset])
        cursor = item.marker_end
    spans.append(record.data[cursor:])
    return tuple(spans)


def marker_topology(record: MsgGameRecord) -> tuple[tuple[bytes, bytes], ...]:
    return tuple(
        (
            record.data[item.marker_offset : item.marker_offset + len(LITERAL_START)],
            record.data[item.marker_end - len(LITERAL_END) : item.marker_end],
        )
        for item in parse_record_literals(record)
    )


def record_layout(
    record: MsgGameRecord, advance: Any
) -> dict[str, Any]:
    widths: list[int] = []
    fallback: set[str] = set()
    for line in "".join(literals(record)).split("\n"):
        width = 0
        for character in line:
            if unicodedata.category(character) == "Cc":
                raise Wave11Error(f"unexpected control U+{ord(character):04X}")
            cell_width, is_fallback = advance(character)
            width += cell_width
            if is_fallback:
                fallback.add(f"U+{ord(character):04X}")
        widths.append(width)
    return {
        "line_count": len(widths),
        "line_widths_px": widths,
        "max_width_px": max(widths, default=0),
        "wide_fallback_codepoints": sorted(fallback),
    }


def assert_source_file(path: Path, expected_sha256: str, label: str) -> None:
    if not path.is_file():
        raise Wave11Error(f"{label} is absent: {path}")
    actual = sha256_path(path)
    if actual != expected_sha256:
        raise Wave11Error(f"{label} hash differs: expected {expected_sha256}, got {actual}")


def validate_semantic_anchors() -> dict[str, Any]:
    assert_source_file(PRISTINE_PK_JP_PATH, PRISTINE_PK_JP_SHA256, "pristine PC PK Japanese")
    assert_source_file(PK_EN_PATH, PK_EN_SHA256, "PC PK English")
    jp = records_by_coordinate(PRISTINE_PK_JP_PATH.read_bytes())
    en = records_by_coordinate(PK_EN_PATH.read_bytes())
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        coordinate = change.record_coordinate
        jp_record = jp.get(coordinate)
        en_record = en.get(coordinate)
        if jp_record is None or en_record is None:
            raise Wave11Error(f"source anchor lacks {change.label}")
        jp_literals = literals(jp_record)
        en_literals = literals(en_record)
        if change.literal_id >= len(jp_literals) or change.literal_id >= len(en_literals):
            raise Wave11Error(f"source anchor literal index differs at {change.label}")
        if JP_FEATURE not in jp_literals[change.literal_id]:
            raise Wave11Error(f"pristine PC Japanese lacks 国替 at {change.label}")
        if EN_FEATURE.casefold() not in en_literals[change.literal_id].casefold():
            raise Wave11Error(f"PC English lacks Switch Countries at {change.label}")
        rows.append(
            {
                "coordinate": change.label,
                "pristine_jp_literal_utf16le_sha256": text_sha256(
                    jp_literals[change.literal_id]
                ),
                "pc_en_literal_utf16le_sha256": text_sha256(en_literals[change.literal_id]),
            }
        )
    return {
        "pristine_pk_jp_sha256": PRISTINE_PK_JP_SHA256,
        "pk_en_sha256": PK_EN_SHA256,
        "feature_anchor_count": len(rows),
        "rows": rows,
    }


def validate_wave9_input(input_root: Path) -> bytes:
    root = input_root.resolve()
    if not root.is_dir():
        raise Wave11Error(f"Wave 9 private input root is absent: {root}")
    if "switch" in "/".join(part.lower() for part in root.parts):
        raise Wave11Error("Nintendo Switch input is forbidden")
    path = root / Path(RESOURCE)
    if not path.is_file():
        raise Wave11Error(f"Wave 9 input lacks {RESOURCE}")
    packed = path.read_bytes()
    actual = sha256_bytes(packed)
    if actual != INPUT_SHA256:
        raise Wave11Error(f"Wave 9 input hash differs: expected {INPUT_SHA256}, got {actual}")
    return packed


def validate_input_record(record: MsgGameRecord, change: Change) -> None:
    if sha256_bytes(record.data) != change.input_record_sha256:
        raise Wave11Error(f"input record hash differs at {change.label}")
    values = literals(record)
    if change.literal_id >= len(values) or values[change.literal_id] != change.current:
        raise Wave11Error(f"input literal differs at {change.label}")
    if b"\x01\x43" in record.data:
        raise Wave11Error(f"unexpected runtime 0143 command at {change.label}")
    actual_spans = tuple(value.hex().upper() for value in opaque_spans(record))
    if actual_spans != change.input_opaque_spans_hex:
        raise Wave11Error(f"input opaque spans differ at {change.label}")
    if not record.data.endswith(RECORD_TERMINATOR):
        raise Wave11Error(f"input terminator differs at {change.label}")
    expected_markers = tuple((LITERAL_START, LITERAL_END) for _ in values)
    if marker_topology(record) != expected_markers:
        raise Wave11Error(f"input marker topology differs at {change.label}")


def rebuild_change(record: MsgGameRecord, change: Change) -> MsgGameRecord:
    data = rebuild_record_literals(record, {change.literal_id: change.target})
    output = MsgGameRecord(
        block_id=record.block_id,
        record_id=record.record_id,
        relative_offset=record.relative_offset,
        data=data,
    )
    output_values = literals(output)
    if output_values[change.literal_id] != change.target:
        raise Wave11Error(f"output literal differs at {change.label}")
    if sha256_bytes(output.data) != change.output_record_sha256:
        raise Wave11Error(f"output record hash differs at {change.label}")
    if opaque_spans(output) != opaque_spans(record):
        raise Wave11Error(f"opaque bytes changed at {change.label}")
    if marker_topology(output) != marker_topology(record):
        raise Wave11Error(f"literal marker topology changed at {change.label}")
    if not output.data.endswith(RECORD_TERMINATOR):
        raise Wave11Error(f"output terminator differs at {change.label}")
    return output


def validate_full_output(
    input_packed: bytes,
    output_packed: bytes,
    expected_records: Mapping[tuple[int, int], MsgGameRecord],
) -> None:
    before = records_by_coordinate(input_packed)
    after = records_by_coordinate(output_packed)
    if before.keys() != after.keys():
        raise Wave11Error("candidate changed msggame record topology")
    changed = {key for key in before if before[key].data != after[key].data}
    expected = set(expected_records)
    if changed != expected:
        raise Wave11Error(
            f"candidate scope differs: expected={sorted(expected)} actual={sorted(changed)}"
        )
    for coordinate, expected_record in expected_records.items():
        if after[coordinate].data != expected_record.data:
            raise Wave11Error(f"rebuilt record differs at {coordinate}")


def prepare_candidate(input_root: Path, font_root: Path) -> CandidateBundle:
    input_packed = validate_wave9_input(input_root)
    semantic_anchors = validate_semantic_anchors()
    advance, font_evidence = WAVE10_METRIC.load_font_advance(font_root)
    before = records_by_coordinate(input_packed)
    expected_records: dict[tuple[int, int], MsgGameRecord] = {}
    replacements: dict[tuple[int, int], bytes] = {}
    audit_rows: list[dict[str, Any]] = []

    for change in CHANGES:
        coordinate = change.record_coordinate
        input_record = before.get(coordinate)
        if input_record is None:
            raise Wave11Error(f"input lacks {change.label}")
        validate_input_record(input_record, change)
        output_record = rebuild_change(input_record, change)
        input_layout = record_layout(input_record, advance)
        output_layout = record_layout(output_record, advance)
        if output_layout["wide_fallback_codepoints"]:
            raise Wave11Error(f"output needs fallback glyphs at {change.label}")
        if output_layout["line_count"] != input_layout["line_count"]:
            raise Wave11Error(f"manual line count changed at {change.label}")
        if tuple(output_layout["line_widths_px"]) != change.expected_record_line_widths_px:
            raise Wave11Error(f"output font widths differ at {change.label}")
        if any(
            after_width > before_width
            for before_width, after_width in zip(
                input_layout["line_widths_px"], output_layout["line_widths_px"]
            )
        ):
            raise Wave11Error(f"output became wider at {change.label}")
        expected_records[coordinate] = output_record
        replacements[coordinate] = output_record.data
        audit_rows.append(
            {
                "coordinate": change.label,
                "input_record_sha256": change.input_record_sha256,
                "output_record_sha256": change.output_record_sha256,
                "input_literal_utf16le_sha256": text_sha256(change.current),
                "output_literal_utf16le_sha256": text_sha256(change.target),
                "input_opaque_span_sha256": [
                    sha256_bytes(value) for value in opaque_spans(input_record)
                ],
                "output_opaque_span_sha256": [
                    sha256_bytes(value) for value in opaque_spans(output_record)
                ],
                "literal_marker_topology": [
                    {"start": start.hex().upper(), "end": end.hex().upper()}
                    for start, end in marker_topology(input_record)
                ],
                "contains_preserved_esc_style_tags": any(
                    value.startswith(b"\x1B") for value in opaque_spans(input_record)
                ),
                "contains_runtime_0143": False,
                "input_layout": input_layout,
                "output_layout": output_layout,
            }
        )

    output_packed = rebuild_packed_msggame(input_packed, replacements)
    validate_full_output(input_packed, output_packed, expected_records)
    output_sha256 = sha256_bytes(output_packed)
    if output_sha256 != TARGET_SHA256:
        raise Wave11Error(
            f"target hash differs: expected {TARGET_SHA256}, got {output_sha256}"
        )
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_free": True,
        "steam_write_capability": "absent",
        "source_policy": {
            "platform": "Steam PC",
            "input_text_profile": "private Wave 9 candidate",
            "semantic_anchors": ["pristine PC Japanese", "PC English"],
            "switch_korean_used": False,
            "excluded": ["Nintendo Switch Korean"],
        },
        "input_sha256": INPUT_SHA256,
        "output_sha256": output_sha256,
        "font_evidence": font_evidence,
        "semantic_anchors": semantic_anchors,
        "summary": {
            "changed_resource": RESOURCE,
            "physical_records": len(CHANGES),
            "literal_slots": len(CHANGES),
            "coordinates": [change.label for change in CHANGES],
            "terminology": "国替 -> 영지 변경",
            "real_game_qa_required_before_release": True,
        },
        "records": audit_rows,
    }
    return CandidateBundle(packed=output_packed, audit=audit)


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def write_json(path: Path, value: Mapping[str, Any]) -> str:
    payload = canonical_json(value)
    atomic_write(path, payload)
    return sha256_bytes(payload)


def write_candidate(bundle: CandidateBundle, output_root: Path) -> None:
    output_root = require_private(output_root, "candidate output")
    if output_root.exists():
        raise Wave11Error(f"refusing to overwrite candidate output: {output_root}")
    destination = output_root / Path(RESOURCE)
    atomic_write(destination, bundle.packed)
    if sha256_path(destination) != TARGET_SHA256:
        raise Wave11Error("written candidate hash differs")


def build_manifest(bundle: CandidateBundle, audit_sha256: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "source_free_audit": True,
        "source_free_audit_sha256": audit_sha256,
        "steam_write_capability": "absent",
        "steam_apply_command": None,
        "input_sha256": INPUT_SHA256,
        "output_sha256": sha256_bytes(bundle.packed),
        "changed_paths": [RESOURCE],
        "coordinates": [change.label for change in CHANGES],
        "real_game_qa_required_before_release": True,
    }


def print_json(value: Mapping[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def command_hash(args: argparse.Namespace) -> int:
    bundle = prepare_candidate(args.input_root, args.font_root)
    print_json(
        {
            "status": "ok",
            "candidate_records": len(CHANGES),
            "output_sha256": sha256_bytes(bundle.packed),
            "steam_write_capability": "absent",
        }
    )
    return 0


def command_audit(args: argparse.Namespace) -> int:
    path = require_private(args.audit_path, "audit output")
    bundle = prepare_candidate(args.input_root, args.font_root)
    audit_sha256 = write_json(path, bundle.audit)
    print_json(
        {
            "status": "ok",
            "audit": path.relative_to(REPO).as_posix(),
            "audit_sha256": audit_sha256,
            "output_sha256": sha256_bytes(bundle.packed),
            "steam_write_capability": "absent",
        }
    )
    return 0


def command_build(args: argparse.Namespace) -> int:
    output_root = require_private(args.output_root, "candidate output")
    audit_path = require_private(args.audit_path, "audit output")
    manifest_path = require_private(args.manifest, "manifest output")
    bundle = prepare_candidate(args.input_root, args.font_root)
    write_candidate(bundle, output_root)
    audit_sha256 = write_json(audit_path, bundle.audit)
    manifest_sha256 = write_json(manifest_path, build_manifest(bundle, audit_sha256))
    print_json(
        {
            "status": "ok",
            "candidate": output_root.relative_to(REPO).as_posix(),
            "audit": audit_path.relative_to(REPO).as_posix(),
            "manifest": manifest_path.relative_to(REPO).as_posix(),
            "audit_sha256": audit_sha256,
            "manifest_sha256": manifest_sha256,
            "output_sha256": sha256_bytes(bundle.packed),
            "steam_write_capability": "absent",
        }
    )
    return 0


def add_input_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input-root", type=Path, default=WAVE9_INPUT_ROOT)
    parser.add_argument("--font-root", type=Path, default=DEFAULT_FONT_ROOT)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    hash_parser = commands.add_parser("hash", help="validate and print the private target hash")
    add_input_arguments(hash_parser)
    hash_parser.set_defaults(func=command_hash)
    audit_parser = commands.add_parser("audit", help="write a source-free private audit")
    add_input_arguments(audit_parser)
    audit_parser.add_argument(
        "--audit-path",
        type=Path,
        default=TMP_ROOT / "audit_pc_dialogue_quality_wave11.v1.json",
    )
    audit_parser.set_defaults(func=command_audit)
    build_parser = commands.add_parser("build", help="write the private candidate and audit")
    add_input_arguments(build_parser)
    build_parser.add_argument(
        "--output-root", type=Path, default=TMP_ROOT / "candidate-build-1"
    )
    build_parser.add_argument(
        "--audit-path",
        type=Path,
        default=TMP_ROOT / "audit_pc_dialogue_quality_wave11.v1.json",
    )
    build_parser.add_argument(
        "--manifest", type=Path, default=TMP_ROOT / "build_manifest.v1.json"
    )
    build_parser.set_defaults(func=command_build)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Wave11Error as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
