#!/usr/bin/env python3
"""Audit the three remaining static-width outliers in PK ``msgev``.

This is an evidence-only workstream.  It reads the latest Wave101 private candidate
and the pinned direct PC language witnesses, then writes one public JSON
ledger below this workstream.  It never creates a message-table candidate and
never writes the Steam installation, Git state, a release payload, or network
state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PUBLIC_DIR = WORKSTREAM / "public"
OUTPUT = PUBLIC_DIR / "pc_event_static_outlier_audit.v1.json"
RESOURCE = Path("MSG_PK") / "JP" / "msgev.bin"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-static-outlier-audit.v1"
ROW_COUNT = 17_916
TARGET_IDS = (17_862, 17_863, 17_864)
BASE_DUPLICATE_IDS = {17_862: 17_814, 17_863: 17_815, 17_864: 17_816}

# Static Patch 007 is the event-dialogue measurement baseline.  It is recorded
# for the outliers but is deliberately not asserted as the renderer contract
# for these three strings: their actual widget route is the subject of this
# audit.
RAW_FULL_WIDTH_PX = 48
RAW_HALF_WIDTH_PX = 24
DRAW_FONT_PX = 30
RAW_LIMIT_PX = 1_440
EFFECTIVE_LIMIT_PX = 912
MAX_DIALOGUE_LINES = 4

# Wave101 is the strict current input.  Wave100 is retained only as an exact
# predecessor for the scoped non-overlap guard: the W101 Kanto wave changes
# 15 rows inside 3489..3526 and must not modify the three held tail rows.
W100_ROOT = REPO / "tmp" / "pc_event_ending_regions_quality_wave100_v1" / "candidate-final"
W100_EVENT = W100_ROOT / RESOURCE
W100_PROFILE: Mapping[str, Any] = {
    "sha256": "245043679E4A7A75628519829C1B16372A8FD085A1CC7F0F4EE97F52BB66BA60",
    "size": 1_048_043,
    "raw_sha256": "F7DB831E850F191CC6320E54BF878DCC8B7F3DC4F5D51AD66379D64617F553ED",
    "raw_size": 1_043_924,
}
W101_ROOT = REPO / "tmp" / "pc_event_kanto_quality_wave101_v1" / "candidate-final"
W101_EVENT = W101_ROOT / RESOURCE
W101_AUDIT = W101_ROOT / "audit.v1.json"
W101_MANIFEST = W101_ROOT / "candidate_manifest.v1.json"
W101_PROFILE: Mapping[str, Any] = {
    "sha256": "96DBB584AE96157E3B7013CAF86A4876CDB0B87EFF66433CB9236206996C2D91",
    "size": 1_048_079,
    "raw_sha256": "507F8FB7CF75D327F8CC88725E17BE3DA1084C4BD96237B9F1A1E8CE5F9D3B41",
    "raw_size": 1_043_960,
}
W101_AUDIT_SHA256 = "AFEFF861A1DD28C688657A00CB08DFA0C615C933983A3D2723D7428796ABACBC"
W101_MANIFEST_SHA256 = "85C1894EE95C844A6F14B542A127D73768717325139B73D28D791B840536CDAD"
W101_CHANGED_IDS = (3489, 3490, 3491, 3493, 3497, 3500, 3502, 3505, 3506, 3508, 3510, 3514, 3516, 3522, 3526)
W101_CHANGE_WINDOW = (3489, 3526)

STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DIRECT_SOURCES: Mapping[str, tuple[Path, Mapping[str, Any]]] = {
    "jp": (
        STEAM
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / RESOURCE,
        {
            "sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
            "size": 562_226,
            "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
            "raw_size": 894_800,
        },
    ),
    "en": (
        STEAM / "MSG_PK" / "EN" / "msgev.bin",
        {
            "sha256": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
            "size": 762_196,
            "raw_sha256": "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911",
            "raw_size": 1_878_836,
        },
    ),
    "sc": (
        STEAM / "MSG_PK" / "SC" / "msgev.bin",
        {
            "sha256": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
            "size": 522_177,
            "raw_sha256": "3ACE267E6B9774D8C940C9D7940F168B61744ADDF7C082F2CB1EA7E9BBD82B5E",
            "raw_size": 754_708,
        },
    ),
    "tc": (
        STEAM / "MSG_PK" / "TC" / "msgev.bin",
        {
            "sha256": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
            "size": 524_909,
            "raw_sha256": "42DC893AA9FF9D3E7B75FBCFFBEFD7C3DFC338CAB71E942C081BDC52C9024BF6",
            "raw_size": 744_212,
        },
    ),
}

# The base string table carries an identical JP trio at a different coordinate.
# It is evidence of a shared event-condition/result string pool, not authority
# to carry the PK Static Patch 007 width rule into Base.
BASE_JP = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.8.0"
    / "originals"
    / "MSG"
    / "JP"
    / "ev_strdata.bin"
)
BASE_JP_PROFILE: Mapping[str, Any] = {
    "sha256": "EADCD167EF9684C7F077694A1A7F68966E34FD2E2EEF9DEFB7817031C3D773EB",
    "size": 496_819,
    "raw_sha256": "5FBD960A4870FA4850BD725C58E67BE3A7F191960737C36E4505151FE4B7C528",
    "raw_size": 789_260,
}
BASE_ROW_COUNT = 17_868

EXPECTED_KO: Mapping[int, str] = {
    17_862: "오다 가문에서 일부 무장이 이탈하여 아케치 가문, 시바타 가문, 하시바 가문이 탄생",
    17_863: "이마가와 가문에서 일부 무장이 이탈하여 마쓰다이라 가문이 탄생",
    17_864: "나가오가에서 일부 무장이 이탈하여, 야마노우치 우에스기가가 탄생",
}
EXPECTED_SOURCE_HASHES: Mapping[int, Mapping[str, str]] = {
    17_862: {
        "jp": "55BAC27BFC6189BBA8C1989C538E59157B3C3E2885BCDB5CAA271B3036BB5889",
        "en": "2DA83D14386A2E8E2089D3CA6FC63E63E8BF93865C089A3547E57B7C5FC74E43",
        "sc": "F76D2AB45AB6C3A7E7913B98068C183815B26F53682D245DD60BCF5D47E97CAA",
        "tc": "441425D326F217F99D3D5F0A262A52E6CFB678C2CAB4BE7ECB61DB88BC65753E",
    },
    17_863: {
        "jp": "2C26881899F0F674D820589A75F1724B7D6A515843EB61EA0921DF4D8D816CF8",
        "en": "4E8A7093D3B378AD6E7612FC70C1F8CCC6232963DF6F3B7B9CFF5D4F33D505D0",
        "sc": "8EAE646B735E49FECFB13A665470FA70119C408E5258E592BA4F1487DC3BFD55",
        "tc": "D7592D0797401F6413E6700354E478C1C8C4419B19189CFE92C1CBC74859753E",
    },
    17_864: {
        "jp": "1E82AD78F18EDDB4B8891BCEFAF7212230D3D324462FE6C0F74AEBAFA84A19FC",
        "en": "794FB2B8278A1292E360D8F4CE95CD1044B3CFFFFD4648D77E7651777E589FEF",
        "sc": "F78B3D7A49E527BD06E50062BFA3DF6BE25992E0B14052827A41D6223E7212A8",
        "tc": "9F87E18ACEB7BC855D41C5BC2D4FEF7DBD5EC2B93AB7D6EEA152C8C48188BECA",
    },
}

# The local sequence is deliberately encoded as exact Korean values.  These
# are selector/condition/result labels surrounding the three outliers, not a
# prose dialogue scene.  They are enough to classify the table section while
# avoiding a claim about an unobserved renderer.
UI_NEIGHBORS: Mapping[int, str] = {
    17_817: "아니다",
    17_818: "이전",
    17_820: "이후",
    17_821: "%d일 이내",
    17_828: "%s와 혼인 동맹 중",
    17_835: "탄생 전",
    17_836: "겐푸쿠 전",
    17_842: "사망",
    17_847: "병량",
    17_848: "금전",
    17_849: "철포",
    17_850: "군마",
    17_851: "증가",
    17_852: "감소",
    17_853: "%d일",
    17_854: "무기한",
    17_855: "%d개월",
    17_856: "적대시",
    17_857: "험악",
    17_858: "불화",
    17_859: "평상",
    17_860: "우호",
    17_861: "친밀",
    17_865: "가게토라의 자질",
    17_866: "간스케의 비책",
    17_867: "오니미노, 신겐을 타이르다",
    17_872: "1개 이상",
    17_873: "과반수 이상",
    17_874: "전체",
    17_875: "(종속 세력 포함)",
    17_876: "취임",
    17_877: "해임",
    17_879: "※추가로 다음 조건을 만족하는 경우, 결과에 변동이 생깁니다※",
    17_880: "자기 세력",
    17_881: "(기존의 외교 관계를 우선)",
    17_882: "아군",
    17_883: "적군",
    17_884: "각 세력의 정세가 크게 변동",
    17_885: "※가상 전개로 진행하면 결과가 달라집니다※",
}

ESC = "\x1b"
ESC_RE = re.compile(r"\x1bC.")
LINEBREAK_RE = re.compile(r"\r\n?|\n")


class AuditError(RuntimeError):
    """Raised when a pinned source, measurement, or output drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO.resolve()).as_posix()
    except ValueError:
        return str(path)


