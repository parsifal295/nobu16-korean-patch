#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 8."""

from __future__ import annotations

import argparse
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


BATCH_ID = "msggame_pk_system_messages_b06r0948_1205.v0.8"
OVERLAY_NAME = "msggame_ko_system_messages_b06r0948_1205.v0.8.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.8.json"
REVIEW_NAME = "translation_review_index.v0.8.json"
VALIDATION_NAME = "translation_validation.v0.8.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (6, 1209, 0)


TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (6, 948): ("가끔은 사치도\n부려 보고 싶군",),
    (6, 955): ("군량을 팔겠습니까?",),
    (6, 956): ("제 물건도 사 주실 수 없습니까?",),
    (6, 967): ("어디에서든\n일해 보이겠습니다",),
    (6, 968): ("영지가 넓어지면\n이동도 어쩔 수 없지",),
    (6, 969): ("적재적소라는\n말이 있습니다",),
    (6, 970): ("이사 비용은\n어떻게 되는 겁니까?",),
    (6, 971): ("싸울 수 있는 곳이라면\n상관없다",),
    (6, 972): ("살던 곳을 떠나는 건\n조금 쓸쓸하군",),
    (6, 979): ("배치를 바꾸는 것이군요",),
    (6, 980): ("새로운 곳으로\n이동하게 되는 겁니까?",),
    (6, 991): ("가신의 마음을\n사로잡는 것도 중요하지",),
    (6, 992): ("박탈이라니 두렵군……",),
    (6, 993): ("공을 세우려면\n어찌해야 할까?",),
    (6, 994): ("칭찬일까, 꾸중일까……",),
    (6, 995): ("공에는 보답해야겠지",),
    (6, 996): ("무언가 받는다면\n거절할 이유가 없지",),
    (6, 1003): ("무슨 상을 내리려는 걸까?",),
    (6, 1004): ("칭찬해 주신다면\n얼마나 기쁠까",),
    (6, 1015): ("오…… 좋은 소식이기를",),
    (6, 1016): ("좋은 날이\n될 것 같군",),
    (6, 1017): ("기쁜 일이\n되겠군요",),
    (6, 1018): ("새 부부는\n분명 그들이겠지……",),
    (6, 1019): ("우리 가문의 전기가 될까",),
    (6, 1020): ("호오, 혼인이라……",),
    (6, 1027): ("누가 혼인하는 거지?",),
    (6, 1028): ("설마…… 나인가?",),
    (6, 1039): ("결심하셨습니까?",),
    (6, 1040): ("설마 가독을\n물려주시려는 겁니까?",),
    (6, 1041): ("다음 세대로 넘어가는 건가……",),
    (6, 1042): ("은거를\n생각하고 계십니까?",),
    (6, 1043): ("모실 수 있어\n영광이었습니다……",),
    (6, 1044): ("가독을 넘긴다고?\n설마……",),
    (6, 1051): ("주군께서 설마\n은거하시다니……",),
    (6, 1052): ("가독에서\n물러나시는 겁니까?",),
    (6, 1063): ("어쩔 수 없는\n판단이겠지",),
    (6, 1064): ("그런 것이군",),
    (6, 1065): ("무슨 의심받을 짓을\n저질렀단 말인가?",),
    (6, 1066): ("추방이라니……",),
    (6, 1067): ("남은 자들만으로도\n충분하겠지",),
    (6, 1068): ("그자를\n추방하신 겁니까?",),
    (6, 1075): ("어쩔 수 없군……",),
    (6, 1076): ("누군가 추방되었군요",),
    (6, 1087): ("새 군단을 편성하시겠습니까?",),
    (6, 1088): ("내가 나설\n기회가 있으려나?",),
    (6, 1089): ("편성을 재검토하는 건\n좋은 생각입니다",),
    (6, 1090): ("과연 어떤 편성이 될까……",),
    (6, 1091): ("군단을 다시 짜는 것도\n좋은 방법이지",),
    (6, 1092): ("군단 구성에서\n전략이 드러나는 법이지",),
    (6, 1099): ("군단을\n편성하시겠습니까?",),
    (6, 1100): ("좋은 곳에\n배속되면 좋겠군",),
    (6, 1111): ("논의는 다 끝났나?",),
    (6, 1112): ("오늘은\n뭘 먹을까?",),
    (6, 1113): ("이제 이야기도\n끝난 거겠지?",),
    (6, 1114): ("정말 따분하군",),
    (6, 1115): ("드디어 끝났군",),
    (6, 1116): ("하마터면 잠들 뻔했군",),
    (6, 1123): ("이제 곧\n끝나겠네요",),
    (6, 1124): ("배가 고프네요",),
    (6, 1131): ("이번에는 내가……!",),
    (6, 1132): ("나도 모르게\n자세를 바로잡았다.",),
    (6, 1133): ("누가 공훈\n일위가 될까?",),
    (6, 1134): ("슬슬 논공행상을\n할 때인가?",),
    (6, 1135): ("어서 빨리\n승진하고 싶군.",),
    (6, 1136): ("뒤를 찔리면\n곤란하니까.",),
    (6, 1137): ("어쩔 수 없는\n지출이군.",),
    (6, 1138): ("바깥을 살피는 것도\n잊어서는 안 된다.",),
    (6, 1139): ("가는 정이 있어야\n오는 정이 있는 법이지.",),
    (6, 1140): ("동맹 관계라면\n안심할 수 있겠군.",),
    (6, 1141): ("늘 감사합니다\n오늘은 무엇을 찾으십니까?",),
    (6, 1142): ("늘 감사합니다\n수확철이라 쌀이 쌉니다.",),
    (6, 1143): ("늘 감사합니다\n이번 풍작으로 쌀이 아주 쌉니다!",),
    (6, 1144): ("늘 감사합니다\n이번 흉작으로 쌀값이 올랐습니다!",),
    (6, 1145): ("늘 감사합니다\n지금은 가보도 판매하고 있습니다.",),
    (6, 1146): ("늘 감사합니다\n단골손님을 위해 좋은 가보를 준비했습니다.",),
    (6, 1147): ("늘 감사합니다, 덕분에\n매입 가격이 낮아졌습니다.",),
    (6, 1148): ("늘 감사합니다, 덕분에\n거래 가능한 수량이 늘었습니다.",),
    (6, 1149): ("구입하시겠군요\n얼마나 필요하십니까?",),
    (6, 1150): ("구입하시겠군요\n어느 것으로 하시겠습니까?",),
    (6, 1151): ("먼저 남만상관을 세우십시오\n이야기는 그다음입니다",),
    (6, 1152): ("안녕하십니까\n철포가 얼마나 필요하십니까?",),
    (6, 1153): ("구입해 주셔서 감사합니다\n수령할 군량:", "입니다."),
    (6, 1154): ("구입해 주셔서 감사합니다\n수령할 군마:", "입니다."),
    (6, 1155): ("구입해 주셔서 감사합니다\n수령할 철포:", "입니다."),
    (6, 1156): ("구입해 주셔서 감사합니다\n받으실 가보는", "입니다."),
    (6, 1157): ("구입해 주셔서 감사합니다\n받으실 물품은", "외", "개입니다."),
    (6, 1158): ("매입이군요\n수량은 얼마나 됩니까?",),
    (6, 1159): ("가보를 파시겠군요\n어느 것을 매입할까요?",),
    (6, 1160): ("그럼 매입하겠습니다\n지급할 금전:", "입니다."),
    (6, 1161): ("매입 대상:", "입니다.\n지급할 금전:", "입니다."),
    (6, 1162): ("매입할 수량:", "개, 대표 물품:", "\n지급할 금전:", "입니다."),
    (6, 1163): ("거래할 수 있는 항목이 없습니다.",),
    (6, 1164): ("물자와 가보를 거래할 수 있습니다.",),
    (6, 1165): ("군량과 가보를 구입할 수 있습니다.",),
    (6, 1166): ("군량과 가보를 팔 수 있습니다.",),
    (6, 1167): ("구입할 수 있는 물품이 없습니다.",),
    (6, 1168): ("팔 수 있는 물품이 없습니다.",),
    (6, 1169): ("이번 계절에는 구입할 군량이 남아 있지 않습니다.",),
    (6, 1170): ("본거지에 군량을 더 비축할 수 없습니다.",),
    (6, 1171): ("다른 가문이 군량 구입을 방해하고 있습니다.",),
    (6, 1172): ("이번 계절에는 군량을 더 팔 수 없습니다.",),
    (6, 1173): ("다른 가문이 군량 판매를 방해하고 있습니다.",),
    (6, 1174): ("이번 계절에는 구입할 군마가 남아 있지 않습니다.",),
    (6, 1175): ("더 이상 군마를 보유할 수 없습니다",),
    (6, 1176): ("다른 가문이 군마 구입을 방해하고 있습니다",),
    (6, 1177): ("군마를 팔 수 없습니다",),
    (6, 1178): ("이번 계절에는 구입할 철포가 남아 있지 않습니다.",),
    (6, 1179): ("더 이상 철포를 보유할 수 없습니다.",),
    (6, 1180): ("아직 철포가 전래되지 않았습니다.",),
    (6, 1181): ("다른 가문이 철포 구입을 방해하고 있습니다.",),
    (6, 1182): ("성하 마을에 남만상관이 없어 철포를 구입할 수 없습니다.",),
    (6, 1183): ("철포를 팔 수 없습니다.",),
    (6, 1184): ("이번 계절에는 상인이 가보를 들여오지 않았습니다.",),
    (6, 1185): ("상인이 들여온 가보가 모두 팔렸습니다.",),
    (6, 1186): ("팔 수 있는 가보가 없습니다.",),
    (6, 1187): ("더 이상 금전을 보유할 수 없습니다.",),
    (6, 1188): ("금전이 부족하여 구입할 수 없습니다.",),
    (6, 1189): ("팔 수 있을 만큼 군량이 충분하지 않습니다.",),
    (6, 1190): ("개발 중\n", "※개발 완료까지 앞으로", "일", "."),
    (6, 1191): ("변경 사항을 취소합니다\n계속하시겠습니까?",),
    (6, 1192): ("설정을 변경할 방침을 선택하십시오.",),
    (6, 1193): ("설정을 확정하고 군단 방침 화면으로 이동합니다.",),
    (6, 1194): ("변경 사항을 취소합니다\n계속하시겠습니까?",),
    (6, 1195): ("방침을 바꾸면 제안 중인 구신을 철회하고\n새 방침에 따라 가신에게 새 제안을 요청합니다\n계속하시겠습니까?",),
    (6, 1196): ("알겠습니다\n모두에게 새로운 목표를 전하겠습니다.",),
    (6, 1197): ("적대 세력의 성만 목표로 삼을 수 있습니다.",),
    (6, 1198): ("너무 멀어 목표로 삼을 수 없습니다.",),
    (6, 1199): ("너무 멀어 목표로 삼을 수 없습니다.",),
    (6, 1200): ("우군 세력을 목표로 삼을 수 없습니다.",),
    (6, 1203): ("첫 번째 목표:", "입니다\n곧바로 공격하겠습니다"),
    (6, 1204): ("첫 번째 목표:", "입니다\n곧바로 공격하겠습니다"),
    (6, 1205): ("첫 번째 목표:", "입니다\n곧바로 공격하겠습니다"),
}

