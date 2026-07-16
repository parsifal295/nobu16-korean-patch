#!/usr/bin/env python3
"""Build a source-free Steam JP v0.9 line-break-only successor.

This workstream imports *only* the pinned Switch v2.2 -> v2.3 delta model
for ``MSG/JP/ev_strdata.bin``.  It deliberately does not copy a Switch
resource, does not import Japanese source prose into a public artifact, and
does not write an installed game file.

The Switch delta has 640 exact coordinates where forced hard line breaks were
replaced by ASCII spaces (1,121 break tokens).  The Steam JP v0.9 predecessor
matches the Switch v2.2 Korean preimage at 625 coordinates.  Eleven remaining
coordinates contain newer Korean wording, so the layout operation is re-based
only after its exact preimage hash, line-break vector, printf/ESC/control/PUA
vectors, and source-derived coordinate contract all pass.  Four coordinates
are Japanese residuals in v0.9: with the approved Switch reference, they are
handled as explicitly separate manual Korean-only translation-and-linebreak
repairs; the Switch reference hash is retained but its residual CJK terms are
not emitted.

Full-width punctuation, U+3000 spaces, and middle-dot normalization are
intentionally outside this builder.  They are a separate, commuting
punctuation-only operation; this builder changes only CRLF/CR/LF into one
ASCII space per break token.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))

import build_common_message_overlay as common  # noqa: E402
from nobu16_lz4 import decompress_wrapper, recompress_wrapper  # noqa: E402
from nobu16_msg_table import MessageTable, parse_message_table, rebuild_message_table  # noqa: E402


RESOURCE = "MSG/JP/ev_strdata.bin"
SWITCH_MEMBER = "NobunagaShinsei_KR/romfs/MSG/JP/ev_strdata.bin"
OVERLAY_SCHEMA = "nobu16.kr.steam-jp-switch-v23-linebreak-overlay.v1"
REVIEW_SCHEMA = "nobu16.kr.steam-jp-switch-v23-linebreak-review.v1"
VALIDATION_SCHEMA = "nobu16.kr.steam-jp-switch-v23-linebreak-validation.v1"
OVERLAY_PATH = WORKSTREAM / "public" / "ev_strdata_ko_switch_v23_linebreak_640.v1.json"
REVIEW_PATH = WORKSTREAM / "review" / "switch_v23_linebreak_deferred.v1.json"
VALIDATION_PATH = WORKSTREAM / "validation.v1.json"
DEFAULT_FULLWIDTH_METADATA_PATH = (
    REPO
    / "workstreams"
    / "steam_jp_fullwidth_normalization_v1"
    / "public"
    / "steam_jp_fullwidth_normalization.v1.json"
)

DEFAULT_SWITCH_V13_ZIP = (
    REPO / "tmp" / "third_party_switch_v13" / "NobunagaShinsei_KoreanPatch_v1.3.zip"
)
DEFAULT_SWITCH_V22_ZIP = (
    REPO / "tmp" / "switch_wheel_button_audit" / "NobunagaShinsei_KoreanPatch_v2.2.zip"
)
DEFAULT_SWITCH_V23_ZIP = (
    REPO / "tmp" / "switch_wheel_button_audit" / "NobunagaShinsei_KoreanPatch_v2.3.zip"
)
DEFAULT_SWITCH_V24_ZIP = (
    REPO / "tmp" / "switch_wheel_button_audit" / "NobunagaShinsei_KoreanPatch_v2.4.zip"
)
DEFAULT_BASELINE_ZIP = (
    REPO
    / "tmp"
    / "steam_jp_117_image_candidate_v1_inputs"
    / "v0.9.0"
    / "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.9.0.zip"
)

ZIP_PINS: dict[str, dict[str, Any]] = {
    "switch_v13": {
        "path": "tmp/third_party_switch_v13/NobunagaShinsei_KoreanPatch_v1.3.zip",
        "size": 72_977_145,
        "sha256": "F4D2563C1B32DB450165C8CCF61C6947DEA904233581036E179AFA1D6A918CC4",
    },
    "switch_v22": {
        "path": "tmp/switch_wheel_button_audit/NobunagaShinsei_KoreanPatch_v2.2.zip",
        "size": 83_752_794,
        "sha256": "5E6354069E38BE22E3B3C9272A6CEC8A4B4110DF2486B9A63E84D1058C35D7F7",
    },
    "switch_v23": {
        "path": "tmp/switch_wheel_button_audit/NobunagaShinsei_KoreanPatch_v2.3.zip",
        "size": 83_756_574,
        "sha256": "A085B5D7F661786CF8E6568A36CF24E7BE1ADF81D042FF8C3D2E220D46A09388",
    },
    "switch_v24": {
        "path": "tmp/switch_wheel_button_audit/NobunagaShinsei_KoreanPatch_v2.4.zip",
        "size": 83_764_122,
        "sha256": "9BAC0A141A7DEBB779BF67EB35F582287B120CBDE6A4B4939AC4903315F7E04C",
    },
    "steam_v09": {
        "path": (
            "tmp/steam_jp_117_image_candidate_v1_inputs/v0.9.0/"
            "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.9.0.zip"
        ),
        "size": 356_951_693,
        "sha256": "1BCC92A3CD7025D307AF9B193BDDD8F1448451024630C8414FC218F0C49FE829",
    },
}

MEMBER_PINS: dict[str, dict[str, Any]] = {
    "switch_v13": {
        "size": 396_257,
        "sha256": "A5D70580790330EF845EC73FDB8D6ACC89EBAD8D026DFE1B1D873C50B43CAD5D",
    },
    "switch_v22": {
        "size": 396_383,
        "sha256": "1BFCE062F91B069A8DBDE0E923407FAADA9798DA81FBBB721BB0F04A02577F37",
    },
    "switch_v23": {
        "size": 395_200,
        "sha256": "F5D0D5DED342F0C4CF6895400927F42543A16C9FCB9FA9F881D4893254A8E7DD",
    },
    "switch_v24": {
        "size": 395_200,
        "sha256": "F5D0D5DED342F0C4CF6895400927F42543A16C9FCB9FA9F881D4893254A8E7DD",
    },
    "steam_v09": {
        "size": 928_464,
        "sha256": "9ED892E85AF18EB3BC965A834853969BC06F486A2466A83F3CEBED1B8D5433C0",
    },
}

EXPECTED = {
    "string_count": 17_868,
    "v22_v23_changed_rows": 1_329,
    "v23_linebreak_rows": 640,
    "v23_linebreak_tokens": 1_121,
    "v23_linebreak_two_token_rows": 481,
    "v23_linebreak_one_token_rows": 159,
    "exact_operations": 625,
    "rebased_operations": 11,
    "residual_translation_repairs": 4,
    "residual_translation_repair_ids_sha256": "3BA90C6EB37BF37E680BE121792EFD827195510E4DEA64A0D07338379D100870",
    "safe_fullwidth_intersection_count": 28,
    "safe_fullwidth_intersection_ids_sha256": "53705CCD9BCE75A1C5974D250C16AFB4E258A3A8B4F79562A8DF792A26D8D147",
    "safe_fullwidth_metadata_sha256": "E902FB90D19B37168C9512A5337CE0A0CB18E1D4EEE77284667BFB7CA7B73329",
    "safe_fullwidth_ev_strdata_operation_count": 526,
    "operation_count": 640,
    "fullwidth_handoff_rows": 686,
    "deferred_rows": 3,
}

LINE_BREAK_RE = re.compile(r"\r\n|\n|\r")
# This is deliberately *not* an output transform.  These are the only
# non-layout substitutions observed while locating the upstream v2.2->v2.3
# line-break coordinates: U+3000, printable full-width ASCII, and the Korean
# middle dot U+00B7 rendered as the game's neutral U+30FB separator.  It is
# reference-only so that a row containing both a punctuation change and a
# removed hard break can still be classified against the Switch delta.  The
# PC target below is always derived from the current Korean preimage solely
# with ``replace_hard_breaks_with_ascii_space``.
SWITCH_REFERENCE_NONLAYOUT_MAP = {"\u00B7": "\u30FB"}
# U+30FB is accepted as a neutral Korean name separator.  Other kana and
# CJK ideographs would mean that source script leaked into a public artifact.
LEXICAL_SOURCE_SCRIPT_RE = re.compile(
    r"[\u3041-\u3096\u309D-\u309F\u30A1-\u30FA\u30FC-\u30FF"
    r"\u31F0-\u31FF\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]"
)
HANGUL_RE = re.compile(r"[\uAC00-\uD7A3]")


class LinebreakError(ValueError):
    """A pinned source, intentional-operation contract, or output diverged."""


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def spec(blob: bytes) -> dict[str, Any]:
    return {"size": len(blob), "sha256": sha256(blob)}


def text_hash(text: str) -> str:
    return sha256(text.encode("utf-16-le"))


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def require_equal(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise LinebreakError(f"{label} differs: expected={expected!r}, actual={actual!r}")


def require_path_spec(path: Path, expected: Mapping[str, Any], label: str) -> bytes:
    if not path.is_file():
        raise LinebreakError(f"missing {label}: {path}")
    blob = path.read_bytes()
    require_equal(spec(blob), {"size": expected["size"], "sha256": expected["sha256"]}, label)
    return blob


def read_zip_member(
    zip_path: Path,
    zip_pin: Mapping[str, Any],
    member: str,
    member_pin: Mapping[str, Any],
    label: str,
) -> bytes:
    require_path_spec(zip_path, zip_pin, f"{label} ZIP")
    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            value = archive.read(member)
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        raise LinebreakError(f"cannot read {label} member: {member}") from exc
    require_equal(spec(value), {"size": member_pin["size"], "sha256": member_pin["sha256"]}, f"{label} member")
    return value


def parse_packed_table(packed: bytes, label: str) -> tuple[Any, bytes, MessageTable]:
    header, raw = decompress_wrapper(packed)
    table = parse_message_table(raw)
    # Several original Switch raw tables deliberately end on a UTF-16 boundary
    # rather than a four-byte boundary.  The shared rebuilder adds canonical
    # zero alignment, so an unchanged source can gain two harmless padding
    # bytes.  Require semantic table round-trip here; candidate validation
    # below separately requires an exact parse/rebuild round-trip after the
    # canonical rebuild.
    unchanged_rebuild = rebuild_message_table(table, table.texts)
    if parse_message_table(unchanged_rebuild).texts != table.texts:
        raise LinebreakError(f"{label} parse/rebuild text round-trip differs")
    if table.string_count != EXPECTED["string_count"]:
        raise LinebreakError(f"{label} string count differs: {table.string_count}")
    return header, raw, table


def linebreaks(text: str) -> tuple[str, ...]:
    return tuple(common.message_invariants(text)["line_breaks"])


def replace_hard_breaks_with_ascii_space(text: str) -> str:
    """Replace each CRLF/CR/LF token with exactly one U+0020, and nothing else."""

    return LINE_BREAK_RE.sub(" ", text)


def switch_reference_nonlayout_normalized(text: str) -> str:
    """Classify the pinned Switch coordinate delta; never mutate PC output."""

    result: list[str] = []
    for character in text:
        codepoint = ord(character)
        if character == "\u3000":
            result.append(" ")
        elif 0xFF01 <= codepoint <= 0xFF5E:
            result.append(chr(codepoint - 0xFEE0))
        elif character in SWITCH_REFERENCE_NONLAYOUT_MAP:
            result.append(SWITCH_REFERENCE_NONLAYOUT_MAP[character])
        else:
            result.append(character)
    return "".join(result)


def protected_signature(text: str) -> dict[str, Any]:
    """The non-layout vectors that a rebased line-break operation must retain."""

    value = common.message_invariants(text)
    return {
        "printf": value["printf"],
        "unknown_percent_count": value["unknown_percent_count"],
        "esc": value["esc"],
        "controls": value["controls"],
        "pua": value["pua"],
    }


def assert_linebreak_only_transition(
    before: str,
    after: str,
    expected_breaks: Sequence[str],
    label: str,
) -> None:
    """Prove the sole mutation is each declared break token becoming U+0020."""

    before_inv = common.message_invariants(before)
    after_inv = common.message_invariants(after)
    require_equal(tuple(before_inv["line_breaks"]), tuple(expected_breaks), f"{label} pre line-break vector")
    require_equal(after_inv["line_breaks"], [], f"{label} post line-break vector")
    require_equal(after, replace_hard_breaks_with_ascii_space(before), f"{label} byte-level text transform")
    require_equal(protected_signature(after), protected_signature(before), f"{label} protected token vector")
    require_equal(after_inv["leading_whitespace"], before_inv["leading_whitespace"], f"{label} leading whitespace")
    require_equal(after_inv["trailing_whitespace"], before_inv["trailing_whitespace"], f"{label} trailing whitespace")
    mismatches = common.invariant_mismatches(before, after)
    if any(not item.startswith("line_breaks:") for item in mismatches):
        raise LinebreakError(f"{label} changed a non-line-break invariant: {mismatches!r}")
    if not mismatches:
        raise LinebreakError(f"{label} has no recorded line-break mismatch")


def _codepoints(*values: int) -> str:
    return "".join(chr(value) for value in values)


def manual_koreanize_switch_v23_residual(entry_id: int, switch_v23_target: str) -> str:
    """Apply four glossary-backed CJK cleanups to an approved Korean reference.

    The reference is only an input to this function.  Its CJK terms are never
    emitted in a public model: the result is required to be CJK/kana-free
    Korean.  Each substitution is anchored to a known residual coordinate so
    it cannot become a generic source-text conversion rule.
    """

    if entry_id == 3917:
        source = "어가인(" + _codepoints(0x5FA1, 0x5BB6, 0x4EBA) + ")"
        target = "고케닌"
    elif entry_id == 7260:
        source = "통(" + _codepoints(0x5927, 0x7B52) + ")"
        target = "포"
    elif entry_id == 8818:
        source = "(" + _codepoints(0x60E3, 0x7121, 0x4E8B) + ")"
        if switch_v23_target.count("\u300C") != 1 or switch_v23_target.count("\u300D") != 1:
            raise LinebreakError(f"manual Korean repair quote contract differs at {entry_id}")
        switch_v23_target = switch_v23_target.replace("\u300C", "'").replace("\u300D", "'")
        target = ""
    elif entry_id == 8904:
        source = "(" + _codepoints(0x5165, 0x9053) + ")"
        target = ""
    else:
        raise LinebreakError(f"unexpected manual Korean residual coordinate: {entry_id}")
    if switch_v23_target.count(source) != 1:
        raise LinebreakError(f"manual Korean repair source-term contract differs at {entry_id}")
    result = switch_v23_target.replace(source, target)
    if result == switch_v23_target:
        raise LinebreakError(f"manual Korean repair has no effect at {entry_id}")
    return result


def assert_manual_korean_residual_translation_and_linebreak_repair(
    current_before: str,
    switch_v22_before: str,
    switch_v23_reference: str,
    manual_korean_target: str,
    label: str,
) -> None:
    """Validate an approved Korean repair without exposing its Japanese preimage.

    This intentionally differs from ``assert_linebreak_only_transition``:
    the v0.9 preimage is known Japanese residual text, while the public target
    is a CJK/kana-free Korean repair based on the approved Switch v2.3 Korean
    reference with the same source-derived hard-break vector removed.
    Renderer-sensitive vectors must nevertheless be identical end-to-end.
    """

    if current_before == switch_v22_before:
        raise LinebreakError(f"{label} is not a residual translation repair")
    require_equal(
        linebreaks(current_before),
        linebreaks(switch_v22_before),
        f"{label} source-derived pre line-break vector",
    )
    require_equal(
        protected_signature(current_before),
        protected_signature(switch_v22_before),
        f"{label} preimage protected vector",
    )
    require_equal(
        switch_v23_reference,
        replace_hard_breaks_with_ascii_space(switch_reference_nonlayout_normalized(switch_v22_before)),
        f"{label} approved Switch v2.3 reference",
    )
    if manual_korean_target == switch_v23_reference:
        raise LinebreakError(f"{label} did not remove CJK reference terms")
    require_equal(linebreaks(manual_korean_target), (), f"{label} target line-break vector")
    require_equal(
        protected_signature(manual_korean_target),
        protected_signature(current_before),
        f"{label} protected vector preservation",
    )
    require_equal(
        common.message_invariants(manual_korean_target)["leading_whitespace"],
        common.message_invariants(current_before)["leading_whitespace"],
        f"{label} leading whitespace",
    )
    require_equal(
        common.message_invariants(manual_korean_target)["trailing_whitespace"],
        common.message_invariants(current_before)["trailing_whitespace"],
        f"{label} trailing whitespace",
    )
    if HANGUL_RE.search(manual_korean_target) is None:
        raise LinebreakError(f"{label} target is not Korean text")
    if LEXICAL_SOURCE_SCRIPT_RE.search(manual_korean_target):
        raise LinebreakError(f"{label} target retains lexical source script")


def id_vector_hash(ids: Iterable[int]) -> str:
    return sha256("".join(f"{entry_id}\n" for entry_id in sorted(ids)).encode("ascii"))


def source_free(value: Any, label: str) -> None:
    encoded = canonical_json_bytes(value).decode("utf-8")
    if LEXICAL_SOURCE_SCRIPT_RE.search(encoded):
        raise LinebreakError(f"{label} contains lexical Japanese/CJK source script")
    if "\0" in encoded:
        raise LinebreakError(f"{label} contains an embedded NUL")


def load_inputs(
    baseline_zip: Path,
    switch_v13_zip: Path,
    switch_v22_zip: Path,
    switch_v23_zip: Path,
    switch_v24_zip: Path,
) -> dict[str, Any]:
    """Read all pinned inputs and prove the v2.4 text member retained v2.3."""

    switch_v13 = read_zip_member(
        switch_v13_zip, ZIP_PINS["switch_v13"], SWITCH_MEMBER, MEMBER_PINS["switch_v13"], "Switch v1.3"
    )
    switch_v22 = read_zip_member(
        switch_v22_zip, ZIP_PINS["switch_v22"], SWITCH_MEMBER, MEMBER_PINS["switch_v22"], "Switch v2.2"
    )
    switch_v23 = read_zip_member(
        switch_v23_zip, ZIP_PINS["switch_v23"], SWITCH_MEMBER, MEMBER_PINS["switch_v23"], "Switch v2.3"
    )
    switch_v24 = read_zip_member(
        switch_v24_zip, ZIP_PINS["switch_v24"], SWITCH_MEMBER, MEMBER_PINS["switch_v24"], "Switch v2.4"
    )
    require_equal(switch_v24, switch_v23, "Switch v2.4 text retention of v2.3")
    baseline = read_zip_member(
        baseline_zip, ZIP_PINS["steam_v09"], RESOURCE, MEMBER_PINS["steam_v09"], "Steam v0.9 baseline"
    )
    parsed = {
        "switch_v13": parse_packed_table(switch_v13, "Switch v1.3"),
        "switch_v22": parse_packed_table(switch_v22, "Switch v2.2"),
        "switch_v23": parse_packed_table(switch_v23, "Switch v2.3"),
        "steam_v09": parse_packed_table(baseline, "Steam v0.9"),
    }
    return {
        "packed": {
            "switch_v13": switch_v13,
            "switch_v22": switch_v22,
            "switch_v23": switch_v23,
            "switch_v24": switch_v24,
            "steam_v09": baseline,
        },
        "parsed": parsed,
    }


def classify_switch_v23_delta(
    v22: Sequence[str], v23: Sequence[str]
) -> tuple[list[int], list[int], list[int]]:
    """Partition the exact v2.2->v2.3 delta without emitting source prose."""

    if len(v22) != len(v23):
        raise LinebreakError("Switch v2.2/v2.3 string counts differ")
    linebreak_ids: list[int] = []
    fullwidth_handoff_ids: list[int] = []
    deferred_ids: list[int] = []
    changed = 0
    for entry_id, (before, after) in enumerate(zip(v22, v23, strict=True)):
        if before == after:
            continue
        changed += 1
        before_breaks = linebreaks(before)
        after_breaks = linebreaks(after)
        if (
            before_breaks
            and not after_breaks
            and replace_hard_breaks_with_ascii_space(switch_reference_nonlayout_normalized(before)) == after
        ):
            linebreak_ids.append(entry_id)
        elif switch_reference_nonlayout_normalized(before) == after:
            fullwidth_handoff_ids.append(entry_id)
        else:
            deferred_ids.append(entry_id)
    require_equal(changed, EXPECTED["v22_v23_changed_rows"], "Switch v2.2->v2.3 changed row count")
    require_equal(len(linebreak_ids), EXPECTED["v23_linebreak_rows"], "Switch v2.3 line-break row count")
    require_equal(
        sum(len(linebreaks(v22[entry_id])) for entry_id in linebreak_ids),
        EXPECTED["v23_linebreak_tokens"],
        "Switch v2.3 line-break token count",
    )
    require_equal(
        sum(len(linebreaks(v22[entry_id])) == 2 for entry_id in linebreak_ids),
        EXPECTED["v23_linebreak_two_token_rows"],
        "Switch v2.3 two-break row count",
    )
    require_equal(
        sum(len(linebreaks(v22[entry_id])) == 1 for entry_id in linebreak_ids),
        EXPECTED["v23_linebreak_one_token_rows"],
        "Switch v2.3 one-break row count",
    )
    require_equal(len(fullwidth_handoff_ids), EXPECTED["fullwidth_handoff_rows"], "full-width handoff row count")
    require_equal(len(deferred_ids), EXPECTED["deferred_rows"], "unclassified v2.3 deferred count")
    return linebreak_ids, fullwidth_handoff_ids, deferred_ids


def make_operations(inputs: Mapping[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Create 625 exact, 11 Korean rebase, and 4 explicit residual repairs."""

    parsed = inputs["parsed"]
    v13 = parsed["switch_v13"][2].texts
    v22 = parsed["switch_v22"][2].texts
    v23 = parsed["switch_v23"][2].texts
    v09 = parsed["steam_v09"][2].texts
    linebreak_ids, fullwidth_handoff_ids, deferred_ids = classify_switch_v23_delta(v22, v23)

    operations: list[dict[str, Any]] = []
    direct_ids: list[int] = []
    rebased_ids: list[int] = []
    residual_repair_ids: list[int] = []
    for entry_id in linebreak_ids:
        upstream_before = v22[entry_id]
        current_before = v09[entry_id]
        break_vector = linebreaks(upstream_before)
        if current_before == upstream_before:
            # The v1.3 transfer text, Switch v2.2 predecessor, and v0.9
            # package must all be the exact same Korean preimage here.
            require_equal(v13[entry_id], upstream_before, f"exact operation v1.3 preimage at {entry_id}")
            operation = "switch_v23_coordinate_exact_linebreak_to_ascii_space"
            target = replace_hard_breaks_with_ascii_space(current_before)
            assert_linebreak_only_transition(current_before, target, break_vector, f"operation {entry_id}")
            direct_ids.append(entry_id)
        elif LEXICAL_SOURCE_SCRIPT_RE.search(current_before):
            # The public artifact stores a CJK/kana-free manual Korean target
            # and only a hash of this Japanese v0.9 residual preimage.  The
            # approved Switch v2.3 target remains hash-only reference evidence
            # because its Korean prose still has a few CJK terms.
            operation = "manual_korean_residual_translation_and_linebreak_repair"
            target = manual_koreanize_switch_v23_residual(entry_id, v23[entry_id])
            assert_manual_korean_residual_translation_and_linebreak_repair(
                current_before,
                upstream_before,
                v23[entry_id],
                target,
                f"residual repair {entry_id}",
            )
            residual_repair_ids.append(entry_id)
        else:
            # Newer project wording is preserved.  We only rebase the layout
            # operation after comparing the source-derived break vector and
            # all renderer-sensitive protected vectors.
            require_equal(linebreaks(current_before), break_vector, f"rebase break vector at {entry_id}")
            require_equal(
                protected_signature(current_before),
                protected_signature(upstream_before),
                f"rebase protected source vector at {entry_id}",
            )
            operation = "switch_v23_rebased_linebreak_to_ascii_space"
            target = replace_hard_breaks_with_ascii_space(current_before)
            assert_linebreak_only_transition(current_before, target, break_vector, f"operation {entry_id}")
            rebased_ids.append(entry_id)
        if target == current_before:
            raise LinebreakError(f"operation has no effect at {entry_id}")
        if HANGUL_RE.search(target) is None:
            raise LinebreakError(f"operation {entry_id} is not Korean text")
        if LEXICAL_SOURCE_SCRIPT_RE.search(target):
            raise LinebreakError(f"operation {entry_id} retains lexical source script")
        operations.append(
            {
                "id": entry_id,
                "operation": operation,
                "preimage_utf16le_sha256": text_hash(current_before),
                "preimage_linebreak_vector": list(linebreaks(current_before)),
                "preimage_protected_signature": protected_signature(current_before),
                "ko": target,
                "ko_utf16le_sha256": text_hash(target),
                "target_protected_signature": protected_signature(target),
                "linebreak_token_count": len(break_vector),
                "source_v22_ko_utf16le_sha256": text_hash(upstream_before),
                "switch_v23_reference_ko_utf16le_sha256": text_hash(v23[entry_id]),
            }
        )

    require_equal(len(operations), EXPECTED["operation_count"], "operation count")
    require_equal(len(direct_ids), EXPECTED["exact_operations"], "exact operation count")
    require_equal(len(rebased_ids), EXPECTED["rebased_operations"], "rebased operation count")
    require_equal(
        len(residual_repair_ids),
        EXPECTED["residual_translation_repairs"],
        "residual translation repair count",
    )
    require_equal(
        id_vector_hash(residual_repair_ids),
        EXPECTED["residual_translation_repair_ids_sha256"],
        "residual translation repair coordinate hash",
    )
    require_equal(
        sum(operation["linebreak_token_count"] for operation in operations),
        EXPECTED["v23_linebreak_tokens"],
        "operation line-break token count",
    )
    if [operation["id"] for operation in operations] != sorted(linebreak_ids):
        raise LinebreakError("operation coordinates are not sorted or do not equal source line-break coordinates")

    review = {
        "schema": REVIEW_SCHEMA,
        "resource": RESOURCE,
        "scope": "unclassified_switch_v22_to_v23_text_delta_not_applied",
        "entry_count": len(deferred_ids),
        "entry_ids_sha256": id_vector_hash(deferred_ids),
        "entries": [
            {
                "id": entry_id,
                "reason": "not_linebreak_to_ascii_space_or_punctuation_only",
                "source_v22_ko_utf16le_sha256": text_hash(v22[entry_id]),
                "switch_v23_reference_ko_utf16le_sha256": text_hash(v23[entry_id]),
            }
            for entry_id in deferred_ids
        ],
    }
    handoff = {
        "entry_count": len(fullwidth_handoff_ids),
        "entry_ids_sha256": id_vector_hash(fullwidth_handoff_ids),
        "policy": "handled_by_separate_punctuation_only_workstream",
    }
    source_free(review, "review model")
    return operations, {"review": review, "handoff": handoff}


