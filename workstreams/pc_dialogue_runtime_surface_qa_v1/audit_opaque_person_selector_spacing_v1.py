#!/usr/bin/env python3
"""Audit no-space Korean nouns after opaque dynamic selectors.

Ghidra proves that the message VM copies selector and literal UTF-16 units
verbatim and inserts no separator.  The repository honorific policy therefore
requires an explicit space between a selected person name and the Korean
honorific/dependent nouns represented here as ``gong``, ``nim``, ``nom``, and
``arae``.

The renderer is symbolic rather than Cartesian-capped.  For every Base/PK
record it propagates every possible short prefix and every lexical-selector
tail through calls and jumps.  This is sufficient to decide the exact
selector/right-literal boundary while avoiding a branch-product limit.
Default output is source-free; private text is allowed only below ``tmp``.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import sys
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
RUNTIME_AUDIT_PATH = WORKSTREAM / "audit_runtime_surface_v1.py"
GHIDRA_CONTRACT_PATH = (
    WORKSTREAM / "ghidra_selector_domain_contract.v1.json"
)
BASE_POLICY_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "build_base_batch001_segment1004.py"
)
PK_POLICY_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_full_retranslation_v0150"
    / "build_pk_batch001_segment1025.py"
)
BASE_REMEDIATION_POLICY_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_runtime_surface_remediation_v1"
    / "base_build_runtime_surface_remediation_v1.py"
)
PK_REMEDIATION_POLICY_PATH = (
    REPO
    / "workstreams"
    / "pc_dialogue_runtime_surface_remediation_v1"
    / "pk_build_runtime_surface_remediation_v1.py"
)
DEFAULT_BASE = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_remediation_v1"
    / "base"
    / "candidate"
    / "MSG"
    / "JP"
    / "msggame.bin"
)
DEFAULT_PK = (
    REPO
    / "tmp"
    / "pc_dialogue_runtime_surface_remediation_v1"
    / "pk"
    / "candidate"
    / "MSG_PK"
    / "JP"
    / "msggame.bin"
)

SCHEMA = "nobu16.kr.opaque-person-selector-spacing-audit.v1"
PERSON_LIKE_SELECTOR_GROUPS = frozenset({1, 2, 5, 6})
LEXICAL_SELECTOR_GROUPS = frozenset(range(1, 14))
WINDOW_UNITS = 8
SELECTOR_MARKERS = {
    group: chr(0xE200 + group)
    for group in LEXICAL_SELECTOR_GROUPS
}
MARKER_TO_GROUP = {
    marker: group
    for group, marker in SELECTOR_MARKERS.items()
}
OTHER_SELECTOR_MARKER = "\uE2FF"
ALL_MARKERS = frozenset(
    {*SELECTOR_MARKERS.values(), OTHER_SELECTOR_MARKER}
)
BOUNDARY_TOKENS = {
    "\uacf5": "honorific_gong",
    "\ub2d8": "honorific_nim",
    "\ub188": "hostile_nom",
    "\uc544\ub798": "dependent_arae",
    "\ubd80\ub300": "unit_budae",
    "\uc8fc\uad70": "noun_jugun",
    "\ub4f1": "dependent_deung",
    "\uad70\ub2e8": "noun_gundan",
    "\uacf5\uaca9": "action_gonggyeok",
    "\uacf5\ub7b5": "action_gongnyak",
    "\ucde8\uc784": "action_chwiim",
    "\uc694\uccad": "action_yocheong",
    "\uc7a5\uc545": "action_jangak",
    "\uc131\uc8fc": "noun_seongju",
    "\uaca9\ud30c": "action_gyeokpa",
    "\ubcf8\uc131": "noun_bonseong",
    "\uc2e4\ud589": "action_silhaeng",
    "\ud68c\uc720": "action_hoeyu",
    "\ud1b5\uc77c": "action_tongil",
    "\uac74\uc124": "action_geonseol",
    "\uc99d\ucd95": "action_jeungchuk",
    "\uc138\ub825": "noun_seryeok",
    "\uc815\ucc45": "noun_jeongchaek",
    "\uc2dc\uc124": "noun_siseol",
    "\ub530\uc704": "dependent_ttawi",
    "\ubc29\uba74": "dependent_bangmyeon",
    "\ub2f9\uc8fc": "noun_dangju",
    "\uc218\uc785": "noun_suip",
    "\ubd80\ubb38": "dependent_bumun",
    "\uc601\uc9c0": "noun_yeongji",
    "\uc678\uad50": "noun_oegyo",
    "\uc2b9\ub099": "noun_seungnak",
    "\uc0ac\uc774": "dependent_sai",
    "\ub9d0\uace0": "dependent_malgo",
    "\uc548\uc5d0\uc11c": "dependent_an",
    "\ub0b4\uc5d0\uc11c": "dependent_nae",
    "\uc8fc\ubcc0": "dependent_jubyeon",
    "\uc778\uadfc": "dependent_ingeun",
    "\uadfc\ucc98": "dependent_geuncheo",
    "\uc18c\uc18d \uad70": "noun_sosok_gun",
    "\uc218\ubcf5": "noun_subok",
    "\uc815\ub3c4": "dependent_jeongdo",
    "\ub2e8 \ud55c \uc0ac\ub78c": "carrier_single_person",
    "\ub2ec\uc131": "noun_dalseong",
    "\uc0dd\uc131\ub428": "noun_saengseong",
    "\uc0ad\uc81c\ub428": "noun_sakje",
    "\uc218\uc815\ub428": "noun_sujeong",
    "\ub2f9\uba74 \ubaa9\ud45c": "noun_dangmyeon_mokpyo",
    "\uc2e0\ubd84": "noun_sinbun",
    "\ucabd": "dependent_jjok",
    "\ucd94\uc784": "noun_chuim",
    "\uac04 ": "dependent_gan",
    "\uc544\uad70": "noun_agun",
    "\ud604\uc7ac": "carrier_hyeonjae",
    "\ubcf8\uac00": "noun_bonga",
    "\ud568\ub77d": "noun_hamrak",
    "\ube7c\uc557\uc558\ub2e4": "carrier_ppaeasatda",
    "\uc0c1\ub300\uc5d0\uac8c": "carrier_sangdaeege",
    "\ud0c8\ucde8": "noun_talchwi",
    "\ubc29\uc704": "noun_bangwi",
    "\uac01\uc624\ud558\ub77c": "carrier_gakohara",
    "\ub3d9\uc694": "noun_dongyo",
    "\ub2a5\ub825": "noun_neungnyeok",
    "\ub530\ub974\uace0": "carrier_ttareugo",
    "\ud560 \uc18d\uc148": "carrier_hal_soksem",
    "\ub178\ub9ac\ub294": "carrier_norineun",
    "\uc900\ube44\ud558\ub294": "carrier_junbihaneun",
    "\ud30c\uad34\ud558\ub77c": "carrier_pagoehara",
    "\ud611\uaca9\ud574": "carrier_hyeopgyeokhae",
    "\ubc29\ube44": "noun_bangbi",
    "\ub450 \uac00\ubb38": "carrier_du_gamun",
    "\uc804\uacfc": "carrier_jeongwa",
    "\uc0ac\uac74": "noun_sageon",
    "\ubcf8\uc9c4": "noun_bonjin",
    "\uc801\uc740 \ubcd1\ub825": "noun_jeogeun_byeongnyeok",
    "\ub140\uc11d": "dependent_nyeoseok",
    "\ud1a0\ubc8c": "noun_tobeol",
    "\uc560\uc1a1\uc774": "dependent_aesongi",
    "\ub4dc,": "carrier_deu",
    "\uc804,": "noun_battle_jeon",
}
PERSON_TITLE_BOUNDARY_CLASSES = frozenset(
    {"honorific_gong", "honorific_nim", "hostile_nom"}
)
BOUNDARY_TOKEN_GROUPS = {
    "unit_budae": frozenset({1, 2}),
    "noun_jugun": frozenset({2}),
    "dependent_deung": LEXICAL_SELECTOR_GROUPS,
    "noun_gundan": frozenset({2}),
    "action_gonggyeok": frozenset({3, 4}),
    "action_gongnyak": frozenset({3, 4, 10}),
    "action_chwiim": frozenset({1}),
    "action_yocheong": frozenset({1}),
    "action_jangak": frozenset({1}),
    "noun_seongju": frozenset({2, 3}),
    "action_gyeokpa": frozenset({1, 6, 11}),
    "noun_bonseong": frozenset({11}),
    "action_silhaeng": frozenset({1}),
    "action_hoeyu": frozenset({2, 9}),
    "action_tongil": frozenset({1}),
    "action_geonseol": frozenset({1}),
    "action_jeungchuk": frozenset({1}),
    "noun_seryeok": frozenset({1, 4}),
    "noun_jeongchaek": frozenset({1}),
    "noun_siseol": frozenset({1}),
    "dependent_ttawi": LEXICAL_SELECTOR_GROUPS,
    "dependent_bangmyeon": frozenset({3}),
    "noun_dangju": frozenset({4}),
    "noun_suip": frozenset({1}),
    "dependent_bumun": frozenset({1}),
    "noun_yeongji": frozenset({4}),
    "noun_oegyo": frozenset({4}),
    "noun_seungnak": frozenset({1}),
    "dependent_sai": frozenset({4, 10}),
    "dependent_malgo": frozenset({4}),
    "dependent_an": frozenset({2}),
    "dependent_nae": frozenset({2}),
    "dependent_jubyeon": frozenset({3}),
    "dependent_ingeun": frozenset({3}),
    "dependent_geuncheo": frozenset({3}),
    "noun_sosok_gun": frozenset({3}),
    "noun_subok": frozenset({3}),
    "dependent_jeongdo": frozenset({2, 9}),
    "carrier_single_person": frozenset({2}),
    "noun_dalseong": frozenset({1}),
    "noun_saengseong": frozenset({1}),
    "noun_sakje": frozenset({1}),
    "noun_sujeong": frozenset({1}),
    "noun_dangmyeon_mokpyo": frozenset({3}),
    "noun_sinbun": frozenset({1}),
    "dependent_jjok": frozenset({1, 2}),
    "noun_chuim": frozenset({1}),
    "dependent_gan": frozenset({10}),
    "noun_agun": frozenset({3}),
    "carrier_hyeonjae": frozenset({1}),
    "noun_bonga": frozenset({4}),
    "noun_hamrak": frozenset({3}),
    "carrier_ppaeasatda": frozenset({3}),
    "carrier_sangdaeege": frozenset({4}),
    "noun_talchwi": frozenset({3}),
    "noun_bangwi": frozenset({3}),
    "carrier_gakohara": frozenset({6}),
    "noun_dongyo": frozenset({3}),
    "noun_neungnyeok": frozenset({1}),
    "carrier_ttareugo": frozenset({1}),
    "carrier_hal_soksem": frozenset({1}),
    "carrier_norineun": frozenset({1}),
    "carrier_junbihaneun": frozenset({1}),
    "carrier_pagoehara": frozenset({1}),
    "carrier_hyeopgyeokhae": frozenset({11}),
    "noun_bangbi": frozenset({1}),
    "carrier_du_gamun": frozenset({4}),
    "carrier_jeongwa": frozenset({4}),
    "noun_sageon": frozenset({4}),
    "noun_bonjin": frozenset({2}),
    "noun_jeogeun_byeongnyeok": frozenset({2}),
    "dependent_nyeoseok": frozenset({2}),
    "noun_tobeol": frozenset({2}),
    "dependent_aesongi": frozenset({2}),
    "carrier_deu": frozenset({2}),
    "noun_battle_jeon": frozenset({3}),
}
# These are continuations of an already recognized noun, not permission for a
# selector to attach directly to an arbitrary Korean word.
GRAMMATICAL_CONTINUATIONS = (
    "\uaed8\uc11c",
    "\uaed8",
    "\uc5d0\uac8c",
    "\uc73c\ub85c",
    "\ub85c\uc11c",
    "\ub85c\uc368",
    "\uc5d0\uc11c",
    "\ubd80\ud130",
    "\uae4c\uc9c0",
    "\ub9c8\ub2e4",
    "\uc870\ucc28",
    "\ub9c8\uc800",
    "\ucc98\ub7fc",
    "\ubcf4\ub2e4",
    "\ud558\uace0",
    "\uc774\uba70",
    "\uc774\ub098",
    "\ub4e4",
    "\uc774",
    "\uac00",
    "\uc740",
    "\ub294",
    "\uc744",
    "\ub97c",
    "\uc640",
    "\uacfc",
    "\uc758",
    "\uc5d0",
    "\ub3c4",
    "\ub9cc",
    "\ub85c",
    "\ub098",
)


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


RUNTIME = load_module(
    "opaque_person_selector_runtime_surface_v1",
    RUNTIME_AUDIT_PATH,
)


class OpaqueSelectorSpacingError(ValueError):
    """Raised when the symbolic inventory cannot be audited safely."""


@dataclass(frozen=True)
class Fragment:
    text: str
    complete: bool


@dataclass(frozen=True)
class SymbolicSummary:
    prefixes: frozenset[Fragment]
    selector_tails: frozenset[Fragment]


@dataclass(frozen=True)
class OpaqueSelectorSpacingIssue:
    resource: str
    block_id: int
    record_id: int
    selector_group: int
    boundary_class: str
    opaque_tail_sha256: str
    tail_complete: bool
    opaque_tail: str | None = None


@dataclass(frozen=True)
class OpaqueSelectorResource:
    resource: str
    path: str
    sha256: str
    size: int
    record_count: int
    decoded_record_count: int
    selector_component_count: int
    lexical_selector_component_count: int
    lexical_selector_record_count: int
    person_selector_component_count: int
    person_selector_record_count: int
    symbolic_prefix_state_count: int
    symbolic_selector_tail_state_count: int
    issues: tuple[OpaqueSelectorSpacingIssue, ...]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise OpaqueSelectorSpacingError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def visible_literal(value: str) -> str:
    return "".join(
        character
        for character in value
        if character in "\r\n\t"
        or not unicodedata.category(character).startswith("C")
    )


def clipped_fragment(value: str, complete: bool = True) -> Fragment:
    if len(value) > WINDOW_UNITS:
        return Fragment(value[:WINDOW_UNITS], False)
    return Fragment(value, complete)


def text_summary(value: str) -> SymbolicSummary:
    require(
        not any(marker in value for marker in ALL_MARKERS),
        "candidate literal collides with opaque selector markers",
    )
    return SymbolicSummary(
        prefixes=frozenset({clipped_fragment(value)}),
        selector_tails=frozenset(),
    )


def selector_summary(group: int) -> SymbolicSummary:
    marker = SELECTOR_MARKERS.get(group, OTHER_SELECTOR_MARKER)
    tail = (
        frozenset({Fragment(marker, True)})
        if group in LEXICAL_SELECTOR_GROUPS
        else frozenset()
    )
    return SymbolicSummary(
        prefixes=frozenset({Fragment(marker, True)}),
        selector_tails=tail,
    )


EMPTY_SUMMARY = text_summary("")


def extend_fragment(
    left: Fragment,
    right: Fragment,
) -> Fragment:
    require(left.complete, "only a complete fragment may be extended")
    combined = left.text + right.text
    if len(combined) > WINDOW_UNITS:
        return Fragment(combined[:WINDOW_UNITS], False)
    return Fragment(combined, right.complete)


def compose(
    left: SymbolicSummary,
    right: SymbolicSummary,
) -> SymbolicSummary:
    prefixes: set[Fragment] = set()
    for left_prefix in left.prefixes:
        if not left_prefix.complete:
            prefixes.add(left_prefix)
            continue
        for right_prefix in right.prefixes:
            prefixes.add(
                extend_fragment(left_prefix, right_prefix)
            )

    tails: set[Fragment] = set(right.selector_tails)
    for left_tail in left.selector_tails:
        if not left_tail.complete:
            tails.add(left_tail)
            continue
        for right_prefix in right.prefixes:
            tails.add(extend_fragment(left_tail, right_prefix))
    return SymbolicSummary(
        prefixes=frozenset(prefixes),
        selector_tails=frozenset(tails),
    )


def union_summaries(
    values: Iterable[SymbolicSummary],
) -> SymbolicSummary:
    prefixes: set[Fragment] = set()
    tails: set[Fragment] = set()
    count = 0
    for value in values:
        count += 1
        prefixes.update(value.prefixes)
        tails.update(value.selector_tails)
    require(count > 0, "cannot union an empty symbolic language")
    return SymbolicSummary(
        prefixes=frozenset(prefixes),
        selector_tails=frozenset(tails),
    )


class OpaqueSelectorRenderer:
    """Exactly propagate the boundary-relevant part of every output language."""

    def __init__(
        self,
        records: Mapping[tuple[int, int], Any],
    ) -> None:
        self.records = records
        self.cache: dict[tuple[int, int], SymbolicSummary] = {}

    def render(
        self,
        coordinate: tuple[int, int],
        trail: tuple[tuple[int, int], ...] = (),
    ) -> SymbolicSummary:
        if coordinate in trail:
            return EMPTY_SUMMARY
        cached = self.cache.get(coordinate)
        if cached is not None:
            return cached
        record = self.records.get(coordinate)
        require(
            record is not None,
            f"VM edge target is absent: {coordinate[0]}:{coordinate[1]}",
        )
        components = RUNTIME.tolerant_decode_record(record)
        literals = tuple(
            literal.text
            for literal in RUNTIME.parse_record_literals(record)
        )
        jump_targets = tuple(
            tuple(component["target"])
            for component in components
            if component["kind"] == "jump"
        )
        if jump_targets:
            result = union_summaries(
                self.render(target, trail + (coordinate,))
                for target in jump_targets
            )
            self.cache[coordinate] = result
            return result

        result = EMPTY_SUMMARY
        for component in components:
            kind = str(component["kind"])
            if kind == "literal_boundary":
                addition = text_summary(
                    visible_literal(literals[int(component["slot"])])
                )
            elif kind == "call":
                addition = self.render(
                    tuple(component["target"]),
                    trail + (coordinate,),
                )
            elif kind == "selector":
                addition = selector_summary(int(component["group"]))
            else:
                # Controls and condition operands do not emit visible spacing.
                continue
            result = compose(result, addition)
        self.cache[coordinate] = result
        return result


def tail_boundary(
    fragment: Fragment,
) -> tuple[int, str] | None:
    require(fragment.text, "empty lexical-selector tail")
    selector_group = MARKER_TO_GROUP.get(fragment.text[0])
    require(
        selector_group is not None,
        "lexical-selector tail has an unexpected marker",
    )
    body = fragment.text[1:]
    for token, boundary_class in BOUNDARY_TOKENS.items():
        if not body.startswith(token):
            continue
        if (
            boundary_class in PERSON_TITLE_BOUNDARY_CLASSES
            and selector_group not in PERSON_LIKE_SELECTOR_GROUPS
        ):
            continue
        allowed_groups = BOUNDARY_TOKEN_GROUPS.get(boundary_class)
        if (
            allowed_groups is not None
            and selector_group not in allowed_groups
        ):
            continue
        if allowed_groups is not None:
            # Every entry in this table is a reviewed lexical/dependent-noun
            # or missing-carrier prefix.  Unlike honorific suffixes, it does
            # not need a following-particle check: the defect is already
            # present at the selector/right-prefix boundary.
            return selector_group, boundary_class
        remainder = body[len(token):]
        if not remainder:
            return (
                (selector_group, boundary_class)
                if fragment.complete
                else None
            )
        if (
            remainder[0].isspace()
            or unicodedata.category(remainder[0]).startswith("P")
            or remainder.startswith(GRAMMATICAL_CONTINUATIONS)
        ):
            return selector_group, boundary_class
    return None


def assignment_node(path: Path, name: str) -> ast.AST:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if (
            isinstance(node, (ast.Assign, ast.AnnAssign))
            and (
                (
                    isinstance(node, ast.Assign)
                    and any(
                        isinstance(target, ast.Name)
                        and target.id == name
                        for target in node.targets
                    )
                )
                or (
                    isinstance(node, ast.AnnAssign)
                    and isinstance(node.target, ast.Name)
                    and node.target.id == name
                )
            )
        ):
            return node.value
    raise OpaqueSelectorSpacingError(
        f"{path.name}: assignment is absent: {name}"
    )


def dictionary_string_field(
    dictionary: ast.AST,
    outer_key: str,
    field: str,
) -> str:
    require(isinstance(dictionary, ast.Dict), "policy is not a dictionary")
    for key_node, value_node in zip(
        dictionary.keys,
        dictionary.values,
        strict=True,
    ):
        if ast.literal_eval(key_node) != outer_key:
            continue
        require(
            isinstance(value_node, ast.Dict),
            "honorific policy row is not a dictionary",
        )
        for field_node, field_value_node in zip(
            value_node.keys,
            value_node.values,
            strict=True,
        ):
            if ast.literal_eval(field_node) == field:
                return str(ast.literal_eval(field_value_node))
    raise OpaqueSelectorSpacingError(
        f"policy field is absent: {outer_key}:{field}"
    )


def dictionary_literal_field(
    dictionary: ast.AST,
    field: str,
) -> Any:
    require(isinstance(dictionary, ast.Dict), "policy is not a dictionary")
    for key_node, value_node in zip(
        dictionary.keys,
        dictionary.values,
        strict=True,
    ):
        if ast.literal_eval(key_node) == field:
            return ast.literal_eval(value_node)
    raise OpaqueSelectorSpacingError(f"policy field is absent: {field}")


def integer_set_assignment(path: Path, name: str) -> frozenset[int]:
    value = assignment_node(path, name)
    if (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Name)
        and value.func.id == "frozenset"
        and len(value.args) == 1
        and not value.keywords
    ):
        value = value.args[0]
    observed = ast.literal_eval(value)
    require(
        isinstance(observed, (set, frozenset)),
        f"{path.name}: {name} is not a set",
    )
    require(
        all(isinstance(group, int) for group in observed),
        f"{path.name}: {name} contains a non-integer group",
    )
    return frozenset(observed)


def load_evidence_contract() -> dict[str, Any]:
    ghidra = json.loads(GHIDRA_CONTRACT_PATH.read_text(encoding="utf-8"))
    require(
        ghidra.get("schema")
        == "nobu16.kr.pc-dialogue-ghidra-selector-domain-contract.v1",
        "unexpected Ghidra selector contract",
    )
    adjudication = ghidra.get("adjudication", {})
    require(
        adjudication.get("automatic_space_insertion_is_absent") is True
        and adjudication.get(
            "literal_and_selector_utf16_units_are_copied_verbatim"
        ) is True,
        "Ghidra copy-verbatim contract is absent",
    )

    expected_honorifics = {
        "\u69d8": "\ub2d8",
        "\u6bbf": "\uacf5",
        "\u3081": "\ub188",
    }
    for path in (BASE_POLICY_PATH, PK_POLICY_PATH):
        honorific = assignment_node(path, "HONORIFIC_SUFFIX_POLICY")
        observed = {
            source: dictionary_string_field(
                honorific,
                source,
                "translation",
            )
            for source in expected_honorifics
        }
        require(
            observed == expected_honorifics,
            f"{path.name}: honorific suffix policy drifted",
        )
        tono = assignment_node(path, "TONO_SPACING_POLICY")
        require(
            dictionary_literal_field(
                tono,
                "automatic_space_inserted",
            )
            is False
            and dictionary_literal_field(
                tono,
                "semantic_candidate",
            )
            == "\uacf5",
            f"{path.name}: tono spacing policy drifted",
        )
    for path in (
        BASE_REMEDIATION_POLICY_PATH,
        PK_REMEDIATION_POLICY_PATH,
    ):
        require(
            integer_set_assignment(
                path,
                "PERSON_LIKE_SELECTOR_GROUPS",
            )
            == PERSON_LIKE_SELECTOR_GROUPS,
            f"{path.name}: person-like selector policy drifted",
        )
    require(
        frozenset(RUNTIME.LEXICAL_SELECTOR_GROUPS)
        == LEXICAL_SELECTOR_GROUPS,
        "runtime lexical selector policy drifted",
    )
    return {
        "ghidra_selector_contract_sha256": sha256_bytes(
            GHIDRA_CONTRACT_PATH.read_bytes()
        ),
        "base_honorific_policy_sha256": sha256_bytes(
            BASE_POLICY_PATH.read_bytes()
        ),
        "pk_honorific_policy_sha256": sha256_bytes(
            PK_POLICY_PATH.read_bytes()
        ),
        "base_person_selector_policy_sha256": sha256_bytes(
            BASE_REMEDIATION_POLICY_PATH.read_bytes()
        ),
        "pk_person_selector_policy_sha256": sha256_bytes(
            PK_REMEDIATION_POLICY_PATH.read_bytes()
        ),
        "runtime_lexical_selector_policy_sha256": sha256_bytes(
            RUNTIME_AUDIT_PATH.read_bytes()
        ),
        "copy_verbatim": True,
        "automatic_space_inserted": False,
        "honorific_suffix_policy_validated": True,
        "tono_spacing_policy_validated": True,
        "person_like_selector_policy_validated": True,
        "lexical_selector_policy_validated": True,
    }


def records_from_path(
    path: Path,
) -> tuple[dict[tuple[int, int], Any], str]:
    return RUNTIME.records_from_path(path)


def audit_resource(
    resource: str,
    path: Path,
    *,
    include_text: bool = False,
) -> OpaqueSelectorResource:
    records, blob_sha256 = records_from_path(path)
    renderer = OpaqueSelectorRenderer(records)
    selector_component_count = 0
    lexical_selector_component_count = 0
    lexical_selector_records: set[tuple[int, int]] = set()
    person_selector_component_count = 0
    person_selector_records: set[tuple[int, int]] = set()
    for coordinate, record in records.items():
        components = RUNTIME.tolerant_decode_record(record)
        for component in components:
            if component["kind"] != "selector":
                continue
            selector_component_count += 1
            if int(component["group"]) in LEXICAL_SELECTOR_GROUPS:
                lexical_selector_component_count += 1
                lexical_selector_records.add(coordinate)
            if int(component["group"]) in PERSON_LIKE_SELECTOR_GROUPS:
                person_selector_component_count += 1
                person_selector_records.add(coordinate)

    issues: dict[
        tuple[int, int, int, str, str, bool],
        OpaqueSelectorSpacingIssue,
    ] = {}
    symbolic_prefix_state_count = 0
    symbolic_selector_tail_state_count = 0
    for coordinate in records:
        summary = renderer.render(coordinate)
        symbolic_prefix_state_count += len(summary.prefixes)
        symbolic_selector_tail_state_count += len(summary.selector_tails)
        for tail in summary.selector_tails:
            boundary = tail_boundary(tail)
            if boundary is None:
                continue
            selector_group, boundary_class = boundary
            tail_sha256 = utf16le_sha256(tail.text)
            key = (
                coordinate[0],
                coordinate[1],
                selector_group,
                boundary_class,
                tail_sha256,
                tail.complete,
            )
            issues[key] = OpaqueSelectorSpacingIssue(
                resource=resource,
                block_id=coordinate[0],
                record_id=coordinate[1],
                selector_group=selector_group,
                boundary_class=boundary_class,
                opaque_tail_sha256=tail_sha256,
                tail_complete=tail.complete,
                opaque_tail=tail.text if include_text else None,
            )

    ordered = tuple(
        sorted(
            issues.values(),
            key=lambda issue: (
                issue.block_id,
                issue.record_id,
                issue.selector_group,
                issue.boundary_class,
                issue.opaque_tail_sha256,
            ),
        )
    )
    return OpaqueSelectorResource(
        resource=resource,
        path=str(path.resolve()),
        sha256=blob_sha256,
        size=path.stat().st_size,
        record_count=len(records),
        decoded_record_count=len(records),
        selector_component_count=selector_component_count,
        lexical_selector_component_count=(
            lexical_selector_component_count
        ),
        lexical_selector_record_count=len(lexical_selector_records),
        person_selector_component_count=person_selector_component_count,
        person_selector_record_count=len(person_selector_records),
        symbolic_prefix_state_count=symbolic_prefix_state_count,
        symbolic_selector_tail_state_count=(
            symbolic_selector_tail_state_count
        ),
        issues=ordered,
    )


def source_free_issue(
    value: OpaqueSelectorSpacingIssue,
) -> dict[str, Any]:
    payload = asdict(value)
    payload.pop("opaque_tail", None)
    return payload


def build_report(
    resources: Sequence[OpaqueSelectorResource],
) -> dict[str, Any]:
    evidence = load_evidence_contract()
    issues = tuple(
        issue
        for resource in resources
        for issue in resource.issues
    )
    category_counts = Counter(
        issue.boundary_class for issue in issues
    )
    return {
        "schema": SCHEMA,
        "status": "PASS" if not issues else "FAIL",
        "issue_count": len(issues),
        "category_counts": dict(sorted(category_counts.items())),
        "resources": {
            resource.resource: {
                "path": resource.path,
                "sha256": resource.sha256,
                "size": resource.size,
                "record_count": resource.record_count,
                "decoded_record_count": resource.decoded_record_count,
                "selector_component_count":
                    resource.selector_component_count,
                "lexical_selector_component_count":
                    resource.lexical_selector_component_count,
                "lexical_selector_record_count":
                    resource.lexical_selector_record_count,
                "person_selector_component_count":
                    resource.person_selector_component_count,
                "person_selector_record_count":
                    resource.person_selector_record_count,
                "symbolic_prefix_state_count":
                    resource.symbolic_prefix_state_count,
                "symbolic_selector_tail_state_count":
                    resource.symbolic_selector_tail_state_count,
                "issue_count": len(resource.issues),
            }
            for resource in resources
        },
        "issues": [
            (
                asdict(issue)
                if issue.opaque_tail is not None
                else source_free_issue(issue)
            )
            for issue in issues
        ],
        "audit_contract": {
            "person_like_selector_groups":
                sorted(PERSON_LIKE_SELECTOR_GROUPS),
            "dependent_noun_selector_groups":
                sorted(LEXICAL_SELECTOR_GROUPS),
            "all_records_symbolically_rendered": True,
            "calls_and_jumps_closed": True,
            "cartesian_variant_cap_used": False,
            "branch_products_summarized_exactly": True,
            "opaque_non_person_selectors_rendered": True,
            "only_no_space_exact_noun_boundaries_rejected": True,
            "ordinary_particles_rejected": False,
            "integer_ordinal_families_rejected": False,
            "castle_clan_unit_families_rejected": False,
            "evidence": evidence,
            "source_or_translation_bodies_omitted": all(
                issue.opaque_tail is None for issue in issues
            ),
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


def canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
    ) + "\n"


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--pk", type=Path, default=DEFAULT_PK)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--include-text", action="store_true")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
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
    report = build_report(resources)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        canonical_json(report),
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "schema": SCHEMA,
                "status": report["status"],
                "issue_count": report["issue_count"],
                "resources": {
                    resource.resource: {
                        "sha256": resource.sha256,
                        "issue_count": len(resource.issues),
                    }
                    for resource in resources
                },
                "output": str(args.output.resolve()),
            },
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 1 if args.strict and report["issue_count"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, OpaqueSelectorSpacingError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
