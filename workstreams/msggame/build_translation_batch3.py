#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 3."""

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


BATCH_ID = "msggame_pk_system_messages_b02r0298_0565.v0.3"
OVERLAY_NAME = "msggame_ko_system_messages_b02r0298_0565.v0.3.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.3.json"
REVIEW_NAME = "translation_review_index.v0.3.json"
VALIDATION_NAME = "translation_validation.v0.3.json"
RESOURCE = previous.RESOURCE
LANGUAGES = previous.LANGUAGES
SOURCE_PATHS = previous.SOURCE_PATHS
NEXT_COORDINATE = (2, 566, 0)


# None marks a deliberately skipped, non-linguistic display candidate. All
# other values are project-authored Korean; no commercial source text is
# embedded in this generator or any generated public artifact.
TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (2, 298): ("성을 지키지 못하다니 불찰이다!\n이제 적병에게 한 방 먹여 주겠다!",),
    (2, 300): ("적의 모략을 막을 자:", "한조", "\n모두 막아 내니 걱정할 것 없다……"),
    (2, 310): ("모두 활을 거두라!\n적대 대상:", "의 적은 곧 모든 무사의 적이다!"),
    (2, 314): ("공격자:", "\n창에 맞은 자:", "!"),
    (2, 315): ("주군을 돕는 것이 진정한 부장의 임무다.\n이곳은 담당자:", "에게 맡겨라!"),
    (2, 319): ("내가 바로 미노의 야차다!\n이런 공세쯤은 아무것도 아니다!",),
    (2, 320): ("담당자:", "은(는) 농사에 제법 일가견이 있다!\n내 지식으로 이 영지를 풍요롭게 하겠다."),
    (2, 321): ("명인이라 불리는 건축 솜씨를\n마음껏 발휘하겠다!\n반드시 훌륭한 성하마을을 세우겠다.",),
    (2, 322): ("건축의 명인이라 불리는 내가\n보좌할 대상:", "을(를) 도와주겠다!\n반드시 훌륭한 성하마을을 세우겠다."),
    (2, 324): ("모두, 일제히 겨눠라!\n", "사이카", "의 철포는 무엇이든 꿰뚫는다!"),
    (2, 325): ("계략이라면 내게 맡겨라!\n당장 첩자를 보내 지휘하여,\n반드시 이 계책을 성공시키겠다.",),
    (2, 326): ("계략이라면 내게 맡겨라!\n반드시", "의 계책을 성공시키겠다."),
    (2, 327): ("누군가 이곳에서 계략을 꾸민다면,\n내가 반드시 막아 내겠다.",),
    (2, 328): ("누군가 이곳에서 계략을 꾸민다면,\n내가 반드시 막아 내겠다.",),
    (2, 329): ("적성을 제압했다!\n이 승전보를 천하에 퍼뜨려,\n천하의 부왕이 지닌 위세를 보여라!",),
    (2, 330): ("주군도 무척 든든하시겠지……\n뜻을 함께할 자:", "이(가) 있으니!"),
    (2, 331): ("정찰 담당:", "\n협공을 눈치채지 못할 줄 알았나?"),
    (2, 332): ("천하에 보여 줄 때가 왔다!\n", "이(가) 자랑하는 기마대의 위력을!"),
    (2, 333): ("이 성을 죽을 자리로 삼았다!\n목숨을 걸고 끝까지 지키겠다!",),
    (2, 334): ("신뢰를 얻는 것이 처세의 길.\n분쟁이 끊이지 않는 세상이기에\n", "은(는) 인연을 무엇보다 중히 여긴다!"),
    (2, 338): ("고금의 학문을 집대성한 문재와,\n온갖 무예를 익힌 무재를,\n이곳에서 펼쳐 보이겠다.",),
    (2, 339): ("용기병이여, 날아올라라!\n천하를 향해 마음껏 달려라!",),
    (2, 341): ("모든 일을 내게 맡겨 주십시오.\n오른눈이 될 자:", "이(가) 주군의 오른눈이 되겠습니다!"),
    (2, 342): ("내가 만민을 위하면 만민도 나를 위한다.\n이것이 영지를 풍요롭게 하는 비결이다……",),
    (2, 350): ("타로타치여, 나의 벗이여!\n이 역경을 이겨 낼 힘을 다오!",),
    (2, 353): ("용기병이여, 날아올라라!\n천하를 향해 마음껏 달려라!",),
    (2, 408): ("절대 꺾이지 않는다!\n절대 포기하지 않는다!",),
    (2, 409): ("지금이 승부처다!\n모두, 절대 포기하지 마라!",),
    (2, 410): ("자, 자! 내가 바로 미나모토노 쿠로 요시쓰네다!\n재주 있는 자여, 한판 겨뤄 보자!",),
    (2, 411): ("상대는", "!\n한판 겨뤄 보자!"),
    (2, 412): ("지금이 성을 공격할 때다!\n정예병으로 단숨에 제압하겠다!",),
    (2, 413): ("지금이 성을 공격할 절호의 기회다!\n단숨에 섬멸하자!",),
    (2, 414): ("하늘이여, 지켜보라!\n백성을 위해 이 몸을 바치겠다!",),
    (2, 415): ("하늘이여, 지켜보라!\n이 목숨을 백성에게 바치겠다!",),
    (2, 416): ("사나운 적에게는 매처럼 덮쳐라!\n이것이 용병의 극의다!",),
    (2, 417): ("사나운 적에게는 매처럼 덮쳐라!\n이것이 바로 용병의 극의다!",),
    (2, 418): ("천연이심류의 검술을,\n여기서 조금 보여 주마!",),
    (2, 419): ("내 검술의 한 자락을\n여기서 보여 주마!",),
    (2, 434): ("내 야망의 막이 이제 오른다.\n전국에 새바람을 일으킬 자:", "이(가) 바로 나다!"),
    (2, 435): ("미하타와 다테나시의 가호 아래!\n천하에 떨칠 가문:", "의 위세를 보여 주자!"),
    (2, 436): ("적의 총대장을 찾았다!\n비사문천이여, 우리에게 힘을 주소서!",),
    (2, 437): ("이 목숨은 아깝지 않다……\n노리는 것은 오직 적의 총대장뿐!",),
    (2, 438): ("똑똑히 보아라……\n독안룡이 하늘로 오르는 모습을!",),
    (2, 439): ("남편을 돕는 것이 아내의 도리!\n적이라면 아버지라도 용서하지 않겠다!",),
    (2, 440): ("내가 당주가 된 이상,\n이 전국에 새바람을 일으키겠다!",),
    (2, 441): ("내가 바로 새 당주다!\n모두 내게 충성을 다하라!",),
    (2, 442): ("적의 총대장을 찾았다!\n모두 나를 따르라!",),
    (2, 443): ("마침내 적의 총대장과 마주쳤다!\n단숨에 공격하라!",),
    (2, 444): ("기마와 철포에는 자신이 있다.\n가문의 병사들을 훈련시키겠다!",),
    (2, 445): ("내가 온 힘을 다해,\n나의 반려를 뒷받침하겠다!",),
    (2, 496): ("누구도 내 앞길을 막을 수 없다!\n천하태평을 향해 전진하라!",),
    (2, 497): ("서둘러 이 군을 복속시켜,\n백성에게 평온한 삶을 돌려주자.",),
    (2, 498): ("전투의 승패는 병사에게 달렸다……\n모두, 너희를 믿겠다.",),
    (2, 499): ("당장 전쟁 준비를 시작하라.\n신속한 자가 전국을 제패한다!",),
    (2, 500): ("맹우에게 위기가 닥쳤다……\n지금이야말로 의를 위해 일어설 때다!",),
    (2, 501): ("내 힘을 똑똑히 보아라!",),
    (2, 502): ("휘하 장수들에게\n마음껏 활약할 무대를 주자!",),
    (2, 503): ("출세야말로\n내 삶의 보람이다!",),
    (2, 504): ("참고 견뎌야 강해지는 법.\n이것이 무사의 기개다……",),
    (2, 505): ("싸우지 않고 상대를 굴복시키는 것이 상책.\n이것이 난세를 헤쳐 가는 길이다……",),
    (2, 506): ("내 힘을 똑똑히 보아라!",),
    (2, 507): ("가문이 하나로 뭉쳐야,\n영지가 안정되는 법이다.",),
    (2, 508): ("지금은 일을 한시라도 빨리 끝내고,\n다음 전투를 준비할 때다……",),
    (2, 509): ("무슨 일이든,\n보좌할 대상:", "을(를) 도와,\n완벽한 성과로 이끌겠다."),
    (2, 510): ("영민의 행복을 바라는 것이,\n영주가 지녀야 할 마음가짐이다……",),
    (2, 511): ("물은 그릇의 모양을 따르는 법……\n성에 따라 공략법도 달라져야 한다.",),
    (2, 512): ("내 힘을 똑똑히 보아라!",),
    (2, 513): ("강적과 싸울 때면……\n왠지 가슴이 뛰는군!",),
    (2, 514): ("내 힘을 똑똑히 보아라!",),
    (2, 515): ("무가에도 풍류는 빠질 수 없다.\n풍아한 마음이야말로 교섭의 요체다.",),
    (2, 516): ("무가에도 풍류는 빠질 수 없다.\n풍아한 마음으로 보좌할 대상:", "의 교섭을 돕겠다."),
    (2, 517): ("가신이 주군을 고른다……\n그것이 난세를 살아가는 비결이지.",),
    (2, 518): ("시코쿠를 다스릴 자:", "\n오직 그뿐이다!"),
    (2, 519): ("내 힘을 똑똑히 보아라!",),
    (2, 520): ("내 힘을 똑똑히 보아라!",),
    (2, 521): ("내 힘을 똑똑히 보아라!",),
    (2, 522): ("내 힘을 똑똑히 보아라!",),
    (2, 523): ("내 힘을 똑똑히 보아라!",),
    (2, 524): ("내 힘을 똑똑히 보아라!",),
    (2, 525): ("출진한다!\n내 병법을 똑똑히 보아라.",),
    (2, 526): ("내 힘을 똑똑히 보아라!",),
    (2, 527): ("적과 아군은 시세에 따라 바뀌는 법.\n다시 손잡을 날도 있겠지.",),
    (2, 528): ("내 힘을 똑똑히 보아라!",),
    (2, 529): ("의 무예를 여기서 보이겠다!\n모두 분발하라!",),
    (2, 530): ("내 힘을 똑똑히 보아라!",),
    (2, 531): ("내 힘을 똑똑히 보아라!",),
    (2, 532): ("포위군이 멋대로 굴게 둘 수 없다.\n우리도 반격하자!",),
    (2, 533): ("내 힘을 똑똑히 보아라!",),
    (2, 534): ("성을 지키지 못하다니 불찰이다!\n이제 적병에게 한 방 먹여 주겠다!",),
    (2, 535): ("내 힘을 똑똑히 보아라!",),
    (2, 536): ("적의 모략은 싹이 트기 전에 막는다.\n그것이", "의 방식이다……"),
    (2, 537): ("무엄하다!\n내가 누구인지 아느냐?!",),
    (2, 538): ("그런 잔재주는 내게 통하지 않는다!",),
    (2, 539): ("이곳에서\n농사 솜씨를 마음껏 발휘하겠다.",),
    (2, 540): ("부대:", "의 철포는\n무엇이든 꿰뚫는다!"),
    (2, 544): ("또 하나의 성이 우리 손에 들어왔다……\n천하에 떨칠 가문:", "의 위세를\n널리 알려라!"),
    (2, 545): ("주군께서 지원하러 오신다!\n모두 힘을 보태 주시오!",),
    (2, 546): ("천하에 보여 줄 때가 왔다!\n", "이(가) 자랑하는 기마대의 위력을!"),
    (2, 547): ("이 난세를 함께 헤쳐 갈 자:", "\n다른 가문과 나란히 걸으리라."),
    (2, 549): ("문무를 겸비한 내 재능을,\n이곳에서 펼쳐 보이겠다.",),
    (2, 550): ("내 지혜로,\n보좌할 대상:", "을(를) 떠받치는 기둥이 되겠습니다."),
    (2, 551): ("이 땅을 풍요롭게 만들기 위해,\n온 힘을 다하겠다.",),
    (2, 553): ("내 창에 상처 입은 자:", ",\n그것을 영광으로 여겨라……"),
    (2, 554): ("우리 부대가 자랑하는 기마와 철포의 위력을\n마음껏 맛보게 해 주마……",),
    (2, 555): ("악귀", ",\n이 정도 열세는 아무것도 아니다!"),
    (2, 556): ("울어라, 톤보키리!\n이 열세야말로 내 무용을 떨칠 무대다!",),
    (2, 557): ("상대는 이름난 맹장:", ",\n내 적수로 부족함이 없다!"),
    (2, 558): ("상대는 이름난 맹장:", "\n지략을 다해 승기를 잡자."),
    (2, 559): ("충의를 결코 잊지 않겠다:", "……\n부디 편히 잠들어라."),
    (2, 560): ("뇌신이여……\n이 열세를 헤쳐 갈 가호를 주소서!",),
    (2, 561): ("이 정도는 열세도 아니다.\n십문자창으로 뒤집을 자:", "이(가) 전세를 뒤집는다!"),
    (2, 562): ("적의 수가 더 많다고!\n하, 창의 마타자 솜씨를 보일 때로군!",),
    (2, 563): ("잡병들은 길을 비켜라!\n전장을 누빌 악귀:", ", 지금 전장을 누빈다!"),
    (2, 564): ("병력의 많고 적음은 사소한 일.\n계책이 많으면 이기고, 적으면 질 뿐이다.",),
    (2, 565): ("열세인가……\n내 계책으로 무너뜨리겠다.",),
}


SKIPPED_CANDIDATES: dict[tuple[int, int, int], str] = {}

EXPECTED_RECORD_IDS = (
    298, 300, 310, 314, 315, 319, 320, 321, 322, 324, 325, 326, 327,
    328, 329, 330, 331, 332, 333, 334, 338, 339, 341, 342, 350, 353,
    408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 434,
    435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 496, 497,
    498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510,
    511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523,
    524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536,
    537, 538, 539, 540, 544, 545, 546, 547, 549, 550, 551, 553, 554,
    555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565,
)


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
    if keys != [(2, record_id) for record_id in EXPECTED_RECORD_IDS]:
        raise ValueError("translation scan record set changed")
    if selected[0] != (2, 298, 0) or selected[-1] != (2, 565, 0):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150:
        raise ValueError("translation batch must contain exactly 150 literals")
    if len(keys) != 115:
        raise ValueError("translation batch must cover exactly 115 records")
    if SKIPPED_CANDIDATES:
        raise ValueError("translation batch unexpectedly declares a visible skip")
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
    if selected[-1] != (2, 565, 0) or NEXT_COORDINATE not in sc_literals:
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
