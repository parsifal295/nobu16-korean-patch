#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 2."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent
REPO_ROOT = SCRIPT_PATH.parents[2]
WORKSPACE_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(TOOLS_ROOT))
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_translation_batch1 as previous  # noqa: E402


BATCH_ID = "msggame_pk_system_messages_b02r0198_0297.v0.2"
OVERLAY_NAME = "msggame_ko_system_messages_b02r0198_0297.v0.2.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.2.json"
REVIEW_NAME = "translation_review_index.v0.2.json"
VALIDATION_NAME = "translation_validation.v0.2.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (2, 298, 0)


# None marks a deliberately skipped, non-linguistic display candidate. All
# other values are project-authored Korean; no commercial source text is
# embedded in this generator or any generated public artifact.
TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (2, 198): ("「", "」 등", "개 정책을 시행했습니다."),
    (2, 199): ("정책「", "」LV", "을 시행했습니다."),
    (2, 200): ("「", "」 등", "개 정책을 시행했습니다."),
    (2, 201): ("정책「", "」LV", "을 시행했습니다."),
    (2, 202): ("다음 달부터 정책「", "」을 철회할 예정입니다."),
    (2, 203): ("다음 달부터 「", "」 등", "개 정책을 철회할 예정입니다."),
    (2, 204): ("정책「", "」LV", "의 시행 준비를 시작했습니다."),
    (2, 205): ("「", "」 등", "개 정책의 시행 준비를 시작했습니다."),
    (2, 206): ("정책「", "」LV", "의 시행 준비를 시작했습니다."),
    (2, 207): ("「", "」 등", "개 정책의 시행 준비를 시작했습니다."),
    (2, 208): ("본가의 위신이", "으로 상승했습니다."),
    (2, 209): ("본가의 위신이", "으로 감소했습니다."),
    (2, 210): ("아군:", "을 제압했습니다. ", None),
    (2, 211): ("이(가) 함락되었습니다. ",),
    (2, 212): ("세력이 분단되어 위신이 변동했습니다.",),
    (2, 213): ("역직「", "」에 취임했습니다. ", None),
    (2, 214): ("관직「", "」에 취임했습니다. ", None),
    (2, 215): ("의 건설 가능 칸이 늘었습니다.",),
    (2, 216): ("의 건설 가능 칸이 줄었습니다.",),
    (2, 217): ("내 힘을 똑똑히 보아라!",),
    (2, 218): ("백성을 다스리는 비결은 진심뿐이다.\n이 군은 내가 장악하겠다!",),
    (2, 219): ("때가 왔다:", "이(가) 쌓아 온 인맥을\n본가에 보탤 때가 온 모양이군."),
    (2, 220): (
        "인맥의 힘:",
        "이(가) 쌓아 온 인맥으로,\n보좌할 대상:",
        "의 움직임을 도와,\n본가에 새바람을 일으키자.",
    ),
    (2, 221): ("사람을 쓰는 일에는 제법 자신이 있지……\n부하 지휘는 내게 맡겨라.",),
    (2, 222): ("말솜씨 하나는 자신 있다.\n내 언변으로 신뢰를 얻어 내지!",),
    (2, 223): ("언변으로 보좌할 대상:", ".\n반드시 신뢰를 얻어 내겠다!"),
    (2, 224): ("내 힘을 똑똑히 보아라!",),
    (2, 225): ("내 영지는 한 치도 침범하게 두지 않겠다!\n철저히 지켜 내겠다!",),
    (2, 226): ("수비야말로 내 특기다!\n철벽의 방비를 보여 주마.",),
    (2, 227): ("내 힘을 똑똑히 보아라!",),
    (2, 228): ("성 공략은 내 본분이다.\n선봉은 우리 부대가 맡겠다!",),
    (2, 229): ("내 힘을 똑똑히 보아라!",),
    (2, 230): ("싸움이야말로 무가의 본분!\n내 활약을 기대하라!",),
    (2, 231): ("적의 공격을 신속히 물리치도록,\n엄중히 경계하며 전진하자.",),
    (2, 232): ("내 힘을 똑똑히 보아라!",),
    (2, 233): ("강공 따위 두렵지 않다.\n지금이 바로 반격할 때다!",),
    (2, 234): ("내 힘을 똑똑히 보아라!",),
    (2, 235): ("내 힘을 똑똑히 보아라!",),
    (2, 236): ("여러 방면에서 협공한다……\n이것이 용병의 묘다.",),
    (2, 237): ("내 힘을 똑똑히 보아라!",),
    (2, 238): ("내 힘을 똑똑히 보아라!",),
    (2, 239): ("내 힘을 똑똑히 보아라!",),
    (2, 240): ("내 힘을 똑똑히 보아라!",),
    (2, 241): ("뒤에서 하는 일은 내게 맡겨라……\n머리를 쓰는 방식부터 다르지……",),
    (2, 242): ("뒷일이라면 내게 맡겨라……\n보좌할 대상:", ".\n반드시 성과를 내 보이겠다."),
    (2, 243): ("내 힘을 똑똑히 보아라!",),
    (2, 244): ("수상전에서는 질 수 없다.\n해신의 가호가 우리와 함께하기를.",),
    (2, 245): ("내 힘을 똑똑히 보아라!",),
    (2, 246): ("내 힘을 똑똑히 보아라!",),
    (2, 247): ("공사는 원래 내 특기지……\n신속히 끝내 주마.",),
    (2, 248): ("건축은 원래 내 특기다……\n뜻을 받들 대상:", "의 뜻을 살펴 보좌하며,\n신속히 건설을 마치겠다."),
    (2, 249): ("재해 피해를 최소한으로 막아 내겠다.\n걱정할 것 없다.",),
    (2, 250): ("서둘러 성루를 보수하고,\n적의 공격에 대비하라!",),
    (2, 251): ("을 손에 넣었다.\n모두에게 보여 주고 싶군.",),
    (2, 252): ("군용 도로 정비에는 제법 자신이 있다.\n안심하고 내게 맡겨라.",),
    (2, 253): ("군용 도로 정비에는 제법 자신이 있다.\n", "의 보좌는 내게 맡겨라."),
    (2, 254): ("내 힘을 똑똑히 보아라!",),
    (2, 255): ("이(가) 가장 자신 있는 일은\n다른 세력과의 교섭이다.",),
    (2, 256): (
        "타 세력과의 교섭은\n담당자:",
        "이(가) 가장 자신 있는 일……\n보좌할 대상:",
        "의 협상을 돕는 것쯤은 식은 죽 먹기다.",
    ),
    (2, 257): ("보아라,", "대 기병의 위력을\n떨칠 때가 왔다!"),
    (2, 258): ("똑똑히 보아라,", "군이 자랑하는\n철포대의 위력을!"),
    (2, 259): ("지금부터 똑똑히 보여 주마.\n기마 철포대의 위력을!",),
    (2, 260): ("누구도 내 앞길을 막을 수 없다!\n천하태평을 향해 전진하라!",),
    (2, 261): ("천하포무!\n백성들이여, 따르라:", "노부나가", "의 패업을!"),
    (2, 262): ("사람은 성이요, 사람은 돌담이며, 사람은 해자다.\n정은 아군이요, 원한은 적이니……",),
    (2, 263): ("즉시 전쟁을 준비하라!\n가이의 호랑이가 출진한다!",),
    (2, 264): ("맹우에게 위기가 닥쳤다……\n지금이야말로 의를 위해 일어설 때다!",),
    (2, 265): ("모두 분발하라!\n에치고의 용이 기세를 보여 주마!",),
    (2, 266): ("내 부하가 된 것은 행운이다.\n활약할 기회를 얼마든지 줄 테니까!",),
    (2, 267): ("출세야말로\n내 삶의 보람이다!",),
    (2, 268): ("참고 견뎌야 강해지는 법.\n이것이 미카와 무사의 기개다……",),
    (2, 269): ("싸우지 않고 이기는 것이 상책이다.\n교활한 너구리라 불러도 좋다……",),
    (2, 270): ("내 힘을 똑똑히 보아라!",),
    (2, 271): ("화살 하나는 꺾여도 셋은 꺾이지 않는다……\n결속이야말로 힘이다.",),
    (2, 272): ("때가 왔다…… 만사는 때를 아껴야,\n완벽한 성과로 이어지는 법.",),
    (2, 273): ("때가 왔다…… 무슨 일이든,\n보좌할 대상:", ".\n완벽한 성과로 이끌겠다."),
    (2, 274): ("녹수응온. 영민의 행복을 비는 것이,\n소운 공 이래 호조 가문의 가풍이다.",),
    (2, 275): ("물은 그릇의 모양을 따르는 법……\n성에 따라 공략법도 달라져야 한다.",),
    (2, 276): ("약하군! 도전자:", ". 생채기라도 내 보아라!"),
    (2, 277): ("큰 적과 맞서 몸을 던진다.\n", "다테", "의 방식이야말로 무가의 멋이다!"),
    (2, 278): ("단 하나의 표적:", "뿐이다!\n목숨을 걸고라도 목을 베겠다!"),
    (2, 279): ("무가에도 풍류는 빠질 수 없다.\n풍아한 마음이야말로 교섭의 요체다.",),
    (2, 280): ("무가에도 풍류는 빠질 수 없다.\n풍아한 마음이야말로 교섭의 요체……\n가르칠 대상:", "이다."),
    (2, 281): ("목적을 이룬다면 굳이 싸울 필요는 없다……\n머리를 쓰지 않으면 녹스는 법이지.",),
    (2, 282): ("시코쿠를 제패할 영웅은,\n단 하나:", "조소카베", "뿐이다!"),
    (2, 283): ("의 강함은 수에 있지 않다.\n적진을 꿰뚫어라!",),
    (2, 284): ("내 힘을 똑똑히 보아라!",),
    (2, 285): ("적군을 무찔렀다!\n병 깨는 자:", ", 천하무적이다!"),
    (2, 286): ("내 힘을 똑똑히 보아라!",),
    (2, 287): ("내 힘을 똑똑히 보아라!",),
    (2, 288): ("내 힘을 똑똑히 보아라!",),
    (2, 289): ("출진한다! 똑똑히 보아라.\n", "한베에", "의 병법을."),
    (2, 290): ("내 힘을 똑똑히 보아라!",),
    (2, 291): ("적과 아군은 시세에 따라 바뀌는 법.\n다시 손잡을 날도 있겠지. 양해하라.",),
    (2, 292): ("내 힘을 똑똑히 보아라!",),
    (2, 293): ("의 무예를 여기서 보이겠다!\n모두 분발하라!",),
    (2, 294): ("내 힘을 똑똑히 보아라!",),
    (2, 295): ("내 힘을 똑똑히 보아라!",),
    (2, 296): ("올 테면 와 보아라!\n", "가이", "의 활로 네놈을 쏘아 쓰러뜨리겠다!"),
    (2, 297): ("내 힘을 똑똑히 보아라!",),
}