def make_overlay(inputs: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    operations, auxiliary = make_operations(inputs)
    exact_count = sum(
        operation["operation"] == "switch_v23_coordinate_exact_linebreak_to_ascii_space"
        for operation in operations
    )
    rebased_count = sum(
        operation["operation"] == "switch_v23_rebased_linebreak_to_ascii_space"
        for operation in operations
    )
    residual_repair_count = sum(
        operation["operation"] == "manual_korean_residual_translation_and_linebreak_repair"
        for operation in operations
    )
    overlay = {
        "schema": OVERLAY_SCHEMA,
        "overlay_id": "steam-jp-switch-v23-linebreak-640-v1",
        "resource": RESOURCE,
        "base_language": "JP",
        "runtime": {
            "distribution": "Steam",
            "pk_version": "1.1.7",
            "steam_build_id": 18_823_764,
            "predecessor_release": "v0.9.0",
        },
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
            "contains_switch_binary": False,
            "installed_game_file_written": False,
        },
        "inputs": {
            "steam_v09": {"zip": dict(ZIP_PINS["steam_v09"]), "resource": dict(MEMBER_PINS["steam_v09"])},
            "switch_v13": {"zip": dict(ZIP_PINS["switch_v13"]), "member": dict(MEMBER_PINS["switch_v13"])},
            "switch_v22": {"zip": dict(ZIP_PINS["switch_v22"]), "member": dict(MEMBER_PINS["switch_v22"])},
            "switch_v23": {"zip": dict(ZIP_PINS["switch_v23"]), "member": dict(MEMBER_PINS["switch_v23"])},
            "switch_v24": {
                "zip": dict(ZIP_PINS["switch_v24"]),
                "member": dict(MEMBER_PINS["switch_v24"]),
                "text_member_byte_identical_to_v23": True,
            },
        },
        "source_delta": {
            "v22_to_v23_changed_rows": EXPECTED["v22_v23_changed_rows"],
            "linebreak_coordinate_count": EXPECTED["v23_linebreak_rows"],
            "linebreak_token_count": EXPECTED["v23_linebreak_tokens"],
            "two_break_row_count": EXPECTED["v23_linebreak_two_token_rows"],
            "one_break_row_count": EXPECTED["v23_linebreak_one_token_rows"],
            "coordinate_ids_sha256": id_vector_hash(operation["id"] for operation in operations),
        },
        "operation_policy": {
            "linebreak_only_entry_count": exact_count + rebased_count,
            "linebreak_only_replacement": "each CRLF/CR/LF token becomes exactly one ASCII space",
            "translation_and_linebreak_repair_entry_count": residual_repair_count,
            "translation_repair_target": "manual Korean target, glossary-backed against Switch v2.3 reference",
            "translation_repair_japanese_preimage_emitted": False,
            "translation_repair_switch_reference_hash_only": True,
            "generic_newline_stripping_forbidden": True,
            "fullwidth_middle_dot_changes_excluded_from_linebreak_only_entries": True,
            "preimage_hash_required": True,
            "rebase_requires_matching_linebreak_vector": True,
            "rebase_requires_printf_esc_control_pua_vector": True,
            "linebreak_only_output_requires_only_linebreak_invariant_difference": True,
            "residual_repair_requires_printf_esc_control_pua_vector": True,
        },
        "entry_count": len(operations),
        "exact_entry_count": exact_count,
        "rebased_entry_count": rebased_count,
        "residual_translation_repair_entry_count": residual_repair_count,
        "entries": operations,
    }
    source_free(overlay, "overlay model")
    return overlay, auxiliary


