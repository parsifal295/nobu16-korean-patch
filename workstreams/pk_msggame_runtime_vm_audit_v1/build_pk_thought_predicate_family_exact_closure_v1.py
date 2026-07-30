#!/usr/bin/env python3
"""Close the PK 0:1538-1544 thought-predicate terminal family.

The predecessor is the exact in-memory merge produced by the committed
``7777aa7`` bound-terminal layer over the frozen post-honorific checkpoint.
This independent layer repairs sixty-eight displayed callers and seven shared
terminal literals, renews fifty-three already-verified rows, and promotes all
twenty-three pending members of the complete incoming closure.

Tracked reports contain only coordinates, hashes, counts, and predicates.
Translation bodies and row evidence remain below ``tmp``.  Steam is read only.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DIALOGUE_TMP = REPO / "tmp" / "pc_dialogue_full_retranslation_v0150"
OVERLAY_DIR = DIALOGUE_TMP / "decisions" / "runtime_verification_overlays"
OVERRIDE_DIR = DIALOGUE_TMP / "semantic_overrides"
BOUND_BUILDER_PATH = (
    WORKSTREAM / "build_pk_bound_terminal_family_exact_closure_v1.py"
)

DEFAULT_AUDIT_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_thought_predicate_family_exact_closure_coverage.v1.json"
)
DEFAULT_PROMOTION_OUTPUT = (
    WORKSTREAM
    / "public"
    / "pk_thought_predicate_family_exact_closure_promotion.v1.json"
)
DEFAULT_DECISION_OUTPUT = (
    OVERRIDE_DIR
    / "pk_thought_predicate_family_exact_integrated_decisions.private.v1.jsonl"
)
DEFAULT_EVIDENCE_OUTPUT = (
    OVERLAY_DIR
    / "pk_thought_predicate_family_exact_closure_evidence.private.v1.jsonl"
)

LIVE_STEAM_BASE = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin"
)
LIVE_STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

AUDIT_SCHEMA = (
    "nobu16.kr.pk-thought-predicate-family-exact-closure-coverage.v1"
)
PROMOTION_SCHEMA = (
    "nobu16.kr.pk-thought-predicate-family-exact-closure-promotion.v1"
)
EVIDENCE_SCHEMA = (
    "nobu16.kr.pk-thought-predicate-family-exact-closure-evidence-row.v1"
)
METHOD = "reversed_vm_pk_thought_predicate_family_exact_closure_analysis"
PREDECESSOR_COMMIT = "7777aa7"

EXPECTED_BOUND_BUILDER_SHA256 = (
    "FF7ADFDF6A6A1566A76286977042738E564C0B86CC8F3ADC1F86C33876E583E7"
)
EXPECTED_PREDECESSOR_ROWS = 52_803
EXPECTED_PREDECESSOR_PENDING = 8_641
EXPECTED_POST_LAYER_PENDING = 8_618
EXPECTED_TRANSLATION_OVERRIDES = 75
EXPECTED_DISPLAY_CALLERS = 69
EXPECTED_DISPLAY_ASSEMBLIES = 483
EXPECTED_DISPLAY_CLOSURE_ROWS = 76
EXPECTED_PENDING_ELIGIBLE_ROWS = 23
EXPECTED_VERIFIED_RENEWAL_ROWS = 53
EXPECTED_REJECTED_ROWS = 0
EXPECTED_PK_PREDECESSOR_CANDIDATE_SHA256 = (
    "902CD3A1372BC19ABCA846C6A9F43195085C0782994ECFCE8A8353B2F9E0A628"
)
EXPECTED_PK_CANDIDATE_SHA256 = (
    "174E3BDBA63E38782531ADBF864FA95FFB75823A679DAC029594FFF1D66F23F4"
)
EXPECTED_OVERRIDE_COORDINATE_SHA256 = (
    "44910093D3966EA9D1B60B55AE0211BD14B1AFAE624DF23523D8C6FDD4A12630"
)
EXPECTED_OVERRIDE_RECORD_SHA256 = (
    "22B4105C06B8FA3B0D950B00298BA21E11E869CE86B02D0D42CB48800AFF754D"
)
EXPECTED_DISPLAY_COORDINATE_SHA256 = (
    "C6F2E2F7586CCD5863A832D05EBEDB479C183C8103A2C4C6FD34DA8D7B342738"
)
EXPECTED_DISPLAY_RECORD_SHA256 = (
    "A3A1248C209E1D84F389D1C656176AAC68BFE38EBF36FA67EE53945AD61361ED"
)
EXPECTED_PENDING_COORDINATE_SHA256 = (
    "7AC0764A958A0D994099C74F1786B29462E3D59FEE00907D25220808B45D462F"
)
EXPECTED_PENDING_RECORD_SHA256 = (
    "87AA79659AA44C0D1AC82817869B3EFF14B259415B62B000D22E5E0A445B1D26"
)
EXPECTED_RENEWAL_COORDINATE_SHA256 = (
    "FD51975BCCC485F80DB24F996E09182D3656D4F012D835B791E3C69B36FA2C0B"
)
EXPECTED_RENEWAL_RECORD_SHA256 = (
    "BD8D3EF9B86EE5C8946E7733BD6CF475C552C9DE5539F26AE26D026A0CEA543D"
)
EXPECTED_ASSEMBLY_MANIFEST_SHA256 = (
    "93F1F8B14FE43A05943BE9828D3A6ECC19BA570140ABBB5BB2DA930CA99C440A"
)
EXPECTED_OVERRIDE_MANIFEST_SHA256 = (
    "3E7A5694DE3EC10BF7969FF0A3DDF6AAA3F0EC47937996EDBE7E6669E034D144"
)
EXPECTED_PREDECESSOR_MERGED_SHA256 = (
    "AA220819FE9B2F8FBF53FBB3728A73A0A30E9422F82A70F721B54F173B57A34E"
)
EXPECTED_AUDIT_PAYLOAD_SHA256 = (
    "BF7EC8A09E119A1B710122573F3583FBCB312B7D79DBB6AFF4D015B9E1F75E91"
)
EXPECTED_AUDIT_FILE_SHA256 = (
    "9B1553E359CAA26627C02058EBE594BFCCB2EB628E2F6F6C5097792E9A37FB69"
)
EXPECTED_PROMOTION_FILE_SHA256 = (
    "624C93B1DE92A25B9D7ECBD0A0B0A3AE549A754ADAAF92ABC977896BA25C9F47"
)
EXPECTED_DECISION_FILE_SHA256 = (
    "5D516DBC69F8E78BC07E78C3BA032DEC68941E453DA687F6CD46E757C70333BD"
)
EXPECTED_EVIDENCE_FILE_SHA256 = (
    "76722DBB632D9CBB78C5BE089C18BDA8AD66C79C8A302B79DBE7DA9C03F32399"
)

CALL_RE = re.compile(b"\x01\x43(.{4})", re.DOTALL)
TARGET_SELECTOR_ROOT = (0, 226)
NON_DISPLAY_CALLER = "1:15:1"
UNCHANGED_DISPLAY_CALLER = "6:4782:1"


class ThoughtPredicateError(ValueError):
    """Raised when the thought-predicate closure proof drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ThoughtPredicateError(message)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


