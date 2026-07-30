#!/usr/bin/env python3
"""Audit user-visible Korean boundaries in Base/PK ``msggame.bin``.

The older runtime audit proves VM topology and byte preservation.  This audit
adds the missing language-facing gate:

* Korean dual-particle placeholders must never reach a candidate;
* a dynamic selector must not be followed by one fixed Korean particle when
  the selected value can vary;
* a called dynamic phrase must not be followed by a fixed Korean particle
  that disagrees with any rendered variant;
* a lexical selector must not be concatenated directly to the visible
  literal on its left because the VM does not insert Korean word spaces;
* a mixed-register runtime address/pronoun family must not be followed by a
  fixed honorific particle such as ``께서``;
* malformed literal endings such as duplicated ``요오`` must not ship;
* a completed Korean ending must not be followed by a VM-selected terminal
  ending.

The VM decoder is reused from ``pk_msggame_runtime_vm_audit_v1``.  Ghidra
proved that literal and selector UTF-16 code units are copied verbatim and
that opcode ``0143`` calls another record, so these checks do not assume any
unobserved Korean post-processing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
DEFAULT_CANDIDATE_ROOT = (
    REPO
    / "tmp"
    / "pc_dialogue_full_retranslation_v0150"
    / "finalizer_preflight_52803"
    / "candidate"
)
DEFAULT_BASE = DEFAULT_CANDIDATE_ROOT / "MSG" / "JP" / "msggame.bin"
DEFAULT_PK = DEFAULT_CANDIDATE_ROOT / "MSG_PK" / "JP" / "msggame.bin"

sys.path[:0] = [
    str(REPO / "tools"),
    str(REPO / "workstreams" / "msggame"),
    str(REPO / "workstreams" / "pk_msggame_runtime_vm_audit_v1"),
]

from msggame_format import (  # noqa: E402
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
)
import build_pk_msggame_runtime_vm_audit_v1 as VM  # noqa: E402


SCHEMA = "nobu16.kr.pc-dialogue-runtime-surface-audit.v1"
DUAL_PARTICLES = (
    "이(가)",
    "은(는)",
    "을(를)",
    "와(과)",
    "(으)로",
    "으로(로)",
)
SELECTOR_PARTICLE_RE = re.compile(
    r"^(?P<particle>이|가|은|는|을|를|와|과|로|으로)"
    r"(?=[\s\n,.:!?…」]|$)"
)
WRAPPED_PARTICLE_RE = re.compile(
    r"^(?P<wrapper>[\s\)\]\u300d\u300f\u3011\u3009\u300b\u3015]+)"
    r"(?P<particle>\uc73c\ub85c|\uac00|\uc740|\ub294|\uc744|\ub97c|\uc640|\uacfc|\ub85c)"
    r"(?=[\s\n,.:!?\u2026\)\]\u300d\u300f\u3011\u3009\u300b\u3015]|$)"
)
WRAPPED_I_PARTICLE_COORDINATES = frozenset(
    {
        ("base_msggame", 2, 645, 2),
        ("pk_msggame", 2, 662, 2),
    }
)
# Ghidra's selector classifier identifies these value classes, while the
# Korean resource contract fixes the visible name suffix.  Property 0x32 is
# the display-name request used by the audited records.
FIXED_BATCHIM_SELECTOR_NAMES = {
    (3, 0x32): "성",      # castle_slot -> canonical Korean castle name
    (4, 0x32): "가문",    # clan_slot -> canonical Korean clan name
}
FIXED_BATCHIM_PARTICLES = frozenset({"이", "은", "을", "과", "으로"})
# These selector groups emit a visible lexical value such as a place, person,
# castle, clan, unit, or county name.  Ghidra proved that the assembler copies
# the selector output verbatim, so a preceding Korean word needs an explicit
# separator in the literal.  Group 0 is deliberately excluded: it is a
# numeric/value selector with reviewed compact forms such as ``LV3`` and
# ``제2`` that need a separate contract.
LEXICAL_SELECTOR_GROUPS = frozenset(
    {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}
)
INTEGER_SELECTOR_GROUP = 0
# An opening delimiter or an intentional in-word separator may directly
# precede a selected lexical value.  Closing delimiters, commas, colons, and
# sentence punctuation are intentionally absent because Korean requires a
# following word space there.
SELECTOR_LEFT_JOINERS = frozenset(
    {
        '"',
        "'",
        "(",
        "[",
        "{",
        "<",
        "\u2018",  # ‘
        "\u201c",  # “
        "\u3008",  # 〈
        "\u300a",  # 《
        "\u300c",  # 「
        "\u300e",  # 『
        "\u3010",  # 【
        "\u3014",  # 〔
        "\u00b7",  # ·
        "\u30fb",  # ・
        "/",
        "\uff0f",  # ／
        "-",
        "\u2014",  # —
        "\u2015",  # ―
        "\u2192",  # → (compact old-name → new-name separator)
    }
)
INTEGER_LEFT_COMPACT_LABELS = frozenset({"통", "무", "지", "정"})
INTEGER_LEFT_COMPACT_SIGNS = frozenset({"+", "-", "\u2212"})
PRONOUN_CALL_TARGETS = frozenset({(0, 1)})
LOW_REGISTER_NOUN_CALL_TARGETS = frozenset({(0, 4), (0, 6)})
ADDRESS_CALL_TARGETS = frozenset(
    {
        (0, 8),
        (0, 17),
        (0, 21),
        (0, 29),
        (0, 34),
        (0, 37),
        (0, 46),
        (0, 50),
    }
)
MIXED_REGISTER_CALL_TARGETS = (
    PRONOUN_CALL_TARGETS
    | LOW_REGISTER_NOUN_CALL_TARGETS
    | ADDRESS_CALL_TARGETS
    | frozenset({(0, 7)})
)
CALL_FIXED_HONORIFIC_RE = re.compile(
    r"^\uaed8(?:\uc11c\ub294|\uc11c\ub3c4|\uc11c|\ub3c4)?"
    r"(?=[\s\n,.:!?\u2026\)\]\u300d\u300f\u3011\u3009\u300b\u3015]|$)"
)
ATTACHED_REFLEXIVE_CARRIER_RE = re.compile(
    r"^(?:\uc790\uc2e0|\ubcf8\uc778)"
    r"(?:\uc73c\ub85c|\uc774|\uac00|\uc740|\ub294|\uc744|\ub97c|\uc640|\uacfc|\ub85c)"
)
SPACED_PERSON_CARRIER_RE = re.compile(
    r"^ (?P<carrier>"
    r"\ubd84|\ubb34\uc7a5|\uc7a5\uc218|\uc8fc\uad70|\uc0ac\uc790|"
    r"\ub2f9\uc8fc|\uc778\ubb3c|\ub300\uc0c1|\ubcf8\uc778|\uc790\uc2e0"
    r")"
    r"(?:\uc73c\ub85c|\uc774|\uac00|\uc740|\ub294|\uc744|\ub97c|\uc640|\uacfc|\ub85c)"
)
SELECTOR_PERSON_CARRIER_RE = re.compile(
    r"^ (?P<carrier>"
    r"\ubd84|\ubb34\uc7a5|\uc7a5\uc218|\uc8fc\uad70|\uc0ac\uc790|"
    r"\ub2f9\uc8fc|\uc778\ubb3c|\ub300\uc0c1|\ud56d\ubaa9|"
    r"\ubcf8\uc778|\uc790\uc2e0"
    r")"
    r"(?:\uc73c\ub85c|\uc774|\uac00|\uc740|\ub294|\uc744|\ub97c|\uc640|\uacfc|\ub85c)"
)
SELECTOR_SIDE_CARRIER_RE = re.compile(
    r"^ \uce21"
    r"(?:\uc73c\ub85c|\uc774|\uac00|\uc740|\ub294|\uc744|\ub97c|\uc640|\uacfc|\ub85c|\uc758)"
)
REVIEWED_PK_SELECTOR_JUGUN_BOUNDARIES = {
    (2, 330, 0): "D62EB5065CA4DAAC807ADC0298D809447169957845F275466D636566919CB324",
    (6, 735, 0): "D1B34664724A01835D53949FBBAE13AB8BC38A4846813781344313518F87F362",
    (9, 3584, 0): "EA869D4752B08884842A53DD3B31E780AD22273617A44A285D2DED827200AAD0",
    (17, 117, 0): "88F5E8041EAA0E637AA5C245DC06105E853625ACEA4152D53EA3251177CEBD78",
    (17, 142, 2): "C50713CC269BE16CF66163764233D9107444B5D446CBDAB7AA54677AFA34D999",
    (17, 147, 1): "482DC67BB9F182EA3A08CEFFCE9207F4AF5C827FFBE69B0DDA8FBCB0EB322A88",
    (17, 151, 0): "A536D095AE75F9E50385BE7939A1AFA89F5D51FA2FF2F28B6938582BE0637E0B",
    (17, 208, 0): "651852862A91463532247489F785D8D8FA69D3AB8905869FAC43639947BBC5E2",
    (17, 236, 1): "8D6A7CE324A0894DEDF6812DF47916C6204DDFBAFAF06E56D0AF6516717E5FEB",
    (17, 280, 0): "14F6942E1D6F22F968B5B65DC6CC1F42D2E2DD3594EF5E4BC85495AF6FCB2BBF",
    (17, 283, 0): "14F6942E1D6F22F968B5B65DC6CC1F42D2E2DD3594EF5E4BC85495AF6FCB2BBF",
    (17, 487, 0): "8E9CC5EC4E0CB65F1E9A573A3D1264A2F42A8C37B865B27970D4E08CD61AB2DF",
    (17, 488, 1): "6DC54FD7958723D966BDE5B6671FEB67E83D1E0C96EB2EB38611A8CEB5C81410",
    (17, 522, 0): "B1E5D4C4326C93B2C350D9EB23CD34E84781EA632B71E66CF48B54A24CE13DFB",
    (17, 678, 0): "1B820B7444050CD1FA2BEDBE6E416491B0AE46A543A7375261273433482ECEE9",
    (17, 706, 0): "6591339BADFE7905C743D7F67C193297A19D70391D367AFBD05A23ED575B64B6",
    (17, 707, 1): "6591339BADFE7905C743D7F67C193297A19D70391D367AFBD05A23ED575B64B6",
    (17, 739, 0): "2CA1316B622DFD9ADB38344117D4B2F819A3E61644AB79D0A6C85B9BD6911BC6",
    (17, 759, 3): "854BE2E97D5425903A02954837D2469A7BE24CF682F2A3D9DFA307D19D616A95",
    (17, 807, 0): "1B820B7444050CD1FA2BEDBE6E416491B0AE46A543A7375261273433482ECEE9",
    (17, 814, 0): "F77EB5B40D95116C37ECB06EB34A3ABFBEF20655A88AB8BE90DC18AC6223DAA6",
    (17, 819, 0): "6591339BADFE7905C743D7F67C193297A19D70391D367AFBD05A23ED575B64B6",
    (17, 848, 0): "C8EAEC5EC8108C3F15893F2705B48DA7267F86F6486DD004B8B482374BB67B31",
    (17, 864, 1): "6591339BADFE7905C743D7F67C193297A19D70391D367AFBD05A23ED575B64B6",
    (17, 881, 3): "854BE2E97D5425903A02954837D2469A7BE24CF682F2A3D9DFA307D19D616A95",
}
REVIEWED_PK_SELECTOR_JANGSU_BOUNDARIES = {
    (6, 4906, 0): "BE88CA586733A64D9317CFD164414C8199AFA9F4CF27923A5362EEA3FA37B701",
    (9, 3570, 1): "DB5F2D1A65AB29F1760614A180F69AB8FB49D1A566588CF2DF3D068B920B5675",
    (9, 3572, 1): "0EDF235B1D4DC57774E476F322B67CB6259C91A9EF2E2007B39CAE92253E5641",
    (9, 3573, 1): "2878CBEC20FF5A40EBA317504377570B62DE4A800ECDD18E43FB1ED74A83ECAA",
    (9, 3575, 1): "B265D4E97FE8BB116CC3E8985C55378C9687AD6E9A2DD6D794073F76E29F24F8",
    (9, 3576, 1): "2878CBEC20FF5A40EBA317504377570B62DE4A800ECDD18E43FB1ED74A83ECAA",
    (9, 3578, 1): "DD22EBC7946A8286619503ACA1C375D8590B6FE8DDA82CBA11D99387B7803EBE",
    (9, 3579, 1): "4AA00C34C4B85C0A8FC20302D5E16B49DFEF7BEE31908BE7733C4D669A813670",
    (9, 3580, 1): "DD22EBC7946A8286619503ACA1C375D8590B6FE8DDA82CBA11D99387B7803EBE",
}
REVIEWED_PK_SELECTOR_CARRIER_BOUNDARIES = {
    **REVIEWED_PK_SELECTOR_JUGUN_BOUNDARIES,
    **REVIEWED_PK_SELECTOR_JANGSU_BOUNDARIES,
}
REVIEWED_BASE_SELECTOR_CARRIER_BOUNDARIES = {
    # A group-4 runtime value is followed by the reviewed role predicate
    # " 당주이신 ".  Ghidra proves the selector and literal are copied
    # verbatim, so the leading separator is required rather than an
    # automatically introduced generic carrier.
    (2, 622, 0): "85FD5C6087DC80F4079FCA833103587C8AF0EED389A413509F2ED28F3659B887",
}
TERMINAL_DUPLICATION_RES = (
    re.compile(
        r"(?:사옵니다|하옵니다|습니다|입니다)"
        r"(?:있소|있다|입니다|이다|하오|하옵니다|사옵니다|습니다)"
    ),
    re.compile(r"(?:합니다|했습니다)(?:이겠|이라|입니다)"),
)
LITERAL_ORTHOGRAPHY_RES = {
    "duplicated_polite_ending_yo_o": re.compile(r"\uc694\uc624"),
}
IGNORABLE_BETWEEN_SELECTOR_AND_LITERAL = frozenset(
    {
        "arithmetic_operator",
        "comparison_operator",
        "logical_operator",
        "decimal_atom",
        "percent_decimal_atom",
        "control_tag",
        "block_token",
        "random_select",
    }
)
MAX_VARIANTS_PER_RECORD = 256


class SurfaceAuditError(ValueError):
    """Raised when an audit input or VM invariant cannot be evaluated."""


@dataclass(frozen=True)
class Issue:
    resource: str
    category: str
    block_id: int
    record_id: int
    literal_id: int | None
    text_sha256: str
    details: Mapping[str, Any]
    text: str | None = None


@dataclass(frozen=True)
class ResourceAudit:
    resource: str
    path: str
    sha256: str
    record_count: int
    literal_count: int
    decoded_record_count: int
    issues: tuple[Issue, ...]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def utf16le_sha256(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SurfaceAuditError(message)


def records_from_path(
    path: Path,
) -> tuple[dict[tuple[int, int], MsgGameRecord], str]:
    require(path.is_file(), f"msggame input is absent: {path}")
    blob = path.read_bytes()
    archive = parse_packed_msggame(blob).archive
    records = {
        (record.block_id, record.record_id): record
        for block in archive.blocks
        for record in block.records
    }
    return records, sha256_bytes(blob)


def tolerant_decode_record(
    record: MsgGameRecord,
) -> tuple[dict[str, Any], ...]:
    """Decode the full current universe without weakening edge discovery.

    The established structural decoder intentionally accepted only the
    comparison operators needed by its Base→PK reuse subset.  The complete
    archives also use ``{``/``}`` comparison forms.  Their branch meaning is
    irrelevant to this audit; their width remains exactly two bytes.  Two
    terminal records also carry a single zero padding byte after ``050505``.
    """

    original_comparison = VM.COMPARISON_OPERATORS
    try:
        VM.COMPARISON_OPERATORS = original_comparison | frozenset(b"{}")
        try:
            return VM.decode_record(record)
        except Exception:
            if not record.data.endswith(b"\x00"):
                raise
            trimmed = MsgGameRecord(
                block_id=record.block_id,
                record_id=record.record_id,
                relative_offset=record.relative_offset,
                data=record.data[:-1],
            )
            return VM.decode_record(trimmed) + ({"kind": "padding_zero"},)
    finally:
        VM.COMPARISON_OPERATORS = original_comparison


def unique_ordered(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def selector_particle_is_safe(
    selector: Mapping[str, Any],
    particle: str,
) -> bool:
    """Return whether a fixed particle follows a proven fixed-batchim name."""

    property_value = selector.get("property")
    if not isinstance(property_value, int):
        return False
    contract = (
        int(selector["group"]),
        property_value,
    )
    return (
        contract in FIXED_BATCHIM_SELECTOR_NAMES
        and particle in FIXED_BATCHIM_PARTICLES
    )


def last_hangul_jongseong(value: str) -> int | None:
    """Return the final Hangul syllable's jongseong index, if one exists."""

    for character in reversed(value):
        codepoint = ord(character)
        if 0xAC00 <= codepoint <= 0xD7A3:
            return (codepoint - 0xAC00) % 28
    return None