U_CODEPOINT_RE = re.compile(r"U\+([0-9A-F]{4,6})$")
SHA256_RE = re.compile(r"[0-9A-F]{64}$")


def parse_u_codepoint(value: Any, label: str) -> str:
    if not isinstance(value, str):
        raise LinebreakError(f"{label} codepoint is not a string")
    match = U_CODEPOINT_RE.fullmatch(value)
    if match is None:
        raise LinebreakError(f"{label} codepoint is invalid: {value!r}")
    number = int(match.group(1), 16)
    if number > 0x10FFFF or 0xD800 <= number <= 0xDFFF:
        raise LinebreakError(f"{label} codepoint is outside Unicode scalar range")
    return chr(number)


def validate_linebreak_overlay_entry(before: str, entry: Mapping[str, Any]) -> tuple[str, str, int]:
    """Validate one public linebreak entry against its exact v0.9 cell."""

    entry_id = entry.get("id")
    if not isinstance(entry_id, int) or entry_id < 0:
        raise LinebreakError(f"overlay entry id is invalid: {entry_id!r}")
    require_equal(text_hash(before), entry.get("preimage_utf16le_sha256"), f"preimage hash at {entry_id}")
    recorded_breaks = entry.get("preimage_linebreak_vector")
    if not isinstance(recorded_breaks, list) or not all(isinstance(value, str) for value in recorded_breaks):
        raise LinebreakError(f"preimage line-break vector is invalid at {entry_id}")
    require_equal(tuple(recorded_breaks), linebreaks(before), f"preimage line-break vector at {entry_id}")
    require_equal(
        protected_signature(before),
        entry.get("preimage_protected_signature"),
        f"preimage protected signature at {entry_id}",
    )
    after = entry.get("ko")
    if not isinstance(after, str):
        raise LinebreakError(f"target Korean text is invalid at {entry_id}")
    if HANGUL_RE.search(after) is None or LEXICAL_SOURCE_SCRIPT_RE.search(after):
        raise LinebreakError(f"target is not Korean-only text at {entry_id}")
    require_equal(
        protected_signature(after),
        entry.get("target_protected_signature"),
        f"target protected signature at {entry_id}",
    )
    count = entry.get("linebreak_token_count")
    if not isinstance(count, int) or count < 1:
        raise LinebreakError(f"line-break count is invalid at {entry_id}")
    require_equal(len(linebreaks(before)), count, f"recorded line-break count at {entry_id}")
    require_equal(text_hash(after), entry.get("ko_utf16le_sha256"), f"target hash at {entry_id}")
    operation = entry.get("operation")
    if operation in {
        "switch_v23_coordinate_exact_linebreak_to_ascii_space",
        "switch_v23_rebased_linebreak_to_ascii_space",
    }:
        assert_linebreak_only_transition(before, after, linebreaks(before), f"apply operation {entry_id}")
    elif operation == "manual_korean_residual_translation_and_linebreak_repair":
        require_equal(linebreaks(after), (), f"residual repair target line-break vector at {entry_id}")
        require_equal(
            protected_signature(after),
            protected_signature(before),
            f"residual repair protected vector at {entry_id}",
        )
        reference_hash = entry.get("switch_v23_reference_ko_utf16le_sha256")
        if not isinstance(reference_hash, str) or SHA256_RE.fullmatch(reference_hash) is None:
            raise LinebreakError(f"residual repair Switch reference hash is invalid at {entry_id}")
    else:
        raise LinebreakError(f"unexpected operation type at {entry_id}: {operation!r}")
    return after, str(operation), count