SKIPPED_CANDIDATES: dict[tuple[int, int, int], str] = {}
EXPECTED_RECORD_KEYS = tuple(TRANSLATIONS)


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
    if keys != sorted(EXPECTED_RECORD_KEYS):
        raise ValueError("translation scan record set changed")
    if selected[0] != (6, 948, 0) or selected[-1] != (6, 1205, 1):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 132:
        raise ValueError("translation batch scope changed")
    if SKIPPED_CANDIDATES:
        raise ValueError("translation batch unexpectedly contains skips")


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
    if coordinate[:2] in {(4, 83), (4, 107)}:
        flags.append("runtime_fragment_join_review")
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
            previous.is_visible_translation_candidate(literal.text)
            for literal in source_record_literals
        ):
            raise ValueError(f"scanned record contains a non-visible literal: {key}")
        language_references = {
            language: previous.record_reference(records[language][key])
            for language in LANGUAGES
        }
        literal_counts = {
            language: language_references[language]["literal_count"]
            for language in LANGUAGES
        }
        record_evidence.append(
            {
                "block_id": block_id,
                "record_id": record_id,
                "selected_sc_literal_ids": list(range(len(replacements))),
                "skipped_sc_literal_ids": [],
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
            if replacement is None:
                raise ValueError(f"unexpected skipped literal at {key}")
            coordinate = (block_id, record_id, literal.literal_id)
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
    if selected[-1] != (6, 1205, 1) or NEXT_COORDINATE not in sc_literals:
        raise ValueError("batch continuation boundary changed")

    record_keys = selected_record_keys()
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
            "scanned_visible_candidate_count": len(selected),
            "skipped_candidates": [],
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
            "scanned_visible_candidate_count": len(selected),
            "nonlinguistic_visible_candidate_skips": 0,
            "skipped_candidates": [],
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
            "skipped_candidates_unchanged": True,
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
        "skipped_count": 0,
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
