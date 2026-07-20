#!/usr/bin/env python3
"""Build the private Wave 98 Gifu-naming event quality candidate.

The only Korean binary input is the latest all-range Static Patch 007
manual-compact restoration candidate.  Pristine PC Japanese and installed PC
EN/SC/TC event resources are read-only source evidence.  This builder writes
only a private candidate below ``tmp``; it has no Steam, Git, release, or
network operation.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
CANDIDATE_ROOT = TMP_ROOT / "candidate-final"
RESOURCE = Path("MSG_PK") / "JP" / "msgev.bin"
TOOLS = REPO / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.pc-event-gifu-quality-wave98.v1"
ROW_COUNT = 17_916
STRICT_WORKSTREAM = "pc_event_manual_compact_static007_3xxx_runtime_restore_v1"
STRICT_ROOT = REPO / "tmp" / STRICT_WORKSTREAM / "candidate-final"
STRICT_EVENT = STRICT_ROOT / RESOURCE
STRICT_AUDIT = STRICT_ROOT / "audit.v1.json"
STRICT_MANIFEST = STRICT_ROOT / "candidate_manifest.v1.json"
EXPECTED_STRICT_PROFILE: Mapping[str, Any] = {
    "raw_sha256": "920373F9AFA47959C291025A3D3230B4064261997090AFC01A1EE57F61153FFB",
    "raw_size": 1_043_920,
    "sha256": "CFF60029741A596F40EA19DF9F05A8FEC53E240EF09C750B732D052195A04D35",
    "size": 1_048_039,
}

STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
SOURCES: Mapping[str, tuple[Path, Mapping[str, Any]]] = {
    "jp": (
        STEAM_ROOT
        / "KR_PATCH_BACKUP"
        / "file_only_transaction"
        / "steam-jp-1.1.7-v0.6.0"
        / "originals"
        / "MSG_PK"
        / "JP"
        / "msgev.bin",
        {
            "raw_sha256": "07D7512BE0235753FC7BB0C7C548B61F471D9CDED01379E63B8AF8EAE013813E",
            "raw_size": 894_800,
            "sha256": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
            "size": 562_226,
        },
    ),
    "en": (
        STEAM_ROOT / "MSG_PK" / "EN" / "msgev.bin",
        {
            "raw_sha256": "6A1F3891412EBFF5AC3188F498C9951431154192D69E82B7ABB6F25AA934D911",
            "raw_size": 1_878_836,
            "sha256": "BDC7705CDFBEF483363679AAD5F4377E1D7CBA161D6D130639DD42312725FF4E",
            "size": 762_196,
        },
    ),
    "sc": (
        STEAM_ROOT / "MSG_PK" / "SC" / "msgev.bin",
        {
            "raw_sha256": "3ACE267E6B9774D8C940C9D7940F168B61744ADDF7C082F2CB1EA7E9BBD82B5E",
            "raw_size": 754_708,
            "sha256": "7C443515D8B42DD5D1A516FE606DB8880F21296F7BEF0C5D067FEA7D9FC991BA",
            "size": 522_177,
        },
    ),
    "tc": (
        STEAM_ROOT / "MSG_PK" / "TC" / "msgev.bin",
        {
            "raw_sha256": "42DC893AA9FF9D3E7B75FBCFFBEFD7C3DFC338CAB71E942C081BDC52C9024BF6",
            "raw_size": 744_212,
            "sha256": "89D183BA95C3BB83B52A5EE408664D5247C695A1DB192105A5D906737E6F78B6",
            "size": 524_909,
        },
    ),
}

METRICS_HELPER_PATH = (
    REPO
    / "workstreams"
    / "pc_event_manual_compact_static007_batch01_v1"
    / "build_pc_event_manual_compact_static007_batch01_v1.py"
)

SCENE_IDS = tuple(range(3_287, 3_309))
CHANGED_IDS = (3_288, 3_293, 3_295, 3_298, 3_299, 3_300, 3_302, 3_303, 3_304, 3_305, 3_306, 3_307)
REFLOW_ONLY_IDS = (3_288, 3_298, 3_299, 3_300, 3_303, 3_304, 3_305, 3_307)
SEMANTIC_CORRECTION_IDS = (3_293, 3_295, 3_302, 3_306)

E = "\x1b"
TARGETS: Mapping[int, str] = {
    3_288: (
        "별말씀을. 주군께서 천하로 나아갈 발판인\n"
        f"{E}CC미노{E}CZ를 얻으셨으니,\n"
        "어찌 축하하러 오지 않겠습니까."
    ),
    3_293: (
        f"{E}CA노부나가{E}CZ가 함락한 {E}CC이나바야마성{E}CZ의 성하 마을은\n"
        f"당시 {E}CC이노쿠치{E}CZ라 불렸다."
    ),
    3_295: (
        "중국의 산에서 따온 이름인가?\n"
        f"그렇다면 {E}CC이노쿠치{E}CZ는 {E}CC기산{E}CZ의 기슭이니……\n"
        f"‘{E}CC기후{E}CZ’라 이름 붙이면 어떨까?"
    ),
    3_298: (
        f"결정됐군! 앞으로 이 마을은 {E}CC기후{E}CZ라 부르겠다.\n"
        f"마을을 내려다보는 {E}CC이나바야마성{E}CZ은\n"
        f"{E}CC기후성{E}CZ이다!"
    ),
    3_299: "성과 마을 모두 내 것으로\n새로 만들겠다. 나의 천하는 여기서 시작된다.",
    3_300: "그렇다면 주군.\n인장에는 이 문구를 쓰시는 게\n어떻겠습니까?",
    3_302: (
        "그렇습니다.\n"
        f"주나라 {E}CA무왕{E}CZ은 일곱 덕을 갖춘 무로\n"
        "천하를 다스렸다고 전해집니다."
    ),
    3_303: "‘무’라는 글자는 본래,\n창을 멈춰 전란을 그친다는 뜻으로도\n풀이되니……",
    3_304: "잠깐, 기다리게, 스승!\n나는 이제 오와리의 얼간이가 아니야.\n긴 이야기는 나중에, 은거한 뒤에라도 듣지.",
    3_305: "하지만 천하포무…… 글자가 마음에 드는군.\n내 생각에 꼭 맞는 인장이야!\n스승, 고맙네.",
    3_306: "하하하, 훌륭합니다, 훌륭합니다.\n그런 점은 주군께서도 여전하신 듯하여\n안심했습니다.",
    3_307: (
        f"이름 유래에는 여러 설이 있으나,\n{E}CC이노쿠치{E}CZ 마을은 ‘{E}CC기후{E}CZ’가 되고\n"
        f"{E}CC이나바야마성{E}CZ은 ‘{E}CC기후성{E}CZ’으로 다시 지어졌다."
    ),
}

BASELINES: Mapping[int, str] = {
    3_288: (
        "별말씀을. 주군께서 천하로 나아갈\n"
        f"발판인 {E}CC미노{E}CZ를 얻으셨으니,\n"
        "어찌 축하하러 오지 않겠습니까."
    ),
    3_293: (
        f"{E}CA노부나가{E}CZ가 함락한 {E}CC이나바야마성{E}CZ\n"
        f"아래 마을은 당시 {E}CC이노쿠치{E}CZ라 불렸다."
    ),
    3_295: (
        "중국의 산에서 따온 이름인가. 그렇다면\n"
        f"{E}CC이노쿠치{E}CZ는 {E}CC기산{E}CZ의 기슭이니……\n"
        f"‘{E}CC기후{E}CZ’라 이름 붙이면 어떨까?"
    ),
    3_298: (
        f"결정됐군! 앞으로 이 마을은 {E}CC기후{E}CZ라\n"
        f"부르겠다. 마을을 내려다보는\n{E}CC이나바야마성{E}CZ은 {E}CC기후성{E}CZ이다!"
    ),
    3_299: "성과 마을 모두 내 것으로 새로\n만들겠다. 나의 천하는 여기서 시작된다.",
    3_300: "그렇다면 주군.\n인장에는 이 문구를\n쓰시는 게 어떻겠습니까?",
    3_302: (
        "그렇습니다.\n"
        f"주의 {E}CA무왕{E}CZ은 일곱 덕을 갖춘 무로\n"
        "천하를 다스렸다고 전해집니다."
    ),
    3_303: "‘무’라는 글자는 본래,\n창을 멈춰 전란을 그친다는\n뜻으로도 풀이되니……",
    3_304: "잠깐, 기다리게, 스승!\n나는 이제 오와리의 얼간이가 아니야. 긴\n이야기는 나중에, 은거한 뒤에라도 듣지.",
    3_305: "하지만 천하포무…… 글자가 마음에\n드는군. 내 생각에 꼭 맞는 인장이야!\n스승, 고맙네.",
    3_306: "하하하, 참으로 좋습니다.\n그런 점은 주군께서도 여전하신 듯하여\n안심했습니다.",
    3_307: (
        f"이름 유래에는 여러 설이 있으나, {E}CC이노쿠치{E}CZ 마을은\n"
        f"‘{E}CC기후{E}CZ’가 되고 {E}CC이나바야마성{E}CZ은\n"
        f"‘{E}CC기후성{E}CZ’으로 다시 지어졌다."
    ),
}

RATIONALES: Mapping[int, str] = {
    3_288: "‘천하로 나아갈 발판’이라는 한 명사구를 분리하지 않고, 획득 사실과 축하 방문의 인과를 문장 단위로 유지했다.",
    3_293: "城下町을 ‘성하 마을’로 바로잡아 이나바야마성에 딸린 성하를 명시했고, 노부나가의 함락·당시 이노쿠치라는 명칭을 모두 보존했다.",
    3_295: "산 이름의 유래를 묻는 의문문과 기산 기슭이라는 추론, 기후 명명의 제안을 각각 독립 의미 단위로 배치했다.",
    3_298: "‘기후라 부르겠다’와 기후성 명명이라는 두 선언을 어절 중간에서 끊지 않도록 재배치했다.",
    3_299: "‘새로 만들겠다’ 동사구를 분리하지 않고 성·마을의 재건과 천하의 시작이라는 두 문장을 보존했다.",
    3_300: "‘이 문구를 쓰시는 게’라는 권유 구문을 한 줄에 유지했다.",
    3_302: "周를 ‘주나라’로 바로잡아 주 무왕임을 명시하고, 칠덕·천하 통치의 원문 의미를 보존했다.",
    3_303: "‘전란을 그친다는 뜻’이라는 풀이를 한 의미 단위로 유지했다.",
    3_304: "‘긴 이야기’ 명사구를 줄 사이에 나누지 않고, 더는 오와리의 얼간이가 아니라는 선언과 은거 뒤에 듣겠다는 말을 보존했다.",
    3_305: "‘마음에 드는군’과 인장이 생각에 맞는다는 두 화자의 발화를 문장 단위로 재배치했다.",
    3_306: "善哉、善哉의 반복된 찬탄을 ‘훌륭합니다, 훌륭합니다’로 복원하고, 주군이 변함없어 안심했다는 뜻을 보존했다.",
    3_307: "이노쿠치→기후, 이나바야마성→기후성이라는 두 명명 결과를 각 절이 끊기지 않도록 재배치했다.",
}

REQUIRED_TERMS: Mapping[int, tuple[str, ...]] = {
    3_293: ("노부나가", "함락", "이나바야마성", "성하", "마을", "당시", "이노쿠치", "불렸다"),
    3_295: ("중국", "산", "이름", "이노쿠치", "기산", "기슭", "기후", "이름 붙이면"),
    3_302: ("그렇습니다", "주나라", "무왕", "일곱", "덕", "무", "천하", "다스렸", "전해"),
    3_306: ("하하하", "훌륭", "주군", "여전", "안심"),
}

# Deterministic output from the pinned full manual-compact restoration candidate.
EXPECTED_OUTPUT_PROFILE: Mapping[str, Any] | None = {
    "raw_sha256": "D0FAB9C303F8F456184DCDD89AC929C675D6528080F8C29E419E1249BD9B7408",
    "raw_size": 1_043_932,
    "sha256": "62C7F55506DB59A43761DDCE07FB5DA4175AD0AC4B68C03507B37AD52E2AEBD3",
    "size": 1_048_051,
}


class Wave98Error(RuntimeError):
    """Raised when an input, evidence, layout, or private output drifts."""


@dataclass(frozen=True)
class LoadedTable:
    packed: bytes
    raw: bytes
    header: Any
    texts: tuple[str, ...]
    profile: Mapping[str, Any]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Wave98Error(message)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def relative(path: Path) -> str:
    return path.resolve().relative_to(REPO.resolve()).as_posix()


def file_record(path: Path) -> Mapping[str, Any]:
    blob = path.read_bytes()
    return {"relative_path": relative(path), "sha256": sha256(blob), "size": len(blob)}


def profile(packed: bytes, raw: bytes) -> Mapping[str, Any]:
    return {
        "raw_sha256": sha256(raw),
        "raw_size": len(raw),
        "sha256": sha256(packed),
        "size": len(packed),
    }


def candidate_files(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def load_table(path: Path, expected: Mapping[str, Any], label: str) -> LoadedTable:
    require(path.is_file(), f"{label}: file missing: {path}")
    packed = path.read_bytes()
    header, raw = decompress_wrapper(packed)
    parsed = parse_message_table(raw)
    texts = tuple(parsed.texts)
    require(len(texts) == ROW_COUNT, f"{label}: row count drift: {len(texts)}")
    require(rebuild_message_table(parsed, texts) == raw, f"{label}: message table round-trip drift")
    measured = profile(packed, raw)
    require(measured == expected, f"{label}: packed/raw profile drift")
    return LoadedTable(packed=packed, raw=raw, header=header, texts=texts, profile=measured)


def load_module(name: str, path: Path) -> Any:
    require(path.is_file(), f"metrics helper missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import metrics helper: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


metrics = load_module("pc_event_gifu_wave98_metrics", METRICS_HELPER_PATH)


def visible_non_whitespace(value: str) -> str:
    output: list[str] = []
    cursor = 0
    while cursor < len(value):
        if value[cursor] == E:
            output.append(value[cursor : cursor + 3])
            cursor += 3
            continue
        character = value[cursor]
        if not character.isspace():
            output.append(character)
        cursor += 1
    return "".join(output)


def ids_hash(ids: Sequence[int]) -> str:
    return sha256(",".join(str(entry_id) for entry_id in ids).encode("ascii"))


def layout_record(value: str) -> Mapping[str, Any]:
    lines = list(metrics.line_metrics(value))
    require(1 <= len(lines) <= 4, f"line count outside 1..4: {len(lines)}")
    require(all(line["passes_static_patch_007"] for line in lines), "line fails Static Patch 007")
    return {
        "line_count": len(lines),
        "lines": lines,
        "max_raw_g1n_width_px": max(line["raw_g1n_width_px"] for line in lines),
        "max_effective_width_px": max(line["effective_width_px"] for line in lines),
        "over_912px": any(line["over_effective_912px"] for line in lines),
        "all_static_patch_007_lines_pass": all(line["passes_static_patch_007"] for line in lines),
    }


def validate_authored_scope() -> None:
    require(SCENE_IDS == tuple(range(3_287, 3_309)), "scene scope drift")
    require(tuple(TARGETS) == CHANGED_IDS, "target scope/order drift")
    require(set(REFLOW_ONLY_IDS).isdisjoint(SEMANTIC_CORRECTION_IDS), "reflow/semantic scope overlap")
    require(set(REFLOW_ONLY_IDS) | set(SEMANTIC_CORRECTION_IDS) == set(CHANGED_IDS), "changed scope classification drift")
    require(set(BASELINES) == set(CHANGED_IDS), "baseline scope drift")
    require(set(RATIONALES) == set(CHANGED_IDS), "rationale scope drift")
    for entry_id in CHANGED_IDS:
        baseline = BASELINES[entry_id]
        target = TARGETS[entry_id]
        require("\x00" not in target, f"{entry_id}: embedded terminator")
        metrics.assert_no_break_inside_tag(baseline)
        metrics.assert_no_break_inside_tag(target)
        before = metrics.control_signature(baseline)
        after = metrics.control_signature(target)
        require(before == after, f"{entry_id}: control/token signature drift")
        require(not before["runtime_tokens"], f"{entry_id}: runtime token outside scope")
        require(not before["printf_tokens"], f"{entry_id}: printf token outside scope")
        require(before["unknown_percent_count"] == 0, f"{entry_id}: unknown percent token")
        require(not before["other_controls"], f"{entry_id}: unexpected control code")
        layout_record(target)
        if entry_id in REFLOW_ONLY_IDS:
            require(
                visible_non_whitespace(baseline) == visible_non_whitespace(target),
                f"{entry_id}: reflow changed visible Korean text",
            )
        else:
            required = REQUIRED_TERMS[entry_id]
            require(all(term in target for term in required), f"{entry_id}: required meaning term missing")


def load_strict_input() -> tuple[LoadedTable, Mapping[str, Any]]:
    root = STRICT_ROOT.resolve(strict=True)
    require(root.is_relative_to((REPO / "tmp").resolve()), "strict input escapes private tmp")
    expected_files = {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"}
    require(candidate_files(root) == expected_files, "strict input candidate scope drift")
    table = load_table(STRICT_EVENT, EXPECTED_STRICT_PROFILE, "latest Korean strict input")
    audit = json.loads(STRICT_AUDIT.read_text(encoding="utf-8"))
    manifest = json.loads(STRICT_MANIFEST.read_text(encoding="utf-8"))
    require(audit.get("candidate_only") is True, "strict input audit is not private")
    require(manifest.get("candidate_only") is True, "strict input manifest is not private")
    require(manifest.get("output") == table.profile, "strict input manifest profile drift")
    require(audit.get("output_event_profile") == table.profile, "strict input audit profile drift")
    return table, {
        "workstream": STRICT_WORKSTREAM,
        "candidate_relative": relative(root),
        "event_relative": relative(STRICT_EVENT),
        "event_profile": table.profile,
        "audit": file_record(STRICT_AUDIT),
        "candidate_manifest": file_record(STRICT_MANIFEST),
    }


def build_bundle(require_output_profile: bool) -> tuple[bytes, Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]]:
    validate_authored_scope()
    strict, strict_record = load_strict_input()
    sources = {label: load_table(path, expected, f"source {label}") for label, (path, expected) in SOURCES.items()}
    texts = list(strict.texts)
    for entry_id, baseline in BASELINES.items():
        require(texts[entry_id] == baseline, f"{entry_id}: strict Korean baseline drift")
        texts[entry_id] = TARGETS[entry_id]

    for entry_id in SCENE_IDS:
        metrics.assert_no_break_inside_tag(texts[entry_id])
        layout_record(texts[entry_id])

    raw = rebuild_message_table(parse_message_table(strict.raw), tuple(texts))
    event = recompress_wrapper(raw, strict.header)
    output_profile = profile(event, raw)
    if require_output_profile:
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        require(output_profile == EXPECTED_OUTPUT_PROFILE, "deterministic output profile drift")

    changed_ids = [entry_id for entry_id, (before, after) in enumerate(zip(strict.texts, texts)) if before != after]
    require(changed_ids == list(CHANGED_IDS), f"changed-row scope drift: {changed_ids}")

    rows: list[Mapping[str, Any]] = []
    for entry_id in SCENE_IDS:
        before = strict.texts[entry_id]
        after = texts[entry_id]
        row_layout = layout_record(after)
        source_evidence = {label: text_hash(source.texts[entry_id]) for label, source in sources.items()}
        rows.append(
            {
                "entry_id": entry_id,
                "changed": entry_id in CHANGED_IDS,
                "change_kind": (
                    "semantic_and_contextual_reflow"
                    if entry_id in SEMANTIC_CORRECTION_IDS
                    else "contextual_reflow"
                    if entry_id in REFLOW_ONLY_IDS
                    else "reviewed_preserve"
                ),
                "baseline_ko_utf16le_sha256": text_hash(before),
                "target_ko_utf16le_sha256": text_hash(after),
                "source_text_utf16le_sha256": source_evidence,
                "control_signature": metrics.control_signature(after),
                "korean_sentence_shortened_or_deleted": False,
                "japanese_source_line_breaks_reused": False,
                "rationale": RATIONALES.get(entry_id, "원문·PC 다국어 대조 후 현재 문안과 문맥 개행을 유지했다."),
                **row_layout,
            }
        )

    require(all(not row["korean_sentence_shortened_or_deleted"] for row in rows), "sentence shortening flag drift")
    require(all(not row["over_912px"] for row in rows), "layout exceeds effective 912px")
    require(all(row["line_count"] <= 4 for row in rows), "layout exceeds four lines")

    source_records = {
        label: {
            "path": str(path),
            "profile": sources[label].profile,
        }
        for label, (path, _expected) in SOURCES.items()
    }
    audit: Mapping[str, Any] = {
        "schema": SCHEMA + ".audit",
        "candidate_only": True,
        "resource": RESOURCE.as_posix(),
        "strict_input": strict_record,
        "source_resources": source_records,
        "static_patch_007_layout": {
            "runtime_font_px": 30,
            "runtime_usable_line_width_px": 912,
            "max_lines": 4,
            "raw_g1n_full_width_px": 48,
            "raw_g1n_half_width_px": 24,
            "raw_g1n_pass_limit_px": 1_440,
            "effective_width_formula": "ceil(raw_g1n_width_px * 30 / 48)",
            "effective_width_pass_limit_px": 912,
        },
        "coverage": {
            "reviewed_scene_ids": list(SCENE_IDS),
            "reviewed_scene_row_count": len(SCENE_IDS),
            "changed_row_ids": list(CHANGED_IDS),
            "changed_row_count": len(CHANGED_IDS),
            "changed_row_ids_sha256": ids_hash(CHANGED_IDS),
            "reflow_only_ids": list(REFLOW_ONLY_IDS),
            "semantic_correction_ids": list(SEMANTIC_CORRECTION_IDS),
            "unchanged_after_review_ids": [entry_id for entry_id in SCENE_IDS if entry_id not in CHANGED_IDS],
            "all_rows_static_patch_007_pass": True,
            "all_rows_four_or_fewer_lines": True,
            "all_rows_sentence_shortened_or_deleted_false": True,
            "unresolved_runtime_hold_ids": [],
        },
        "output_event_profile": output_profile,
        "rows": rows,
        "policy": {
            "direct_pc_jp_en_sc_tc_used_as_read_only_evidence": True,
            "switch_translation_used": False,
            "japanese_source_line_breaks_not_reused": True,
            "sentence_shortening_or_deletion_allowed": False,
            "tag_internal_line_break_allowed": False,
            "steam_game_resource_written": False,
            "git_operation_performed": False,
            "release_published": False,
            "network_operation_performed": False,
        },
    }
    manifest: Mapping[str, Any] = {
        "schema": SCHEMA + ".manifest",
        "candidate_only": True,
        "candidate_output_must_be_under": relative(TMP_ROOT),
        "resource": RESOURCE.as_posix(),
        "strict_input": strict_record,
        "reviewed_scene_ids": list(SCENE_IDS),
        "applied_row_ids": list(CHANGED_IDS),
        "output": output_profile,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }
    return event, output_profile, audit, manifest


def require_private(path: Path) -> Path:
    resolved = path.resolve()
    root = TMP_ROOT.resolve()
    require(resolved.is_relative_to(root), f"candidate path escapes private tmp root: {resolved}")
    return resolved


def write_candidate(event: bytes, audit: Mapping[str, Any], manifest: Mapping[str, Any]) -> Path:
    root = require_private(CANDIDATE_ROOT)
    if root.exists():
        shutil.rmtree(root)
    (root / RESOURCE).parent.mkdir(parents=True, exist_ok=True)
    (root / RESOURCE).write_bytes(event)
    (root / "audit.v1.json").write_bytes(canonical_json(audit))
    (root / "candidate_manifest.v1.json").write_bytes(canonical_json(manifest))
    return root


def verify_private_candidate() -> Mapping[str, Any]:
    event, output_profile, audit, manifest = build_bundle(require_output_profile=True)
    root = require_private(CANDIDATE_ROOT)
    require(root.is_dir(), "private candidate missing")
    expected_files = {RESOURCE.as_posix(), "audit.v1.json", "candidate_manifest.v1.json"}
    require(candidate_files(root) == expected_files, "private candidate file scope drift")
    require((root / RESOURCE).read_bytes() == event, "private event differs from deterministic build")
    require((root / "audit.v1.json").read_bytes() == canonical_json(audit), "private audit differs")
    require((root / "candidate_manifest.v1.json").read_bytes() == canonical_json(manifest), "private manifest differs")
    return {
        "status": "PASS",
        "candidate_root": relative(root),
        "event_profile": output_profile,
        "reviewed_scene_row_count": len(SCENE_IDS),
        "applied_row_count": len(CHANGED_IDS),
        "applied_row_ids": list(CHANGED_IDS),
        "unresolved_runtime_hold_count": 0,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
    }


def source_whitespace_check() -> None:
    for path in (
        WORKSTREAM / "README_KO.md",
        SCRIPT,
        WORKSTREAM / "test_pc_event_gifu_quality_wave98_v1.py",
    ):
        require(path.is_file(), f"authoring file missing: {path.name}")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            require(line == line.rstrip(), f"trailing whitespace: {path.name}:{number}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("profile", "build", "verify-private", "diff-check"))
    command = parser.parse_args().command
    if command == "profile":
        _event, output_profile, _audit, _manifest = build_bundle(require_output_profile=False)
        print(json.dumps(output_profile, ensure_ascii=False, sort_keys=True))
        return 0
    if command == "build":
        source_whitespace_check()
        require(EXPECTED_OUTPUT_PROFILE is not None, "output profile is not pinned")
        event, _output_profile, audit, manifest = build_bundle(require_output_profile=True)
        print(relative(write_candidate(event, audit, manifest)))
        return 0
    if command == "verify-private":
        source_whitespace_check()
        print(json.dumps(verify_private_candidate(), ensure_ascii=False, sort_keys=True))
        return 0
    _event, output_profile, audit, _manifest = build_bundle(require_output_profile=True)
    print(
        json.dumps(
            {
                "event_profile": output_profile,
                "changed_row_ids": audit["coverage"]["changed_row_ids"],
                "reviewed_scene_ids": audit["coverage"]["reviewed_scene_ids"],
                "unresolved_runtime_hold_ids": audit["coverage"]["unresolved_runtime_hold_ids"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Wave98Error, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
