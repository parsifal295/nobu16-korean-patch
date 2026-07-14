#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 16."""

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


BATCH_ID = "msggame_pk_system_messages_b06r2436_2787.v0.16"
OVERLAY_NAME = "msggame_ko_system_messages_b06r2436_2787.v0.16.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.16.json"
REVIEW_NAME = "translation_review_index.v0.16.json"
VALIDATION_NAME = "translation_validation.v0.16.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (6, 2787, 1)


TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (6, 2436): (None, "님 같은 분과 교섭하다니\n제가 어리석었습니다."),
    (6, 2437): ("이런 조건은 받아들일 수 없습니다.\n교섭 상대:", "님 같은 분과 교섭하다니\n제가 어리석었습니다."),
    (6, 2438): ("이런 조건은 받아들일 수 없습니다.\n교섭 상대:", "님 같은 분과 교섭하다니\n제가 어리석었습니다."),
    (6, 2442): ("이런 조건은 받아들일 수 없습니다.\n교섭 상대:", "님 같은 분과 교섭하다니\n제가 어리석었습니다."),
    (6, 2458): ("지금 나가면 교섭 실패로 처리되어\n우호도가 낮아집니다.\n정말 외교 화면에서 나가시겠습니까?",),
    (6, 2459): ("이 내용으로 교섭을 제안합니다.\n계속하시겠습니까?",),
    (6, 2460): ("성공률이 100％가 아닙니다.\n계속하시겠습니까?\n실패하면 상대가 노하여 교섭이 어려워집니다.",),
    (6, 2461): ("성공률이 100％가 아닙니다.\n계속하시겠습니까?\n실패하면 교섭이 종료됩니다.",),
    (6, 2465): ("실패했습니다.\n상대를 화나게 했군요……",),
    (6, 2466): ("실패했습니다.\n상대를 화나게 했군요……",),
    (6, 2467): ("실패했습니다.\n상대를 화나게 했군요……",),
    (6, 2471): ("실패했습니다.\n상대를 화나게 했군요……",),
    (6, 2477): ("공략에 성공했습니다.\n진심으로 감사드립니다.",),
    (6, 2478): ("공략에 성공했습니다.\n진심으로 감사드립니다.",),
    (6, 2479): ("공략에 성공했습니다.\n진심으로 감사드립니다.",),
    (6, 2483): ("공략에 성공했습니다.\n진심으로 감사드립니다.",),
    (6, 2489): ("의뢰한 성을 함락한 듯합니다.\n다음 전투를 준비하겠습니다.",),
    (6, 2490): ("의뢰한 성을 함락한 듯합니다.\n다음 전투를 준비하겠습니다.",),
    (6, 2491): ("의뢰한 성을 함락한 듯합니다.\n다음 전투를 준비하겠습니다.",),
    (6, 2495): ("의뢰한 성을 함락한 듯합니다.\n다음 전투를 준비하겠습니다.",),
    (6, 2501): ("더는 원군이 필요 없는 듯합니다.\n철수하겠습니다.",),
    (6, 2502): ("더는 원군이 필요 없는 듯합니다.\n철수하겠습니다.",),
    (6, 2503): ("더는 원군이 필요 없는 듯합니다.\n철수하겠습니다.",),
    (6, 2507): ("더는 원군이 필요 없는 듯합니다.\n철수하겠습니다.",),
    (6, 2513): ("지켜 내지 못했습니다……\n그래도 원군에는 감사드립니다.",),
    (6, 2514): ("지켜 내지 못했습니다……\n그래도 원군에는 감사드립니다.",),
    (6, 2515): ("지켜 내지 못했습니다……\n그래도 원군에는 감사드립니다.",),
    (6, 2519): ("지켜 내지 못했습니다……\n그래도 원군에는 감사드립니다.",),
    (6, 2525): ("지켜 내지 못했습니다……\n다음에는 부탁드립니다.",),
    (6, 2526): ("지켜 내지 못했습니다……\n다음에는 부탁드립니다.",),
    (6, 2527): ("지켜 내지 못했습니다……\n다음에는 부탁드립니다.",),
    (6, 2531): ("지켜 내지 못했습니다……\n다음에는 부탁드립니다.",),
    (6, 2537): ("죄송합니다. 지켜 내지 못했습니다……",),
    (6, 2538): ("죄송합니다. 지켜 내지 못했습니다……",),
    (6, 2539): ("죄송합니다. 지켜 내지 못했습니다……",),
    (6, 2543): ("죄송합니다. 지켜 내지 못했습니다……",),
    (6, 2549): ("원군은 고마웠지만\n성을 함락하지 못했습니다.",),
    (6, 2550): ("원군은 고마웠지만\n성을 함락하지 못했습니다.",),
    (6, 2551): ("원군은 고마웠지만\n성을 함락하지 못했습니다.",),
    (6, 2555): ("원군은 고마웠지만\n성을 함락하지 못했습니다.",),
    (6, 2561): ("이번 공략은 실패했습니다……\n다음에는 부탁드립니다.",),
    (6, 2562): ("이번 공략은 실패했습니다……\n다음에는 부탁드립니다.",),
    (6, 2563): ("이번 공략은 실패했습니다……\n다음에는 부탁드립니다.",),
    (6, 2567): ("이번 공략은 실패했습니다……\n다음에는 부탁드립니다.",),
    (6, 2573): ("죄송합니다. 공략에 실패했습니다……",),
    (6, 2574): ("죄송합니다. 공략에 실패했습니다……",),
    (6, 2575): ("죄송합니다. 공략에 실패했습니다……",),
    (6, 2579): ("죄송합니다. 공략에 실패했습니다……",),
    (6, 2585): ("방어에 성공했습니다!\n큰 도움이 되었습니다. 감사합니다!",),
    (6, 2586): ("방어에 성공했습니다!\n큰 도움이 되었습니다. 감사합니다!",),
    (6, 2587): ("방어에 성공했습니다!\n큰 도움이 되었습니다. 감사합니다!",),
    (6, 2591): ("방어에 성공했습니다!\n큰 도움이 되었습니다. 감사합니다!",),
    (6, 2597): ("방어에 성공했습니다.\n진심으로 감사드립니다.",),
    (6, 2598): ("방어에 성공했습니다.\n진심으로 감사드립니다.",),
    (6, 2599): ("방어에 성공했습니다.\n진심으로 감사드립니다.",),
    (6, 2603): ("방어에 성공했습니다.\n진심으로 감사드립니다.",),
    (6, 2609): ("성을 지켜 낸 듯합니다.\n그럼 병력을 철수하겠습니다.",),
    (6, 2610): ("성을 지켜 낸 듯합니다.\n그럼 병력을 철수하겠습니다.",),
    (6, 2611): ("성을 지켜 낸 듯합니다.\n그럼 병력을 철수하겠습니다.",),
    (6, 2615): ("성을 지켜 낸 듯합니다.\n그럼 병력을 철수하겠습니다.",),
    (6, 2623): ("전투는 병력으로만 하는 것이 아닙니다.\n말로 겨루는 것도 전투의 한 형태입니다.",),
    (6, 2624): ("무력만으로 해결할 수 없는 일도 많습니다.\n오히려 언변으로 이기는 경우도 있습니다.",),
    (6, 2625): ("우리의 지혜를 활용해야 합니다.\n무력만 쓰는 것이 능사는 아닙니다.",),
    (6, 2626): ("병력을 다루는 무략도 중요하지만\n언변을 활용하는 지략도 소홀히 할 수 없습니다.",),
    (6, 2627): ("출병했다면 전의를 가다듬어야 하지만\n지금은 말의 칼날을 벼릴 때입니다.",),
    (6, 2628): ("말 대신 칼과 창으로 모든 것을 해결할 수 있다면\n세상일이 훨씬 편하겠지요.",),
    (6, 2635): ("전투가 계속되고 있지만\n교섭도 잊어서는 안 됩니다.",),
    (6, 2636): ("전투로 승부를 가리는 것만이 아니라\n담판을 벌이는 것도 한 방법입니다.",),
    (6, 2647): ("숙적과의 전투가 피할 수 없다면\n미리 대비하는 것도 당연합니다.",),
    (6, 2648): ("눈앞을 막는 적이 있어도 언변으로\n길을 열 수 있다면 그보다 좋은 일은 없습니다.",),
    (6, 2649): ("눈앞의 적에 대비하려면\n언변도 잘 활용해야 합니다.",),
    (6, 2650): ("적과 싸우기 위해\n쓸 수 있는 모든 수단을 동원해야 합니다.",),
    (6, 2651): ("적과의 전투가 기다리고 있으니\n마음에 걸리는 일을 미리 끝내야 합니다.",),
    (6, 2652): ("병마를 갖추는 것처럼 외교로도\n전투에 대비해야 합니다.",),
    (6, 2659): ("언젠가 전투가 벌어질 것입니다.\n그에 대비하려면 외교도 필요합니다.",),
    (6, 2660): ("결국 병력으로 싸우더라도 외교로\n판세를 정비하는 일은 유용합니다.",),
    (6, 2671): ("앞날을 생각해 우호 관계를 맺을 세력:", "\n좋은 관계를 구축해야 합니다."),
    (6, 2672): ("친밀해질 세력:", "와 관계를 다지면\n앞길이 열릴 것입니다."),
    (6, 2673): ("이럴 때 손잡고 싶은 세력:", "\n함께 이 일을 해결하고 싶습니다."),
    (6, 2674): ("관계를 다시 구축할 세력:", "과\n좋은 관계를 맺으면 판세를 바꿀 수 있습니다."),
    (6, 2675): ("새로운 관계를 맺는 것도 방법입니다. 대상:\n", "과 잘 지내 봅시다."),
    (6, 2676): ("전투만이 능사는 아닙니다.\n친선을 추진할 세력:", "과 우호 관계를 다져야 합니다."),
    (6, 2683): ("우리 사정에 따른 일이지만\n우호를 구할 세력:", "과 좋은 관계를 맺어야 합니다."),
    (6, 2684): ("우리 처지를 생각해 친해져야 할 세력:", "\n우호 관계를 맺는 것이 최선입니다."),
    (6, 2695): ("앞으로도 관계를 유지할 세력:", "\n좋은 관계를 계속 지키고 싶습니다."),
    (6, 2696): ("본가와 유대를 이어 갈 세력:", "과의\n굳은 인연이 오래 이어지기를 바랍니다."),
    (6, 2697): ("우호 관계를 맺은 세력: ", "과 우호를 지키는 것이 무엇보다 중요합니다.\n그것이 우정인지 책략인지는 모르겠지만요."),
    (6, 2698): ("서로의 속셈과 관계없이 함께할 세력:", "\n그 관계가 오래 이어지기를 바랍니다."),
    (6, 2699): ("본가와 반석 같은 관계를 맺은 세력:", "과의 관계는 굳건합니다.\n언제까지나 이대로이기를 바랍니다."),
    (6, 2700): ("본가의 맹우:", ". 더없이 소중한 동맹입니다.\n이 우정을 해치지 않도록 주의해야 합니다."),
    (6, 2707): ("좋은 관계를 맺은 세력:", ". 관계는 좋지만\n난세에는 방심할 수 없습니다."),
    (6, 2708): ("계속 좋은 관계를 유지할 세력:", "\n이 관계가 오래 이어지기를 바랍니다."),
    (6, 2719): ("힘이 부족해 지금 따르는 세력:", "\n언젠가 뒤집을 기회가 올 것입니다."),
    (6, 2720): ("강자가 약자를 거느리는 것이 세상의 이치지만,\n앞으로도 계속 따를 세력은 아닙니다:",),
    (6, 2721): ("지금 본가를 억누르는 세력:", "의 아래에 있지만,\n당분간은 보호막으로 이용합시다."),
    (6, 2722): ("분하지만 지금은 어쩔 수 없습니다.\n종속할 세력:", "의 아래에 있겠습니다…… 지금만은.\n"),
    (6, 2723): ("본가가 약한 탓입니다. 벗어나야 할 세력:", ".\n종속되기 싫다면 강해져야 합니다."),
    (6, 2724): ("본가가 아래에 놓인 세력:", ". 굴욕스럽지만,\n지금은 힘을 비축해야 합니다."),
    (6, 2731): ("신종한 처지는 괴롭지만,\n영원히 따를 세력은 아닙니다:", "."),
    (6, 2732): ("언젠가 반드시 벗어나겠습니다.\n종속된 세력:", "의 굴레를 벗어던질 것입니다."),
    (6, 2743): ("당면한 적:", "\n외교로도 철저히 몰아붙여야 합니다."),
    (6, 2744): ("눈앞을 가로막는 적:", ".\n이 또한 철저히 무너뜨리기 위한 포석입니다."),
    (6, 2745): ("외교도 전투의 한 형태입니다.\n그 위력을 보여 줄 세력:", "에게 보여 주어야 합니다."),
    (6, 2746): ("격파해야 할 적:", ".\n지금은 언변의 칼날을 겨룰 때입니다."),
    (6, 2747): ("제가 무예만 아는 사람이라 생각한다면\n외교 실력도 보여 주겠습니다.",),
    (6, 2748): ("무력으로 쓰러뜨리는 것이 최선이지만:", "\n쉽게 무너지지는 않을 것입니다."),
    (6, 2755): ("맞서야 할 적:", ". 맞설 때는\n쓸 수 있는 모든 수단을 동원해야 합니다."),
    (6, 2756): ("앞으로 다툴 상대:", ". 경쟁할 때는\n외교로 활로를 찾아야 합니다."),
    (6, 2767): ("언젠가 닥칠 분란에 대비하려면\n교섭에도 힘을 쏟아야 합니다.",),
    (6, 2768): ("지금은 안으로 힘을 모을 때이기에\n바깥에도 눈을 돌려야 합니다.",),
    (6, 2769): ("주요한 적이 없는 지금이야말로\n외부와의 교류를 중시해야 합니다.",),
    (6, 2770): ("지금은 정무에 힘을 쏟을 때지만\n외교도 소홀히 할 수 없습니다.",),
    (6, 2771): ("전쟁이 없어도 늘 대비해야 합니다.\n외교도 그 준비의 일부입니다.",),
    (6, 2772): ("싸우지 않으면 창이 녹슬겠지만,\n전투만으로 살아남을 수 없으니 외교에 나섭시다.",),
    (6, 2779): ("지금은 나라를 부유하게 할 때입니다. 영내뿐 아니라,\n외교로도 아군과 이익을 얻어야 합니다.",),
    (6, 2780): ("본가를 번영시키려면 지금이 중요합니다.\n외교에도 소홀함이 없어야 합니다.",),
    (6, 2787): ("본가에 종속된 세력을 가신으로 삼는 방안. 대상:", None),
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
    if selected[0] != (6, 2436, 1) or selected[-1] != (6, 2787, 0):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 117:
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
                "selected_sc_literal_ids": [
                    literal_id
                    for literal_id, replacement in enumerate(replacements)
                    if replacement is not None
                ],
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
                continue
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
    if selected[-1] != (6, 2787, 0) or NEXT_COORDINATE not in sc_literals:
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
