#!/usr/bin/env python3
"""Read-only re-audit of Wave 51 block 13–14 dialogue holds.

This workstream reads the latest private Wave 97 PC dialogue candidate and
the direct PC JP/EN/SC/TC resources.  It emits a classification report only:
no MSGGAME binary is rebuilt, and there is no Steam, Git, release, or network
code path.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
PUBLIC = WORKSTREAM / "public"
OUTPUT = PUBLIC / "pc_dialogue_blocks13_14_hold_reaudit.v1.json"

SCHEMA = "nobu16.kr.pc-dialogue-blocks13-14-hold-reaudit.v1"
RESOURCE_BASE = "MSG/JP/msggame.bin"
RESOURCE_PK = "MSG_PK/JP/msggame.bin"

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
W97_ROOT = REPO / "tmp" / "pc_dialogue_quality_wave97_pk_security_development_static_v1" / "candidate"

CURRENT_PATHS = {
    RESOURCE_BASE: W97_ROOT / RESOURCE_BASE,
    RESOURCE_PK: W97_ROOT / RESOURCE_PK,
}
CURRENT_PROFILES = {
    RESOURCE_BASE: (1_504_458, "27C0D9A5FEE6D212105EE6E6BA14F5DF7B653C0073DBF80AAEBB697D34CC51B2"),
    RESOURCE_PK: (1_806_687, "E507D55F2FECE844FA3AF1FBA213DE2DB7D0F4113082190615DA9C15D3906540"),
}

STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DIRECT_PATHS = {
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
DIRECT_HASHES = {
    "JP_BASE": "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
    "JP_PK": "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
    "EN": "68B9597DEA78CA2327EE36D62EF03DD673CE2449D40A18392D1ACF837B85A916",
    "SC": "8884BCC1C085D85AEFDBB2C45180D5E9D4A495B0094A157444C2BA2D39029802",
    "TC": "C5EF565CBDFB4D95B5A1785D83A758C0057569CCC6ECF1EA873EA7E5F8AD6A23",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def load_w27() -> Any:
    require(W27_HELPER.is_file(), "Wave 27 parser helper is absent")
    require(sha256_path(W27_HELPER) == W27_HELPER_SHA256, "Wave 27 parser helper hash differs")
    spec = importlib.util.spec_from_file_location("blocks13_14_reaudit_w27", W27_HELPER)
    require(spec is not None and spec.loader is not None, "cannot import Wave 27 parser helper")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


W27 = load_w27()


def expand_specs(specs: Iterable[str]) -> set[tuple[int, int]]:
    result: set[tuple[int, int]] = set()
    for spec in specs:
        block_text, ids_text = spec.split(":", 1)
        block = int(block_text)
        for part in ids_text.split(","):
            if "-" in part:
                start, end = (int(value) for value in part.split("-", 1))
                result.update((block, record_id) for record_id in range(start, end + 1))
            else:
                result.add((block, int(part)))
    return result


# This is the complete block-13/14 hold inventory declared by Wave 51's
# README/build script.  Overlapping reasons are intentionally retained.
HOLD_GROUPS: Mapping[str, Mapping[str, tuple[str, ...]]] = {
    "terminology_policy": {
        RESOURCE_BASE: ("13:185", "13:341", "13:344", "13:409-412", "14:71"),
        RESOURCE_PK: ("13:185", "13:365", "13:368", "13:444-447", "14:97-98"),
    },
    "dialogue_reflow": {
        RESOURCE_BASE: ("13:213",),
        RESOURCE_PK: ("13:213",),
    },
    "help_or_table_ui_qa": {
        RESOURCE_BASE: ("13:8", "14:57"),
        RESOURCE_PK: ("13:8", "14:81", "14:156-157"),
    },
    "semantic_retranslation": {
        RESOURCE_PK: ("13:563", "13:573", "13:590", "14:97-98", "14:221"),
    },
    "runtime_or_morphology": {
        RESOURCE_BASE: (
            "13:15-16", "13:22", "13:25-26", "13:51", "13:53-54", "13:75", "13:77",
            "13:93-94", "13:105", "13:112-115", "13:117-119", "13:123-126", "13:129",
            "13:141", "13:162-164", "13:171", "13:182",
        ),
        RESOURCE_PK: (
            "13:15-16", "13:22", "13:25-26", "13:51", "13:53-54", "13:75", "13:77",
            "13:93-94", "13:105", "13:112-115", "13:117-119", "13:123-126", "13:129",
            "13:141", "13:162-164", "13:171", "13:182", "14:109",
        ),
    },
    "source_condition_conflict": {
        RESOURCE_BASE: ("14:112",),
        RESOURCE_PK: ("14:154-155",),
    },
}


def key(resource: str, coordinate: tuple[int, int]) -> str:
    return f"{'Base' if resource == RESOURCE_BASE else 'PK'} {coordinate[0]}:{coordinate[1]}"


def make_group_index() -> Mapping[tuple[str, tuple[int, int]], list[str]]:
    result: dict[tuple[str, tuple[int, int]], list[str]] = defaultdict(list)
    for group, resources in HOLD_GROUPS.items():
        for resource, specs in resources.items():
            for coordinate in expand_specs(specs):
                result[(resource, coordinate)].append(group)
    return result


GROUP_INDEX = make_group_index()

# Base 14:71 is the shorter pre-PK version of PK 14:97.  The remaining Base
# holds either retain their same-coordinate PK text or map uniquely by full
# direct-JP literals.
BASE_TO_PK_CONTEXT_OVERRIDES: Mapping[tuple[int, int], tuple[int, int]] = {
    (14, 71): (14, 97),
}


STATIC_POLICY_RETAIN = {
    (resource, coordinate)
    for (resource, coordinate), groups in GROUP_INDEX.items()
    if groups == ["terminology_policy"]
}


STATIC_REFLOW_PROPOSALS: Mapping[tuple[str, tuple[int, int]], str] = {
    (RESOURCE_BASE, (13, 213)): "군의 개발이 진행되면 더욱 효과가 큰\n「성하 시설」을 건설할 수 있게 됩니다.\n어서 지어 봅시다.",
    (RESOURCE_PK, (13, 213)): "군의 개발이 진행되면 더욱 효과가 큰\n「성하 시설」을 건설할 수 있게 됩니다.\n어서 지어 봅시다.",
}

STATIC_TEXT_PROPOSALS: Mapping[tuple[str, tuple[int, int]], str] = {
    (RESOURCE_PK, (13, 563)): (
        "무장들은 승리와 공명을 위해 스스로 판단해 부대를 움직이고 싸웁니다.\n\n"
        "하지만 전황이 변하면 판단을 구해 오기도 합니다.\n"
        "기회와 위기에 어떻게 대응하느냐에 따라 승패가 갈립니다."
    ),
    (RESOURCE_PK, (13, 573)): (
        "무장들은 승리와 공명을 위해 스스로 판단해 부대를 움직이고 싸웁니다.\n\n"
        "하지만 전황이 변하면 판단을 구해 오기도 합니다.\n"
        "기회와 위기에 어떻게 대응하느냐에 따라 승패가 갈립니다."
    ),
    (RESOURCE_PK, (13, 590)): (
        "【공성전으로 인한 위풍】\n"
        "승패에 따라 위풍이 발생합니다.\n"
        "적의 침공을 막아 내면 반격의 기회가 됩니다.\n"
        "하지만 적에게 제압당하면 적의 위풍이 발생하므로 주의하십시오.\n"
        "※방위 승리 때 발생한 위풍으로는 적 성의 배반이 일어나지 않습니다.\n\n"
        "방위 거점은 주변에서 발생한 위풍의 영향을 받지 않고 그 확산을 막습니다.\n"
        "방위 거점을 잘 설정하면 패배의 영향을 최소화할 수 있습니다."
    ),
}

SEMANTIC_DRAFTS: Mapping[tuple[str, tuple[int, int]], str] = {
    (RESOURCE_PK, (14, 97)): (
        "【건의】\n"
        "건의는 상황에 따라 가신이 다이묘에게 올리는 제언입니다.\n"
        "승인하면 가신이 건의 내용을 실행에 옮기며, 거부할 수도 있습니다.\n"
        "성주·대관·측근 무장이 건의해 옵니다.\n\n"
        "◇건의의 종류\n"
        "건의에는 몇 가지 종류가 있으며, 아이콘으로 구별할 수 있습니다.\n"
        " ·시동의 건의 …　┨　튜토리얼로서 다음에 할 일이 건의됩니다.\n"
        " ·조언      …　┯　상황에 따라 지금 해야 할 일이 건의됩니다.\n"
        " ·통상 건의   … 가신이 실행해야 한다고 생각하는 일이 건의됩니다.\n"
        "            금전과 노력이 필요하며, 실패할 수도 있습니다.\n"
        " ·세력 목표 건의 … 현재 설정된 세력의 목표가 표시됩니다.\n"
        "            제안된 내용을 기한 내에 달성하면 보상을 받습니다.\n"
        "            ※달성하지 못해도 불이익은 없습니다.\n"
        "            ※설정>시나리오에서 끌 수 있습니다."
    ),
    (RESOURCE_PK, (14, 98)): (
        "【건의】\n"
        "건의는 상황에 따라 가신이 다이묘에게 올리는 제언입니다.\n"
        "승인하면 가신이 건의 내용을 실행하며, 거부할 수도 있습니다.\n"
        "성주·대관·측근 무장이 건의합니다.\n\n"
        "◇건의의 종류\n"
        "건의에는 몇 가지 종류가 있으며, 아이콘으로 구별할 수 있습니다.\n"
        " ·시동의 건의 …　┨　튜토리얼로서 다음에 할 일이 건의됩니다.\n"
        " ·조언      …　┯　상황에 따라 지금 해야 할 일이 건의됩니다.\n"
        " ·통상 건의   … 가신이 실행해야 한다고 생각하는 일이 건의됩니다.\n"
        "            금전과 노력이 필요하며, 실패할 수도 있습니다.\n"
        " ·소목표 건의   … 세력 발전을 위한 소목표가 건의됩니다.\n"
        "            제안된 내용을 기한 내에 달성하면 보상을 받습니다.\n"
        "            ※달성하지 못해도 불이익은 없습니다.\n"
        "            ※설정>시나리오에서 끌 수 있습니다."
    ),
    (RESOURCE_PK, (14, 221)): (
        "【이벤트 합전】\n"
        "게임에서 일정 조건을 충족하면 발생하는 역사적인 전투입니다.\n"
        "이벤트 합전 중에는 전장에서 다양한 사건이 발생합니다.\n"
        "부대를 조작해 목표를 달성하고 승리를 목표로 합시다.\n\n"
        "역사적으로 패배한 세력을 조작하는 경우도 있습니다.\n"
        "승리하면 『노부나가의 야망·신생』만의 오리지널 전개를 즐길 수 있습니다.\n\n"
        "◇이벤트 합전의 특징\n"
        " ·화면 왼쪽에 표시되는 목표를 달성하면 승리할 수 있다\n"
        " ·이벤트 합전의 종류마다 출진하는 무장과 병력이 정해져 있다\n"
        " ·일부 특성·정책·가재의 효과는 이벤트 합전 중에는 발휘되지 않는다"
    ),
}

UI_TEXT_FINDINGS: Mapping[tuple[str, tuple[int, int]], Mapping[str, str]] = {
    (RESOURCE_PK, (14, 156)): {
        "evidence": "JP 足軽大将, EN Infantry Leader, SC/TC 足轻大将이지만 KO는 ‘족경대장’이다.",
        "proposal": " ·아시가루대장 … 「영주」「대관」에 임명 가능 ",
    },
    (RESOURCE_PK, (14, 157)): {
        "evidence": "JP 侍大将, EN Samurai Leader, SC/TC 侍大将이지만 KO는 ‘시대장’이다.",
        "proposal": " ·사무라이대장 … 부장과 같은 직명에 임명 가능",
    },
}

EVIDENCE_NOTES: Mapping[tuple[str, tuple[int, int]], str] = {
    (RESOURCE_PK, (13, 563)): "JP 判断を求めてくる 및 EN request your commands는 ‘도움’이 아니라 플레이어의 판단·지시를 구한다는 뜻이다.",
    (RESOURCE_PK, (13, 573)): "JP 判断を求めてくる 및 EN request your commands는 ‘도움’이 아니라 플레이어의 판단·지시를 구한다는 뜻이다.",
    (RESOURCE_PK, (13, 590)): "JP 威風が発生する/敵城の寝返りは起こらない와 EN/SC/TC는 위풍의 발생과 적 성 배반 불발을 명시한다.",
    (RESOURCE_PK, (14, 97)): "JP 通常の具申・勢力目標の具申과 EN Normal/Clan Target submissions를 KO가 ‘통상 보고/세력 목표 보고’로 바꾸어 제도명과 주체가 흐려졌다.",
    (RESOURCE_PK, (14, 98)): "JP 小目標具申は 세력 발전을 위한 소목표 건의인데, KO가 현재 설정된 세력 목표의 표시로 바꾸었다.",
    (RESOURCE_PK, (14, 221)): "JP 敗北した勢力を操作する場合/オリジナルの展開, EN control clans that suffered historical defeats/uncover original developments와 달리 KO가 ‘조작되는 상황’과 ‘원작 체험’으로 의미를 바꾸었다.",
    (RESOURCE_BASE, (13, 213)): "JP 可能になります。早速建ててみましょう와 EN/SC/TC의 동일 안내는 완결된 세 문장이다. KO의 ‘가능해\\n집니다’만 어절을 분리한다.",
    (RESOURCE_PK, (13, 213)): "JP 可能になります。早速建ててみましょう와 EN/SC/TC의 동일 안내는 완결된 세 문장이다. KO의 ‘가능해\\n집니다’만 어절을 분리한다.",
    (RESOURCE_BASE, (14, 57)): "내용 자체는 JP와 대응하지만 ‘적 성\\n에’, ‘무장\\n이’의 어절 분리가 표 UI 실제 폭과 연결돼 있다.",
    (RESOURCE_PK, (14, 81)): "내용 자체는 JP와 대응하지만 ‘적 성\\n에’, ‘무장\\n이’의 어절 분리가 표 UI 실제 폭과 연결돼 있다.",
    (RESOURCE_BASE, (14, 112)): "JP는 마지막 조건을 知略70 이상으로 표기하지만 대응 PK EN/SC/TC는 POL/政務 70 이상으로 표기한다. 실게임 조건 없이는 어느 쪽도 확정할 수 없다.",
    (RESOURCE_PK, (14, 154)): "JP는 마지막 조건을 知略70 이상으로 표기하지만 EN/SC/TC는 POL/政務 70 이상으로 표기한다. 실게임 조건 없이는 어느 쪽도 확정할 수 없다.",
    (RESOURCE_PK, (14, 155)): "JP는 마지막 조건을 知略70 이상으로 표기하지만 SC/TC는 政務 70 이상으로 표기한다. 실게임 조건 없이는 어느 쪽도 확정할 수 없다.",
}


def text(record: Any) -> str:
    return "".join(W27.literal_texts(record))


def text_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-16-le")).hexdigest().upper()


def runtime_02xx_opcodes(record: Any) -> list[str]:
    opcodes: list[str] = []
    for span in W27.opaque_spans(record):
        for index, byte in enumerate(span[:-1]):
            if byte == 0x02:
                opcodes.append(span[index:index + 2].hex().upper())
    return opcodes


def marker_signature(record: Any) -> list[list[str]]:
    return [[start.hex().upper(), end.hex().upper()] for start, end in W27.marker_topology(record)]


def record_structure(record: Any, advance: Any) -> Mapping[str, Any]:
    value = text(record)
    layout = W27.line_layout((value,), advance)
    return {
        "record_sha256": hashlib.sha256(record.data).hexdigest().upper(),
        "literal_count": len(W27.literal_texts(record)),
        "marker_signature": marker_signature(record),
        "complete_0143_commands": list(W27.complete_0143_commands(W27.opaque_spans(record))),
        "runtime_02xx_opcodes": runtime_02xx_opcodes(record),
        "terminator_present": record.data.endswith(W27.RECORD_TERMINATOR),
        "manual_line_count": value.count("\n") + 1,
        "line_widths_px": list(layout["line_widths_px"]),
        "max_line_width_px": layout["max_width_px"],
        "fallback_codepoints": list(layout["wide_fallback_codepoints"]),
    }


def source_profile(path: Path, expected_hash: str) -> Mapping[str, Any]:
    require(path.is_file(), f"source missing: {path}")
    actual = sha256_path(path)
    require(actual == expected_hash, f"source hash drift: {path}")
    return {"relative_or_absolute_path": str(path), "size": path.stat().st_size, "sha256": actual}


def current_profile(resource: str) -> Mapping[str, Any]:
    path = CURRENT_PATHS[resource]
    expected_size, expected_hash = CURRENT_PROFILES[resource]
    require(path.is_file(), f"Wave 97 candidate missing: {resource}")
    require(path.stat().st_size == expected_size, f"Wave 97 candidate size drift: {resource}")
    actual = sha256_path(path)
    require(actual == expected_hash, f"Wave 97 candidate hash drift: {resource}")
    return {"relative_path": path.relative_to(REPO).as_posix(), "size": expected_size, "sha256": actual}


def classification(resource: str, coordinate: tuple[int, int], groups: list[str]) -> tuple[str, str, str | None]:
    item = (resource, coordinate)
    if item in STATIC_REFLOW_PROPOSALS:
        return (
            "a_static_high_confidence",
            "static_reflow_ready",
            "Direct JP and the three PC locale contexts agree; reflow only fixes a Korean word split and keeps all source meaning.",
        )
    if item in STATIC_TEXT_PROPOSALS:
        return (
            "a_static_high_confidence",
            "static_text_correction_ready",
            "No 02xx/0143 control route is required for the correction; direct PC JP/EN/SC/TC establish the missing meaning.",
        )
    if item in SEMANTIC_DRAFTS:
        return (
            "b_semantic_retranslation",
            "semantic_draft_ready_for_later_layout_review",
            "Source meaning is materially wrong across several clauses; a full semantic rewrite and later table/layout audit are required.",
        )
    if item in UI_TEXT_FINDINGS:
        return (
            "c_runtime_or_real_game_ui_evidence",
            "text_error_found_but_table_ui_qa_required",
            "The source term is unambiguous, but the replacement grows a fixed-width help-table label and needs real-game UI validation before a candidate.",
        )
    if "source_condition_conflict" in groups:
        return (
            "c_runtime_or_real_game_ui_evidence",
            "source_condition_conflict_requires_game_rule_evidence",
            "PC Japanese and other PC locale condition statements conflict; text cannot choose the active game rule.",
        )
    if "help_or_table_ui_qa" in groups:
        return (
            "c_runtime_or_real_game_ui_evidence",
            "fixed_help_or_table_ui_width_requires_real_game_qa",
            "The remaining issue is a manual wrap/alignment in a fixed help or table widget, not a safe text-only edit.",
        )
    if "runtime_or_morphology" in groups:
        return (
            "c_runtime_or_real_game_ui_evidence",
            "runtime_or_morphology_route_requires_evidence",
            "At least one 02xx runtime opcode or complete 0143 morphology command remains; preserve the route until token/morphology behavior is evidenced.",
        )
    if "terminology_policy" in groups:
        return (
            "a_static_high_confidence",
            "static_policy_retain_current_ko",
            "The project already standardized 小姓 as ‘시동’; direct source comparison finds no translation error requiring 시종 substitution.",
        )
    raise RuntimeError(f"no classification for {key(resource, coordinate)}")


def proposed_text(resource: str, coordinate: tuple[int, int]) -> str | None:
    item = (resource, coordinate)
    return STATIC_REFLOW_PROPOSALS.get(item) or STATIC_TEXT_PROPOSALS.get(item) or SEMANTIC_DRAFTS.get(item) or UI_TEXT_FINDINGS.get(item, {}).get("proposal")


def find_pk_context_coordinate(
    resource: str,
    coordinate: tuple[int, int],
    jp_record: Any,
    pk_by_text: Mapping[tuple[str, ...], list[tuple[int, int]]],
) -> tuple[int, int] | None:
    if resource == RESOURCE_PK:
        return coordinate
    if coordinate in BASE_TO_PK_CONTEXT_OVERRIDES:
        return BASE_TO_PK_CONTEXT_OVERRIDES[coordinate]
    matches = pk_by_text.get(W27.literal_texts(jp_record), [])
    if coordinate in matches:
        return coordinate
    return matches[0] if len(matches) == 1 else None


def direct_contexts(
    resource: str,
    coordinate: tuple[int, int],
    jp_record: Any,
    archives: Mapping[str, Mapping[tuple[int, int], Any]],
    pk_by_text: Mapping[tuple[str, ...], list[tuple[int, int]]],
) -> Mapping[str, Any]:
    pk_coordinate = find_pk_context_coordinate(resource, coordinate, jp_record, pk_by_text)
    contexts: dict[str, Any] = {
        "jp": text(jp_record),
        "en": None,
        "sc": None,
        "tc": None,
        "cross_locale_coordinate": None,
    }
    if pk_coordinate is None:
        contexts["cross_locale_coordinate"] = "unresolved_base_to_pk_text_mapping"
        return contexts
    contexts["cross_locale_coordinate"] = f"{pk_coordinate[0]}:{pk_coordinate[1]}"
    for language in ("EN", "SC", "TC"):
        record = archives[language].get(pk_coordinate)
        require(record is not None, f"direct PC {language} coordinate missing: {pk_coordinate}")
        contexts[language.lower()] = text(record)
    return contexts


def build_report() -> Mapping[str, Any]:
    require(W97_BUILDER.is_file(), "Wave 97 builder is absent")
    require(sha256_path(W97_BUILDER) == W97_BUILDER_SHA256, "Wave 97 builder hash differs")
    candidate_profiles = {resource: current_profile(resource) for resource in (RESOURCE_BASE, RESOURCE_PK)}
    direct_profiles = {name: source_profile(path, DIRECT_HASHES[name]) for name, path in DIRECT_PATHS.items()}

    archives = {
        "KO_BASE": W27.records_by_coordinate(CURRENT_PATHS[RESOURCE_BASE].read_bytes()),
        "KO_PK": W27.records_by_coordinate(CURRENT_PATHS[RESOURCE_PK].read_bytes()),
        "JP_BASE": W27.records_by_coordinate(DIRECT_PATHS["JP_BASE"].read_bytes()),
        "JP_PK": W27.records_by_coordinate(DIRECT_PATHS["JP_PK"].read_bytes()),
        "EN": W27.records_by_coordinate(DIRECT_PATHS["EN"].read_bytes()),
        "SC": W27.records_by_coordinate(DIRECT_PATHS["SC"].read_bytes()),
        "TC": W27.records_by_coordinate(DIRECT_PATHS["TC"].read_bytes()),
    }
    pk_by_text: dict[tuple[str, ...], list[tuple[int, int]]] = defaultdict(list)
    for coordinate, record in archives["JP_PK"].items():
        pk_by_text[W27.literal_texts(record)].append(coordinate)
    advance, font_profile = W27.load_font_advance()

    rows: list[Mapping[str, Any]] = []
    for (resource, coordinate), groups in sorted(GROUP_INDEX.items(), key=lambda item: (item[0][0], item[0][1])):
        current_name = "KO_BASE" if resource == RESOURCE_BASE else "KO_PK"
        jp_name = "JP_BASE" if resource == RESOURCE_BASE else "JP_PK"
        current = archives[current_name].get(coordinate)
        jp = archives[jp_name].get(coordinate)
        require(current is not None and jp is not None, f"coordinate missing: {key(resource, coordinate)}")
        category, disposition, rationale = classification(resource, coordinate, groups)
        contexts = direct_contexts(resource, coordinate, jp, archives, pk_by_text)
        current_structure = record_structure(current, advance)
        jp_structure = record_structure(jp, advance)
        runtime_or_morph = bool(current_structure["runtime_02xx_opcodes"] or current_structure["complete_0143_commands"])
        proposal = proposed_text(resource, coordinate)
        if category == "a_static_high_confidence" and disposition != "static_policy_retain_current_ko":
            require(not runtime_or_morph, f"static classification has runtime/morph route: {key(resource, coordinate)}")
            require(proposal is not None, f"static correction lacks proposal: {key(resource, coordinate)}")
        rows.append(
            {
                "resource": resource,
                "coordinate": f"{coordinate[0]}:{coordinate[1]}",
                "prior_hold_groups": groups,
                "classification": category,
                "disposition": disposition,
                "rationale": rationale,
                "finding": EVIDENCE_NOTES.get((resource, coordinate), UI_TEXT_FINDINGS.get((resource, coordinate), {}).get("evidence")),
                "current_ko": text(current),
                "current_ko_utf16le_sha256": text_hash(text(current)),
                "direct_pc_sources": contexts,
                "current_structure": current_structure,
                "direct_jp_structure": jp_structure,
                "current_and_jp_marker_topology_match": W27.marker_topology(current) == W27.marker_topology(jp),
                "current_and_jp_opaque_spans_match": W27.opaque_spans(current) == W27.opaque_spans(jp),
                "proposed_ko_without_shortening": proposal,
                "proposal_status": (
                    "not_needed_current_policy_is_canonical"
                    if disposition == "static_policy_retain_current_ko"
                    else "draft_only_no_candidate_binary_created"
                    if proposal is not None
                    else "no_text_proposal_until_runtime_or_ui_evidence"
                ),
            }
        )

    counts = Counter(row["classification"] for row in rows)
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "read_only_audit": True,
        "candidate_binary_created_by_this_workstream": False,
        "steam_game_resource_written": False,
        "git_operation_performed": False,
        "release_published": False,
        "network_operation_performed": False,
        "scope": {
            "legacy_workstream": "pc_dialogue_quality_wave51_static_blocks13_14_v1",
            "latest_candidate": "pc_dialogue_quality_wave97_pk_security_development_static_v1",
            "resources": [RESOURCE_BASE, RESOURCE_PK],
            "classification_codes": {
                "a_static_high_confidence": "Static text-only correction or verified no-change is safe to prepare after normal record/topology validation.",
                "b_semantic_retranslation": "Direct sources establish a material meaning problem, but a semantic rewrite and later layout review are still required.",
                "c_runtime_or_real_game_ui_evidence": "Do not make a text candidate until runtime/morphology, active game rule, or real UI geometry is evidenced.",
            },
        },
        "pinned_inputs": {
            "wave97_builder": {"relative_path": W97_BUILDER.relative_to(REPO).as_posix(), "sha256": W97_BUILDER_SHA256},
            "wave97_candidate": candidate_profiles,
            "direct_pc_sources": direct_profiles,
            "font_profile": font_profile,
        },
        "summary": {
            "unique_hold_row_count": len(rows),
            "classification_counts": dict(sorted(counts.items())),
            "static_text_correction_ready_count": sum(
                row["disposition"] in {"static_reflow_ready", "static_text_correction_ready"}
                for row in rows
            ),
            "static_policy_retain_current_ko_count": sum(
                row["disposition"] == "static_policy_retain_current_ko" for row in rows
            ),
            "static_high_confidence_ids": [f"{row['resource']}:{row['coordinate']}" for row in rows if row["classification"] == "a_static_high_confidence"],
            "semantic_retranslation_ids": [f"{row['resource']}:{row['coordinate']}" for row in rows if row["classification"] == "b_semantic_retranslation"],
            "runtime_or_ui_evidence_ids": [f"{row['resource']}:{row['coordinate']}" for row in rows if row["classification"] == "c_runtime_or_real_game_ui_evidence"],
            "all_rows_have_direct_pc_jp": all(row["direct_pc_sources"]["jp"] is not None for row in rows),
            "all_rows_have_direct_pc_en_sc_tc_context": all(
                all(row["direct_pc_sources"][language] is not None for language in ("en", "sc", "tc"))
                for row in rows
            ),
            "all_rows_read_only": True,
        },
        "rows": rows,
    }
    return report


def validate(report: Mapping[str, Any]) -> None:
    require(report["schema"] == SCHEMA, "schema differs")
    require(report["summary"]["unique_hold_row_count"] == len(GROUP_INDEX), "hold inventory count differs")
    require(report["summary"]["all_rows_have_direct_pc_jp"], "direct PC Japanese source is missing")
    require(report["summary"]["all_rows_have_direct_pc_en_sc_tc_context"], "direct PC EN/SC/TC context is missing")
    require(report["summary"]["all_rows_read_only"], "read-only state differs")
    allowed = {
        "a_static_high_confidence",
        "b_semantic_retranslation",
        "c_runtime_or_real_game_ui_evidence",
    }
    for row in report["rows"]:
        require(row["classification"] in allowed, f"classification differs: {row['resource']}:{row['coordinate']}")
        require(row["current_structure"]["terminator_present"], f"terminator absent: {row['resource']}:{row['coordinate']}")
        if row["classification"] == "a_static_high_confidence" and row["disposition"] != "static_policy_retain_current_ko":
            require(row["proposed_ko_without_shortening"], f"static proposal absent: {row['resource']}:{row['coordinate']}")
            require(not row["current_structure"]["runtime_02xx_opcodes"], f"static route has 02xx: {row['resource']}:{row['coordinate']}")
            require(not row["current_structure"]["complete_0143_commands"], f"static route has 0143: {row['resource']}:{row['coordinate']}")


def print_summary(report: Mapping[str, Any]) -> None:
    summary = report["summary"]
    print(f"unique hold rows: {summary['unique_hold_row_count']}")
    for name, count in summary["classification_counts"].items():
        print(f"  {name}: {count}")
    print(f"static text corrections ready: {summary['static_text_correction_ready_count']}")
    print(f"static policy retains: {summary['static_policy_retain_current_ko_count']}")
    print("read-only audit: true")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "validate", "summary"))
    args = parser.parse_args()
    report = build_report()
    validate(report)
    if args.command == "build":
        PUBLIC.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(canonical_json(report))
        print(f"wrote {OUTPUT.relative_to(REPO).as_posix()}")
    else:
        print("validation passed")
    print_summary(report)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from None