def fixed_particle_matches_variant(
    particle: str,
    variant: str,
) -> bool | None:
    """Check one fixed particle against a rendered Korean variant.

    ``None`` means that the renderer did not expose a Hangul syllable from
    which the required particle form can be proved.
    """

    jongseong = last_hangul_jongseong(variant)
    if jongseong is None:
        return None
    if particle in {"\uc774", "\uc740", "\uc744", "\uacfc"}:
        return jongseong != 0
    if particle in {"\uac00", "\ub294", "\ub97c", "\uc640"}:
        return jongseong == 0
    if particle == "\uc73c\ub85c":
        return jongseong not in {0, 8}
    if particle == "\ub85c":
        return jongseong in {0, 8}
    return None


def boundary_particle_match(
    resource: str,
    coordinate: tuple[int, int],
    literal_id: int,
    text: str,
) -> re.Match[str] | None:
    direct = SELECTOR_PARTICLE_RE.search(text)
    if direct is not None:
        return direct
    wrapped = WRAPPED_PARTICLE_RE.search(text)
    if wrapped is not None:
        return wrapped
    wrapped_i = re.search(
        r"^(?P<wrapper>[\s\)\]\u300d\u300f\u3011\u3009\u300b\u3015]+)"
        r"(?P<particle>\uc774)"
        r"(?=[\s\n,.:!?\u2026\)\]\u300d\u300f\u3011\u3009\u300b\u3015]|$)",
        text,
    )
    if (
        wrapped_i is not None
        and (resource, coordinate[0], coordinate[1], literal_id)
        in WRAPPED_I_PARTICLE_COORDINATES
    ):
        return wrapped_i
    return None