SKIPPED_CANDIDATES: dict[tuple[int, int, int], str] = {
    (2, 210, 2): "nonlinguistic_numeric_delta_prefix",
    (2, 213, 2): "nonlinguistic_numeric_delta_prefix",
    (2, 214, 2): "nonlinguistic_numeric_delta_prefix",
}


def selected_record_keys() -> list[tuple[int, int]]:
    return sorted(TRANSLATIONS)


def selected_coordinates() -> list[tuple[int, int, int]]:
    return [
        (block_id, record_id, literal_id)
        for (block_id, record_id), replacements in sorted(TRANSLATIONS.items())
        for literal_id, replacement in enumerate(replacements)
        if replacement is not None
    ]


def validate_static_scope() -> None:
    keys = selected_record_keys()
    selected = selected_coordinates()
    if keys != [(2, record_id) for record_id in range(198, 298)]:
        raise ValueError("translation scan must cover block 2 records 198 through 297")
    if selected[0] != (2, 198, 0) or selected[-1] != (2, 297, 0):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150:
        raise ValueError("translation batch must contain exactly 150 literals")
    if len(SKIPPED_CANDIDATES) != 3:
        raise ValueError("translation batch skip count changed")
    if set(selected) & set(SKIPPED_CANDIDATES):
        raise ValueError("a skipped coordinate is also selected")


