#!/usr/bin/env python3
"""Build a private Wave 98 block-13/14 static-dialogue correction candidate.

Only the exact Wave 97 private candidate is accepted as Korean input.  This
wave corrects five literal slots: Base/PK 13:213 uses the fixed person-dialogue
three-line contract, while PK 13:563, 13:573, and 13:590 retain their existing
multi-line tutorial/help layout and require real-game UI QA before deployment.
The script only writes its private candidate beneath ``tmp``; it has no Steam,
Git, network, or release operation.
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

BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_ORDER = (BASE_RESOURCE, PK_RESOURCE)

W27_HELPER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave27_static_quality_v1"
    / "build_pc_dialogue_quality_wave27_static_quality_v1.py"
)
W27_HELPER_SHA256 = "D63EA16EECF77F769C3B4AE21579A6C1227531E7FBDD0C07BB83C3E2B3A41438"

W97_BUILDER = (
    REPO
    / "workstreams"
    / "pc_dialogue_quality_wave97_pk_security_development_static_v1"
    / "build_pc_dialogue_quality_wave97_pk_security_development_static_v1.py"
)
W97_BUILDER_SHA256 = "A4D7D425ACD93C5EEBCA1F35BB6197E3CD917C46DACC8B97D55313BA5404C3B2"
W97_CANDIDATE_ROOT = (
    REPO / "tmp" / "pc_dialogue_quality_wave97_pk_security_development_static_v1" / "candidate"
)

SCHEMA = "nobu16.kr.pc-dialogue-quality-wave98-blocks13-14-static.v1"
AUDIT_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave98-blocks13-14-static-audit.v1"
MANIFEST_SCHEMA = "nobu16.kr.pc-dialogue-quality-wave98-blocks13-14-static-manifest.v1"

RAW_G1N_FULL_WIDTH_ADVANCE = 48
RAW_G1N_HALF_WIDTH_ADVANCE = 24
MAX_PERSON_DIALOGUE_RAW_LINE_PX = 888
MAX_PERSON_DIALOGUE_LINES = 3

INPUT_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "size": 1_504_458,
        "sha256": "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2",
        "raw_size": 1_498_556,
        "raw_sha256": "213BA9519E7E3C4B89BA300AB110CBFB3544FAE0407F2CF66906157761C3FDC1",
    },
    PK_RESOURCE: {
        "size": 1_806_687,
        "sha256": "E507D55F2FECE844FA3AF1FBA213DE2DB7D0F4113082190615DA9C15D3906540",
        "raw_size": 1_799_604,
        "raw_sha256": "599C1415FA511E934303FFF7B15BB92834DAB90C54365A7FD62E6BB12C850F67",
    },
}

W97_EVIDENCE: Mapping[str, Mapping[str, Any]] = {
    "audit.v1.json": {
        "size": 18_710,
        "sha256": "54BF4C8A0BC63C91CEEE91652D33D680E56717C5E05D1748A6F1C2E2BC12E5A2",
    },
    "build_manifest.v1.json": {
        "size": 2_733,
        "sha256": "AA242F0EBFCB3E5BEB1F046D87BB3F0C6DD274380A901550367A7A0DCC824AEB",
    },
}

TARGET_PROFILES: Mapping[str, Mapping[str, Any]] = {
    BASE_RESOURCE: {
        "size": 1_504_462,
        "sha256": "9F6D6FE75FA03818C1E93139C4957B5A8F5C8198D54909F9EE0CC78C7A4446D3",
        "raw_size": 1_498_560,
        "raw_sha256": "CE1AFCC37C914ED47ACA974781E408F235B2D6F28D656E6DB0B39EB716B07399",
    },
    PK_RESOURCE: {
        "size": 1_806_699,
        "sha256": "1CE593470463A09DD0547CCF04AAEEB2EC142D9FF5DBBEC7D01A0D648186A24A",
        "raw_size": 1_799_616,
        "raw_sha256": "85DF2ECCE4612BAD44F0661647D30889E7D43E3E167964953FBDAD2F5DF27F0D",
    },
}

STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DIRECT_PATHS: Mapping[str, Path] = {
    "JP_BASE": Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
    "JP_PK": (
        STEAM_ROOT
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msggame.bin"
    ),
    "EN": STEAM_ROOT / "MSG_PK" / "EN" / "msggame.bin",
    "SC": STEAM_ROOT / "MSG_PK" / "SC" / "msggame.bin",
    "TC": STEAM_ROOT / "MSG_PK" / "TC" / "msggame.bin",
}
DIRECT_FILE_SHA256: Mapping[str, str] = {
    "JP_BASE": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    "JP_PK": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "EN": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "SC": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "TC": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}


class Wave98Error(RuntimeError):
    """Raised when a source, structure, layout, or output contract drifts."""


@dataclass(frozen=True)
class Change:
    name: str
    resource: str
    coordinate: tuple[int, int]
    target_literal: str
    current_record_sha256: str
    current_record_size: int
    direct_record_sha256: Mapping[str, str]
    layout_kind: str
    semantic_reason: str


@dataclass(frozen=True)
class CandidateBundle:
    packed: Mapping[str, bytes]
    raw: Mapping[str, bytes]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


COUNTY_FACILITY = (
    "군의 개발이 진행되면 더욱 효과가\n"
    "큰 「성하 시설」을 건설할 수\n"
    "있게 됩니다. 어서 지어 봅시다."
)

BATTLE_COMMANDS = (
    "무장들은 승리와 공명을 위해 스스로 판단해 부대를 움직이고 싸웁니다.\n"
    "\n"
    "하지만 전황이 변하면 판단을 구해 오기도 합니다.\n"
    "기회와 위기에 어떻게 대응하느냐에 따라 승패가 갈립니다."
)

SIEGE_AUTHORITY = (
    "【공성전으로 인한 위풍】\n"
    "승패에 따라 위풍이 발생합니다.\n"
    "적의 침공을 막아 내면 반격의 기회가 됩니다.\n"
    "하지만 적에게 제압당하면 적의 위풍이 발생하므로 주의하십시오.\n"
    "※방위 승리 때 발생한 위풍으로는 적 성의 배반이 일어나지 않습니다.\n"
    "\n"
    "방위 거점은 주변에서 발생한 위풍의 영향을 받지 않고 그 확산을 막습니다.\n"
    "방위 거점을 잘 설정하면 패배의 영향을 최소화할 수 있습니다."
)


def direct_hashes(*, jp_primary: str, coordinate: tuple[int, int]) -> Mapping[str, str]:
    """The Base 13:213 row uses its matching PK locale rows as PC context."""

    if coordinate == (13, 213):
        return {
            "JP_BASE": "35DE4BA566F48F116534C65B2339D9B4617596FBE4D70691D7EBF55E9F13BFC5",
            "JP_PK": "35DE4BA566F48F116534C65B2339D9B4617596FBE4D70691D7EBF55E9F13BFC5",
            "EN": "8A1B64D0680E68A14DB42EBBA2A8273C46CD21AB3D2B2AB557F361227D57603E",
            "SC": "3F687DC8D0910B9E938E6510E2EB20434D41C5A8951A7F651318E4EE0C5329F9",
            "TC": "F0B744BD8AC26A3341441CBFDE5BFBB4E43136B6947F4F86C07E729117DD5BD6",
        }
    if coordinate in ((13, 563), (13, 573)):
        return {
            "JP_PK": "483EF52CEB68DDABA5D740BE8029BFA2ED9CDFA55392865643E99921893BB1D0",
            "EN": (
                "DC6843D6284AD1C49A2C558D7F15740AC3B575A7600B917915D3570AAB219713"
                if coordinate == (13, 563)
                else "4D3A4F5C3D6899E9618F7D4899D4F717F69753690044417D0587EFC038B76D29"
            ),
            "SC": "63F75D615CADCA48178D2A272765E381F0F0487856195E11F99884BB9A5BD6DB",
            "TC": "E4C4BE7322CC3451D6DC537FC6B4721A10A61FBF664BEA53A36D8B327F0C32E1",
        }
    if coordinate == (13, 590):
        return {
            "JP_PK": "E45105C404AAA71BFE58EBDE2D6BD2815A7CEF4BC23A0340184A3BF2D2DF3C41",
            "EN": "C59BD0381D3321D9C80F40D0020102C7C5BF04093AF20145401743C383CAC076",
            "SC": "22D7FC7301BC9E622E458D9CC748939C9BE0E45F974DC7064922C19E56B61D0A",
            "TC": "6BDC218C5DC43E54030FD47F2B114314C936F89C8A6E54989187A4CB24DDF7A4",
        }
    raise Wave98Error(f"unmapped direct source coordinate: {jp_primary} {coordinate}")


CHANGES = (
    Change(
        "county_facility_layout_base",
        BASE_RESOURCE,
        (13, 213),
        COUNTY_FACILITY,
        "048AE51B466D64576CB38BD478B9F5B7DB0DEC52960A2C9D44DE2AC92C3EF546",
        111,
        direct_hashes(jp_primary="JP_BASE", coordinate=(13, 213)),
        "fixed_person_3line_888px",
        "한국어 어절을 분리했던 ‘가능해\\n집니다’를 문맥상 세 줄로 재배치하고, "
        "성하 시설을 건설할 수 있다는 원문의 가능 표현을 복원한다.",
    ),
    Change(
        "county_facility_layout_pk",
        PK_RESOURCE,
        (13, 213),
        COUNTY_FACILITY,
        "048AE51B466D64576CB38BD478B9F5B7DB0DEC52960A2C9D44DE2AC92C3EF546",
        111,
        direct_hashes(jp_primary="JP_PK", coordinate=(13, 213)),
        "fixed_person_3line_888px",
        "한국어 어절을 분리했던 ‘가능해\\n집니다’를 문맥상 세 줄로 재배치하고, "
        "성하 시설을 건설할 수 있다는 원문의 가능 표현을 복원한다.",
    ),
    Change(
        "battle_commands_563",
        PK_RESOURCE,
        (13, 563),
        BATTLE_COMMANDS,
        "A342310C003162656CF9B2EE4176168C5C0DD0F6D7DA85753F489C2AA6492610",
        205,
        direct_hashes(jp_primary="JP_PK", coordinate=(13, 563)),
        "tutorial_help_manual_lines_preserved",
        "判断を求めてくる와 EN의 ‘request your commands’를 ‘도움을 요청’으로 "
        "약화하지 않고, 플레이어의 판단을 구한다는 뜻으로 바로잡는다.",
    ),
    Change(
        "battle_commands_573",
        PK_RESOURCE,
        (13, 573),
        BATTLE_COMMANDS,
        "A342310C003162656CF9B2EE4176168C5C0DD0F6D7DA85753F489C2AA6492610",
        205,
        direct_hashes(jp_primary="JP_PK", coordinate=(13, 573)),
        "tutorial_help_manual_lines_preserved",
        "判断を求めてくる와 EN의 ‘request your commands’를 ‘도움을 요청’으로 "
        "약화하지 않고, 플레이어의 판단을 구한다는 뜻으로 바로잡는다.",
    ),
    Change(
        "siege_authority_590",
        PK_RESOURCE,
        (13, 590),
        SIEGE_AUTHORITY,
        "1D273C869EDB5BDD5963128B9A950B5E52C5C04D2D9CB7A02247FD5DDE95F0B3",
        425,
        direct_hashes(jp_primary="JP_PK", coordinate=(13, 590)),
        "tutorial_help_manual_lines_preserved",
        "威風が発生する와 敵城の寝返りは起こらない를 ‘위풍 발생’과 "
        "‘적 성의 배반 없음’으로 복원하고, 방위 거점이 확산을 막는다는 뜻을 보존한다.",
    ),
)


def require(condition: bool, label: str) -> None:
    if not condition:
        raise Wave98Error(label)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def require_private(path: Path, label: str) -> Path:
    resolved = path.resolve()
    root = TMP_ROOT.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as error:
        raise Wave98Error(f"private path escapes tmp root: {label}") from error
    if any(part.casefold() == "steam" for part in resolved.parts):
        raise Wave98Error(f"private path points to Steam: {label}")
    return resolved


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "pinned Wave 27 parser is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "pinned Wave 27 parser differs")
    spec = importlib.util.spec_from_file_location("wave98_w27", W27_HELPER)
    require(spec is not None and spec.loader is not None, "cannot import Wave 27 parser")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()


def marker_hex(record: Any) -> list[list[str]]:
    return [[span.hex().upper() for span in group] for group in W27.marker_topology(record)]


def opaque_hex(record: Any) -> list[str]:
    return [span.hex().upper() for span in W27.opaque_spans(record)]


def opaque_02xx_prefixes(record: Any) -> list[str]:
    found: list[str] = []
    for span in W27.opaque_spans(record):
        for index in range(len(span) - 1):
            if span[index] == 0x02:
                found.append(span[index:index + 2].hex().upper())
    return found


def manual_layout_topology(value: str) -> Mapping[str, Any]:
    lines = value.split("\n")
    return {
        "manual_line_count": len(lines),
        "manual_line_break_count": value.count("\n"),
        "blank_line_indexes_zero_based": [index for index, line in enumerate(lines) if not line],
    }


def measured_lines(value: str, advance: Any) -> Mapping[str, Any]:
    rows: list[dict[str, Any]] = []
    fallback: set[str] = set()
    for display_string in value.split("\n"):
        raw_width = 0
        full_width_count = 0
        half_width_count = 0
        for char in display_string:
            raw_advance, used_fallback = advance(char)
            if raw_advance == RAW_G1N_FULL_WIDTH_ADVANCE:
                full_width_count += 1
            elif raw_advance == RAW_G1N_HALF_WIDTH_ADVANCE:
                half_width_count += 1
            else:
                raise Wave98Error(
                    f"unexpected raw G1N advance U+{ord(char):04X}: {raw_advance}"
                )
            raw_width += raw_advance
            if used_fallback:
                fallback.add(f"U+{ord(char):04X}")
        rows.append(
            {
                "display_string": display_string,
                "raw_g1n_width_px": raw_width,
                "full_width_character_count": full_width_count,
                "half_width_character_count": half_width_count,
                "exceeds_888px": raw_width > MAX_PERSON_DIALOGUE_RAW_LINE_PX,
            }
        )
    return {
        "line_count": len(rows),
        "raw_g1n_line_widths_px": [row["raw_g1n_width_px"] for row in rows],
        "max_raw_g1n_width_px": max((row["raw_g1n_width_px"] for row in rows), default=0),
        "any_line_exceeds_888px": any(row["exceeds_888px"] for row in rows),
        "wide_fallback_codepoints": sorted(fallback),
        "lines": rows,
    }


def record_evidence(record: Any) -> Mapping[str, Any]:
    literals = W27.literal_texts(record)
    return {
        "sha256": sha256_bytes(record.data),
        "size": len(record.data),
        "literal_count": len(literals),
        "visible_literal_utf16le_sha256": [sha256_bytes(value.encode("utf-16le")) for value in literals],
        "visible_literals": list(literals),
        "marker_topology_hex": marker_hex(record),
        "opaque_spans_hex": opaque_hex(record),
        "complete_0143_commands": list(W27.complete_0143_commands(W27.opaque_spans(record))),
        "runtime_02xx_opcodes": opaque_02xx_prefixes(record),
        "terminator": record.data.endswith(W27.RECORD_TERMINATOR),
    }


def load_predecessors() -> tuple[dict[str, bytes], dict[str, Mapping[tuple[int, int], Any]], Mapping[str, Any]]:
    require(W97_BUILDER.is_file(), "pinned Wave 97 builder is absent")
    require(sha256_path(W97_BUILDER) == W97_BUILDER_SHA256, "pinned Wave 97 builder differs")
    evidence: dict[str, Any] = {}
    for name, profile in W97_EVIDENCE.items():
        path = W97_CANDIDATE_ROOT / name
        require(path.is_file(), f"Wave 97 evidence is absent: {name}")
        require(path.stat().st_size == profile["size"], f"Wave 97 evidence size differs: {name}")
        require(sha256_path(path) == profile["sha256"], f"Wave 97 evidence hash differs: {name}")
        evidence[name] = {"path": relative(path), **profile}

    packed_by_resource: dict[str, bytes] = {}
    records_by_resource: dict[str, Mapping[tuple[int, int], Any]] = {}
    predecessor_resources: dict[str, Any] = {}
    for resource in RESOURCE_ORDER:
        path = W97_CANDIDATE_ROOT / resource
        profile = INPUT_PROFILES[resource]
        require(path.is_file(), f"Wave 97 predecessor is absent: {resource}")
        packed = path.read_bytes()
        require(len(packed) == profile["size"], f"Wave 97 predecessor size differs: {resource}")
        require(sha256_bytes(packed) == profile["sha256"], f"Wave 97 predecessor hash differs: {resource}")
        W27.validate_raw_roundtrip(packed, f"Wave 98 predecessor {resource}")
        _header, raw = W27.decompress_wrapper(packed)
        require(len(raw) == profile["raw_size"], f"Wave 97 predecessor raw size differs: {resource}")
        require(sha256_bytes(raw) == profile["raw_sha256"], f"Wave 97 predecessor raw hash differs: {resource}")
        packed_by_resource[resource] = packed
        records_by_resource[resource] = W27.records_by_coordinate(packed)
        predecessor_resources[resource] = {
            "path": relative(path),
            **profile,
        }
    return packed_by_resource, records_by_resource, {
        "builder": {"path": relative(W97_BUILDER), "sha256": W97_BUILDER_SHA256},
        "candidate_resources": predecessor_resources,
        "candidate_evidence": evidence,
    }


def load_direct_sources() -> tuple[dict[str, Mapping[tuple[int, int], Any]], Mapping[str, str]]:
    records: dict[str, Mapping[tuple[int, int], Any]] = {}
    hashes: dict[str, str] = {}
    for language, path in DIRECT_PATHS.items():
        require(path.is_file(), f"direct PC source is absent: {language}")
        actual = sha256_path(path)
        require(actual == DIRECT_FILE_SHA256[language], f"direct PC source differs: {language}")
        records[language] = W27.records_by_coordinate(path.read_bytes())
        hashes[language] = actual
    return records, hashes


def validate_direct_context(change: Change, sources: Mapping[str, Mapping[tuple[int, int], Any]]) -> Mapping[str, Any]:
    expected_languages = set(change.direct_record_sha256)
    require(expected_languages.issubset(set(sources)), f"direct language scope differs: {change.name}")
    anchors: dict[str, Any] = {}
    for language, expected_hash in change.direct_record_sha256.items():
        record = sources[language].get(change.coordinate)
        require(record is not None, f"direct record is absent: {change.name} {language}")
        require(sha256_bytes(record.data) == expected_hash, f"direct record differs: {change.name} {language}")
        literals = W27.literal_texts(record)
        require(len(literals) == 1 and literals[0], f"direct literal topology differs: {change.name} {language}")
        anchors[language] = {
            "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
            "record_sha256": expected_hash,
            "visible_literal_utf16le_sha256": sha256_bytes(literals[0].encode("utf-16le")),
            "visible_literal": literals[0],
        }
    if change.resource == BASE_RESOURCE:
        require("JP_BASE" in anchors and {"JP_PK", "EN", "SC", "TC"}.issubset(anchors), "Base locale context is incomplete")
        anchors["cross_resource_locale_context"] = {
            "pk_coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
            "reason": "Base has no installed direct EN resource; same-coordinate direct PK JP/EN/SC/TC records are pinned as cross-locale context.",
        }
    else:
        require({"JP_PK", "EN", "SC", "TC"}.issubset(anchors), "PK locale context is incomplete")
    return anchors


def validate_change(change: Change, before: Any, sources: Mapping[str, Mapping[tuple[int, int], Any]], advance: Any) -> tuple[bytes, Mapping[str, Any]]:
    label = f"{change.resource}:{change.coordinate[0]}:{change.coordinate[1]}"
    require(sha256_bytes(before.data) == change.current_record_sha256, f"current record hash differs: {label}")
    require(len(before.data) == change.current_record_size, f"current record size differs: {label}")
    current_literals = W27.literal_texts(before)
    require(len(current_literals) == 1 and current_literals[0], f"current literal topology differs: {label}")
    require(before.data.endswith(W27.RECORD_TERMINATOR), f"current terminator differs: {label}")
    require(not W27.complete_0143_commands(W27.opaque_spans(before)), f"0143 command is forbidden: {label}")
    require(not opaque_02xx_prefixes(before), f"runtime 02xx opcode is forbidden: {label}")

    current_topology = manual_layout_topology(current_literals[0])
    target_topology = manual_layout_topology(change.target_literal)
    require(current_topology["manual_line_break_count"] == target_topology["manual_line_break_count"], f"manual LF count differs: {label}")
    if change.layout_kind == "fixed_person_3line_888px":
        require(target_topology["manual_line_count"] == MAX_PERSON_DIALOGUE_LINES, f"fixed person line count differs: {label}")
    elif change.layout_kind == "tutorial_help_manual_lines_preserved":
        require(current_topology == target_topology, f"tutorial manual layout differs: {label}")
    else:
        raise Wave98Error(f"unknown layout kind: {change.layout_kind}")

    layout = measured_lines(change.target_literal, advance)
    require(not layout["wide_fallback_codepoints"], f"target fallback glyph differs: {label}")
    fixed_contract: Mapping[str, Any]
    if change.layout_kind == "fixed_person_3line_888px":
        require(layout["line_count"] == MAX_PERSON_DIALOGUE_LINES, f"fixed person line count changed: {label}")
        require(not layout["any_line_exceeds_888px"], f"fixed person line exceeds 888px: {label}")
        fixed_contract = {
            "applied": True,
            "max_raw_g1n_line_width_px": MAX_PERSON_DIALOGUE_RAW_LINE_PX,
            "max_lines": MAX_PERSON_DIALOGUE_LINES,
            "passes": True,
        }
    else:
        fixed_contract = {
            "applied": False,
            "reason": "Multi-sentence tutorial/help text uses a separate widget/manual layout; fixed person-dialogue 3-line/888px rule is not transferred.",
            "steam_pre_release_ui_qa_required": True,
            "passes": None,
        }

    rebuilt = W27.rebuild_static_record(before, (change.target_literal,))
    after = W27.MsgGameRecord(before.block_id, before.record_id, before.relative_offset, rebuilt)
    require(W27.literal_texts(after) == (change.target_literal,), f"target literal differs: {label}")
    require(W27.marker_topology(after) == W27.marker_topology(before), f"marker topology differs: {label}")
    require(W27.opaque_spans(after) == W27.opaque_spans(before), f"opaque structure differs: {label}")
    require(after.data.endswith(W27.RECORD_TERMINATOR), f"target terminator differs: {label}")
    require(not W27.complete_0143_commands(W27.opaque_spans(after)), f"0143 command introduced: {label}")
    require(not opaque_02xx_prefixes(after), f"runtime 02xx opcode introduced: {label}")
    direct_context = validate_direct_context(change, sources)

    return rebuilt, {
        "name": change.name,
        "resource": change.resource,
        "coordinate": f"{change.coordinate[0]}:{change.coordinate[1]}",
        "semantic_repair": change.semantic_reason,
        "layout_kind": change.layout_kind,
        "current_record": record_evidence(before),
        "target_record": record_evidence(after),
        "current_manual_layout": current_topology,
        "target_manual_layout": target_topology,
        "fixed_person_3line_888px_contract": fixed_contract,
        "target_layout_report": layout,
        "direct_pc_jp_en_sc_tc_context": direct_context,
    }


def profile_for(packed: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "size": len(packed),
        "sha256": sha256_bytes(packed),
        "raw_size": len(raw),
        "raw_sha256": sha256_bytes(raw),
    }


def prepare_candidate(*, pin_outputs: bool = True) -> CandidateBundle:
    packed_before, records_before, predecessor = load_predecessors()
    sources, source_file_hashes = load_direct_sources()
    advance, font = W27.load_font_advance()
    replacements: dict[str, dict[tuple[int, int], bytes]] = {resource: {} for resource in RESOURCE_ORDER}
    rows: list[Mapping[str, Any]] = []

    for change in CHANGES:
        before = records_before[change.resource].get(change.coordinate)
        require(before is not None, f"predecessor coordinate is absent: {change.name}")
        require(change.coordinate not in replacements[change.resource], f"duplicate target coordinate: {change.name}")
        replacement, row = validate_change(change, before, sources, advance)
        replacements[change.resource][change.coordinate] = replacement
        rows.append(row)

    packed_after: dict[str, bytes] = {}
    raw_after: dict[str, bytes] = {}
    output_profiles: dict[str, Mapping[str, Any]] = {}
    non_target_counts: dict[str, int] = {}
    for resource in RESOURCE_ORDER:
        candidate = W27.rebuild_packed_msggame(packed_before[resource], replacements[resource])
        W27.validate_raw_roundtrip(candidate, f"Wave 98 candidate {resource}")
        _header, raw = W27.decompress_wrapper(candidate)
        after_records = W27.records_by_coordinate(candidate)
        before_records = records_before[resource]
        require(set(before_records) == set(after_records), f"record coordinate set differs: {resource}")
        actual_changed = {
            coordinate
            for coordinate, before in before_records.items()
            if before.data != after_records[coordinate].data
        }
        expected_changed = set(replacements[resource])
        require(actual_changed == expected_changed, f"changed record scope differs: {resource}")
        for coordinate, before in before_records.items():
            if coordinate not in expected_changed:
                require(before.data == after_records[coordinate].data, f"non-target record changed: {resource}:{coordinate}")
        packed_after[resource] = candidate
        raw_after[resource] = raw
        output_profiles[resource] = profile_for(candidate, raw)
        non_target_counts[resource] = len(before_records) - len(expected_changed)

    if pin_outputs:
        require(TARGET_PROFILES, "target output profiles are not pinned")
        require(dict(output_profiles) == dict(TARGET_PROFILES), "target packed/raw profiles differ")

    audit: Mapping[str, Any] = {
        "schema": AUDIT_SCHEMA,
        "source_policy": {
            "predecessor": "exact Wave 97 private candidate only",
            "korean_input": "Wave 97 candidate only",
            "direct_pc_jp_en_sc_tc_read": True,
            "switch_korean_read": False,
            "sentence_shortening": "forbidden",
            "manual_line_policy": {
                "Base/PK 13:213": "semantic three-line reflow under fixed person-dialogue 888px contract",
                "PK 13:563/573/590": "source/current manual LF and blank-line topology preserved; no line deletion or fixed-person layout transfer",
            },
            "steam_pre_release_ui_qa_required_for": ["MSG_PK/JP/msggame.bin:13:563", "MSG_PK/JP/msggame.bin:13:573", "MSG_PK/JP/msggame.bin:13:590"],
            "steam_game_resource_written": False,
            "steam_transaction_capability": "absent",
            "git_operation": "absent",
            "network_operation": "absent",
            "release_operation": "absent",
        },
        "layout_baseline": {
            "fixed_person_dialogue_only": {
                "raw_g1n_full_width_advance_px": RAW_G1N_FULL_WIDTH_ADVANCE,
                "raw_g1n_half_width_advance_px": RAW_G1N_HALF_WIDTH_ADVANCE,
                "max_raw_g1n_line_width_px": MAX_PERSON_DIALOGUE_RAW_LINE_PX,
                "max_lines": MAX_PERSON_DIALOGUE_LINES,
            },
            "tutorial_help_exception": "PK 13:563/573/590 are multi-sentence tutorial/help literals; manual topology is preserved and real-game UI QA is required before Steam deployment.",
        },
        "predecessor": predecessor,
        "direct_pc_source_packed_sha256": source_file_hashes,
        "font": font,
        "records": rows,
        "changed_record_count": len(CHANGES),
        "changed_literal_slot_count": sum(len(W27.literal_texts(records_before[change.resource][change.coordinate])) for change in CHANGES),
        "non_target_record_counts": non_target_counts,
        "non_target_record_byte_identity": "PASS",
        "target": output_profiles,
    }
    manifest: Mapping[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": relative(TMP_ROOT),
        "predecessor": predecessor,
        "resources": {
            resource: {
                "input": INPUT_PROFILES[resource],
                "output": output_profiles[resource],
                "changed_coordinates": [
                    f"{change.coordinate[0]}:{change.coordinate[1]}"
                    for change in CHANGES
                    if change.resource == resource
                ],
            }
            for resource in RESOURCE_ORDER
        },
        "changed_record_count": len(CHANGES),
        "changed_literal_slot_count": sum(len(W27.literal_texts(records_before[change.resource][change.coordinate])) for change in CHANGES),
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(packed_after, raw_after, audit, manifest)


def write_candidate(bundle: CandidateBundle) -> Path:
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT))
    try:
        for resource, packed in bundle.packed.items():
            path = stage / resource
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(packed)
        (stage / "audit.v1.json").write_bytes(canonical_json(bundle.audit))
        (stage / "build_manifest.v1.json").write_bytes(canonical_json(bundle.manifest))
        if output.exists():
            require_private(output, "existing candidate output")
            shutil.rmtree(output)
        os.replace(stage, output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    return output


def derive_pins() -> Mapping[str, Any]:
    bundle = prepare_candidate(pin_outputs=False)
    return {resource: profile_for(bundle.packed[resource], bundle.raw[resource]) for resource in RESOURCE_ORDER}


def verify_private() -> Mapping[str, Any]:
    bundle = prepare_candidate()
    output = require_private(TMP_ROOT / "candidate", "candidate output")
    for resource, packed in bundle.packed.items():
        path = output / resource
        require(path.is_file() and path.read_bytes() == packed, f"private candidate differs: {resource}")
    require((output / "audit.v1.json").read_bytes() == canonical_json(bundle.audit), "private audit differs")
    require((output / "build_manifest.v1.json").read_bytes() == canonical_json(bundle.manifest), "private manifest differs")
    return {
        "candidate_root": relative(output),
        "changed_record_count": len(CHANGES),
        "changed_literal_slot_count": len(CHANGES),
        "steam_game_resource_written": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify-private", "derive-pins"))
    args = parser.parse_args(argv)
    if args.command == "derive-pins":
        result: Mapping[str, Any] = derive_pins()
    elif args.command == "build":
        bundle = prepare_candidate()
        output = write_candidate(bundle)
        result = {
            "candidate_root": relative(output),
            "changed_record_count": len(CHANGES),
            "changed_literal_slot_count": len(CHANGES),
            "steam_game_resource_written": False,
        }
    else:
        result = verify_private()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