def call_semantic_carrier_artifact_reason(
    target: tuple[int, int],
    text: str,
) -> str | None:
    """Reject mechanical carriers that make rendered address terms unnatural."""

    if (
        target in MIXED_REGISTER_CALL_TARGETS
        and CALL_FIXED_HONORIFIC_RE.search(text) is not None
    ):
        return "mixed_register_call_followed_by_fixed_honorific_particle"
    if (
        target in PRONOUN_CALL_TARGETS
        and ATTACHED_REFLEXIVE_CARRIER_RE.search(text) is not None
    ):
        return "missing_space_before_reflexive_carrier"
    carrier_match = SPACED_PERSON_CARRIER_RE.search(text)
    if carrier_match is not None:
        if (
            target in MIXED_REGISTER_CALL_TARGETS
            and target not in PRONOUN_CALL_TARGETS
            and carrier_match.group("carrier")
            in {"\ubcf8\uc778", "\uc790\uc2e0"}
        ):
            return "mixed_register_call_followed_by_self_reference_carrier"
        if target in ADDRESS_CALL_TARGETS:
            return "address_term_followed_by_role_carrier"
        if target in LOW_REGISTER_NOUN_CALL_TARGETS:
            return "low_register_noun_followed_by_person_carrier"
        if carrier_match.group("carrier") == "\ubd84":
            return "generic_person_carrier_after_call"
    return None


