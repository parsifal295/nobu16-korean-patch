#!/usr/bin/env python3
"""Read-only source-complete review for the 3xxx runtime-token event rows.

This workstream consumes batch07's private candidate as a strict Korean input
and does not build a message binary.  It restores the complete Korean source
for the parent-selected manual-compaction rows, applies only semantic Korean
line breaks, and tests every displayed line after substituting the strict
name-table value for each runtime token.  Steam, Git, releases, and network
operations are deliberately absent.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PUBLIC = WORKSTREAM / "public"
OUTPUT = PUBLIC / "pc_event_3xxx_runtime_review.v1.json"
MSGEV = "MSG_PK/JP/msgev.bin"

BATCH07_BUILDER = (
    REPO
    / "workstreams"
    / "pc_event_manual_compact_static007_batch07_v1"
    / "build_pc_event_manual_compact_static007_batch07_v1.py"
)
FULL_KOREAN_SOURCES = (
    REPO / "workstreams" / "dialogue" / "public" / "msgev_ko_historical_events_3689_3818.v0.6.json",
    REPO / "workstreams" / "dialogue" / "public" / "msgev_ko_historical_events_3819_3929.v0.7.json",
    REPO / "workstreams" / "steam_jp_common_messages_v1" / "public" / "msgev_ko_steam_jp_native.v1.json",
)
RESERVATION_MANIFEST = (
    REPO / "workstreams" / "steam_jp_msgev_full_layout_v2" / "public" / "runtime_token_reservations.v1.json"
)

SCHEMA = "nobu16.kr.pc-event-3xxx-runtime-review.v1"
MANUAL_RUNTIME_IDS = (
    3_692,
    3_694,
    3_703,
    3_713,
    3_715,
    3_734,
    3_736,
    3_765,
    3_766,
    3_767,
    3_783,
    3_789,
    3_795,
    3_798,
    3_806,
    3_810,
    3_815,
    3_818,
    3_859,
    3_860,
    3_861,
    3_862,
    3_865,
    3_875,
    3_876,
    3_877,
)
SOURCE_SEQUENCE_REORDER_IDS = (3_767,)
SOURCE_MEANING_CORRECTION_IDS = (3_713, 3_767, 3_789)
E = "\x1b"
RUNTIME_RE = re.compile(r"\[([a-z]+)(\d+)\]")
ESC_RE = re.compile(r"\x1b(?:CA|CB|CC|CZ)")
WORD_RE = re.compile(r"\[[a-z]+\d+\]|[가-힣A-Za-z0-9]+")


TARGETS: Mapping[int, str] = {
    3_692: (
        f"{E}CA요시모토{E}CZ에게 부추김을 받은 {E}CB양 우에스기 가문{E}CZ과 {E}CB고가쿠보{E}CZ는\n"
        f"여전히 {E}CC가와고에성{E}CZ을 포위하고 있었다.\n"
        f"성을 지킨 이는 {E}CA우지야스{E}CZ의 매제 {E}CA[bm790]{E}CZ 공이었다……"
    ),
    3_694: (
        f"{E}CC가와고에성{E}CZ을 지키는 {E}CA우지야스{E}CZ의 매제 {E}CA[bm790]{E}CZ 공은\n"
        "대군의 맹공을 필사적으로 버텼고,\n"
        "농성전은 이미 몇 달째 이어지고 있었다."
    ),
    3_703: (
        f"거기에 {E}CC가와고에성{E}CZ 안에서 뛰쳐나온\n"
        f"‘지키하치만’의 맹장 {E}CA[b790]{E}CZ 공의 군대까지 가세해,\n"
        "협공을 받은 포위군은 완전히 무너졌다."
    ),
    3_713: (
        f"{E}CB요시하루{E}CZ는 적장자 {E}CA기쿠도마루{E}CZ를 데리고,\n"
        f"{E}CC단바{E}CZ를 거쳐 {E}CC오미{E}CZ의 {E}CC구쓰키다니{E}CZ로 달아났다.\n"
        f"그곳에서 {E}CA기쿠도마루{E}CZ를 원복시켜\n"
        f"{E}CA[bm75]{E}CZ 공이라 이름하게 했다."
    ),
    3_715: (
        f"{E}CA요시하루{E}CZ는 자신처럼 11세에 원복한 아들에게\n"
        "쇼군 자리를 물려주었다.\n"
        f"{E}CA[bm75]{E}CZ 공은 무로마치 막부 제13대 쇼군에 올랐다."
    ),
    3_734: (
        f"{E}CA아시카가 요시하루{E}CZ가 쇼군 자리를 물려준 까닭은,\n"
        f"{E}CA[bm75]{E}CZ 공이 자신이 취임했던 나이에\n"
        "이르렀기 때문만은 아니었다……"
    ),
    3_736: (
        f"훗날 {E}CA[bm75]{E}CZ 공은\n"
        f"‘검성’ {E}CA쓰카하라 보쿠덴{E}CZ에게 배워,\n"
        "역대 쇼군을 뛰어넘는 검술을 지니게 되었다."
    ),
    3_765: (
        f"우유부단한 {E}CA하루카게{E}CZ는 이 사태에 전혀 대처하지 못해,\n"
        f"나이 차가 큰 아우 {E}CA[bm1448]{E}CZ 공에게만\n"
        "반란군 진압을 맡겼다."
    ),
    3_766: (
        f"{E}CA[bm1448]{E}CZ 공의 싸움은 막 첫 출진을 마친\n"
        "소년의 것이라고는 믿을 수 없었고,\n"
        "사람들은 피어난 군재에 혀를 내둘렀다."
    ),
    3_767: (
        f"예전부터 {E}CA하루카게{E}CZ의 통치에\n"
        f"불만을 품은 많은 {E}CB나가오{E}CZ 가신은\n"
        f"{E}CA[bm1448]{E}CZ 공이 당주에 오르기를\n"
        "바라게 되었지만―"
    ),
    3_783: (
        f"아닙니다. 모반이 아닙니다……\n"
        f"{E}CA하루카게{E}CZ 님께서 {E}CA[bm1448]{E}CZ 공을 양자로 맞으시고,\n"
        "조용히 은거해 주시기를 바랄 뿐입니다."
    ),
    3_789: (
        f"{E}CA[bm1448]{E}CZ 공의 스승이자 {E}CC린센지{E}CZ 주지로서\n"
        f"가문 내에 따르는 이도 많은 {E}CA덴시쓰 고이쿠{E}CZ가\n"
        f"중재에 나서 {E}CA하루카게{E}CZ에게 은거를\n"
        "간곡히 거듭 권했다. 그리고……"
    ),
    3_795: (
        f"{E}CA나가오 하루카게{E}CZ는 아우 {E}CA[bm1448]{E}CZ 공을 양자로 맞아,\n"
        f"은거하고 {E}CA[bm1448]{E}CZ 공에게 당주 자리를 넘겼다."
    ),
    3_798: (
        f"{E}CC에치고{E}CZ에는 {E}CA하루카게{E}CZ를 지지한 유력자도 있었다.\n"
        f"특히 {E}CB우에다 나가오 가문{E}CZ의 {E}CA마사카게{E}CZ와\n"
        f"{E}CA[bm1448]{E}CZ 공 사이에는 미묘한 앙금이 남았다……"
    ),
    3_806: (
        f"{E}CA[bm1730]{E}CZ 공은 아끼는 지도리 다치를 곁에 세우고,\n"
        "다시 큰 나무 아래에 몸을 누였다.\n"
        "연전의 피로가 그를 편안한 잠으로 이끌었다."
    ),
    3_810: (
        "본래 벼락을 맞으면 목숨을 건질 수 없다.\n"
        f"하지만 다행히 번개는 {E}CA[bm1730]{E}CZ 공이 아니라,\n"
        "조금 전까지 기대 있던 큰 나무에 떨어졌다."
    ),
    3_815: (
        "하얗게 빛나는군…… 그래.\n"
        "이제부터 ‘라이키리마루’라 이름 짓겠다!\n"
        f"앞으로도 이 {E}CA[bm1730]{E}CZ 공을 지켜 다오!"
    ),
    3_818: (
        "하지만 그 투지는 만년까지 쇠하지 않았고,\n"
        "사람들은 이 사건과 용맹한 모습 때문에\n"
        f"{E}CA[bm1730]{E}CZ 공을 ‘뇌신’이라 부르며 두려워했다……"
    ),
    3_859: (
        f"하지만 {E}CA하루카게{E}CZ를 대신해 당주가 된 {E}CA[bm1448]{E}CZ 공은,\n"
        f"{E}CB우에다 나가오 가문{E}CZ을 끌어들이지 않고서는\n"
        f"{E}CC에치고{E}CZ를 장악할 수 없었다."
    ),
    3_860: (
        f"한편 {E}CB우에다 나가오 가문{E}CZ의 {E}CA마사카게{E}CZ도,\n"
        f"{E}CA[bm1448]{E}CZ 공이 빠르게 {E}CC에치고{E}CZ의 기반을 굳히자,\n"
        "자신이 고립될 것을 염려했다."
    ),
    3_861: (
        f"서로의 필요는 인정했지만 교섭이 늦어지자,\n"
        f"초조해진 {E}CA[bm1448]{E}CZ 공은 마침내 {E}CA마사카게{E}CZ가 있는\n"
        f"{E}CC사카토성{E}CZ으로 군사를 보냈다……"
    ),
    3_862: (
        f"{E}CA[b1448]{E}CZ 공은 젊은데도 제법이군.\n"
        "말단 병사까지 군령이 닿고 진형에 흐트러짐이 없다.\n"
        "행군이 무엇인지 제대로 아는 자다."
    ),
    3_865: (
        f"과연 {E}CA[bm1448]{E}CZ 공은 성을 포위하기만 했을 뿐,\n"
        "공격할 기색은 보이지 않았다.\n"
        "그렇다고 병량을 끊으려 하지도 않았다."
    ),
    3_875: (
        "이는 바라 마지않던 일이오.\n"
        f"{E}CA우에다 나가오 마사카게{E}CZ는 이제부터 {E}CA[bm1448]{E}CZ 공의\n"
        "일문으로서 충성을 맹세하겠소."
    ),
    3_876: (
        "공적인 이야기를 나누는 동안,\n"
        f"{E}CA[bm1448]{E}CZ 공과 {E}CA마사카게{E}CZ는 서로의 사람됨을 살폈고,\n"
        "마침내 서로를 인정했다."
    ),
    3_877: (
        "다른 고쿠진이 보는 앞에서 일족이라도 가차 없이\n"
        "군사를 보내 굴복시키는 모습을 보임으로써,\n"
        f"가문을 다시 다잡은 {E}CA[bm1448]{E}CZ 공―"
    ),
}


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


batch07 = load_module("pc_event_3xxx_runtime_review_batch07", BATCH07_BUILDER)
base = batch07.base


class RuntimeReviewError(RuntimeError):
    """Raised when source, token, or Static Patch 007 evidence drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeReviewError(message)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def file_spec(path: Path) -> Mapping[str, Any]:
    payload = path.read_bytes()
    return {"path": path.relative_to(REPO).as_posix(), "size": len(payload), "sha256": sha256(payload)}


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def normalized_source_visible(value: str) -> str:
    value = ESC_RE.sub("", value)
    value = RUNTIME_RE.sub(lambda match: f"[id{match.group(2)}]", value)
    return "".join(character for character in value if not character.isspace())