BOUND = load_module(
    "pk_thought_predicate_bound_predecessor",
    BOUND_BUILDER_PATH,
)
HONORIFIC = BOUND.HONORIFIC
BASE_AUDIT = BOUND.BASE_AUDIT
ENGINE = BOUND.ENGINE
RESIDUAL_AUDIT = BOUND.CROSS.RESIDUAL_AUDIT


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    require(path.is_file(), f"required file is absent: {path}")
    return sha256_bytes(path.read_bytes())


def canonical_sha256(value: Any) -> str:
    return BOUND.canonical_sha256(value)


def canonical_json(value: Mapping[str, Any]) -> str:
    return BOUND.canonical_json(value)


def canonical_jsonl(rows: Iterable[Mapping[str, Any]]) -> str:
    return BOUND.canonical_jsonl(rows)


def coordinate_digest(values: Iterable[str]) -> str:
    return BOUND.coordinate_digest(values)


def record_digest_from_coordinates(values: Iterable[str]) -> str:
    roots = {
        BASE_AUDIT.parse_literal_coordinate(value)[:2]
        for value in values
    }
    return BOUND.record_digest(roots)


def row_sort_key(row: Mapping[str, Any]) -> tuple[int, int, int, int]:
    return HONORIFIC.row_sort_key(row)


def live_hash(path: Path) -> str | None:
    return HONORIFIC.live_hash(path)


def seal_report(report: Mapping[str, Any]) -> dict[str, Any]:
    return HONORIFIC.seal_report(report)


def validate_seal(report: Mapping[str, Any]) -> None:
    HONORIFIC.validate_seal(report)


TERMINAL_OVERRIDES = {
    "0:1538:0": "고 봅니다",
    "0:1539:0": "고 본다",
    "0:1540:0": "고 보옵니다",
    "0:1541:0": "고 보옵니다",
    "0:1542:0": "고 보옵니다",
    "0:1543:0": "고 보오",
    "0:1544:0": "고 보오",
}

# Suffix replacements whose predecessor retranslations already pass the actual
# current per-line envelope.  The full replacement is derived with an exact
# endswith guard.
SUFFIX_RULES = {
    "6:4398:0": ("훌륭한 방안인 듯하", "훌륭한 방안이라"),
    "6:4437:0": ("좋은 방안이라 생각하", "좋은 방안이라"),
    "6:4440:1": (
        "문제없이 실현할 수 있을 듯하",
        "문제없이 실현할 수 있다",
    ),
    "6:4454:2": ("떠나기 어렵", "떠날 수 없다"),
    "6:4468:3": ("손해 볼 일은 없을 듯하", "손해는 없다"),
    "6:4492:2": ("꼭 함께 일하고 싶", "꼭 함께하고프다"),
    "6:4496:1": ("영주로 적임일 듯하", "영주 적임자라"),
    "6:4506:0": ("참으로 황공하", "황공하다"),
    "8:353:1": (
        "민심을 위무하는 것이 좋을 듯하",
        "민심을 위무하는 게 좋다",
    ),
    "8:1004:3": ("마련할까 하", "마련한다"),
    "8:1204:0": ("온천향을 조성하고자 하", "온천향을 조성한다"),
    "8:1205:0": ("대농촌으로 바꾸고자 하", "대농촌으로 바꾼다"),
    "8:1206:0": ("대시장을 건설하고자 하", "대시장을 건설한다"),
    "8:1239:1": (
        "이후의 판단은 주군께 맡기고자 하",
        "이후 판단은 주군께 맡긴다",
    ),
    "15:382:1": ("걸고자 하옵니다", "걸겠다"),
    "15:922:0": ("구멍을 내고자 하옵니다", "구멍을 내겠다"),
    "15:1355:1": ("수월하리라 생각하", "수월할 것이라"),
    "15:1384:0": ("서둘러 모으고자", "서둘러 모으겠다"),
    "15:1430:1": ("꼭 확인해 보고 싶", "꼭 확인하고프다"),
    "15:1470:0": ("뒤흔들고자", "뒤흔들겠다"),
    "15:1540:4": (
        "빼내기 교섭을 시도하고자",
        "빼내기 교섭을 시도하겠다",
    ),
    "15:1698:1": ("교섭해야 할 듯하옵니다", "교섭해야 한다"),
    "15:1831:1": ("좋은 기회라고", "좋은 기회라"),
    "15:1845:1": ("늘 주의를 기울여야 한다고", "늘 주의해야 한다"),
    "15:1876:2": ("공격하는 것이 좋을 것으로", "공격하는 게 좋다"),
    "15:1909:1": ("발령해야 한다고", "발령해야 한다"),
    "15:1999:1": ("실행할 때라고", "실행할 때라"),
    "15:2006:1": ("실행할 때라고", "실행할 때라"),
    "15:2007:1": ("실행할 때라고", "실행할 때라"),
    "15:2010:1": ("실행할 때라고", "실행할 때라"),
    "15:2015:1": ("실행할 때라고", "실행할 때라"),
    "15:2301:1": ("다시 짓고자", "다시 짓겠다"),
    "15:2302:1": ("다시 짓고자", "다시 짓겠다"),
}