def selector_semantic_carrier_artifact_reason(
    selector: Mapping[str, Any],
    text: str,
) -> str | None:
    """Reject mechanical role nouns appended to a dynamic selector.

    A selector already emits the visible runtime value.  Appending a generic
    role noun merely to obtain a stable Korean particle creates constructions
    such as ``<name> 장수가`` or ``<name> 인물이``.  Those outputs can be
    grammatical in a narrowly reviewed context, but they are not a safe
    automatic fallback: the selected person may be a court noble, woman,
    messenger, relative, or enemy.  Recast the sentence around an invariant
    relation instead of treating the selector domain as a visible title.
    """

    if SELECTOR_PERSON_CARRIER_RE.match(text) is not None:
        return "dynamic_selector_followed_by_unreviewed_person_carrier"
    if (
        int(selector["group"]) in {3, 10}
        and SELECTOR_SIDE_CARRIER_RE.match(text) is not None
    ):
        return "location_selector_followed_by_faction_side_carrier"
    return None


def literal_orthography_artifact_reasons(text: str) -> tuple[str, ...]:
    """Return exact malformed Korean forms that must not ship."""

    return tuple(
        reason
        for reason, pattern in LITERAL_ORTHOGRAPHY_RES.items()
        if pattern.search(text) is not None
    )


