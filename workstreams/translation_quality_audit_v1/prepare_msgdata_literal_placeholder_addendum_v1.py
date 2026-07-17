#!/usr/bin/env python3
"""Build source-gated repairs for visible literal placeholders in ``msgdata``.

This narrow audit only repairs records whose pristine PC Japanese coordinate is
an actual policy-effect/landmark-effect label while the live PC Korean text
and all PC EN/SC/TC counterparts contain the same literal placeholder.  It
uses no Switch Korean translation and no historic Korean backup.  ``--write``
creates a review JSONL below ``tmp`` only; it never writes a game resource.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
PRISTINE_JP = (
    STEAM
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
    / "MSG_PK"
    / "JP"
    / "msgdata.bin"
)
LIVE_KO = STEAM / "MSG_PK" / "JP" / "msgdata.bin"
REFERENCES = {
    language.lower(): STEAM / "MSG_PK" / language / "msgdata.bin"
    for language in ("EN", "SC", "TC")
}
TMP_ROOT = REPO / "tmp"
OUTPUT = (
    TMP_ROOT
    / "translation_quality_audit_v1"
    / "semantic"
    / "msgdata_literal_placeholder_addendum.v1.jsonl"
)


@dataclass(frozen=True)
class Candidate:
    source_text: str
    expected_ko: str
    proposed_ko: str
    anchor_id: int
    anchor_expected_ko: str
    anchor_relation: str
    rationale: str
    format_exception: str | None = None


# IDs 21640--21675 are concise policy-effect labels whose Korean/EN/SC/TC
# slots still show POLICY_EFFECT_NAME_0134--0169.  The nearby normal Korean
# policy-effect result strings are evidence anchors; where the concise source
# wording differs from its parameterized counterpart, the proposal follows
# the pristine source rather than copying unrelated detail.
CANDIDATES: dict[int, Candidate] = {
    21640: Candidate(
        "評定衆解放", "POLICY_EFFECT_NAME_0134", "평정중 해금",
        22640, "봉행의 「증설」 명령 해금",
        "평정중 기능 해금의 parameterized Korean counterpart",
        "순정 PC JP의 실제 정책 효과명 ‘評定衆解放’가 모든 PC 비일본어 경로에서 리터럴 placeholder로 남아 있다. 기존 PC 한국어의 ‘평정중’ 용어와 정상 효과명 좌표를 기준으로 복원한다.",
    ),
    21641: Candidate(
        "本拠防衛拠点解放", "POLICY_EFFECT_NAME_0135", "본거 방위 거점 해금",
        22641, "「방위 거점」 명령 해금",
        "defensive-base command Korean counterpart",
        "순정 PC JP의 본거 방위 거점 해금 효과명이 리터럴 placeholder로 노출된다. 정상 ‘방위 거점’ 한국어 효과명과 같은 용어로 복원한다.",
    ),
    21642: Candidate(
        "補給防衛拠点解放", "POLICY_EFFECT_NAME_0136", "보급·방위 거점 해금",
        22642, "「방위 거점」「보급 거점」 명령 해금",
        "supply/defensive-base command Korean counterpart",
        "순정 PC JP의 보급·방위 거점 해금 효과명이 리터럴 placeholder로 남아 있다. 정상 보급·방위 거점 한국어 용어를 사용한다.",
    ),
    21643: Candidate(
        "領地持ち忠誠", "POLICY_EFFECT_NAME_0137", "영지 보유 무장 충성",
        22643, "영지를 가진 무장의 충성%+d",
        "parameterized territory-holding officer loyalty counterpart",
        "순정 PC JP의 영지 보유 무장 충성 효과명이 placeholder로 남아 있다. 정상 parameterized 효과명과 뜻이 일치하는 짧은 한국어 라벨로 복원한다.",
    ),
    21644: Candidate(
        "領内行動の市掌握速度", "POLICY_EFFECT_NAME_0138", "영내 행동의 시 장악 속도",
        22644, "영내 행동의 시 장악 일수%+d%",
        "parameterized city-seizure-speed counterpart",
        "순정 PC JP의 영내 행동 시 장악 속도 효과명이 placeholder로 남아 있다. 정상 시 장악 효과명의 용어를 사용해 복원한다.",
    ),
    21645: Candidate(
        "領内行動で市掌握優先", "POLICY_EFFECT_NAME_0139", "영내 행동에서 시 장악 우선",
        22645, "영내 행동에서 시 장악 우선",
        "exact normal Korean counterpart",
        "순정 PC JP의 시 장악 우선 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    21646: Candidate(
        "威信に応じて部隊能力上昇", "POLICY_EFFECT_NAME_0140", "위신에 따른 부대 능력 상승",
        22646, "위신 100마다 부대 능력+1(최대 +%d)",
        "parameterized prestige-based unit-ability counterpart",
        "순정 PC JP의 위신 연동 부대 능력 효과명이 placeholder로 남아 있다. 정상 parameterized 효과명의 뜻을 보존해 복원한다.",
    ),
    21647: Candidate(
        "戦法ダメージ", "POLICY_EFFECT_NAME_0141", "전법 피해",
        22647, "전법으로 주는 피해+%d%",
        "parameterized tactic-damage counterpart",
        "순정 PC JP의 전법 피해 효과명이 placeholder로 남아 있다. 정상 전법 피해 효과명의 용어로 복원한다.",
    ),
    21648: Candidate(
        "領内行動の農村掌握速度", "POLICY_EFFECT_NAME_0142", "영내 행동의 농촌 장악 속도",
        22648, "영내 행동의 농촌 장악 일수%+d%",
        "parameterized rural-seizure-speed counterpart",
        "순정 PC JP의 영내 행동 농촌 장악 속도 효과명이 placeholder로 남아 있다. 정상 농촌 장악 효과명의 용어를 사용해 복원한다.",
    ),
    21649: Candidate(
        "領内行動で農村掌握優先", "POLICY_EFFECT_NAME_0143", "영내 행동에서 농촌 장악 우선",
        22649, "영내 행동에서 농촌 장악 우선",
        "exact normal Korean counterpart",
        "순정 PC JP의 농촌 장악 우선 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    21650: Candidate(
        "全集落掌握下商業", "POLICY_EFFECT_NAME_0144", "모든 취락 장악 시 상업",
        22699, "모든 취락 장악 중인 군 상업%+d",
        "same all-settlements-seized commerce effect family",
        "순정 PC JP의 모든 취락 장악 시 상업 효과명이 placeholder로 남아 있다. 같은 효과군의 정상 PC 한국어 라벨을 근거로 원문 의미를 보존해 복원한다.",
    ),
    21651: Candidate(
        "挟撃時攻撃", "POLICY_EFFECT_NAME_0145", "협공 시 공격",
        22651, "협공 시 부대 공격+%d",
        "parameterized pincer-attack counterpart",
        "순정 PC JP의 협공 시 공격 효과명이 placeholder로 남아 있다. 정상 협공 효과명의 용어로 복원한다.",
    ),
    21652: Candidate(
        "街道封鎖時攻撃・防御", "POLICY_EFFECT_NAME_0146", "가도 봉쇄 시 공격·방어",
        22652, "가도 봉쇄 시 부대 공격·포위+%d",
        "same road-blockade policy-effect family; proposal follows target JP attack/defense wording",
        "순정 PC JP의 가도 봉쇄 시 공격·방어 효과명이 placeholder로 남아 있다. 정상 가도 봉쇄 용어를 유지하면서 해당 좌표 원문의 공격·방어 의미를 그대로 복원한다.",
    ),
    21653: Candidate(
        "調略成功率上昇", "POLICY_EFFECT_NAME_0147", "조략 성공률 상승",
        29212, "조략 성공률 상승",
        "exact normal Korean counterpart",
        "순정 PC JP의 조략 성공률 상승 효과명이 placeholder로 남아 있다. 동일 원문의 정상 PC 한국어 좌표와 일치시켜 복원한다.",
    ),
    21654: Candidate(
        "登用時に身分低下緩和", "POLICY_EFFECT_NAME_0148", "등용 시 신분 하락 완화",
        22654, "적 무장 등용 시 신분 하락 폭 %s",
        "recruitment status-drop mitigation counterpart",
        "순정 PC JP의 등용 시 신분 하락 완화 효과명이 placeholder로 남아 있다. 정상 등용 효과명의 용어로 원문 의미를 복원한다.",
    ),
    21655: Candidate(
        "配下武将の最高位能力上昇", "POLICY_EFFECT_NAME_0149", "휘하 무장의 최고 능력 상승",
        22655, "휘하 무장의 최고 능력%+d",
        "parameterized highest-ability counterpart",
        "순정 PC JP의 휘하 무장 최고 능력 상승 효과명이 placeholder로 남아 있다. 정상 parameterized 효과명의 용어로 복원한다.",
    ),
    21656: Candidate(
        "城下施設、政策、具申等の期間短縮", "POLICY_EFFECT_NAME_0150", "성하 시설·정책·건의 등의 기간 단축",
        23156, "성하 시설·정책·건의 등의 기간 단축",
        "exact normal Korean counterpart",
        "순정 PC JP의 성하 시설·정책·건의 기간 단축 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    21657: Candidate(
        "部隊武将が一定数以上で攻撃・防御上昇", "POLICY_EFFECT_NAME_0151", "무장이 일정 수 이상인 부대의 공격·방어 상승",
        23157, "무장이 일정 수 이상인 부대의 공격·방어 상승",
        "exact normal Korean counterpart",
        "순정 PC JP의 일정 수 이상 무장 부대 공격·방어 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    21658: Candidate(
        "具申失敗時でも達成時と同様の勲功獲得", "POLICY_EFFECT_NAME_0152", "건의 실패 시에도 성공 시와 같은 공훈 획득",
        22658, "건의 실패 시에도 공훈 획득",
        "failed-submission honor counterpart",
        "순정 PC JP의 건의 실패 시 성공과 같은 공훈 획득 효과명이 placeholder로 남아 있다. 정상 건의·공훈 용어를 유지하며 원문의 성공 시 동등 보상을 복원한다.",
    ),
    21659: Candidate(
        "腰兵糧30日以下で部隊の攻撃上昇", "POLICY_EFFECT_NAME_0153", "휴대 군량 30일 이하일 때 부대 공격 상승",
        23159, "휴대 군량 30일 이하일 때 부대 공격 상승",
        "exact normal Korean counterpart",
        "순정 PC JP의 저휴대군량 시 부대 공격 상승 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    21660: Candidate(
        "交易港がある補給拠点で兵力減少なし", "POLICY_EFFECT_NAME_0154", "교역항이 있는 보급 거점에서 병력 감소 없음",
        22660, "교역항이 있는 보급 거점은 병력 감소 없음",
        "exact normal Korean counterpart apart from surface particle",
        "순정 PC JP의 교역항 보급 거점 병력 감소 없음 효과명이 placeholder로 남아 있다. 정상 PC 한국어 효과명의 뜻을 보존해 복원한다.",
    ),
    21661: Candidate(
        "交易港がある補給拠点で金銭収入減少なし", "POLICY_EFFECT_NAME_0155", "교역항이 있는 보급 거점에서 금전 수입 감소 없음",
        22661, "교역항이 있는 보급 거점은 병력과 금전 수입 감소 없음",
        "same trade-port supply-base effect family; proposal follows target JP money-income wording",
        "순정 PC JP의 교역항 보급 거점 금전 수입 감소 없음 효과명이 placeholder로 남아 있다. 정상 보급 거점 용어를 유지하면서 해당 좌표 원문의 금전 수입 의미를 복원한다.",
    ),
    21662: Candidate(
        "交易港がある城で補給兵糧収入上昇", "POLICY_EFFECT_NAME_0156", "교역항이 있는 성의 보급 군량 수입 상승",
        23162, "교역항이 있는 성의 보급 군량 수입 상승",
        "exact normal Korean counterpart",
        "순정 PC JP의 교역항 성 보급 군량 수입 상승 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    21663: Candidate(
        "味方勢力の数に応じて部隊能力上昇", "POLICY_EFFECT_NAME_0157", "아군 세력 수에 따른 부대 능력 상승",
        23163, "아군 세력 수에 따라 부대 능력 상승",
        "normal Korean counterpart with equivalent surface phrasing",
        "순정 PC JP의 아군 세력 수 연동 부대 능력 상승 효과명이 placeholder로 남아 있다. 정상 PC 한국어 효과명의 뜻을 보존해 복원한다.",
    ),
    21664: Candidate(
        "城の開発率25％ごとに部隊能力上昇", "POLICY_EFFECT_NAME_0158", "성 개발률 25%마다 부대 능력 상승",
        23164, "성 개발률 25%마다 부대 능력 상승",
        "exact normal Korean counterpart",
        "순정 PC JP의 성 개발률 25퍼센트마다 부대 능력 상승 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
        "source_fullwidth_percent_normalized_to_existing_ascii_korean",
    ),
    21665: Candidate(
        "敵視されていない隣接する勢力の信用値が毎月一定数増加", "POLICY_EFFECT_NAME_0159", "“적대”가 아닌 인접 세력의 신용이 매월 일정량 증가",
        23165, "“적대”가 아닌 인접 세력의 신용 매월 증가",
        "normal Korean counterpart with target-JP quantity restored",
        "순정 PC JP의 비적대 인접 세력 신용 월간 증가 효과명이 placeholder로 남아 있다. 정상 ‘적대’·신용 용어를 유지하고 원문의 일정량 증가를 복원한다.",
    ),
    21666: Candidate(
        "城の武将数に応じて掌握速度上昇", "POLICY_EFFECT_NAME_0160", "성의 무장 수에 따른 장악 속도 상승",
        23166, "성의 무장 수에 따라 장악 속도 상승",
        "normal Korean counterpart with equivalent surface phrasing",
        "순정 PC JP의 성 무장 수 연동 장악 속도 상승 효과명이 placeholder로 남아 있다. 정상 PC 한국어 효과명의 뜻을 보존해 복원한다.",
    ),
    21667: Candidate(
        "農村の数が増加", "POLICY_EFFECT_NAME_0161", "농촌 수 증가",
        23167, "농촌 수 증가",
        "exact normal Korean counterpart",
        "순정 PC JP의 농촌 수 증가 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    21668: Candidate(
        "市の数が増加", "POLICY_EFFECT_NAME_0162", "시 수 증가",
        23168, "시 수 증가",
        "exact normal Korean counterpart",
        "순정 PC JP의 시 수 증가 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    21669: Candidate(
        "市の商業増加", "POLICY_EFFECT_NAME_0163", "시 상업 증가",
        23169, "시 상업 증가",
        "exact normal Korean counterpart",
        "순정 PC JP의 시 상업 증가 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    21670: Candidate(
        "水上で攻撃と防御上昇", "POLICY_EFFECT_NAME_0164", "수상에서 공격·방어 상승",
        23170, "수상에서 공격·방어 상승",
        "exact normal Korean counterpart",
        "순정 PC JP의 수상 공격·방어 상승 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    21671: Candidate(
        "一定官位以上の勢力への外交姿勢向上", "POLICY_EFFECT_NAME_0165", "일정 관위 이상인 세력의 외교 자세 향상",
        23171, "일정 관위 이상인 세력의 외교 자세 향상",
        "exact normal Korean counterpart",
        "순정 PC JP의 일정 관위 이상 세력 외교 자세 향상 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    21672: Candidate(
        "本拠で攻城戦可能", "POLICY_EFFECT_NAME_0166", "본거에서 공성전 가능",
        22672, "본거에서 공성전 가능",
        "exact normal Korean counterpart",
        "순정 PC JP의 본거 공성전 가능 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    21673: Candidate(
        "郡代/城代が集落掌握可能", "POLICY_EFFECT_NAME_0167", "군대/성대가 취락 장악 가능",
        22673, "군대/성대가 취락 장악 가능",
        "exact normal Korean counterpart",
        "순정 PC JP의 군대/성대 취락 장악 가능 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    21674: Candidate(
        "郡代/城代が設備建設可能", "POLICY_EFFECT_NAME_0168", "군대/성대가 설비 건설 가능",
        22674, "군대/성대가 설비 건설 가능",
        "exact normal Korean counterpart",
        "순정 PC JP의 군대/성대 설비 건설 가능 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    21675: Candidate(
        "郡代/城代が集落建設可能", "POLICY_EFFECT_NAME_0169", "군대/성대가 취락 건설 가능",
        22675, "군대/성대가 개발 용지에 취락 건설 가능",
        "normal Korean counterpart with target-JP shorter scope retained",
        "순정 PC JP의 군대/성대 취락 건설 가능 효과명이 placeholder로 남아 있다. 정상 군대/성대·취락 용어를 유지하면서 해당 좌표 원문의 범위를 보존한다.",
    ),
    23030: Candidate(
        "最高能力60未満の武将の忠誠上昇", "POLICY_EFFECT_NAME", "최고 능력 60 미만 무장의 충성 상승",
        22530, "최고 능력 60 미만 무장 충성 %+d",
        "parameterized under-60 highest-ability loyalty counterpart",
        "순정 PC JP의 최고 능력 60 미만 무장 충성 상승 효과명이 placeholder로 남아 있다. 정상 parameterized 효과명의 용어로 복원한다.",
    ),
    23059: Candidate(
        "部隊の防御上昇", "POLICY_EFFECT_NAME", "부대 방어 상승",
        22559, "부대의 방어%+d",
        "parameterized unit-defense counterpart",
        "순정 PC JP의 부대 방어 상승 효과명이 placeholder로 남아 있다. 정상 부대 방어 효과명의 용어로 복원한다.",
    ),
    23079: Candidate(
        "防衛設備の発動頻度上昇", "POLICY_EFFECT_NAME", "방위 설비 발동 빈도 상승",
        21579, "방위 설비 발동 빈도 상승",
        "exact normal Korean counterpart",
        "순정 PC JP의 방위 설비 발동 빈도 상승 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    23085: Candidate(
        "領内問題による一揆発生率減少", "POLICY_EFFECT_NAME", "영내 문제로 인한 잇키 발생률 감소",
        23037, "영내 문제로 인한 잇키 발생률 감소",
        "exact normal Korean counterpart",
        "순정 PC JP의 영내 문제로 인한 잇키 발생률 감소 효과명이 placeholder로 남아 있다. 동일한 정상 PC 한국어 효과명으로 복원한다.",
    ),
    23088: Candidate(
        "南蛮寺の商業増加", "POLICY_EFFECT_NAME", "남만사 상업 증가",
        29199, "남만사의 상업 +%d",
        "parameterized church-commerce counterpart",
        "순정 PC JP의 남만사 상업 증가 효과명이 placeholder로 남아 있다. 정상 남만사 상업 효과명의 용어로 복원한다.",
    ),
    23089: Candidate(
        "寺の商業増加", "POLICY_EFFECT_NAME", "절 상업 증가",
        29198, "절의 상업 +%d",
        "parameterized temple-commerce counterpart",
        "순정 PC JP의 절 상업 증가 효과명이 placeholder로 남아 있다. 정상 절 상업 효과명의 용어로 복원한다.",
    ),
    23101: Candidate(
        "保守・中道主義の武将の忠誠上昇", "POLICY_EFFECT_NAME", "보수·중도주의 무장 충성 상승",
        21601, "보수·중도 무장 충성",
        "same conservative/neutral officer-loyalty effect family",
        "순정 PC JP의 보수·중도주의 무장 충성 상승 효과명이 placeholder로 남아 있다. 정상 보수·중도 무장 충성 효과명의 용어를 사용해 복원한다.",
    ),
    23106: Candidate(
        "城制圧時の集落制圧率上昇", "POLICY_EFFECT_NAME", "성 제압 시 취락 제압률 상승",
        22606, "성 제압 시의 취락 제압률%+d%",
        "parameterized settlement-seizure-rate counterpart",
        "순정 PC JP의 성 제압 시 취락 제압률 상승 효과명이 placeholder로 남아 있다. 정상 취락 제압률 효과명의 용어로 복원한다.",
    ),
    26483: Candidate(
        "威風の効果範囲が拡大", "LANDMARK_NAME_0022", "위풍의 효과 범위 확대",
        25185, "위풍",
        "normal Korean term anchor for 威風",
        "순정 PC JP의 명소 효과명 ‘威風の効果範囲が拡大’가 명소 이름 placeholder로 잘못 남아 있다. 정상 PC 한국어의 ‘위풍’ 용어와 원문 의미에 맞춰 복원한다.",
    ),
    26533: Candidate(
        "威風の効果範囲が拡大", "LANDMARKEFFECT_DESC_0022", "위풍의 효과 범위 확대",
        25185, "위풍",
        "normal Korean term anchor for 威風",
        "순정 PC JP의 명소 효과 설명 ‘威風の効果範囲が拡大’가 리터럴 description placeholder로 남아 있다. 정상 PC 한국어의 ‘위풍’ 용어와 원문 의미에 맞춰 복원한다.",
    ),
}


sys.path.insert(0, str(REPO / "tools"))
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
RUNTIME_RE = re.compile(r"\[[a-z]+\d+\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
PRIVATE_USE_RE = re.compile(r"[\ue000-\uf8ff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
JAPANESE_OR_CJK_RE = re.compile(
    r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff"
    r"\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]"
)
PLACEHOLDER_RE = re.compile(
    r"^(?:POLICY_EFFECT_NAME(?:_\d+)?|LANDMARK_NAME_\d+|LANDMARKEFFECT_DESC_\d+)$"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def load_msgdata(path: Path) -> list[str]:
    _header, raw = decompress_wrapper(path.read_bytes())
    return parse_message_table(raw).texts


def profile(text: str) -> dict[str, object]:
    return {
        "escape_tags": ESC_RE.findall(text),
        "runtime_tokens": RUNTIME_RE.findall(text),
        "printf": PRINTF_RE.findall(text),
        "newlines": re.findall(r"\r\n|\n|\r", text),
        "outer_ascii_whitespace": [
            text[: len(text) - len(text.lstrip(" \t"))],
            text[len(text.rstrip(" \t")) :],
        ],
        "private_use": PRIVATE_USE_RE.findall(text),
        "fullwidth_percent_count": text.count("％"),
        "question_mark_count": text.count("?"),
    }


def protected_profile(text: str) -> dict[str, object]:
    values = profile(text)
    return {
        key: values[key]
        for key in (
            "escape_tags",
            "runtime_tokens",
            "printf",
            "newlines",
            "outer_ascii_whitespace",
            "private_use",
        )
    }


def candidate_files() -> list[Path]:
    audit = TMP_ROOT / "translation_quality_audit_v1"
    paths = list((audit / "semantic").glob("msgdata*.jsonl"))
    paths += list((audit / "proposals").glob("msgdata*.jsonl"))
    return sorted({path.resolve() for path in paths if path.resolve() != OUTPUT.resolve()})


def read_existing_ids() -> set[int]:
    result: set[int] = set()
    for path in candidate_files():
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            row = json.loads(line)
            values = (row.get("id"), row.get("coordinate"))
            for value in values:
                try:
                    identifier = int(value)
                except (TypeError, ValueError):
                    continue
                if identifier in result:
                    # Existing source files deliberately duplicate the original
                    # Japanese-residual list in a proposal mirror.  Only target
                    # overlap matters for this addendum.
                    continue
                result.add(identifier)
    return result


def safe_output(path: Path) -> Path:
    resolved = path.resolve(strict=False)
    root = TMP_ROOT.resolve(strict=False)
    if resolved != root and root not in resolved.parents:
        raise ValueError(f"output must stay under {root}: {resolved}")
    return resolved


def atomic_write(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    jp = load_msgdata(PRISTINE_JP)
    ko = load_msgdata(LIVE_KO)
    references = {language: load_msgdata(path) for language, path in REFERENCES.items()}
    if len(jp) != len(ko) or any(len(table) != len(jp) for table in references.values()):
        raise ValueError("PC msgdata table cardinalities differ")
    if len(CANDIDATES) != 46:
        raise ValueError(f"unexpected candidate count: {len(CANDIDATES)}")
    if len(CANDIDATES) != len(set(CANDIDATES)):
        raise ValueError("candidate IDs are not unique")
    existing = read_existing_ids()
    overlapping = sorted(existing.intersection(CANDIDATES))
    if overlapping:
        raise ValueError(f"candidate IDs already appear in msgdata review files: {overlapping}")

    file_hashes = {
        "live_steam_ko": sha256_file(LIVE_KO),
        "pristine_pc_jp": sha256_file(PRISTINE_JP),
        **{language: sha256_file(path) for language, path in REFERENCES.items()},
    }
    rows: list[dict[str, object]] = []
    for identifier, candidate in sorted(CANDIDATES.items()):
        if not (0 <= identifier < len(jp) and 0 <= candidate.anchor_id < len(jp)):
            raise ValueError(f"coordinate outside msgdata table: {identifier}")
        source = jp[identifier]
        current = ko[identifier]
        if source != candidate.source_text:
            raise ValueError(f"{identifier}: pristine Japanese source gate failed: {source!r}")
        if current != candidate.expected_ko:
            raise ValueError(f"{identifier}: current Korean target gate failed: {current!r}")
        if not PLACEHOLDER_RE.fullmatch(current):
            raise ValueError(f"{identifier}: current Korean text is not the expected literal placeholder")
        if candidate.proposed_ko == current:
            raise ValueError(f"{identifier}: proposal is not an effective correction")

        reference_texts = {language: table[identifier] for language, table in references.items()}
        if any(value != current for value in reference_texts.values()):
            raise ValueError(f"{identifier}: PC reference placeholder consensus changed: {reference_texts!r}")

        anchor_ko = ko[candidate.anchor_id]
        if anchor_ko != candidate.anchor_expected_ko:
            raise ValueError(
                f"{identifier}: normal Korean anchor changed at {candidate.anchor_id}: {anchor_ko!r}"
            )
        if PLACEHOLDER_RE.fullmatch(anchor_ko) or not HANGUL_RE.search(anchor_ko):
            raise ValueError(f"{identifier}: normal Korean anchor is invalid")

        source_profile = profile(source)
        current_profile = profile(current)
        proposed_profile = profile(candidate.proposed_ko)
        anchor_profile = profile(anchor_ko)
        if protected_profile(source) != protected_profile(candidate.proposed_ko):
            raise ValueError(f"{identifier}: source/proposed protected format differs")
        if protected_profile(current) != protected_profile(candidate.proposed_ko):
            raise ValueError(f"{identifier}: placeholder/proposed protected format differs")
        if candidate.format_exception is None:
            if source_profile["fullwidth_percent_count"] != proposed_profile["fullwidth_percent_count"]:
                raise ValueError(f"{identifier}: source/proposed fullwidth percent count differs")
        elif candidate.format_exception == "source_fullwidth_percent_normalized_to_existing_ascii_korean":
            if not (
                source_profile["fullwidth_percent_count"] == 1
                and proposed_profile["fullwidth_percent_count"] == 0
                and anchor_profile["fullwidth_percent_count"] == 0
            ):
                raise ValueError(f"{identifier}: expected percent-normalization evidence changed")
        else:
            raise ValueError(f"{identifier}: unknown format exception")
        if current_profile["fullwidth_percent_count"] != proposed_profile["fullwidth_percent_count"]:
            raise ValueError(f"{identifier}: current/proposed fullwidth percent count differs")
        if current_profile["question_mark_count"] != proposed_profile["question_mark_count"]:
            raise ValueError(f"{identifier}: current/proposed question-mark count differs")
        if not HANGUL_RE.search(candidate.proposed_ko):
            raise ValueError(f"{identifier}: proposal has no Hangul")
        if JAPANESE_OR_CJK_RE.search(candidate.proposed_ko):
            raise ValueError(f"{identifier}: proposal retains Japanese/CJK text")
        if "\ufffd" in candidate.proposed_ko or "??" in candidate.proposed_ko:
            raise ValueError(f"{identifier}: proposal has a corruption marker")

        rows.append(
            {
                "id": identifier,
                "resource": "msgdata",
                "ko": current,
                "proposed_ko": candidate.proposed_ko,
                "current_hash": text_hash(current),
                "source_text": source,
                "source_text_hash": text_hash(source),
                "live_ko_file_sha256": file_hashes["live_steam_ko"],
                "pristine_jp_file_sha256": file_hashes["pristine_pc_jp"],
                "reference_file_sha256": {
                    language: file_hashes[language] for language in REFERENCES
                },
                "issue_type": "literal_placeholder_for_nonplaceholder_source",
                "rationale": candidate.rationale,
                "source_gate_validation": "exact_match",
                "current_ko_gate_validation": "exact_match",
                "pc_target_contexts": reference_texts,
                "normal_ko_counterpart": {
                    "id": candidate.anchor_id,
                    "pristine_jp": jp[candidate.anchor_id],
                    "ko": anchor_ko,
                    "relation": candidate.anchor_relation,
                },
                "placeholder_evidence": {
                    "current_ko_is_literal_placeholder": True,
                    "all_pc_reference_targets_match_same_placeholder": True,
                    "switch_korean_translation_used": False,
                    "historic_korean_backup_used": False,
                },
                "format_profile": {
                    "current_ko": current_profile,
                    "proposed_ko": proposed_profile,
                    "pristine_jp": source_profile,
                    "normal_ko_counterpart": anchor_profile,
                },
                "format_validation": {
                    "protected_source_to_proposed": "all_match",
                    "protected_current_to_proposed": "all_match",
                    "current_fullwidth_percent_to_proposed": "match",
                    "source_fullwidth_percent_exception": candidate.format_exception,
                    "current_question_mark_to_proposed": "match",
                    "hangul_present": True,
                    "no_japanese_or_cjk_residue": True,
                    "no_replacement_glyph": True,
                },
                "game_files_written": False,
            }
        )

    policy_ids = [identifier for identifier in CANDIDATES if identifier < 24000]
    landmark_ids = [identifier for identifier in CANDIDATES if identifier >= 24000]
    summary = {
        "row_count": len(rows),
        "unique_id_count": len({row["id"] for row in rows}),
        "policy_effect_placeholder_count": len(policy_ids),
        "landmark_effect_placeholder_count": len(landmark_ids),
        "ids": [row["id"] for row in rows],
        "source_gates": "all_exact_match",
        "current_ko_gates": "all_exact_match",
        "pc_reference_placeholder_consensus": "all_exact_match",
        "normal_ko_anchor_gates": "all_exact_match",
        "existing_msgdata_candidate_overlap": "none",
        "switch_korean_translation_used": False,
        "historic_korean_backup_used": False,
        "game_files_written": False,
        "json_encoding": "ensure_ascii_true_utf8",
    }
    return rows, summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true", help="validate only; write no files")
    parser.add_argument("--write", action="store_true", help="write review JSONL below tmp")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.validate and args.write:
        parser.error("choose either --validate or --write")
    rows, summary = build_rows()
    if args.validate:
        print(json.dumps(summary, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
        return 0
    if args.write:
        output = safe_output(args.output)
        payload = "".join(
            json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n" for row in rows
        )
        if any(byte > 0x7F for byte in payload.encode("utf-8")):
            raise ValueError("review JSONL must be ASCII-only")
        atomic_write(output, payload)
        print(
            json.dumps(
                {**summary, "output": str(output), "output_bytes": output.stat().st_size},
                ensure_ascii=True,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return 0
    for row in rows:
        print(json.dumps(row, ensure_ascii=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