# These predecessor retranslations exceeded at least one actual-current line.
# Their exact full replacements are grounded in the pristine JP meaning while
# retaining the current newline/protected structure and staying within every
# actual-current line envelope.
CURRENT_AUTHORITY_OVERRIDES = {
    "6:1559:0": (
        "와 손을 끊은 이상\n"
        "앞으로 외교가 어려워짐은 필연…\n"
        "병마를 갖춰야 할 것이라"
    ),
    "6:3511:0": (
        "상벌을 분명히 하는 것은 나라의 근본.\n"
        "공을 세운 자에게 합당한 상을 내리는 것은\n"
        "당연한 일이라"
    ),
    "6:3531:1": "을 모실 수 있게 되어\n기쁘다",
    "6:3551:1": "\n늘 이러고 싶다",
    "6:4247:0": (
        "공략을 위해\n"
        "호족을 우리 편으로 끌어들이는 것도\n"
        "한 선택이라"
    ),
    "6:4500:1": "따위는\n영주에 걸맞은 인물이라",
    "6:4875:1": "감장을 내리시니 황송하기 그지없다",
    "8:992:3": "의\n장악부터 착수해야 한다",
    "8:995:2": "에\n교류를 제안한다",
    "8:999:3": "을(를) 건설하여\n임지의 활기를 높이겠다",
    "8:1002:3": "을(를) 건설하여\n군비를 갖추겠다",
    "9:4131:1": (
        "\n성에서 가장 용맹한 자를 쓰러뜨려 적의 사기를 낮추면\n"
        "성 측도 일찍 항복할 것이라"
    ),
    "13:26:0": (
        "보다 힘 있는 상대…\n"
        "대항할 만한 힘을 기르기 위해\n"
        "우선 내정에 힘써야 한다"
    ),
    "15:227:0": (
        "사람 찾기는 어려운 일이라 성패는 운에 달렸으나\n"
        "그래도 충분히 찾아볼 가치는\n"
        "있다"
    ),
    "15:314:0": (
        "이(가) 당가에 몸을 의탁해\n"
        "사관하고 싶다 한다는데…\n"
        "꼭 맞아들여야 한다"
    ),
    "15:1068:0": "을 수복하겠다",
    "15:1236:0": (
        "의 방비를 무너뜨리고자\n"
        "땅굴 공격을 시도해\n"
        "적의 간담을 서늘케 하겠다"
    ),
    "15:1383:1": (
        "가\n"
        "당장이라도 병사를 내보내고자\n"
        "백성에게 병량을 징수하겠다"
    ),
    "15:1613:1": "공략의 가망은 희박하니\n지금이 물러날 때라",
    "15:1619:0": (
        "무사시는 반도의 중심이자 인접국도 많은 땅\n"
        "타국에 진출하는 데에도, 무사시 일대를 지배한\n"
        "의미는 크다"
    ),
    "15:1622:0": (
        "오와리는 동국과 서국의 경계에 해당하며,\n"
        "기나이도 넘볼 수 있는 요충지\n"
        "이 지역을 제압한 의의는 크다"
    ),
    "15:1626:0": (
        "옛 도읍이자, 지금도 많은 상인이 모이는\n"
        "남도를 품은 야마토국을 제압한 의미는\n"
        "크다"
    ),
    "15:1661:0": "슬슬 눈이 닿지 않는 성도\n나올 때라",
    "15:1847:2": "와는\n더 나은 관계를 쌓아야 한다",
    "15:1854:2": (
        "\n군비를 갖추면 전시에 다소 전력 차가 있어도\n"
        "뒤집기 쉽다"
    ),
    "15:1888:0": (
        "주위 세력을 보건대 당가의 전기는 멀었으니\n"
        "지금은 힘을 기를 때라"
    ),
    "15:1924:1": (
        "\n취락의 장악이나 성하 시설 등으로\n"
        "수익을 개선해야 한다"
    ),
    "15:2002:1": "허락을\n청하겠다",
    "15:2287:0": (
        "의 병사가 우리 영지를 침범한 것이 여러 번…\n"
        "그 성을 함락해 우환을 끊어야 한다"
    ),
    "15:2303:2": "시설을\n시세에 맞춰\n다시 짓겠다",
    "15:2304:2": "시설을\n시세에 맞춰\n다시 짓겠다",
    "15:2305:2": "시설을\n시세에 맞춰\n다시 짓겠다",
    "15:2373:0": "적의 다이묘는 상당한 지략가\n이번 일은 어렵다",
    "15:2374:0": "목표한 영주는 상당한 지략가\n이번 건은 어렵다",
    "15:2456:1": (
        "…\n"
        "지금까지의 공적을 감장으로 치하하면\n"
        "충성심도 높아질 것이라"
    ),
}


def load_bound_predecessor() -> tuple[
    dict[tuple[str, str], dict[str, Any]],
    bytes,
    Mapping[tuple[int, int], Any],
    dict[str, Any],
]:
    require(
        sha256_file(BOUND_BUILDER_PATH) == EXPECTED_BOUND_BUILDER_SHA256,
        "7777aa7 bound-terminal builder drifted",
    )
    (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        bundle,
    ) = BOUND.build_outputs()
    BOUND.validate_outputs(
        decision_content=decision_content,
        evidence_content=evidence_content,
        audit_content=audit_content,
        promotion_content=promotion_content,
        audit=audit,
        bundle=bundle,
    )
    generated = {
        BOUND.DEFAULT_DECISION_OUTPUT: decision_content,
        BOUND.DEFAULT_EVIDENCE_OUTPUT: evidence_content,
        BOUND.DEFAULT_AUDIT_OUTPUT: audit_content,
        BOUND.DEFAULT_PROMOTION_OUTPUT: promotion_content,
    }
    for path, content in generated.items():
        require(
            path.is_file() and path.read_text(encoding="utf-8") == content,
            f"7777aa7 predecessor output drifted: {path}",
        )
    merged = {
        key: copy.deepcopy(dict(row))
        for key, row in bundle["checkpoint_rows"].items()
    }
    delta = {
        (str(row["resource"]), str(row["coordinate"])): copy.deepcopy(row)
        for row in bundle["updated_rows"]
    }
    require(set(delta) <= set(merged), "bound-terminal delta has foreign rows")
    merged.update(delta)
    pending = [
        key for key, row in merged.items()
        if row.get("runtime_review") == "pending"
    ]
    merged_rows = sorted(merged.values(), key=row_sort_key)
    merged_content = canonical_jsonl(merged_rows)
    merged_sha256 = sha256_bytes(merged_content.encode("utf-8"))
    require(
        len(merged) == EXPECTED_PREDECESSOR_ROWS
        and len(pending) == EXPECTED_PREDECESSOR_PENDING,
        "7777aa7 predecessor row/pending universe drifted",
    )
    if EXPECTED_PREDECESSOR_MERGED_SHA256:
        require(
            merged_sha256 == EXPECTED_PREDECESSOR_MERGED_SHA256,
            "7777aa7 merged predecessor digest drifted",
        )
    predecessor_blob = bundle["analysis"]["pk_candidate_blob"]
    predecessor_records = bundle["analysis"]["pk_candidate_records"]
    require(
        sha256_bytes(predecessor_blob)
        == EXPECTED_PK_PREDECESSOR_CANDIDATE_SHA256,
        "7777aa7 PK candidate drifted",
    )
    return merged, predecessor_blob, predecessor_records, {
        "merged_private_sha256": merged_sha256,
        "bound_audit_file_sha256": sha256_bytes(
            audit_content.encode("utf-8")
        ),
        "bound_audit_payload_sha256": audit["guards"][
            "report_payload_sha256"
        ],
        "bound_promotion_file_sha256": sha256_bytes(
            promotion_content.encode("utf-8")
        ),
        "bound_decision_file_sha256": sha256_bytes(
            decision_content.encode("utf-8")
        ),
        "bound_evidence_file_sha256": sha256_bytes(
            evidence_content.encode("utf-8")
        ),
    }