def extract_fullwidth_ev_strdata_operations(fullwidth_metadata: Mapping[str, Any]) -> dict[int, Mapping[str, Any]]:
    """Read only another workstream's hash-gated ev_strdata operation model.

    This does not copy or emit punctuation targets.  It accepts the external
    fullwidth model solely so a caller can compose both independent v0.9
    preimage-gated passes for coordinates that overlap.
    """

    raw_operations = fullwidth_metadata.get("operations")
    if not isinstance(raw_operations, list):
        raise LinebreakError("fullwidth operation model has no operations list")
    result: dict[int, Mapping[str, Any]] = {}
    for external in raw_operations:
        if not isinstance(external, Mapping) or external.get("resource") != RESOURCE:
            continue
        if external.get("kind") != "table":
            raise LinebreakError("fullwidth ev_strdata operation kind differs")
        coordinate = external.get("coordinate")
        if not isinstance(coordinate, Mapping) or tuple(coordinate) != ("id",):
            raise LinebreakError("fullwidth ev_strdata coordinate differs")
        entry_id = coordinate.get("id")
        if not isinstance(entry_id, int) or entry_id < 0 or entry_id in result:
            raise LinebreakError("fullwidth ev_strdata coordinate is invalid or duplicated")
        if not isinstance(external.get("before_utf16le_sha256"), str) or not isinstance(
            external.get("after_utf16le_sha256"), str
        ):
            raise LinebreakError("fullwidth ev_strdata hash gate is absent")
        character_operations = external.get("character_operations")
        if not isinstance(character_operations, list) or not character_operations:
            raise LinebreakError("fullwidth ev_strdata character operations are absent")
        for character_operation in character_operations:
            if not isinstance(character_operation, Mapping):
                raise LinebreakError("fullwidth ev_strdata character operation is invalid")
            if character_operation.get("operation_type") != "fullwidth_ascii":
                raise LinebreakError(
                    "only safe ASCII-width fullwidth operations may join this composition"
                )
            if (
                character_operation.get("from") == "U+00B7"
                or character_operation.get("to") == "U+30FB"
            ):
                raise LinebreakError("middle-dot operation is deferred pending the font prerequisite")
        result[entry_id] = external
    return result


