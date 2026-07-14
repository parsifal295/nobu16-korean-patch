#!/usr/bin/env python3
"""Build a source-text-free Korean draft for the first two historical events.

The script reads pinned SC/JP/EN ``msgev.bin`` resources, but writes only
project-authored Korean text, source-text hashes, and structural metadata.
Official reference strings never enter the public workstream artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSPACE_ROOT = SCRIPT_PATH.parents[3]
TOOLS_DIR = SCRIPT_PATH.parents[2] / "tools"
sys.path.insert(0, str(TOOLS_DIR))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


BATCH_ID = "msgev_event_opening_3202_3229.v0.1"
OVERLAY_NAME = "msgev_ko_event_opening_3202_3229.v0.1.json"
STRING_COUNT = 17_910

FONT_V5_METRICS = {
    "logical_path": (
        "KR_PATCH_WORK/workstreams/officer_names/font_v5/"
        "public/metrics/glyphs.jsonl"
    ),
    "size": 731_013,
    "sha256": "FDB468457B00D47CD86B6DD95B0E4C8E38A0DAB1A724FE9DE297233D14C813B8",
}
FONT_V5_EXPECTED_MISSING_HANGUL = (
    "갔깊깼꼭꼼꾀끼낳뇌눴닥닷딸땅떨뚫렀먹밤빛섬슨식쌓쓸암였잃잦젯졌죽쥔짝째척켜튿틈혀"
)

SOURCE_PINS: dict[str, dict[str, Any]] = {
    "SC": {
        "logical_path": "MSG_PK/SC/msgev.bin",
        "size": 522_918,
        "packed_sha256": "7221A53E6E5CF493A3FAFFFCE35280E8147898120EEC59E460A2429AA265C1F9",
        "raw_size": 750_584,
        "raw_sha256": "99E0338A64FF4140AD6E27503B1BF138AC44F5B68F01973ED61D0C949619DC91",
    },
    "JP": {
        "logical_path": "MSG_PK/JP/msgev.bin",
        "size": 555_784,
        "packed_sha256": "03426B59D32EB628021DE43BC02FF82B56B04D97C25CE37F735630EA7C4E2002",
        "raw_size": 890_428,
        "raw_sha256": "4A916CA6837C4F8FC2D8B6254ECBEF26339558D2DDFEBF5A1637F8426F5918DE",
    },
    "EN": {
        "logical_path": "MSG_PK/EN/msgev.bin",
        "size": 758_160,
        "packed_sha256": "95CDB15F1AED529C95ADDE784A750059E90060A44DF1EA208EB4A56E2F685640",
        "raw_size": 1_868_232,
        "raw_sha256": "806A34770ABA15550033E0B2D51CFA849E3C9367B61BC0BA05C37B87F13475EF",
    },
}

EVENTS = (
    {
        "event_id": "kai_sagami_suruga_alliance",
        "title_ko": "카이·사가미·스루가 삼국동맹",
        "start_id": 3202,
        "end_id": 3214,
    },
    {
        "event_id": "battle_of_itsukushima",
        "title_ko": "이쓰쿠시마 전투",
        "start_id": 3215,
        "end_id": 3229,
    },
)

TRANSLATIONS: dict[int, str] = {
    3202: (
        "\x1bCB카이 겐지\x1bCZ의 강호 \x1bCB다케다\x1bCZ.\n"
        "\x1bCB아시카가 일문\x1bCZ의 명문 \x1bCB이마가와\x1bCZ.\n"
        "\x1bCA이마가와\x1bCZ에서 독립해 \x1bCC간토\x1bCZ를 개척한 \x1bCB호조\x1bCZ."
    ),
    3203: (
        "동국에 할거한 세 대다이묘는 때로\n"
        "손잡고 서로 속이며, 한 치 땅을 다투는\n"
        "호적수로서 서로를 경계했다."
    ),
    3204: (
        "그러나 덴분 23년(1554년),\n"
        "각자 배후에 적을 둔 세 가문의\n"
        "이해가 뜻밖에도 맞아떨어졌다."
    ),
    3205: (
        "이 기회를 놓칠 수 없다!\n"
        "즉시 움직인 이는 \x1bCB이마가와 가문\x1bCZ을 떠받친\n"
        "먹빛 승복의 군사, \x1bCA다이겐 소후\x1bCZ."
    ),
    3206: "이 괴승은 \x1bCA셋사이 선사\x1bCZ로도 불렸다.",
    3207: (
        "\x1bCA셋사이\x1bCZ는 재빨리 양가를 설득해,\n"
        "\x1bCA이마가와 요시모토\x1bCZ·\x1bCA다케다 하루노부\x1bCZ·\n"
        "\x1bCA호조 우지야스\x1bCZ 각 가문의 적장자에게"
    ),
    3208: (
        "서로의 딸을 맞는 혼담을 성사시켜,\n"
        "\x1bCC카이·사가미·스루가\x1bCZ 삼각동맹을 맺었다."
    ),
    3209: (
        "마지막으로,\n"
        "\x1bCA셋사이\x1bCZ는 \x1bCA하루노부\x1bCZ와 \x1bCA우지야스\x1bCZ를\n"
        "인연 깊은 \x1bCC스루가 젠토쿠지\x1bCZ로 불렀다."
    ),
    3210: (
        "오늘날 이 회담을 부정하는 설도 있다.\n"
        "하지만 세 거물이 한자리에 모였다면,\n"
        "무슨 말을 나눴을지 상상만 해도 흥미롭다."
    ),
    3211: (
        "걸물끼리 서로의 속내를 읽지 못하고,\n"
        "또 읽히지도 않는다. 그래도 상관없다."
    ),
    3212: (
        "세 사람이 \x1bCC젠토쿠지\x1bCZ에서 손잡았다는 사실……\n"
        "그 자체가 주변 다이묘들에게\n"
        "커다란 위협이 되었다."
    ),
    3213: "타산과 이해관계, 그리고\n혼인으로 맺어진 삼각형은",
    3214: (
        "배반이 잦은 전국시대에도,\n"
        "드물게 십수 년이라는 긴 세월을\n"
        "이어 갔다."
    ),
    3215: (
        "서국 제일의 대국 \x1bCB오우치 가문\x1bCZ도 이제\n"
        "주군을 죽이고 실권을 쥔\n"
        "\x1bCA스에 하루카타\x1bCZ의 꼭두각시였다."
    ),
    3216: (
        "한편 \x1bCB오우치\x1bCZ·\x1bCB아마고\x1bCZ 사이를 오가며\n"
        "국인중에서 다이묘로 급성장한\n"
        "\x1bCA모리 모토나리\x1bCZ는 \x1bCA하루카타\x1bCZ에게 도전했다."
    ),
    3217: "덴분 24년(1555년),\n두 모략가의 두뇌전이 막을 올렸다.",
    3218: (
        "\x1bCA모토나리\x1bCZ는 신역 \x1bCC이쓰쿠시마\x1bCZ에 성을 쌓았다.\n"
        "전략적 가치는 전혀 없이,\n"
        "오직 \x1bCB오우치\x1bCZ군을 꾀어낼 미끼였다."
    ),
    3219: "의심이 암귀를 낳는다……",
    3220: (
        "\x1bCA모토나리\x1bCZ가 쓸모없는 성을 쌓을 리 없다.\n"
        "그 선입견 때문에 \x1bCA하루카타\x1bCZ는 대군을 이끌고\n"
        "\x1bCC미야오성\x1bCZ으로 향했다."
    ),
    3221: (
        "계획대로다! \x1bCA하루카타\x1bCZ의 포진 소식에\n"
        "\x1bCA모토나리\x1bCZ는 폭풍우 치는 밤 몰래\n"
        "소수 병력을 이끌고 \x1bCC이쓰쿠시마\x1bCZ로 출항했다."
    ),
    3222: (
        "밤을 틈탄다 해도,\n"
        "폭풍 속 출항은 자살행위였다.\n"
        "하지만 \x1bCA모토나리\x1bCZ는 오늘이 길일이라 호언했다."
    ),
    3223: (
        "이튿날 아침, \x1bCC미야오성\x1bCZ 포위군은\n"
        "후방에서 들이닥친 적습에 잠을 깼다."
    ),
    3224: (
        "“어째서 \x1bCB모리군\x1bCZ이 여기에!\n"
        "설마 어젯밤 폭풍을 뚫고 온 건가?”"
    ),
    3225: (
        "기습당한 \x1bCB오우치 가문\x1bCZ의 대군은\n"
        "좁은 섬에서 꼼짝 못 한 채 통제를 잃었다."
    ),
    3226: (
        "간신히 전장을 빠져나온 \x1bCA하루카타\x1bCZ는\n"
        "바닷길로 퇴각하려고 항구로 달려갔다."
    ),
    3227: (
        "그러나 그가 본 것은 아군의 군선이\n"
        "\x1bCA모토나리\x1bCZ가 지휘한 수군에\n"
        "모조리 먹잇감이 되는 광경이었다."
    ),
    3228: (
        "한 시대의 효웅 \x1bCA스에 하루카타\x1bCZ는\n"
        "절망 속에서 스스로 생을 마감했다."
    ),
    3229: (
        "\x1bCA오우치\x1bCZ에서 \x1bCA모리\x1bCZ로……\n"
        "\x1bCC주고쿠\x1bCZ의 패권이 넘어가는 순간이었다."
    ),
}

UNCERTAINTY_FLAGS: dict[int, list[str]] = {
    3202: ["literal_term_kogo_rendered_as_gangho_requires_style_review"],
    3205: ["proper_name_reading_taigen_sofu_requires_human_review"],
    3208: ["alliance_name_rendered_semantically_instead_of_on_reading"],
    3214: ["en_reference_diverges; draft_follows_sc_and_jp_duration"],
    3215: ["en_reference_diverges; draft_follows_sc_and_jp_lord_killing"],
    3218: ["literal_term_shiniki_rendered_as_sinyeok_requires_style_review"],
    3219: ["idiom_localization_requires_style_review"],
    3228: ["historical_epithet_and_death_wording_require_style_review"],
    3229: ["regional_name_reading_chugoku_requires_glossary_review"],
}

EVIDENCE_ROOT_KEYS = {
    "schema",
    "batch_id",
    "resource",
    "alignment_basis",
    "source_files",
    "event_ranges",
    "boundary_anchors",
    "entry_count",
    "entries",
    "contains_commercial_source_text",
}
EVIDENCE_SOURCE_KEYS = {
    "logical_path",
    "size",
    "packed_sha256",
    "raw_size",
    "raw_sha256",
    "string_count",
}
EVIDENCE_EVENT_KEYS = {"event_id", "title_ko", "start_id", "end_id"}
EVIDENCE_BOUNDARY_KEYS = {"id", "role", "hashes"}
EVIDENCE_ENTRY_KEYS = {
    "id",
    "event_id",
    "references",
    "manual_semantic_crosscheck",
}
EVIDENCE_REFERENCE_KEYS = {"utf16le_sha256", "structure"}
EVIDENCE_STRUCTURE_KEYS = {
    "esc",
    "line_breaks",
    "printf",
    "unknown_percent_count",
    "control_count",
    "pua",
    "leading_whitespace_utf16le_sha256",
    "trailing_whitespace_utf16le_sha256",
}
REVIEW_ROOT_KEYS = {
    "schema",
    "batch_id",
    "quality_state",
    "entry_count",
    "entries",
    "contains_commercial_source_text",
}
REVIEW_ENTRY_KEYS = {
    "id",
    "event_id",
    "status",
    "translation_origin",
    "automated_draft",
    "human_review_required",
    "runtime_reviewed",
    "uncertainty_flags",
}
VALIDATION_ROOT_KEYS = {
    "schema",
    "batch_id",
    "passed",
    "selected_entry_count",
    "selected_ids_sha256",
    "event_count",
    "source_alignment",
    "replacement_invariants",
    "translation_status",
    "layout_heuristic",
    "font_integration",
    "source_free_scan",
    "strict_schema",
    "artifacts",
    "generator",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def encode_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )


def write_json(path: Path, value: Any, relative_path: str) -> dict[str, Any]:
    blob = encode_json(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return {
        "path": relative_path,
        "size": len(blob),
        "sha256": sha256(blob),
    }


def cjk_unified_count(text: str) -> int:
    ranges = (
        (0x3400, 0x4DBF),
        (0x4E00, 0x9FFF),
        (0x20000, 0x2EBEF),
        (0x30000, 0x323AF),
    )
    return sum(any(start <= ord(ch) <= end for start, end in ranges) for ch in text)


def kana_count(text: str) -> int:
    ranges = (
        (0x3040, 0x309F),
        (0x30A0, 0x30FF),
        (0x31F0, 0x31FF),
        (0xFF66, 0xFF9D),
    )
    return sum(any(start <= ord(ch) <= end for start, end in ranges) for ch in text)


def validate_public_shapes(
    evidence: dict[str, Any], review: dict[str, Any], ids: list[int]
) -> None:
    common.require_exact_keys(evidence, EVIDENCE_ROOT_KEYS, "alignment evidence")
    common.require_exact_keys(
        evidence["source_files"], {"SC", "JP", "EN"}, "alignment source files"
    )
    for language in ("SC", "JP", "EN"):
        common.require_exact_keys(
            evidence["source_files"][language],
            EVIDENCE_SOURCE_KEYS,
            f"alignment source {language}",
        )
    for index, event in enumerate(evidence["event_ranges"]):
        common.require_exact_keys(event, EVIDENCE_EVENT_KEYS, f"event range {index}")
    for index, boundary in enumerate(evidence["boundary_anchors"]):
        common.require_exact_keys(
            boundary, EVIDENCE_BOUNDARY_KEYS, f"boundary anchor {index}"
        )
        common.require_exact_keys(
            boundary["hashes"], {"SC", "JP", "EN"}, f"boundary hashes {index}"
        )
    if len(evidence["entries"]) != len(ids):
        raise ValueError("alignment evidence entry count differs from selected ids")
    for expected_id, entry in zip(ids, evidence["entries"], strict=True):
        common.require_exact_keys(entry, EVIDENCE_ENTRY_KEYS, f"evidence id {expected_id}")
        common.require_exact_keys(
            entry["references"], {"SC", "JP", "EN"}, f"references id {expected_id}"
        )
        for language in ("SC", "JP", "EN"):
            reference = entry["references"][language]
            common.require_exact_keys(
                reference,
                EVIDENCE_REFERENCE_KEYS,
                f"reference id {expected_id} {language}",
            )
            common.require_exact_keys(
                reference["structure"],
                EVIDENCE_STRUCTURE_KEYS,
                f"structure id {expected_id} {language}",
            )

    common.require_exact_keys(review, REVIEW_ROOT_KEYS, "review index")
    if len(review["entries"]) != len(ids):
        raise ValueError("review entry count differs from selected ids")
    for expected_id, entry in zip(ids, review["entries"], strict=True):
        common.require_exact_keys(entry, REVIEW_ENTRY_KEYS, f"review id {expected_id}")


def font_v5_integration() -> dict[str, Any]:
    metrics_path = (
        SCRIPT_PATH.parents[1]
        / "officer_names"
        / "font_v5"
        / "public"
        / "metrics"
        / "glyphs.jsonl"
    )
    blob = metrics_path.read_bytes()
    if len(blob) != FONT_V5_METRICS["size"] or sha256(blob) != FONT_V5_METRICS["sha256"]:
        raise ValueError("officer font-v5 metrics do not match the pinned public artifact")
    covered: set[str] = set()
    for line_number, line in enumerate(blob.decode("utf-8").splitlines(), start=1):
        row = json.loads(line, object_pairs_hook=common.strict_object)
        character = row.get("character")
        if not isinstance(character, str) or len(character) != 1:
            raise ValueError(f"invalid font-v5 metrics character at line {line_number}")
        if 0xAC00 <= ord(character) <= 0xD7A3:
            covered.add(character)
    demanded = sorted(
        {
            character
            for replacement in TRANSLATIONS.values()
            for character in replacement
            if 0xAC00 <= ord(character) <= 0xD7A3
        }
    )
    missing = sorted(set(demanded) - covered)
    missing_text = "".join(missing)
    if missing_text != FONT_V5_EXPECTED_MISSING_HANGUL:
        raise ValueError(
            "font-v5 missing Hangul set changed; refresh the reviewed integration pin"
        )
    return {
        "baseline": {
            **FONT_V5_METRICS,
            "unique_hangul": len(covered),
        },
        "dialogue_unique_hangul": len(demanded),
        "missing_hangul_count": len(missing),
        "missing_hangul": missing_text,
        "missing_codepoints": [f"U+{ord(character):04X}" for character in missing],
        "release_blocked_until_font_vnext": True,
    }


def validate_generation_validation_shape(value: dict[str, Any]) -> None:
    common.require_exact_keys(value, VALIDATION_ROOT_KEYS, "generation validation")
    common.require_exact_keys(
        value["font_integration"],
        {
            "baseline",
            "dialogue_unique_hangul",
            "missing_hangul_count",
            "missing_hangul",
            "missing_codepoints",
            "release_blocked_until_font_vnext",
        },
        "font integration",
    )
    common.require_exact_keys(
        value["font_integration"]["baseline"],
        {"logical_path", "size", "sha256", "unique_hangul"},
        "font integration baseline",
    )
    common.require_exact_keys(
        value["source_free_scan"],
        {"overlay", "alignment_evidence", "review_index"},
        "source-free scan",
    )
    for name, result in value["source_free_scan"].items():
        common.require_exact_keys(
            result, {"cjk_unified_count", "kana_count"}, f"source-free scan {name}"
        )
    common.require_exact_keys(
        value["strict_schema"],
        {
            "artifacts_checked",
            "duplicate_or_case_colliding_keys_rejected",
            "unexpected_keys_rejected",
            "passed",
        },
        "strict schema validation",
    )


def load_source(path: Path, language: str):
    pin = SOURCE_PINS[language]
    packed = path.read_bytes()
    if len(packed) != pin["size"] or sha256(packed) != pin["packed_sha256"]:
        raise ValueError(f"{language} packed source does not match the pinned release")
    _, raw = decompress_wrapper(packed)
    if len(raw) != pin["raw_size"] or sha256(raw) != pin["raw_sha256"]:
        raise ValueError(f"{language} raw source does not match the pinned release")
    table = parse_message_table(raw)
    if table.string_count != STRING_COUNT:
        raise ValueError(f"{language} string count is {table.string_count}, expected {STRING_COUNT}")
    if rebuild_message_table(table, table.texts) != raw:
        raise ValueError(f"{language} parse/rebuild is not byte-identical")
    return packed, raw, table


def selected_ids() -> list[int]:
    ids: list[int] = []
    for event in EVENTS:
        ids.extend(range(int(event["start_id"]), int(event["end_id"]) + 1))
    if ids != sorted(set(ids)):
        raise ValueError("event ranges must be sorted, unique, and non-overlapping")
    if ids != sorted(TRANSLATIONS):
        raise ValueError("translation ids must exactly cover the declared event ranges")
    return ids


def event_for(entry_id: int) -> str:
    for event in EVENTS:
        if int(event["start_id"]) <= entry_id <= int(event["end_id"]):
            return str(event["event_id"])
    raise KeyError(entry_id)


def source_structure(text: str) -> dict[str, Any]:
    inv = common.message_invariants(text)
    return {
        "esc": inv["esc"],
        "line_breaks": inv["line_breaks"],
        "printf": inv["printf"],
        "unknown_percent_count": inv["unknown_percent_count"],
        "control_count": len(inv["controls"]),
        "pua": inv["pua"],
        "leading_whitespace_utf16le_sha256": common.text_hash(inv["leading_whitespace"]),
        "trailing_whitespace_utf16le_sha256": common.text_hash(inv["trailing_whitespace"]),
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    ids = selected_ids()
    paths = {"SC": args.stock_sc, "JP": args.stock_jp, "EN": args.stock_en}
    loaded = {language: load_source(path, language) for language, path in paths.items()}
    tables = {language: value[2] for language, value in loaded.items()}

    overlay_entries: list[dict[str, Any]] = []
    evidence_entries: list[dict[str, Any]] = []
    invariant_failures: list[dict[str, Any]] = []
    for entry_id in ids:
        source_sc = tables["SC"].texts[entry_id]
        replacement = TRANSLATIONS[entry_id]
        problems = common.invariant_mismatches(source_sc, replacement)
        if problems:
            invariant_failures.append({"id": entry_id, "problems": problems})
        overlay_entries.append(
            {
                "id": entry_id,
                "source_sc_utf16le_sha256": common.text_hash(source_sc),
                "ko": replacement,
            }
        )
        evidence_entries.append(
            {
                "id": entry_id,
                "event_id": event_for(entry_id),
                "references": {
                    language: {
                        "utf16le_sha256": common.text_hash(tables[language].texts[entry_id]),
                        "structure": source_structure(tables[language].texts[entry_id]),
                    }
                    for language in ("SC", "JP", "EN")
                },
                "manual_semantic_crosscheck": True,
            }
        )

    if invariant_failures:
        raise ValueError(f"replacement invariants failed: {invariant_failures}")

    sc_packed, sc_raw, _ = loaded["SC"]
    overlay = {
        "schema": common.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": "MSG_PK/SC/msgev.bin",
        "base_language": "SC",
        "entry_count": len(overlay_entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "size": len(sc_packed),
            "packed_sha256": sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": sha256(sc_raw),
            "string_count": STRING_COUNT,
        },
        "defaults": {"status": "translated"},
        "entries": overlay_entries,
    }
    common.validate_overlay_shape(overlay)

    evidence = {
        "schema": "nobu16.kr.event-dialogue-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": "msgev",
        "alignment_basis": [
            "same_resource_role",
            "same_17910_entry_count",
            "same_numeric_string_ids",
            "manual_semantic_crosscheck_of_selected_entries",
            "event_boundaries_crosschecked_in_sc_jp_en",
        ],
        "source_files": {
            language: {
                **SOURCE_PINS[language],
                "string_count": STRING_COUNT,
            }
            for language in ("SC", "JP", "EN")
        },
        "event_ranges": list(EVENTS),
        "boundary_anchors": [
            {
                "id": boundary_id,
                "role": role,
                "hashes": {
                    language: common.text_hash(tables[language].texts[boundary_id])
                    for language in ("SC", "JP", "EN")
                },
            }
            for boundary_id, role in (
                (3201, "empty_before_first_event"),
                (3202, "first_selected_entry"),
                (3214, "first_event_last_entry"),
                (3215, "second_event_first_entry"),
                (3229, "second_event_last_entry"),
                (3230, "next_event_first_entry_excluded"),
            )
        ],
        "entry_count": len(evidence_entries),
        "entries": evidence_entries,
        "contains_commercial_source_text": False,
    }

    review_entries = [
        {
            "id": entry_id,
            "event_id": event_for(entry_id),
            "status": "translated",
            "translation_origin": "assistant_generated_draft_from_pinned_sc_jp_en",
            "automated_draft": True,
            "human_review_required": True,
            "runtime_reviewed": False,
            "uncertainty_flags": UNCERTAINTY_FLAGS.get(entry_id, []),
        }
        for entry_id in ids
    ]
    review = {
        "schema": "nobu16.kr.event-dialogue-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "draft_not_human_or_runtime_reviewed",
        "entry_count": len(review_entries),
        "entries": review_entries,
        "contains_commercial_source_text": False,
    }
    validate_public_shapes(evidence, review, ids)

    out_root = args.out_root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}
    artifacts["overlay"] = write_json(
        out_root / "public" / OVERLAY_NAME,
        overlay,
        f"public/{OVERLAY_NAME}",
    )
    artifacts["alignment_evidence"] = write_json(
        out_root / "evidence" / "alignment_evidence.v0.1.json",
        evidence,
        "evidence/alignment_evidence.v0.1.json",
    )
    artifacts["review_index"] = write_json(
        out_root / "review" / "review_index.v0.1.json",
        review,
        "review/review_index.v0.1.json",
    )

    public_texts = {
        "overlay": (out_root / "public" / OVERLAY_NAME).read_text(encoding="utf-8"),
        "alignment_evidence": (
            out_root / "evidence" / "alignment_evidence.v0.1.json"
        ).read_text(encoding="utf-8"),
        "review_index": (out_root / "review" / "review_index.v0.1.json").read_text(
            encoding="utf-8"
        ),
    }
    visible_line_lengths = {
        entry_id: [
            len(common.ESC_RE.sub("", line))
            for line in TRANSLATIONS[entry_id].splitlines()
        ]
        for entry_id in ids
    }
    max_visible_line = max(
        length for lengths in visible_line_lengths.values() for length in lengths
    )
    font_integration = font_v5_integration()
    validation = {
        "schema": "nobu16.kr.event-dialogue-generation-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "selected_entry_count": len(ids),
        "selected_ids_sha256": sha256(
            json.dumps(ids, separators=(",", ":")).encode("utf-8")
        ),
        "event_count": len(EVENTS),
        "source_alignment": {
            "languages": ["SC", "JP", "EN"],
            "string_count_each": STRING_COUNT,
            "selected_entries_semantically_crosschecked": len(ids),
        },
        "replacement_invariants": {
            "checked": len(ids),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "edge_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
            ],
        },
        "translation_status": {
            "translated_draft": len(ids),
            "reviewed": 0,
            "automated_draft": len(ids),
            "human_review_required": len(ids),
            "runtime_reviewed": 0,
            "entries_with_specific_uncertainty_flags": len(UNCERTAINTY_FLAGS),
        },
        "layout_heuristic": {
            "metric": "unicode_codepoints_per_authored_line_excluding_esc_sequences",
            "max": max_visible_line,
            "entries_over_24": [
                entry_id
                for entry_id, lengths in visible_line_lengths.items()
                if max(lengths) > 24
            ],
            "runtime_layout_review_still_required": True,
        },
        "font_integration": font_integration,
        "source_free_scan": {
            name: {
                "cjk_unified_count": cjk_unified_count(text),
                "kana_count": kana_count(text),
            }
            for name, text in public_texts.items()
        },
        "strict_schema": {
            "artifacts_checked": ["overlay", "alignment_evidence", "review_index"],
            "duplicate_or_case_colliding_keys_rejected": True,
            "unexpected_keys_rejected": True,
            "passed": True,
        },
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": sha256(SCRIPT_PATH.read_bytes()),
        },
    }
    validate_generation_validation_shape(validation)
    if any(
        result["cjk_unified_count"] != 0 or result["kana_count"] != 0
        for result in validation["source_free_scan"].values()
    ):
        raise ValueError("a public artifact contains CJK Unified Ideographs or kana")
    artifacts["generation_validation"] = write_json(
        out_root / "validation.json", validation, "validation.json"
    )
    return {
        "out_root": out_root,
        "entry_count": len(ids),
        "artifacts": artifacts,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stock-sc",
        type=Path,
        default=WORKSPACE_ROOT
        / "KR_PATCH_WORK"
        / "backups"
        / "officer_name_probe_v0_1"
        / "msgev.SC.stock.bin",
    )
    parser.add_argument(
        "--stock-jp", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "JP" / "msgev.bin"
    )
    parser.add_argument(
        "--stock-en", type=Path, default=WORKSPACE_ROOT / "MSG_PK" / "EN" / "msgev.bin"
    )
    parser.add_argument("--out-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    try:
        result = build(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={result['out_root']}")
    print(f"entries={result['entry_count']}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