def word_counter(value: str) -> Counter[str]:
    value = ESC_RE.sub("", value)
    value = RUNTIME_RE.sub(lambda match: f"[id{match.group(2)}]", value)
    return Counter(WORD_RE.findall(value))


def load_strict_input() -> tuple[Any, Mapping[str, Any], Mapping[str, Any]]:
    candidate_root = batch07.CANDIDATE_ROOT
    expected_files = {MSGEV, "audit.v1.json", "candidate_manifest.v1.json"}
    actual_files = {path.relative_to(candidate_root).as_posix() for path in candidate_root.rglob("*") if path.is_file()}
    require(actual_files == expected_files, f"batch07 candidate scope drift: {sorted(actual_files)}")
    event = (candidate_root / MSGEV).read_bytes()
    _header, raw, korean = base.parse_table("batch07 strict Korean runtime review input", event)
    profile = base.profile(event, raw)
    require(profile == batch07.EXPECTED_OUTPUT_PROFILE, "batch07 strict input profile drift")
    audit = json.loads((candidate_root / "audit.v1.json").read_text(encoding="utf-8"))
    require(audit.get("actual_changed_row_ids") == list(batch07.CHANGED_IDS), "batch07 audit changed-ID drift")
    return korean, profile, audit


def load_full_korean_sources() -> tuple[Mapping[int, str], list[Mapping[str, Any]]]:
    selected: dict[int, str] = {}
    profiles: list[Mapping[str, Any]] = []
    for path in FULL_KOREAN_SOURCES:
        require(path.is_file(), f"full Korean source missing: {path}")
        document = json.loads(path.read_text(encoding="utf-8"))
        entries = document.get("entries")
        require(isinstance(entries, list), f"entries missing: {path.name}")
        profiles.append(file_spec(path))
        for entry in entries:
            if not isinstance(entry, dict) or type(entry.get("id")) is not int or not isinstance(entry.get("ko"), str):
                continue
            entry_id = entry["id"]
            if entry_id in MANUAL_RUNTIME_IDS and entry_id not in selected:
                selected[entry_id] = entry["ko"]
    require(tuple(sorted(selected)) == MANUAL_RUNTIME_IDS, "complete Korean source coverage drift")
    return selected, profiles