def selector_left_boundary_spacing_reason(
    selector: Mapping[str, Any],
    prefix: str,
) -> str | None:
    """Return why a lexical selector needs a space on its left."""

    group = int(selector["group"])
    if (
        group not in LEXICAL_SELECTOR_GROUPS
        and group != INTEGER_SELECTOR_GROUP
    ):
        return None
    if not prefix:
        return None
    final = prefix[-1]
    if final.isspace() or final in SELECTOR_LEFT_JOINERS:
        return None
    if group == INTEGER_SELECTOR_GROUP:
        if prefix.endswith("LV"):
            return None
        if prefix in INTEGER_LEFT_COMPACT_LABELS:
            return None
        if final in INTEGER_LEFT_COMPACT_SIGNS:
            return None
        if prefix.endswith("\uc81c") and (
            len(prefix) == 1 or prefix[-2].isspace()
        ):
            return None
        return "integer_selector_concatenated_to_left_literal"
    return "lexical_selector_concatenated_to_left_literal"


class TerminalRenderer:
    """Conservatively enumerate strings emitted by call/jump terminal trees."""

    def __init__(
        self,
        records: Mapping[tuple[int, int], MsgGameRecord],
    ) -> None:
        self.records = records
        self.cache: dict[tuple[int, int], tuple[str, ...]] = {}

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
            raise SurfaceAuditError(
                f"VM edge target is absent: {coordinate[0]}:{coordinate[1]}"
            )
        components = tolerant_decode_record(record)
        literals = tuple(
            literal.text for literal in parse_record_literals(record)
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
            )[:MAX_VARIANTS_PER_RECORD]
            self.cache[coordinate] = variants
            return variants

        states = ("",)
        for component in components:
            kind = component["kind"]
            if kind == "literal_boundary":
                additions = (literals[int(component["slot"])],)
            elif kind == "call":
                additions = self.render(
                    tuple(component["target"]),
                    trail + (coordinate,),
                )
            elif kind == "output_control":
                additions = (chr(int(component["code"])),)
            else:
                continue
            states = tuple(
                left + right
                for left in states
                for right in additions
            )[:MAX_VARIANTS_PER_RECORD]
        variants = unique_ordered(states)
        self.cache[coordinate] = variants
        return variants