def _uncertainty_flags(
    coordinate: tuple[int, int, int],
    record_counts: dict[str, int],
    sc_literal_count: int,
) -> list[str]:
    flags = ["runtime_line_wrap_review"]
    if len(set(record_counts.values())) != 1:
        flags.append("cross_language_literal_shape_diff")
    if sc_literal_count > 1:
        flags.append("runtime_dynamic_join_review")
    if coordinate[1] in {198, 200, 203, 205, 207}:
        flags.append("runtime_count_join_review")
    return flags


def _assert_public_source_free(paths: Iterable[Path]) -> dict[str, dict[str, int]]:
    scans: dict[str, dict[str, int]] = {}
    for path in paths:
        counts = previous.script_counts(path.read_text(encoding="utf-8"))
        scans[path.name] = counts
        if counts != {"cjk_unified_count": 0, "kana_count": 0}:
            raise ValueError(f"source-script text leaked into {path}")
    return scans


def build(args: argparse.Namespace) -> dict[str, Any]:
    validate_static_scope()
    paths = {
        language: Path(getattr(args, f"stock_{language.lower()}")).resolve()
        for language in LANGUAGES
    }
    installed_before = {
        language: previous.sha256(path.read_bytes()) for language, path in paths.items()
    }
    loaded = previous.load_sources(paths)
    archives = {
        language: loaded[language]["parsed"].archive for language in LANGUAGES
    }
    records = {
        language: previous._record_map(archive)
        for language, archive in archives.items()
    }
    sc_literals = previous._literal_map(archives["SC"])

    overlay_entries: list[dict[str, Any]] = []
    review_entries: list[dict[str, Any]] = []
    invariant_failures: list[dict[str, Any]] = []
    record_evidence: list[dict[str, Any]] = []
    replacement_map: dict[tuple[int, int, int], str] = {}
    observed_skips: set[tuple[int, int, int]] = set()

    for block_id, record_id in selected_record_keys():
        key = (block_id, record_id)
        source_record_literals = previous.parse_record_literals(records["SC"][key])
        replacements = TRANSLATIONS[key]
        if len(source_record_literals) != len(replacements):
            raise ValueError(
                f"translation literal count mismatch at {key}: "
                f"source={len(source_record_literals)}, ko={len(replacements)}"
            )
        if not all(
            previous.is_visible_translation_candidate(item.text)
            for item in source_record_literals
        ):
            raise ValueError(f"scanned record contains an invisible SC literal: {key}")

        language_references = {
            language: previous.record_reference(records[language][key])
            for language in LANGUAGES
        }
        literal_counts = {
            language: language_references[language]["literal_count"]
            for language in LANGUAGES
        }
        selected_ids = [
            literal_id
            for literal_id, replacement in enumerate(replacements)
            if replacement is not None
        ]
        skipped_ids = [
            literal_id
            for literal_id, replacement in enumerate(replacements)
            if replacement is None
        ]
        record_evidence.append(
            {
                "block_id": block_id,
                "record_id": record_id,
                "selected_sc_literal_ids": selected_ids,
                "skipped_sc_literal_ids": skipped_ids,
                "references": language_references,
                "literal_shape_aligned_across_languages": len(set(literal_counts.values()))
                == 1,
                "cross_language_literal_id_alignment_used": False,
                "manual_same_record_semantic_crosscheck": True,
            }
        )

        for literal, replacement in zip(
            source_record_literals, replacements, strict=True
        ):
            coordinate = (block_id, record_id, literal.literal_id)
            if replacement is None:
                if coordinate not in SKIPPED_CANDIDATES:
                    raise ValueError(f"unexplained skipped coordinate: {coordinate}")
                observed_skips.add(coordinate)
                continue
            problems = previous.common.invariant_mismatches(literal.text, replacement)
            if previous.bracket_sequence(literal.text) != previous.bracket_sequence(
                replacement
            ):
                problems.append(
                    "bracket_sequence: "
                    f"source={previous.bracket_sequence(literal.text)!r}, "
                    f"ko={previous.bracket_sequence(replacement)!r}"
                )
            if problems:
                invariant_failures.append(
                    {"coordinate": list(coordinate), "problems": problems}
                )
            replacement_map[coordinate] = replacement
            overlay_entries.append(
                {
                    "block_id": block_id,
                    "record_id": record_id,
                    "literal_id": literal.literal_id,
                    "source_sc_utf16le_sha256": previous.text_hash(literal.text),
                    "ko": replacement,
                }
            )
            review_entries.append(
                {
                    "block_id": block_id,
                    "record_id": record_id,
                    "literal_id": literal.literal_id,
                    "status": "translated",
                    "translation_origin": "assistant_generated_draft_from_pinned_sc_jp_en_tc_record_context",
                    "automated_draft": True,
                    "human_review_required": True,
                    "runtime_reviewed": False,
                    "uncertainty_flags": _uncertainty_flags(
                        coordinate, literal_counts, len(source_record_literals)
                    ),
                }
            )
    if observed_skips != set(SKIPPED_CANDIDATES):
        raise ValueError("declared skipped coordinates were not observed")
    if invariant_failures:
        raise ValueError(f"replacement invariants failed: {invariant_failures}")

    sc_packed = loaded["SC"]["packed"]
    sc_raw = loaded["SC"]["raw"]
    overlay = {
        "schema": previous.OVERLAY_SCHEMA,
        "overlay_id": BATCH_ID,
        "resource": RESOURCE,
        "base_language": "SC",
        "defaults": {"status": "translated"},
        "entry_count": len(overlay_entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_sc": {
            "packed_size": len(sc_packed),
            "packed_sha256": previous.sha256(sc_packed),
            "raw_size": len(sc_raw),
            "raw_sha256": previous.sha256(sc_raw),
            "record_count": archives["SC"].record_count,
            "literal_slot_count": len(sc_literals),
        },
        "entries": overlay_entries,
    }

    rebuilt, binary_manifest = previous.apply_overlay_blob(sc_packed, overlay)
    _target_header, target_raw = previous.decompress_wrapper(rebuilt)
    target = previous.parse_packed_msggame(rebuilt)
    target_literals = previous._literal_map(target.archive)
    target_records = previous._record_map(target.archive)

    if set(target_literals) != set(sc_literals):
        raise ValueError("literal coordinates changed after rebuild")
    for coordinate, source_literal in sc_literals.items():
        expected = replacement_map.get(coordinate, source_literal.text)
        if target_literals[coordinate].text != expected:
            raise ValueError(f"rebuilt literal mismatch at {coordinate}")
    if set(target_records) != set(records["SC"]):
        raise ValueError("record coordinates changed after rebuild")
    if any(
        previous.record_skeleton(records["SC"][key])
        != previous.record_skeleton(target_records[key])
        for key in target_records
    ):
        raise ValueError("opaque record bytecode changed outside literal text")
    if previous.rebuild_raw_msggame(target.archive) != target_raw:
        raise ValueError("rebuilt target raw parse/rebuild is not byte-identical")
    if [len(block.records) for block in archives["SC"].blocks] != [
        len(block.records) for block in target.archive.blocks
    ]:
        raise ValueError("top-level block record counts changed")
    if any(block.offset % 4 for block in target.archive.blocks):
        raise ValueError("rebuilt top-level block offset is not four-byte aligned")

    selected = selected_coordinates()
    actual_coordinates = [
        tuple(entry[key] for key in ("block_id", "record_id", "literal_id"))
        for entry in overlay_entries
    ]
    if actual_coordinates != selected:
        raise ValueError("overlay coordinate order is not deterministic")
    if selected[-1] != (2, 297, 0) or NEXT_COORDINATE not in sc_literals:
        raise ValueError("batch continuation boundary changed")

    record_keys = selected_record_keys()
    skipped = [
        {"coordinate": list(coordinate), "reason": reason}
        for coordinate, reason in sorted(SKIPPED_CANDIDATES.items())
    ]
    evidence = {
        "schema": "nobu16.kr.msggame-translation-alignment-evidence.v1",
        "batch_id": BATCH_ID,
        "resource": RESOURCE,
        "scope": {
            "first_coordinate": list(selected[0]),
            "last_coordinate": list(selected[-1]),
            "selected_record_count": len(record_keys),
            "selected_literal_count": len(selected),
            "next_coordinate": list(NEXT_COORDINATE),
            "scanned_visible_candidate_count": len(selected) + len(skipped),
            "skipped_candidates": skipped,
        },
        "alignment_basis": [
            "same_pk_resource_role",
            "same_18_block_shape",
            "same_block_and_record_coordinates",
            "manual_same_record_semantic_crosscheck",
            "language_literal_shapes_may_differ",
            "cross_language_literal_id_alignment_not_used",
        ],
        "source_files": {
            language: {
                "logical_path": SOURCE_PATHS[language],
                **previous.SOURCE_PINS[SOURCE_PATHS[language]],
            }
            for language in LANGUAGES
        },
        "record_count": len(record_evidence),
        "records": record_evidence,
        "contains_commercial_source_text": False,
    }
    review = {
        "schema": "nobu16.kr.msggame-translation-review-index.v1",
        "batch_id": BATCH_ID,
        "quality_state": "draft_not_human_or_runtime_reviewed",
        "entry_count": len(review_entries),
        "entries": review_entries,
        "contains_commercial_source_text": False,
    }

    out_root = args.out_root.resolve()
    artifacts: dict[str, dict[str, Any]] = {}
    overlay_path = out_root / "public" / OVERLAY_NAME
    evidence_path = out_root / "evidence" / EVIDENCE_NAME
    review_path = out_root / "review" / REVIEW_NAME
    artifacts["overlay"] = previous.write_json(overlay_path, overlay)
    artifacts["alignment_evidence"] = previous.write_json(evidence_path, evidence)
    artifacts["review_index"] = previous.write_json(review_path, review)
    source_free_scan = _assert_public_source_free(
        (overlay_path, evidence_path, review_path)
    )

    installed_after = {
        language: previous.sha256(path.read_bytes()) for language, path in paths.items()
    }
    if installed_before != installed_after:
        raise ValueError("installed game source changed during read-only batch build")

    validation = {
        "schema": "nobu16.kr.msggame-translation-generation-validation.v1",
        "batch_id": BATCH_ID,
        "passed": True,
        "scope": {
            "first_coordinate": list(selected[0]),
            "last_coordinate": list(selected[-1]),
            "selected_record_count": len(record_keys),
            "selected_literal_count": len(selected),
            "next_coordinate": list(NEXT_COORDINATE),
            "selected_coordinates_sha256": previous.sha256(
                json.dumps(selected, separators=(",", ":")).encode("utf-8")
            ),
        },
        "selection": {
            "stable_sc_coordinate_order": True,
            "natural_scan_record_boundaries": True,
            "all_linguistic_literals_in_scanned_records_selected": True,
            "scanned_visible_candidate_count": len(selected) + len(skipped),
            "nonlinguistic_visible_candidate_skips": len(skipped),
            "skipped_candidates": skipped,
        },
        "source_alignment": {
            "languages": list(LANGUAGES),
            "record_coordinates_aligned": True,
            "literal_shapes_assumed_aligned": False,
            "manual_same_record_semantic_crosschecks": len(record_keys),
            "record_reference_count": len(record_keys) * len(LANGUAGES),
        },
        "replacement_invariants": {
            "checked": len(selected),
            "failures": 0,
            "preserved": [
                "printf_tokens",
                "unknown_percent_count",
                "leading_whitespace",
                "trailing_whitespace",
                "escape_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "bracket_sequence_in_order",
            ],
        },
        "offline_binary_validation": {
            "entry_count": binary_manifest["entry_count"],
            "target_packed_size": len(rebuilt),
            "target_packed_sha256": previous.sha256(rebuilt),
            "target_raw_size": len(target_raw),
            "target_raw_sha256": previous.sha256(target_raw),
            "literal_coordinates_preserved": True,
            "record_coordinates_preserved": True,
            "opaque_record_bytecode_preserved": True,
            "top_level_offsets_recomputed_and_aligned": True,
            "raw_parse_rebuild_byte_exact": True,
            "skipped_candidates_unchanged": all(
                target_literals[coordinate].text == sc_literals[coordinate].text
                for coordinate in SKIPPED_CANDIDATES
            ),
            "installed_game_file_written": False,
        },
        "translation_status": {
            "translated_draft": len(selected),
            "human_review_required": len(selected),
            "runtime_reviewed": 0,
        },
        "source_free_scan": source_free_scan,
        "artifacts": artifacts,
        "generator": {
            "path": SCRIPT_PATH.name,
            "sha256": previous.sha256(SCRIPT_PATH.read_bytes()),
        },
        "reproducibility": {
            "required_runs": ["isolated_a", "isolated_b", "final"],
            "byte_identical_artifacts_required": True,
            "byte_identical_offline_binary_required": True,
        },
        "safety": {
            "installed_game_files_modified": False,
            "font_files_modified": False,
            "installer_modified": False,
            "root_readme_modified": False,
            "progress_manifest_modified": False,
            "other_workstreams_modified": False,
            "process_memory_access": False,
            "dll_injection": False,
            "executable_modified": False,
            "registry_modified": False,
        },
    }
    validation_path = out_root / VALIDATION_NAME
    artifacts["generation_validation"] = previous.write_json(
        validation_path, validation
    )
    if previous.script_counts(validation_path.read_text(encoding="utf-8")) != {
        "cjk_unified_count": 0,
        "kana_count": 0,
    }:
        raise ValueError("source-script text leaked into validation artifact")
    return {
        "out_root": out_root,
        "entry_count": len(selected),
        "record_count": len(record_keys),
        "skipped_count": len(skipped),
        "next_coordinate": NEXT_COORDINATE,
        "target_packed_sha256": previous.sha256(rebuilt),
        "artifacts": artifacts,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for language in LANGUAGES:
        parser.add_argument(
            f"--stock-{language.lower()}",
            type=Path,
            default=WORKSPACE_ROOT / Path(SOURCE_PATHS[language]),
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
    print(f"records={result['record_count']}")
    print(f"entries={result['entry_count']}")
    print(f"skipped={result['skipped_count']}")
    print("next_coordinate=" + ",".join(map(str, result["next_coordinate"])))
    print(f"target_packed_sha256={result['target_packed_sha256']}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