def load_reservations() -> tuple[Mapping[str, Mapping[str, Any]], Mapping[str, Any]]:
    require(RESERVATION_MANIFEST.is_file(), f"runtime reservation manifest missing: {RESERVATION_MANIFEST}")
    document = json.loads(RESERVATION_MANIFEST.read_text(encoding="utf-8"))
    reservations = document.get("reservations")
    require(isinstance(reservations, dict), "runtime reservation rows missing")
    return reservations, {"file": file_spec(RESERVATION_MANIFEST), "policy": document.get("reservation_policy")}


def substitute_strict_runtime_names(text: str, korean: Any) -> tuple[str, list[Mapping[str, Any]]]:
    details: list[Mapping[str, Any]] = []

    def replacement(match: re.Match[str]) -> str:
        token = match.group(0)
        name_id = int(match.group(2))
        require(0 <= name_id < len(korean.texts), f"runtime name ID outside strict table: {token}")
        strict_name = korean.texts[name_id]
        require("\n" not in strict_name and "\x00" not in strict_name, f"runtime name is not one line: {token}")
        name_metrics = base.line_metrics(strict_name)
        require(len(name_metrics) == 1, f"runtime name metrics split unexpectedly: {token}")
        details.append(
            {
                "token": token,
                "prefix": match.group(1),
                "strict_name_id": name_id,
                "strict_korean_name": strict_name,
                "strict_korean_name_utf16le_sha256": text_hash(strict_name),
                "strict_korean_name_raw_g1n_width_px": name_metrics[0]["raw_g1n_width_px"],
                "strict_korean_name_effective_width_px": name_metrics[0]["effective_width_px"],
            }
        )
        return strict_name

    return RUNTIME_RE.sub(replacement, text), details