def issue(
    *,
    resource: str,
    category: str,
    coordinate: tuple[int, int],
    literal_id: int | None,
    text: str,
    details: Mapping[str, Any],
    include_text: bool,
) -> Issue:
    return Issue(
        resource=resource,
        category=category,
        block_id=coordinate[0],
        record_id=coordinate[1],
        literal_id=literal_id,
        text_sha256=utf16le_sha256(text),
        details=dict(details),
        text=text if include_text else None,
    )


def audit_resource(
    resource: str,
    path: Path,
    *,
    include_text: bool = False,
) -> ResourceAudit:
    records, blob_sha256 = records_from_path(path)
    renderer = TerminalRenderer(records)
    issues: list[Issue] = []
    literal_count = 0
    decoded = 0

    for coordinate, record in records.items():
        literals = tuple(
            literal.text for literal in parse_record_literals(record)
        )
        literal_count += len(literals)
        components = tolerant_decode_record(record)
        decoded += 1

        for literal_id, text in enumerate(literals):
            matched = tuple(
                token for token in DUAL_PARTICLES if token in text
            )
            if matched:
                issues.append(
                    issue(
                        resource=resource,
                        category="unresolved_dual_particle",
                        coordinate=coordinate,
                        literal_id=literal_id,
                        text=text,
                        details={"tokens": matched},
                        include_text=include_text,
                    )
                )
            orthography_reasons = literal_orthography_artifact_reasons(text)
            if orthography_reasons:
                issues.append(
                    issue(
                        resource=resource,
                        category="literal_orthography_artifact",
                        coordinate=coordinate,
                        literal_id=literal_id,
                        text=text,
                        details={"reasons": orthography_reasons},
                        include_text=include_text,
                    )
                )

        previous_selector: Mapping[str, Any] | None = None
        previous_literal: tuple[int, str] | None = None
        previous_call: tuple[tuple[int, int], tuple[str, ...]] | None = None
        for component in components:
            kind = str(component["kind"])
            if kind == "selector":
                if previous_literal is not None:
                    literal_id, prefix = previous_literal
                    spacing_reason = selector_left_boundary_spacing_reason(
                        component,
                        prefix,
                    )
                    if spacing_reason is not None:
                        issues.append(
                            issue(
                                resource=resource,
                                category="selector_left_boundary_spacing",
                                coordinate=coordinate,
                                literal_id=literal_id,
                                text=prefix,
                                details={
                                    "selector_group":
                                        int(component["group"]),
                                    "selector_slot":
                                        int(component["slot"]),
                                    "selector_property":
                                        component.get("property"),
                                    "selector_raw_hex":
                                        str(component["raw_hex"]),
                                    "reason": spacing_reason,
                                },
                                include_text=include_text,
                            )
                        )
                previous_selector = component
                previous_literal = None
                previous_call = None
                continue
            if kind == "literal_boundary":
                literal_id = int(component["slot"])
                text = literals[literal_id]
                particle_match = boundary_particle_match(
                    resource,
                    coordinate,
                    literal_id,
                    text,
                )
                if (
                    previous_selector is not None
                    and particle_match is not None
                    and not selector_particle_is_safe(
                        previous_selector,
                        particle_match.group("particle"),
                    )
                ):
                    issues.append(
                        issue(
                            resource=resource,
                            category="selector_fixed_particle",
                            coordinate=coordinate,
                            literal_id=literal_id,
                            text=text,
                            details={
                                "selector_group":
                                    int(previous_selector["group"]),
                                "selector_slot":
                                    int(previous_selector["slot"]),
                                "selector_property":
                                    previous_selector.get("property"),
                                "selector_raw_hex":
                                    str(previous_selector["raw_hex"]),
                                "particle":
                                    particle_match.group("particle"),
                            },
                            include_text=include_text,
                        )
                    )
                if previous_selector is not None:
                    artifact_reason = (
                        selector_semantic_carrier_artifact_reason(
                            previous_selector,
                            text,
                        )
                    )
                    reviewed_carrier_boundaries = (
                        REVIEWED_BASE_SELECTOR_CARRIER_BOUNDARIES
                        if resource == "base_msggame"
                        else REVIEWED_PK_SELECTOR_CARRIER_BOUNDARIES
                        if resource == "pk_msggame"
                        else {}
                    )
                    reviewed_carrier_boundary = (
                        reviewed_carrier_boundaries.get(
                            (
                                coordinate[0],
                                coordinate[1],
                                literal_id,
                            )
                        )
                        == utf16le_sha256(text)
                    )
                    if (
                        artifact_reason is not None
                        and not reviewed_carrier_boundary
                    ):
                        issues.append(
                            issue(
                                resource=resource,
                                category=(
                                    "selector_semantic_carrier_artifact"
                                ),
                                coordinate=coordinate,
                                literal_id=literal_id,
                                text=text,
                                details={
                                    "selector_group":
                                        int(previous_selector["group"]),
                                    "selector_slot":
                                        int(previous_selector["slot"]),
                                    "selector_property":
                                        previous_selector.get("property"),
                                    "selector_raw_hex":
                                        str(previous_selector["raw_hex"]),
                                    "reason": artifact_reason,
                                },
                                include_text=include_text,
                            )
                        )
                if previous_call is not None and particle_match is not None:
                    target, rendered_variants = previous_call
                    nonempty_variants = tuple(
                        value for value in rendered_variants if value
                    )
                    verdicts = tuple(
                        fixed_particle_matches_variant(
                            particle_match.group("particle"),
                            value,
                        )
                        for value in nonempty_variants
                    )
                    mismatch_count = sum(
                        verdict is False for verdict in verdicts
                    )
                    unknown_count = sum(
                        verdict is None for verdict in verdicts
                    )
                    if nonempty_variants and (
                        mismatch_count or unknown_count
                    ):
                        jongseong_counts = Counter(
                            (
                                "unknown"
                                if last_hangul_jongseong(value) is None
                                else str(last_hangul_jongseong(value))
                            )
                            for value in nonempty_variants
                        )
                        issues.append(
                            issue(
                                resource=resource,
                                category="call_fixed_particle",
                                coordinate=coordinate,
                                literal_id=literal_id,
                                text=text,
                                details={
                                    "call_target":
                                        f"{target[0]}:{target[1]}",
                                    "particle":
                                        particle_match.group("particle"),
                                    "variant_count":
                                        len(nonempty_variants),
                                    "mismatch_count": mismatch_count,
                                    "unknown_count": unknown_count,
                                    "jongseong_counts":
                                        dict(sorted(jongseong_counts.items())),
                                },
                                include_text=include_text,
                            )
                        )
                if previous_call is not None:
                    target, _rendered_variants = previous_call
                    artifact_reason = call_semantic_carrier_artifact_reason(
                        target,
                        text,
                    )
                    if artifact_reason is not None:
                        issues.append(
                            issue(
                                resource=resource,
                                category="call_semantic_carrier_artifact",
                                coordinate=coordinate,
                                literal_id=literal_id,
                                text=text,
                                details={
                                    "call_target":
                                        f"{target[0]}:{target[1]}",
                                    "reason": artifact_reason,
                                },
                                include_text=include_text,
                            )
                        )
                previous_selector = None
                previous_call = None
                previous_literal = (literal_id, text)
                continue
            if kind == "call":
                target = tuple(component["target"])
                rendered_variants = renderer.render(target)
                if previous_literal is not None:
                    literal_id, prefix = previous_literal
                    for suffix in rendered_variants:
                        combined = prefix + suffix
                        if not any(
                            pattern.search(combined)
                            for pattern in TERMINAL_DUPLICATION_RES
                        ):
                            continue
                        issues.append(
                            issue(
                                resource=resource,
                                category="duplicated_terminal_boundary",
                                coordinate=coordinate,
                                literal_id=literal_id,
                                text=combined,
                                details={
                                    "call_target":
                                        f"{target[0]}:{target[1]}",
                                    "prefix_sha256":
                                        utf16le_sha256(prefix),
                                    "suffix_sha256":
                                        utf16le_sha256(suffix),
                                },
                                include_text=include_text,
                            )
                        )
                previous_literal = None
                previous_selector = None
                previous_call = (target, rendered_variants)
                continue
            if kind in IGNORABLE_BETWEEN_SELECTOR_AND_LITERAL:
                continue
            previous_selector = None
            previous_literal = None
            previous_call = None

    deduplicated = tuple(
        {
            (
                value.resource,
                value.category,
                value.block_id,
                value.record_id,
                value.literal_id,
                value.text_sha256,
                json.dumps(
                    value.details,
                    ensure_ascii=True,
                    sort_keys=True,
                    separators=(",", ":"),
                ),
            ): value
            for value in issues
        }.values()
    )
    ordered = tuple(
        sorted(
            deduplicated,
            key=lambda value: (
                value.category,
                value.block_id,
                value.record_id,
                -1 if value.literal_id is None else value.literal_id,
                value.text_sha256,
            ),
        )
    )
    return ResourceAudit(
        resource=resource,
        path=str(path.resolve()),
        sha256=blob_sha256,
        record_count=len(records),
        literal_count=literal_count,
        decoded_record_count=decoded,
        issues=ordered,
    )