def build_translation_overrides(
    predecessor_records: Mapping[tuple[int, int], Any],
) -> tuple[dict[str, str], dict[str, str]]:
    overrides: dict[str, str] = {}
    basis: dict[str, str] = {}
    for coordinate, (old_suffix, new_suffix) in SUFFIX_RULES.items():
        block, record, literal = BASE_AUDIT.parse_literal_coordinate(
            coordinate
        )
        text = BASE_AUDIT.parse_record_literals(
            predecessor_records[(block, record)]
        )[literal].text
        require(
            text.endswith(old_suffix),
            f"thought-predicate suffix predecessor drifted: {coordinate}",
        )
        overrides[coordinate] = text[: -len(old_suffix)] + new_suffix
        basis[coordinate] = text
    current_records = BASE_AUDIT.archive_records(
        BASE_AUDIT.DEFAULT_PK_CURRENT
    )[0]
    for coordinate, translation in CURRENT_AUTHORITY_OVERRIDES.items():
        block, record, literal = BASE_AUDIT.parse_literal_coordinate(
            coordinate
        )
        basis[coordinate] = BASE_AUDIT.parse_record_literals(
            current_records[(block, record)]
        )[literal].text
        overrides[coordinate] = translation
    for coordinate, translation in TERMINAL_OVERRIDES.items():
        block, record, literal = BASE_AUDIT.parse_literal_coordinate(
            coordinate
        )
        basis[coordinate] = BASE_AUDIT.parse_record_literals(
            predecessor_records[(block, record)]
        )[literal].text
        overrides[coordinate] = translation
    require(
        len(SUFFIX_RULES) == 33
        and len(CURRENT_AUTHORITY_OVERRIDES) == 35
        and len(TERMINAL_OVERRIDES) == 7
        and len(overrides) == EXPECTED_TRANSLATION_OVERRIDES,
        "thought-predicate override partition drifted",
    )
    require(
        coordinate_digest(overrides) == EXPECTED_OVERRIDE_COORDINATE_SHA256
        and record_digest_from_coordinates(overrides)
        == EXPECTED_OVERRIDE_RECORD_SHA256,
        "thought-predicate override universe drifted",
    )
    return overrides, basis


def build_candidate(
    predecessor_blob: bytes,
    overrides: Mapping[str, str],
) -> tuple[bytes, Mapping[tuple[int, int], Any]]:
    replacements = {
        BASE_AUDIT.parse_literal_coordinate(coordinate): translation
        for coordinate, translation in overrides.items()
    }
    blob = BASE_AUDIT.rebuild_packed_with_literals(
        predecessor_blob,
        replacements,
    )
    records = BASE_AUDIT.records_from_blob(blob)
    candidate_sha256 = sha256_bytes(blob)
    if EXPECTED_PK_CANDIDATE_SHA256:
        require(
            candidate_sha256 == EXPECTED_PK_CANDIDATE_SHA256,
            "thought-predicate full PK candidate drifted",
        )
    return blob, records


def discover_display_callers(
    candidate_records: Mapping[tuple[int, int], Any],
    predecessor_rows: Mapping[tuple[str, str], Mapping[str, Any]],
) -> list[str]:
    callers: list[str] = []
    for root, record in candidate_records.items():
        literals = BASE_AUDIT.parse_record_literals(record)
        for gap_index, gap in enumerate(BASE_AUDIT.literal_gaps(record)):
            targets = [
                struct.unpack("<I", match.group(1))[0]
                for match in CALL_RE.finditer(gap)
            ]
            if 226 not in targets:
                continue
            require(
                gap_index > 0 and gap_index - 1 < len(literals),
                f"0:226 call has no preceding literal: {root}",
            )
            coordinate = f"{root[0]}:{root[1]}:{gap_index - 1}"
            row = predecessor_rows.get(("pk_msggame", coordinate))
            require(row is not None, f"0:226 caller row is absent: {coordinate}")
            if row.get("runtime_review") == "not_required":
                require(
                    coordinate == NON_DISPLAY_CALLER,
                    f"unexpected non-display 0:226 caller: {coordinate}",
                )
                continue
            callers.append(coordinate)
    callers.sort(key=BASE_AUDIT.parse_literal_coordinate)
    require(
        len(callers) == EXPECTED_DISPLAY_CALLERS
        and UNCHANGED_DISPLAY_CALLER in callers,
        "displayed 0:226 caller universe drifted",
    )
    return callers