def fullwidth_target_from_external_operation(before: str, external: Mapping[str, Any], label: str) -> str:
    """Reproduce one external punctuation target from an exact v0.9 preimage."""

    require_equal(text_hash(before), external.get("before_utf16le_sha256"), f"{label} fullwidth preimage hash")
    external_protected = external.get("protected_invariants")
    if not isinstance(external_protected, Mapping):
        raise LinebreakError(f"{label} fullwidth protected signature is absent")
    local_invariants = common.message_invariants(before)
    for local_key, external_key in (
        ("printf", "printf"),
        ("esc", "esc"),
        ("controls", "controls"),
        ("line_breaks", "line_breaks"),
        ("pua", "pua"),
        ("leading_whitespace", "leading_whitespace"),
        ("trailing_whitespace", "trailing_whitespace"),
    ):
        require_equal(
            external_protected.get(external_key),
            local_invariants[local_key],
            f"{label} fullwidth protected {external_key}",
        )
    operations = external.get("character_operations")
    if not isinstance(operations, list):
        raise LinebreakError(f"{label} fullwidth character operations are absent")
    output = list(before)
    previous_index = -1
    for item in operations:
        if not isinstance(item, Mapping):
            raise LinebreakError(f"{label} fullwidth character operation is invalid")
        index = item.get("char_index")
        if not isinstance(index, int) or index <= previous_index or index < 0 or index >= len(output):
            raise LinebreakError(f"{label} fullwidth character index is invalid")
        previous_index = index
        original = parse_u_codepoint(item.get("from"), f"{label} fullwidth source")
        replacement = parse_u_codepoint(item.get("to"), f"{label} fullwidth target")
        if original in "\r\n" or replacement in "\r\n":
            raise LinebreakError(f"{label} fullwidth operation touches a line break")
        if output[index] != original:
            raise LinebreakError(f"{label} fullwidth source character differs at {index}")
        output[index] = replacement
    after = "".join(output)
    require_equal(text_hash(after), external.get("after_utf16le_sha256"), f"{label} fullwidth target hash")
    require_equal(common.invariant_mismatches(before, after), [], f"{label} fullwidth invariant preservation")
    return after