def steam_relative(path: Path) -> str:
    """Return a distribution-safe path relative to the PC installation."""

    try:
        return path.resolve().relative_to(STEAM.resolve()).as_posix()
    except ValueError:
        return path.name


def profile(packed: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "sha256": sha256(packed),
        "size": len(packed),
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
    }


def candidate_files(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def load_table(path: Path, expected: Mapping[str, Any], row_count: int, label: str) -> tuple[tuple[str, ...], Mapping[str, Any]]:
    require(path.is_file(), f"{label}: missing: {path}")
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    require(len(table.texts) == row_count, f"{label}: row count drift: {len(table.texts)}")
    require(rebuild_message_table(table, table.texts) == raw, f"{label}: message table round-trip drift")
    measured = profile(packed, raw)
    require(measured == expected, f"{label}: packed/raw profile drift: {measured}")
    return tuple(table.texts), measured


def is_full_width_visible(character: str) -> bool:
    codepoint = ord(character)
    return (
        0x1100 <= codepoint <= 0x11FF
        or 0x3130 <= codepoint <= 0x318F
        or 0x3400 <= codepoint <= 0x4DBF
        or 0x4E00 <= codepoint <= 0x9FFF
        or 0xAC00 <= codepoint <= 0xD7AF
        or 0xF900 <= codepoint <= 0xFAFF
    )


def rendered_display_line(value: str) -> str:
    display: list[str] = []
    cursor = 0
    while cursor < len(value):
        if value[cursor] == ESC:
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token: {token!r}")
            cursor += 3
            continue
        character = value[cursor]
        require(unicodedata.category(character) != "Cc", f"unexpected visible control U+{ord(character):04X}")
        display.append(character)
        cursor += 1
    return "".join(display)


def control_signature(value: str) -> Mapping[str, Any]:
    esc_tokens: list[str] = []
    controls: list[str] = []
    cursor = 0
    while cursor < len(value):
        if value[cursor] == ESC:
            token = value[cursor : cursor + 3]
            require(ESC_RE.fullmatch(token) is not None, f"malformed ESC token: {token!r}")
            esc_tokens.append(token)
            cursor += 3
            continue
        character = value[cursor]
        if character not in "\r\n" and unicodedata.category(character) == "Cc":
            controls.append(f"U+{ord(character):04X}")
        cursor += 1
    return {"esc_tokens": esc_tokens, "other_controls": controls}


def layout_metrics(value: str) -> Mapping[str, Any]:
    lines: list[Mapping[str, Any]] = []
    for line_number, source_line in enumerate(LINEBREAK_RE.sub("\n", value).split("\n"), 1):
        display = rendered_display_line(source_line)
        full = sum(is_full_width_visible(character) for character in display)
        half = len(display) - full
        raw = full * RAW_FULL_WIDTH_PX + half * RAW_HALF_WIDTH_PX
        effective = (raw * DRAW_FONT_PX + RAW_FULL_WIDTH_PX - 1) // RAW_FULL_WIDTH_PX
        lines.append(
            {
                "line_number": line_number,
                "display_string": display,
                "raw_g1n_width_px": raw,
                "effective_width_px": effective,
                "full_width_character_count": full,
                "half_width_character_count": half,
                "over_raw_1440px": raw > RAW_LIMIT_PX,
                "over_effective_912px": effective > EFFECTIVE_LIMIT_PX,
                "passes_static_patch_007": raw <= RAW_LIMIT_PX and effective <= EFFECTIVE_LIMIT_PX,
            }
        )
    return {
        "line_count": len(lines),
        "lines": lines,
        "max_raw_g1n_width_px": max(line["raw_g1n_width_px"] for line in lines),
        "max_effective_width_px": max(line["effective_width_px"] for line in lines),
        "over_912px": any(line["over_effective_912px"] for line in lines),
    }


def flow_direct_reference_probe() -> Mapping[str, Any]:
    """Probe only direct 32-bit ID literals in historical FLOW scripts.

    A negative result is intentionally non-conclusive: a script may use an
    indirect table or a different identifier.  It is included only to avoid
    pretending that static source data proved a dialogue trigger.
    """

    roots = (STEAM / "FLOW", STEAM / "FLOW_PK")
    files = tuple(sorted(path for root in roots for path in root.rglob("*.bsf")))
    require(files, "historical FLOW probe has no .bsf files")
    matches: dict[str, list[str]] = {str(entry_id): [] for entry_id in TARGET_IDS}
    for path in files:
        blob = path.read_bytes()
        for entry_id in TARGET_IDS:
            needle = entry_id.to_bytes(4, "little", signed=False)
            offset = 0
            while True:
                offset = blob.find(needle, offset)
                if offset < 0:
                    break
                matches[str(entry_id)].append(f"{steam_relative(path)}:0x{offset:X}")
                offset += 1
    return {
        "method": "Search FLOW and FLOW_PK .bsf files for each table index encoded as direct 32-bit little-endian value.",
        "files": [steam_relative(path) for path in files],
        "matches": matches,
        "conclusion": "No direct match proves neither absence nor a renderer route; indirect table references remain possible.",
    }


def assert_public_output(path: Path) -> None:
    resolved = path.resolve(strict=False)
    root = PUBLIC_DIR.resolve(strict=False)
    require(resolved.is_relative_to(root), f"output escapes public workstream: {resolved}")


def build_document() -> Mapping[str, Any]:
    w100_texts, w100_profile = load_table(W100_EVENT, W100_PROFILE, ROW_COUNT, "Wave100 predecessor")
    w101_root = W101_ROOT.resolve(strict=True)
    require(w101_root.is_relative_to((REPO / "tmp").resolve()), "Wave101 strict input escapes private tmp")
    require(
        candidate_files(w101_root) == {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"},
        "Wave101 strict input file scope drift",
    )
    candidate, candidate_profile = load_table(W101_EVENT, W101_PROFILE, ROW_COUNT, "Wave101 strict candidate")
    require(W101_AUDIT.is_file() and W101_MANIFEST.is_file(), "Wave101 audit/manifest missing")
    require(sha256(W101_AUDIT.read_bytes()) == W101_AUDIT_SHA256, "Wave101 audit hash drift")
    require(sha256(W101_MANIFEST.read_bytes()) == W101_MANIFEST_SHA256, "Wave101 manifest hash drift")
    candidate_audit = json.loads(W101_AUDIT.read_text(encoding="utf-8"))
    candidate_manifest = json.loads(W101_MANIFEST.read_text(encoding="utf-8"))
    require(candidate_audit.get("candidate_only") is True, "Wave101 audit is not candidate-only")
    require(candidate_manifest.get("candidate_only") is True, "Wave101 manifest is not candidate-only")
    require(candidate_audit.get("output_event_profile") == candidate_profile, "Wave101 audit profile drift")
    require(candidate_manifest.get("output") == candidate_profile, "Wave101 manifest profile drift")
    require(candidate_manifest.get("applied_row_ids") == list(W101_CHANGED_IDS), "Wave101 applied row scope drift")

    changed_ids = tuple(
        entry_id
        for entry_id, (w100_value, w101_value) in enumerate(zip(w100_texts, candidate))
        if w100_value != w101_value
    )
    require(changed_ids == W101_CHANGED_IDS, f"Wave101 predecessor diff drift: {changed_ids}")
    require(all(W101_CHANGE_WINDOW[0] <= entry_id <= W101_CHANGE_WINDOW[1] for entry_id in changed_ids), "Wave101 changes escape Kanto window")
    require(all(w100_texts[entry_id] == candidate[entry_id] for entry_id in TARGET_IDS), "held outlier rows changed during Wave101 rebase")

    sources: dict[str, tuple[str, ...]] = {}
    source_profiles: dict[str, Mapping[str, Any]] = {}
    for language, (path, expected) in DIRECT_SOURCES.items():
        texts, source_profiles[language] = load_table(path, expected, ROW_COUNT, f"direct PC {language.upper()}")
        sources[language] = texts

    base_texts, base_profile = load_table(BASE_JP, BASE_JP_PROFILE, BASE_ROW_COUNT, "direct PC Base JP")

    entries: list[Mapping[str, Any]] = []
    for entry_id in TARGET_IDS:
        value = candidate[entry_id]
        require(value == EXPECTED_KO[entry_id], f"candidate Korean drift: {entry_id}")
        signature = control_signature(value)
        require(signature == {"esc_tokens": [], "other_controls": []}, f"candidate control drift: {entry_id}")
        require("\r" not in value and "\n" not in value, f"candidate line break drift: {entry_id}")
        measured = layout_metrics(value)
        require(measured["line_count"] == 1, f"unexpected candidate line count: {entry_id}")
        require(measured["over_912px"] is True, f"expected static width outlier: {entry_id}")

        witness_hashes: dict[str, str] = {}
        witness_break_counts: dict[str, int] = {}
        for language, texts in sources.items():
            source_value = texts[entry_id]
            source_hash = text_hash(source_value)
            require(source_hash == EXPECTED_SOURCE_HASHES[entry_id][language], f"{language} witness drift: {entry_id}")
            witness_hashes[language] = source_hash
            witness_break_counts[language] = source_value.count("\n") + source_value.count("\r")
            require(witness_break_counts[language] == 0, f"{language} witness unexpected LF: {entry_id}")

        base_id = BASE_DUPLICATE_IDS[entry_id]
        base_value = base_texts[base_id]
        require(text_hash(base_value) == witness_hashes["jp"], f"Base JP duplicate drift: {entry_id}->{base_id}")

        entries.append(
            {
                "entry_id": entry_id,
                "candidate_text_utf16le_sha256": text_hash(value),
                "classification": "ui_or_notification_path_evidence_hold",
                "decision": "retain_one_line_no_candidate_mutation",
                "static_patch_007_measurement": measured,
                "control_signature": signature,
                "direct_pc_witnesses": {
                    "text_utf16le_sha256": witness_hashes,
                    "line_break_character_count": witness_break_counts,
                    "semantic_witness": "All four direct PC languages describe officers leaving a clan and the resulting clan formation; the Korean preserves that event-result meaning.",
                },
                "base_duplicate_evidence": {
                    "resource": "MSG/JP/ev_strdata.bin",
                    "entry_id": base_id,
                    "jp_text_utf16le_sha256": text_hash(base_value),
                    "same_as_pk_direct_jp": True,
                    "interpretation": "The identical JP text occurs in Base at a shifted index, consistent with a shared event-condition/result string pool. This does not establish that Base and PK use the same renderer.",
                },
                "widget_judgement": {
                    "is_static_patch_007_dialogue_box_proven": False,
                    "is_separate_widget_proven": False,
                    "likely_section": "historical-event condition/result selection or notification UI",
                    "reason": "The immediate surrounding rows are condition selectors, relationship/resource states, historical-event titles, result-count choices, appointment buttons, and outcome-change notices rather than a contiguous prose dialogue scene.",
                    "action": "Do not insert a manual LF until an observed UI route or code-path trace identifies this string's renderer and available width.",
                },
                "no_shortening_or_source_lf_import": True,
            }
        )

    expected_outliers = {
        17_862: (1_896, 1_185, 33, 13),
        17_863: (1_464, 915, 27, 7),
        17_864: (1_512, 945, 28, 7),
    }
    for entry in entries:
        line = entry["static_patch_007_measurement"]["lines"][0]
        actual = (
            line["raw_g1n_width_px"],
            line["effective_width_px"],
            line["full_width_character_count"],
            line["half_width_character_count"],
        )
        require(actual == expected_outliers[entry["entry_id"]], f"measurement drift: {entry['entry_id']}")

    for entry_id, expected_value in UI_NEIGHBORS.items():
        require(candidate[entry_id] == expected_value, f"UI-neighbor sequence drift: {entry_id}")

    return {
        "schema": SCHEMA,
        "candidate_only": True,
        "mutation_scope": "read_only_audit_public_json_only",
        "resource": RESOURCE.as_posix(),
        "scope": {
            "target_ids": list(TARGET_IDS),
            "target_count": len(TARGET_IDS),
            "reason": "These are the only three static one-line values over raw 1440/effective 912 in the all-row scan rebased to Wave101.",
        },
        "static_patch_007_baseline": {
            "font_px": DRAW_FONT_PX,
            "line_spacing_setting": 8,
            "effective_line_width_px": EFFECTIVE_LIMIT_PX,
            "max_dialogue_lines": MAX_DIALOGUE_LINES,
            "raw_full_width_px": RAW_FULL_WIDTH_PX,
            "raw_half_width_px": RAW_HALF_WIDTH_PX,
            "raw_equivalent_limit_px": RAW_LIMIT_PX,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "application_statement": "Recorded as an audit measurement. It is not treated as a proven renderer contract for the three held UI-path rows.",
        },
        "input": {
            "workstream": "pc_event_kanto_quality_wave101_v1",
            "candidate_relative_path": relative(W101_ROOT),
            "event_profile": candidate_profile,
            "audit_sha256": W101_AUDIT_SHA256,
            "candidate_manifest_sha256": W101_MANIFEST_SHA256,
        },
        "rebase_from_wave100": {
            "workstream": "pc_event_ending_regions_quality_wave100_v1",
            "candidate_relative_path": relative(W100_ROOT),
            "event_profile": w100_profile,
            "wave101_changed_ids": list(changed_ids),
            "wave101_change_window": list(W101_CHANGE_WINDOW),
            "target_rows_identical_to_wave100": True,
        },
        "direct_pc_source_profiles": source_profiles,
        "base_jp_duplicate_source_profile": base_profile,
        "ui_neighbor_evidence": [
            {"entry_id": entry_id, "display_string": candidate[entry_id]}
            for entry_id in UI_NEIGHBORS
        ],
        "direct_flow_le32_probe": flow_direct_reference_probe(),
        "entries": entries,
        "conclusion": {
            "approved_manual_line_break_count": 0,
            "remaining_static_width_outlier_count": len(entries),
            "status": "renderer_path_hold",
            "summary": "All three strings exceed the 912px Static Patch 007 measurement only as one-line text, but static evidence places them in a historical-event condition/result UI block and does not prove the patched event-dialogue box. Preserve text and one-line topology until runtime/UI-path evidence is collected.",
        },
    }


def build() -> None:
    document = build_document()
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    assert_public_output(OUTPUT)
    OUTPUT.write_bytes(canonical_json(document))
    print(f"wrote {relative(OUTPUT)}")


def verify() -> None:
    require(OUTPUT.is_file(), f"audit output missing: {OUTPUT}")
    expected = canonical_json(build_document())
    actual = OUTPUT.read_bytes()
    require(actual == expected, "audit output drift; run build")
    print("verification passed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "verify"))
    args = parser.parse_args()
    if args.command == "build":
        build()
    else:
        verify()


if __name__ == "__main__":
    try:
        main()
    except AuditError as exc:
        raise SystemExit(f"error: {exc}") from exc