def build_analysis() -> dict[str, Any]:
    steam_before = {
        "base": live_hash(LIVE_STEAM_BASE),
        "pk": live_hash(LIVE_STEAM_PK),
    }
    (
        predecessor_rows,
        predecessor_blob,
        predecessor_records,
        predecessor_metadata,
    ) = load_bound_predecessor()
    overrides, override_basis = build_translation_overrides(
        predecessor_records
    )
    candidate_blob, candidate_records = build_candidate(
        predecessor_blob,
        overrides,
    )
    source_records = BASE_AUDIT.archive_records(
        BASE_AUDIT.DEFAULT_PK_PRISTINE
    )[0]
    current_records = BASE_AUDIT.archive_records(
        BASE_AUDIT.DEFAULT_PK_CURRENT
    )[0]
    callers = discover_display_callers(candidate_records, predecessor_rows)
    display_coordinates = set(callers) | set(TERMINAL_OVERRIDES)
    require(
        len(display_coordinates) == EXPECTED_DISPLAY_CLOSURE_ROWS
        and coordinate_digest(display_coordinates)
        == EXPECTED_DISPLAY_COORDINATE_SHA256
        and record_digest_from_coordinates(display_coordinates)
        == EXPECTED_DISPLAY_RECORD_SHA256,
        "thought-predicate display closure drifted",
    )
    require(
        set(overrides) == display_coordinates - {UNCHANGED_DISPLAY_CALLER},
        "override/display closure relation drifted",
    )

    override_manifest: list[dict[str, Any]] = []
    for coordinate in sorted(
        overrides,
        key=BASE_AUDIT.parse_literal_coordinate,
    ):
        block, record, literal = BASE_AUDIT.parse_literal_coordinate(
            coordinate
        )
        root = (block, record)
        predecessor_text = BASE_AUDIT.parse_record_literals(
            predecessor_records[root]
        )[literal].text
        current_text = BASE_AUDIT.parse_record_literals(
            current_records[root]
        )[literal].text
        candidate_text = BASE_AUDIT.parse_record_literals(
            candidate_records[root]
        )[literal].text
        basis_text = override_basis[coordinate]
        require(
            candidate_text == overrides[coordinate]
            and ENGINE.protected_signature(basis_text)
            == ENGINE.protected_signature(candidate_text)
            and ENGINE.protected_signature(current_text)
            == ENGINE.protected_signature(candidate_text)
            and ENGINE.protected_signature(predecessor_text)
            == ENGINE.protected_signature(candidate_text),
            f"thought-predicate protected signature drifted: {coordinate}",
        )
        require(
            ENGINE.record_gap_bytes(source_records[root])
            == ENGINE.record_gap_bytes(current_records[root])
            == ENGINE.record_gap_bytes(predecessor_records[root])
            == ENGINE.record_gap_bytes(candidate_records[root]),
            f"thought-predicate record gaps drifted: {coordinate}",
        )
        require(
            HONORIFIC.component_signatures(source_records[root])
            == HONORIFIC.component_signatures(current_records[root])
            == HONORIFIC.component_signatures(predecessor_records[root])
            == HONORIFIC.component_signatures(candidate_records[root]),
            f"thought-predicate VM components drifted: {coordinate}",
        )
        override_manifest.append(
            {
                "coordinate": coordinate,
                "record": [block, record],
                "predecessor_literal_utf16le_sha256": ENGINE.sha256_text(
                    predecessor_text
                ),
                "current_literal_utf16le_sha256": ENGINE.sha256_text(
                    current_text
                ),
                "candidate_literal_utf16le_sha256": ENGINE.sha256_text(
                    candidate_text
                ),
                "predecessor_record_sha256": sha256_bytes(
                    predecessor_records[root].data
                ),
                "candidate_record_sha256": sha256_bytes(
                    candidate_records[root].data
                ),
                "protected_signature_sha256": canonical_sha256(
                    ENGINE.protected_signature(candidate_text)
                ),
            }
        )
    override_manifest_sha256 = canonical_sha256(override_manifest)
    if EXPECTED_OVERRIDE_MANIFEST_SHA256:
        require(
            override_manifest_sha256 == EXPECTED_OVERRIDE_MANIFEST_SHA256,
            "thought-predicate override manifest drifted",
        )

    assembly_manifest: list[dict[str, Any]] = []
    for caller_coordinate in callers:
        block, record, literal = BASE_AUDIT.parse_literal_coordinate(
            caller_coordinate
        )
        root = (block, record)
        current_caller = BASE_AUDIT.parse_record_literals(
            current_records[root]
        )[literal].text
        candidate_caller = BASE_AUDIT.parse_record_literals(
            candidate_records[root]
        )[literal].text
        require(
            candidate_caller.endswith(("다", "라")),
            f"caller is not a 0:226 connective precursor: {caller_coordinate}",
        )
        for terminal_coordinate in sorted(
            TERMINAL_OVERRIDES,
            key=BASE_AUDIT.parse_literal_coordinate,
        ):
            t_block, t_record, t_literal = (
                BASE_AUDIT.parse_literal_coordinate(terminal_coordinate)
            )
            t_root = (t_block, t_record)
            current_terminal = BASE_AUDIT.parse_record_literals(
                current_records[t_root]
            )[t_literal].text
            candidate_terminal = BASE_AUDIT.parse_record_literals(
                candidate_records[t_root]
            )[t_literal].text
            require(
                candidate_terminal.startswith("고 "),
                f"terminal does not own connective+space: {terminal_coordinate}",
            )
            current_lines = (current_caller + current_terminal).split("\n")
            candidate_lines = (
                candidate_caller + candidate_terminal
            ).split("\n")
            require(
                len(current_lines) == len(candidate_lines),
                f"assembly line count drifted: "
                f"{caller_coordinate}->{terminal_coordinate}",
            )
            current_widths = [
                RESIDUAL_AUDIT.raw_line_widths(line)[0]
                for line in current_lines
            ]
            candidate_widths = [
                RESIDUAL_AUDIT.raw_line_widths(line)[0]
                for line in candidate_lines
            ]
            require(
                all(
                    candidate <= current
                    for current, candidate in zip(
                        current_widths,
                        candidate_widths,
                    )
                ),
                f"actual-current raw-G1N expansion: "
                f"{caller_coordinate}->{terminal_coordinate}",
            )
            assembly_manifest.append(
                {
                    "caller": caller_coordinate,
                    "terminal": terminal_coordinate,
                    "assembled_utf16le_sha256": ENGINE.sha256_text(
                        candidate_caller + candidate_terminal
                    ),
                    "current_line_widths_raw_g1n": current_widths,
                    "final_line_widths_raw_g1n": candidate_widths,
                }
            )
    require(
        len(assembly_manifest) == EXPECTED_DISPLAY_ASSEMBLIES,
        "thought-predicate assembly count drifted",
    )
    assembly_manifest_sha256 = canonical_sha256(assembly_manifest)
    require(
        assembly_manifest_sha256 == EXPECTED_ASSEMBLY_MANIFEST_SHA256,
        "thought-predicate assembly manifest drifted",
    )

    pending_coordinates = sorted(
        (
            coordinate
            for coordinate in display_coordinates
            if predecessor_rows[("pk_msggame", coordinate)].get(
                "runtime_review"
            )
            == "pending"
        ),
        key=BASE_AUDIT.parse_literal_coordinate,
    )
    renewal_coordinates = sorted(
        (
            coordinate
            for coordinate in display_coordinates
            if predecessor_rows[("pk_msggame", coordinate)].get(
                "runtime_review"
            )
            == "verified"
        ),
        key=BASE_AUDIT.parse_literal_coordinate,
    )
    require(
        len(pending_coordinates) == EXPECTED_PENDING_ELIGIBLE_ROWS
        and coordinate_digest(pending_coordinates)
        == EXPECTED_PENDING_COORDINATE_SHA256
        and record_digest_from_coordinates(pending_coordinates)
        == EXPECTED_PENDING_RECORD_SHA256,
        "thought-predicate pending eligible universe drifted",
    )
    require(
        len(renewal_coordinates) == EXPECTED_VERIFIED_RENEWAL_ROWS
        and coordinate_digest(renewal_coordinates)
        == EXPECTED_RENEWAL_COORDINATE_SHA256
        and record_digest_from_coordinates(renewal_coordinates)
        == EXPECTED_RENEWAL_RECORD_SHA256,
        "thought-predicate renewal universe drifted",
    )
    steam_after = {
        "base": live_hash(LIVE_STEAM_BASE),
        "pk": live_hash(LIVE_STEAM_PK),
    }
    require(
        steam_before == steam_after,
        "live Steam msggame changed during thought-predicate analysis",
    )
    return {
        "predecessor_rows": predecessor_rows,
        "predecessor_blob": predecessor_blob,
        "predecessor_records": predecessor_records,
        "predecessor_metadata": predecessor_metadata,
        "candidate_blob": candidate_blob,
        "candidate_records": candidate_records,
        "source_records": source_records,
        "current_records": current_records,
        "overrides": overrides,
        "override_basis": override_basis,
        "override_manifest": override_manifest,
        "override_manifest_sha256": override_manifest_sha256,
        "callers": callers,
        "display_coordinates": sorted(
            display_coordinates,
            key=BASE_AUDIT.parse_literal_coordinate,
        ),
        "assembly_manifest": assembly_manifest,
        "assembly_manifest_sha256": assembly_manifest_sha256,
        "pending_coordinates": pending_coordinates,
        "renewal_coordinates": renewal_coordinates,
        "steam_before": steam_before,
        "steam_after": steam_after,
    }