def validate_authored_targets() -> None:
    require(tuple(TARGETS) == MANUAL_RUNTIME_IDS, "target ID order/scope drift")
    require(len(MANUAL_RUNTIME_IDS) == 26, "manual runtime target count drift")
    require(set(MANUAL_RUNTIME_IDS).issubset(batch07.RUNTIME_HOLD_IDS), "manual target is not a batch07 runtime row")
    require(set(SOURCE_SEQUENCE_REORDER_IDS).issubset(MANUAL_RUNTIME_IDS), "source reorder scope drift")
    require(set(SOURCE_MEANING_CORRECTION_IDS).issubset(MANUAL_RUNTIME_IDS), "source meaning-correction scope drift")
    for entry_id, target in TARGETS.items():
        require("\x00" not in target, f"embedded terminator: {entry_id}")
        base.assert_no_break_inside_tag(target)
        signature = base.control_signature(target)
        require(signature["runtime_tokens"], f"runtime token absent from target: {entry_id}")
        require(signature["printf_tokens"] == [], f"printf token present: {entry_id}")
        require(signature["unknown_percent_count"] == 0, f"unknown percent token: {entry_id}")
        require(signature["other_controls"] == [], f"unexpected control: {entry_id}")


def target_row(
    entry_id: int,
    *,
    korean: Any,
    direct: Mapping[str, Any],
    full_korean: Mapping[int, str],
    reservations: Mapping[str, Mapping[str, Any]],
) -> Mapping[str, Any]:
    current = korean.texts[entry_id]
    target = TARGETS[entry_id]
    complete = full_korean[entry_id]
    current_signature = base.control_signature(current)
    target_signature = base.control_signature(target)
    require(current_signature == base.control_signature(direct["jp"].texts[entry_id]), f"KO/JP control drift: {entry_id}")
    require(target_signature == current_signature, f"target control drift: {entry_id}")
    if entry_id not in SOURCE_SEQUENCE_REORDER_IDS + SOURCE_MEANING_CORRECTION_IDS:
        require(
            normalized_source_visible(target) == normalized_source_visible(complete),
            f"complete Korean visible-sequence drift: {entry_id}",
        )
    elif entry_id == 3_713:
        require(
            target == (
                f"{E}CB요시하루{E}CZ는 적장자 {E}CA기쿠도마루{E}CZ를 데리고,\n"
                f"{E}CC단바{E}CZ를 거쳐 {E}CC오미{E}CZ의 {E}CC구쓰키다니{E}CZ로 달아났다.\n"
                f"그곳에서 {E}CA기쿠도마루{E}CZ를 원복시켜\n"
                f"{E}CA[bm75]{E}CZ 공이라 이름하게 했다."
            ),
            "3713 direct-JP semantic correction text drift",
        )
        require("원복시켜" in target and "공이라 이름하게 했다" in target, "3713 causative restoration drift")
    elif entry_id == 3_767:
        require(
            target
            == (
                f"예전부터 {E}CA하루카게{E}CZ의 통치에\n"
                f"불만을 품은 많은 {E}CB나가오{E}CZ 가신은\n"
                f"{E}CA[bm1448]{E}CZ 공이 당주에 오르기를\n"
                "바라게 되었지만―"
            ),
            "3767 subject-before-predicate reflow drift",
        )
    else:
        require(
            target
            == (
                f"{E}CA[bm1448]{E}CZ 공의 스승이자 {E}CC린센지{E}CZ 주지로서\n"
                f"가문 내에 따르는 이도 많은 {E}CA덴시쓰 고이쿠{E}CZ가\n"
                f"중재에 나서 {E}CA하루카게{E}CZ에게 은거를\n"
                "간곡히 거듭 권했다. 그리고……"
            ),
            "3789 direct-JP mediator/followers restoration drift",
        )
    rendered, token_details = substitute_strict_runtime_names(target, korean)
    lines = list(base.line_metrics(rendered))
    require(1 <= len(lines) <= 4, f"runtime rendered line count exceeds max: {entry_id}")
    require(all(line["passes_static_patch_007"] for line in lines), f"runtime rendered line exceeds Static Patch 007: {entry_id}")
    reservation_rows: list[Mapping[str, Any]] = []
    for detail in token_details:
        reservation = reservations.get(detail["token"])
        require(isinstance(reservation, Mapping), f"reservation missing: {entry_id}:{detail['token']}")
        reservation_rows.append(
            {
                **detail,
                "legacy_manifest_reserved_raw_g1n_width_px": reservation["reserved_full_name_width_px"],
                "legacy_manifest_source_name_id": reservation["source_name_id"],
                "legacy_manifest_source_name_utf16le_sha256": reservation["source_name_utf16le_sha256"],
                "conservative_reservation_policy": "Strict Korean same-ID full-name width; numeric suffix routing evidence only, no prefix-specific inference.",
            }
        )
        require(reservation["source_name_id"] == detail["strict_name_id"], f"reservation ID drift: {entry_id}:{detail['token']}")
    return {
        "entry_id": entry_id,
        "scene": batch07.SCENE_INDEX[entry_id],
        "change_mode": "SOURCE_COMPLETE_RUNTIME_TOKEN_RESTORATION_WITH_SEMANTIC_REFLOW",
        "strict_batch07_current_ko": current,
        "complete_korean_source": complete,
        "target_ko": target,
        "strict_batch07_current_ko_utf16le_sha256": text_hash(current),
        "complete_korean_source_utf16le_sha256": text_hash(complete),
        "target_ko_utf16le_sha256": text_hash(target),
        "direct_pc_jp": direct["jp"].texts[entry_id],
        "direct_pc_en": direct["en"].texts[entry_id],
        "direct_pc_sc": direct["sc"].texts[entry_id],
        "direct_pc_tc": direct["tc"].texts[entry_id],
        "direct_control_signatures": {language: base.control_signature(direct[language].texts[entry_id]) for language in ("jp", "en", "sc", "tc")},
        "target_control_signature": target_signature,
        "runtime_token_reservations": reservation_rows,
        "rendered_display_template": rendered,
        "displayed_lines": lines,
        "line_count": len(lines),
        "all_static_patch_007_lines_pass": True,
        "japanese_source_line_breaks_used": False,
        "korean_sentence_shortened_or_deleted": False,
        "route_status": "CONSERVATIVE_SAME_ID_STRICT_NAME_RESERVATION_READY_FOR_FOLLOWUP_CANDIDATE",
        "route_limit": "No live runtime trace or prefix-specific width claim is made; the complete strict Korean same-ID name is reserved for every token occurrence.",
        "source_sequence_reordered_for_protected_tag_order": entry_id in SOURCE_SEQUENCE_REORDER_IDS,
        "source_meaning_corrected_from_direct_pc_jp": entry_id in SOURCE_MEANING_CORRECTION_IDS,
        "source_meaning_correction_note": {
            3_713: "Direct PC JP is a causative construction: Yoshiharu has Kikudomaru undergo genpuku and take the name [bm75].",
            3_767: "Reflow puts the long-dissatisfied Nagao retainers before their predicate so the Korean subject remains bound to the desire clause.",
            3_789: "Direct PC JP restores followers within the clan and Tenshitsu Koiku entering as mediator before repeatedly urging retirement.",
        }.get(entry_id),
    }