def report(
    audits: Sequence[ResourceAudit],
) -> dict[str, Any]:
    category_counts = Counter(
        value.category
        for audit in audits
        for value in audit.issues
    )
    resource_counts = {
        audit.resource: {
            "record_count": audit.record_count,
            "literal_count": audit.literal_count,
            "decoded_record_count": audit.decoded_record_count,
            "issue_count": len(audit.issues),
            "category_counts": dict(
                sorted(
                    Counter(
                        value.category for value in audit.issues
                    ).items()
                )
            ),
            "path": audit.path,
            "sha256": audit.sha256,
        }
        for audit in audits
    }
    return {
        "schema": SCHEMA,
        "status": "PASS" if not category_counts else "FAIL",
        "issue_count": sum(category_counts.values()),
        "category_counts": dict(sorted(category_counts.items())),
        "resources": resource_counts,
        "issues": [
            asdict(value)
            for audit in audits
            for value in audit.issues
        ],
        "ghidra_contract": {
            "literal_and_dynamic_output_are_verbatim": True,
            "automatic_space_inserted": False,
            "automatic_punctuation_inserted": False,
            "opcode_0143_calls_record": True,
        },
    }


def canonical_json(value: Any) -> str:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--pk", type=Path, default=DEFAULT_PK)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--include-text",
        action="store_true",
        help="include Korean bodies in the output; keep such reports private",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return exit code 1 when any user-visible defect is found",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    audits = (
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
    payload = report(audits)
    rendered = canonical_json(payload)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "issue_count": payload["issue_count"],
                "category_counts": payload["category_counts"],
                "resources": {
                    key: {
                        "issue_count": value["issue_count"],
                        "category_counts": value["category_counts"],
                        "sha256": value["sha256"],
                    }
                    for key, value in payload["resources"].items()
                },
                "output": (
                    str(args.output.resolve())
                    if args.output is not None
                    else None
                ),
            },
            ensure_ascii=True,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    if args.strict and payload["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