def build_audit(analysis: Mapping[str, Any]) -> dict[str, Any]:
    predecessor_metadata = analysis["predecessor_metadata"]
    report = {
        "schema": AUDIT_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "method": METHOD,
        "predecessor": {
            "git_commit": PREDECESSOR_COMMIT,
            "rows": EXPECTED_PREDECESSOR_ROWS,
            "pending_rows": EXPECTED_PREDECESSOR_PENDING,
            "pk_candidate_packed_sha256":
            EXPECTED_PK_PREDECESSOR_CANDIDATE_SHA256,
            "merged_private_sha256": predecessor_metadata[
                "merged_private_sha256"
            ],
        },
        "scope": {
            "translation_override_rows": EXPECTED_TRANSLATION_OVERRIDES,
            "displayed_caller_rows": EXPECTED_DISPLAY_CALLERS,
            "displayed_terminal_rows": len(TERMINAL_OVERRIDES),
            "displayed_closure_rows": EXPECTED_DISPLAY_CLOSURE_ROWS,
            "displayed_assembly_combinations": EXPECTED_DISPLAY_ASSEMBLIES,
            "pending_eligible_rows": EXPECTED_PENDING_ELIGIBLE_ROWS,
            "existing_verified_evidence_renewal_rows":
            EXPECTED_VERIFIED_RENEWAL_ROWS,
            "rejected_rows": EXPECTED_REJECTED_ROWS,
            "post_layer_pending_rows": EXPECTED_POST_LAYER_PENDING,
            "base_resource_renewal_rows": 0,
        },
        "guards": {
            "bound_builder_sha256": EXPECTED_BOUND_BUILDER_SHA256,
            "bound_audit_file_sha256": predecessor_metadata[
                "bound_audit_file_sha256"
            ],
            "bound_audit_payload_sha256": predecessor_metadata[
                "bound_audit_payload_sha256"
            ],
            "bound_decision_file_sha256": predecessor_metadata[
                "bound_decision_file_sha256"
            ],
            "bound_evidence_file_sha256": predecessor_metadata[
                "bound_evidence_file_sha256"
            ],
            "bound_promotion_file_sha256": predecessor_metadata[
                "bound_promotion_file_sha256"
            ],
            "pk_predecessor_candidate_packed_sha256":
            EXPECTED_PK_PREDECESSOR_CANDIDATE_SHA256,
            "pk_candidate_packed_sha256": sha256_bytes(
                analysis["candidate_blob"]
            ),
            "override_coordinate_sha256":
            EXPECTED_OVERRIDE_COORDINATE_SHA256,
            "override_record_sha256": EXPECTED_OVERRIDE_RECORD_SHA256,
            "override_manifest_sha256": analysis[
                "override_manifest_sha256"
            ],
            "display_coordinate_sha256":
            EXPECTED_DISPLAY_COORDINATE_SHA256,
            "display_record_sha256": EXPECTED_DISPLAY_RECORD_SHA256,
            "assembly_manifest_sha256":
            EXPECTED_ASSEMBLY_MANIFEST_SHA256,
            "pending_eligible_coordinate_sha256":
            EXPECTED_PENDING_COORDINATE_SHA256,
            "pending_eligible_record_sha256":
            EXPECTED_PENDING_RECORD_SHA256,
            "verified_renewal_coordinate_sha256":
            EXPECTED_RENEWAL_COORDINATE_SHA256,
            "verified_renewal_record_sha256":
            EXPECTED_RENEWAL_RECORD_SHA256,
            "rejected_coordinate_sha256": coordinate_digest([]),
            "rejected_record_sha256": BOUND.record_digest(set()),
        },
        "adjudication": {
            "descriptor_row71_body_route_reconfirmed": True,
            "descriptor_row71_body_message_id_hex": "0000EAB5",
            "descriptor_row71_body_root": "6:85",
            "selector_route": [
                "6:85",
                "6:1559",
                "0:226",
                "0:227",
                "0:1538",
            ],
            "automatic_space_inserted": False,
            "caller_owns_predicative_precursor": True,
            "terminal_owns_connective_and_register": True,
            "all_483_assemblies_grammar_complete": True,
            "all_483_assemblies_actual_current_relative_nonexpanding": True,
            "raw_g1n_full_width_px": 48,
            "raw_g1n_half_width_px": 24,
            "one_absolute_widget_gate_assumed": False,
            "pk_msgev_912px_rule_applied": False,
            "line_breaks_preserved": True,
            "control_components_preserved": True,
            "protected_signatures_preserved": True,
            "per_row_game_playback_required": False,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_contains_translation_bodies": False,
        },
        "steam_write_performed": False,
    }
    return seal_report(report)