def current_runtime_scan(korean: Any) -> list[Mapping[str, Any]]:
    rows: list[Mapping[str, Any]] = []
    for entry_id in batch07.RUNTIME_HOLD_IDS:
        rendered, details = substitute_strict_runtime_names(korean.texts[entry_id], korean)
        metrics = list(base.line_metrics(rendered))
        rows.append(
            {
                "entry_id": entry_id,
                "parent_selected_manual_source_complete_target": entry_id in MANUAL_RUNTIME_IDS,
                "runtime_tokens": [detail["token"] for detail in details],
                "current_rendered_lines": metrics,
                "current_rendered_line_count": len(metrics),
                "current_rendered_static_patch_007_passes": all(line["passes_static_patch_007"] for line in metrics),
            }
        )
    return rows


def build_report() -> Mapping[str, Any]:
    validate_authored_targets()
    korean, strict_profile, strict_audit = load_strict_input()
    direct, direct_profiles = base.load_direct_contexts()
    require(all(len(table.texts) == len(korean.texts) for table in direct.values()), "direct context topology drift")
    full_korean, source_profiles = load_full_korean_sources()
    reservations, reservation_provenance = load_reservations()
    rows = [
        target_row(entry_id, korean=korean, direct=direct, full_korean=full_korean, reservations=reservations)
        for entry_id in MANUAL_RUNTIME_IDS
    ]
    runtime_scan = current_runtime_scan(korean)
    require(all(row["all_static_patch_007_lines_pass"] for row in rows), "target line pass aggregation drift")
    require(all(row["current_rendered_static_patch_007_passes"] for row in runtime_scan), "current runtime scan overflow")
    return {
        "schema": SCHEMA,
        "candidate_created": False,
        "strict_input": {
            "candidate_relative": (batch07.CANDIDATE_ROOT / MSGEV).relative_to(REPO).as_posix(),
            "profile": strict_profile,
            "batch07_changed_row_ids": strict_audit["actual_changed_row_ids"],
            "only_korean_build_input": True,
        },
        "source_policy": {
            "complete_korean_sources": source_profiles,
            "direct_pc_context_read_only": True,
            "direct_pc_context_languages": ["jp", "en", "sc", "tc"],
            "japanese_source_line_breaks_used": False,
            "korean_sentence_shortened_or_deleted": False,
            "runtime_prefix_specific_inference": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "network_operation_performed": False,
            "release_published": False,
        },
        "layout_policy": {
            "authority": "F:/Games/NOBU16/AGENTS.md Static Patch 007 baseline",
            "raw_full_width_px": 48,
            "raw_half_width_px": 24,
            "raw_hard_limit_px": 1_440,
            "effective_width_hard_limit_px": 912,
            "max_lines": 4,
            "draw_font_px": 30,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "runtime_name_reservation": "Substitute the strict Korean table value at the token numeric suffix, then measure the displayed line.",
        },
        "runtime_reservation_provenance": reservation_provenance,
        "coverage": {
            "batch07_runtime_row_count": len(batch07.RUNTIME_HOLD_IDS),
            "manual_source_complete_runtime_target_ids": list(MANUAL_RUNTIME_IDS),
            "manual_source_complete_runtime_target_count": len(MANUAL_RUNTIME_IDS),
            "other_runtime_row_ids": [entry_id for entry_id in batch07.RUNTIME_HOLD_IDS if entry_id not in MANUAL_RUNTIME_IDS],
            "other_runtime_row_count": len(batch07.RUNTIME_HOLD_IDS) - len(MANUAL_RUNTIME_IDS),
            "source_sequence_reordered_for_tag_order_ids": list(SOURCE_SEQUENCE_REORDER_IDS),
            "source_meaning_correction_ids": list(SOURCE_MEANING_CORRECTION_IDS),
        },
        "rows": rows,
        "current_runtime_name_substitution_scan": runtime_scan,
        "summary": {
            "all_26_targets_ready_for_followup_candidate": True,
            "all_48_current_runtime_rows_fit_with_strict_name_substitution": True,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "network_operation_performed": False,
            "release_published": False,
        },
    }


def write_report(report: Mapping[str, Any]) -> Path:
    PUBLIC.mkdir(parents=True, exist_ok=True)
    payload = canonical_json(report)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{OUTPUT.name}.", suffix=".tmp", dir=PUBLIC)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, OUTPUT)
    finally:
        temporary_path.unlink(missing_ok=True)
    return OUTPUT


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "report", "write-report"))
    command = parser.parse_args().command
    report = build_report()
    if command == "check":
        print(
            json.dumps(
                {
                    "manual_source_complete_runtime_target_ids": list(MANUAL_RUNTIME_IDS),
                    "target_count": len(MANUAL_RUNTIME_IDS),
                    "all_26_targets_ready_for_followup_candidate": report["summary"]["all_26_targets_ready_for_followup_candidate"],
                    "all_48_current_runtime_rows_fit_with_strict_name_substitution": report["summary"]["all_48_current_runtime_rows_fit_with_strict_name_substitution"],
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0
    if command == "report":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0
    print(write_report(report).relative_to(REPO).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
