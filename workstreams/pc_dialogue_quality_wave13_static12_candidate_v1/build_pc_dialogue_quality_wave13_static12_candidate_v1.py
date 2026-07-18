#!/usr/bin/env python3
"""Build a private, PC-only static repair candidate for twelve PK dialogues.

The builder reads the *current* Steam PC PK ``msggame.bin`` only after pinning
its full-file SHA-256.  It writes a candidate only below this workstream's
private ``tmp`` directory.  It deliberately has no Steam apply, Git, network,
or Nintendo Switch Korean input path.

Each target record is fully static.  The repair preserves its literal-marker
count and manual line break, removes only the listed Japanese ``01 43``
morphology commands, and leaves the ``05 05 05`` record terminator intact.
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
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
TOOLS = REPO / "tools"
PRIVATE_TMP_ROOT = REPO / "tmp" / WORKSTREAM.name

RESOURCE = "MSG_PK/JP/msggame.bin"
CURRENT_STEAM_PK_MSGGAME = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave13-static12-candidate.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave13-static12-audit.v1"
RECORD_TERMINATOR = b"\x05\x05\x05"
LITERAL_START = b"\x07\x07\x01"
LITERAL_END = b"\x07\x07\x02"
MANUAL_LINE_COUNT = 2

# Fixed to the current Steam PK resource that this candidate was reviewed
# against.  A changed live file is rejected rather than silently rebased.
INPUT_SHA256 = "209B96CADE84D82810A8A79CA362DFA1B6665A8C601D3DB2C3DC0F96986E9930"
INPUT_SIZE = 1_806_795
TARGET_SHA256 = "FB8E8A82675C9A4EAABEE060F0616CF08CD7D2C57DB05BBFD04FC597FA07B34C"
TARGET_SIZE = 1_806_731


@dataclass(frozen=True)
class Change:
    record_id: int
    current_literals: tuple[str, ...]
    target_literals: tuple[str, ...]
    input_record_sha256: str
    target_record_sha256: str
    input_record_size: int
    target_record_size: int
    removed_opaque_commands_hex: tuple[str, ...]

    @property
    def coordinate(self) -> tuple[int, int]:
        return (6, self.record_id)


CHANGES = (
    Change(
        4341,
        ("주군께서 내리신 땅을\n끝까지 지키는 것이 무사의 명예", "！"),
        ("주군께서 내리신 땅을\n끝까지 지키는 것이 무사의 명예다", "!"),
        "280838B27BF88AD0F1F7F5675CEF8FD8C061A195C192D4900938CBD21D62F47E",
        "846344DB3398F8A5342CFED792DA437AD6EFB87DA2A8C68C04E090F5C1FA44B6",
        81,
        77,
        ("0143FC010000",),
    ),
    Change(
        4342,
        ("예로부터 이어진 우리 가문의 이름을\n천하에 떨치겠", "！"),
        ("예로부터 이어진 우리 가문의 이름을\n천하에 떨치겠다", "!"),
        "BB6F3C72A9DC0FEA4BC08C09107046ED7724DD5A31702E4D4F2F62B8B2AA7D34",
        "391364FB210AF3CFE82D8C2DD5B7091D74B0F0D3AF570EA86B1F8696C856AFF0",
        77,
        73,
        ("014326020000",),
    ),
    Change(
        4343,
        ("신불의 가르침으로\n나라의 정치를 바로잡겠", "！"),
        ("신불의 가르침으로\n나라의 정치를 바로잡겠다", "!"),
        "4DAE16F21E6D4888EEA131D563BF0AA9D39C475A0EF55E4745A9603F84CD6740",
        "F3D40663DCB570C414338293E85AB9044E75B95D5132BAF9802200F37E917840",
        67,
        63,
        ("01432A040000",),
    ),
    Change(
        4344,
        ("아미타불도 돈 앞에서는 빛나는 법!\n내 장사 수완으로 이익을 가져오겠", "！"),
        ("아미타불도 돈 앞에서는 빛나는 법!\n내 장사 수완으로 이익을 가져오겠다", "!"),
        "9C11512CDFF7211EBDF4F8054681149E79943843D0A5B837E177BCF512495F18",
        "D0A284FDAF34D56AD61DC4DA3390214A29D8DC27567FB3CC4EDE0543B0767F1F",
        99,
        95,
        ("01438A040000",),
    ),
    Change(
        4345,
        ("우리 가문의 무예를 갈고닦도록\n내 유파의 검술을 가르치겠", "！"),
        ("우리 가문의 무예를 갈고닦도록\n내 유파의 검술을 가르치겠다", "!"),
        "4A52CB7802ABBC53DE9032696E81B3D92B82B4E9404477365BAB9D72376FF39C",
        "76943A1394C507B6106E71E6521DC4F5C5CC2C296A9CA5D12FACABA5BE610735",
        85,
        81,
        ("01432A040000",),
    ),
    Change(
        4346,
        ("백성은 나라보다 귀한 법…\n백성의 힘으로 나라를 풍요롭게 하겠", "！"),
        ("백성은 나라보다 귀한 법…\n백성의 힘으로 나라를 풍요롭게 하겠다", "!"),
        "D5AA5EB3C9767736540327B444E2AF54BE6034A4DA4EE155BF76E5F141F6749F",
        "2695BFF88B5DD6976B2C3BD54D9064D621715E3FC013722BF2C2AF610445EDBD",
        91,
        87,
        ("0143A8010000",),
    ),
    Change(
        4352,
        ("너희는 모두 나의 심복이", "!\n각자의 장기를 마음껏 살려 보아라", "！"),
        ("너희는 모두 나의 심복이다", "!\n각자의 장기를 마음껏 살려 보아라", "!"),
        "950C2A9EFAC0D59A0B971326A15844157D60E6CAE237CEB5E2C7619762A4176D",
        "969C408E3C3AD654400864D7AF43EF7952E413A99045C91728FB0E52B98EA83E",
        101,
        91,
        ("014352000000", "01432A040000"),
    ),
    Change(
        4354,
        ("한마음으로 뭉친 병사는 강하다!\n병력 차이가 아무리 커도 결코 지지 않겠", "！"),
        ("한마음으로 뭉친 병사는 강하다!\n병력 차이가 아무리 커도 결코 지지 않겠다", "!"),
        "5C07460073D0C1B11EB63BB80016666A4B2CE8986DA09BB7A050FBA14AD4D8EC",
        "119B51641EA7C60F25376B5C76A86AB766CC6E594223EF56516D64C39964E0E6",
        103,
        99,
        ("0143EC020000",),
    ),
    Change(
        4355,
        ("무사도란 죽음을 각오하는 것!\n궁지에서야말로 온 힘을 다하겠", "！"),
        ("무사도란 죽음을 각오하는 것!\n궁지에서야말로 온 힘을 다하겠다", "!"),
        "1FB90C15087B61D78D552D12FBCB96CDF2CDCC2451DC3B2150D1328F5312084D",
        "B01AD21986030F1DC36023108925EF63F91AC3BABCD5DC65649F542AF4D7A5FD",
        89,
        85,
        ("014352030000",),
    ),
    Change(
        4359,
        ("이 땅의 백성을 향사로 등용하리라!\n모두 함께 이 땅을 일으켜 세우자", "！"),
        ("이 땅의 백성을 향사로 등용하리라!\n모두 함께 이 땅을 일으켜 세우자", "!"),
        "8A7D651568B791308D1D0A54F396474366F217165C8038D07FEDED1D69891CB4",
        "FF239FD7C8A8C69212251D384931E139E3B85BE845C4179F56E9BE268D6A4504",
        99,
        93,
        ("014302020000",),
    ),
    Change(
        4366,
        ("상업을 지배하는 자가 천하를 지배한다!\n한 푼의 돈도 소홀히 하지 않겠", "！"),
        ("상업을 지배하는 자가 천하를 지배한다!\n한 푼의 돈도 소홀히 하지 않겠다", "!"),
        "16D4D9F147C22A89935ECC6EFCCB11782BFAA7BB6A1D65FA53C2DAB42015E2FC",
        "2C0022CF2CA4489A3C779D9E0431E4F2EBC6A2B3B635F1F633B117AF58E585F7",
        107,
        97,
        ("01432E030000", "014302020000"),
    ),
    Change(
        4367,
        ("우리는 진수대장군의 후예다!\n병사들이여, 두려워 말고 나아가라", "！"),
        ("우리는 진수대장군의 후예다!\n병사들이여, 두려워 말고 나아가라", "!"),
        "CCB69CE99C433782F08C7EC154300B7FC683695B05E6378C1BA61AE5DA2ACF5B",
        "E765F00BBC00547D21582FDB7A8057FF259B986E5BADD914080F3ABB74B0E9D6",
        91,
        85,
        ("014352030000",),
    ),
)

CHANGE_BY_COORDINATE = {change.coordinate: change for change in CHANGES}
if len(CHANGE_BY_COORDINATE) != len(CHANGES):
    raise RuntimeError("duplicate Wave 13 target coordinate")


class Wave13Error(RuntimeError):
    """A source, byte-preservation, or private-output contract failed."""


for module_root in (TOOLS, MSGGAME_TOOLS):
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from msggame_format import (  # noqa: E402
    MsgGameRecord,
    parse_packed_msggame,
    parse_raw_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_raw_msggame,
)


@dataclass(frozen=True)
class CandidateBundle:
    packed_msggame: bytes
    input_sha256: str
    output_sha256: str
    audit: Mapping[str, Any]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Mapping[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def coordinate_text(coordinate: tuple[int, int]) -> str:
    return f"{coordinate[0]}:{coordinate[1]}"


def require_under(path: Path, root: Path, label: str) -> Path:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise Wave13Error(f"{label} escapes {resolved_root}: {resolved_path}") from exc
    return resolved_path


def require_private_output(path: Path, label: str) -> Path:
    return require_under(path, PRIVATE_TMP_ROOT, label)


def literal_texts(record: MsgGameRecord) -> tuple[str, ...]:
    return tuple(literal.text for literal in parse_record_literals(record))


def opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    cursor = 0
    spans: list[bytes] = []
    for literal in parse_record_literals(record):
        spans.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    spans.append(record.data[cursor:])
    return tuple(spans)


def marker_topology(record: MsgGameRecord) -> tuple[tuple[bytes, bytes], ...]:
    return tuple(
        (
            record.data[literal.marker_offset : literal.marker_offset + len(LITERAL_START)],
            record.data[literal.marker_end - len(LITERAL_END) : literal.marker_end],
        )
        for literal in parse_record_literals(record)
    )


def records_by_coordinate(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    archive = parse_packed_msggame(packed).archive
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def expected_input_opaque(change: Change) -> tuple[str, ...]:
    # ``6:4352`` has three literal slots and one morphology command in each
    # interior gap.  The other records have two literal slots; ``6:4366`` is
    # the one case with two consecutive 01 43 commands in its single gap.
    if len(change.current_literals) == 3:
        return ("", *change.removed_opaque_commands_hex, RECORD_TERMINATOR.hex().upper())
    return ("", "".join(change.removed_opaque_commands_hex), RECORD_TERMINATOR.hex().upper())


def expected_output_opaque(change: Change) -> tuple[str, ...]:
    return (*("" for _ in change.target_literals), RECORD_TERMINATOR.hex().upper())


def validate_static_text(text: str, label: str) -> None:
    if text.count("\n") != MANUAL_LINE_COUNT - 1:
        raise Wave13Error(f"{label} must preserve exactly {MANUAL_LINE_COUNT} manual lines")
    if "\x1b" in text or "%" in text:
        raise Wave13Error(f"{label} contains a runtime token marker")
    encoded = text.encode("utf-16-le")
    if LITERAL_START in encoded or LITERAL_END in encoded:
        raise Wave13Error(f"{label} encodes a reserved literal marker")
    for character in text:
        if character != "\n" and unicodedata.category(character) == "Cc":
            raise Wave13Error(f"{label} contains control U+{ord(character):04X}")


def validate_input_record(record: MsgGameRecord, change: Change) -> None:
    coordinate = coordinate_text(change.coordinate)
    if len(record.data) != change.input_record_size:
        raise Wave13Error(f"{coordinate} input record size differs")
    if sha256_bytes(record.data) != change.input_record_sha256:
        raise Wave13Error(f"{coordinate} input record SHA-256 differs")
    if literal_texts(record) != change.current_literals:
        raise Wave13Error(f"{coordinate} input literal tuple differs")
    actual_opaque = tuple(value.hex().upper() for value in opaque_spans(record))
    if actual_opaque != expected_input_opaque(change):
        raise Wave13Error(f"{coordinate} input opaque command layout differs")
    if not all(command.startswith("0143") for command in change.removed_opaque_commands_hex):
        raise Wave13Error(f"{coordinate} removal is not restricted to 01 43 commands")
    if not record.data.endswith(RECORD_TERMINATOR):
        raise Wave13Error(f"{coordinate} input record lacks terminator")
    if marker_topology(record) != tuple((LITERAL_START, LITERAL_END) for _ in change.current_literals):
        raise Wave13Error(f"{coordinate} input marker topology differs")
    validate_static_text("".join(change.current_literals), f"{coordinate} current text")


def rebuild_static_record(record: MsgGameRecord, change: Change) -> MsgGameRecord:
    """Rebuild this static record without its Japanese morphology commands."""
    validate_input_record(record, change)
    payload = bytearray()
    for literal in change.target_literals:
        payload.extend(LITERAL_START)
        payload.extend(literal.encode("utf-16-le"))
        payload.extend(LITERAL_END)
    payload.extend(RECORD_TERMINATOR)
    output = MsgGameRecord(
        block_id=record.block_id,
        record_id=record.record_id,
        relative_offset=record.relative_offset,
        data=bytes(payload),
    )
    coordinate = coordinate_text(change.coordinate)
    if len(output.data) != change.target_record_size:
        raise Wave13Error(f"{coordinate} target record size differs")
    if sha256_bytes(output.data) != change.target_record_sha256:
        raise Wave13Error(f"{coordinate} target record SHA-256 differs")
    if literal_texts(output) != change.target_literals:
        raise Wave13Error(f"{coordinate} target literal tuple differs")
    if tuple(value.hex().upper() for value in opaque_spans(output)) != expected_output_opaque(change):
        raise Wave13Error(f"{coordinate} target opaque layout differs")
    if marker_topology(output) != marker_topology(record):
        raise Wave13Error(f"{coordinate} target changed literal marker topology")
    if not output.data.endswith(RECORD_TERMINATOR):
        raise Wave13Error(f"{coordinate} target lost terminator")
    if bytes((1, 67)) in output.data:
        raise Wave13Error(f"{coordinate} target retained a 01 43 command")
    validate_static_text("".join(change.target_literals), f"{coordinate} target text")
    return output


def validate_current_steam_input(path: Path) -> bytes:
    if path.resolve() != CURRENT_STEAM_PK_MSGGAME.resolve():
        raise Wave13Error("Wave 13 intentionally accepts only the current Steam PK input path")
    if not path.is_file():
        raise Wave13Error(f"current Steam PK input is absent: {path}")
    packed = path.read_bytes()
    if len(packed) != INPUT_SIZE:
        raise Wave13Error(f"current Steam PK input size differs: expected {INPUT_SIZE}")
    if sha256_bytes(packed) != INPUT_SHA256:
        raise Wave13Error("current Steam PK input SHA-256 differs; explicit re-audit required")
    return packed


def validate_raw_roundtrip(packed: bytes) -> None:
    """Prove that the output raw archive is structurally stable through LZ4."""
    header, raw = decompress_wrapper(packed)
    archive = parse_raw_msggame(raw)
    rebuilt_raw = rebuild_raw_msggame(archive)
    if rebuilt_raw != raw:
        raise Wave13Error("raw msggame round-trip differs")
    repacked = recompress_wrapper(rebuilt_raw, header)
    _roundtrip_header, roundtrip_raw = decompress_wrapper(repacked)
    if roundtrip_raw != raw:
        raise Wave13Error("LZ4 raw round-trip differs")


def validate_full_output(input_packed: bytes, output_packed: bytes, expected: Mapping[tuple[int, int], MsgGameRecord]) -> None:
    before = records_by_coordinate(input_packed)
    after = records_by_coordinate(output_packed)
    if before.keys() != after.keys():
        raise Wave13Error("record topology changed")
    changed = {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}
    expected_coordinates = set(CHANGE_BY_COORDINATE)
    if changed != expected_coordinates:
        raise Wave13Error(
            f"only-12-record regression failed: expected {sorted(expected_coordinates)}, got {sorted(changed)}"
        )
    for coordinate, before_record in before.items():
        if coordinate in expected_coordinates:
            if after[coordinate].data != expected[coordinate].data:
                raise Wave13Error(f"{coordinate_text(coordinate)} target record differs")
        elif after[coordinate].data != before_record.data:
            raise Wave13Error(f"non-target record changed: {coordinate_text(coordinate)}")
    validate_raw_roundtrip(output_packed)


def prior_wave_coordinates() -> dict[str, set[tuple[int, int]]]:
    """Load W10--12 metadata solely to assert this batch is disjoint."""
    builders = {
        "wave10": REPO / "workstreams" / "pc_dialogue_quality_wave10_candidate_v1" / "build_pc_dialogue_quality_wave10_candidate_v1.py",
        "wave11": REPO / "workstreams" / "pc_dialogue_quality_wave11_candidate_v1" / "build_pc_dialogue_quality_wave11_candidate_v1.py",
        "wave12": REPO / "workstreams" / "pc_dialogue_quality_wave12_candidate_v1" / "build_pc_dialogue_quality_wave12_candidate_v1.py",
    }
    modules: dict[str, Any] = {}
    for label, path in builders.items():
        spec = importlib.util.spec_from_file_location(f"_wave13_{label}", path)
        if spec is None or spec.loader is None:
            raise Wave13Error(f"cannot load {label} metadata")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        modules[label] = module
    return {
        "wave10": {(6, record_id) for record_id in modules["wave10"].PK_RECORD_IDS},
        "wave11": {change.record_coordinate for change in modules["wave11"].CHANGES},
        "wave12": {modules["wave12"].COORDINATE},
    }


def validate_prior_wave_disjointness() -> dict[str, list[str]]:
    ours = set(CHANGE_BY_COORDINATE)
    evidence: dict[str, list[str]] = {}
    for label, coordinates in prior_wave_coordinates().items():
        overlap = ours & coordinates
        if overlap:
            raise Wave13Error(f"Wave 13 overlaps {label}: {sorted(overlap)}")
        evidence[label] = [coordinate_text(value) for value in sorted(coordinates)]
    return evidence


def audit_record(change: Change, input_record: MsgGameRecord, output_record: MsgGameRecord) -> dict[str, Any]:
    current_text = "".join(change.current_literals)
    target_text = "".join(change.target_literals)
    return {
        "coordinate": coordinate_text(change.coordinate),
        "input_record_sha256": sha256_bytes(input_record.data),
        "target_record_sha256": sha256_bytes(output_record.data),
        "input_record_size": len(input_record.data),
        "target_record_size": len(output_record.data),
        "current_literals": list(change.current_literals),
        "target_literals": list(change.target_literals),
        "literal_marker_count": len(change.current_literals),
        "literal_marker_topology_hex": [
            {"start": start.hex().upper(), "end": end.hex().upper()}
            for start, end in marker_topology(input_record)
        ],
        "removed_opaque_commands_hex": list(change.removed_opaque_commands_hex),
        "input_opaque_spans_hex": [value.hex().upper() for value in opaque_spans(input_record)],
        "target_opaque_spans_hex": [value.hex().upper() for value in opaque_spans(output_record)],
        "terminator_hex": RECORD_TERMINATOR.hex().upper(),
        "manual_line_count": {"current": current_text.count("\n") + 1, "target": target_text.count("\n") + 1},
        "runtime_tokens": {"current": [], "target": []},
    }


def prepare_candidate(input_path: Path = CURRENT_STEAM_PK_MSGGAME) -> CandidateBundle:
    input_packed = validate_current_steam_input(input_path)
    validate_raw_roundtrip(input_packed)
    previous_waves = validate_prior_wave_disjointness()
    before = records_by_coordinate(input_packed)
    replacements: dict[tuple[int, int], bytes] = {}
    expected_records: dict[tuple[int, int], MsgGameRecord] = {}
    rows: list[dict[str, Any]] = []
    for change in CHANGES:
        record = before.get(change.coordinate)
        if record is None:
            raise Wave13Error(f"current Steam PK input lacks {coordinate_text(change.coordinate)}")
        target = rebuild_static_record(record, change)
        replacements[change.coordinate] = target.data
        expected_records[change.coordinate] = target
        rows.append(audit_record(change, record, target))
    output_packed = rebuild_packed_msggame(input_packed, replacements)
    validate_full_output(input_packed, output_packed, expected_records)
    if len(output_packed) != TARGET_SIZE:
        raise Wave13Error(f"candidate size differs: expected {TARGET_SIZE}, got {len(output_packed)}")
    output_sha = sha256_bytes(output_packed)
    if output_sha != TARGET_SHA256:
        raise Wave13Error(f"candidate SHA-256 differs: expected {TARGET_SHA256}, got {output_sha}")
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "input": "current Steam MSG_PK/JP/msggame.bin with pinned SHA-256",
            "switch_korean_used": False,
            "steam_write_capability": "absent",
        },
        "resource": RESOURCE,
        "input_sha256": INPUT_SHA256,
        "target_sha256": TARGET_SHA256,
        "only_changed_coordinates": [coordinate_text(change.coordinate) for change in CHANGES],
        "prior_wave_disjointness": previous_waves,
        "raw_roundtrip": "pass",
        "records": rows,
    }
    return CandidateBundle(output_packed, INPUT_SHA256, output_sha, audit)


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def write_candidate(bundle: CandidateBundle, output_root: Path) -> None:
    output_root = require_private_output(output_root, "candidate output")
    if output_root.exists():
        raise Wave13Error(f"refusing to overwrite candidate output: {output_root}")
    destination = output_root / Path(RESOURCE)
    atomic_write(destination, bundle.packed_msggame)
    if sha256_path(destination) != TARGET_SHA256:
        raise Wave13Error("written private candidate SHA-256 differs")


def write_json(path: Path, value: Mapping[str, Any]) -> str:
    payload = canonical_json(value)
    atomic_write(path, payload)
    return sha256_bytes(payload)


def build_manifest(bundle: CandidateBundle, audit_sha256: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "steam_write_capability": "absent",
        "steam_apply_command": None,
        "git_operation": None,
        "input_sha256": bundle.input_sha256,
        "target_sha256": bundle.output_sha256,
        "changed_paths": [RESOURCE],
        "coordinates": [coordinate_text(change.coordinate) for change in CHANGES],
        "audit_sha256": audit_sha256,
        "real_game_qa_required_before_release": True,
    }


def print_json(value: Mapping[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def command_hash(args: argparse.Namespace) -> int:
    bundle = prepare_candidate(args.input_path)
    print_json({"status": "ok", "target_sha256": bundle.output_sha256, "steam_write_capability": "absent"})
    return 0


def command_build(args: argparse.Namespace) -> int:
    output_root = require_private_output(args.output_root, "candidate output")
    audit_path = require_private_output(args.audit_path, "audit output")
    manifest_path = require_private_output(args.manifest_path, "manifest output")
    bundle = prepare_candidate(args.input_path)
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
            "target_sha256": bundle.output_sha256,
            "steam_write_capability": "absent",
        }
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("hash", "build"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--input-path", type=Path, default=CURRENT_STEAM_PK_MSGGAME)
        if command == "build":
            subparser.add_argument(
                "--output-root", type=Path, default=PRIVATE_TMP_ROOT / "candidate-build-1"
            )
            subparser.add_argument(
                "--audit-path", type=Path, default=PRIVATE_TMP_ROOT / "audit.v1.json"
            )
            subparser.add_argument(
                "--manifest-path", type=Path, default=PRIVATE_TMP_ROOT / "manifest.v1.json"
            )
            subparser.set_defaults(func=command_build)
        else:
            subparser.set_defaults(func=command_hash)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