def fullwidth_linebreak_intersection(
    overlay: Mapping[str, Any], fullwidth_metadata: Mapping[str, Any]
) -> dict[str, Any]:
    """Return source-free overlap evidence without embedding external operations."""

    entries = overlay.get("entries")
    if not isinstance(entries, list):
        raise LinebreakError("linebreak overlay has no entries")
    linebreak_ids = {entry.get("id") for entry in entries if isinstance(entry, Mapping)}
    if len(linebreak_ids) != len(entries) or not all(isinstance(entry_id, int) for entry_id in linebreak_ids):
        raise LinebreakError("linebreak overlay coordinate set is invalid")
    fullwidth = extract_fullwidth_ev_strdata_operations(fullwidth_metadata)
    overlap = sorted(linebreak_ids & set(fullwidth))
    line_entries = {int(entry["id"]): entry for entry in entries if isinstance(entry, Mapping)}
    manual_overlap = [
        entry_id
        for entry_id in overlap
        if line_entries[entry_id].get("operation")
        == "manual_korean_residual_translation_and_linebreak_repair"
    ]
    return {
        "fullwidth_model_sha256": sha256(canonical_json_bytes(fullwidth_metadata)),
        "fullwidth_ev_strdata_operation_count": len(fullwidth),
        "intersection_entry_count": len(overlap),
        "intersection_entry_ids_sha256": id_vector_hash(overlap),
        "manual_residual_intersection_count": len(manual_overlap),
        "manual_residual_intersection_ids_sha256": id_vector_hash(manual_overlap),
        "composition_order_for_linebreak_only_overlap": "v0.9 -> fullwidth_punctuation -> CRLF_CR_LF_to_ascii_space",
        "manual_residual_overlap_allowed": False,
        "safe_ascii_only_fullwidth_model": True,
        "middle_dot_composition_included": False,
        "middle_dot_font_prerequisite_deferred": True,
    }


def apply_overlay_to_baseline(packed: bytes, overlay: Mapping[str, Any]) -> tuple[bytes, dict[str, Any]]:
    """Rebuild a candidate in memory, with a hash gate before every mutation."""

    header, raw, table = parse_packed_table(packed, "Steam v0.9 baseline candidate")
    entries = overlay.get("entries")
    if not isinstance(entries, list):
        raise LinebreakError("overlay entries are absent")
    if len(entries) != EXPECTED["operation_count"]:
        raise LinebreakError("overlay operation count differs")
    texts = list(table.texts)
    selected: set[int] = set()
    exact_count = 0
    rebased_count = 0
    residual_repair_count = 0
    token_count = 0
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise LinebreakError("overlay entry is not an object")
        entry_id = entry.get("id")
        if not isinstance(entry_id, int) or entry_id < 0 or entry_id >= len(texts):
            raise LinebreakError(f"overlay entry id is invalid: {entry_id!r}")
        if entry_id in selected:
            raise LinebreakError(f"duplicate overlay entry id: {entry_id}")
        selected.add(entry_id)
        before = texts[entry_id]
        after, operation, count = validate_linebreak_overlay_entry(before, entry)
        if operation == "switch_v23_coordinate_exact_linebreak_to_ascii_space":
            exact_count += 1
        elif operation == "switch_v23_rebased_linebreak_to_ascii_space":
            rebased_count += 1
        elif operation == "manual_korean_residual_translation_and_linebreak_repair":
            residual_repair_count += 1
        else:
            raise LinebreakError(f"unexpected operation type at {entry_id}: {operation!r}")
        token_count += count
        texts[entry_id] = after

    require_equal(exact_count, EXPECTED["exact_operations"], "applied exact operation count")
    require_equal(rebased_count, EXPECTED["rebased_operations"], "applied rebased operation count")
    require_equal(
        residual_repair_count,
        EXPECTED["residual_translation_repairs"],
        "applied residual translation repair count",
    )
    require_equal(token_count, EXPECTED["v23_linebreak_tokens"], "applied line-break token count")
    candidate_raw = rebuild_message_table(table, texts)
    candidate = recompress_wrapper(candidate_raw, header)
    candidate_header, candidate_roundtrip = decompress_wrapper(candidate)
    require_equal(candidate_header.prefix, header.prefix, "candidate wrapper prefix")
    require_equal(candidate_roundtrip, candidate_raw, "candidate wrapper round-trip")
    candidate_table = parse_message_table(candidate_raw)
    require_equal(candidate_table.string_count, table.string_count, "candidate string count")
    changed = {
        entry_id
        for entry_id, (before, after) in enumerate(zip(table.texts, candidate_table.texts, strict=True))
        if before != after
    }
    require_equal(changed, selected, "candidate changed-coordinate domain")
    for entry in entries:
        entry_id = int(entry["id"])
        require_equal(candidate_table.texts[entry_id], entry["ko"], f"candidate output at {entry_id}")
    return candidate, {
        "packed": spec(candidate),
        "raw": spec(candidate_raw),
        "changed_entry_count": len(changed),
        "changed_entry_ids_sha256": id_vector_hash(changed),
        "exact_entry_count": exact_count,
        "rebased_entry_count": rebased_count,
        "residual_translation_repair_entry_count": residual_repair_count,
        "linebreak_tokens_replaced": token_count,
        "raw_parse_rebuild_valid": rebuild_message_table(candidate_table, candidate_table.texts) == candidate_raw,
        "wrapper_prefix_preserved": True,
    }


