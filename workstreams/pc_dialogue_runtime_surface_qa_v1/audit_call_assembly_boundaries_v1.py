#!/usr/bin/env python3
"""Audit every msggame call after literal/call runtime assembly.

The existing terminal-boundary detector intentionally catches only a fixed
literal that is already a complete sentence before a called terminal suffix.
That does not cover the inverse edge or Korean allomorph mismatches such as::

    "생각하" + "습니다"                  -> "생각하습니다"
    "동의해 주시" + "합니다" + "까?"   -> "동의해 주시합니다까?"
    "알겠" + "했습니다"                -> "알겠했습니다"
    "받아들이" + "받겠습니다"          -> "받아들이받겠습니다"

Ghidra proves that the runtime assembler copies UTF-16 units verbatim; it does
not conjugate Korean or repair spacing.  This audit therefore renders every
call target and every call-bearing record, checks both local call boundaries
and the complete Cartesian record variants, and reports only high-confidence
malformed combinations.

Tracked/default output is source-free. ``--include-text`` is accepted only for
an output below the repository ``tmp`` directory.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
AUDIT_PATH = WORKSTREAM / "audit_runtime_surface_v1.py"
BASE_MORPH_PAIR_CONTRACT_PATH = (
    WORKSTREAM / "base_morph_pair_contract.source_free.v1.json"
)
PK_FALSE_SIGNATURE_CONTRACT_PATH = (
    WORKSTREAM
    / "pk_call_assembly_false_signature_contract.source_free.v1.json"
)
SCHEMA = "nobu16.kr.pc-dialogue-call-assembly-boundary-audit.v1"
BASE_MORPH_PAIR_CONTRACT_SCHEMA = (
    "nobu16.kr.base-morph-pair-contract.source-free.v1"
)
PK_FALSE_SIGNATURE_CONTRACT_SCHEMA = (
    "nobu16.kr.pk-call-assembly-reviewed-false-signature-contract."
    "source-free.v1"
)
BASE_MORPH_PAIR_DISCOVERY_INPUT_SHA256 = (
    "A4BDE0E0AEFD9A8E67117E99FC6808767BCE2876524A7C51BDD4B861C703ACA2"
)
BASE_MORPH_PAIR_COORDINATE_COUNT = 386
BASE_MORPH_PAIR_COORDINATE_SHA256 = (
    "93507FD1E2E9DC39CD1A5E7AB5785BF0E63BD3866241DE9497DA2FD3C5995FB5"
)
BASE_MORPH_PAIR_ENTRY_COUNT = 536
BASE_MORPH_PAIR_ENTRY_SHA256 = (
    "6F177213D0AAEDCA50EBD51FF668B7C999133C961B726D5A5B980D5A2EFA274B"
)
PK_FALSE_SIGNATURE_ENTRY_COUNT = 131
PK_FALSE_SIGNATURE_ENTRY_SHA256 = (
    "A27F4EA328B26802186C1760C1BCC8DAF67862889C5083629B358919FC9F5C40"
)
PK_FALSE_SIGNATURE_COORDINATE_RULE_SHA256 = (
    "5E625BD912C88AE412104638029B527C692BCE66E598CEB0697E8B3DF6125B4E"
)
PK_FALSE_SIGNATURE_REVIEW_CLASS_COUNTS = {
    "non_side_false_positive": 33,
    "selector_side_legitimate": 98,
}
PK_FALSE_SIGNATURE_RULE_COUNTS = {
    "deut_bare_copula": 15,
    "finite_suffix_before_same_sentence_hangul": 17,
    "rendered_missing_exist_stem_before_bare_formal": 1,
    "rendered_selector_side_role_smell": 98,
}
# Reviewed historical register, not malformed dynamic assembly:
# - 정진하겠사와요: archaic/feminine -사와요
# - 원군을 청하옵시다: archaic deferential 청하옵시다
BASE_MORPH_PAIR_EXACT_ALLOWLIST = frozenset(
    {
        (
            (6, 3432),
            "prefinal_ending_followed_by_predicate",
            "C76B10109A7922D1581D7899BB591570D1E352B1B5D0E29DD8A4EF738A9DD738",
        ),
        (
            (7, 1096),
            "prefinal_ending_followed_by_predicate",
            "8E6325934115F1D7B08841EE384D9629AADF3254B23B1A433EAF8DDF22C8DBAE",
        ),
    }
)

# Ghidra selector-domain contract: p32 is the display-name property used by
# these two runtime selectors.  A fixed representative is sufficient for
# boundary grammar because selectors are copied verbatim by the VM.
SYNTHETIC_SELECTOR_VALUES: Mapping[tuple[int, int], tuple[str, ...]] = {
    (3, 0x32): ("아리오카성",),
    (4, 0x32): ("도쿠가와 가문",),
}
UNKNOWN_OUTPUT_SELECTOR_SENTINEL = "\uE000"
SOURCE_FREE_FINDING_FIELDS = (
    "resource",
    "category",
    "block_id",
    "record_id",
    "component_index",
    "literal_id",
    "call_target",
    "rule",
    "previous_literal_sha256",
    "call_variant_sha256",
    "next_literal_sha256",
    "assembled_sha256",
)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = load_module(
    "pc_dialogue_runtime_surface_for_call_assembly_v1",
    AUDIT_PATH,
)

DEFAULT_BASE = AUDIT.DEFAULT_BASE
DEFAULT_PK = AUDIT.DEFAULT_PK


def load_base_morph_pair_contract() -> Mapping[
    tuple[int, int],
    Mapping[str, tuple[str, ...]],
]:
    payload = json.loads(
        BASE_MORPH_PAIR_CONTRACT_PATH.read_text(encoding="utf-8")
    )
    require(
        payload.get("schema") == BASE_MORPH_PAIR_CONTRACT_SCHEMA,
        "unexpected Base morph-pair contract schema",
    )
    require(
        payload.get("discovery_input_sha256")
        == BASE_MORPH_PAIR_DISCOVERY_INPUT_SHA256,
        "unexpected Base morph-pair discovery input",
    )
    require(
        payload.get("coordinate_count") == BASE_MORPH_PAIR_COORDINATE_COUNT,
        "unexpected Base morph-pair coordinate count",
    )
    require(
        payload.get("coordinate_sha256")
        == BASE_MORPH_PAIR_COORDINATE_SHA256,
        "unexpected Base morph-pair coordinate digest",
    )
    entries = tuple(payload.get("entries", ()))
    require(
        len(entries) == BASE_MORPH_PAIR_ENTRY_COUNT
        and payload.get("entry_count") == BASE_MORPH_PAIR_ENTRY_COUNT,
        "unexpected Base morph-pair entry count",
    )
    body = "\n".join(
        (
            f"{int(row['block_id'])}:{int(row['record_id'])}:"
            f"{row['class']}:{row['signature_sha256']}:"
            f"{row['segment_sha256']}"
        )
        for row in sorted(
            entries,
            key=lambda row: (
                int(row["block_id"]),
                int(row["record_id"]),
                str(row["class"]),
                str(row["signature_sha256"]),
                str(row["segment_sha256"]),
            ),
        )
    )
    require(
        sha256_bytes(body.encode("utf-8"))
        == BASE_MORPH_PAIR_ENTRY_SHA256
        == payload.get("entry_sha256"),
        "unexpected Base morph-pair entry digest",
    )
    by_coordinate: dict[
        tuple[int, int],
        dict[str, set[str]],
    ] = {}
    for row in entries:
        coordinate = (int(row["block_id"]), int(row["record_id"]))
        segment_sha256 = str(row["segment_sha256"])
        category = str(row["class"])
        by_coordinate.setdefault(coordinate, {}).setdefault(
            segment_sha256,
            set(),
        ).add(category)
    require(
        len(by_coordinate) == BASE_MORPH_PAIR_COORDINATE_COUNT,
        "Base morph-pair contract has an unexpected coordinate set",
    )
    return {
        coordinate: {
            segment: tuple(sorted(categories))
            for segment, categories in segment_map.items()
        }
        for coordinate, segment_map in by_coordinate.items()
    }


NON_EMITTING_COMPONENTS = frozenset(
    {
        "arithmetic_operator",
        "comparison_operator",
        "logical_operator",
        "decimal_atom",
        "percent_decimal_atom",
        "control_tag",
        "block_token",
        "random_select",
        "padding_zero",
    }
)

SENTENCE_BOUNDARY_PUNCTUATION = frozenset(
    ".!?;:"
    "。．！？；："
    "\"'”’」』》〉】〕）)]}"
    "…⋯"
)

# A called output with one of these endings is a complete Korean predicate or
# command.  A following literal that starts directly with Hangul cannot be
# treated as another suffix fragment.
FINITE_OUTPUT_RE = re.compile(
    r"(?:"
    r"습니다|사옵니다|옵니다|나이다|"
    r"한다|했다|된다|됐다|있다|없다|겠다|"
    r"하오|하겠소|받겠소|드리겠소|"
    r"합니다|했습니다|하옵니다|하겠습니다|하겠사옵니다|"
    r"받겠습니다|받겠사옵니다|주겠습니다|드리겠습니다|"
    r"합시다|받읍시다|하자|받자|가라|하라|하십시오|"
    r"입니까|합니까|하옵니까|괜찮습니까|어떻습니까|"
    r"어떠한가|어떠하오|어떠하옵니까|"
    r"군요|네요|지요|죠"
    r")$"
)

FULL_RENDER_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "rendered_trailing_ha_before_full_ha",
        re.compile(
            r"하(?:합니다|한다|하옵니다|했습니다|했다|"
            r"하겠습니다|하겠다|하겠소|하겠사옵니다|"
            r"합시다|하자)"
        ),
    ),
    (
        "rendered_trailing_ha_before_bare_formal",
        re.compile(r"하습니다"),
    ),
    (
        "rendered_trailing_get_before_full_ha",
        re.compile(r"겠(?:합니다|한다|하옵니다|했습니다|했다)"),
    ),
    (
        "rendered_request_stem_before_full_ha",
        re.compile(
            r"(?<!예의)주시(?:합니다|한다|하옵니다|"
            r"하지 않습니다|하지 않는다|하지 않사옵니다)"
        ),
    ),
    (
        "rendered_alget_before_past_ha",
        re.compile(r"알겠(?:했습니다|했다)"),
    ),
    (
        "rendered_accept_before_receive",
        re.compile(r"받아들이받"),
    ),
    (
        "rendered_finite_then_question_fragment",
        re.compile(
            r"(?:합니다|한다|하옵니다|했습니다|했다|"
            r"습니다|사옵니다|옵니다|겠습니다|겠다|"
            r"겠소|겠사옵니다)(?:까|인가|시겠습니까|"
            r"겠습니까|습니까|는가|은가|일까)[?？]?"
        ),
    ),
    (
        "rendered_formal_finite_then_jiman",
        re.compile(
            r"(?:입니다|합니다|했습니다|습니다|사옵니다|옵니다)지만"
        ),
    ),
    (
        "rendered_exist_copula_collision",
        re.compile(r"있입니다"),
    ),
    (
        "rendered_become_bare_collision",
        re.compile(r"되습니다"),
    ),
    (
        "rendered_absent_lexeme_collision",
        re.compile(r"없없습니다"),
    ),
    (
        "rendered_negative_copula_collision",
        re.compile(r"않이지요"),
    ),
    (
        "rendered_causative_negative_collision",
        re.compile(r"(?:시키|내)하지"),
    ),
    (
        "rendered_give_lexeme_collision",
        re.compile(r"주주(?:시오|십시오)"),
    ),
    (
        "rendered_double_honorific",
        re.compile(
            r"(?:아버님|어머님|할아버님|할머님|형님|누님|주군님)님"
        ),
    ),
    (
        "rendered_object_particle_before_full_ha",
        re.compile(r"[을를]하(?:겠습니다|겠다|자|합니다|한다|하옵니다)"),
    ),
    (
        "rendered_missing_space_before_full_absent",
        re.compile(
            r"(?:은|는|이|가|도|리가|할 수)"
            r"없(?:습니다|다|소|사옵니다|었습니다|었다|었사옵니다)"
        ),
    ),
    (
        "rendered_missing_exist_stem_before_bare_formal",
        re.compile(
            r"(?:에|고)(?:습니다|사옵니다|소|다)"
            r"(?=$|[\s.!?…。])"
        ),
    ),
    (
        "rendered_negative_stem_before_past_ha",
        re.compile(r"않(?:했습니다|했다)"),
    ),
    (
        "rendered_exist_stem_before_full_ha",
        re.compile(
            r"있(?:합니다|한다|하옵니다|하겠습니다|"
            r"하겠사옵니다|하겠다|하겠소)"
        ),
    ),
    (
        "rendered_benefit_subject_before_past_ha",
        re.compile(r"도움이(?:했습니다|했다)"),
    ),
    (
        "rendered_action_stem_before_full_future_ha",
        re.compile(
            r"(?:보이|맡)하(?:겠습니다|겠다|겠소|겠사옵니다)"
        ),
    ),
    (
        "rendered_decision_stem_before_full_propositive",
        re.compile(r"내리(?:합시다|하자)"),
    ),
    (
        "rendered_question_topic_missing_space",
        re.compile(
            r"(?:것은|것이)(?:어떻습니까|어떠한가|어떠하오|"
            r"어떠하옵니까)"
        ),
    ),
    (
        "rendered_question_predicate_double_terminal",
        re.compile(
            r"(?:어떻습니까|어떠한가|어떠하오|어떠하옵니까)"
            r"(?:일까요|일까|입니까|일까 하오|이겠지요|이리라|이겠지)"
        ),
    ),
    (
        "rendered_persona_relative_clause_missing_space",
        re.compile(r"다스리는(?:소승|나|저|소인|이 몸)"),
    ),
    (
        "rendered_object_phrase_missing_space",
        re.compile(r"준비를(?:하지|해야만)"),
    ),
    (
        "rendered_command_auxiliary_missing_space",
        re.compile(
            r"(?:맡겨|떠받쳐|검토해)"
            r"(?:주시오|다오|주십시오|주소서|주시옵소서)"
        ),
    ),
    (
        "rendered_big_problem_copula_allomorph",
        re.compile(r"큰일이(?:습니다|사옵니다)"),
    ),
    (
        "rendered_finite_literal_before_duplicate_da",
        re.compile(r"종료됩니다다"),
    ),
    (
        "rendered_double_yo_terminal",
        re.compile(r"요(?:요|군)(?=$|[\s.!?…。])"),
    ),
    (
        "rendered_double_da_terminal",
        re.compile(
            r"(?:합니다|습니다|옵니다|했습니다|사옵니다|"
            r"했다|한다|이다|였다|았다|었다|"
            r"합시다|드립니다|것입니다)"
            r"(?:여|다)(?=$|[\s.!?…。])"
        ),
    ),
    (
        "rendered_negative_ha_collision",
        re.compile(r"못하하지"),
    ),
    (
        "rendered_give_past_collision",
        re.compile(r"(?:입혀|해) 주(?:했습니다|했다)"),
    ),
    (
        "rendered_bare_suffix_after_particle",
        re.compile(r"[은는이가에고도](?:습니다|사옵니다)(?=$|[\s.!?…。])"),
    ),
    (
        "rendered_hae_before_full_propositive",
        re.compile(r"해(?:합시다|하자)"),
    ),
    (
        "rendered_missing_space_je_him",
        re.compile(r"제힘"),
    ),
    (
        "rendered_missing_space_deung_hyeopryeok",
        re.compile(r"등의협력"),
    ),
    (
        "rendered_missing_space_military_hyeopryeok",
        re.compile(r"군사적협력"),
    ),
    (
        "rendered_missing_space_seong_deung",
        re.compile(
            r"성등(?=(?:의|을|은|이|과|으로)?(?:$|[\s,·]))"
        ),
    ),
    (
        "rendered_predicative_stem_before_copula",
        re.compile(
            r"(?:듯하|보류하|짓고 싶)"
            r"(?:입니다|이오|이옵니다|이니라)"
        ),
    ),
    (
        "rendered_parenthesized_particle_placeholder",
        re.compile(
            r"\((?:이|가|은|는|을|를|와|과|으|로)\)"
            r"(?:가|는|를|과|로)?"
        ),
    ),
    (
        "rendered_comma_missing_space",
        re.compile(r"[,，](?=[가-힣])"),
    ),
    (
        "rendered_person_reflexive_redundancy",
        re.compile(r"(?:소승|소인|나|저|이 몸|\ue000)\s*본인"),
    ),
    (
        "rendered_question_marker_collision",
        re.compile(r"[?？](?=[가-힣])"),
    ),
    (
        "rendered_hada_copula_collision",
        re.compile(r"하(?:입니다|이다|이오)"),
    ),
    (
        "rendered_novel_high_confidence_collision",
        re.compile(
            r"(?:"
            r"예정이(?:으므로|으니)|"
            r"여기까지로(?:합니다|한다|하옵니다)|"
            r"약속드리(?:합니다|한다|하옵니다)|"
            r"는군(?:입니다|다|이오|이옵니다|이니라)|"
            r"찾아오셨(?:했습니다|했다)|"
            r"조정에서사자|"
            r"꼭(?:아버님|어머님|할아버님|할머님)|"
            r"나왔했다|"
            r"지시해 주사옵니다|"
            r"하주(?:시오|십시오|소서)|"
            r"내키지 않지 않|"
            r"하고(?:소승|소인|나|저|이 몸)|"
            r"아니없(?:습니다|다|소|사옵니다)|"
            r"생각이신(?:입니까|인가|이오|이옵니까)|"
            r"없하지 않|"
            r"가보를(?:소승|소인|나|저|이 몸)|"
            r"따위없|"
            r"감사하하고|"
            r"싶은 법다|"
            r"그런 뜻다|"
            r"좋것(?:입니다|이다|이니라)|"
            r"아쉽(?:입니다|이오|이옵니다)|"
            r"\ue000—\ue000|"
            r"웃음(?:으세요|어라|으시오|으시옵소서|습니다|는다|사옵니다)|"
            r"그러고 보니(?:아버님|어머님|할아버님|할머님|누님|형님|"
            r"쇼군님|주군|스님|그대|너|당신|자네|숙부님|숙모님|"
            r"도련님|아가씨|귀하|귀공|원숭이|네놈)|"
            r"말하며(?:었습니다|었다)|"
            r"중요하다고생각|"
            r"말인(?:일까요|일까|입니까|일까 하오)|"
            r"이름명(?:습니다|다|사옵니다)|"
            r"진행 중다|예정다|"
            r"(?:기쁜|해 오던|고마울 따름)일?(?:습니다|다|사옵니다)|"
            r"이이름놈다|일번창은(?:소승|나|저|소인|이 몸)다|"
            r"향(?:습니다|는다|사옵니다)|"
            r"삼한다|"
            r"시달리(?:입니다|있소|있다)|"
            r"없없(?:겠지요|으리|겠소|겠사옵니다)|"
            r"다스리하겠|성주인(?:소승|나|저|소인|이 몸)|"
            r"짓눌리하겠|맞서(?:습니다|다|사옵니다)|"
            r"열리하지|싸우(?:습니다|는다|사옵니다)|"
            r"날이 오하겠|"
            r"계책이 있(?:들으세요|들어라|들어 주십시오|들어 주시오|"
            r"부디 들어 주소서|받아들여 주시오|들어다오)|"
            r"걸리(?:합니다|한다|하옵니다)|"
            r"보이(?:합시다|하자)|겪하겠|돌리이겠|"
            r"해야 하(?:이겠|인가)|"
            r"송구하없|줄이(?:합시다|하자)|"
            r"건의드리(?:합니다|한다|하옵니다)|"
            r"이루하겠|않(?:입니다|있소|있다)|있(?:했습니다|했다)|"
            r"되었(?:했습니다|했다)|"
            r"(?:유의|건설|착수)하(?:하라|하십시오|해 주)|"
            r"일하힘쓰|힘쓰(?:합니다|한다|하옵니다|합시다|하자|"
            r"하겠습니다|하겠다|하겠소|하겠사옵니다|하지)|"
            r"발생하하고|않안 됩니다네요|"
            r"경계하주의해|방해하주겠|신중하주의해|"
            r"천명이(?:입니다|있소|있다)|"
            r"이상적이(?:입니다|이오|이옵니다|이니라)|"
            r"군이(?:입니다|있소|있다)|"
            r"보이(?:입니다|이오)|곳이(?:입니다|있소|있다)|"
            r"사이이옵니다|움직임이(?:입니다|있소|있다)|"
            r"틀림없인가|있인가|어렵인가"
            r")"
        ),
    ),
    (
        "rendered_selector_side_role_smell",
        re.compile(r"\ue000\s*측(?:은|는|이|가|을|를|의|에)?"),
    ),
)

# High-confidence blind spots found by rendering the first canonicalized
# candidate again.  Keep this as an independent post-canonical layer: these
# strings were not all present in the A4 morph discovery input and therefore
# cannot be covered by that exact segment-hash contract.
POST_CANONICAL_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("missing_space_su_eop", re.compile(r"수없(?:습니다|다|사옵니다|소)")),
    (
        "missing_space_go_saenggak",
        re.compile(r"고생각(?:합니다|한다|하옵니다|하오)"),
    ),
    (
        "copula_i_plus_full_hada",
        re.compile(
            r"(?:기분|바|뜻|의미|모양|상태|상황|각오|영광|농담|듯)"
            r"이(?:합니다|한다|하옵니다|하오)"
        ),
    ),
    (
        "bat_plus_full_hada",
        re.compile(
            r"(?:인정받|보답받|대접받|보호받)"
            r"(?:합니다|한다|하옵니다|하오)"
        ),
    ),
    (
        "stem_plus_full_hada",
        re.compile(
            r"(?:이루어 내|보여 드리|이어 보이|만들어 보이|"
            r"갖추|손보|불리|일컬어져|느껴지|되어 있|되어지)"
            r"하(?:겠습니다|겠다|겠소|겠사옵니다|"
            r"합니다|한다|하옵니다|하오)"
        ),
    ),
    ("deut_ha_saenggak", re.compile(r"듯하생각")),
    (
        "coda_noun_bare_ending",
        re.compile(
            r"(?:농담|영광|금물|동맹|상황|모양|놈|것|계절|마지막|"
            r"일|명령|소승|도련님|네놈|군|말|중단|발생|요청|"
            r"제압|달성|향|청|전법)"
            r"(?:다|습니다|사옵니다|네|군요|군|여)(?![가-힣])"
        ),
    ),
    (
        "deut_bare_copula",
        re.compile(r"듯(?:입니다|다|이오)(?![가-힣])"),
    ),
    (
        "jyeo_bare_ending",
        re.compile(r"일컬어져(?:습니다|다|사옵니다)"),
    ),
    ("double_question_copula", re.compile(r"괜찮은가일까요")),
    (
        "dynamic_persona_missing_space",
        re.compile(
            r"(?:에게|기세로)귀공|"
            r"(?:앞으로도|그야말로|분명)"
            r"(?:소승|나|저|소인|이 몸)|"
            r"(?:에게|에|로|부터)"
            r"(?:소승|나|저|소인|이 몸)\s+자신"
        ),
    ),
    (
        "bare_da_after_coda_role",
        re.compile(r"(?:영광|농담|금물|동맹|상황|모양|명령|전법)다"),
    ),
    (
        "missing_space_castle_action",
        re.compile(r"성(?:공략|침공|방어|구원)"),
    ),
    ("broken_knowledge_conditional", re.compile(r"조예가다면")),
    (
        "negative_double_lexeme",
        re.compile(r"(?:않없|없못하|않못하)"),
    ),
    (
        "broken_seems_past",
        re.compile(r"뻔였(?:습니다|지요|다|소|사옵니다)"),
    ),
    ("broken_hurry_negative", re.compile(r"서둘러지 않")),
    ("missing_space_reward_review", re.compile(r"은상의검토")),
    (
        "past_stem_plus_second_past",
        re.compile(
            r"(?:발생하여|붙잡아|정리되어|완성되어)"
            r"(?:했|했다|했습니다)"
        ),
    ),
    (
        "double_style_terminal",
        re.compile(
            r"(?:뻔했소|뻔했다|뻔했습니다)"
            r"(?:였습니다|였다|이었습니다)"
        ),
    ),
    (
        "formal_terminal_plus_saenggak",
        re.compile(r"(?:하옵니다|합니다)생각"),
    ),
    ("clan_ro_particle", re.compile(r"가문로(?:부터|향해|가|는|를|의)?")),
    ("broken_eotteoh_future", re.compile(r"어떻이겠")),
    ("broken_council_decision", re.compile(r"군의를 열판단")),
    ("thing_bare_da", re.compile(r"것다(?![가-힣])")),
    (
        "dynamic_persona_modifier_spacing",
        re.compile(r"(?:소승|나|저|소인|이 몸)(?:따위|같은)"),
    ),
    (
        "dynamic_talent_role_collision",
        re.compile(
            r"(?:기개가 엿보이는|뛰어난|재능을 꽃피우지 못한|"
            r"재주 있는|재능을 갖춘)\s*\ue000\s*방책|"
            r"지도해 주면하|괜찮으신지일|좋다입니까"
        ),
    ),
    (
        "dynamic_persona_budi_boundary",
        re.compile(r"부디(?:소승|나|저|소인|이 몸)(?:\s*에게)?"),
    ),
    (
        "dynamic_persona_concessive_boundary",
        re.compile(r"외람되오나(?:소승|나|저|소인|이 몸)"),
    ),
    (
        "dative_verb_missing_space",
        re.compile(r"에게(?:맡겨|명해)"),
    ),
    (
        "eodeo_second_past",
        re.compile(r"얻어(?:했다|했습니다)"),
    ),
    ("saeroi_gundan_missing_space", re.compile(r"새로이군단")),
    (
        "double_desire_terminal",
        re.compile(r"얻어 가고 싶은 것입니다[.] 그렇군"),
    ),
    ("broken_yeonyeon_negative", re.compile(r"연연해지 않")),
    ("broken_gatchwo_past", re.compile(r"갖춰습니다")),
    ("broken_naseo_propositive", re.compile(r"나서합시다")),
    (
        "dynamic_persona_topic_boundary",
        re.compile(
            r"(?:은|는)(?:소승|나|저|소인|이 몸)"
        ),
    ),
    (
        "dynamic_honorific_activity_boundary",
        re.compile(r"(?:님|의)활약"),
    ),
    (
        "duplicate_style_past_terminal",
        re.compile(
            r"많으셨습니다(?:였)?습니다|많으셨습니다였다|수고하였소였습니다"
        ),
    ),
    ("missing_space_bandeusi_gidae", re.compile(r"반드시기대")),
    ("instrumental_full_hada", re.compile(r"힘으로합니다")),
    (
        "boi_future_spacing",
        re.compile(r"보이 하(?:겠습니다|겠다|겠소|겠사옵니다)"),
    ),
    (
        "bara_terminal_collision",
        re.compile(r"바라(?:습니다|는다|사옵니다)"),
    ),
    (
        "formal_terminal_reaction_collision",
        re.compile(
            r"(?:없습니다|없다|없소|없사옵니다)[.] 그렇군요"
        ),
    ),
    ("duplicate_war_object", re.compile(r"전쟁은\s*전쟁을")),
    ("broken_return_terminal", re.compile(r"오합니다")),
    ("persona_iroda_allomorph", re.compile(r"(?:나|저)이로다")),
    (
        "auxiliary_request_missing_space",
        re.compile(r"기울여(?:주시오|다오|주십시오|주소서)"),
    ),
    (
        "target_question_terminal_collision",
        re.compile(r"목표로(?:합니다|한다|하옵니다)[?]"),
    ),
    (
        "possessive_nominal_missing_space",
        re.compile(r"(?:님|의)(?:기대|무운|은혜|하명)"),
    ),
    (
        "particle_existence_collision",
        re.compile(r"일(?:에|이)(?:입니다|있소|있다)"),
    ),
    (
        "succession_sentence_collision",
        re.compile(r"안심하십시오주시오|당주했습니다"),
    ),
    (
        "show_full_hada_collision",
        re.compile(r"보여(?:하겠습니다|하겠다|하겠소|하겠사옵니다)"),
    ),
    (
        "appointment_terminal_collision",
        re.compile(r"되었다(?:것입니다|것이다|것이옵니다)"),
    ),
    (
        "negative_auxiliary_collision",
        re.compile(r"해지 않"),
    ),
    (
        "underestimate_copula_collision",
        re.compile(r"얕보인다(?:이겠지요|이리라|이겠지)"),
    ),
    (
        "shortage_situation_collision",
        re.compile(r"부족하지 않는다상황"),
    ),
    (
        "future_terminal_collision",
        re.compile(r"앞날은 없다(?:지요|군|네요|이지요)"),
    ),
    (
        "loyalty_terminal_collision",
        re.compile(r"여기까지라(?:하겠습니다|하겠다|하자)"),
    ),
    (
        "double_opinion_predicate",
        re.compile(r"봅니다(?:생각합니다|생각한다|생각하옵니다|생각하오)"),
    ),
    (
        "double_permission_terminal",
        re.compile(
            r"보아도(?:좋습니다|좋다|좋소|좋사옵니다)"
            r"(?:이겠지요|이리라|이겠지)"
        ),
    ),
    (
        "good_future_terminal_collision",
        re.compile(
            r"좋(?:습니다|다|소|사옵니다)"
            r"(?:이겠지요|이리라|이겠지)"
        ),
    ),
    (
        "appoint_propositive_collision",
        re.compile(r"내린다고(?:합시다|하자|하겠소|하겠습니다)"),
    ),
    (
        "response_negative_collision",
        re.compile(r"응해 주지하지 않"),
    ),
    (
        "intention_opinion_collision",
        re.compile(
            r"맡기고자 하(?:생각합니다|생각한다|생각하옵니다|생각하오)"
        ),
    ),
    (
        "instrumental_hada_missing_space",
        re.compile(r"(?:주인|곳|것)으로(?:하겠습니다|하겠다|하자|하라|하지)"),
    ),
    (
        "entrust_missing_space",
        re.compile(r"(?:뒷일|지원)은맡겨|내게맡겨"),
    ),
    (
        "command_missing_space",
        re.compile(r"(?:행동|선동)을명해"),
    ),
    (
        "confirm_missing_space",
        re.compile(r"(?:상황|세력)을확인"),
    ),
    (
        "negative_bound_missing_space",
        re.compile(r"늦춰서는(?:안|아니)"),
    ),
    (
        "achievement_predicate_missing_space",
        re.compile(r"활약을(?:하지|해야)"),
    ),
    ("mission_missing_space", re.compile(r"설득하는임무")),
    ("gratitude_command_missing_space", re.compile(r"고마운지휘")),
    ("answer_missing_space", re.compile(r"좋은답변")),
    ("castle_modifier_missing_space", re.compile(r"어려운성")),
    ("person_epithet_missing_space", re.compile(r"높은스에")),
    (
        "honorific_modifier_missing_space",
        re.compile(
            r"(?:주신|준)(?:아버님|어머님|할아버님|할머님|누님|형님|"
            r"쇼군님|주군|스님|그대|너|당신|귀공|귀하)"
        ),
    ),
    ("desire_negative_collision", re.compile(r"바랄하지")),
    (
        "attributive_future_collision",
        re.compile(r"(?:만들|할)하겠"),
    ),
    (
        "progress_future_collision",
        re.compile(r"진행될(?:이겠지요|이리라|이겠지)"),
    ),
    (
        "belief_seems_collision",
        re.compile(r"믿고는듯"),
    ),
    (
        "guard_negative_collision",
        re.compile(r"방심해서는하지"),
    ),
    (
        "general_negative_collision",
        re.compile(r"장수가(?:지 않사옵니다|지 않는다|지 않습니다)"),
    ),
    ("malformed_negative_boundary", re.compile(r"알아야 하안|안 되늘")),
    (
        "reviewed_spacing_collision",
        re.compile(
            r"우리가받|그곳을비|더는손쓸|싸움을그만|"
            r"언변으로(?:그분|그자|누님|도련님|쇼군님|숙모님|숙부님|"
            r"스님|아가씨|아버님|어머님|원숭이|주군|할머님|"
            r"할아버님|형님)|화승총으로노부나가|살날|젊은것|"
            r"번영을약속|반드시네놈|입니다만우리|지시를받|"
            r"부족하여는현재|최대한의경계|군단에맡겨|"
            r"공격은하옵니다|향해는다|"
            r"지시를(?:다오|주소서|주시오|주십시오)|"
            r"해야만(?:안|아니)|방안도검토|승전보를기대|"
            r"수밖에없|사로잡히고했|소임을맡겨|실행을허가|"
            r"빼내기를 위한 한 수로하|군을대관|신설을검토|"
            r"꼭논공행상에모습|성과를거두|그자를알현|"
            r"인근의아군|것으로생각"
        ),
    ),
    (
        "reviewed_sentence_collision",
        re.compile(
            r"것이군겠|보여서는하다|"
            r"(?:것이|것도)(?:좋습니다|좋다|좋소|좋사옵니다)[?]|"
            r"(?:출진 여부는|판단은)맡기|"
            r"이렇다 할 명장은지 않|"
            r"그곳 공략에 도움이(?:하겠다|하자)|"
            r"없지는하지 않|어떠한가하|볼만하"
        ),
    ),
)


class CallAssemblyBoundaryError(ValueError):
    """Raised when the call-assembly audit cannot be evaluated safely."""


class SyntheticSelectorRenderer(AUDIT.TerminalRenderer):
    """Render calls plus the fixed selector representatives from Ghidra."""

    def render(
        self,
        coordinate: tuple[int, int],
        trail: tuple[tuple[int, int], ...] = (),
    ) -> tuple[str, ...]:
        if coordinate in trail:
            return ("",)
        if coordinate in self.cache:
            return self.cache[coordinate]
        record = self.records.get(coordinate)
        if record is None:
            raise CallAssemblyBoundaryError(
                f"VM edge target is absent: {coordinate[0]}:{coordinate[1]}"
            )
        components = AUDIT.tolerant_decode_record(record)
        literals = tuple(
            literal.text for literal in AUDIT.parse_record_literals(record)
        )
        jump_targets = tuple(
            tuple(component["target"])
            for component in components
            if component["kind"] == "jump"
        )
        if jump_targets:
            variants = unique_ordered(
                variant
                for target in jump_targets
                for variant in self.render(target, trail + (coordinate,))
            )[: AUDIT.MAX_VARIANTS_PER_RECORD]
            self.cache[coordinate] = variants
            return variants

        states = ("",)
        for component in components:
            kind = str(component["kind"])
            if kind == "literal_boundary":
                additions = (literals[int(component["slot"])],)
            elif kind == "call":
                additions = self.render(
                    tuple(component["target"]),
                    trail + (coordinate,),
                )
            elif kind == "selector":
                selector_property = component.get("property")
                key = (
                    int(component["group"]),
                    (
                        int(selector_property)
                        if selector_property is not None
                        else -1
                    ),
                )
                additions = SYNTHETIC_SELECTOR_VALUES.get(
                    key,
                    (UNKNOWN_OUTPUT_SELECTOR_SENTINEL,),
                )
            elif kind == "output_control":
                additions = (chr(int(component["code"])),)
            else:
                continue
            states = tuple(
                left + right
                for left in states
                for right in additions
            )[: AUDIT.MAX_VARIANTS_PER_RECORD]
        variants = unique_ordered(states)
        self.cache[coordinate] = variants
        return variants


@dataclass(frozen=True)
class CallAssemblyIssue:
    resource: str
    category: str
    block_id: int
    record_id: int
    component_index: int
    literal_id: int | None
    call_target: str | None
    rule: str
    previous_literal_sha256: str | None
    call_variant_sha256: str | None
    next_literal_sha256: str | None
    assembled_sha256: str
    previous_literal: str | None = None
    call_variant: str | None = None
    next_literal: str | None = None
    assembled: str | None = None


@dataclass(frozen=True)
class CallAssemblyResource:
    resource: str
    path: str
    sha256: str
    record_count: int
    decoded_record_count: int
    call_record_count: int
    call_site_count: int
    unique_call_target_count: int
    rendered_call_variant_count: int
    assembled_record_variant_count: int
    synthetic_selector_call_record_count: int
    issues: tuple[CallAssemblyIssue, ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CallAssemblyBoundaryError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_signature_line(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def source_free_finding_mapping(
    value: Mapping[str, Any] | CallAssemblyIssue,
) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return {
            field: value.get(field)
            for field in SOURCE_FREE_FINDING_FIELDS
        }
    return {
        field: getattr(value, field)
        for field in SOURCE_FREE_FINDING_FIELDS
    }


def finding_signature_sha256(
    value: Mapping[str, Any] | CallAssemblyIssue,
) -> str:
    return sha256_bytes(
        canonical_signature_line(
            source_free_finding_mapping(value)
        ).encode("ascii")
    )


def false_signature_contract_entry_digest(
    entries: Iterable[Mapping[str, Any]],
) -> str:
    body = "\n".join(
        canonical_signature_line(entry)
        for entry in sorted(
            entries,
            key=lambda row: (
                str(row["review_class"]),
                str(row["rule"]),
                int(row["block_id"]),
                int(row["record_id"]),
                str(row["finding_signature_sha256"]),
            ),
        )
    )
    return sha256_bytes(body.encode("ascii"))


def load_pk_false_signature_contract() -> frozenset[str]:
    payload = json.loads(
        PK_FALSE_SIGNATURE_CONTRACT_PATH.read_text(encoding="utf-8")
    )
    require(
        payload.get("schema") == PK_FALSE_SIGNATURE_CONTRACT_SCHEMA,
        "unexpected PK false-signature contract schema",
    )
    require(
        payload.get("source_free") is True
        and payload.get("private_text_included") is False,
        "PK false-signature contract is not source-free",
    )
    application_contract = payload.get("application_contract", {})
    require(
        application_contract
        == {
            "candidate_file_hash_required": False,
            "coordinate_rule_only_suppression_forbidden": True,
            "exact_finding_signature_required": True,
            "rule_only_suppression_forbidden": True,
        },
        "unexpected PK false-signature application contract",
    )
    require(
        payload.get("review_class_counts")
        == PK_FALSE_SIGNATURE_REVIEW_CLASS_COUNTS,
        "unexpected PK false-signature review counts",
    )
    require(
        payload.get("rule_counts") == PK_FALSE_SIGNATURE_RULE_COUNTS,
        "unexpected PK false-signature rule counts",
    )
    require(
        payload.get("coordinate_rule_sha256")
        == PK_FALSE_SIGNATURE_COORDINATE_RULE_SHA256,
        "unexpected PK false-signature coordinate/rule digest",
    )
    entries = tuple(payload.get("entries", ()))
    require(
        len(entries) == PK_FALSE_SIGNATURE_ENTRY_COUNT
        and payload.get("entry_count") == PK_FALSE_SIGNATURE_ENTRY_COUNT,
        "unexpected PK false-signature entry count",
    )
    expected_keys = frozenset(
        {
            *SOURCE_FREE_FINDING_FIELDS,
            "finding_signature_sha256",
            "review_class",
        }
    )
    for entry in entries:
        require(
            frozenset(entry) == expected_keys,
            "unexpected PK false-signature entry fields",
        )
        require(
            entry.get("resource") == "pk_msggame",
            "non-PK false-signature entry",
        )
        require(
            entry.get("review_class")
            in PK_FALSE_SIGNATURE_REVIEW_CLASS_COUNTS,
            "unexpected PK false-signature review class",
        )
        require(
            entry.get("finding_signature_sha256")
            == finding_signature_sha256(entry),
            "PK false-signature finding digest mismatch",
        )
    require(
        false_signature_contract_entry_digest(entries)
        == PK_FALSE_SIGNATURE_ENTRY_SHA256
        == payload.get("entry_sha256"),
        "PK false-signature contract digest mismatch",
    )
    signatures = frozenset(
        str(entry["finding_signature_sha256"])
        for entry in entries
    )
    require(
        len(signatures) == PK_FALSE_SIGNATURE_ENTRY_COUNT,
        "duplicate PK false-signature finding digest",
    )
    return signatures


BASE_MORPH_PAIR_CONTRACT = load_base_morph_pair_contract()
PK_REVIEWED_FALSE_SIGNATURES = load_pk_false_signature_contract()


def is_reviewed_false_signature(value: CallAssemblyIssue) -> bool:
    return (
        value.resource == "pk_msggame"
        and finding_signature_sha256(value)
        in PK_REVIEWED_FALSE_SIGNATURES
    )


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def unique_ordered(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def normalize_visible(value: str) -> str:
    return "".join(
        character
        for character in value
        if not unicodedata.category(character).startswith("C")
    )


def normalize_rendered_visible(value: str) -> str:
    """Remove VM controls while preserving displayed layout boundaries."""

    return "".join(
        character
        for character in value
        if character in "\r\n\t"
        or character == UNKNOWN_OUTPUT_SELECTOR_SENTINEL
        or not unicodedata.category(character).startswith("C")
    )


def rendered_morph_pair_segments(value: str) -> tuple[tuple[str, str], ...]:
    """Return the exact normalized segment hashes used by Kiwi discovery."""

    visible = normalize_rendered_visible(value).replace(
        UNKNOWN_OUTPUT_SELECTOR_SENTINEL,
        "이름",
    )
    segments: list[tuple[str, str]] = []
    for segment in re.split(r"[\n.!?…]+", visible):
        segment = segment.strip()
        if len(segment) < 3 or re.search(r"[가-힣]", segment) is None:
            continue
        segments.append((segment, sha256_bytes(segment.encode("utf-8"))))
    return tuple(segments)


def reviewed_morph_pair_collisions(
    resource: str,
    coordinate: tuple[int, int],
    assembled: str,
) -> tuple[tuple[str, str], ...]:
    """Match source-free reviewed segment hashes without a Kiwi dependency."""

    if resource != "base_msggame":
        return ()
    contract = BASE_MORPH_PAIR_CONTRACT.get(coordinate, {})
    matches: list[tuple[str, str]] = []
    for segment, segment_sha256 in rendered_morph_pair_segments(assembled):
        for morph_category in contract.get(segment_sha256, ()):
            if (
                coordinate,
                morph_category,
                segment_sha256,
            ) in BASE_MORPH_PAIR_EXACT_ALLOWLIST:
                continue
            matches.append((morph_category, segment))
    return tuple(matches)


def is_hangul(character: str) -> bool:
    codepoint = ord(character)
    return (
        0xAC00 <= codepoint <= 0xD7A3
        or 0x1100 <= codepoint <= 0x11FF
        or 0x3130 <= codepoint <= 0x318F
    )


def directly_continues_with_hangul(value: str) -> bool:
    """Return whether a following literal starts a same-sentence Hangul tail."""

    for character in value:
        if character in "\r\n":
            return False
        if character.isspace() or unicodedata.category(character).startswith("C"):
            continue
        if character in SENTENCE_BOUNDARY_PUNCTUATION:
            return False
        return is_hangul(character)
    return False


def finite_output(value: str) -> bool:
    normalized = normalize_visible(value).strip()
    return FINITE_OUTPUT_RE.search(normalized) is not None


def local_stem_rules(previous: str, variant: str) -> tuple[str, ...]:
    """Classify high-confidence literal-stem/call-suffix incompatibilities."""

    if (
        not previous
        or not variant
        or previous[-1].isspace()
        or variant[0].isspace()
        or unicodedata.category(previous[-1]).startswith("C")
        or unicodedata.category(variant[0]).startswith("C")
    ):
        return ()
    visible_previous = normalize_visible(previous)
    left_has_trailing_space = previous[-1].isspace()
    left = visible_previous.rstrip()
    right = normalize_visible(variant).lstrip()
    rules: list[str] = []

    if left.endswith("하") and re.match(
        r"^(?:합니다|한다|하옵니다|했습니다|했다|"
        r"하겠습니다|하겠다|하겠소|하겠사옵니다|합시다|하자|"
        r"하고 있습니다|하고 있다|하고 있사옵니다|"
        r"하십시오|하라|해 주십시오|해 주시오|해 주시옵소서|"
        r"하시오|하시라)",
        right,
    ):
        rules.append("trailing_ha_before_full_ha")
    if left.endswith("하") and right.startswith("습니다"):
        rules.append("trailing_ha_before_bare_formal")
    if left.endswith("겠") and re.match(
        r"^(?:합니다|한다|하옵니다|했습니다|했다)",
        right,
    ):
        rules.append("trailing_get_before_full_ha")
    if (
        left.endswith("주시")
        and not left.endswith("예의주시")
        and re.match(
            r"^(?:합니다|한다|하옵니다|"
            r"하지 않습니다|하지 않는다|하지 않사옵니다)",
            right,
        )
    ):
        rules.append("request_stem_before_full_ha")
    if left.endswith("모시") and re.match(
        r"^(?:합니다|한다|하옵니다)",
        right,
    ):
        rules.append("mosi_stem_before_full_ha")
    if left.endswith("알겠") and re.match(r"^(?:했습니다|했다)", right):
        rules.append("alget_before_past_ha")
    if left.endswith("받아들이") and right.startswith("받"):
        rules.append("accept_before_receive")
    if left.endswith("있") and right.startswith("입니다"):
        rules.append("exist_stem_before_copula")
    if left.endswith("되") and right.startswith("습니다"):
        rules.append("become_stem_before_bare_formal")
    if left.endswith("없") and right.startswith("없습니다"):
        rules.append("absent_stem_before_full_absent")
    if left.endswith("않") and right.startswith("이지요"):
        rules.append("negative_stem_before_copula")
    if left.endswith(("시키", "내")) and right.startswith("하지"):
        rules.append("causative_stem_before_negative_ha")
    if left.endswith("주") and right.startswith(("주시오", "주십시오")):
        rules.append("give_stem_before_full_give")
    if (
        left.endswith(
            (
                "은",
                "는",
                "이",
                "가",
                "도",
                "리가",
                "할 수",
            )
        )
        and not left_has_trailing_space
        and re.match(
            r"^없(?:습니다|다|소|사옵니다|었습니다|었다|었사옵니다)",
            right,
        )
    ):
        rules.append("missing_space_before_full_absent")
    if (
        left.endswith(("에", "고"))
        and right in {"습니다", "다", "소", "사옵니다"}
    ):
        rules.append("missing_exist_stem_before_bare_formal")
    if left.endswith("않") and right in {"했습니다", "했다"}:
        rules.append("negative_stem_before_past_ha")
    if left.endswith(("었", "았")) and right in {"했습니다", "했다"}:
        rules.append("past_stem_before_past_ha")
    if left.endswith("있") and right in {"했습니다", "했다"}:
        rules.append("exist_stem_before_past_ha")
    if left.endswith("있") and right in {
        "합니다",
        "한다",
        "하옵니다",
        "하겠습니다",
        "하겠사옵니다",
        "하겠다",
        "하겠소",
    }:
        rules.append("exist_stem_before_full_ha")
    if left.endswith("도움이") and right in {"했습니다", "했다"}:
        rules.append("benefit_subject_before_past_ha")
    if left.endswith(
        (
            "보이",
            "맡",
            "다스리",
            "짓눌리",
            "겪",
            "이루",
            "오",
        )
    ) and right in {
        "하겠습니다",
        "하겠다",
        "하겠소",
        "하겠사옵니다",
    }:
        rules.append("action_stem_before_full_future_ha")
    if left.endswith("내리") and right in {"합시다", "하자"}:
        rules.append("decision_stem_before_full_propositive")
    if left.endswith(("것은", "것이")) and right in {
        "어떻습니까",
        "어떠한가",
        "어떠하오",
        "어떠하옵니까",
    }:
        rules.append("question_topic_missing_space")
    if left.endswith("다스리는") and right in {
        "소승",
        "나",
        "저",
        "소인",
        "이 몸",
    }:
        rules.append("persona_relative_clause_missing_space")
    if left.endswith("준비를") and right.startswith(
        ("하지", "해야만")
    ):
        rules.append("object_phrase_missing_space")
    if left.endswith(("맡겨", "떠받쳐", "검토해")) and right.startswith(
        ("주시오", "다오", "주십시오", "주소서", "주시옵소서")
    ):
        rules.append("command_auxiliary_missing_space")
    if left.endswith("하") and right.startswith(
        ("주시오", "주십시오", "주소서", "주시옵소서")
    ):
        rules.append("ha_before_give_command")
    if left.endswith("큰일이") and right in {"습니다", "사옵니다"}:
        rules.append("big_problem_copula_allomorph")
    if left.endswith("종료됩니다") and right == "다":
        rules.append("finite_literal_before_duplicate_da")
    if left.endswith("못하") and right.startswith("하지"):
        rules.append("negative_ha_collision")
    if left.endswith("없") and right.startswith("하지 않"):
        rules.append("absent_stem_before_negative_ha")
    if left.endswith("않") and right.startswith("지 않"):
        rules.append("negative_stem_before_negative_ha")
    if left.endswith(("입혀 주", "해 주")) and right in {
        "했습니다",
        "했다",
    }:
        rules.append("give_past_collision")
    if left.endswith("매진해") and right in {"합시다", "하자"}:
        rules.append("hae_before_full_propositive")
    if left.endswith("힘쓰") and re.match(
        r"^(?:합니다|한다|하옵니다|합시다|하자|"
        r"하겠습니다|하겠다|하겠소|하겠사옵니다|하지)",
        right,
    ):
        rules.append("himsseu_before_full_ha")
    if left.endswith(
        (
            "아버님",
            "어머님",
            "할아버님",
            "할머님",
            "형님",
            "누님",
            "주군님",
        )
    ) and right.startswith("님"):
        rules.append("honorific_before_honorific")
    return tuple(rules)


def next_literal_rules(variant: str, next_literal: str) -> tuple[str, ...]:
    """Return high-confidence complete-output/following-fragment collisions."""

    if not directly_continues_with_hangul(next_literal):
        return ()
    suffix = normalize_visible(variant).strip()
    following = normalize_visible(next_literal).lstrip()
    if not finite_output(suffix):
        return ()
    if (
        following.startswith("만")
        and re.search(
            r"(?:입니다|합니다|했습니다|습니다|사옵니다|옵니다|"
            r"겠습니다|겠사옵니다|하오|나이다)$",
            suffix,
        )
    ):
        return ()

    rules: list[str] = []
    if re.match(
        r"^(?:까|인가|시겠습니까|겠습니까|습니까|는가|은가|일까)"
        r"(?:[?？]|$)",
        following,
    ):
        rules.append("finite_suffix_before_question_fragment")
    if (
        re.search(
            r"(?:입니다|합니다|했습니다|습니다|사옵니다|옵니다)$",
            suffix,
        )
        and following.startswith("지만")
    ):
        rules.append("formal_finite_suffix_before_jiman")
    if following.startswith(("다!", "다！", "다?", "다？")):
        rules.append("finite_suffix_before_duplicate_da")
    if not rules:
        rules.append("finite_suffix_before_same_sentence_hangul")
    return tuple(rules)


EMPTY_DEPENDENT_LITERAL_PREFIXES = (
    "에게는",
    "에게",
    "보다",
    "만큼",
    "방문",
    "곁",
    "뜻",
    "힘",
    "의",
    "에",
    "과",
    "와",
)


def empty_dynamic_call_rules(
    components: Sequence[Mapping[str, Any]],
    component_index: int,
    target: tuple[int, int],
    variants: Sequence[str],
    previous_literal: str | None,
    next_literal: str | None,
) -> tuple[str, ...]:
    if (
        "" not in variants
        or variants == ("",)
        or next_literal is None
    ):
        return ()
    following = normalize_visible(next_literal).lstrip()
    if following.startswith(EMPTY_DEPENDENT_LITERAL_PREFIXES):
        return ("empty_dynamic_call_followed_by_dependent_literal",)
    return ()


def adjacent_literal(
    components: Sequence[Mapping[str, Any]],
    literals: Sequence[str],
    component_index: int,
    *,
    direction: int,
) -> tuple[int, str] | None:
    if direction not in {-1, 1}:
        raise ValueError("direction must be -1 or 1")
    values = (
        reversed(components[:component_index])
        if direction == -1
        else iter(components[component_index + 1 :])
    )
    for component in values:
        kind = str(component["kind"])
        if kind == "literal_boundary":
            literal_id = int(component["slot"])
            return literal_id, literals[literal_id]
        if kind not in NON_EMITTING_COMPONENTS:
            return None
    return None


def issue(
    *,
    resource: str,
    category: str,
    coordinate: tuple[int, int],
    component_index: int,
    literal_id: int | None,
    call_target: str | None,
    rule: str,
    previous_literal: str | None,
    call_variant: str | None,
    next_literal: str | None,
    assembled: str,
    include_text: bool,
) -> CallAssemblyIssue:
    return CallAssemblyIssue(
        resource=resource,
        category=category,
        block_id=coordinate[0],
        record_id=coordinate[1],
        component_index=component_index,
        literal_id=literal_id,
        call_target=call_target,
        rule=rule,
        previous_literal_sha256=(
            utf16le_sha256(previous_literal)
            if previous_literal is not None
            else None
        ),
        call_variant_sha256=(
            utf16le_sha256(call_variant)
            if call_variant is not None
            else None
        ),
        next_literal_sha256=(
            utf16le_sha256(next_literal)
            if next_literal is not None
            else None
        ),
        assembled_sha256=utf16le_sha256(assembled),
        previous_literal=previous_literal if include_text else None,
        call_variant=call_variant if include_text else None,
        next_literal=next_literal if include_text else None,
        assembled=assembled if include_text else None,
    )


def audit_resource(
    resource: str,
    path: Path,
    *,
    include_text: bool = False,
) -> CallAssemblyResource:
    records, blob_sha256 = AUDIT.records_from_path(path)
    renderer = SyntheticSelectorRenderer(records)
    findings: list[CallAssemblyIssue] = []
    decoded_record_count = 0
    call_record_count = 0
    call_site_count = 0
    rendered_call_variant_count = 0
    assembled_record_variant_count = 0
    synthetic_selector_call_record_count = 0
    call_targets: set[tuple[int, int]] = set()
    morph_contract = (
        BASE_MORPH_PAIR_CONTRACT
        if resource == "base_msggame"
        else {}
    )

    for coordinate, record in records.items():
        components = AUDIT.tolerant_decode_record(record)
        decoded_record_count += 1
        calls = tuple(
            (index, component)
            for index, component in enumerate(components)
            if component["kind"] == "call"
        )
        has_selector = any(
            str(component["kind"]) == "selector"
            for component in components
        )
        if calls:
            call_record_count += 1
            if any(
                str(component["kind"]) == "selector"
                and component.get("property") is not None
                and (
                    int(component["group"]),
                    int(component["property"]),
                ) in SYNTHETIC_SELECTOR_VALUES
                for component in components
            ):
                synthetic_selector_call_record_count += 1
        literals = tuple(
            literal.text for literal in AUDIT.parse_record_literals(record)
        )
        if calls or has_selector or coordinate in morph_contract:
            assembled_variants = unique_ordered(renderer.render(coordinate))
            assembled_record_variant_count += len(assembled_variants)

            # This is deliberately independent from local-edge checks: it
            # proves that every dynamic Cartesian record variant was
            # inspected, including selector-only records.
            for assembled in assembled_variants:
                visible = normalize_rendered_visible(assembled)
                for rule, pattern in FULL_RENDER_PATTERNS:
                    if pattern.search(visible) is None:
                        continue
                    findings.append(
                        issue(
                            resource=resource,
                            category="malformed_cartesian_rendered_string",
                            coordinate=coordinate,
                            component_index=-1,
                            literal_id=None,
                            call_target=None,
                            rule=rule,
                            previous_literal=None,
                            call_variant=None,
                            next_literal=None,
                            assembled=assembled,
                            include_text=include_text,
                        )
                    )
                for rule, pattern in POST_CANONICAL_PATTERNS:
                    if pattern.search(visible) is None:
                        continue
                    findings.append(
                        issue(
                            resource=resource,
                            category=(
                                "post_canonical_"
                                "high_confidence_collision"
                            ),
                            coordinate=coordinate,
                            component_index=-1,
                            literal_id=None,
                            call_target=None,
                            rule=rule,
                            previous_literal=None,
                            call_variant=None,
                            next_literal=None,
                            assembled=assembled,
                            include_text=include_text,
                        )
                    )
                for morph_category, segment in (
                    reviewed_morph_pair_collisions(
                        resource,
                        coordinate,
                        assembled,
                    )
                ):
                        findings.append(
                            issue(
                                resource=resource,
                                category=(
                                    "rendered_morph_pair_"
                                    "high_confidence_collision"
                                ),
                                coordinate=coordinate,
                                component_index=-1,
                                literal_id=None,
                                call_target=None,
                                rule=morph_category,
                                previous_literal=None,
                                call_variant=None,
                                next_literal=None,
                                assembled=segment,
                                include_text=include_text,
                            )
                        )
        if not calls:
            continue

        for component_index, component in calls:
            call_site_count += 1
            target_values = tuple(component["target"])
            target = (int(target_values[0]), int(target_values[1]))
            call_targets.add(target)
            target_key = f"{target[0]}:{target[1]}"
            variants = unique_ordered(renderer.render(target))
            rendered_call_variant_count += len(variants)
            previous = adjacent_literal(
                components,
                literals,
                component_index,
                direction=-1,
            )
            following = adjacent_literal(
                components,
                literals,
                component_index,
                direction=1,
            )
            literal_id = previous[0] if previous is not None else None
            previous_literal = previous[1] if previous is not None else None
            next_literal = following[1] if following is not None else None

            for variant in variants:
                local = (
                    (previous_literal or "")
                    + variant
                    + (next_literal or "")
                )
                if next_literal is not None:
                    for rule in next_literal_rules(variant, next_literal):
                        findings.append(
                            issue(
                                resource=resource,
                                category=(
                                    "finite_call_output_followed_by_"
                                    "incompatible_hangul_fragment"
                                ),
                                coordinate=coordinate,
                                component_index=component_index,
                                literal_id=literal_id,
                                call_target=target_key,
                                rule=rule,
                                previous_literal=previous_literal,
                                call_variant=variant,
                                next_literal=next_literal,
                                assembled=local,
                                include_text=include_text,
                            )
                        )
                if previous_literal is not None:
                    for rule in local_stem_rules(previous_literal, variant):
                        findings.append(
                            issue(
                                resource=resource,
                                category=(
                                    "incompatible_literal_stem_call_suffix"
                                ),
                                coordinate=coordinate,
                                component_index=component_index,
                                literal_id=literal_id,
                                call_target=target_key,
                                rule=rule,
                                previous_literal=previous_literal,
                                call_variant=variant,
                                next_literal=next_literal,
                                assembled=local,
                                include_text=include_text,
                            )
                        )
            for rule in empty_dynamic_call_rules(
                components,
                component_index,
                target,
                variants,
                previous_literal,
                next_literal,
            ):
                findings.append(
                    issue(
                        resource=resource,
                        category=(
                            "empty_dynamic_call_followed_by_dependent_literal"
                        ),
                        coordinate=coordinate,
                        component_index=component_index,
                        literal_id=literal_id,
                        call_target=target_key,
                        rule=rule,
                        previous_literal=previous_literal,
                        call_variant="",
                        next_literal=next_literal,
                        assembled=(
                            (previous_literal or "")
                            + (next_literal or "")
                        ),
                        include_text=include_text,
                    )
                )

    deduplicated = {
        (
            finding.resource,
            finding.category,
            finding.block_id,
            finding.record_id,
            finding.component_index,
            finding.literal_id,
            finding.call_target,
            finding.rule,
            finding.previous_literal_sha256,
            finding.next_literal_sha256,
        ): finding
        for finding in findings
    }
    ordered = tuple(
        sorted(
            (
                finding
                for finding in deduplicated.values()
                if not is_reviewed_false_signature(finding)
            ),
            key=lambda value: (
                value.block_id,
                value.record_id,
                value.component_index,
                value.category,
                value.rule,
                value.call_variant_sha256 or "",
                value.assembled_sha256,
            ),
        )
    )
    return CallAssemblyResource(
        resource=resource,
        path=str(path.resolve()),
        sha256=blob_sha256,
        record_count=len(records),
        decoded_record_count=decoded_record_count,
        call_record_count=call_record_count,
        call_site_count=call_site_count,
        unique_call_target_count=len(call_targets),
        rendered_call_variant_count=rendered_call_variant_count,
        assembled_record_variant_count=assembled_record_variant_count,
        synthetic_selector_call_record_count=(
            synthetic_selector_call_record_count
        ),
        issues=ordered,
    )


def source_free_issue(value: CallAssemblyIssue) -> dict[str, Any]:
    payload = asdict(value)
    for key in (
        "previous_literal",
        "call_variant",
        "next_literal",
        "assembled",
    ):
        payload.pop(key, None)
    return payload


def build_report(
    resources: Sequence[CallAssemblyResource],
    *,
    include_text: bool,
) -> dict[str, Any]:
    issues = tuple(
        issue_value
        for resource in resources
        for issue_value in resource.issues
    )
    category_counts = Counter(value.category for value in issues)
    rule_counts = Counter(value.rule for value in issues)
    payload_resources = {}
    for resource in resources:
        payload_resources[resource.resource] = {
            "path": resource.path,
            "sha256": resource.sha256,
            "record_count": resource.record_count,
            "decoded_record_count": resource.decoded_record_count,
            "call_record_count": resource.call_record_count,
            "call_site_count": resource.call_site_count,
            "unique_call_target_count": resource.unique_call_target_count,
            "rendered_call_variant_count":
                resource.rendered_call_variant_count,
            "assembled_record_variant_count":
                resource.assembled_record_variant_count,
            "synthetic_selector_call_record_count":
                resource.synthetic_selector_call_record_count,
            "issue_count": len(resource.issues),
        }
    return {
        "schema": SCHEMA,
        "status": "PASS" if not issues else "FAIL",
        "issue_count": len(issues),
        "category_counts": dict(sorted(category_counts.items())),
        "rule_counts": dict(sorted(rule_counts.items())),
        "resources": payload_resources,
        "issues": [
            (
                asdict(value)
                if include_text
                else source_free_issue(value)
            )
            for value in issues
        ],
        "audit_contract": {
            "all_call_sites_enumerated": True,
            "all_call_targets_rendered": True,
            "all_call_bearing_records_cartesian_rendered": True,
            "ghidra_fixed_selector_representatives_rendered": {
                "g3_p32": "아리오카성",
                "g4_p32": "도쿠가와 가문",
            },
            "local_previous_call_next_boundaries_checked": True,
            "finite_suffix_hangul_continuation_checked": True,
            "korean_stem_allomorph_mismatches_checked": True,
            "empty_dynamic_call_dependent_literal_checked": True,
            "source_free_reviewed_morph_pair_contract_checked": True,
            "reviewed_morph_pair_exact_allowlist_count": len(
                BASE_MORPH_PAIR_EXACT_ALLOWLIST
            ),
            "pk_reviewed_false_signature_count": len(
                PK_REVIEWED_FALSE_SIGNATURES
            ),
            "literal_bodies_omitted": not include_text,
        },
        "steam_write_performed": False,
    }


def ensure_private_output(path: Path) -> None:
    resolved = path.resolve()
    tmp_root = (REPO / "tmp").resolve()
    require(
        resolved == tmp_root or tmp_root in resolved.parents,
        "--include-text output must remain below repository tmp/",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--pk", type=Path, default=DEFAULT_PK)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--include-text", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    if args.include_text:
        ensure_private_output(args.output)
    resources = (
        audit_resource(
            "base_msggame",
            args.base,
            include_text=args.include_text,
        ),
        audit_resource(
            "pk_msggame",
            args.pk,
            include_text=args.include_text,
        ),
    )
    report = build_report(resources, include_text=args.include_text)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(canonical_json(report), encoding="utf-8")
    print(
        json.dumps(
            {
                "schema": report["schema"],
                "status": report["status"],
                "issue_count": report["issue_count"],
                "category_counts": report["category_counts"],
                "resources": report["resources"],
                "output": str(args.output.resolve()),
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    return 1 if args.strict and report["issue_count"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, CallAssemblyBoundaryError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