def evidence_row(
    *,
    coordinate: str,
    predecessor: Mapping[str, Any],
    updated: Mapping[str, Any],
    action: str,
    analysis: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> dict[str, Any]:
    block, record, literal = BASE_AUDIT.parse_literal_coordinate(coordinate)
    root = (block, record)
    predecessor_text = BASE_AUDIT.parse_record_literals(
        analysis["predecessor_records"][root]
    )[literal].text
    candidate_text = BASE_AUDIT.parse_record_literals(
        analysis["candidate_records"][root]
    )[literal].text
    evidence = {
        "schema": EVIDENCE_SCHEMA,
        "resource": "pk_msggame",
        "coordinate": coordinate,
        "method": METHOD,
        "result": "verified",
        "status": "verified",
        "action": action,
        "predecessor_runtime_review": predecessor.get("runtime_review"),
        "candidate_record_raw_sha256": sha256_bytes(
            analysis["candidate_records"][root].data
        ),
        "predecessor_record_raw_sha256": sha256_bytes(
            analysis["predecessor_records"][root].data
        ),
        "current_record_raw_sha256": sha256_bytes(
            analysis["current_records"][root].data
        ),
        "predecessor_literal_utf16le_sha256": ENGINE.sha256_text(
            predecessor_text
        ),
        "candidate_literal_utf16le_sha256": ENGINE.sha256_text(
            candidate_text
        ),
        "updated_translation_utf16le_sha256": ENGINE.sha256_text(
            str(updated["translation"])
        ),
        "coverage_report_file_sha256": audit_file_sha256,
        "coverage_report_payload_sha256": audit["guards"][
            "report_payload_sha256"
        ],
        "assembly_manifest_sha256": EXPECTED_ASSEMBLY_MANIFEST_SHA256,
        "pk_candidate_packed_sha256": audit["guards"][
            "pk_candidate_packed_sha256"
        ],
        "full_incoming_closure_verified": True,
        "grammar_complete_for_all_registers": True,
        "actual_current_relative_nonexpanding": True,
        "control_components_preserved": True,
        "protected_signature_preserved": True,
        "per_row_game_playback_required": False,
    }
    evidence["row_verification_sha256"] = canonical_sha256(evidence)
    return evidence


def build_updated_rows(
    *,
    analysis: Mapping[str, Any],
    audit: Mapping[str, Any],
    audit_file_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    pending = set(analysis["pending_coordinates"])
    overrides = analysis["overrides"]
    updated_rows: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    for coordinate in analysis["display_coordinates"]:
        key = ("pk_msggame", coordinate)
        predecessor = analysis["predecessor_rows"][key]
        updated = copy.deepcopy(dict(predecessor))
        is_override = coordinate in overrides
        is_promotion = coordinate in pending
        if is_override:
            updated["translation"] = overrides[coordinate]
        if is_promotion:
            require(
                predecessor.get("runtime_review") == "pending"
                and predecessor.get("scope_classification")
                == "runtime_fragment_pending",
                f"promotion predecessor drifted: {coordinate}",
            )
            updated["runtime_review"] = "verified"
            updated["scope_classification"] = "retranslated"
            updated["layout_review"] = "runtime_verified"
            action = (
                "translation_override_and_runtime_promotion"
                if is_override
                else "runtime_promotion"
            )
        else:
            require(
                predecessor.get("runtime_review") == "verified"
                and is_override,
                f"renewal predecessor drifted: {coordinate}",
            )
            action = "translation_override_and_verification_renewal"
        updated["thought_predicate_family_update_action"] = action
        evidence = evidence_row(
            coordinate=coordinate,
            predecessor=predecessor,
            updated=updated,
            action=action,
            analysis=analysis,
            audit=audit,
            audit_file_sha256=audit_file_sha256,
        )
        updated["runtime_vm_verification"] = evidence
        updated_rows.append(updated)
        evidence_rows.append(evidence)
    updated_rows.sort(key=row_sort_key)
    evidence_rows.sort(
        key=lambda row: BASE_AUDIT.parse_literal_coordinate(
            str(row["coordinate"])
        )
    )
    require(
        len(updated_rows) == EXPECTED_DISPLAY_CLOSURE_ROWS
        and len(evidence_rows) == EXPECTED_DISPLAY_CLOSURE_ROWS,
        "thought-predicate private delta row count drifted",
    )
    return updated_rows, evidence_rows


def build_promotion_report(
    *,
    audit: Mapping[str, Any],
    audit_file_sha256: str,
    decision_content: str,
    evidence_content: str,
    evidence_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    actions = Counter(str(row["action"]) for row in evidence_rows)
    report = {
        "schema": PROMOTION_SCHEMA,
        "status": "PASS",
        "release_target": "0.15.0",
        "resource": "MSG_PK/JP/msggame.bin",
        "method": METHOD,
        "result": {
            "translation_override_rows": EXPECTED_TRANSLATION_OVERRIDES,
            "runtime_promotion_rows": EXPECTED_PENDING_ELIGIBLE_ROWS,
            "existing_verified_evidence_renewal_rows":
            EXPECTED_VERIFIED_RENEWAL_ROWS,
            "rejected_rows": EXPECTED_REJECTED_ROWS,
            "pending_rows_before": EXPECTED_PREDECESSOR_PENDING,
            "pending_rows_after": EXPECTED_POST_LAYER_PENDING,
            "decision_delta_rows": EXPECTED_DISPLAY_CLOSURE_ROWS,
            "private_evidence_rows": EXPECTED_DISPLAY_CLOSURE_ROWS,
            "private_decision_delta_sha256": sha256_bytes(
                decision_content.encode("utf-8")
            ),
            "private_evidence_sha256": sha256_bytes(
                evidence_content.encode("utf-8")
            ),
            "translation_body_copied_to_evidence": False,
        },
        "action_counts": dict(sorted(actions.items())),
        "evidence": {
            "audit_report_file_sha256": audit_file_sha256,
            "audit_report_payload_sha256": audit["guards"][
                "report_payload_sha256"
            ],
            "pk_candidate_packed_sha256": audit["guards"][
                "pk_candidate_packed_sha256"
            ],
            "assembly_manifest_sha256":
            EXPECTED_ASSEMBLY_MANIFEST_SHA256,
            "pending_eligible_coordinate_sha256":
            EXPECTED_PENDING_COORDINATE_SHA256,
            "verified_renewal_coordinate_sha256":
            EXPECTED_RENEWAL_COORDINATE_SHA256,
        },
        "distribution_policy": {
            "tracked_report_contains_commercial_source_text": False,
            "tracked_report_contains_translated_dialogue_text": False,
            "private_decision_bodies_stay_below_tmp": True,
            "private_evidence_contains_translation_bodies": False,
        },
        "steam_write_performed": False,
    }
    return seal_report(report)


def build_outputs() -> tuple[
    str,
    str,
    str,
    str,
    dict[str, Any],
    dict[str, Any],
]:
    analysis = build_analysis()
    audit = build_audit(analysis)
    validate_seal(audit)
    audit_content = canonical_json(audit)
    audit_file_sha256 = sha256_bytes(audit_content.encode("utf-8"))
    updated_rows, evidence_rows = build_updated_rows(
        analysis=analysis,
        audit=audit,
        audit_file_sha256=audit_file_sha256,
    )
    decision_content = canonical_jsonl(updated_rows)
    evidence_content = canonical_jsonl(evidence_rows)
    promotion = build_promotion_report(
        audit=audit,
        audit_file_sha256=audit_file_sha256,
        decision_content=decision_content,
        evidence_content=evidence_content,
        evidence_rows=evidence_rows,
    )
    validate_seal(promotion)
    promotion_content = canonical_json(promotion)
    return (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        {
            "analysis": analysis,
            "updated_rows": updated_rows,
            "evidence_rows": evidence_rows,
            "promotion": promotion,
        },
    )


def validate_outputs(
    *,
    decision_content: str,
    evidence_content: str,
    audit_content: str,
    promotion_content: str,
    audit: Mapping[str, Any],
    bundle: Mapping[str, Any],
) -> None:
    require(
        decision_content == canonical_jsonl(bundle["updated_rows"])
        and evidence_content == canonical_jsonl(bundle["evidence_rows"])
        and audit_content == canonical_json(audit)
        and promotion_content == canonical_json(bundle["promotion"]),
        "thought-predicate output serialization drifted",
    )
    validate_seal(audit)
    validate_seal(bundle["promotion"])
    guards = audit["guards"]
    conditional_guards = {
        "pk_candidate_packed_sha256": EXPECTED_PK_CANDIDATE_SHA256,
        "override_manifest_sha256": EXPECTED_OVERRIDE_MANIFEST_SHA256,
        "report_payload_sha256": EXPECTED_AUDIT_PAYLOAD_SHA256,
    }
    for key, expected in conditional_guards.items():
        if expected:
            require(
                guards[key] == expected,
                f"thought-predicate audit guard drifted: {key}",
            )
    output_hashes = (
        (audit_content, EXPECTED_AUDIT_FILE_SHA256, "audit"),
        (promotion_content, EXPECTED_PROMOTION_FILE_SHA256, "promotion"),
        (decision_content, EXPECTED_DECISION_FILE_SHA256, "decision"),
        (evidence_content, EXPECTED_EVIDENCE_FILE_SHA256, "evidence"),
    )
    for content, expected, label in output_hashes:
        if expected:
            require(
                sha256_bytes(content.encode("utf-8")) == expected,
                f"thought-predicate {label} output digest drifted",
            )
    merged = {
        key: copy.deepcopy(dict(row))
        for key, row in bundle["analysis"]["predecessor_rows"].items()
    }
    delta = {
        (str(row["resource"]), str(row["coordinate"])): row
        for row in bundle["updated_rows"]
    }
    require(set(delta) <= set(merged), "private delta has foreign rows")
    merged.update(delta)
    pending = [
        key for key, row in merged.items()
        if row.get("runtime_review") == "pending"
    ]
    require(
        len(merged) == EXPECTED_PREDECESSOR_ROWS
        and len(pending) == EXPECTED_POST_LAYER_PENDING,
        "thought-predicate delta does not merge to pending 8618",
    )
    promoted = [
        row for row in bundle["updated_rows"]
        if row["thought_predicate_family_update_action"]
        in {
            "runtime_promotion",
            "translation_override_and_runtime_promotion",
        }
    ]
    renewed = [
        row for row in bundle["updated_rows"]
        if row["thought_predicate_family_update_action"]
        == "translation_override_and_verification_renewal"
    ]
    require(
        len(promoted) == EXPECTED_PENDING_ELIGIBLE_ROWS
        and len(renewed) == EXPECTED_VERIFIED_RENEWAL_ROWS
        and coordinate_digest(
            str(row["coordinate"]) for row in promoted
        )
        == EXPECTED_PENDING_COORDINATE_SHA256
        and coordinate_digest(
            str(row["coordinate"]) for row in renewed
        )
        == EXPECTED_RENEWAL_COORDINATE_SHA256,
        "thought-predicate promotion/renewal delta drifted",
    )
    for evidence in bundle["evidence_rows"]:
        require(
            "translation" not in evidence
            and evidence.get("per_row_game_playback_required") is False,
            "thought-predicate evidence leaked a translation body",
        )
    require(
        audit.get("steam_write_performed") is False
        and bundle["promotion"].get("steam_write_performed") is False,
        "thought-predicate report claims a Steam write",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-output",
        type=Path,
        default=DEFAULT_AUDIT_OUTPUT,
    )
    parser.add_argument(
        "--promotion-output",
        type=Path,
        default=DEFAULT_PROMOTION_OUTPUT,
    )
    parser.add_argument(
        "--decision-output",
        type=Path,
        default=DEFAULT_DECISION_OUTPUT,
    )
    parser.add_argument(
        "--evidence-output",
        type=Path,
        default=DEFAULT_EVIDENCE_OUTPUT,
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser


def validate_output_paths(args: argparse.Namespace) -> None:
    private_root = DIALOGUE_TMP.resolve(strict=False)
    public_root = (WORKSTREAM / "public").resolve(strict=False)
    resolved: list[Path] = []
    for path in (args.decision_output, args.evidence_output):
        value = path.resolve(strict=False)
        require(
            value != private_root and private_root in value.parents,
            f"private output must remain below {private_root}: {path}",
        )
        resolved.append(value)
    for path in (args.audit_output, args.promotion_output):
        value = path.resolve(strict=False)
        require(
            value != public_root and public_root in value.parents,
            f"public output must remain below {public_root}: {path}",
        )
        resolved.append(value)
    live_paths = {
        LIVE_STEAM_BASE.resolve(strict=False),
        LIVE_STEAM_PK.resolve(strict=False),
    }
    require(
        len(set(resolved)) == len(resolved)
        and not (set(resolved) & live_paths),
        "thought-predicate outputs overlap or target live Steam",
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    require(args.write or args.check, "choose --write, --check, or both")
    validate_output_paths(args)
    (
        decision_content,
        evidence_content,
        audit_content,
        promotion_content,
        audit,
        bundle,
    ) = build_outputs()
    validate_outputs(
        decision_content=decision_content,
        evidence_content=evidence_content,
        audit_content=audit_content,
        promotion_content=promotion_content,
        audit=audit,
        bundle=bundle,
    )
    outputs = {
        args.decision_output: decision_content,
        args.evidence_output: evidence_content,
        args.audit_output: audit_content,
        args.promotion_output: promotion_content,
    }
    if args.write:
        for path, content in outputs.items():
            ENGINE.atomic_write(path, content)
    if args.check:
        for path, content in outputs.items():
            require(
                path.is_file()
                and path.read_text(encoding="utf-8") == content,
                f"generated thought-predicate output drifted: {path}",
            )
    print(
        "PASS "
        f"overrides={EXPECTED_TRANSLATION_OVERRIDES} "
        f"assemblies={EXPECTED_DISPLAY_ASSEMBLIES} "
        f"renewed={EXPECTED_VERIFIED_RENEWAL_ROWS} "
        f"promoted={EXPECTED_PENDING_ELIGIBLE_ROWS} "
        f"pending={EXPECTED_POST_LAYER_PENDING} "
        "rejected=0 steam_write=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        OSError,
        ValueError,
        ThoughtPredicateError,
        BOUND.TerminalFamilyError,
        HONORIFIC.HonorificSpacingError,
        ENGINE.RetranslationError,
    ) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
