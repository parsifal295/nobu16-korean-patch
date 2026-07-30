#!/usr/bin/env python3
"""Deterministically repair Base msggame runtime call assemblies.

The VM concatenates literal, selector, and call output UTF-16 units verbatim.
This pass owns the finite set discovered by the Ghidra-backed Cartesian audit
and preserves every record outside that pinned coordinate universe.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import struct
import sys
import unicodedata
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
QA_DIR = REPO / "workstreams" / "pc_dialogue_runtime_surface_qa_v1"
SURFACE_QA_PATH = QA_DIR / "audit_runtime_surface_v1.py"
CALL_QA_PATH = QA_DIR / "audit_call_assembly_boundaries_v1.py"
DEFAULT_SOURCE = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_remediation_v1"
    / "base"
    / "pre_call_assembly"
    / "MSG"
    / "JP"
    / "msggame.bin"
)
DEFAULT_OUTPUT = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_remediation_v1"
    / "base"
    / "call_assembly_candidate"
    / "MSG"
    / "JP"
    / "msggame.bin"
)
DEFAULT_REPORT = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_remediation_v1"
    / "base"
    / "base_call_assembly_remediation.private.v1.json"
)
DEFAULT_STRUCTURE_ALLOWLIST = (
    WORKSTREAM
    / "base_call_assembly_structure_allowlist.source_free.v1.json"
)
AUDIT_INPUT = DEFAULT_REPORT.parent / ".base-call-assembly.audit-input.bin"
SCHEMA = "nobu16.kr.base-call-assembly-remediation.v1"

# Pinned after the synthetic g3:p32/g4:p32 selector path was added.
EXPECTED_SOURCE_SHA256 = (
    "49963B81F810561A110E6F74F2B83BC1664AD47F6D96935F572945E28AB59AB7"
)
EXPECTED_ISSUE_COUNT = 3000
EXPECTED_COORDINATE_COUNT = 1371
EXPECTED_COORDINATE_SHA256 = (
    "6D64B6842EB0CDBF1BBDA3C0715ED15D989AD3386CE80B27D7D7224A3D0E4D7B"
)
EXPECTED_CATEGORY_COORDINATE_COUNTS = {
    "finite_call_output_followed_by_incompatible_hangul_fragment": 255,
    "incompatible_literal_stem_call_suffix": 665,
    "malformed_cartesian_rendered_string": 1304,
}


class BaseCallAssemblyRemediationError(ValueError):
    """Raised when the pinned call-remediation contract drifts."""


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise BaseCallAssemblyRemediationError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


SURFACE_QA = load_module("base_call_surface_qa_v1", SURFACE_QA_PATH)
CALL_QA = load_module("base_call_boundary_qa_v1", CALL_QA_PATH)

sys.path.insert(0, str(REPO / "workstreams" / "msggame"))
from msggame_format import (  # noqa: E402
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_packed_with_literals,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise BaseCallAssemblyRemediationError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def coordinate_digest(values: Iterable[tuple[int, int]]) -> str:
    payload = "\n".join(
        f"{block_id}:{record_id}"
        for block_id, record_id in sorted(values)
    ).encode("ascii")
    return sha256_bytes(payload)


def records_from_blob(blob: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    return {
        (record.block_id, record.record_id): record
        for block in parse_packed_msggame(blob).archive.blocks
        for record in block.records
    }


def audit_blob(
    blob: bytes,
    *,
    include_text: bool,
) -> Any:
    AUDIT_INPUT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_INPUT.write_bytes(blob)
    return CALL_QA.audit_resource(
        "base_msggame",
        AUDIT_INPUT,
        include_text=include_text,
    )


def literal_map(blob: bytes) -> dict[tuple[int, int, int], str]:
    return {
        (literal.block_id, literal.record_id, literal.literal_id): literal.text
        for block in parse_packed_msggame(blob).archive.blocks
        for record in block.records
        for literal in parse_record_literals(record)
    }


@dataclass(frozen=True)
class Retarget:
    coordinate: tuple[int, int]
    call_ordinal: int
    old_target: int
    new_target: int
    rule: str


QUESTION_PREFIXES = tuple(
    sorted(
        {
            "시겠습니까?",
            "겠습니까?",
            "습니까?",
            "입니까?",
            "어떻겠습니까?",
            "것입니까?",
            "는 것은 어떻습니까?",
            "인가……",
            "인가…",
            "인가?",
            "인가",
            "는가……",
            "는가…",
            "는가",
            "은가",
            "일까?",
            "가?",
            "까?",
            "까",
            "습니까",
        },
        key=len,
        reverse=True,
    )
)

CONNECTOR_PREFIXES: tuple[tuple[str, str], ...] = tuple(
    sorted(
        {
            "겠지만": ". 하지만",
            "이지만": ". 하지만",
            "하지만": ". 하지만",
            "그러하오니": ". 그러므로",
            "그러므로": ". 그러므로",
            "그러니": ". 그러니",
            "지만": ". 하지만",
            "으나": ". 그러나",
            "이나": ". 그러나",
            "나": ". 그러나",
            "으니": ". 그러므로",
            "기에": ". 그러므로",
            "어서": ". 그래서",
            "면": ". 그러면",
            "인데": ". 그런데",
            "만": ". 다만",
            "인 이상": ". 그런 이상",
            "인 듯합니다": ". 그런 듯합니다",
            "고 여깁니다": ". 그렇게 여깁니다",
            "라고\n여겨졌습니다": ". 그렇게\n여겨졌습니다",
            "도록 하십시오": ". 그렇게 하십시오",
            "도록 하라": ". 그렇게 하라",
            "지 못해서는": ". 그러지 못해서는",
            "것이니": ". 그러하니",
            "으리라": ". 그리 되리라",
            "다니": ". 그렇다니",
            "단 말인가": "? 그런 말인가",
        }.items(),
        key=lambda value: len(value[0]),
        reverse=True,
    )
)


def repair_following_literal(value: str) -> tuple[str, str]:
    """Turn a suffix fragment after a finite call into an independent clause."""

    leading_len = len(value) - len(value.lstrip())
    leading = value[:leading_len]
    body = value[leading_len:]
    if re.match(r"^다(?=[!?.…。]|$)", body):
        return leading + body[1:], "drop_duplicate_da"
    for prefix in QUESTION_PREFIXES:
        if body.startswith(prefix):
            tail = body[len(prefix):]
            if prefix == "인가" and tail.startswith(" 하고"):
                return leading + "?" + tail, "question_fragment_to_punctuation"
            return leading + "?" + tail, "question_fragment_to_punctuation"
    for prefix, replacement in CONNECTOR_PREFIXES:
        if body.startswith(prefix):
            return (
                leading + replacement + body[len(prefix):],
                "dependent_connector_to_independent_clause",
            )
    lexical_replacements = {
        "지역은": ". 그 지역은",
        "지역에서는": ". 그 지역에서는",
        "성을\n": ". 그 성을\n",
        "취임으로": ". 이번 취임으로",
        "가뭄입니다": ". 가뭄입니다",
        "그렇지": ". 그렇지",
        "군": ". 그렇군",
        "구나": ". 그렇구나",
        "겠소": ". 그리하겠소",
        "어요": ". 그렇군요",
        "시": ". 이때",
    }
    for prefix, replacement in sorted(
        lexical_replacements.items(),
        key=lambda value: len(value[0]),
        reverse=True,
    ):
        if body.startswith(prefix):
            return (
                leading + replacement + body[len(prefix):],
                "lexical_fragment_to_independent_clause",
            )
    return leading + ". " + body, "fallback_sentence_boundary"


def repair_empty_dependent_literal(
    value: str,
    *,
    target: int,
    only_empty: bool,
) -> str:
    leading_len = len(value) - len(value.lstrip())
    leading = value[:leading_len]
    body = value[leading_len:]
    if only_empty:
        carrier = "주군" if target == 1162 else "그대"
        replacements = {
            "에게는": f" {carrier}에게는",
            "에게": f" {carrier}에게",
            "보다": f" {carrier}보다",
            "만큼": f" {carrier}만큼",
            "방문": f" {carrier}의 방문",
            "곁": f" {carrier}의 곁",
            "뜻": f" {carrier}의 뜻",
            "힘": f" {carrier}의 힘",
            "의": f" {carrier}의",
            "에": f" {carrier}에게",
            "과": f" {carrier}과",
            "와": f" {carrier}과",
        }
    else:
        replacements = {
            "에게는": " 측에는",
            "에게": " 측에",
            "보다": " 쪽보다",
            "만큼": " 쪽만큼",
            "방문": " 측의 방문",
            "곁": " 주변",
            "뜻": " 측의 뜻",
            "힘": " 측의 힘",
            "의": " 측의",
            "에": " 측에",
            "과": " 측과",
            "와": " 측과",
        }
    for prefix, replacement in sorted(
        replacements.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if body.startswith(prefix):
            return leading + replacement + body[len(prefix):]
    raise BaseCallAssemblyRemediationError(
        f"unsupported empty-call dependent literal: {value!r}"
    )


def replace_tail(value: str, old: str, new: str) -> str:
    require(value.rstrip().endswith(old), f"tail {old!r} absent: {value!r}")
    trailing = value[len(value.rstrip()):]
    return value.rstrip()[: -len(old)] + new + trailing


def repair_reviewed_morph_text(value: str) -> str:
    """Repair the reviewed high-confidence morph pairs in one static span.

    This runs only on the 384-coordinate reviewed contract.  Grammar calls
    are first resolved to their canonical formal variant, so these rewrites
    preserve tense and intent without requiring Kiwi at build or release
    time.
    """

    replacements = (
        # Coda noun followed by an ending that requires a copular carrier.
        ("것군요", "것이군요"),
        ("것네", "것이네"),
        ("계절네", "계절이네"),
        ("금물다", "금물이다"),
        ("놈다", "놈이다"),
        ("동맹다", "동맹이다"),
        ("있는 듯군", "있는 듯하군"),
        ("마지막군요", "마지막이군요"),
        ("마지막네", "마지막이네"),
        ("모양다", "모양이다"),
        ("일사옵니다", "일이옵니다"),
        ("일습니다", "일입니다"),
        ("일다", "일이다"),
        # Two complete final endings were concatenated.
        ("입니다네요", "이네요"),
        ("입니다군", "이군"),
        ("입니다지요", "이지요"),
        ("사옵니다네요", "사옵니다"),
        ("사옵니다군", "사옵니다"),
        ("사옵니다지요", "사옵니다"),
        ("습니다네요", "네요"),
        ("습니다군", "군"),
        ("습니다지요", "지요"),
        ("옵니다지요", "옵지요"),
        ("겠다군", "겠군"),
        # Past-tense lexeme followed by a second full 하다 suffix.
        ("갖추했습니다", "갖추었습니다"),
        ("거두했습니다", "거두었습니다"),
        ("손에 넣했습니다", "손에 넣었습니다"),
        ("되했습니다", "되었습니다"),
        ("맡했습니다", "맡았습니다"),
        ("모으했습니다", "모았습니다"),
        ("인정받했습니다", "인정받았습니다"),
        ("받들했습니다", "받들었습니다"),
        ("함락시키했습니다", "함락시켰습니다"),
        ("알현시키했습니다", "알현시켰습니다"),
        ("줄어들했습니다", "줄어들었습니다"),
        ("해 오했습니다", "해 왔습니다"),
        ("출진해 오했습니다", "출진해 왔습니다"),
        # Present/future/propositive lexeme collisions.
        ("갖추하겠습니다", "갖추겠습니다"),
        ("끌어올리하겠습니다", "끌어올리겠습니다"),
        ("넓히하겠습니다", "넓히겠습니다"),
        ("도움이 되하겠습니다", "도움이 되겠습니다"),
        ("드리하겠습니다", "드리겠습니다"),
        ("떨치하겠습니다", "떨치겠습니다"),
        ("만들하겠습니다", "만들겠습니다"),
        ("받아들이하겠습니다", "받아들이겠습니다"),
        ("벌이하겠습니다", "벌이겠습니다"),
        ("보이하겠습니다", "보이겠습니다"),
        ("보하겠습니다", "보겠습니다"),
        ("삼하겠습니다", "삼겠습니다"),
        ("손보하겠습니다", "손보겠습니다"),
        ("시키하겠습니다", "시키겠습니다"),
        ("올리하겠습니다", "올리겠습니다"),
        ("불리하겠습니다", "불리겠습니다"),
        ("갖추합니다", "갖춥니다"),
        ("그지없합니다", "그지없습니다"),
        ("근질거리합니다", "근질거립니다"),
        ("돌아오합니다", "돌아옵니다"),
        ("되합니다", "됩니다"),
        ("보여 드리합니다", "보여 드립니다"),
        ("드리합니다", "드립니다"),
        ("만들합니다", "만듭니다"),
        ("받들합니다", "받듭니다"),
        ("받아들이합니다", "받아들입니다"),
        ("벌이합니다", "벌입니다"),
        ("보이합니다", "보입니다"),
        ("보합니다", "봅니다"),
        ("불리합니다", "불립니다"),
        ("빌합니다", "빕니다"),
        ("섬기합니다", "섬깁니다"),
        ("손보합니다", "손봅니다"),
        ("철수시키합니다", "철수시킵니다"),
        ("시키합니다", "시킵니다"),
        ("없합니다", "없습니다"),
        ("올리합니다", "올립니다"),
        ("잃합니다", "잃습니다"),
        ("느껴지합니다", "느껴집니다"),
        ("생기습니다", "생겼습니다"),
        ("사습니다", "샀습니다"),
        ("드리합시다", "드립시다"),
        ("열매를 맺합시다", "열매를 맺읍시다"),
        ("실행에 옮기합시다", "실행에 옮깁시다"),
        ("춤이라도 추합시다", "춤이라도 춥시다"),
        ("승기를 잡겠합시다", "승기를 잡읍시다"),
        ("착수하겠합시다", "착수합시다"),
        # Negation and auxiliary boundaries.
        ("거절당하버렸습니다", "거절당해 버렸습니다"),
        ("돌아보좋겠지요", "돌아보는 게 좋겠지요"),
        ("모르하지 않습니다", "모르지 않습니다"),
        ("해 드리하지 않습니다", "해 드리지 않습니다"),
        ("않하지 않습니다", "않습니다"),
        ("않이겠지요", "않겠지요"),
        ("있하지 않습니다", "있지 않습니다"),
        ("좋하지 않습니다", "좋지 않습니다"),
        ("부족하하지 않습니다", "부족하지 않습니다"),
        ("활용하하지 않으면", "활용하지 않으면"),
        ("보필하해 주", "보필해 주"),
        ("같지 않없습니다", "같지 않습니다"),
        ("채택되하지 않는다다니", "채택되지 않았다니"),
        ("있하지 않았습니다", "있지 않았습니다"),
        # Other reviewed predicate allomorphs.
        ("느끼하옵니다", "느낍니다"),
        ("돌아오한다", "돌아온다"),
        ("되했다", "되었다"),
        ("그지없한다", "그지없다"),
        ("느끼한다", "느낀다"),
        ("드리한다", "드린다"),
        ("벌이한다", "벌인다"),
        ("빌한다", "빈다"),
        ("섬기한다", "섬긴다"),
        ("시키한다", "시킨다"),
        ("오한다", "온다"),
        ("잃한다", "잃는다"),
        ("듯하이군", "듯하군"),
        # Prefinal ending followed by another predicate/copula.
        ("겠보여하겠습니다", "여 드리겠습니다"),
        ("겠하겠습니다", "겠습니다"),
        ("알겠사했습니다", "알겠습니다"),
        ("겠입니까", "겠습니까"),
        ("겠이겠지요", "겠지요"),
        ("곤궁해졌이겠지요", "곤궁해졌겠지요"),
        ("머지않았이지요", "머지않았지요"),
        ("맞았사했습니다", "맞았사옵니다"),
        ("끝났입니다", "끝났습니다"),
        ("왔이지요", "왔지요"),
        ("찾아왔입니다", "찾아왔습니다"),
        ("세웠했습니다", "세웠습니다"),
        ("찾아냈했습니다", "찾아냈습니다"),
        ("넓어졌했습니다", "넓어졌습니다"),
        ("들었합니다", "들었습니다"),
        ("했했습니다", "했습니다"),
        ("했했다", "했다"),
        ("왔했습니다", "왔습니다"),
        ("왔했다", "왔다"),
        ("섰했습니다", "섰습니다"),
        ("알겠사옵했습니다", "알겠사옵니다"),
    )
    repaired = value
    for old, new in replacements:
        repaired = repaired.replace(old, new)
    repaired = re.sub(r"수없(?=(?:습니다|다|사옵니다|소))", "수 없", repaired)
    repaired = re.sub(
        r"고생각(?=(?:합니다|한다|하옵니다|하오))",
        "고 생각",
        repaired,
    )
    for noun in (
        "기분",
        "바",
        "뜻",
        "의미",
        "모양",
        "상태",
        "상황",
        "각오",
        "영광",
        "농담",
        "듯",
    ):
        repaired = repaired.replace(noun + "이합니다", noun + "입니다")
        repaired = repaired.replace(noun + "이한다", noun + "이다")
        repaired = repaired.replace(noun + "이하옵니다", noun + "이옵니다")
        repaired = repaired.replace(noun + "이하오", noun + "이오")
    for stem in ("인정받", "보답받", "대접받", "보호받"):
        repaired = repaired.replace(stem + "합니다", stem + "습니다")
        repaired = repaired.replace(stem + "한다", stem + "는다")
        repaired = repaired.replace(stem + "하옵니다", stem + "사옵니다")
        repaired = repaired.replace(stem + "하오", stem + "소")
    for stem in (
        "이루어 내",
        "보여 드리",
        "이어 보이",
        "만들어 보이",
        "갖추",
        "손보",
        "불리",
        "느껴지",
        "되어 있",
        "되어지",
    ):
        repaired = repaired.replace(stem + "하겠", stem + "겠")
    repaired = repaired.replace("일컬어져하겠", "일컬어지겠")
    repaired = repaired.replace("듯하생각합니다", "듯합니다")
    repaired = repaired.replace("듯하생각한다", "듯하다")
    repaired = repaired.replace("듯하생각하옵니다", "듯하옵니다")
    repaired = repaired.replace("듯하생각하오", "듯하오")
    for noun in (
        "농담",
        "영광",
        "금물",
        "동맹",
        "상황",
        "모양",
        "놈",
        "것",
        "계절",
        "마지막",
        "일",
        "명령",
        "소승",
        "도련님",
        "네놈",
        "군",
        "말",
        "중단",
        "발생",
        "요청",
        "제압",
        "달성",
        "향",
        "청",
        "전법",
    ):
        repaired = re.sub(
            re.escape(noun) + r"다(?![가-힣])",
            noun + "이다",
            repaired,
        )
        repaired = re.sub(
            re.escape(noun) + r"습니다(?![가-힣])",
            noun + "입니다",
            repaired,
        )
        repaired = re.sub(
            re.escape(noun) + r"사옵니다(?![가-힣])",
            noun + "이옵니다",
            repaired,
        )
        repaired = re.sub(
            re.escape(noun) + r"네(?![가-힣])",
            noun + "이네",
            repaired,
        )
        repaired = re.sub(
            re.escape(noun) + r"군요(?![가-힣])",
            noun + "이군요",
            repaired,
        )
        repaired = re.sub(
            re.escape(noun) + r"군(?![가-힣])",
            noun + "이군",
            repaired,
        )
        repaired = re.sub(
            re.escape(noun) + r"여(?![가-힣])",
            noun + "이여",
            repaired,
        )
    repaired = re.sub(r"듯입니다(?![가-힣])", "듯합니다", repaired)
    repaired = re.sub(r"듯다(?![가-힣])", "듯하다", repaired)
    repaired = re.sub(r"듯이오(?![가-힣])", "듯하오", repaired)
    repaired = repaired.replace("일컬어져습니다", "일컬어집니다")
    repaired = repaired.replace("일컬어져다", "일컬어진다")
    repaired = repaired.replace("일컬어져사옵니다", "일컬어지옵니다")
    repaired = repaired.replace("괜찮은가일까요", "괜찮을까요")
    repaired = re.sub(
        r"성(?=(?:공략|침공|방어|구원))",
        "성 ",
        repaired,
    )
    repaired = repaired.replace("조예가다면", "조예가 있다면")
    repaired = repaired.replace("않없", "않")
    repaired = repaired.replace("없못하", "하지 못하")
    repaired = repaired.replace("않못하", "못하")
    repaired = repaired.replace("뻔였", "뻔했")
    repaired = repaired.replace("서둘러지 않", "서두르지 않")
    repaired = repaired.replace("은상의검토", "은상의 검토")
    repaired = repaired.replace("발생하여했습니다", "발생했습니다")
    repaired = repaired.replace("발생하여했다", "발생했다")
    repaired = repaired.replace("붙잡아했습니다", "붙잡았습니다")
    repaired = repaired.replace("붙잡아했다", "붙잡았다")
    repaired = repaired.replace("정리되어했습니다", "정리되었습니다")
    repaired = repaired.replace("정리되어했다", "정리되었다")
    repaired = repaired.replace("완성되어했습니다", "완성되었습니다")
    repaired = repaired.replace("완성되어했다", "완성되었다")
    repaired = repaired.replace("뻔했소였습니다", "뻔했습니다")
    repaired = repaired.replace("뻔했소였다", "뻔했다")
    repaired = repaired.replace("뻔했다였습니다", "뻔했습니다")
    repaired = repaired.replace("뻔했다였다", "뻔했다")
    repaired = repaired.replace("뻔했습니다였습니다", "뻔했습니다")
    repaired = repaired.replace("뻔했습니다이었다", "뻔했습니다")
    repaired = repaired.replace(
        "고자 하옵니다생각합니다",
        "고자 합니다",
    )
    repaired = repaired.replace(
        "고자 하옵니다생각한다",
        "고자 한다",
    )
    repaired = repaired.replace(
        "듯하옵니다생각합니다",
        "듯합니다",
    )
    repaired = repaired.replace(
        "듯하옵니다생각한다",
        "듯하다",
    )
    repaired = repaired.replace("가문로부터", "가문으로부터")
    repaired = repaired.replace("가문로 향해", "가문을 향해")
    repaired = repaired.replace("가문로", "가문으로")
    repaired = repaired.replace("어떻이겠", "어떻겠")
    repaired = repaired.replace("군의를 열판단", "군의를 열어 판단")
    repaired = re.sub(r"것다(?![가-힣])", "것이다", repaired)
    repaired = repaired.replace("모양이군입니다", "모양입니다")
    repaired = repaired.replace("의지하여주시오", "의지하여 주시오")
    repaired = repaired.replace("새로이군단", "새로이 군단")
    repaired = repaired.replace("신용을 얻어했다", "신용을 얻었다")
    repaired = repaired.replace("신용을 얻어했습니다", "신용을 얻었습니다")
    repaired = repaired.replace("에게맡겨", "에게 맡겨")
    repaired = repaired.replace("에게명해", "에게 명해")
    repaired = repaired.replace(
        "얻어 가고 싶은 것입니다. 그렇군",
        "얻어 가고 싶구려",
    )
    repaired = repaired.replace("연연해지 않", "연연하지 않")
    repaired = repaired.replace("갖춰습니다", "갖추었습니다")
    repaired = repaired.replace("나서합시다", "나섭시다")
    repaired = repaired.replace("많으셨습니다였습니다", "많으셨습니다")
    repaired = repaired.replace("많으셨습니다였다", "많으셨습니다")
    repaired = repaired.replace("수고하였소였습니다", "수고하셨습니다")
    repaired = repaired.replace("반드시기대", "반드시 기대")
    repaired = repaired.replace("힘으로합니다", "힘으로 다스리겠습니다")
    repaired = repaired.replace("보이 하겠습니다", "보이겠습니다")
    repaired = repaired.replace("보이 하겠다", "보이겠다")
    repaired = repaired.replace("보이 하겠소", "보이겠소")
    repaired = repaired.replace("보이 하겠사옵니다", "보이겠사옵니다")
    repaired = repaired.replace("바라습니다", "바랍니다")
    repaired = repaired.replace("바라는다", "바란다")
    repaired = repaired.replace("바라사옵니다", "바라옵니다")
    repaired = repaired.replace("오합니다", "오겠습니다")
    repaired = repaired.replace("생각해지 않", "생각하지 않")
    repaired = re.sub(
        r"(?<=의)(?=(?:기대|무운|은혜|하명))",
        " ",
        repaired,
    )
    repaired = repaired.replace("일에입니다", "일입니다")
    repaired = repaired.replace("일에있소", "일이오")
    repaired = repaired.replace("일에있다", "일이다")
    repaired = repaired.replace("일이입니다", "일입니다")
    repaired = repaired.replace("일이있소", "일이오")
    repaired = repaired.replace("일이있다", "일이다")
    return repaired


def add_retarget(
    values: list[Retarget],
    *,
    coordinate: tuple[int, int],
    call_ordinal: int,
    old_target: int,
    new_target: int,
    rule: str,
) -> None:
    if old_target == new_target:
        return
    candidate = Retarget(
        coordinate,
        call_ordinal,
        old_target,
        new_target,
        rule,
    )
    existing = [
        value
        for value in values
        if value.coordinate == coordinate
        and value.call_ordinal == call_ordinal
    ]
    require(
        not existing or existing == [candidate],
        f"conflicting retarget at {coordinate} call {call_ordinal}: "
        f"{existing} versus {candidate}",
    )
    if not existing:
        values.append(candidate)


def retarget_for_get(old_target: int) -> int:
    if old_target in {532, 616, 1078}:
        return 83
    return 82


def build_plan(
    source_blob: bytes,
) -> tuple[
    dict[tuple[int, int, int], str],
    tuple[Retarget, ...],
    dict[str, Any],
]:
    source_records = records_from_blob(source_blob)
    # The reviewed morph-pair contract was discovered against the
    # post-call-remediation candidate.  Keep the historical 3,000-issue
    # baseline as a distinct phase, then enforce morph findings against the
    # provisional/final candidate below.
    initial_with_morph = audit_blob(source_blob, include_text=True)
    initial = replace(
        initial_with_morph,
        issues=tuple(
            issue
            for issue in initial_with_morph.issues
            if issue.category not in {
                "rendered_morph_pair_high_confidence_collision",
                "post_canonical_high_confidence_collision",
            }
        ),
    )
    coordinates = {
        (issue.block_id, issue.record_id)
        for issue in initial.issues
    }
    category_counts = {
        category: len(
            {
                (issue.block_id, issue.record_id)
                for issue in initial.issues
                if issue.category == category
            }
        )
        for category in sorted({issue.category for issue in initial.issues})
    }
    require(
        sha256_bytes(source_blob) == EXPECTED_SOURCE_SHA256,
        f"source hash drifted: {sha256_bytes(source_blob)}",
    )
    require(
        len(initial.issues) == EXPECTED_ISSUE_COUNT,
        f"source issue count drifted: {len(initial.issues)}",
    )
    require(
        len(coordinates) == EXPECTED_COORDINATE_COUNT,
        f"source coordinate count drifted: {len(coordinates)}",
    )
    require(
        coordinate_digest(coordinates) == EXPECTED_COORDINATE_SHA256,
        f"source coordinate digest drifted: {coordinate_digest(coordinates)}",
    )
    require(
        category_counts == EXPECTED_CATEGORY_COORDINATE_COUNTS,
        f"source category-coordinate counts drifted: {category_counts}",
    )

    renderer = CALL_QA.SyntheticSelectorRenderer(source_records)
    source_literals = literal_map(source_blob)
    replacements = dict(source_literals)
    changed: set[tuple[int, int, int]] = set()
    methods: dict[tuple[int, int, int], set[str]] = {}
    retargets: list[Retarget] = []

    def set_literal(
        coordinate: tuple[int, int],
        literal_id: int,
        value: str,
        method: str,
    ) -> None:
        key = (coordinate[0], coordinate[1], literal_id)
        if replacements[key] != value:
            replacements[key] = value
            changed.add(key)
            methods.setdefault(key, set()).add(method)

    request_questions = {
        (6, 3759): ("동의해 주시", "동의하시겠습니까"),
        (6, 3761): ("약속해 주시", "약속하시겠습니까"),
        (6, 3762): ("찬동해 주시", "찬동하시겠습니까"),
        (6, 3843): ("창을 거두어 주시", "전쟁을 멈추시겠습니까"),
        (15, 1428): ("사관을 허락해 주시", "사관을 허락하시겠습니까"),
    }

    for coordinate in sorted(coordinates):
        record = source_records[coordinate]
        components = SURFACE_QA.tolerant_decode_record(record)
        call_ordinal = -1
        for component_index, component in enumerate(components):
            if component["kind"] != "call":
                continue
            call_ordinal += 1
            target = int(component["target"][1])
            variants = tuple(dict.fromkeys(renderer.render((0, target))))
            previous = CALL_QA.adjacent_literal(
                components,
                [replacements[(coordinate[0], coordinate[1], literal.literal_id)]
                 for literal in parse_record_literals(record)],
                component_index,
                direction=-1,
            )
            following = CALL_QA.adjacent_literal(
                components,
                [replacements[(coordinate[0], coordinate[1], literal.literal_id)]
                 for literal in parse_record_literals(record)],
                component_index,
                direction=1,
            )
            previous_id = previous[0] if previous is not None else None
            previous_text = (
                replacements[(coordinate[0], coordinate[1], previous_id)]
                if previous_id is not None
                else None
            )
            following_id = following[0] if following is not None else None
            following_text = (
                replacements[(coordinate[0], coordinate[1], following_id)]
                if following_id is not None
                else None
            )

            if target == 8 and following_id is not None:
                if following_text is not None and following_text.startswith("님"):
                    set_literal(
                        coordinate,
                        following_id,
                        following_text[1:],
                        "call8_includes_honorific",
                    )
                    following_text = replacements[
                        (coordinate[0], coordinate[1], following_id)
                    ]

            rules = {
                rule
                for variant in variants
                for rule in (
                    CALL_QA.local_stem_rules(previous_text or "", variant)
                    if previous_text is not None
                    else ()
                )
            }
            if previous_id is not None and previous_text is not None:
                value = previous_text
                if "trailing_ha_before_full_ha" in rules:
                    value = replace_tail(value, "하", "")
                if "trailing_ha_before_bare_formal" in rules:
                    value = replace_tail(value, "하", "")
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=1084,
                        rule="bare_formal_to_full_ha",
                    )
                if "trailing_get_before_full_ha" in rules:
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=retarget_for_get(target),
                        rule="full_ha_to_bare_after_get",
                    )
                if "absent_stem_before_full_absent" in rules:
                    value = replace_tail(value, "없", "")
                if "accept_before_receive" in rules:
                    value = replace_tail(value, "받아들이", "")
                if "mosi_stem_before_full_ha" in rules:
                    value = replace_tail(value, "모시", "충성")
                if "exist_stem_before_copula" in rules:
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=70,
                        rule="copula_to_bare_after_exist",
                    )
                if "become_stem_before_bare_formal" in rules:
                    value = replace_tail(
                        value,
                        "방비가 강화되",
                        "방비 강화가 완료되었",
                    )
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=83,
                        rule="become_allomorph_to_past_bare",
                    )
                if "negative_stem_before_copula" in rules:
                    value = replace_tail(
                        value,
                        "나쁘지 않",
                        "나쁘지 않은 일",
                    )
                if "causative_stem_before_negative_ha" in rules:
                    if value.rstrip().endswith("지켜 내"):
                        value = replace_tail(value, "지켜 내", "수호")
                    elif value.rstrip().endswith("함락시키"):
                        value = replace_tail(value, "함락시키", "공략")
                    else:
                        raise BaseCallAssemblyRemediationError(
                            f"unknown causative stem at {coordinate}: {value!r}"
                        )
                if "give_stem_before_full_give" in rules:
                    value = replace_tail(value, "주", "")
                if "missing_space_before_full_absent" in rules:
                    value = value + " "
                if "missing_exist_stem_before_bare_formal" in rules:
                    value = value + " 있"
                if "negative_stem_before_past_ha" in rules:
                    value = replace_tail(value, "않", "않았")
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=178,
                        rule="past_ha_to_bare_after_negative",
                    )
                if "past_stem_before_past_ha" in rules:
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=178,
                        rule="past_ha_to_bare_after_past_stem",
                    )
                if "exist_stem_before_past_ha" in rules:
                    value = replace_tail(value, "있", "있었")
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=178,
                        rule="past_ha_to_bare_after_exist_stem",
                    )
                if "exist_stem_before_full_ha" in rules:
                    future_variant = any(
                        CALL_QA.normalize_visible(value).lstrip().startswith(
                            "하겠"
                        )
                        for value in variants
                    )
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=1114 if future_variant else 178,
                        rule="full_ha_to_bare_after_exist",
                    )
                if "benefit_subject_before_past_ha" in rules:
                    value = replace_tail(value, "도움이", "도움이 되었")
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=178,
                        rule="past_ha_to_bare_after_benefit",
                    )
                if "action_stem_before_full_future_ha" in rules:
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=1114,
                        rule="full_future_ha_to_bare_after_action_stem",
                    )
                if "decision_stem_before_full_propositive" in rules:
                    value = replace_tail(value, "내리", "발령")
                if "question_topic_missing_space" in rules:
                    value = value + " "
                    for next_index in range(
                        component_index + 1,
                        len(components),
                    ):
                        next_component = components[next_index]
                        next_kind = str(next_component["kind"])
                        if next_kind in CALL_QA.NON_EMITTING_COMPONENTS:
                            continue
                        require(
                            next_kind == "call",
                            "question terminal is not followed by a call at "
                            f"{coordinate}",
                        )
                        next_target = int(next_component["target"][1])
                        require(
                            next_target in {292, 598},
                            "unexpected question terminal target at "
                            f"{coordinate}: {next_target}",
                        )
                        next_call_ordinal = sum(
                            1
                            for prior in components[: next_index + 1]
                            if prior["kind"] == "call"
                        ) - 1
                        add_retarget(
                            retargets,
                            coordinate=coordinate,
                            call_ordinal=next_call_ordinal,
                            old_target=next_target,
                            new_target=1193,
                            rule="duplicate_question_terminal_removed",
                        )
                        break
                if "persona_relative_clause_missing_space" in rules:
                    value = value + " "
                if "object_phrase_missing_space" in rules:
                    value = value + " "
                if "command_auxiliary_missing_space" in rules:
                    value = value + " "
                if "ha_before_give_command" in rules:
                    value = replace_tail(value, "하", "해 ")
                if "big_problem_copula_allomorph" in rules:
                    value = replace_tail(value, "큰일이", "큰일입니다")
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=1193,
                        rule="big_problem_fixed_terminal",
                    )
                if "finite_literal_before_duplicate_da" in rules:
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=1193,
                        rule="duplicate_da_terminal_removed",
                    )
                if "negative_ha_collision" in rules:
                    value = replace_tail(value, "못하", "못")
                if "absent_stem_before_negative_ha" in rules:
                    value = replace_tail(value, "없", "")
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=730,
                        rule="negative_ha_to_absent_after_absent_stem",
                    )
                if "negative_stem_before_negative_ha" in rules:
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=178,
                        rule="negative_ha_to_bare_after_negative_stem",
                    )
                if "give_past_collision" in rules:
                    value = replace_tail(value, "입혀 주", "입혀 주었")
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=178,
                        rule="past_ha_to_bare_after_give",
                    )
                if "hae_before_full_propositive" in rules:
                    value = replace_tail(value, "매진해", "매진")
                if "himsseu_before_full_ha" in rules:
                    value = replace_tail(value, "힘쓰", "노력")
                if coordinate in request_questions and (
                    "request_stem_before_full_ha" in rules
                ):
                    old, new = request_questions[coordinate]
                    value = replace_tail(value, old, new)
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=call_ordinal,
                        old_target=target,
                        new_target=1193,
                        rule="request_question_fixed_literal",
                    )
                if (
                    value.rstrip().endswith(("을", "를"))
                    and any(
                        re.match(
                            r"^하(?:겠습니다|겠다|자|합니다|한다|하옵니다)",
                            CALL_QA.normalize_visible(variant).lstrip(),
                        )
                        for variant in variants
                    )
                ):
                    value = value + " "
                set_literal(
                    coordinate,
                    previous_id,
                    value,
                    "+".join(sorted(rules)) or "object_particle_spacing",
                )
                previous_text = value

            if following_id is not None and following_text is not None:
                if any(
                    CALL_QA.next_literal_rules(variant, following_text)
                    for variant in variants
                ):
                    repaired, method = repair_following_literal(following_text)
                    set_literal(coordinate, following_id, repaired, method)
                    following_text = repaired
                if CALL_QA.empty_dynamic_call_rules(
                    components,
                    component_index,
                    (0, target),
                    variants,
                    previous_text,
                    following_text,
                ):
                    repaired = repair_empty_dependent_literal(
                        following_text,
                        target=target,
                        only_empty=variants == ("",),
                    )
                    set_literal(
                        coordinate,
                        following_id,
                        repaired,
                        "empty_call_dependent_carrier",
                    )

    issue_coordinates_by_rule = {
        rule: {
            (issue.block_id, issue.record_id)
            for issue in initial.issues
            if issue.rule == rule
        }
        for rule in {issue.rule for issue in initial.issues}
    }

    def retarget_matching_calls(
        coordinate: tuple[int, int],
        targets: frozenset[int],
        rule: str,
    ) -> None:
        ordinal = -1
        for component in SURFACE_QA.tolerant_decode_record(
            source_records[coordinate]
        ):
            if component["kind"] != "call":
                continue
            ordinal += 1
            target = int(component["target"][1])
            if target not in targets:
                continue
            if any(
                value.coordinate == coordinate
                and value.call_ordinal == ordinal
                for value in retargets
            ):
                continue
            add_retarget(
                retargets,
                coordinate=coordinate,
                call_ordinal=ordinal,
                old_target=target,
                new_target=1193,
                rule=rule,
            )

    for coordinate in sorted(
        issue_coordinates_by_rule.get(
            "rendered_double_da_terminal",
            set(),
        )
    ):
        retarget_matching_calls(
            coordinate,
            frozenset({502, 508}),
            "duplicate_da_or_connective_terminal_removed",
        )

    for coordinate in sorted(
        issue_coordinates_by_rule.get(
            "rendered_double_yo_terminal",
            set(),
        )
    ):
        retarget_matching_calls(
            coordinate,
            frozenset({718}),
            "duplicate_yo_terminal_removed",
        )

    question_double_coordinates = issue_coordinates_by_rule.get(
        "rendered_question_predicate_double_terminal",
        set(),
    )
    for coordinate in sorted(question_double_coordinates):
        record = source_records[coordinate]
        components = SURFACE_QA.tolerant_decode_record(record)
        literal_values = [
            replacements[
                (coordinate[0], coordinate[1], literal.literal_id)
            ]
            for literal in parse_record_literals(record)
        ]
        for component_index, component in enumerate(components):
            if (
                component["kind"] != "call"
                or int(component["target"][1]) != 688
            ):
                continue
            previous = CALL_QA.adjacent_literal(
                components,
                literal_values,
                component_index,
                direction=-1,
            )
            if previous is not None:
                previous_id, previous_text = previous
                value = replacements[
                    (coordinate[0], coordinate[1], previous_id)
                ]
                if value.rstrip().endswith("어떠할지"):
                    value = replace_tail(value, "어떠할지", "")
                elif value.rstrip().endswith("어떻"):
                    value = replace_tail(value, "어떻", "")
                if value and not (
                    value[-1].isspace()
                    or unicodedata.category(value[-1]).startswith("C")
                ):
                    value += " "
                set_literal(
                    coordinate,
                    previous_id,
                    value,
                    "question_predicate_carrier",
                )
                literal_values[previous_id] = value
            for next_index in range(component_index + 1, len(components)):
                next_component = components[next_index]
                next_kind = str(next_component["kind"])
                if next_kind in CALL_QA.NON_EMITTING_COMPONENTS:
                    continue
                require(
                    next_kind == "call",
                    "question call is not followed by a terminal call at "
                    f"{coordinate}",
                )
                next_target = int(next_component["target"][1])
                require(
                    next_target in {292, 598, 604},
                    "unexpected duplicate question target at "
                    f"{coordinate}: {next_target}",
                )
                next_ordinal = sum(
                    1
                    for prior in components[: next_index + 1]
                    if prior["kind"] == "call"
                ) - 1
                if not any(
                    value.coordinate == coordinate
                    and value.call_ordinal == next_ordinal
                    for value in retargets
                ):
                    add_retarget(
                        retargets,
                        coordinate=coordinate,
                        call_ordinal=next_ordinal,
                        old_target=next_target,
                        new_target=1193,
                        rule="duplicate_question_terminal_removed",
                    )
                break

    lexical_repairs = {
        "제힘": "제 힘",
        "군사적협력": "군사적 협력",
        "등의협력": "등의 협력",
        "성등": "성 등",
    }
    lexical_rules = {
        "rendered_missing_space_je_him",
        "rendered_missing_space_deung_hyeopryeok",
        "rendered_missing_space_military_hyeopryeok",
        "rendered_missing_space_seong_deung",
    }
    lexical_coordinates = set().union(
        *(
            issue_coordinates_by_rule.get(rule, set())
            for rule in lexical_rules
        )
    )
    for coordinate in sorted(lexical_coordinates):
        for literal in parse_record_literals(source_records[coordinate]):
            key = (coordinate[0], coordinate[1], literal.literal_id)
            value = replacements[key]
            repaired = value
            for old, new in lexical_repairs.items():
                repaired = repaired.replace(old, new)
            set_literal(
                coordinate,
                literal.literal_id,
                repaired,
                "lexical_spacing",
            )

    # A comma is always followed by a visible space in Korean prose.  Scope
    # the mechanical rewrite to coordinates proven by the full Cartesian
    # renderer so unrelated literal bytes remain untouched.
    for coordinate in sorted(
        issue_coordinates_by_rule.get(
            "rendered_comma_missing_space",
            set(),
        )
    ):
        for literal in parse_record_literals(source_records[coordinate]):
            key = (coordinate[0], coordinate[1], literal.literal_id)
            set_literal(
                coordinate,
                literal.literal_id,
                re.sub(r"([,，])(?=[가-힣])", r"\1 ", replacements[key]),
                "rendered_comma_spacing",
            )

    # Cross-component lexical spacing and screenshot regressions.
    set_literal((8, 1020), 0, "하아… 설마, ", "screenshot_regression")
    set_literal(
        (8, 1020),
        1,
        "에게도 병환이 들다니…\n…당분간은 제 힘을 발휘",
        "screenshot_regression",
    )
    set_literal((6, 3761), 1, "에게 원군이나 중재 등\n군사적 ", "lexical_spacing")
    set_literal((6, 3951), 2, " 등의 ", "lexical_spacing")
    for coordinate in ((6, 3952), (6, 3953)):
        set_literal(coordinate, 1, " 등의 ", "lexical_spacing")
    for coordinate in ((6, 4015), (6, 4016), (6, 4017)):
        set_literal(coordinate, 0, " 공략", "lexical_spacing")
    for coordinate, literal_id in (
        ((15, 2233), 1),
        ((15, 2234), 1),
        ((15, 2235), 2),
    ):
        set_literal(
            coordinate,
            literal_id,
            replacements[(coordinate[0], coordinate[1], literal_id)].replace(
                "등",
                " 등",
                1,
            ),
            "lexical_spacing",
        )

    # Bare suffixes after a noun or subject particle need either a fixed
    # copular sentence or an explicit existential stem.
    set_literal((8, 264), 0, "올해는 흉작이었으나, 이를 면한\n지역입니다", "fixed_copula")
    retarget_matching_calls((8, 264), frozenset({70}), "fixed_copula")
    set_literal((8, 266), 0, "올해에는 흉작입니다", "fixed_copula")
    set_literal(
        (8, 266),
        1,
        ",\n유비무환의 덕으로\n피해를 면한 지역입니다",
        "fixed_copula",
    )
    retarget_matching_calls((8, 266), frozenset({70}), "fixed_copula")
    set_literal(
        (8, 343),
        1,
        "의 영내에서도\n거세게 몰아쳐,\n큰 피해를 입은 군입니다",
        "fixed_copula",
    )
    retarget_matching_calls((8, 343), frozenset({82}), "fixed_copula")
    for coordinate, literal_id in (
        ((6, 4383), 3),
        ((8, 267), 1),
        ((15, 918), 3),
        ((15, 1464), 0),
        ((15, 1676), 2),
        ((15, 2285), 0),
        ((15, 2286), 0),
        ((15, 2389), 1),
    ):
        key = (coordinate[0], coordinate[1], literal_id)
        value = replacements[key]
        if not value.rstrip().endswith("있"):
            value += " 있"
        set_literal(
            coordinate,
            literal_id,
            value,
            "explicit_existential_stem",
        )

    set_literal(
        (6, 4148),
        0,
        "적의 성을 공략하기에는\n전선의 병력만으로는 부족하다\n더 많은 병력이 필요합니다",
        "fixed_terminal",
    )
    retarget_matching_calls((6, 4148), frozenset({556}), "fixed_terminal")
    for coordinate, literal_id, target in (
        ((6, 4442), 1, 556),
        ((6, 4444), 1, 556),
        ((6, 4458), 2, 538),
        ((6, 4468), 2, 556),
    ):
        key = (coordinate[0], coordinate[1], literal_id)
        value = replacements[key]
        value = replace_tail(value, "듯하", "듯합니다")
        set_literal(
            coordinate,
            literal_id,
            value,
            "fixed_predicative_terminal",
        )
        retarget_matching_calls(
            coordinate,
            frozenset({target}),
            "fixed_predicative_terminal",
        )
    for coordinate, literal_id, target in (
        ((6, 2169), 0, 538),
        ((6, 3668), 1, 586),
        ((6, 3852), 2, 550),
    ):
        key = (coordinate[0], coordinate[1], literal_id)
        value = replacements[key]
        value = replace_tail(value, "듯하", "듯합니다")
        set_literal(
            coordinate,
            literal_id,
            value,
            "fixed_predicative_terminal",
        )
        retarget_matching_calls(
            coordinate,
            frozenset({target}),
            "fixed_predicative_terminal",
        )
    set_literal(
        (6, 4383),
        2,
        "도 꼭 짓고 싶습니다",
        "fixed_predicative_terminal",
    )
    retarget_matching_calls(
        (6, 4383),
        frozenset({538}),
        "fixed_predicative_terminal",
    )

    for coordinate, literal_id in (
        ((2, 247), 0),
        ((6, 4010), 0),
        ((6, 4384), 1),
        ((8, 318), 1),
        ((8, 320), 0),
        ((13, 112), 1),
        ((15, 1190), 0),
        ((15, 1486), 1),
        ((15, 1647), 0),
        ((15, 2181), 0),
        ((15, 2263), 1),
        ((15, 2277), 0),
        ((15, 2278), 0),
        ((15, 2279), 0),
        ((15, 2280), 0),
        ((15, 2281), 0),
        ((15, 2282), 0),
        ((15, 2283), 0),
    ):
        key = (coordinate[0], coordinate[1], literal_id)
        value = replacements[key]
        if not value.rstrip().endswith("있"):
            value += " 있"
        set_literal(
            coordinate,
            literal_id,
            value,
            "explicit_existential_stem",
        )
    for coordinate, literal_id, target, old, new in (
        ((7, 2447), 0, 82, "방면이", "방면입니다"),
        ((8, 265), 0, 70, "지역이", "지역입니다"),
        ((8, 342), 0, 82, "군이", "군입니다"),
        ((15, 314), 0, 178, "낭인이", "낭인입니다"),
        ((15, 896), 0, 82, "계책이", "계책입니다"),
    ):
        key = (coordinate[0], coordinate[1], literal_id)
        set_literal(
            coordinate,
            literal_id,
            replace_tail(replacements[key], old, new),
            "fixed_copula",
        )
        retarget_matching_calls(
            coordinate,
            frozenset({target}),
            "fixed_copula",
        )
    set_literal(
        (15, 1486),
        0,
        replace_tail(
            replacements[(15, 1486, 0)],
            "불안해져",
            "불안해졌",
        ),
        "past_allomorph",
    )
    set_literal(
        (15, 921),
        0,
        replace_tail(
            replacements[(15, 921, 0)],
            "쉽다",
            "쉽습니다",
        ),
        "fixed_terminal",
    )
    retarget_matching_calls((15, 921), frozenset({556}), "fixed_terminal")
    set_literal(
        (15, 1541),
        0,
        "취임, 참으로 경사입니다",
        "fixed_terminal",
    )
    set_literal(
        (15, 1541),
        2,
        replacements[(15, 1541, 2)].replace("이루", "실현"),
        "propositive_allomorph",
    )
    set_literal((15, 1541), 3, "", "duplicate_terminal_removed")
    retarget_matching_calls((15, 1541), frozenset({538}), "fixed_terminal")
    set_literal(
        (9, 1437),
        0,
        "인 줄은 몰랐군……\n기뻐해야 할지 탄식해야 할지",
        "particle_neutral_carrier",
    )
    set_literal(
        (9, 1499),
        0,
        "에게라면\n맡길 수 있겠지",
        "particle_neutral_carrier",
    )
    set_literal(
        (9, 1695),
        0,
        "에게 맞서라고!?\n반드시 베겠다!",
        "particle_neutral_carrier",
    )
    set_literal(
        (9, 2443),
        1,
        "의 차례다!\n자, 덤벼 보아라",
        "particle_neutral_carrier",
    )
    set_literal(
        (15, 2063),
        0,
        "이 상대…… 목표로 삼을 성을\n고르는 것이 고민",
        "fixed_selector_particle",
    )
    set_literal(
        (15, 2063),
        2,
        " 방책이라도……",
        "particle_neutral_carrier",
    )
    set_literal(
        (15, 2065),
        1,
        "이 상대인가\n우선은 ",
        "fixed_selector_particle",
    )
    retarget_matching_calls(
        (15, 2065),
        frozenset({1054}),
        "full_future_ha_to_bare_after_action_stem",
    )
    for coordinate in ((15, 355), (15, 1408), (15, 1426)):
        set_literal(
            coordinate,
            1,
            "—그렇게 불러 주십시오\n조금이나마 ",
            "particle_neutral_carrier",
        )
    set_literal(
        (15, 437),
        0,
        "—그게 내 이름이다\n",
        "particle_neutral_carrier",
    )

    # Parenthesized Korean particles are editorial placeholders, not runtime
    # allomorph operators.  Every dynamic name/facility context is rewritten
    # to a carrier that is grammatical for both vowel- and consonant-final
    # values.
    for coordinate in ((7, 88), (7, 95), (7, 2355), (7, 2657)):
        for literal in parse_record_literals(source_records[coordinate]):
            key = (coordinate[0], coordinate[1], literal.literal_id)
            set_literal(
                coordinate,
                literal.literal_id,
                replacements[key].replace("(이)라면", " 정도라면"),
                "particle_neutral_carrier",
            )
    set_literal(
        (7, 2793),
        0,
        " 휘하가 ",
        "particle_neutral_carrier",
    )
    for coordinate in ((8, 72), (8, 746), (8, 752), (8, 754)):
        for literal in parse_record_literals(source_records[coordinate]):
            key = (coordinate[0], coordinate[1], literal.literal_id)
            set_literal(
                coordinate,
                literal.literal_id,
                replacements[key].replace("(이)라면", "의 경우라면"),
                "particle_neutral_carrier",
            )
    for coordinate in ((9, 164), (9, 2227), (9, 2276)):
        for literal in parse_record_literals(source_records[coordinate]):
            key = (coordinate[0], coordinate[1], literal.literal_id)
            set_literal(
                coordinate,
                literal.literal_id,
                replacements[key].replace("(이)라고?", " 말인가?"),
                "particle_neutral_carrier",
            )
    for coordinate in ((9, 169), (9, 2285)):
        for literal in parse_record_literals(source_records[coordinate]):
            key = (coordinate[0], coordinate[1], literal.literal_id)
            set_literal(
                coordinate,
                literal.literal_id,
                replacements[key].replace(
                    "(이)라고……?",
                    " 말인가……?",
                ),
                "particle_neutral_carrier",
            )
    for coordinate in ((9, 172), (9, 2323)):
        for literal in parse_record_literals(source_records[coordinate]):
            key = (coordinate[0], coordinate[1], literal.literal_id)
            set_literal(
                coordinate,
                literal.literal_id,
                replacements[key].replace(
                    "(이)라기에",
                    " 관련 소식이라기에",
                ),
                "particle_neutral_carrier",
            )
    for coordinate in ((9, 190), (9, 2564)):
        for literal in parse_record_literals(source_records[coordinate]):
            key = (coordinate[0], coordinate[1], literal.literal_id)
            set_literal(
                coordinate,
                literal.literal_id,
                replacements[key].replace(
                    "(이)로다!",
                    "에게 맡긴다!",
                ),
                "particle_neutral_carrier",
            )
    for coordinate in ((9, 2283), (9, 2312)):
        for literal in parse_record_literals(source_records[coordinate]):
            key = (coordinate[0], coordinate[1], literal.literal_id)
            set_literal(
                coordinate,
                literal.literal_id,
                replacements[key].replace("(이)란", " 따위는"),
                "particle_neutral_carrier",
            )
    for literal in parse_record_literals(source_records[(9, 2317)]):
        key = (9, 2317, literal.literal_id)
        set_literal(
            (9, 2317),
            literal.literal_id,
            replacements[key].replace(
                "(이)라니",
                " 같은 계책이라니",
            ),
            "particle_neutral_carrier",
        )

    for coordinate in (
        (15, 346),
        (15, 347),
        (15, 352),
        (15, 1399),
        (15, 1400),
        (15, 1405),
        (15, 1417),
        (15, 1418),
        (15, 1423),
    ):
        set_literal(
            coordinate,
            0,
            "의 이름은 ",
            "particle_neutral_name_carrier",
        )
        key = (coordinate[0], coordinate[1], 1)
        set_literal(
            coordinate,
            1,
            re.sub(
                r"^\(이\)라 (?:하오|한다)",
                "입니다",
                replacements[key],
            ),
            "particle_neutral_name_carrier",
        )
    for coordinate in ((15, 348), (15, 1401), (15, 1419)):
        set_literal(
            coordinate,
            0,
            "—그렇게 불러 주십시오\n인연이 닿아 ",
            "particle_neutral_name_carrier",
        )
    for coordinate in ((15, 351), (15, 1404), (15, 1422)):
        set_literal(
            coordinate,
            0,
            "—그렇게 불러 주시옵소서\n"
            "이번에 말석에 들게 되었사오니\n"
            "어떠한 일이라도 맡겨 주시옵소서",
            "particle_neutral_name_carrier",
        )
    for coordinate in ((15, 353), (15, 1406), (15, 1424)):
        set_literal(
            coordinate,
            0,
            "—그게 제 이름입니다\n"
            "부족한 점도 많겠지만\n최선을 다하겠습니다!",
            "particle_neutral_name_carrier",
        )
    for coordinate in ((15, 354), (15, 1407), (15, 1425)):
        set_literal(
            coordinate,
            1,
            "입니다\n이제부터 신세 좀 지겠다\n"
            "싸움이라면 내게 맡겨 주시오!",
            "particle_neutral_name_carrier",
        )
    for coordinate in ((15, 318), (15, 319)):
        for literal in parse_record_literals(source_records[coordinate]):
            key = (coordinate[0], coordinate[1], literal.literal_id)
            set_literal(
                coordinate,
                literal.literal_id,
                replacements[key].replace(
                    "(이)라는 자가",
                    ", 그 무장이",
                ),
                "particle_neutral_name_carrier",
            )
    for coordinate in ((15, 383),):
        set_literal(
            coordinate,
            1,
            " 측의 ",
            "particle_neutral_name_carrier",
        )
        set_literal(
            coordinate,
            2,
            " 같은 인물 말이오",
            "particle_neutral_name_carrier",
        )
    for coordinate in ((15, 438),):
        set_literal(
            coordinate,
            1,
            "—그렇게 불러 주시옵소서\n"
            "부족한 몸이오나 아무쪼록 잘 부탁드리옵니다",
            "particle_neutral_name_carrier",
        )
    set_literal(
        (15, 433),
        1,
        "—그렇게 불러 주시옵소서\n",
        "particle_neutral_name_carrier",
    )
    set_literal(
        (15, 435),
        0,
        "이제부터 함께할 사람의 이름은 ",
        "particle_neutral_name_carrier",
    )
    set_literal(
        (15, 435),
        1,
        "일세\n",
        "particle_neutral_name_carrier",
    )
    set_literal(
        (15, 436),
        1,
        "입니다\n앞으로 잘 부탁드리옵니다",
        "particle_neutral_name_carrier",
    )
    for coordinate in ((15, 917), (15, 922)):
        set_literal(
            coordinate,
            2,
            ", 그곳이 급소로 판단되므로\n"
            "미리 성벽을 무너뜨려 두고자 하옵니다",
            "particle_neutral_name_carrier",
        )
    set_literal(
        (6, 4655),
        0,
        "\n가재로 임명합니다\n계속하시겠습니까?",
        "selector_person_reflexive_carrier",
    )
    set_literal(
        (6, 4656),
        0,
        "\n",
        "selector_person_reflexive_carrier",
    )
    set_literal(
        (6, 3658),
        0,
        " 가보를 ",
        "persona_boundary_spacing",
    )
    set_literal(
        (6, 3619),
        0,
        "하고 ",
        "persona_boundary_spacing",
    )
    set_literal(
        (6, 3676),
        2,
        "에게 잘못 따위 ",
        "lexical_spacing",
    )
    set_literal(
        (6, 4656),
        1,
        "\n종속 다이묘의 가재로 임명합니다\n계속하시겠습니까?",
        "selector_person_reflexive_carrier",
    )
    set_literal(
        (7, 802),
        1,
        " 등 ",
        "selector_noun_spacing",
    )
    set_literal(
        (7, 805),
        2,
        " 등 ",
        "selector_noun_spacing",
    )

    exact_call_retargets = (
        ((6, 3758), 1, 34, 1193, "selector_family_call34_removed"),
        ((6, 3842), 0, 34, 1193, "selector_family_call34_removed"),
        ((6, 3932), 1, 34, 1193, "selector_family_call34_removed"),
    )
    for coordinate, ordinal, old, new, rule in exact_call_retargets:
        add_retarget(
            retargets,
            coordinate=coordinate,
            call_ordinal=ordinal,
            old_target=old,
            new_target=new,
            rule=rule,
        )
    set_literal(
        (6, 3758),
        1,
        "에서 온 사절의\n도착",
        "selector_family_sentence",
    )
    set_literal(
        (6, 3758),
        2,
        "",
        "selector_family_sentence",
    )
    set_literal((6, 3842), 0, " 당주", "selector_family_sentence")
    set_literal(
        (6, 3842),
        1,
        " 측에서\n면회를 청하러 찾아왔습니다",
        "selector_family_sentence",
    )
    set_literal(
        (6, 3932),
        1,
        " 측에서\n면회를 요청해 와 있",
        "selector_family_sentence",
    )
    set_literal(
        (6, 3932),
        2,
        "",
        "selector_family_sentence",
    )
    for coordinate, literal_id, particle, carrier in (
        ((2, 101), 1, "을", " 같은 분을"),
        ((2, 103), 1, "께", " 같은 분께"),
        ((2, 104), 1, "을", " 같은 분을"),
        ((15, 1600), 2, "을", " 같은 분을"),
    ):
        key = (coordinate[0], coordinate[1], literal_id)
        value = replacements[key]
        require(
            value.startswith(particle),
            f"call8 carrier prefix drifted at {key}: {value!r}",
        )
        set_literal(
            coordinate,
            literal_id,
            carrier + value[len(particle):],
            "call8_particle_neutral_carrier",
        )
    for record_id in range(1426, 1438):
        set_literal(
            (6, record_id),
            2,
            " 주군의 기대에 부응",
            "exact_noop_call_carrier",
        )
    set_literal(
        (7, 271),
        1,
        " 주군의 뜻대로 쓰시오",
        "exact_noop_call_carrier",
    )
    set_literal(
        (15, 1529),
        3,
        " 그대의 힘을 보태 주시옵소서!",
        "exact_noop_call_carrier",
    )

    exact_flatten: dict[
        tuple[int, int],
        tuple[tuple[str, ...], frozenset[int]],
    ] = {
        (1, 11): (
            (
                "안 되겠습니다. 황송합니다. 그러나, "
                "저는 이후 일정이 있으므로\n"
                "이 건은 여기까지 하겠습니다.",
                "",
                "",
                "",
                "",
            ),
            frozenset(),
        ),
        (2, 123): (
            (
                "부디 안심하십시오, ",
                "의 뜻대로\n",
                " 가문을 제 지혜와 용맹으로 이어 가고…\n"
                "아니, 더욱 번영시키겠다고 ",
                "약속드리겠습니다",
            ),
            frozenset({0}),
        ),
        (2, 129): (
            (
                "우리 가문의 앞날을 맡게 되다니\n"
                "더없는 기쁨인 동시에, 막중한 소임에\n"
                "마음이 절로 다잡히는군요",
                "",
            ),
            frozenset(),
        ),
        (2, 121): (
            (
                "의 이름이 주는 책임은 무겁지만 자랑스럽기도 하니\n"
                "절로 마음가짐이 바로 섭니다.",
                "\n부디 뒷일은 맡겨 주십시오.",
            ),
            frozenset(),
        ),
        (2, 531): (
            (
                "의 힘이 되어 주도록\n"
                "다시 생각해 주지 않겠나?",
            ),
            frozenset(),
        ),
        (2, 533): (
            (
                "에게는 스와의 가호가 있다!\n"
                "함께 천하를 노립시다",
            ),
            frozenset(),
        ),
        (2, 646): (
            (
                "\n완료까지 앞으로 ",
                "일 정도 걸릴 전망입니다",
            ),
            frozenset(),
        ),
        (2, 648): (
            (
                "\n완료까지 앞으로 ",
                "일 정도 걸릴 전망입니다",
            ),
            frozenset(),
        ),
        (6, 1134): (
            (
                "배후를 기습당하면\n곤란합니다.",
                "",
            ),
            frozenset(),
        ),
        (6, 3517): (
            (
                "에 이름을 올린다는 것은\n"
                "일거수일투족마다 우리 가문을 짊어진다는 것\n"
                "품격 없는 행동은 삼가야 합니다.",
                "",
            ),
            frozenset(),
        ),
        (6, 3845): (
            (
                "에는 ",
                "과 동맹을 맺고 있어\n"
                "섣불리 공격하기는 위험합니다.",
                "",
            ),
            frozenset(),
        ),
        (6, 3944): (
            (
                ", 조정에서 ",
                "사자가 찾아와",
                "\n꼭 ",
                " 쪽으로\n가고 싶다고 합니다.",
            ),
            frozenset({0, 3}),
        ),
        (6, 4182): (
            (
                "영내 정책의 방침을 각 성주에게 전했더니\n"
                "구체적인 방안이 나왔습니다",
                "\n어느 성을 강화할지, ",
                "지시해 주십시오",
            ),
            frozenset(),
        ),
        (6, 4383): (
            (
                "정책「",
                "」 발령 뒤 지을 수 있는\n",
                "도 꼭 짓고 싶습니다",
                "\n우리 성에는 건설에 능한 자가 있습니다.",
                "",
            ),
            frozenset(),
        ),
        (6, 3557): (
            (
                "앞으로도 잘 부탁드립니다",
            ),
            frozenset(),
        ),
        (6, 3397): (
            (
                "의 뒤를 이을 수 있다니 더없는 영광입니다.\n",
                "의 뜻과 ",
                "의 이름을 이어\n가문을 지켜내겠습니다",
            ),
            frozenset({0}),
        ),
        (6, 3407): (
            (
                ", 안심하십시오",
                ".\n",
                "의 뜻과 ",
                "의 이름을 이어\n가문을 지켜 보이겠습니다",
            ),
            frozenset({0}),
        ),
        (6, 3614): (
            (
                " 가보를 줄 테니\n",
                " 가보를 돌려달라니…\n마음대로 하십시오",
            ),
            frozenset(),
        ),
        (6, 3615): (
            (
                " 가보가\n",
                "제가 가진 ",
                "보다\n더 낫거나 못지않은 물건이라면…",
            ),
            frozenset(),
        ),
        (6, 3616): (
            (
                "마음은 고맙습니다. 하지만\n",
                "",
                "제가 가진 ",
                "보다\n더 나은 것을 받고 싶습니다",
                "…",
            ),
            frozenset(),
        ),
        (6, 3617): (
            (
                " 가보를 주신다 해도\n",
                "제가 가진 ",
                "하고\n비교하면 다소…",
            ),
            frozenset(),
        ),
        (6, 3618): (
            (
                " 가보를 줄 테니\n",
                " 가보를 돌려달라니, 결국\n그런 뜻입니다. 그렇군…",
                "",
            ),
            frozenset(),
        ),
        (6, 3619): (
            (
                "하고 제가 가진 ",
                "",
                "의 가치를 비교하면\n",
                "저에 대한 평가도 알 수 있겠습니다",
                "…",
            ),
            frozenset(),
        ),
        (6, 3620): (
            (
                " 가보를 받을 수 있는 것",
                "\n다만, 그 대신 ",
                " 가보를 내놓는 것은\n그다지 내키지 않습니다",
                "…",
            ),
            frozenset({0}),
        ),
        (6, 3621): (
            (
                "솔직히 말씀드리면 ",
                "보다\n",
                "제가 가진 ",
                " 쪽이\n더 좋습니다",
                "…",
            ),
            frozenset(),
        ),
        (6, 3622): (
            (
                "하고 제가 가진 ",
                "",
                " 가보를 맞바꾸는 것입니까?",
                "\n아니요",
                ", 아무것도 아닙니다",
                "…",
            ),
            frozenset(),
        ),
        (6, 3623): (
            (
                "하고\n제가 가진 ",
                "",
                " 가보를 맞바꾸다니\n무슨 생각이십니까",
                "…",
            ),
            frozenset(),
        ),
        (6, 3624): (
            (
                " 가보를 받아 기쁩니다만\n",
                " 가보를 돌려드려야 하는 점은 아쉽습니다",
                "…",
            ),
            frozenset(),
        ),
        (6, 3625): (
            (
                " 가보를 받을 수 있는 것입니까",
                "\n다만, 제가 가진 ",
                "",
                "하고\n비교하면 다소…",
            ),
            frozenset(),
        ),
        (6, 3652): (
            (
                "이럴 수가, ",
                " 가보를…!\n",
                "의 취향을 알고 계시다니\n"
                "놀라움을 금할 수 없습니다",
            ),
            frozenset({0}),
        ),
        (6, 3669): (
            (
                "의 ",
                " 가보를 거두어 가시다니\n"
                "그런 일은 결단코 용납할 수 없습니다",
            ),
            frozenset({0}),
        ),
        (6, 3660): (
            (
                "늙은이라 해서\n물욕이 없는 것은 아닙니다",
            ),
            frozenset(),
        ),
        (6, 3670): (
            (
                "의 ",
                " 가보를 거두어 가시다니…\n"
                "웃을 수 없습니다",
                ". 그렇군",
            ),
            frozenset({0}),
        ),
        (15, 1198): (
            (
                "은 단것을 고마워하는 모양입니다\n"
                "코…… 콘페…… 콘페이토? "
                "피로에 효험이 있다 들었소",
            ),
            frozenset(),
        ),
        (15, 383): (
            (
                "귀순을 권하려면 상대를\n"
                "잘 가려야 하오…… 이를테면\n",
                "",
                " 같은 인물 말이오",
            ),
            frozenset(),
        ),
        (15, 1645): (
            (
                "의 위치로는 전쟁을 지휘하기에\n"
                "너무 멀리 떨어져 있을지도 모르겠습니다.\n",
                "우리 가문도 제법 커졌습니다.",
                "",
            ),
            frozenset(),
        ),
        (15, 1677): (
            (
                ", ",
                "합전",
                "의 지휘를 맡아 주십시오!\n"
                "직접 지휘하신다면\n"
                "단기 결착을 기대할 수 있겠사옵니다",
            ),
            frozenset({0}),
        ),
        (9, 3677): (
            (
                "아군의 우세는 확고합니다.\n",
                "하지만 지장·",
                "의 지략은 널리 알려졌으니\n"
                "전장을 휘저으면 성가실 것입니다.",
            ),
            frozenset(),
        ),
        (15, 2230): (
            (
                "을 공략해 차지하는 것이 어떻겠소\n"
                "우리 병력은 ",
                "보다 우세하니\n대군을 동원해 쳐부숩시다",
            ),
            frozenset(),
        ),
        (15, 2254): (
            (
                "헌언을 허락해 주시니, 고맙습니다",
                "",
                "\n그러면 지금 해야 할 일에 관해\n제",
                " 견해를 말씀드리겠습니다",
            ),
            frozenset(),
        ),
        (8, 1018): (
            (
                "콜록, 콜록…\n몸을 돌보지 않은 탓인 듯합니다…",
                "",
            ),
            frozenset(),
        ),
        (8, 1019): (
            (
                "으윽, 병에 걸린 모양입니다…\n"
                "반드시 회복하겠습니다. 그러므로, 잠시 시간을…",
                "",
                "",
                "",
            ),
            frozenset(),
        ),
        (6, 4385): (
            (
                "도 짓고 싶지만\n"
                "그에 걸맞게 상업이 진흥될 때까지\n"
                "보류하겠습니다",
                "",
            ),
            frozenset(),
        ),
        (6, 3756): (
            (
                "에게 당장 원군을 청하기는 어렵습니다.\n",
                "앞날까지 내다본 방안이라면 검토할 만합니다.",
            ),
            frozenset(),
        ),
        (6, 3757): (
            (
                "에게 당장 원군을 청하는 것은 어리석은 계책입니다.\n",
                "다만 앞날을 내다보고 신용을 쌓는 일은 "
                "나쁘지 않습니다.",
            ),
            frozenset(),
        ),
        (6, 3858): (
            (
                " 쪽으로 임명된다면\n"
                "기뻐하지 않을 다이묘가 있겠습니까?",
                "",
            ),
            frozenset(),
        ),
        (6, 4376): (
            (
                "…말씀드리기 어렵습니다.\n",
                "",
                "제게는 벅찬 일인 듯합니다.",
            ),
            frozenset(),
        ),
        (8, 263): (
            (
                ", 올해는 흉작이지만\n",
                "미리 대비한 지역은 큰 피해를 면했습니다.",
            ),
            frozenset({0}),
        ),
        (8, 285): (
            (
                "영내에 가뭄이 발생했지만,\n"
                "미리 대책을 세워 둔 지역은 화를 면했습니다.",
                "",
                "",
            ),
            frozenset(),
        ),
        (8, 286): (
            (
                "가뭄이 닥쳤지만,\n대책을 마련한 영지는 화를 면했습니다.\n"
                "선견지명이란 바로 이런 것입니다.",
                "",
                "",
            ),
            frozenset(),
        ),
        (8, 287): (
            (
                "우리 영내도 가뭄에 시달렸지만,\n"
                "미리 대비한 지역은 큰 피해를 면했습니다.",
                "",
                "",
            ),
            frozenset(),
        ),
        (8, 288): (
            (
                "영내에 가뭄이 닥쳤지만,\n"
                "미리 대책을 마련하여 무사히 넘긴 지역이 있습니다.",
                "",
                "",
                "",
            ),
            frozenset(),
        ),
        (8, 289): (
            (
                "가뭄 발생에 간담이 서늘했지만,\n"
                "미리 대책을 마련해 두어 큰 피해를 막았습니다.\n"
                "그대의 대처가 참으로 훌륭합니다.",
                "",
                "",
                "",
            ),
            frozenset(),
        ),
        (8, 305): (
            (
                "홍수 피해를 입었지만,\n"
                "미리 대책을 마련한 곳은 화를 면했다는 소식입니다.",
                "",
                "",
            ),
            frozenset(),
        ),
        (8, 308): (
            (
                "영내에서 홍수가 발생했지만,\n"
                "미리 대응한 곳은 화를 면했습니다.",
                "",
                "",
            ),
            frozenset(),
        ),
        (8, 309): (
            (
                "영내에서 홍수가 발생했지만,\n"
                "미리 대비한 곳은 피해가 줄었습니다.",
                "",
                "",
            ),
            frozenset(),
        ),
        (8, 329): (
            (
                "태풍이 영내를 지나갔지만,\n"
                "미리 대책을 마련한 곳은 큰 피해를 면했습니다.",
                "",
                "",
            ),
            frozenset(),
        ),
        (8, 330): (
            (
                "태풍 피해를 입었지만,\n"
                "미리 대비한 지역은 큰 피해를 면했습니다.",
                "",
                "",
            ),
            frozenset(),
        ),
        (8, 331): (
            (
                "태풍 피해가 발생했지만,\n"
                "사전에 대책을 마련한 지역은 무사히 넘겼습니다.",
                "",
                "",
            ),
            frozenset(),
        ),
        (8, 391): (
            (
                "분부라면 따르겠습니다.\n"
                "다만 납득하기는 어렵습니다…",
                "",
                "",
            ),
            frozenset(),
        ),
        (8, 392): (
            (
                "제가 납득한 것으로\n여겨졌습니까?",
                "",
            ),
            frozenset(),
        ),
        (8, 1196): (
            (
                "그렇습니까…\n유감이지만 어쩔 수 없습니다.",
                "",
                "",
            ),
            frozenset(),
        ),
        (15, 264): (
            (
                "한 말씀 올리겠습니다.\n"
                "이럴 때는 제가 재지를 발휘하여\n"
                "누구도 생각지 못할 묘안을 내겠습니다.",
                "",
                "",
                "",
            ),
            frozenset(),
        ),
        (15, 281): (
            (
                "좋은 방안이라 생각했지만…\n"
                "조금 궁리가 부족했던 것일까요?",
                "",
                "",
            ),
            frozenset(),
        ),
        (15, 1226): (
            (
                "요해인 ",
                "을 함락하려면\n땅굴 공략을 쓰는 것이 좋겠습니다.",
            ),
            frozenset(),
        ),
    }
    # Reviewed high-confidence failures discovered by the independent
    # full-Cartesian and Kiwi probes.  Selector components remain in place;
    # only incompatible style calls are redirected to the empty terminal.
    exact_flatten.update(
        {
            (1, 14): (
                (
                    "힘들 때일수록 웃으십시오.\n",
                    "그러고 보니 그분께서는\n",
                    "언제나 그렇게 말씀하셨습니다",
                    ".",
                ),
                frozenset(),
            ),
            (1, 15): (
                (
                    "힘들 때일수록 웃어야 합니다",
                    ".\n그러한 마음가짐이야말로 중요합니다",
                    ".\n누가 한 말일까요",
                    ".",
                ),
                frozenset(),
            ),
            (2, 105): (
                (
                    "원복을 마치고\n한 사람 몫을 하게 된 무장 수: ",
                    "명입니다",
                ),
                frozenset(),
            ),
            (2, 106): (
                (
                    "원복을 마치고\n휘하에 들어오는 무장 수: ",
                    "명입니다",
                ),
                frozenset(),
            ),
            (2, 494): (
                ("일문이 굳게 뭉쳐야\n영지가 안정되는 법입니다",),
                frozenset(),
            ),
            (2, 647): (
                ("에 관한 진언이 진행 중입니다",),
                frozenset(),
            ),
            (2, 650): (
                ("에 대한 친선은\n", "개월 후 완료될 예정입니다"),
                frozenset(),
            ),
            (2, 651): (
                ("조정과의 친선은\n", "개월 후 완료될 예정입니다"),
                frozenset(),
            ),
            (6, 3506): (
                (
                    "공을 인정받아 참으로 기쁩니다",
                    ".\n참으로 고마울 따름입니다",
                    "!\n앞으로 더욱 놀라게 해 보이겠습니다",
                    "!",
                ),
                frozenset(),
            ),
            (6, 3508): (
                (
                    "훈공 1위, 감사히 받겠습니다",
                    "!\n",
                    "의 말석에 이름을 올린 몸으로서\n"
                    "신분에 부끄럽지 않도록 노력하겠습니다",
                    "!",
                ),
                frozenset(),
            ),
            (6, 3534): (
                (
                    "신하의 도를 닦는 길에는 끝이 없으니…\n"
                    "우리 가문의 앞날을 지켜보는 것이야말로\n",
                    "의 천명입니다",
                ),
                frozenset({0}),
            ),
            (6, 3727): (
                (
                    "과의 정전 기한이 끝났습니다",
                    "\n빈틈을 보이지 않도록 ",
                    "유의해 주십시오",
                ),
                frozenset(),
            ),
            (6, 3746): (
                ("의 뜻을 받들어\n", "외교 관계 유지에 노력하겠습니다"),
                frozenset(),
            ),
            (6, 3748): (
                ("과의 관계 유지에 노력하겠습니다",),
                frozenset(),
            ),
            (6, 3851): (
                (
                    "다음은 ",
                    "의 관직에\n천거받을 수 있도록 노력하겠습니다",
                ),
                frozenset(),
            ),
            (6, 3877): (
                (
                    " 시설을 건설해 주십시오",
                    "\n훌륭히 일한 자에게는 상을 내리십시오",
                    "\n모두, 힘써 일하십시오",
                ),
                frozenset(),
            ),
            (6, 4169): (
                (
                    "의 출진에 맞춰\n",
                    "",
                    "우리도 출진할 때까지\n영내 발전에 노력하겠습니다",
                ),
                frozenset(),
            ),
            (6, 4173): (
                (
                    "주명을 가신들에게 알렸더니\n"
                    "방침에 부합할 만한 제안이 있었습니다",
                    "\n승인할지 확인해 주십시오",
                ),
                frozenset(),
            ),
            (6, 4180): (
                (
                    "에 착수하십시오",
                    "\n훌륭히 일한 자에게는 상을 내리십시오",
                    "\n모두, 힘써 일하십시오",
                ),
                frozenset(),
            ),
            (6, 4365): (
                (
                    "배려에 감사합니다",
                    "\n",
                    "의 성주로서\n성하 발전에 노력하겠습니다",
                ),
                frozenset(),
            ),
            (6, 4387): (
                (
                    " 시설을 지을 수 있다면\n더욱 이상적입니다",
                    ". 하지만…",
                ),
                frozenset(),
            ),
            (7, 261): (
                ("의 아량에 감사합니다", "\n이제부터 충성을 다하겠습니다"),
                frozenset({0}),
            ),
            (7, 269): (
                (
                    "우리 가문이 천하를 다스릴 길은 끊겼습니다",
                    "……\n이후로는 「",
                    "」의 휘하에서\n천하를 위해 힘쓰겠습니다",
                ),
                frozenset({1}),
            ),
            (7, 2542): (
                (
                    "이번 일은 제가 맡겠습니다",
                    "!\n모두, ",
                    "저를 본보기로 삼으십시오\n"
                    "그러면 범과 같은 군대가 될 것입니다",
                ),
                frozenset(),
            ),
            (8, 277): (
                (
                    "올해는 참으로 통탄스럽게도\n"
                    "우리 영내가 흉작에 시달렸습니다",
                    "\n병사들을 굶길 수는 없습니다",
                ),
                frozenset(),
            ),
            (8, 296): (
                (
                    ", 「",
                    "」의 영지에\n가뭄 피해가 발생했습니다",
                    "\n토지는 황폐해지고 민충도 떨어졌습니다",
                ),
                frozenset({0, 1}),
            ),
            (8, 297): (
                (
                    "영내에 가뭄 피해가 발생했습니다",
                    "\n천재지변은 피할 수 없다지만\n"
                    "좀처럼 뜻대로 되지 않네요",
                ),
                frozenset(),
            ),
            (8, 319): (
                (
                    "홍수 피해를 입은 곳이 있습니다",
                    "\n그곳에 사는 이들이 고초를 겪고 있습니다",
                    ".\n대책을 마련해야 할 듯합니다",
                ),
                frozenset(),
            ),
            (8, 340): (
                (
                    ", 영내를 태풍이 덮쳐,\n큰 피해를 입은 군이 있습니다",
                    "\n대책을 세워야 합니다",
                ),
                frozenset({0}),
            ),
            (8, 390): (
                (
                    "선뜻 수긍하기는 어렵습니다",
                    "\n하지만 따를 수밖에 없겠지요",
                ),
                frozenset(),
            ),
            (8, 1004): (
                (
                    "주변 세력의 위협은 없는 듯합니다",
                    "\n당분간 내정에 힘을 쏟아\n"
                    "차분히 자리 잡고 임지를 발전시키겠습니다",
                ),
                frozenset(),
            ),
            (8, 1012): (
                (
                    "적과의 경계에서 먼 이 땅에서는\n"
                    "내정에 중점을 두는 편이 상책일 듯합니다.\n"
                    "장기적인 영토 발전을 목표로 삼겠습니다",
                ),
                frozenset(),
            ),
            (8, 1017): (
                (
                    "알겠습니다",
                    "\n성주인 제가 직접 ",
                    "이 땅을 다스리겠습니다",
                ),
                frozenset(),
            ),
            (8, 1182): (
                (
                    "금 광맥을 발견했다는\n백성의 보고가 있었습니다",
                    "\n채굴에 나서 보는 것이 어떻겠습니까",
                ),
                frozenset(),
            ),
        }
    )
    exact_flatten.update(
        {
            (6, 4294): (
                (
                    "정책「",
                    "」(LV",
                    ")\n발령했습니다",
                    "\n더할 나위 없는 내용이 되었습니다",
                ),
                frozenset(),
            ),
            (6, 4366): (
                (
                    "과분한 ",
                    "배려에 감사한 마음을 금할 길 없습니다",
                    "\n저와 「",
                    "",
                    "」 두 사람은 서로 힘을 합쳐\n",
                    " 그리고 「",
                    "」의 발전에 노력하겠습니다",
                ),
                frozenset(),
            ),
            (7, 2394): (
                (
                    "다음 성을 공격하겠습니다",
                    "\n",
                    "으로 향하겠습니다",
                    "!",
                ),
                frozenset(),
            ),
            (8, 982): (
                (
                    "이 땅을 풍요롭게 하도록 노력하겠습니다",
                    "\n우선 영내의 「",
                    "」 장악에 착수하겠습니다",
                ),
                frozenset(),
            ),
            (8, 988): (
                (
                    "이 땅을 풍요롭게 하도록 노력하겠습니다",
                    "\n우선 「",
                    "」 성하에 「",
                    "」 건설을\n그 첫걸음으로 삼겠습니다",
                ),
                frozenset(),
            ),
            (8, 991): (
                (
                    "이 땅을 통치하도록 노력하겠습니다",
                    "\n우선 「",
                    "」 성하에 「",
                    "」 건설을\n그 첫걸음으로 삼겠습니다",
                ),
                frozenset(),
            ),
            (8, 994): (
                (
                    "이 땅을 통치하도록 노력하겠습니다",
                    "\n우선 영내에 「",
                    "」 설치를\n그 첫걸음으로 삼겠습니다",
                ),
                frozenset(),
            ),
            (8, 996): (
                (
                    "이 영지, 분명히 맡겠습니다",
                    "\n",
                    "을 공략할 준비를 갖추고자\n"
                    "영주로서 노력하겠습니다",
                ),
                frozenset(),
            ),
            (8, 1000): (
                ("이 땅을 풍요롭게 하기 위해\n미력하나마 노력하겠습니다",),
                frozenset(),
            ),
            (15, 2160): (
                (
                    "취락을 지배하게 되어\n",
                    "에 새 시설을\n착공할 수 있게 되었습니다",
                ),
                frozenset(),
            ),
        }
    )
    exact_flatten.update(
        {
            (9, 3672): (
                (
                    "전력은 호각이라 할 만합니다",
                    "\n적장 「",
                    "」, 맹장으로 이름 높으니\n"
                    "어설픈 부대로는 단숨에 짓눌릴 것입니다",
                ),
                frozenset(),
            ),
            (9, 3673): (
                (
                    "양군의 전력은 팽팽히 맞섭니다",
                    ", 하지만\n적진에는 지장·",
                    "의 모습이 보이는군\n"
                    "전장에서도 무언가 수를 써 올지 모르네",
                ),
                frozenset(),
            ),
            (9, 3674): (
                (
                    "양군의 전력은 팽팽히 맞섭니다",
                    ", 하지만\n적진에 이름난 장수는 없습니다",
                    "\n정면으로 싸우면 이길 수 있습니다",
                ),
                frozenset(),
            ),
            (9, 3679): (
                (
                    "아군은 상당히 열세입니다",
                    "\n게다가 맹장·",
                    "까지 출진하다니…\n",
                    "의 기세를 막아야 활로가 열립니다",
                ),
                frozenset({1}),
            ),
            (9, 3684): (
                ("수비를 중시해\n견실하게 싸우겠습니다",),
                frozenset(),
            ),
            (13, 115): (
                (
                    "또한 영토의 발전을 생각하신다면\n정무에 능한 이 \"",
                    "\"의 재능이\n반드시 도움이 될 날이 올 것입니다",
                ),
                frozenset(),
            ),
            (13, 126): (
                (
                    "영토의 발전을 생각하신다면\n정무에 능한 이 \"",
                    "\"의 재능이\n반드시 도움이 될 날이 올 것입니다",
                ),
                frozenset(),
            ),
            (15, 244): (
                ("좋은 방안입니다", "\n성공은 틀림없겠지요"),
                frozenset(),
            ),
            (15, 265): (
                (
                    "주제넘은 말씀입니다",
                    ". 그러나…\n신앙의 힘은 얕볼 수 없습니다.\n",
                    "에게도 한 가지 계책이 있습니다",
                ),
                frozenset({1}),
            ),
            (15, 274): (
                (
                    "더 성공하기 쉬운 계책이라 할 수 있습니다",
                    "\n시간은 걸립니다",
                    ". 하지만\n착실히 진행할 수 있습니다",
                ),
                frozenset(),
            ),
            (15, 275): (
                (
                    "더 성공하기 쉬운 계책이라 할 수 있습니다",
                    "\n시간은 걸립니다",
                    ". 하지만\n착실히 진행할 수 있습니다",
                ),
                frozenset(),
            ),
            (15, 636): (
                (
                    "우리와 ",
                    " 쪽은 이제\n운명을 함께하는 사이옵니다\n"
                    "속히 휘하에 들여야 할 듯하옵니다",
                ),
                frozenset(),
            ),
            (15, 1096): (
                (
                    "송구하기 그지없습니다",
                    "……조략이 드러나\n",
                    "·",
                    " 두 가문의\n"
                    "우리 가문에 대한 인상이 나빠진 모양입니다……",
                ),
                frozenset(),
            ),
            (15, 1192): (
                (
                    "과의 관계 개선은\n제가 맡겠습니다",
                    "",
                    "\n금전에 걸맞은 성과를 보이겠습니다",
                ),
                frozenset(),
            ),
            (15, 1344): (
                (
                    "맹장·",
                    "의 건재 시\n",
                    " 공략은 난항을 겪을 것입니다",
                    ". 그렇지\n그래, 어디까지나 건재한 한……",
                ),
                frozenset(),
            ),
            (15, 1435): (
                (
                    " 근처는 경비가 허술한 모양입니다.\n"
                    "출병용 병량을 불태워\n",
                    "의 전력을 줄입시다",
                ),
                frozenset(),
            ),
            (15, 1461): (
                (
                    "의 모략은 통하지 않습니다",
                    "\n이런 자는 금세 유언비어를 믿고\n"
                    "주군 가문에 등을 돌릴 것입니다",
                ),
                frozenset(),
            ),
            (15, 1471): (
                (
                    "의 경우 유언비어에 현혹되어\n"
                    "제 거취를 망설이는 모양입니다.\n"
                    "이참에 그자를 빼내자고 건의드립니다",
                ),
                frozenset(),
            ),
            (15, 1487): (
                (
                    "재해로 인해 ",
                    "에서는\n불온한 움직임이 있습니다",
                    "\n잇키를 경계해야 합니다",
                ),
                frozenset(),
            ),
            (15, 1526): (
                (
                    "유망한 낭인은 발견하지 못했습니다",
                    "……\n싸움에서 사로잡은 다른 가문의 자를 설득하는 등\n"
                    "다른 길을 모색해야겠습니다",
                ),
                frozenset(),
            ),
            (15, 1539): (
                (
                    "우리 가문이야말로 이 나라에 둘도 없는 무가\n"
                    "천하에 패권을 떨쳐\n천하 평정을 이루겠습니다",
                    "",
                ),
                frozenset(),
            ),
            (15, 1581): (
                (
                    "……본의는 아닙니다",
                    ". 그러나\n이번 ",
                    " 공략은\n중단해야 합니다",
                    "……",
                ),
                frozenset(),
            ),
            (15, 1584): (
                (
                    "병량이 이제 곧 바닥납니다",
                    "\n내키지는 않습니다",
                    ". 다만\n여기서는 철수해야 합니다",
                    "……",
                ),
                frozenset(),
            ),
            (15, 1585): (
                (
                    "지금 우리의 전력으로는\n",
                    "을 공략하기는 어렵습니다",
                    "\n지금이 물러날 때인지도 모르옵니다",
                ),
                frozenset(),
            ),
            (15, 2186): (
                (
                    " 군이 ",
                    "에게서\n조략을 받고 있는 듯합니다",
                    "\n출병하여 방해하겠습니다",
                ),
                frozenset(),
            ),
            (15, 2244): (
                (
                    "이 적의 편에 붙었습니다",
                    "\n쳐들어갈 때는 원군을 ",
                    "주의해 주십시오",
                ),
                frozenset(),
            ),
            (15, 2245): (
                (
                    "을 비롯한 ",
                    "개 세력이\n적의 편에 붙었습니다",
                    "\n쳐들어갈 때는 원군을 ",
                    "주의해 주십시오",
                ),
                frozenset(),
            ),
            (15, 2257): (
                (
                    "그 말씀을 기다리고 있었습니다",
                    "!\n즉시 출병을 준비하겠습니다",
                ),
                frozenset(),
            ),
            (15, 2415): (
                (
                    "이번 ",
                    ", ",
                    "에게 간파되어\n오히려 아군까지 동요했습니다",
                    "\n",
                    "을 상대로 조략을 펼칠 때는 ",
                    "신중히 해야 합니다",
                ),
                frozenset(),
            ),
        }
    )
    for record_id in range(2355, 2363):
        coordinate = (15, record_id)
        original = tuple(
            replacements[(15, record_id, literal.literal_id)]
            for literal in parse_record_literals(source_records[coordinate])
        )
        facility = (
            original[-1]
            .replace("알맞게 운용하는 편이", "알맞게 운용하는 편이 좋겠습니다.")
        )
        if record_id <= 2358:
            literals = (
                "우리 가문은 다른 가문에 비해\n",
                "의 수입이 부족한 상태입니다.",
                facility,
            )
        else:
            literals = (
                "우리 가문은 그리 풍족하지 않습니다.\n특히 ",
                "",
                "의 수입은 다른 가문보다 부족합니다.",
                facility,
            )
        exact_flatten[coordinate] = (literals, frozenset())

    for coordinate, (literals, keep_call_ordinals) in sorted(
        exact_flatten.items()
    ):
        record_literals = parse_record_literals(source_records[coordinate])
        require(
            len(record_literals) == len(literals),
            f"exact flatten literal count drifted at {coordinate}",
        )
        for literal, value in zip(record_literals, literals):
            set_literal(
                coordinate,
                literal.literal_id,
                value,
                "exact_cartesian_sentence_rewrite",
            )
        retargets = [
            value for value in retargets if value.coordinate != coordinate
        ]
        ordinal = -1
        for component in SURFACE_QA.tolerant_decode_record(
            source_records[coordinate]
        ):
            if component["kind"] != "call":
                continue
            ordinal += 1
            if ordinal in keep_call_ordinals:
                continue
            target = int(component["target"][1])
            add_retarget(
                retargets,
                coordinate=coordinate,
                call_ordinal=ordinal,
                old_target=target,
                new_target=1193,
                rule="exact_cartesian_sentence_rewrite",
            )

    # Resolve the reviewed morph-pair leaf records to one grammatical formal
    # variant.  Dynamic selectors and substantive person/name calls remain in
    # place; only grammar calls are folded into an adjacent literal.  The 101
    # selector/jump-only parents then become clean transitively.
    morph_provisional_blob = apply_plan(
        source_blob,
        {
            coordinate: replacements[coordinate]
            for coordinate in changed
        },
        tuple(retargets),
    )
    morph_records = records_from_blob(morph_provisional_blob)
    morph_renderer = CALL_QA.SyntheticSelectorRenderer(morph_records)
    substantive_call_targets = frozenset(
        {
            1,   # speaker first-person register
            4,   # dynamic person name, sometimes with 놈
            7,   # 저희/우리
            8, 17, 21, 29, 37,  # dynamic kinship/address
            34,  # dynamic person name/honorific
        }
    )
    morph_allowlist_coordinates = {
        coordinate
        for coordinate, _category, _segment
        in CALL_QA.BASE_MORPH_PAIR_EXACT_ALLOWLIST
    }

    def replace_retarget_with_empty(
        coordinate: tuple[int, int],
        call_ordinal: int,
        current_target: int,
    ) -> None:
        nonlocal retargets
        existing = [
            value
            for value in retargets
            if value.coordinate == coordinate
            and value.call_ordinal == call_ordinal
        ]
        if current_target == 1193:
            require(
                not existing or existing[0].new_target == 1193,
                f"unexpected chained empty retarget at {coordinate}",
            )
            return
        require(
            len(existing) <= 1,
            f"duplicate retarget at {coordinate} call {call_ordinal}",
        )
        old_target = current_target
        if existing:
            require(
                existing[0].new_target == current_target,
                f"provisional target drift at {coordinate} "
                f"call {call_ordinal}",
            )
            old_target = existing[0].old_target
            retargets = [
                value for value in retargets
                if not (
                    value.coordinate == coordinate
                    and value.call_ordinal == call_ordinal
                )
            ]
        add_retarget(
            retargets,
            coordinate=coordinate,
            call_ordinal=call_ordinal,
            old_target=old_target,
            new_target=1193,
            rule="reviewed_morph_pair_canonical_form",
        )

    # The name selector may end in a vowel or consonant; a comma is an
    # allomorph-neutral vocative boundary.
    set_literal(
        (2, 607),
        0,
        ", 언제나 배웅해 줘서 고맙다\n"
        "싸움의 승리를 그대에게 바치마",
        "reviewed_morph_pair_name_vocative",
    )

    for coordinate in sorted(CALL_QA.BASE_MORPH_PAIR_CONTRACT):
        if coordinate in morph_allowlist_coordinates or coordinate == (2, 607):
            continue
        record = morph_records[coordinate]
        components = SURFACE_QA.tolerant_decode_record(record)
        if any(component["kind"] == "jump" for component in components):
            continue
        call_components = [
            component
            for component in components
            if component["kind"] == "call"
        ]
        if not call_components:
            continue
        record_literals = parse_record_literals(record)
        literal_values = {
            literal.literal_id: literal.text
            for literal in record_literals
        }
        interval = 0
        interval_chunks: dict[int, str] = {0: ""}
        interval_slots: dict[int, list[int]] = {0: []}
        flattened_call_ordinals: list[tuple[int, int]] = []
        persona_following_intervals: set[int] = set()
        dynamic_following_intervals: set[int] = set()
        clan_following_intervals: set[int] = set()
        call_ordinal = -1
        for component in components:
            kind = str(component["kind"])
            if kind == "literal_boundary":
                literal_id = int(component["slot"])
                interval_slots.setdefault(interval, []).append(literal_id)
                interval_chunks[interval] = (
                    interval_chunks.get(interval, "")
                    + literal_values[literal_id]
                )
                continue
            if kind == "call":
                call_ordinal += 1
                target = int(component["target"][1])
                variants = morph_renderer.render(tuple(component["target"]))
                substantive = (
                    int(component["target"][0]) != 0
                    or target in substantive_call_targets
                    or any(
                        CALL_QA.UNKNOWN_OUTPUT_SELECTOR_SENTINEL in variant
                        for variant in variants
                    )
                )
                if not substantive:
                    interval_chunks[interval] = (
                        interval_chunks.get(interval, "")
                        + variants[0]
                    )
                    flattened_call_ordinals.append(
                        (call_ordinal, target)
                    )
                    continue
            # Preserve selectors, substantive calls, output controls, and VM
            # operators at their exact structural position.
            interval += 1
            interval_chunks.setdefault(interval, "")
            interval_slots.setdefault(interval, [])

        for interval_id in sorted(interval_chunks):
            chunk = repair_reviewed_morph_text(
                interval_chunks[interval_id]
            )
            slots = interval_slots[interval_id]
            require(
                not chunk or slots,
                f"morph span has no literal carrier at {coordinate} "
                f"interval {interval_id}",
            )
            if not slots:
                continue
            set_literal(
                coordinate,
                slots[0],
                chunk,
                "reviewed_morph_pair_canonical_form",
            )
            for literal_id in slots[1:]:
                set_literal(
                    coordinate,
                    literal_id,
                    "",
                    "reviewed_morph_pair_canonical_form",
                )
        for call_ordinal, target in flattened_call_ordinals:
            replace_retarget_with_empty(
                coordinate,
                call_ordinal,
                target,
            )

    set_literal(
        (6, 3859),
        0,
        "\n막부의 사자로서 ",
        "reviewed_morph_pair_dynamic_name_boundary",
    )
    set_literal(
        (7, 2533),
        0,
        "일번창은 바로 ",
        "reviewed_morph_pair_dynamic_name_copula",
    )
    set_literal(
        (7, 2533),
        1,
        "이다\n다케다 기마대의 용맹을\n똑똑히 깨달았으리라",
        "reviewed_morph_pair_dynamic_name_copula",
    )
    set_literal(
        (7, 792),
        0,
        "(내 영지를 지켜 주지 못했다는 말인가……\n"
        " 우리 가문의 힘도 알 만하군……)",
        "reviewed_morph_pair_exact_sentence",
    )
    set_literal((7, 792), 1, "", "reviewed_morph_pair_exact_sentence")
    set_literal((7, 792), 2, "", "reviewed_morph_pair_exact_sentence")
    set_literal(
        (15, 357),
        0,
        "님을 찾아냈습니다. 그러나\n"
        "사관 권유는 거절당해 버렸습니다\n"
        "설득하지 못해 송구합니다",
        "reviewed_morph_pair_exact_sentence",
    )
    set_literal(
        (15, 1524),
        0,
        "근방에 유망한 자는 있지 않았습니다\n"
        "더 넓은 인맥을 지닌 자라면\n"
        "찾아낼 수 있을지도 모릅니다",
        "reviewed_morph_pair_exact_sentence",
    )

    post_morph_blob = apply_plan(
        source_blob,
        {
            coordinate: replacements[coordinate]
            for coordinate in changed
        },
        tuple(retargets),
    )
    post_morph_records = records_from_blob(post_morph_blob)
    post_morph_renderer = CALL_QA.SyntheticSelectorRenderer(
        post_morph_records
    )
    post_morph_audit = audit_blob(post_morph_blob, include_text=True)
    post_coordinates = {
        (issue.block_id, issue.record_id)
        for issue in post_morph_audit.issues
        if issue.category == "post_canonical_high_confidence_collision"
    }
    for coordinate in sorted(post_coordinates):
        record = post_morph_records[coordinate]
        components = SURFACE_QA.tolerant_decode_record(record)
        if any(component["kind"] == "jump" for component in components):
            continue
        if not any(component["kind"] == "call" for component in components):
            # Literal-only rows are handled by the same static span rewrite.
            for literal in parse_record_literals(record):
                set_literal(
                    coordinate,
                    literal.literal_id,
                    repair_reviewed_morph_text(literal.text),
                    "post_canonical_high_confidence_form",
                )
            continue
        record_literals = parse_record_literals(record)
        literal_values = {
            literal.literal_id: literal.text
            for literal in record_literals
        }
        interval = 0
        interval_chunks: dict[int, str] = {0: ""}
        interval_slots: dict[int, list[int]] = {0: []}
        flattened_call_ordinals: list[tuple[int, int]] = []
        persona_following_intervals: set[int] = set()
        call_ordinal = -1
        for component in components:
            kind = str(component["kind"])
            if kind == "literal_boundary":
                literal_id = int(component["slot"])
                interval_slots.setdefault(interval, []).append(literal_id)
                interval_chunks[interval] = (
                    interval_chunks.get(interval, "")
                    + literal_values[literal_id]
                )
                continue
            if kind == "call":
                call_ordinal += 1
                target = int(component["target"][1])
                variants = post_morph_renderer.render(
                    tuple(component["target"])
                )
                substantive = (
                    int(component["target"][0]) != 0
                    or target in substantive_call_targets
                    or any(
                        CALL_QA.UNKNOWN_OUTPUT_SELECTOR_SENTINEL in variant
                        for variant in variants
                    )
                )
                if not substantive:
                    interval_chunks[interval] = (
                        interval_chunks.get(interval, "")
                        + variants[0]
                    )
                    flattened_call_ordinals.append(
                        (call_ordinal, target)
                    )
                    continue
                if (
                    target in {1, 8, 17, 21, 29, 37}
                    and interval_chunks.get(interval, "").endswith(
                        (
                            "에게",
                            "에",
                            "로",
                            "부터",
                            "분명",
                            "그야말로",
                            "기세로",
                            "앞으로도",
                            "부디",
                            "뒷일은",
                            "이곳은",
                            "외람되오나",
                        )
                    )
                ):
                    interval_chunks[interval] += " "
            interval += 1
            interval_chunks.setdefault(interval, "")
            interval_slots.setdefault(interval, [])
            if kind == "call" and target == 1:
                persona_following_intervals.add(interval)
            if kind == "selector" or (
                kind == "call"
                and any(
                    CALL_QA.UNKNOWN_OUTPUT_SELECTOR_SENTINEL in variant
                    for variant in variants
                )
            ):
                dynamic_following_intervals.add(interval)
            if (
                kind == "selector"
                and int(component["group"]) == 4
                and int(component.get("property") or -1) == 0x32
            ):
                clan_following_intervals.add(interval)

        for interval_id in sorted(interval_chunks):
            chunk = repair_reviewed_morph_text(
                interval_chunks[interval_id]
            )
            if (
                interval_id in persona_following_intervals
                and chunk.startswith(("따위", "같은"))
            ):
                chunk = " " + chunk
            if (
                interval_id in persona_following_intervals
                and chunk.startswith("\n에게")
            ):
                chunk = chunk[1:]
            if (
                interval_id in dynamic_following_intervals
                and chunk.startswith(("공략", "침공", "방어", "구원"))
            ):
                chunk = " " + chunk
            if (
                interval_id in clan_following_intervals
                and chunk.startswith("로부터")
            ):
                chunk = "으로부터" + chunk[len("로부터"):]
            slots = interval_slots[interval_id]
            require(
                not chunk or slots,
                f"post-canonical span has no literal carrier at "
                f"{coordinate} interval {interval_id}",
            )
            if not slots:
                continue
            set_literal(
                coordinate,
                slots[0],
                chunk,
                "post_canonical_high_confidence_form",
            )
            for literal_id in slots[1:]:
                set_literal(
                    coordinate,
                    literal_id,
                    "",
                    "post_canonical_high_confidence_form",
                )
        for call_ordinal, target in flattened_call_ordinals:
            replace_retarget_with_empty(
                coordinate,
                call_ordinal,
                target,
            )

    talent_sentences = {
        1495: (
            "기개가 엿보이는 무장입니다: ",
            "\n제가 조금 지도해 드리겠습니다\n괜찮겠습니까?",
        ),
        1496: (
            "우리 가문에 인재가 있습니다: ",
            "\n외람되오나 제가 지도하고자 합니다\n괜찮겠습니까?",
        ),
        1498: (
            "우리 가문의 뛰어난 무장을 소개하겠습니다: ",
            "\n제가 비결을 전수하고 싶습니다\n괜찮겠습니까?",
        ),
        1499: (
            "아직 재능을 꽃피우지 못한 무장이 있습니다: ",
            "\n그렇다면 제가 직접 가르쳐 보도록 하지\n"
            "괜찮겠습니까?",
        ),
        1500: (
            "재주 있는 무장이 눈에 띄는군: ",
            "\n제가 요령을 조금 일러 주겠습니다\n괜찮겠습니까?",
        ),
        1501: (
            "우리 가문에 뛰어난 무장이 있군: ",
            "\n제가 조금 지도해 주겠습니다\n괜찮겠습니까?",
        ),
        1502: (
            "우리 가문을 떠받칠 뛰어난 무장입니다: ",
            "\n제가 조금이나마 가르치겠습니다\n"
            "제게 맡겨 주시겠습니까?",
        ),
        1503: (
            "힘과 재능을 갖춘 무장입니다: ",
            "\n제가 직접 지도하고자 합니다\n괜찮겠습니까?",
        ),
        1504: (
            "우리 가문에 뛰어난 무장이 있군: ",
            "\n제가 조금 지도해 주겠습니다\n괜찮겠습니까?",
        ),
    }
    for record_id, (before_name, after_name) in talent_sentences.items():
        coordinate = (15, record_id)
        record_literals = parse_record_literals(
            post_morph_records[coordinate]
        )
        set_literal(
            coordinate,
            record_literals[0].literal_id,
            before_name,
            "dynamic_talent_exact_sentence",
        )
        set_literal(
            coordinate,
            record_literals[1].literal_id,
            after_name,
            "dynamic_talent_exact_sentence",
        )
        for literal in record_literals[2:]:
            set_literal(
                coordinate,
                literal.literal_id,
                "",
                "dynamic_talent_exact_sentence",
            )
        ordinal = -1
        for component in SURFACE_QA.tolerant_decode_record(
            post_morph_records[coordinate]
        ):
            if component["kind"] != "call":
                continue
            ordinal += 1
            target = int(component["target"][1])
            if target == 1:
                replace_retarget_with_empty(
                    coordinate,
                    ordinal,
                    target,
                )
    for literal in parse_record_literals(post_morph_records[(15, 918)]):
        key = (15, 918, literal.literal_id)
        set_literal(
            (15, 918),
            literal.literal_id,
            replacements[key].replace(
                "자신이 있습니다",
                "자신 있습니다",
            ),
            "confidence_predicate_exact_sentence",
        )

    def replace_current_literal_text(
        coordinate: tuple[int, int],
        literal_id: int,
        old: str,
        new: str,
        method: str,
    ) -> None:
        key = (coordinate[0], coordinate[1], literal_id)
        value = replacements[key]
        if old not in value:
            require(
                new in value,
                f"exact post-canonical text absent at {key}: {old!r}",
            )
            return
        set_literal(
            coordinate,
            literal_id,
            value.replace(old, new),
            method,
        )

    def ensure_call_empty(
        coordinate: tuple[int, int],
        call_ordinal: int,
        source_target: int,
    ) -> None:
        existing = [
            value
            for value in retargets
            if value.coordinate == coordinate
            and value.call_ordinal == call_ordinal
        ]
        current_target = (
            existing[0].new_target if existing else source_target
        )
        replace_retarget_with_empty(
            coordinate,
            call_ordinal,
            current_target,
        )

    def ensure_call_target(
        coordinate: tuple[int, int],
        call_ordinal: int,
        source_target: int,
        target: int,
        method: str,
    ) -> None:
        existing = [
            value
            for value in retargets
            if value.coordinate == coordinate
            and value.call_ordinal == call_ordinal
        ]
        current_target = (
            existing[0].new_target if existing else source_target
        )
        require(
            current_target in {source_target, target},
            f"conflicting exact retarget at {coordinate} call "
            f"{call_ordinal}: {current_target} versus {target}",
        )
        if current_target == target:
            return
        add_retarget(
            retargets,
            coordinate=coordinate,
            call_ordinal=call_ordinal,
            old_target=source_target,
            new_target=target,
            rule=method,
        )

    # Independent post-remediation review found several sentence-level
    # defects that a local stem/call boundary rule cannot safely infer.
    # Keep these owner fixes exact and source-anchored.
    replace_current_literal_text(
        (2, 125),
        0,
        "많으셨습니다였습니다",
        "많으셨습니다",
        "post_review_duplicate_past_terminal",
    )
    set_literal(
        (2, 214),
        2,
        "의 ",
        "post_review_dynamic_activity_boundary",
    )
    replace_current_literal_text(
        (6, 4413),
        1,
        "주시길 바라",
        "주시길 바랍니다",
        "post_review_bara_terminal",
    )
    ensure_call_empty((6, 4413), 1, 190)

    set_literal(
        (6, 4425),
        0,
        "취락 장악은 제 특기입니다\n"
        "부디 이 땅은 제게 맡겨 주십시오!\n"
        "단숨에 진척시켜 보이겠습니다",
        "post_review_persona_consistent_sentence",
    )
    set_literal(
        (6, 4425),
        1,
        "",
        "post_review_persona_consistent_sentence",
    )
    ensure_call_empty((6, 4425), 0, 1)
    ensure_call_empty((6, 4425), 1, 1114)

    set_literal(
        (6, 3547),
        1,
        "의 훈공이 1위여도 괜찮을까요\n"
        "여러분, 그래서는 저를\n",
        "post_review_formal_reaction_sentence",
    )
    set_literal(
        (6, 3547),
        2,
        "따라잡을 수 없답니다",
        "post_review_formal_reaction_sentence",
    )
    set_literal(
        (6, 3547),
        3,
        "",
        "post_review_formal_reaction_sentence",
    )
    ensure_call_empty((6, 3547), 0, 1)
    ensure_call_empty((6, 3547), 1, 730)

    replace_current_literal_text(
        (6, 3843),
        2,
        "과의 전쟁은\n전쟁을 멈추시겠습니까",
        "과의 전쟁을\n멈추시겠습니까",
        "post_review_duplicate_war_object",
    )

    set_literal(
        (7, 2534),
        0,
        "이번 일번창의 영예는 내 것이로다\n",
        "post_review_persona_allomorph_sentence",
    )
    set_literal(
        (7, 2534),
        1,
        "자, 비사문천의 깃발을 내걸고\n천하에 의를 보이리라",
        "post_review_persona_allomorph_sentence",
    )
    ensure_call_empty((7, 2534), 0, 1)

    set_literal(
        (7, 2540),
        0,
        "이번 일번창의 영예는 제 것입니다\n",
        "post_review_persona_consistent_sentence",
    )
    set_literal(
        (7, 2540),
        1,
        "",
        "post_review_persona_consistent_sentence",
    )
    set_literal(
        (7, 2540),
        2,
        "무사의 자식으로서, 마음만 먹으면\n"
        "일만 대군도 물리쳐 보이겠소",
        "post_review_persona_consistent_sentence",
    )
    ensure_call_empty((7, 2540), 0, 1)
    ensure_call_empty((7, 2540), 1, 1)

    replace_current_literal_text(
        (7, 2802),
        1,
        "보내고 오합니다",
        "보내고 오겠습니다",
        "post_review_broken_return_terminal",
    )
    replace_current_literal_text(
        (8, 968),
        1,
        "막아 보이 하겠습니다",
        "막아 보이겠습니다",
        "post_review_boi_future_spacing",
    )
    replace_current_literal_text(
        (15, 898),
        1,
        "귀를 기울여",
        "귀를 기울여 ",
        "post_review_auxiliary_spacing",
    )

    set_literal(
        (15, 428),
        0,
        ", 저를 거두어 주신 은혜는\n이 ",
        "post_review_subject_object_sentence",
    )
    set_literal(
        (15, 428),
        1,
        "",
        "post_review_subject_object_sentence",
    )
    set_literal(
        (15, 428),
        2,
        ", 절대 잊지 않겠습니다\n"
        "반드시 도움이 되겠습니다!",
        "post_review_subject_object_sentence",
    )
    ensure_call_empty((15, 428), 1, 1)

    set_literal(
        (15, 1631),
        0,
        "슬슬 미처 살피지 못하는 성도\n"
        "생길 때가 된 듯합니다\n새로이 ",
        "post_review_saeroi_gundan_spacing",
    )
    set_literal(
        (15, 2396),
        1,
        "을 목표로 삼으시겠습니까?",
        "post_review_question_terminal",
    )
    set_literal(
        (15, 2396),
        2,
        "",
        "post_review_question_terminal",
    )
    ensure_call_empty((15, 2396), 0, 460)
    set_literal(
        (15, 2413),
        2,
        " ",
        "post_review_dynamic_nominal_spacing",
    )

    set_literal(
        (2, 127),
        0,
        "안심하십시오.\n새 가주 ",
        "post_review_succession_sentence",
    )
    set_literal(
        (2, 127),
        1,
        "",
        "post_review_succession_sentence",
    )
    set_literal(
        (2, 127),
        2,
        "입니다\n이번 취임을 계기로, 어떤 수를 써서라도\n"
        "가문을 번영시키겠습니다",
        "post_review_succession_sentence",
    )
    set_literal(
        (2, 127),
        3,
        "",
        "post_review_succession_sentence",
    )
    ensure_call_empty((2, 127), 1, 8)

    set_literal(
        (6, 3527),
        0,
        " 관직에 임명되었습니다\n"
        "이 정도는 해내야 하지 않겠습니까?\n"
        "그러지 않으면 다른 이들에게 얕보일 테니까요",
        "post_review_appointment_sentence",
    )
    set_literal(
        (6, 3527),
        1,
        "",
        "post_review_appointment_sentence",
    )
    set_literal(
        (6, 3527),
        2,
        "",
        "post_review_appointment_sentence",
    )
    set_literal(
        (6, 3527),
        3,
        "",
        "post_review_appointment_sentence",
    )
    ensure_call_empty((6, 3527), 0, 844)
    ensure_call_empty((6, 3527), 1, 1066)
    ensure_call_empty((6, 3527), 2, 598)

    set_literal(
        (6, 3568),
        0,
        "기대 이상의 활약을\n보여 드리겠습니다",
        "post_review_show_sentence",
    )
    ensure_call_empty((6, 3568), 0, 1054)

    set_literal(
        (6, 4558),
        0,
        "에게 우리 가문의 제안이 받아들여졌으나\n"
        "한 번 더 밀어붙일 힘이 부족한 상황입니다\n",
        "post_review_shortage_sentence",
    )
    set_literal(
        (6, 4558),
        1,
        "",
        "post_review_shortage_sentence",
    )
    set_literal(
        (6, 4558),
        2,
        "도움을 받을 수 있겠습니까?",
        "post_review_shortage_sentence",
    )
    set_literal(
        (6, 4558),
        3,
        "",
        "post_review_shortage_sentence",
    )
    ensure_call_empty((6, 4558), 1, 8)

    set_literal(
        (7, 819),
        0,
        "의 쇠퇴가 이토록 심하다니……\n"
        "이대로 계속 섬겨도 앞날은 없습니다\n"
        "충성을 바치는 것도 여기까지로 하겠습니다",
        "post_review_loyalty_sentence",
    )
    set_literal(
        (7, 819),
        1,
        "",
        "post_review_loyalty_sentence",
    )
    ensure_call_empty((7, 819), 0, 706)
    ensure_call_empty((7, 819), 1, 148)

    set_literal(
        (15, 224),
        0,
        "사람 찾기는 어려운 일이라 성패는 운에 달려 있습니다\n"
        "허나 충분히 찾아볼 가치는\n있다고 생각합니다",
        "post_review_opinion_sentence",
    )
    ensure_call_empty((15, 224), 0, 226)

    set_literal(
        (15, 1397),
        0,
        "우리 성과 같은 전선에서야말로 제 힘을 발휘할\n"
        "싸움에 능한 낭인을 알고 있습니다\n"
        "말을 걸어 보아도 좋겠지요?",
        "post_review_permission_sentence",
    )
    set_literal(
        (15, 1397),
        1,
        "",
        "post_review_permission_sentence",
    )
    set_literal(
        (15, 1397),
        2,
        "",
        "post_review_permission_sentence",
    )
    ensure_call_empty((15, 1397), 0, 178)
    ensure_call_empty((15, 1397), 1, 1036)
    ensure_call_empty((15, 1397), 2, 598)

    set_literal(
        (6, 3921),
        0,
        "좋습니다\n",
        "post_review_appointment_permission_sentence",
    )
    set_literal(
        (6, 3921),
        1,
        "",
        "post_review_appointment_permission_sentence",
    )
    set_literal(
        (6, 3921),
        2,
        " 관직을 ",
        "post_review_appointment_permission_sentence",
    )
    set_literal(
        (6, 3921),
        3,
        "에게 내리겠습니다\n막부에 대한 충근을 기대합니다",
        "post_review_appointment_permission_sentence",
    )
    set_literal(
        (6, 3921),
        4,
        "",
        "post_review_appointment_permission_sentence",
    )
    ensure_call_empty((6, 3921), 0, 598)
    ensure_call_empty((6, 3921), 2, 418)
    ensure_call_empty((6, 3921), 3, 460)

    set_literal(
        (6, 4559),
        0,
        "의 빼내기가 난항을 겪고 있습니다\n"
        "요구를 받아들이지 않으면 응하지 않을 듯합니다\n",
        "post_review_response_sentence",
    )
    set_literal(
        (6, 4559),
        1,
        "",
        "post_review_response_sentence",
    )
    set_literal(
        (6, 4559),
        2,
        "도움을 받을 수 있겠습니까?",
        "post_review_response_sentence",
    )
    set_literal(
        (6, 4559),
        3,
        "",
        "post_review_response_sentence",
    )
    ensure_call_empty((6, 4559), 2, 8)

    set_literal(
        (8, 1199),
        0,
        "제가 할 수 있는 일은 여기까지입니다\n"
        "이후 판단은 주군께 맡기고자 합니다\n"
        "그래도 괜찮겠지요?",
        "post_review_judgment_sentence",
    )
    set_literal(
        (8, 1199),
        1,
        "",
        "post_review_judgment_sentence",
    )
    set_literal(
        (8, 1199),
        2,
        "",
        "post_review_judgment_sentence",
    )
    set_literal(
        (8, 1199),
        3,
        "",
        "post_review_judgment_sentence",
    )
    ensure_call_empty((8, 1199), 0, 1)
    ensure_call_empty((8, 1199), 1, 538)
    ensure_call_empty((8, 1199), 2, 226)
    ensure_call_empty((8, 1199), 3, 1036)
    ensure_call_empty((8, 1199), 4, 598)

    set_literal(
        (15, 1507),
        1,
        " 근처에 나타난 도적 무리의\n"
        "토벌을 맡겨도 좋겠지요?",
        "post_review_subjugation_permission_sentence",
    )
    set_literal(
        (15, 1507),
        2,
        "",
        "post_review_subjugation_permission_sentence",
    )
    ensure_call_empty((15, 1507), 0, 598)

    set_literal(
        (4, 26),
        0,
        "【AI 호전도】\n타 세력의 호전도를 설정합니다\n"
        "높을수록 적국을 침공하기\n쉬워집니다",
        "post_review_ui_word_boundary",
    )

    # Signature triage marked these remaining adverb coordinates as real
    # assembly defects.  Shared surface forms use exact old/new assertions;
    # sentence-level collisions are fixed only at their reviewed leaves.
    replace_current_literal_text(
        (6, 3680), 1, "참으로", "참으로 ",
        "reviewed_adverb_boundary",
    )
    replace_current_literal_text(
        (6, 3541), 2, "넘", "넘길 ",
        "reviewed_adverb_sentence",
    )
    replace_current_literal_text(
        (7, 266), 0, "삼가제안", "삼가 제안",
        "reviewed_adverb_boundary",
    )
    replace_current_literal_text(
        (7, 876), 1, "엄중히", "엄중히 ",
        "reviewed_adverb_boundary",
    )
    replace_current_literal_text(
        (8, 397), 1, "다시", "다시 ",
        "reviewed_adverb_boundary",
    )
    replace_current_literal_text(
        (8, 758), 0, "휘쓸려", "휩쓸려",
        "reviewed_adverb_lexeme",
    )
    replace_current_literal_text(
        (8, 993), 2, "높이하겠습니다", "높이겠습니다",
        "reviewed_adverb_sentence",
    )
    replace_current_literal_text(
        (8, 278), 0, "올해는 흉작이 들", "올해는 흉작이 들었",
        "reviewed_adverb_sentence",
    )
    ensure_call_target(
        (8, 278), 0, 376, 70,
        "reviewed_adverb_sentence",
    )
    replace_current_literal_text(
        (8, 278), 1, "고려해야 하", "고려해야 ",
        "reviewed_adverb_sentence",
    )
    ensure_call_target(
        (8, 278), 1, 796, 436,
        "reviewed_adverb_sentence",
    )
    replace_current_literal_text(
        (9, 2571), 0, "저리되고", "저리 되고",
        "reviewed_adverb_boundary",
    )
    set_literal(
        (9, 3676), 0, "아군의 우세는 분명합니다",
        "reviewed_adverb_sentence",
    )
    ensure_call_empty((9, 3676), 0, 556)
    replace_current_literal_text(
        (9, 3676), 3, "방심하지 않", " 방심하지 마십시오",
        "reviewed_adverb_sentence",
    )
    ensure_call_empty((9, 3676), 2, 1102)
    set_literal(
        (9, 3676), 4, ".",
        "reviewed_adverb_sentence",
    )
    replace_current_literal_text(
        (15, 252), 3, "꼭고려", "꼭 고려",
        "reviewed_adverb_boundary",
    )
    replace_current_literal_text(
        (15, 254), 0,
        "선동의 건, 비용이 더 늘",
        "선동에 드는 비용은 더 늘어납니다",
        "reviewed_adverb_sentence",
    )
    ensure_call_empty((15, 254), 0, 436)
    replace_current_literal_text(
        (15, 254), 1, "백성에게 풀", "백성에게 풀자",
        "reviewed_adverb_sentence",
    )
    ensure_call_empty((15, 254), 1, 1150)
    replace_current_literal_text(
        (15, 267), 0, "잠시", "잠시 ",
        "reviewed_adverb_boundary",
    )
    replace_current_literal_text(
        (15, 267), 1, "맡길 수는 없", "맡길 ",
        "reviewed_adverb_sentence",
    )
    replace_current_literal_text(
        (15, 267), 3, "의 출진이 급", "의 출진이 시급합니다",
        "reviewed_adverb_sentence",
    )
    ensure_call_empty((15, 267), 3, 1084)
    replace_current_literal_text(
        (15, 1540), 0, "이제", "이제 ",
        "reviewed_adverb_boundary",
    )
    replace_current_literal_text(
        (15, 1540), 1, "야말로", "이야말로",
        "reviewed_adverb_allomorph",
    )
    replace_current_literal_text(
        (15, 1540), 2, "이루", "이루자",
        "reviewed_adverb_sentence",
    )
    ensure_call_empty((15, 1540), 1, 1150)
    replace_current_literal_text(
        (15, 1628), 1, "새로이", "새로이 ",
        "reviewed_adverb_boundary",
    )
    replace_current_literal_text(
        (15, 1898), 0, "조금만 더", "조금만 더 ",
        "reviewed_adverb_boundary",
    )
    replace_current_literal_text(
        (15, 2064), 0,
        "목표로 삼을 성은 아직",
        "목표로 삼을 성은 아직 정하지 않았",
        "reviewed_adverb_sentence",
    )
    ensure_call_target(
        (15, 2064), 0, 160, 70,
        "reviewed_adverb_sentence",
    )
    replace_current_literal_text(
        (15, 2064), 2,
        " 방책을\n시험해 볼 생각",
        " 방책을\n시험해 볼 생각입니다",
        "reviewed_adverb_sentence",
    )
    ensure_call_empty((15, 2064), 1, 1084)

    set_literal(
        (1, 18), 0,
        "감사합니다. 저는 부모의 원수를 찾아 여러 나라를 떠돌고 있습니다.",
        "reviewed_adverb_whole_sentence",
    )
    set_literal((1, 18), 1, "", "reviewed_adverb_whole_sentence")
    set_literal((1, 18), 2, "", "reviewed_adverb_whole_sentence")
    set_literal((1, 18), 3, "", "reviewed_adverb_whole_sentence")
    ensure_call_empty((1, 18), 0, 280)
    ensure_call_empty((1, 18), 1, 1)
    ensure_call_empty((1, 18), 2, 100)
    ensure_call_empty((1, 18), 3, 400)

    # Opaque dynamic-name selectors are invisible to ordinary morphology
    # tokenization.  Ghidra-backed owner tracing resolves these exact boundary
    # fragments through their leaf records.
    for coordinate, literal_id in (
        ((6, 1627), 1),
        ((6, 1628), 0),
        ((6, 1629), 0),
        ((6, 1630), 0),
        ((6, 1631), 0),
        ((6, 1633), 0),
        ((6, 1634), 0),
        ((6, 1635), 0),
        ((6, 1636), 1),
        ((6, 1637), 0),
        ((6, 1638), 0),
    ):
        replace_current_literal_text(
            coordinate,
            literal_id,
            "하고",
            "하고 ",
            "reviewed_opaque_name_left_boundary",
        )
    for coordinate, old, new in (
        ((0, 1274), "님", " 님"),
        ((0, 1285), "님", " 님"),
        ((0, 1286), "공", " 공"),
        ((0, 1208), "놈", " 놈"),
        ((0, 1251), "공", " 공"),
        ((0, 1246), "놈", " 놈"),
    ):
        replace_current_literal_text(
            coordinate,
            0,
            old,
            new,
            "reviewed_opaque_name_title_boundary",
        )
    for coordinate in ((6, 3471), (6, 3529)):
        replace_current_literal_text(
            coordinate,
            0,
            "\n과연",
            "\n과연 ",
            "reviewed_opaque_name_left_boundary",
        )
    replace_current_literal_text(
        (6, 3402),
        0,
        "안심하고주시오",
        "안심하고 주시오, ",
        "reviewed_opaque_name_vocative_boundary",
    )
    ensure_call_empty((7, 218), 0, 7)
    set_literal(
        (7, 218),
        0,
        "의 활약으로\n적장을 포박",
        "reviewed_opaque_subject_sentence",
    )

    # Bound-noun signatures are globally stable.  The coordinate/literal-id
    # tables keep the change source-free and assert the exact current token.
    for coordinate, literal_id in (
        ((6, 596), 0), ((6, 824), 1), ((6, 825), 0),
        ((6, 1546), 1), ((6, 1568), 1), ((6, 1570), 0),
        ((6, 2451), 1), ((6, 2736), 0), ((6, 3260), 1),
        ((6, 3262), 1), ((6, 3285), 0), ((6, 3288), 1),
        ((6, 4027), 1), ((6, 4030), 1), ((7, 941), 0),
        ((7, 949), 1), ((7, 951), 0), ((7, 1340), 0),
        ((7, 1653), 0), ((7, 1663), 0), ((7, 1670), 0),
        ((7, 1678), 0), ((7, 1684), 0), ((9, 808), 0),
        ((9, 1505), 0), ((9, 2672), 0),
    ):
        replace_current_literal_text(
            coordinate, literal_id, "따위", " 따위",
            "reviewed_bound_noun_boundary",
        )

    for coordinate, literal_id in (
        ((6, 629), 0), ((6, 633), 0), ((6, 639), 0),
        ((6, 1557), 0), ((6, 1563), 0), ((6, 1577), 0),
        ((6, 2722), 0), ((6, 2910), 1), ((6, 2915), 1),
        ((6, 2917), 0), ((6, 2922), 1), ((6, 2927), 1),
        ((6, 2929), 0),
    ):
        replace_current_literal_text(
            coordinate, literal_id, "놈", "의 놈",
            "reviewed_bound_noun_genitive",
        )

    for coordinate, literal_id, old, new in (
        ((9, 811), 0, "쪽", " 쪽"),
        ((2, 113), 0, "측과", " 측과"),
        ((2, 114), 0, "등과", " 등과"),
        ((15, 1805), 3, "등은", " 등은"),
        ((15, 1829), 2, "등", " 등"),
    ):
        replace_current_literal_text(
            coordinate, literal_id, old, new,
            "reviewed_bound_noun_boundary",
        )
    replace_current_literal_text(
        (15, 803), 0, "구", "구하",
        "reviewed_bound_noun_sentence",
    )
    set_literal(
        (15, 2264), 0,
        "의 성하를 번영시키기 위해서라도\n"
        "영지를 넓히려는 뜻입니다",
        "reviewed_bound_noun_whole_sentence",
    )
    set_literal(
        (15, 2264), 1, "\n검토해 주십시오",
        "reviewed_bound_noun_whole_sentence",
    )
    ensure_call_empty((15, 2264), 0, 838)
    ensure_call_empty((15, 2264), 1, 322)

    replace_current_literal_text(
        (6, 2237), 0, "같은 자", " 같은 자",
        "reviewed_noun_phrase_boundary",
    )
    replace_current_literal_text(
        (15, 2346), 1, "어쩔 수", "어쩔 수 ",
        "reviewed_noun_phrase_boundary",
    )
    replace_current_literal_text(
        (6, 3386), 0, "납득할 수", "납득할 수 없",
        "reviewed_noun_phrase_sentence",
    )
    ensure_call_target(
        (6, 3386), 0, 736, 70,
        "reviewed_noun_phrase_sentence",
    )
    replace_current_literal_text(
        (7, 2764), 0, "통과할 수", "통과할 수 없",
        "reviewed_noun_phrase_sentence",
    )
    ensure_call_target(
        (7, 2764), 0, 736, 70,
        "reviewed_noun_phrase_sentence",
    )
    set_literal(
        (7, 2764), 1, "\n일단 성으로 돌아가겠습니다",
        "reviewed_noun_phrase_whole_sentence",
    )
    ensure_call_empty((7, 2764), 1, 1078)
    replace_current_literal_text(
        (8, 327), 0, "곳이", "곳이 있습니다",
        "reviewed_noun_phrase_whole_sentence",
    )
    ensure_call_empty((8, 327), 1, 70)
    set_literal(
        (8, 327), 1,
        ". 대책을 마련한 곳은\n무사하다는 소식입니다",
        "reviewed_noun_phrase_whole_sentence",
    )
    ensure_call_empty((8, 327), 2, 700)
    set_literal((8, 327), 2, "", "reviewed_noun_phrase_whole_sentence")
    ensure_call_empty((8, 327), 3, 376)
    set_literal(
        (15, 2376), 0,
        "아직 출진할 채비를 갖추지 않았지만",
        "reviewed_noun_phrase_sentence",
    )
    ensure_call_empty((15, 2376), 0, 160)
    replace_current_literal_text(
        (15, 2376), 1, "만,", ",",
        "reviewed_noun_phrase_sentence",
    )
    replace_current_literal_text(
        (15, 2376), 2, "판단해", "판단해 ",
        "reviewed_noun_phrase_boundary",
    )
    replace_current_literal_text(
        (15, 2154), 0, "\n풍문", "\n그런 풍문이 있",
        "reviewed_noun_phrase_sentence",
    )
    ensure_call_target(
        (15, 2154), 0, 376, 70,
        "reviewed_noun_phrase_sentence",
    )
    replace_current_literal_text(
        (15, 2154), 1, "보고", "보고드리겠습니다",
        "reviewed_noun_phrase_whole_sentence",
    )
    ensure_call_empty((15, 2154), 1, 148)
    set_literal(
        (15, 2154), 2, ".", "reviewed_noun_phrase_whole_sentence",
    )
    replace_current_literal_text(
        (6, 3537), 2, "것일 뿐", "것일 뿐입니다",
        "reviewed_noun_phrase_sentence",
    )
    ensure_call_empty((6, 3537), 1, 736)
    replace_current_literal_text(
        (7, 2438), 0, "선택", "선택해 ",
        "reviewed_noun_phrase_boundary",
    )
    replace_current_literal_text(
        (15, 804), 0, "뿐", "뿐입니다",
        "reviewed_noun_phrase_sentence",
    )
    ensure_call_empty((15, 804), 0, 376)
    replace_current_literal_text(
        (8, 275), 0, "흉작", "흉작입니다",
        "reviewed_noun_phrase_sentence",
    )
    ensure_call_empty((8, 275), 1, 376)
    set_literal(
        (15, 1410), 0,
        "님을 찾아냈습니다\n"
        "우리 가문에 사관하고 싶다는 뜻이오. 어떠하오?",
        "reviewed_noun_phrase_whole_sentence",
    )
    set_literal((15, 1410), 1, "", "reviewed_noun_phrase_whole_sentence")
    set_literal((15, 1410), 2, "", "reviewed_noun_phrase_whole_sentence")
    set_literal((15, 1410), 3, "", "reviewed_noun_phrase_whole_sentence")
    set_literal((15, 1410), 4, "", "reviewed_noun_phrase_whole_sentence")
    ensure_call_empty((15, 1410), 0, 532)
    ensure_call_empty((15, 1410), 1, 556)
    ensure_call_empty((15, 1410), 2, 688)
    ensure_call_empty((15, 1410), 3, 1054)

    set_literal(
        (2, 334),
        1,
        "」란 이를\n천하의 주인으로 세우겠습니다",
        "post_review_instrumental_sentence",
    )
    ensure_call_empty((2, 334), 1, 148)

    set_literal(
        (6, 3878),
        0,
        "의 건설에 착수합시다\n"
        "우리 성하를 더욱 나은 곳으로 만들어야 합니다",
        "post_review_construction_sentence",
    )
    set_literal(
        (6, 3878),
        1,
        "",
        "post_review_construction_sentence",
    )
    ensure_call_empty((6, 3878), 0, 964)
    ensure_call_empty((6, 3878), 1, 490)

    set_literal(
        (6, 3879),
        1,
        " 시설을 건설합니다\n"
        "허투루 짓지 말고 후세에 남을 만하게 해 주십시오",
        "post_review_construction_sentence",
    )
    set_literal(
        (6, 3879),
        2,
        "",
        "post_review_construction_sentence",
    )
    ensure_call_empty((6, 3879), 0, 460)
    ensure_call_empty((6, 3879), 1, 496)

    replace_current_literal_text(
        (6, 3393),
        0,
        "뒷일은맡겨",
        "뒷일은 맡겨",
        "post_review_entrust_spacing",
    )
    set_literal(
        (6, 3393),
        2,
        " ",
        "post_review_dynamic_nominal_spacing",
    )
    set_literal(
        (6, 3396),
        0,
        "의 이름은 무겁지만 자랑스럽기도 하여\n"
        "절로 자세가 바로 서는 기분입니다\n"
        "부디, 뒷일은 맡겨 주십시오",
        "post_review_entrust_sentence",
    )
    set_literal(
        (6, 3396),
        1,
        "",
        "post_review_entrust_sentence",
    )
    ensure_call_empty((6, 3396), 0, 538)
    ensure_call_empty((6, 3396), 1, 892)
    replace_current_literal_text(
        (6, 3408),
        0,
        "뒷일은",
        "뒷일은 ",
        "post_review_entrust_spacing",
    )
    replace_current_literal_text(
        (7, 2411),
        0,
        "지원은",
        "지원은 ",
        "post_review_entrust_spacing",
    )
    replace_current_literal_text(
        (6, 3391),
        0,
        "내게",
        "내게 ",
        "post_review_entrust_spacing",
    )

    for coordinate, literal_id in (
        ((7, 2397), 0),
        ((7, 2401), 0),
        ((15, 805), 0),
    ):
        replace_current_literal_text(
            coordinate,
            literal_id,
            "을",
            "을 ",
            "post_review_command_spacing",
        )
    set_literal(
        (7, 2399),
        0,
        "을 공격하는 적은\n이제 없습니다\n"
        "앞으로의 행동을 명해 주십시오",
        "post_review_command_sentence",
    )
    set_literal(
        (7, 2399),
        1,
        "",
        "post_review_command_sentence",
    )
    ensure_call_empty((7, 2399), 0, 160)
    ensure_call_empty((7, 2399), 1, 946)

    for coordinate, literal_id in (
        ((15, 1542), 2),
        ((15, 1544), 2),
        ((15, 1546), 1),
    ):
        value = replacements[
            (coordinate[0], coordinate[1], literal_id)
        ]
        set_literal(
            coordinate,
            literal_id,
            value if value.startswith(" ") else " " + value,
            "post_review_confirm_spacing",
        )

    set_literal(
        (15, 1843),
        0,
        "에는 이름난 장수가 많지 않지만\n"
        "결코 경계를 늦춰서는 안 됩니다",
        "post_review_guard_sentence",
    )
    set_literal(
        (15, 1843),
        1,
        "",
        "post_review_guard_sentence",
    )
    ensure_call_empty((15, 1843), 0, 160)
    ensure_call_empty((15, 1843), 1, 796)

    set_literal(
        (15, 1845),
        0,
        "에는 이름난 장수가 많지 않지만\n",
        "post_review_guard_sentence",
    )
    set_literal(
        (15, 1845),
        2,
        " 등 주력 장수들에 대해서는\n"
        "결코 경계를 늦춰서는 안 됩니다",
        "post_review_guard_sentence",
    )
    ensure_call_empty((15, 1845), 0, 160)
    ensure_call_empty((15, 1845), 1, 796)

    for coordinate, literal_id in (
        ((6, 3495), 3),
        ((6, 3529), 1),
    ):
        value = replacements[
            (coordinate[0], coordinate[1], literal_id)
        ]
        set_literal(
            coordinate,
            literal_id,
            value if value.endswith(" ") else value + " ",
            "post_review_achievement_spacing",
        )
    set_literal(
        (6, 3495),
        2,
        "에…\n주군께서 이 판단을 후회하지 않도록\n"
        "지위에 부끄럽지 않은 활약을 하지 않으면",
        "post_review_achievement_sentence",
    )
    set_literal(
        (6, 3495),
        3,
        "",
        "post_review_achievement_sentence",
    )
    set_literal(
        (6, 3529),
        1,
        ", 비할 데 없다고…\n"
        "먼 나라에까지 이름을 떨칠 활약을 하지 않으면",
        "post_review_achievement_sentence",
    )

    set_literal(
        (2, 250),
        0,
        "타 가문을 설득하는 임무라면\n",
        "post_review_mission_spacing",
    )
    set_literal(
        (2, 250),
        1,
        " ",
        "post_review_mission_spacing",
    )
    replace_current_literal_text(
        (15, 2191),
        0,
        "고마운지휘",
        "고마운 지휘",
        "post_review_command_noun_spacing",
    )
    set_literal(
        (6, 3760),
        1,
        "과는\n손을 잡고 싶다고 생각합니다\n"
        "그때는 좋은 답변을 기대해도 되겠습니까…?",
        "post_review_answer_sentence",
    )
    set_literal(
        (6, 3760),
        2,
        "",
        "post_review_answer_sentence",
    )
    set_literal(
        (6, 3760),
        3,
        "",
        "post_review_answer_sentence",
    )
    ensure_call_empty((6, 3760), 0, 1084)
    ensure_call_empty((6, 3760), 1, 1156)

    set_literal(
        (1, 27),
        0,
        "이를 공략하기 어려운 성을 참으로 잘 함락했도다!",
        "post_review_castle_modifier_sentence",
    )
    set_literal(
        (1, 27),
        1,
        "",
        "post_review_castle_modifier_sentence",
    )
    ensure_call_empty((1, 27), 0, 820)
    value_2_616_1 = replacements[(2, 616, 1)]
    set_literal(
        (2, 616),
        1,
        value_2_616_1
        if value_2_616_1.startswith(" ")
        else " " + value_2_616_1,
        "post_review_person_epithet_spacing",
    )
    set_literal(
        (6, 3514),
        0,
        " 자신이 훈공 1위라 해서 놀라지 않습니다\n"
        "오히려 놀라운 것은 이처럼 아랫사람에게\n"
        "공을 세울 기회를 주신 주군의 혜안이 아니겠습니까?",
        "post_review_honorific_sentence",
    )
    set_literal(
        (6, 3514),
        1,
        "",
        "post_review_honorific_sentence",
    )
    set_literal(
        (6, 3514),
        2,
        "",
        "post_review_honorific_sentence",
    )
    ensure_call_empty((6, 3514), 1, 298)
    ensure_call_empty((6, 3514), 2, 1232)

    set_literal(
        (6, 3546),
        0,
        "정상에 올라섰습니다?\n기회를 준 ",
        "post_review_honorific_modifier_spacing",
    )
    set_literal(
        (6, 3546),
        1,
        "",
        "post_review_honorific_modifier_spacing",
    )

    set_literal(
        (6, 4145),
        0,
        "병력이 부족해 영지 확대를 바라지 않습니다\n"
        "당분간 영지 발전에 힘쓰며\n"
        "주변의 빈틈을 엿보겠습니다",
        "post_review_desire_sentence",
    )
    set_literal(
        (6, 4145),
        1,
        "",
        "post_review_desire_sentence",
    )
    ensure_call_empty((6, 4145), 0, 736)
    ensure_call_empty((6, 4145), 1, 190)

    set_literal(
        (15, 1456),
        1,
        "에 퍼뜨려\n성에 봉직하는 적장들을\n"
        "서로 의심하게 만들겠습니다",
        "post_review_rumor_sentence",
    )
    ensure_call_empty((15, 1456), 0, 1054)

    set_literal(
        (15, 1839),
        2,
        "은\n가장 위험한 상대라 하겠습니다",
        "post_review_threat_sentence",
    )
    ensure_call_empty((15, 1839), 0, 1054)
    set_literal(
        (15, 1840),
        0,
        "은 우리 가문보다 규모가 작지만\n"
        "결코 방심해서는 안 됩니다\n"
        "경계해야 할 상대입니다",
        "post_review_threat_sentence",
    )
    set_literal(
        (15, 1840),
        1,
        "",
        "post_review_threat_sentence",
    )
    ensure_call_empty((15, 1840), 0, 736)
    ensure_call_empty((15, 1840), 1, 556)

    set_literal(
        (7, 2437),
        0,
        "특별한 장애는 없을 듯합니다\n"
        "문제없이 일이 진행될 것입니다",
        "post_review_progress_sentence",
    )
    set_literal(
        (7, 2437),
        1,
        "",
        "post_review_progress_sentence",
    )
    ensure_call_empty((7, 2437), 0, 586)
    ensure_call_empty((7, 2437), 1, 598)

    set_literal(
        (15, 1468),
        1,
        " 방책은 성공했습니다\n"
        "그자의 충성이 흔들리고 있습니다\n"
        "우리가 퍼뜨린 유언비어를 철석같이 믿고 있는 듯합니다",
        "post_review_belief_sentence",
    )
    set_literal(
        (15, 1468),
        2,
        "",
        "post_review_belief_sentence",
    )
    set_literal(
        (15, 1468),
        3,
        "",
        "post_review_belief_sentence",
    )
    set_literal(
        (15, 1468),
        4,
        "",
        "post_review_belief_sentence",
    )
    ensure_call_empty((15, 1468), 0, 532)
    ensure_call_empty((15, 1468), 1, 178)
    ensure_call_empty((15, 1468), 2, 184)
    ensure_call_empty((15, 1468), 3, 592)

    set_literal(
        (15, 1542),
        1,
        "의 상황을 확인해 주십시오\n",
        "post_review_confirm_sentence",
    )
    set_literal(
        (15, 1542),
        2,
        "",
        "post_review_confirm_sentence",
    )
    set_literal(
        (15, 1542),
        3,
        "",
        "post_review_confirm_sentence",
    )
    set_literal(
        (15, 1542),
        4,
        " 방책을 제압하려면\n그 땅을 알아야 합니다",
        "post_review_confirm_sentence",
    )
    ensure_call_empty((15, 1542), 1, 406)
    ensure_call_empty((15, 1542), 2, 796)

    set_literal(
        (15, 1544),
        0,
        "대망을 앞두니 피가 끓습니다……\n"
        "우선 통치 상황을 확인해 주십시오",
        "post_review_confirm_sentence",
    )
    set_literal(
        (15, 1544),
        1,
        "",
        "post_review_confirm_sentence",
    )
    set_literal(
        (15, 1544),
        2,
        "",
        "post_review_confirm_sentence",
    )
    ensure_call_empty((15, 1544), 0, 1114)
    ensure_call_empty((15, 1544), 1, 1162)
    ensure_call_empty((15, 1544), 2, 406)

    set_literal(
        (15, 1546),
        0,
        "우리 가문의 무위라면\n모든 나라를 복속시킬 수 있을 터\n"
        "남은 세력을 확인해 주십시오",
        "post_review_confirm_sentence",
    )
    set_literal(
        (15, 1546),
        1,
        "",
        "post_review_confirm_sentence",
    )
    ensure_call_empty((15, 1546), 0, 1162)
    ensure_call_empty((15, 1546), 1, 406)

    set_literal(
        (15, 1816),
        1,
        "은\n유감스럽게도 우리 가문보다 강대하여……\n"
        "유연하게 대응해야 하겠습니다",
        "post_review_diplomacy_sentence",
    )
    ensure_call_empty((15, 1816), 0, 1054)

    set_literal(
        (15, 1831),
        0,
        "침공은 대체로 순조롭습니다\n"
        "다만, 방심하지 말고 경계해야 합니다",
        "post_review_invasion_sentence",
    )
    set_literal(
        (15, 1831),
        1,
        "",
        "post_review_invasion_sentence",
    )
    set_literal(
        (15, 1831),
        2,
        "",
        "post_review_invasion_sentence",
    )

    set_literal(
        (1, 19),
        1,
        "가 받겠습니다。",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (1, 20),
        1,
        "의 주군은 결코 흔들리지 않습니다! "
        "에잇, 그곳을 비키시오！",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (1, 21),
        0,
        "아무래도 호게호게라는 소식… 어떠한가요。",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (1, 22),
        0,
        "원군은 바라지 못합니다… 더는 손쓸 방도가 없다.",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (1, 23),
        0,
        "이제 좋겠지요。싸움을 그만두십시오。",
        "spacing_triage_exact_sentence",
    )
    replace_current_literal_text(
        (2, 131),
        0,
        "살날",
        "살 날",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (2, 615),
        0,
        "여기는 내게 맡겨 줘!\n이 화승총으로 ",
        "spacing_triage_exact_sentence",
    )
    replace_current_literal_text(
        (6, 664),
        0,
        "젊은것들",
        "젊은 것들",
        "spacing_triage_exact_sentence",
    )
    replace_current_literal_text(
        (6, 3398),
        2,
        "번영을약속",
        "번영을 약속",
        "spacing_triage_exact_sentence",
    )
    replace_current_literal_text(
        (6, 3406),
        0,
        "살날",
        "살 날",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (6, 3408),
        1,
        " ",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (6, 3408),
        3,
        " 휘하를 강대하게 키워 보이겠습니다",
        "spacing_triage_exact_sentence",
    )
    replace_current_literal_text(
        (6, 3852),
        1,
        "관직입니다만우리",
        "관직입니다만 우리",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (6, 4149),
        0,
        "상황이 바뀌어\n공략 지시를 받았습니다. 그 성을\n"
        "공격할 수 없습니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (6, 4377),
        0,
        "인원이 부족하여 현재로서는\n진행하기 어려울 듯합니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (6, 4469),
        4,
        "」은 이제 우리 가문의 적…\n최대한의 경계를 갖추겠습니다",
        "spacing_triage_exact_sentence",
    )
    replace_current_literal_text(
        (7, 1340),
        0,
        "볼만하겠구나",
        "볼 만하겠구나",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (7, 2415),
        0,
        " 부대와 우리의 힘은 거의 호각\n"
        "승패는 지휘에 달렸습니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (7, 2423),
        0,
        "과 우리의 전력은 거의 호각\n"
        "승패는 지휘에 달렸습니다\n"
        "다만 병량에는 불안이 남아 있으니 유의하시오",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (7, 2424),
        0,
        "과 우리의 전력은 거의 호각\n"
        "승패는 지휘에 달렸습니다\n"
        "하지만 적군의 병량은 충분하옵니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (7, 2425),
        0,
        "과 우리의 전력은 거의 호각\n"
        "승패는 지휘에 달렸습니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (7, 2416),
        1,
        "을 함락하기는 어려울 듯하옵니다\n"
        "주명이시라면 전력을 다해 공격하겠습니다. 하지만……",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (7, 2434),
        1,
        " 세력을 제압하러 향하겠습니다\n"
        "병량이 바닥나지 않게 주의해 주십시오",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (7, 2435),
        1,
        " 세력을 제압하러 향하겠습니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (7, 2436),
        0,
        "제가 판단하건대\n필요한 병력은 충분합니다\n"
        "직접 지시해 주십시오",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (7, 2436),
        1,
        "",
        "spacing_triage_exact_sentence",
    )
    ensure_call_empty((7, 2436), 0, 1)
    set_literal(
        (7, 2442),
        0,
        "불온한 정세입니다\n속히 진압해야 합니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (7, 2445),
        0,
        "을 공격하신다면\n직진 외에도 다른 방법이 있습니다\n"
        "제 방안도 검토해 주십시오",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (7, 2445),
        1,
        "",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (7, 2445),
        2,
        "",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (7, 2445),
        3,
        "",
        "spacing_triage_exact_sentence",
    )
    ensure_call_empty((7, 2445), 1, 1)
    replace_current_literal_text(
        (7, 2795),
        0,
        "군단에맡겨",
        "군단에 맡겨",
        "spacing_triage_exact_sentence",
    )
    replace_current_literal_text(
        (7, 2797),
        1,
        "승전보를기대",
        "승전보를 기대",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (8, 320),
        0,
        "영내에 홍수 피해를 입은 곳이 있습니다\n"
        "토지는 황폐하고 민충도 떨어졌습니다.\n"
        "주의해야 합니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (9, 3266),
        0,
        "전황은 명백한 열세입니다\n"
        "여기서는 물러날 수밖에 없겠지요…",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (9, 3274),
        0,
        ", 사로잡혔습니다…!",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (9, 3275),
        0,
        ", 사로잡혔습니다…!\n"
        "그 밖에도 행방을 알 수 없는 자가 있다고…",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (13, 113),
        0,
        "무용만큼은 자신 있으므로\n전투에서는 이 \"",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (13, 113),
        2,
        "\"에게 선봉의 소임을 맡겨 주십시오\n"
        "적을 무찔러 보이겠습니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (13, 124),
        2,
        "\"에게 선봉의 소임을 맡겨 주십시오\n"
        "적을 무찔러 보이겠습니다",
        "spacing_triage_exact_sentence",
    )
    replace_current_literal_text(
        (15, 377),
        2,
        "실행을허가",
        "실행을 허가",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1058),
        0,
        "을 서둘러 수복해야 할 듯하옵니다\n"
        "이곳은 적지와 가까우니\n빈틈을 보여서는 안 됩니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1341),
        0,
        "에게 자객을 보내겠습니까?\n",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1341),
        2,
        "의 병사들의 움직임을 봉쇄하려면\n"
        "지휘관을 노리는 것이 좋겠습니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1463),
        0,
        "의 재능은 우리 가문에 꼭 필요하니\n"
        "주군을 의심하게 만들어\n"
        "빼내기를 위한 한 수로 삼겠습니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1629),
        0,
        "본거지의 군을 대관에게 다스리게 해 보시는 것은 "
        "어떻겠소?\n임명된 자에게도\n"
        "공을 세울 좋은 기회가 될 것입니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1629),
        1,
        "",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1629),
        2,
        "",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1632),
        0,
        "많은 성을 아우르려면\n군단 편성이 반드시 필요하오니\n"
        "신설을 검토해 주시옵소서……",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1632),
        1,
        "",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1632),
        2,
        "",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1632),
        3,
        "",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 2394),
        0,
        "이렇다 할 명장은 없습니다. 하지만\n",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 2394),
        2,
        " 같은 무장 앞에서는\n방심할 수 없습니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 2373),
        0,
        "유감스럽게도 현재 우리는 열세지만\n"
        "장병은 모두 출진할 준비를 마쳤습니다\n"
        "판단은 맡기겠습니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 2378),
        0,
        "모든 군에서 채비를 마친 것은 아니지만\n"
        "이미 우리가 우세한 상태입니다\n"
        "출진 여부는 맡기겠습니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1672),
        0,
        "시간이 있다면\n꼭 논공행상에 모습을 보여 주시면\n"
        "승진한 이들도 기뻐할 것입니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1672),
        1,
        "",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1672),
        2,
        "",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1672),
        3,
        "",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 2194),
        1,
        "\n기대 이상의 성과를 ",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 313),
        0,
        "라는 낭인이\n우리 가문의 승전보를 듣고 꼭 섬기고 싶다 하니\n"
        "한 번 만나 보시는 것도 좋겠습니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 317),
        0,
        "라는 낭인이\n기세를 탄 우리 가문을 꼭 섬기고 싶다 하니\n"
        "한 번 만나 보시는 것도 좋겠습니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 427),
        0,
        "에게 권해\n우리 가문에 귀순시켰습니다!\n"
        "당장 그자를 알현시키겠습니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 801),
        0,
        "이 위협이 되어\n인근의 아군이 출병하기 어려운 모양\n"
        "하지만 백성이 들고일어나면 그들도 움직이지 못할 터",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 812),
        0,
        "에서 잇키 선동에 성공했습니다!\n"
        "진압에는 얼마간의 시간이 걸리겠습니다\n"
        "잇키에 호응하여 출진해 보는 것도 좋겠습니다",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 919),
        1,
        "의 성벽에 공작을 벌여\n"
        "그곳 공략에 도움이 되겠습니다",
        "spacing_triage_exact_sentence",
    )
    replace_current_literal_text(
        (15, 1824),
        1,
        "것으로생각",
        "것으로 생각",
        "spacing_triage_exact_sentence",
    )
    replace_current_literal_text(
        (15, 1846),
        2,
        "것으로생각",
        "것으로 생각",
        "spacing_triage_exact_sentence",
    )
    set_literal(
        (15, 1975),
        1,
        "\n일 가능성도 있습니다",
        "spacing_triage_exact_sentence",
    )

    # A large family has a comma in a literal immediately before a dynamic
    # call/selector.  The VM concatenates both pieces byte-for-byte, so the
    # separator must live in the preceding literal.  Evaluate the provisional
    # post-retarget graph and add exactly one trailing space when the next
    # emitting component starts with Hangul.
    provisional_blob = apply_plan(
        source_blob,
        {
            coordinate: replacements[coordinate]
            for coordinate in changed
        },
        tuple(retargets),
    )
    provisional_records = records_from_blob(provisional_blob)
    provisional_renderer = CALL_QA.SyntheticSelectorRenderer(
        provisional_records
    )

    def component_starts_with_hangul(
        component: Mapping[str, Any],
        literal_values: Mapping[int, str],
    ) -> tuple[bool, bool]:
        kind = str(component["kind"])
        if kind == "call":
            variants = provisional_renderer.render(
                tuple(component["target"])
            )
            visible = tuple(
                CALL_QA.normalize_visible(value).lstrip()
                for value in variants
            )
            nonempty = tuple(value for value in visible if value)
            return (
                any(CALL_QA.is_hangul(value[0]) for value in nonempty),
                bool(nonempty),
            )
        if kind == "selector":
            return True, True
        if kind == "literal_boundary":
            visible = CALL_QA.normalize_visible(
                literal_values[int(component["slot"])]
            ).lstrip()
            return (
                bool(visible) and CALL_QA.is_hangul(visible[0]),
                bool(visible),
            )
        return False, False

    for coordinate, record in sorted(provisional_records.items()):
        components = SURFACE_QA.tolerant_decode_record(record)
        candidate_literals = {
            literal.literal_id: literal.text
            for literal in parse_record_literals(record)
        }
        literal_sequence = [
            candidate_literals[literal_id]
            for literal_id in sorted(candidate_literals)
        ]
        for component_index, component in enumerate(components):
            if (
                component["kind"] == "call"
                and int(component["target"][1])
                in {1, 4, 7, 8, 17, 21, 29, 34, 37}
            ):
                previous = CALL_QA.adjacent_literal(
                    components,
                    literal_sequence,
                    component_index,
                    direction=-1,
                )
                if previous is not None:
                    literal_id, value = previous
                    visible = CALL_QA.normalize_visible(value)
                    if (
                        visible
                        and CALL_QA.is_hangul(visible[-1])
                        and not value.endswith((" ", "\n", "\t"))
                    ):
                        set_literal(
                            coordinate,
                            literal_id,
                            value + " ",
                            "dynamic_nominal_leading_spacing",
                        )

            if (
                component["kind"] == "selector"
                and int(component["group"]) == 3
                and int(component.get("property") or -1) == 0x32
            ):
                for following in components[component_index + 1:]:
                    if following["kind"] == "literal_boundary":
                        literal_id = int(following["slot"])
                        value = candidate_literals[literal_id]
                        if value.startswith(
                            ("공략", "침공", "방어", "구원")
                        ):
                            set_literal(
                                coordinate,
                                literal_id,
                                " " + value,
                                "dynamic_castle_action_spacing",
                            )
                        break
                    if following["kind"] in {"call", "selector", "jump"}:
                        break

            if component["kind"] != "literal_boundary":
                continue
            literal_id = int(component["slot"])
            value = candidate_literals[literal_id]
            if not value.endswith((",", "，")):
                continue
            starts_hangul = False
            for following in components[component_index + 1:]:
                starts_hangul, emits = component_starts_with_hangul(
                    following,
                    candidate_literals,
                )
                if emits:
                    break
            if starts_hangul:
                set_literal(
                    coordinate,
                    literal_id,
                    value + " ",
                    "dynamic_comma_boundary_spacing",
                )

    # Final empirical same-block width/line-count closure.  These coordinates
    # are already owned by the semantic call rebuild; keeping the exact
    # post-flatten text here avoids a second postprocessor and binds every
    # change into the before/after hash contract below.
    for coordinate, literal_id, value in (
        (
            (1, 11),
            0,
            "송구하지만 다음 일정이 있어, 여기서 마치겠습니다.",
        ),
        ((1, 14), 0, "힘들 때일수록 웃으십시오. "),
        ((1, 14), 1, "그러고 보니 그분께서는 "),
        (
            (1, 15),
            1,
            ". 그러한 마음가짐이야말로 중요합니다",
        ),
        ((1, 15), 2, ". 누가 한 말일까요"),
        (
            (1, 18),
            0,
            "감사합니다. 부모의 원수를 찾아 떠돌고 있습니다.",
        ),
        (
            (1, 20),
            1,
            "의 주군은 결코 흔들리지 않습니다! 에잇, 비키시오！",
        ),
        (
            (15, 1940),
            0,
            "임무는 순조롭게 진행 중입니다.\n"
            "하지만 아직 절반이 남았습니다\n완료까지 ",
        ),
        (
            (15, 1940),
            4,
            "일 정도 더 걸릴 것으로 보입니다",
        ),
    ):
        set_literal(
            coordinate,
            literal_id,
            value,
            "final_empirical_block_width_closure",
        )

    owned_replacements = {
        coordinate: replacements[coordinate]
        for coordinate in sorted(changed)
    }
    ordered_retargets = tuple(
        sorted(
            retargets,
            key=lambda value: (
                value.coordinate,
                value.call_ordinal,
                value.old_target,
                value.new_target,
            ),
        )
    )
    structure_entries: list[dict[str, Any]] = []
    for value in ordered_retargets:
        call_component_indices = [
            index
            for index, component in enumerate(
                SURFACE_QA.tolerant_decode_record(
                    source_records[value.coordinate]
                )
            )
            if component["kind"] == "call"
        ]
        component_index = call_component_indices[value.call_ordinal]
        structure_entries.append(
            {
                "coordinate":
                    f"{value.coordinate[0]}:{value.coordinate[1]}",
                "component_index": component_index,
                "old_target": f"0:{value.old_target}",
                "new_target": f"0:{value.new_target}",
                "rule": value.rule,
            }
        )
    structure_payload = "\n".join(
        f"{entry['coordinate']}:{entry['component_index']}:"
        f"{entry['old_target']}:{entry['new_target']}:{entry['rule']}"
        for entry in structure_entries
    ).encode("utf-8")
    structure_allowlist = {
        "schema":
            "nobu16.kr.base-call-assembly-structure-allowlist.v1",
        "resource": "MSG/JP/msggame.bin",
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_coordinate_count": EXPECTED_COORDINATE_COUNT,
        "source_coordinate_sha256": EXPECTED_COORDINATE_SHA256,
        "allowed_mutation_count": len(structure_entries),
        "allowed_mutation_sha256": sha256_bytes(structure_payload),
        "entries": structure_entries,
        "source_or_translation_bodies_omitted": True,
        "steam_write_performed": False,
    }
    literal_hash_entries = [
        {
            "coordinate":
                f"{coordinate[0]}:{coordinate[1]}:{coordinate[2]}",
            "before_utf16le_sha256": sha256_bytes(
                source_literals[coordinate].encode("utf-16le")
            ),
            "after_utf16le_sha256": sha256_bytes(
                owned_replacements[coordinate].encode("utf-16le")
            ),
            "methods": sorted(methods[coordinate]),
        }
        for coordinate in sorted(owned_replacements)
    ]
    literal_hash_payload = "\n".join(
        f"{entry['coordinate']}:{entry['before_utf16le_sha256']}:"
        f"{entry['after_utf16le_sha256']}:"
        f"{','.join(entry['methods'])}"
        for entry in literal_hash_entries
    ).encode("ascii")
    report = {
        "source_issue_count": len(initial.issues),
        "source_coordinate_count": len(coordinates),
        "source_coordinate_sha256": coordinate_digest(coordinates),
        "source_category_coordinate_counts": category_counts,
        "literal_replacement_count": len(owned_replacements),
        "literal_coordinate_sha256": sha256_bytes(
            "\n".join(
                f"{block_id}:{record_id}:{literal_id}"
                for block_id, record_id, literal_id
                in sorted(owned_replacements)
            ).encode("ascii")
        ),
        "retarget_count": len(ordered_retargets),
        "retarget_coordinate_sha256": sha256_bytes(
            "\n".join(
                f"{value.coordinate[0]}:{value.coordinate[1]}:"
                f"{value.call_ordinal}:{value.old_target}:{value.new_target}"
                for value in ordered_retargets
            ).encode("ascii")
        ),
        "literal_methods": {
            f"{coordinate[0]}:{coordinate[1]}:{coordinate[2]}":
                sorted(methods[coordinate])
            for coordinate in sorted(methods)
        },
        "literal_before_after_hash_contract": {
            "entry_count": len(literal_hash_entries),
            "entry_sha256": sha256_bytes(literal_hash_payload),
            "entries": literal_hash_entries,
            "source_or_translation_bodies_omitted": True,
        },
        "retargets": [
            {
                "coordinate":
                    f"{value.coordinate[0]}:{value.coordinate[1]}",
                "call_ordinal": value.call_ordinal,
                "old_target": f"0:{value.old_target}",
                "new_target": f"0:{value.new_target}",
                "rule": value.rule,
            }
            for value in ordered_retargets
        ],
        "structure_allowlist": structure_allowlist,
    }
    return owned_replacements, ordered_retargets, report


def call_bytes(target: int) -> bytes:
    return b"\x01\x43" + struct.pack("<I", target)


def patch_call_ordinal(
    payload: bytes,
    *,
    call_ordinal: int,
    old_target: int,
    new_target: int,
) -> bytes:
    positions: list[int] = []
    cursor = 0
    while True:
        found = payload.find(b"\x01\x43", cursor)
        if found < 0:
            break
        positions.append(found)
        cursor = found + 6
    require(
        call_ordinal < len(positions),
        f"call ordinal {call_ordinal} absent",
    )
    position = positions[call_ordinal]
    old = call_bytes(old_target)
    require(
        payload[position:position + 6] == old,
        f"call target drift at ordinal {call_ordinal}",
    )
    return (
        payload[:position]
        + call_bytes(new_target)
        + payload[position + 6:]
    )


def apply_plan(
    source_blob: bytes,
    replacements: Mapping[tuple[int, int, int], str],
    retargets: Sequence[Retarget],
) -> bytes:
    literal_candidate = rebuild_packed_with_literals(source_blob, replacements)
    records = records_from_blob(literal_candidate)
    by_coordinate: dict[tuple[int, int], list[Retarget]] = {}
    for retarget in retargets:
        by_coordinate.setdefault(retarget.coordinate, []).append(retarget)
    record_replacements: dict[tuple[int, int], bytes] = {}
    for coordinate, values in sorted(by_coordinate.items()):
        payload = records[coordinate].data
        for value in sorted(values, key=lambda item: item.call_ordinal):
            try:
                payload = patch_call_ordinal(
                    payload,
                    call_ordinal=value.call_ordinal,
                    old_target=value.old_target,
                    new_target=value.new_target,
                )
            except BaseCallAssemblyRemediationError as exc:
                raise BaseCallAssemblyRemediationError(
                    f"{coordinate} retarget failed: {exc}"
                ) from exc
        record_replacements[coordinate] = payload
    return rebuild_packed_msggame(literal_candidate, record_replacements)


def build(source_blob: bytes) -> tuple[bytes, dict[str, Any]]:
    replacements, retargets, report = build_plan(source_blob)
    candidate = apply_plan(source_blob, replacements, retargets)
    source_records = records_from_blob(source_blob)
    candidate_records = records_from_blob(candidate)
    require(
        source_records.keys() == candidate_records.keys(),
        "record universe changed",
    )
    owned_records = {
        coordinate[:2] for coordinate in replacements
    } | {value.coordinate for value in retargets}
    for coordinate in source_records:
        if coordinate not in owned_records:
            require(
                source_records[coordinate].data
                == candidate_records[coordinate].data,
                f"unowned record changed: {coordinate}",
            )
    final_audit = audit_blob(candidate, include_text=True)
    report.update(
        {
            "schema": SCHEMA,
            "status": "PASS" if not final_audit.issues else "FAIL",
            "source_sha256": sha256_bytes(source_blob),
            "candidate_sha256": sha256_bytes(candidate),
            "candidate_size": len(candidate),
            "final_issue_count": len(final_audit.issues),
            "final_issue_coordinates": sorted(
                {
                    f"{value.block_id}:{value.record_id}"
                    for value in final_audit.issues
                }
            ),
            "steam_write_performed": False,
        }
    )
    return candidate, report


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--structure-allowlist",
        type=Path,
        default=DEFAULT_STRUCTURE_ALLOWLIST,
    )
    args = parser.parse_args()
    candidate, report = build(args.source.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(candidate)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(canonical_json(report), encoding="utf-8")
    args.structure_allowlist.parent.mkdir(parents=True, exist_ok=True)
    args.structure_allowlist.write_text(
        canonical_json(report["structure_allowlist"]),
        encoding="utf-8",
    )
    print(
        canonical_json(
            {
                "status": report["status"],
                "source_issue_count": report["source_issue_count"],
                "final_issue_count": report["final_issue_count"],
                "candidate_sha256": report["candidate_sha256"],
                "literal_replacement_count":
                    report["literal_replacement_count"],
                "retarget_count": report["retarget_count"],
                "output": str(args.output.resolve()),
                "report": str(args.report.resolve()),
            }
        ),
        end="",
    )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
