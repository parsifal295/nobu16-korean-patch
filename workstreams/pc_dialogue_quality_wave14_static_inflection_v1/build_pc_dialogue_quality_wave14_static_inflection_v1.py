#!/usr/bin/env python3
"""Build a PC-only candidate for static dialogue records with stale JP ``01 43`` endings.

The records in this batch are deliberately limited to fully static dialogue
templates.  Every removed opaque command is a pinned Japanese morphology
command and the remaining opaque bytecode is only the ``05 05 05`` record
terminator.  Runtime-token records stay out of scope.

This builder reads the current Steam profile and PC JP/EN/SC/TC references,
then writes a candidate only under this workstream's private ``tmp`` tree. It
has no Steam writer, Git, network, or Switch-Korean input path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")

sys.path.insert(0, str(MSGGAME_TOOLS))

from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
)


SCHEMA = "nobu16.kr.pc-dialogue-quality-wave14-static-inflection.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave14-static-inflection-audit.v1"
RECORD_TERMINATOR = b"\x05\x05\x05"
MORPHOLOGY_PREFIX = b"\x01\x43"

PROFILE_PATHS = (
    "MSG/JP/ev_strdata.bin",
    "MSG/JP/msggame.bin",
    "MSG/JP/strdata.bin",
    "MSG_PK/JP/msgbre.bin",
    "MSG_PK/JP/msgdata.bin",
    "MSG_PK/JP/msgev.bin",
    "MSG_PK/JP/msggame.bin",
    "MSG_PK/JP/msgire.bin",
    "MSG_PK/JP/msgstf.bin",
    "MSG_PK/JP/msgstf_ce.bin",
    "MSG_PK/JP/msgui.bin",
)
BASE_MSGGAME = "MSG/JP/msggame.bin"
PK_MSGGAME = "MSG_PK/JP/msggame.bin"
CHANGED_PATHS = (BASE_MSGGAME, PK_MSGGAME)

# v0.11.3's current Steam text profile is this batch's only accepted input.
INPUT_SHA256 = {
    "MSG/JP/ev_strdata.bin": "BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80",
    BASE_MSGGAME: "C74A5D2382D809FAF3EF6A78751872C6B99DAC15FCAB21CEA73E0C904736A347",
    "MSG/JP/strdata.bin": "5F308F416378976C1AB0B50D4A91C9DA38C637A0A842BAB04FB48256B2103E28",
    "MSG_PK/JP/msgbre.bin": "E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939",
    "MSG_PK/JP/msgdata.bin": "69090EC9EEE1DF9EAFB64BB35CEFD285A5089FDE78E9A4A855EAA0AE5991C168",
    "MSG_PK/JP/msgev.bin": "3E2323DDFAD70DAA15713DD1C4D622508BD2E610C65683C0A06D3D1FAC9827A5",
    PK_MSGGAME: "3924ADABF69C9BA72EEBA95E4CE07A3CB8FCD716A31D8F6217ECC5FFAA7B96C5",
    "MSG_PK/JP/msgire.bin": "46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB",
    "MSG_PK/JP/msgstf.bin": "13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B",
    "MSG_PK/JP/msgstf_ce.bin": "06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63",
    "MSG_PK/JP/msgui.bin": "5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7",
}

TARGET_SHA256 = {
    **INPUT_SHA256,
    BASE_MSGGAME: "4D147A4AD73466E882043D8A5E47F0D4DAF37473702A8CEABAEFFBF4E76F2EB8",
    PK_MSGGAME: "BD789D1C5230159433BDB9F2FCBE4B0ABABF9D84FAD2FE1C16EED45B071CE860",
}

PC_JP_SOURCES = {
    BASE_MSGGAME: (
        Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    ),
    PK_MSGGAME: (
        DEFAULT_STEAM_ROOT
        / "KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.6.0/originals/MSG_PK/JP/msggame.bin",
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    ),
}
PC_CONTEXTS = {
    BASE_MSGGAME: {
        "SC": ("MSG/SC/msggame.bin", "B2FC3C18DA0F03ACFA93B1EAB0D09FBFCF7CD5076E667602D1AF212953A09BF7"),
        "TC": ("MSG/TC/msggame.bin", "20E710A11CDADFAF514EBC3B9C664E9C57B1A737138F29BF38CFB6527C0A5E95"),
    },
    PK_MSGGAME: {
        "EN": ("MSG_PK/EN/msggame.bin", "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916"),
        "SC": ("MSG_PK/SC/msggame.bin", "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802"),
        "TC": ("MSG_PK/TC/msggame.bin", "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23"),
    },
}


@dataclass(frozen=True)
class Change:
    resource: str
    coordinate: tuple[int, int]
    current_literals: tuple[str, ...]
    target_literals: tuple[str, ...]
    input_record_sha256: str
    input_record_size: int
    removed_commands_hex: tuple[str, ...]
    target_record_sha256: str = ""
    target_record_size: int = 0

    @property
    def coordinate_text(self) -> str:
        return f"{self.coordinate[0]}:{self.coordinate[1]}"


# The intent is a full Korean terminal ending for each static template.  These
# records contain no runtime tokens; their opaque payload is morphology only.
CHANGES = (
    Change(
        BASE_MSGGAME, (6, 3531),
        ("공적 필두가 되다니\n영광스럽기 그지없", "\n앞으로도 가문을 일으켜 세우겠"),
        ("공적의 으뜸이 되다니\n더없이 영광스럽습니다.", "\n앞으로도 가문을 일으키겠습니다."),
        "821E4443296F8613395EC4AB5428C3F8BBE729A38983ADEF6533879C38B219F8", 101,
        ("0143D2010000", "01435A040000"),
        "EEE2E5C6CB676242DD2C7D359807708971D705F47350B9A88B36B6B2693C2E50", 99,
    ),
    Change(
        BASE_MSGGAME, (7, 262),
        ("권유에 감사", "\n사로잡혔던 오명을\n공적으로 씻어 보이겠"),
        ("권유에 감사드립니다.", "\n사로잡혔던 오명을\n공을 세워 씻어 내겠습니다."),
        "3ADA51471E5C06F1333D9066AE97F7C6D4489214292304767410A73CB9095F43", 89,
        ("014384040000", "0143CC010000", "01431E040000"),
        "402BDE9F9D2D16584590C6D261E062DD4234C0E8BF11195EEE4618393AEE8596", 89,
    ),
    Change(
        BASE_MSGGAME, (8, 396),
        ("분부대로\n즉시 이동하겠",),
        ("분부대로\n즉시 이동하겠습니다.",),
        "56C0CDBC7229BBA89BC14B27D17F7C3AEA66A48A5179DEF87A41F319A70A1182", 39,
        ("0143CC010000",),
        "C18D74FF1B33FE7F94DA1DE89EB6FC53D92C19C90CFCFB38BDEFB16D6E87B393", 41,
    ),
    Change(
        BASE_MSGGAME, (15, 2197),
        ("고메고로자라는 별호처럼\n어떠한 청이든 응해 보이겠",),
        ("고메고로자라는 별호답게\n어떤 청에도 응하겠습니다.",),
        "8CB8D444B45AA05F5C93070C9998D2F774102B06DB0C438CAF9671E2A48466FF", 69,
        ("01431E040000",),
        "7693BB87548F9E29BA43932AE22C00E16BAAE97FE1859EC3C6B9715D65BB5E27", 63,
    ),
    Change(
        PK_MSGGAME, (2, 349),
        ("무엇이든 먼저 필요한 것은 돈…\n이곳에서는 지출을 줄이고 재물을 모으겠",),
        ("무엇이든 먼저 필요한 것은 돈…\n이곳에서는 지출을 줄이고 재물을 모으겠다.",),
        "5DD07B5AC08A5D904207C3ED100E789DA8B1B82BAC83FF2D7FC80FCC4B65CF36", 93,
        ("01432A040000",),
        "2215F30093BB42FC4C69210630E6768737D6D0C8025D1D309165242FB0226DF6", 91,
    ),
    Change(
        PK_MSGGAME, (6, 3538),
        ("공적 필두가 되다니\n영광스럽기 그지없", "\n앞으로도 가문을 일으켜 세우겠"),
        ("공적의 으뜸이 되다니\n더없이 영광스럽습니다.", "\n앞으로도 가문을 일으키겠습니다."),
        "279E63E36E5B054E5EA355A7E4F215F4A3C9A58C93796C4D76C9F62AEC00C25B", 101,
        ("0143D8010000", "014366040000"),
        "EEE2E5C6CB676242DD2C7D359807708971D705F47350B9A88B36B6B2693C2E50", 99,
    ),
    Change(
        PK_MSGGAME, (6, 4639),
        ("상대로서 훌륭히", "여기까지 싸웠군", "\n항복에 관해 좋은 방안이 있습니", "까\n내용에 따라 상을 내리겠"),
        ("상대로서 ", "여기까지 잘 싸웠군.", "\n항복에 관해 좋은 방안은 있습니까?", "\n내용에 따라 상을 내리겠다."),
        "8226B811BBCEA739218FF4C17A9180583A108C61FD3F803E0697C13CE462B8FA", 161,
        ("014307000000", "014302020000", "01437A020000", "0143DA020000", "0143F2020000", "01432A040000"),
        "8B11CC04D86600C71CFCDDDDE79700E3BF93A11D35B6FAD084B096C9C8EE5664", 131,
    ),
    Change(
        PK_MSGGAME, (6, 4643),
        (", 위험을 무릅쓰고\n성을 선물로 바치며 항복하겠다니", "\n우리도 성의를 보이겠"),
        ("하하하, 위험을 무릅쓰고\n성을 선물로 바치며 항복하겠다니.", "\n우리도 성의를 보이겠다."),
        "02923030601F1B8A99D01180520A7344C52525A91C5EE9C336BD3CFF91FFD41A", 119,
        ("014345000000", "014338020000", "01432A040000", "014302020000"),
        "A0F7678E8266C82785E64C5249D3700895B00948786C376448846430E602A448", 107,
    ),
    Change(
        PK_MSGGAME, (7, 266),
        ("권유에 감사", "\n사로잡혔던 오명을\n공적으로 씻어 보이겠"),
        ("권유에 감사드립니다.", "\n사로잡혔던 오명을\n공을 세워 씻어 내겠습니다."),
        "C94E9910F4061FC08811A369755EDAD6F4C2B93B655D12A9680F74069F41930F", 89,
        ("014390040000", "0143D2010000", "01432A040000"),
        "402BDE9F9D2D16584590C6D261E062DD4234C0E8BF11195EEE4618393AEE8596", 89,
    ),
    Change(
        PK_MSGGAME, (8, 408),
        ("분부대로\n즉시 이동하겠",),
        ("분부대로\n즉시 이동하겠습니다.",),
        "A40741FA85D87A59AE4F509B08E6DCF1D7020FED6D7649789B624EBC077D6E64", 39,
        ("0143D2010000",),
        "C18D74FF1B33FE7F94DA1DE89EB6FC53D92C19C90CFCFB38BDEFB16D6E87B393", 41,
    ),
    Change(
        PK_MSGGAME, (15, 2227),
        ("고메고로자라는 별호처럼\n어떠한 청이든 응해 보이겠",),
        ("고메고로자라는 별호답게\n어떤 청에도 응하겠습니다.",),
        "AEDBF475FF98DD69B9475B265DE5B9B7B3894DEDB0CC4E392568C6806D836425", 69,
        ("01432A040000",),
        "7693BB87548F9E29BA43932AE22C00E16BAAE97FE1859EC3C6B9715D65BB5E27", 63,
    ),
)


class Wave14Error(ValueError):
    """A source, profile, or byte-preservation contract failed."""


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def records_by_coordinate(packed: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    archive = parse_packed_msggame(packed).archive
    return {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }


def literal_texts(record: MsgGameRecord) -> tuple[str, ...]:
    return tuple(literal.text for literal in parse_record_literals(record))


def opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    cursor = 0
    values: list[bytes] = []
    for literal in parse_record_literals(record):
        values.append(record.data[cursor : literal.marker_offset])
        cursor = literal.marker_end
    values.append(record.data[cursor:])
    return tuple(values)


def morphology_commands(record: MsgGameRecord) -> tuple[str, ...]:
    commands: list[str] = []
    for span in opaque_spans(record):
        offset = 0
        while offset < len(span):
            if span[offset : offset + 2] == MORPHOLOGY_PREFIX:
                if offset + 6 > len(span):
                    raise Wave14Error("truncated 01 43 command")
                commands.append(span[offset : offset + 6].hex().upper())
                offset += 6
            else:
                offset += 1
    return tuple(commands)


def stripped_opaque_spans(record: MsgGameRecord) -> tuple[bytes, ...]:
    """Remove only well-formed ``01 43`` commands from every opaque span."""
    values: list[bytes] = []
    for span in opaque_spans(record):
        output = bytearray()
        offset = 0
        while offset < len(span):
            if span[offset : offset + 2] == MORPHOLOGY_PREFIX:
                if offset + 6 > len(span):
                    raise Wave14Error("truncated 01 43 command")
                offset += 6
                continue
            output.append(span[offset])
            offset += 1
        values.append(bytes(output))
    return tuple(values)


def profile_hashes(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for relative in PROFILE_PATHS:
        path = root / relative
        if not path.is_file():
            raise Wave14Error(f"profile resource is absent: {relative}")
        result[relative] = sha256_path(path)
    return result


def assert_profile(root: Path, expected: Mapping[str, str], label: str) -> None:
    actual = profile_hashes(root)
    if actual != dict(expected):
        mismatch = {
            path: {"expected": expected.get(path), "actual": actual.get(path)}
            for path in PROFILE_PATHS
            if actual.get(path) != expected.get(path)
        }
        raise Wave14Error(f"{label} profile mismatch: {json.dumps(mismatch, sort_keys=True)}")


def validate_text(value: str, coordinate: str, label: str) -> None:
    if not value or "\x1b" in value or "%" in value:
        raise Wave14Error(f"{coordinate} {label} contains a runtime marker or is empty")
    encoded = value.encode("utf-16-le")
    if LITERAL_START in encoded or LITERAL_END in encoded:
        raise Wave14Error(f"{coordinate} {label} encodes a reserved marker")
    for character in value:
        if character != "\n" and unicodedata.category(character) == "Cc":
            raise Wave14Error(f"{coordinate} {label} contains control U+{ord(character):04X}")


def line_upper_bound_px(value: str) -> list[int]:
    """Conservative 48px-wide / 24px-space diagnostic for three-line text."""
    return [sum(24 if character == " " else 48 for character in line) for line in value.split("\n")]


def rebuild_static_record(record: MsgGameRecord, change: Change) -> bytes:
    payload = bytearray()
    for text in change.target_literals:
        payload.extend(LITERAL_START)
        payload.extend(text.encode("utf-16-le"))
        payload.extend(LITERAL_END)
    payload.extend(RECORD_TERMINATOR)
    return bytes(payload)


def reference_records(steam_root: Path) -> tuple[dict[str, dict[tuple[int, int], MsgGameRecord]], dict[str, dict[str, dict[tuple[int, int], MsgGameRecord]]]]:
    jp: dict[str, dict[tuple[int, int], MsgGameRecord]] = {}
    contexts: dict[str, dict[str, dict[tuple[int, int], MsgGameRecord]]] = {}
    for resource, (path, expected) in PC_JP_SOURCES.items():
        if not path.is_file() or sha256_path(path) != expected:
            raise Wave14Error(f"pristine PC JP source hash differs: {resource}")
        jp[resource] = records_by_coordinate(path.read_bytes())
        contexts[resource] = {}
        for language, (relative, context_hash) in PC_CONTEXTS[resource].items():
            context = steam_root / relative
            if not context.is_file() or sha256_path(context) != context_hash:
                raise Wave14Error(f"PC {language} context hash differs: {resource}")
            contexts[resource][language] = records_by_coordinate(context.read_bytes())
    return jp, contexts


def validate_change(
    change: Change,
    current: Mapping[tuple[int, int], MsgGameRecord],
    jp: Mapping[tuple[int, int], MsgGameRecord],
    contexts: Mapping[str, Mapping[tuple[int, int], MsgGameRecord]],
    *,
    require_pinned_targets: bool,
) -> tuple[bytes, dict[str, Any]]:
    coordinate = change.coordinate_text
    record = current.get(change.coordinate)
    source = jp.get(change.coordinate)
    if record is None or source is None:
        raise Wave14Error(f"missing current or PC JP source record: {change.resource} {coordinate}")
    if len(record.data) != change.input_record_size or sha256_bytes(record.data) != change.input_record_sha256:
        raise Wave14Error(f"current record preimage differs: {change.resource} {coordinate}")
    if literal_texts(record) != change.current_literals:
        raise Wave14Error(f"current literals differ: {change.resource} {coordinate}")
    if len(change.current_literals) != len(change.target_literals):
        raise Wave14Error(f"literal marker count differs: {change.resource} {coordinate}")
    if morphology_commands(record) != change.removed_commands_hex:
        raise Wave14Error(f"current morphology command list differs: {change.resource} {coordinate}")
    if morphology_commands(source) != change.removed_commands_hex:
        raise Wave14Error(f"PC JP morphology command list differs: {change.resource} {coordinate}")
    if stripped_opaque_spans(record) != tuple(b"" for _ in change.current_literals) + (RECORD_TERMINATOR,):
        raise Wave14Error(f"record contains non-morphology opaque bytes: {change.resource} {coordinate}")
    for language, rows in contexts.items():
        context = rows.get(change.coordinate)
        if context is None or morphology_commands(context):
            raise Wave14Error(f"PC {language} context retains morphology: {change.resource} {coordinate}")
    current_text = "".join(change.current_literals)
    target_text = "".join(change.target_literals)
    validate_text(current_text, coordinate, "current text")
    validate_text(target_text, coordinate, "target text")
    if current_text.count("\n") != target_text.count("\n"):
        raise Wave14Error(f"manual line count changed: {change.resource} {coordinate}")
    widths = line_upper_bound_px(target_text)
    if len(widths) > 3:
        raise Wave14Error(f"target exceeds three explicit lines: {change.resource} {coordinate}")
    rebuilt = rebuild_static_record(record, change)
    if len(rebuilt) != change.target_record_size and require_pinned_targets:
        raise Wave14Error(f"target record size differs: {change.resource} {coordinate}")
    if change.target_record_sha256 and sha256_bytes(rebuilt) != change.target_record_sha256:
        raise Wave14Error(f"target record SHA-256 differs: {change.resource} {coordinate}")
    if require_pinned_targets and (not change.target_record_sha256 or not change.target_record_size):
        raise Wave14Error(f"target record is not pinned: {change.resource} {coordinate}")
    return rebuilt, {
        "resource": change.resource,
        "coordinate": coordinate,
        "input_record_sha256": change.input_record_sha256,
        "target_record_sha256": sha256_bytes(rebuilt),
        "input_record_size": len(record.data),
        "target_record_size": len(rebuilt),
        "removed_opaque_commands_hex": list(change.removed_commands_hex),
        "manual_line_count": target_text.count("\n") + 1,
        "line_upper_bound_px": widths,
        "pc_context_languages_without_0143": sorted(contexts),
    }


def prepare_candidate(steam_root: Path, *, require_pinned_targets: bool = True) -> tuple[dict[str, bytes], dict[str, Any]]:
    steam_root = steam_root.resolve(strict=True)
    assert_profile(steam_root, INPUT_SHA256, "current Steam")
    jp, contexts = reference_records(steam_root)
    grouped: dict[str, dict[tuple[int, int], bytes]] = {path: {} for path in CHANGED_PATHS}
    audit_rows: list[dict[str, Any]] = []
    for change in CHANGES:
        if change.resource not in grouped or change.coordinate in grouped[change.resource]:
            raise Wave14Error(f"duplicate or unsupported change: {change.resource} {change.coordinate_text}")
        current = records_by_coordinate((steam_root / change.resource).read_bytes())
        rebuilt, row = validate_change(
            change, current, jp[change.resource], contexts[change.resource],
            require_pinned_targets=require_pinned_targets,
        )
        grouped[change.resource][change.coordinate] = rebuilt
        audit_rows.append(row)
    output: dict[str, bytes] = {}
    for resource in CHANGED_PATHS:
        before = (steam_root / resource).read_bytes()
        after = rebuild_packed_msggame(before, grouped[resource])
        old_records = records_by_coordinate(before)
        new_records = records_by_coordinate(after)
        changed = {coordinate for coordinate in old_records if old_records[coordinate].data != new_records[coordinate].data}
        if changed != set(grouped[resource]):
            raise Wave14Error(f"unexpected changed record set: {resource} {sorted(changed)}")
        output[resource] = after
    target_hashes = {**INPUT_SHA256, **{resource: sha256_bytes(value) for resource, value in output.items()}}
    if require_pinned_targets and target_hashes != TARGET_SHA256:
        mismatch = {
            resource: {"expected": TARGET_SHA256[resource], "actual": target_hashes[resource]}
            for resource in PROFILE_PATHS
            if TARGET_SHA256[resource] != target_hashes[resource]
        }
        raise Wave14Error(f"target profile is not pinned: {json.dumps(mismatch, sort_keys=True)}")
    audit = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "platform": "Steam PC",
            "pristine_pc_japanese_read": True,
            "pc_en_sc_tc_context_read": True,
            "switch_korean_read": False,
            "steam_game_resource_written": False,
        },
        "input_sha256": INPUT_SHA256,
        "target_sha256": target_hashes,
        "records": audit_rows,
    }
    return output, audit


def verify_installed(steam_root: Path) -> None:
    """Require the exact applied Wave 14 target without rebuilding a candidate."""
    steam_root = steam_root.resolve(strict=True)
    assert_profile(steam_root, TARGET_SHA256, "installed Steam")
    for change in CHANGES:
        record = records_by_coordinate((steam_root / change.resource).read_bytes()).get(change.coordinate)
        if record is None:
            raise Wave14Error(f"installed target lacks record: {change.resource} {change.coordinate_text}")
        if sha256_bytes(record.data) != change.target_record_sha256 or len(record.data) != change.target_record_size:
            raise Wave14Error(f"installed target record differs: {change.resource} {change.coordinate_text}")
        if literal_texts(record) != change.target_literals or morphology_commands(record):
            raise Wave14Error(f"installed target literal/command differs: {change.resource} {change.coordinate_text}")
        if opaque_spans(record) != tuple(b"" for _ in change.target_literals) + (RECORD_TERMINATOR,):
            raise Wave14Error(f"installed target opaque layout differs: {change.resource} {change.coordinate_text}")


def require_tmp(path: Path, label: str) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=False)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Wave14Error(f"{label} must stay below {root}") from exc
    return resolved


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def build_candidate(steam_root: Path, output_root: Path, audit_path: Path, manifest_path: Path) -> dict[str, Any]:
    output_root = require_tmp(output_root, "candidate output")
    audit_path = require_tmp(audit_path, "audit output")
    manifest_path = require_tmp(manifest_path, "manifest output")
    if output_root.exists() or audit_path.exists() or manifest_path.exists():
        raise Wave14Error("candidate output, audit, or manifest already exists")
    output, audit = prepare_candidate(steam_root)
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{output_root.name}.", dir=output_root.parent))
    try:
        for relative in PROFILE_PATHS:
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if relative in output:
                destination.write_bytes(output[relative])
            else:
                shutil.copy2(steam_root / relative, destination)
        assert_profile(stage, TARGET_SHA256, "candidate")
        os.replace(stage, output_root)
        audit_bytes = (json.dumps(audit, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
        atomic_write(audit_path, audit_bytes)
        manifest = {
            "schema": SCHEMA,
            "transaction_id": "pc-dialogue-quality-wave14-static-inflection-v1",
            "profile_paths": list(PROFILE_PATHS),
            "changed_paths": list(CHANGED_PATHS),
            "input_sha256": INPUT_SHA256,
            "output_sha256": TARGET_SHA256,
            "pinned_output_sha256": TARGET_SHA256,
            "audit_sha256": sha256_bytes(audit_bytes),
            "record_count": len(CHANGES),
            "steam_write_capability": "absent",
            "real_game_qa_required_before_release": True,
        }
        atomic_write(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        return manifest
    except Exception:
        if stage.exists():
            shutil.rmtree(stage)
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    hash_parser = sub.add_parser("hash", help="calculate/verify the deterministic target")
    hash_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    verify_parser = sub.add_parser("verify-installed", help="require the exact applied Wave 14 target")
    verify_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser = sub.add_parser("build", help="write a private candidate only below tmp")
    build_parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    build_parser.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
    build_parser.add_argument("--audit-path", type=Path, default=TMP_ROOT / "audit.v1.json")
    build_parser.add_argument("--manifest-path", type=Path, default=TMP_ROOT / "build_manifest.v1.json")
    args = parser.parse_args(argv)
    try:
        if args.command == "hash":
            output, audit = prepare_candidate(args.steam_root)
            print(json.dumps({"status": "ok", "target_sha256": audit["target_sha256"], "records": audit["records"], "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
            return 0
        if args.command == "verify-installed":
            verify_installed(args.steam_root)
            print(json.dumps({"status": "ok", "installed_target_sha256": TARGET_SHA256, "steam_write_capability": "absent"}, ensure_ascii=False, sort_keys=True))
            return 0
        manifest = build_candidate(args.steam_root, args.output_root, args.audit_path, args.manifest_path)
        print(json.dumps({"status": "ok", "manifest": manifest, "steam_write_capability": "absent"}, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, Wave14Error) as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