def apply_composed_fullwidth_and_linebreak_to_baseline(
    packed: bytes,
    overlay: Mapping[str, Any],
    fullwidth_metadata: Mapping[str, Any],
) -> tuple[bytes, dict[str, Any]]:
    """Compose two independently v0.9-hash-gated passes for this one resource.

    The external fullwidth model remains external: this API reads its
    character-operation records at call time and emits no copy of them.  For
    an overlapping linebreak-only cell it constructs exactly
    ``v0.9 -> punctuation -> hard-break-to-space``.  Manual residual repairs
    are intentionally rejected on overlap because their Korean prose is a
    separate translation decision rather than a commuting layout operation.
    """

    source_free(fullwidth_metadata, "fullwidth composition input")
    header, _raw, table = parse_packed_table(packed, "Steam v0.9 composed candidate")
    entries = overlay.get("entries")
    if not isinstance(entries, list) or len(entries) != EXPECTED["operation_count"]:
        raise LinebreakError("linebreak overlay operation count differs for composition")
    external = extract_fullwidth_ev_strdata_operations(fullwidth_metadata)
    report = fullwidth_linebreak_intersection(overlay, fullwidth_metadata)
    if report["manual_residual_intersection_count"] != 0:
        raise LinebreakError("manual residual repair overlaps a fullwidth operation; manual composition is required")

    line_entries: dict[int, Mapping[str, Any]] = {}
    line_targets: dict[int, str] = {}
    line_token_count = 0
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise LinebreakError("linebreak composition entry is invalid")
        entry_id = entry.get("id")
        if not isinstance(entry_id, int) or entry_id < 0 or entry_id >= table.string_count:
            raise LinebreakError("linebreak composition coordinate is invalid")
        if entry_id in line_entries:
            raise LinebreakError("linebreak composition coordinate is duplicated")
        target, _operation, count = validate_linebreak_overlay_entry(table.texts[entry_id], entry)
        line_entries[entry_id] = entry
        line_targets[entry_id] = target
        line_token_count += count
    require_equal(line_token_count, EXPECTED["v23_linebreak_tokens"], "composed line-break token count")

    replacements: dict[int, str] = {}
    for entry_id, external_entry in external.items():
        if entry_id >= table.string_count:
            raise LinebreakError(f"fullwidth composition coordinate is outside table: {entry_id}")
        replacements[entry_id] = fullwidth_target_from_external_operation(
            table.texts[entry_id], external_entry, f"fullwidth composition {entry_id}"
        )
    for entry_id, line_entry in line_entries.items():
        operation = line_entry.get("operation")
        if entry_id not in replacements:
            replacements[entry_id] = line_targets[entry_id]
            continue
        if operation == "manual_korean_residual_translation_and_linebreak_repair":
            raise LinebreakError(f"manual residual overlap unexpectedly reached composition at {entry_id}")
        punctuation_target = replacements[entry_id]
        combined_target = replace_hard_breaks_with_ascii_space(punctuation_target)
        assert_linebreak_only_transition(
            punctuation_target,
            combined_target,
            linebreaks(punctuation_target),
            f"composed overlap {entry_id}",
        )
        if HANGUL_RE.search(combined_target) is None or LEXICAL_SOURCE_SCRIPT_RE.search(combined_target):
            raise LinebreakError(f"composed overlap target is not Korean-only at {entry_id}")
        replacements[entry_id] = combined_target

    candidate_raw = rebuild_message_table(table, [replacements.get(index, text) for index, text in enumerate(table.texts)])
    candidate = recompress_wrapper(candidate_raw, header)
    _candidate_header, candidate_roundtrip = decompress_wrapper(candidate)
    require_equal(candidate_roundtrip, candidate_raw, "composed candidate wrapper round-trip")
    candidate_table = parse_message_table(candidate_raw)
    changed = {
        entry_id
        for entry_id, (before, after) in enumerate(zip(table.texts, candidate_table.texts, strict=True))
        if before != after
    }
    require_equal(changed, set(replacements), "composed candidate changed-coordinate domain")
    return candidate, {
        "packed": spec(candidate),
        "raw": spec(candidate_raw),
        "changed_entry_count": len(changed),
        "changed_entry_ids_sha256": id_vector_hash(changed),
        "linebreak_tokens_replaced": line_token_count,
        "fullwidth_linebreak_composition": report,
        "fullwidth_operations_embedded_in_linebreak_overlay": False,
        "raw_parse_rebuild_valid": rebuild_message_table(candidate_table, candidate_table.texts) == candidate_raw,
    }


def expected_artifacts(
    baseline_zip: Path = DEFAULT_BASELINE_ZIP,
    switch_v13_zip: Path = DEFAULT_SWITCH_V13_ZIP,
    switch_v22_zip: Path = DEFAULT_SWITCH_V22_ZIP,
    switch_v23_zip: Path = DEFAULT_SWITCH_V23_ZIP,
    switch_v24_zip: Path = DEFAULT_SWITCH_V24_ZIP,
    fullwidth_metadata_path: Path = DEFAULT_FULLWIDTH_METADATA_PATH,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], bytes]:
    inputs = load_inputs(baseline_zip, switch_v13_zip, switch_v22_zip, switch_v23_zip, switch_v24_zip)
    overlay, auxiliary = make_overlay(inputs)
    fullwidth_metadata = read_fullwidth_metadata(fullwidth_metadata_path)
    fullwidth_composition = fullwidth_linebreak_intersection(overlay, fullwidth_metadata)
    require_equal(
        fullwidth_composition["fullwidth_model_sha256"],
        EXPECTED["safe_fullwidth_metadata_sha256"],
        "safe fullwidth metadata hash",
    )
    require_equal(
        fullwidth_composition["fullwidth_ev_strdata_operation_count"],
        EXPECTED["safe_fullwidth_ev_strdata_operation_count"],
        "safe fullwidth ev_strdata operation count",
    )
    require_equal(
        fullwidth_composition["intersection_entry_count"],
        EXPECTED["safe_fullwidth_intersection_count"],
        "safe fullwidth/linebreak intersection count",
    )
    require_equal(
        fullwidth_composition["intersection_entry_ids_sha256"],
        EXPECTED["safe_fullwidth_intersection_ids_sha256"],
        "safe fullwidth/linebreak intersection coordinate hash",
    )
    if fullwidth_composition["manual_residual_intersection_count"] != 0:
        raise LinebreakError("manual residual translation repair overlaps fullwidth metadata")
    candidate, candidate_meta = apply_overlay_to_baseline(inputs["packed"]["steam_v09"], overlay)
    _composed_candidate, composed_candidate_meta = apply_composed_fullwidth_and_linebreak_to_baseline(
        inputs["packed"]["steam_v09"], overlay, fullwidth_metadata
    )
    require_equal(
        composed_candidate_meta["fullwidth_linebreak_composition"],
        fullwidth_composition,
        "fullwidth composition report",
    )
    validation = {
        "schema": VALIDATION_SCHEMA,
        "status": "PASS",
        "resource": RESOURCE,
        "runtime": overlay["runtime"],
        "source_delta": overlay["source_delta"],
        "operations": {
            "entry_count": overlay["entry_count"],
            "exact_entry_count": overlay["exact_entry_count"],
            "rebased_entry_count": overlay["rebased_entry_count"],
            "residual_translation_repair_entry_count": overlay[
                "residual_translation_repair_entry_count"
            ],
            "linebreak_tokens_replaced": EXPECTED["v23_linebreak_tokens"],
        },
        "candidate": candidate_meta,
        "fullwidth_handoff": auxiliary["handoff"],
        "fullwidth_linebreak_composition": fullwidth_composition,
        "fullwidth_composed_candidate": composed_candidate_meta,
        "deferred": {
            "entry_count": auxiliary["review"]["entry_count"],
            "entry_ids_sha256": auxiliary["review"]["entry_ids_sha256"],
        },
        "checks": {
            "switch_v22_v23_coordinate_delta_pinned": True,
            "switch_v24_text_member_equals_v23": True,
            "v09_preimage_hash_gate": True,
            "exact_v13_v22_v09_preimage_gate": True,
            "rebase_linebreak_vector_gate": True,
            "rebase_printf_esc_control_pua_gate": True,
            "linebreak_only_entries_replace_only_breaks_with_ascii_space": True,
            "residual_translation_repairs_use_manual_cjk_kana_free_korean_target": True,
            "residual_translation_repairs_retain_switch_v23_reference_hash_only": True,
            "residual_japanese_preimages_hash_only": True,
            "all_public_targets_korean_only": True,
            "generic_linebreak_stripping": False,
            "fullwidth_or_middle_dot_mutation_in_linebreak_only_entries": False,
            "fullwidth_overlap_reported_from_external_v0_9_hash_gated_model": True,
            "fullwidth_linebreak_overlap_requires_composed_candidate_api": True,
            "fullwidth_linebreak_combined_candidate_validated_in_memory": True,
            "middle_dot_fullwidth_composition_deferred_pending_font_prerequisite": True,
            "candidate_changed_domain_exact": True,
            "candidate_parse_roundtrip": True,
            "installed_game_file_written": False,
            "switch_binary_written": False,
            "release_asset_written": False,
        },
    }
    source_free(overlay, "overlay")
    source_free(auxiliary["review"], "review")
    source_free(validation, "validation")
    return overlay, auxiliary["review"], validation, candidate


def write_exact(path: Path, value: Mapping[str, Any]) -> None:
    payload = canonical_json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    require_equal(path.read_bytes(), payload, f"written artifact {path.name}")


def generate_public(
    baseline_zip: Path = DEFAULT_BASELINE_ZIP,
    switch_v13_zip: Path = DEFAULT_SWITCH_V13_ZIP,
    switch_v22_zip: Path = DEFAULT_SWITCH_V22_ZIP,
    switch_v23_zip: Path = DEFAULT_SWITCH_V23_ZIP,
    switch_v24_zip: Path = DEFAULT_SWITCH_V24_ZIP,
    fullwidth_metadata_path: Path = DEFAULT_FULLWIDTH_METADATA_PATH,
) -> dict[str, Any]:
    overlay, review, validation, _candidate = expected_artifacts(
        baseline_zip, switch_v13_zip, switch_v22_zip, switch_v23_zip, switch_v24_zip, fullwidth_metadata_path
    )
    write_exact(OVERLAY_PATH, overlay)
    write_exact(REVIEW_PATH, review)
    write_exact(VALIDATION_PATH, validation)
    return validation


def build_blob(
    baseline_zip: Path = DEFAULT_BASELINE_ZIP,
    switch_v13_zip: Path = DEFAULT_SWITCH_V13_ZIP,
    switch_v22_zip: Path = DEFAULT_SWITCH_V22_ZIP,
    switch_v23_zip: Path = DEFAULT_SWITCH_V23_ZIP,
    switch_v24_zip: Path = DEFAULT_SWITCH_V24_ZIP,
    fullwidth_metadata_path: Path = DEFAULT_FULLWIDTH_METADATA_PATH,
) -> tuple[bytes, dict[str, Any]]:
    """Return only an in-memory candidate resource and its source-free metadata."""

    _overlay, _review, validation, candidate = expected_artifacts(
        baseline_zip, switch_v13_zip, switch_v22_zip, switch_v23_zip, switch_v24_zip, fullwidth_metadata_path
    )
    return candidate, validation


def read_strict_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LinebreakError(f"cannot read JSON artifact: {path}") from exc
    if not isinstance(value, dict):
        raise LinebreakError(f"JSON artifact root is not an object: {path}")
    return value


def read_fullwidth_metadata(path: Path) -> dict[str, Any]:
    """Load the external source-free punctuation operation model by path."""

    value = read_strict_json(path)
    source_free(value, "fullwidth metadata")
    # Parsing the scoped operations also validates their coordinate shape.
    extract_fullwidth_ev_strdata_operations(value)
    return value


def verify(
    baseline_zip: Path = DEFAULT_BASELINE_ZIP,
    switch_v13_zip: Path = DEFAULT_SWITCH_V13_ZIP,
    switch_v22_zip: Path = DEFAULT_SWITCH_V22_ZIP,
    switch_v23_zip: Path = DEFAULT_SWITCH_V23_ZIP,
    switch_v24_zip: Path = DEFAULT_SWITCH_V24_ZIP,
    fullwidth_metadata_path: Path = DEFAULT_FULLWIDTH_METADATA_PATH,
) -> dict[str, Any]:
    overlay, review, validation, first = expected_artifacts(
        baseline_zip, switch_v13_zip, switch_v22_zip, switch_v23_zip, switch_v24_zip, fullwidth_metadata_path
    )
    tracked = ((OVERLAY_PATH, overlay), (REVIEW_PATH, review), (VALIDATION_PATH, validation))
    for path, expected in tracked:
        actual = read_strict_json(path)
        require_equal(actual, expected, f"tracked model {path.name}")
        require_equal(path.read_bytes(), canonical_json_bytes(actual), f"canonical tracked bytes {path.name}")
        source_free(actual, f"tracked {path.name}")
    _overlay2, _review2, validation2, second = expected_artifacts(
        baseline_zip, switch_v13_zip, switch_v22_zip, switch_v23_zip, switch_v24_zip, fullwidth_metadata_path
    )
    require_equal(second, first, "deterministic candidate A/B")
    require_equal(validation2, validation, "deterministic validation A/B")
    return validation | {"deterministic_ab_equal": True}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate-public", "verify", "build"))
    parser.add_argument("--baseline-zip", type=Path, default=DEFAULT_BASELINE_ZIP)
    parser.add_argument("--switch-v13-zip", type=Path, default=DEFAULT_SWITCH_V13_ZIP)
    parser.add_argument("--switch-v22-zip", type=Path, default=DEFAULT_SWITCH_V22_ZIP)
    parser.add_argument("--switch-v23-zip", type=Path, default=DEFAULT_SWITCH_V23_ZIP)
    parser.add_argument("--switch-v24-zip", type=Path, default=DEFAULT_SWITCH_V24_ZIP)
    parser.add_argument("--fullwidth-metadata", type=Path, default=DEFAULT_FULLWIDTH_METADATA_PATH)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "generate-public":
            result = generate_public(
                args.baseline_zip,
                args.switch_v13_zip,
                args.switch_v22_zip,
                args.switch_v23_zip,
                args.switch_v24_zip,
                args.fullwidth_metadata,
            )
        elif args.command == "verify":
            result = verify(
                args.baseline_zip,
                args.switch_v13_zip,
                args.switch_v22_zip,
                args.switch_v23_zip,
                args.switch_v24_zip,
                args.fullwidth_metadata,
            )
        else:
            _candidate, result = build_blob(
                args.baseline_zip,
                args.switch_v13_zip,
                args.switch_v22_zip,
                args.switch_v23_zip,
                args.switch_v24_zip,
                args.fullwidth_metadata,
            )
    except (OSError, ValueError, LinebreakError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"status={result['status']}")
    print(f"operations={result['operations']['entry_count']}")
    print(f"exact={result['operations']['exact_entry_count']}")
    print(f"rebased={result['operations']['rebased_entry_count']}")
    print(f"residual_translation_repairs={result['operations']['residual_translation_repair_entry_count']}")
    print(f"linebreak_tokens={result['operations']['linebreak_tokens_replaced']}")
    print("installed_game_file_written=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
