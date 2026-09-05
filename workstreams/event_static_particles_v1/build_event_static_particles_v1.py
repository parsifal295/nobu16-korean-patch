#!/usr/bin/env python3
"""Resolve fixed-person event particles without an executable patch.

Only particles immediately following numeric person tokens (``[bN]``,
``[bmN]``, and ``[bsN]``) are in scope.  The 18 unification-ending
boundaries that use variable symbolic tokens are deliberately preserved
byte-for-byte at the text-table level.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = SCRIPT.parents[2]
TOOLS = REPO / "tools"
sys.path.insert(0, str(TOOLS))

from nobu16_lz4 import decompress_wrapper, recompress_wrapper_greedy  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402


SCHEMA = "nobu16.kr.event-static-particles.v1"
EVENT_FIRST_ID = 3202
EVENT_LAST_ID = 16402
NUMERIC_TOKEN_RE = re.compile(r"\[(b|bm|bs)(\d+)\]")
SYMBOLIC_TOKEN_RE = re.compile(r"\[(?:bu|bum|cuh)\]")
CONTROL_TAG_RE = re.compile(r"\x1bC.")

# This pin represents the ordered 609-boundary set, not the selected output.
# It prevents a future grammar change from silently broadening or narrowing
# the reviewed scope.
BOUNDARY_SIGNATURE_SHA256 = (
    "09273B53E37382A8D49B4FB4D699FCC1CBE7532818C16275A4708396C9A30608"
)
SYMBOLIC_SIGNATURE_SHA256 = (
    "D599447EDD598CDAD77BB261C3DFAA16EEA9ED31C884B22E9C212CCEDC22E0ED"
)


@dataclass(frozen=True)
class ResourcePin:
    relative: str
    size: int
    sha256: str
    boundary_count: int
    changed_boundary_count: int
    changed_row_count: int
    symbolic_boundary_count: int


RESOURCE_PINS = (
    ResourcePin(
        "MSG/JP/ev_strdata.bin",
        928_123,
        "50CA2B4068D31856291399601944D0A378EAA6D4C2C714CA1B9011B42382828C",
        316,
        61,
        61,
        14,
    ),
    ResourcePin(
        "MSG_PK/JP/msgev.bin",
        1_048_336,
        "37948BCE02E7233FFFCAF5A555A550569655B1CA6D8B8098F37C3052F9819EAB",
        293,
        80,
        79,
        4,
    ),
)


# Ordered longest-first below.  A candidate is accepted only when the next
# character is not Hangul, so ordinary words such as "이다" are not mistaken
# for the one-syllable subject particle "이".
FAMILY_FORMS: dict[str, tuple[str, ...]] = {
    "past_copula": (
        "이었(였)던가",
        "이었(였)으나",
        "이었(였)다",
        "이었(였)을",
        "이었던가",
        "였던가",
        "이었으나",
        "였으나",
        "이었다",
        "였다",
        "이었을",
        "였을",
    ),
    "optional_i_copula": (
        "이()야말로",
        "이()기는",
        "이()라는",
        "이()라",
        "이()여",
        "이()요",
        "이()고",
        "이야말로",
        "야말로",
        "이기는",
        "기는",
        "이라는",
        "라는",
        "이여",
        "여",
        "이라",
        "라",
        "이요",
        "요",
        "이고",
        "고",
    ),
    "direction": (
        "으()로서도",
        "으()로부터",
        "으()로",
        "으로서도",
        "로서도",
        "으로부터",
        "로부터",
        "으로",
        "로",
    ),
    "comitative": ("과(와)의", "과(와)", "과의", "와의", "과", "와"),
    "topic": ("은(는)", "은", "는"),
    "subject": ("이(가)", "이", "가"),
    "object": ("을(를)", "을", "를"),
}
ORDERED_FORMS = tuple(
    sorted(
        ((surface, family) for family, forms in FAMILY_FORMS.items() for surface in forms),
        key=lambda item: len(item[0]),
        reverse=True,
    )
)


class EventStaticParticleError(RuntimeError):
    """A pinned input or reviewed particle invariant changed."""


@dataclass(frozen=True)
class Boundary:
    entry_id: int
    token_ordinal: int
    token: str
    token_kind: str
    person_id: int
    family: str
    source_surface: str
    surface_start: int
    surface_end: int


def sha256_bytes(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def canonical_sha256(value: Any) -> str:
    blob = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(blob)


def file_spec(path: Path) -> dict[str, Any]:
    blob = path.read_bytes()
    return {"size": len(blob), "sha256": sha256_bytes(blob)}


def require(actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        raise EventStaticParticleError(
            f"{label} differs: expected={expected!r}, actual={actual!r}"
        )


def is_hangul_syllable(character: str) -> bool:
    return len(character) == 1 and "가" <= character <= "힣"


def skip_control_tags(text: str, position: int) -> int:
    while True:
        match = CONTROL_TAG_RE.match(text, position)
        if match is None:
            return position
        position = match.end()


def match_particle(text: str, position: int) -> tuple[str, str, int] | None:
    for surface, family in ORDERED_FORMS:
        if not text.startswith(surface, position):
            continue
        end = position + len(surface)
        if end < len(text) and is_hangul_syllable(text[end]):
            continue
        return family, surface, end
    return None


def find_numeric_boundaries(entry_id: int, text: str) -> tuple[Boundary, ...]:
    boundaries: list[Boundary] = []
    for token_ordinal, token_match in enumerate(NUMERIC_TOKEN_RE.finditer(text)):
        surface_start = skip_control_tags(text, token_match.end())
        particle = match_particle(text, surface_start)
        if particle is None:
            continue
        family, surface, surface_end = particle

        # ``[bsN]가`` is also the game's coloured "surname + 家" clan form.
        # That lexical suffix has its own colour-closing tag after 가.  A true
        # subject particle is followed by ordinary text/space/newline instead.
        if (
            token_match.group(1) == "bs"
            and surface == "가"
            and text.startswith("\x1bCZ", surface_end)
        ):
            continue

        boundaries.append(
            Boundary(
                entry_id=entry_id,
                token_ordinal=token_ordinal,
                token=token_match.group(0),
                token_kind=token_match.group(1),
                person_id=int(token_match.group(2)),
                family=family,
                source_surface=surface,
                surface_start=surface_start,
                surface_end=surface_end,
            )
        )
    return tuple(boundaries)


def find_symbolic_boundaries(entry_id: int, text: str) -> tuple[tuple[int, str, str], ...]:
    findings: list[tuple[int, str, str]] = []
    for token_match in SYMBOLIC_TOKEN_RE.finditer(text):
        position = skip_control_tags(text, token_match.end())
        particle = match_particle(text, position)
        if particle is not None:
            findings.append((entry_id, token_match.group(0), particle[1]))
    return tuple(findings)


def rendered_name(texts: Sequence[str], token_kind: str, person_id: int) -> str:
    if person_id >= len(texts):
        raise EventStaticParticleError(f"person id {person_id} is outside the event table")
    full_name = texts[person_id]
    if token_kind == "b":
        name = full_name
    else:
        if " " not in full_name:
            raise EventStaticParticleError(
                f"person id {person_id} has no surname/given-name separator: {full_name!r}"
            )
        surname, given_name = full_name.rsplit(" ", 1)
        name = given_name if token_kind == "bm" else surname
    if not name or not is_hangul_syllable(name[-1]):
        raise EventStaticParticleError(
            f"{token_kind}{person_id} does not end in a Hangul syllable: {name!r}"
        )
    return name


def jongseong_index(name: str) -> int:
    if not name or not is_hangul_syllable(name[-1]):
        raise EventStaticParticleError(f"cannot inspect final sound: {name!r}")
    return (ord(name[-1]) - 0xAC00) % 28


def allomorph_pair(family: str, surface: str) -> tuple[str, str]:
    """Return (consonant-final, vowel-final) forms."""
    if family == "topic":
        return "은", "는"
    if family == "subject":
        return "이", "가"
    if family == "object":
        return "을", "를"
    if family == "comitative":
        return ("과의", "와의") if surface.endswith("의") else ("과", "와")
    if family == "direction":
        if surface.endswith("로서도"):
            tail = "로서도"
        elif surface.endswith("로부터"):
            tail = "로부터"
        else:
            tail = "로"
        return "으" + tail, tail
    if family == "optional_i_copula":
        for tail in ("야말로", "기는", "라는", "라", "여", "요", "고"):
            if surface.endswith(tail):
                return "이" + tail, tail
    if family == "past_copula":
        for tail in ("던가", "으나", "다", "을"):
            if surface.endswith(tail):
                return "이었" + tail, "였" + tail
    raise EventStaticParticleError(f"unsupported particle form: {family} {surface!r}")


def select_surface(family: str, source_surface: str, name: str) -> str:
    consonant_form, vowel_form = allomorph_pair(family, source_surface)
    final_index = jongseong_index(name)
    if family == "direction":
        # ㄹ-final nouns take 로, like vowel-final nouns.
        return vowel_form if final_index in (0, 8) else consonant_form
    return consonant_form if final_index else vowel_form


def expand_numeric_tokens_for_layout(text: str, texts: Sequence[str]) -> str:
    def replace(match: re.Match[str]) -> str:
        return rendered_name(texts, match.group(1), int(match.group(2)))

    return CONTROL_TAG_RE.sub("", NUMERIC_TOKEN_RE.sub(replace, text))


def is_fullwidth_layout_character(character: str) -> bool:
    return (
        is_hangul_syllable(character)
        or "\u3400" <= character <= "\u9fff"
        or "\uf900" <= character <= "\ufaff"
    )


def changed_row_layout(entry_id: int, text: str, texts: Sequence[str]) -> dict[str, Any]:
    visible = expand_numeric_tokens_for_layout(text, texts)
    lines: list[dict[str, Any]] = []
    for line_index, line in enumerate(visible.split("\n")):
        fullwidth_count = sum(is_fullwidth_layout_character(character) for character in line)
        halfwidth_count = len(line) - fullwidth_count
        raw_width = fullwidth_count * 48 + halfwidth_count * 24
        effective_width = (raw_width * 30 + 47) // 48
        lines.append(
            {
                "line_index": line_index,
                "visible_string": line,
                "raw_g1n_width_px": raw_width,
                "effective_width_px": effective_width,
                "fullwidth_character_count": fullwidth_count,
                "halfwidth_character_count": halfwidth_count,
                "exceeds_912px": effective_width > 912,
            }
        )
    return {
        "id": entry_id,
        "line_count": len(lines),
        "exceeds_four_lines": len(lines) > 4,
        "lines": lines,
    }


def process_texts(
    relative: str, texts: Sequence[str]
) -> tuple[tuple[str, ...], list[dict[str, Any]], list[list[Any]]]:
    if len(texts) <= EVENT_LAST_ID:
        raise EventStaticParticleError(
            f"{relative} has only {len(texts)} entries; event id {EVENT_LAST_ID} is absent"
        )

    output = list(texts)
    audit: list[dict[str, Any]] = []
    signature: list[list[Any]] = []
    for entry_id in range(EVENT_FIRST_ID, EVENT_LAST_ID + 1):
        source_text = texts[entry_id]
        boundaries = find_numeric_boundaries(entry_id, source_text)
        replacements: list[tuple[int, int, str]] = []
        for boundary in boundaries:
            name = rendered_name(texts, boundary.token_kind, boundary.person_id)
            target_surface = select_surface(
                boundary.family, boundary.source_surface, name
            )
            replacements.append(
                (boundary.surface_start, boundary.surface_end, target_surface)
            )
            signature.append(
                [
                    relative,
                    boundary.entry_id,
                    boundary.token_ordinal,
                    boundary.token,
                    boundary.family,
                    boundary.source_surface,
                ]
            )
            audit.append(
                {
                    "id": boundary.entry_id,
                    "token_ordinal": boundary.token_ordinal,
                    "token": boundary.token,
                    "rendered_name": name,
                    "family": boundary.family,
                    "source_surface": boundary.source_surface,
                    "target_surface": target_surface,
                    "changed": boundary.source_surface != target_surface,
                }
            )

        target_text = source_text
        for start, end, replacement in reversed(replacements):
            target_text = target_text[:start] + replacement + target_text[end:]
        output[entry_id] = target_text

    return tuple(output), audit, signature


def symbolic_signature(relative: str, texts: Sequence[str]) -> list[list[Any]]:
    result: list[list[Any]] = []
    for entry_id in range(EVENT_FIRST_ID, EVENT_LAST_ID + 1):
        for _, token, surface in find_symbolic_boundaries(entry_id, texts[entry_id]):
            result.append([relative, entry_id, token, surface])
    return result


def ensure_output_is_safe(input_root: Path, output_root: Path) -> None:
    input_resolved = input_root.resolve(strict=True)
    output_resolved = output_root.resolve(strict=False)
    if input_resolved == output_resolved:
        raise EventStaticParticleError("output root cannot equal the pinned input root")
    folded = str(output_resolved).replace("/", "\\").casefold()
    if "\\steamapps\\common\\nobu16" in folded:
        raise EventStaticParticleError("this builder never writes directly to a Steam install")


def build(input_root: Path, output_root: Path, audit_path: Path) -> dict[str, Any]:
    ensure_output_is_safe(input_root, output_root)
    resources: list[dict[str, Any]] = []
    complete_signature: list[list[Any]] = []
    complete_symbolic_signature: list[list[Any]] = []

    for pin in RESOURCE_PINS:
        source = input_root / Path(pin.relative)
        if not source.is_file():
            raise EventStaticParticleError(f"pinned input is absent: {source}")
        packed = source.read_bytes()
        require(len(packed), pin.size, f"{pin.relative} input size")
        require(sha256_bytes(packed), pin.sha256, f"{pin.relative} input SHA-256")

        wrapper, raw = decompress_wrapper(packed)
        table = parse_message_table(raw)
        target_texts, findings, signature = process_texts(pin.relative, table.texts)
        symbolic_before = symbolic_signature(pin.relative, table.texts)

        require(len(findings), pin.boundary_count, f"{pin.relative} boundary count")
        changed = [finding for finding in findings if finding["changed"]]
        changed_ids = sorted({int(finding["id"]) for finding in changed})
        require(
            len(changed),
            pin.changed_boundary_count,
            f"{pin.relative} changed boundary count",
        )
        require(
            len(changed_ids), pin.changed_row_count, f"{pin.relative} changed row count"
        )
        require(
            len(symbolic_before),
            pin.symbolic_boundary_count,
            f"{pin.relative} symbolic boundary count",
        )

        # Numeric-only replacements guarantee every other row, including the
        # 18 variable ending rows and printf templates, remains identical.
        changed_id_set = set(changed_ids)
        for entry_id, (before, after) in enumerate(zip(table.texts, target_texts)):
            if entry_id not in changed_id_set:
                require(after, before, f"{pin.relative} untouched row {entry_id}")
        require(
            symbolic_signature(pin.relative, target_texts),
            symbolic_before,
            f"{pin.relative} symbolic endings",
        )

        layouts = [
            changed_row_layout(entry_id, target_texts[entry_id], target_texts)
            for entry_id in changed_ids
        ]
        if pin.relative == "MSG_PK/JP/msgev.bin":
            over_width = [
                (row["id"], line["line_index"], line["effective_width_px"])
                for row in layouts
                for line in row["lines"]
                if line["exceeds_912px"]
            ]
            over_lines = [row["id"] for row in layouts if row["exceeds_four_lines"]]
            require(over_width, [], f"{pin.relative} 912px layout gate")
            require(over_lines, [], f"{pin.relative} four-line layout gate")

        target_raw = rebuild_message_table(table, target_texts)
        reparsed = parse_message_table(target_raw)
        require(reparsed.texts, target_texts, f"{pin.relative} rebuilt text round trip")
        target_packed = recompress_wrapper_greedy(target_raw, wrapper)
        _, verify_raw = decompress_wrapper(target_packed)
        require(verify_raw, target_raw, f"{pin.relative} packed round trip")

        target = output_root / Path(pin.relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(target_packed)

        family_counts = collections.Counter(finding["family"] for finding in findings)
        resources.append(
            {
                "relative_path": pin.relative,
                "input": {"size": len(packed), "sha256": sha256_bytes(packed)},
                "input_raw": {"size": len(raw), "sha256": sha256_bytes(raw)},
                "output": {
                    "size": len(target_packed),
                    "sha256": sha256_bytes(target_packed),
                },
                "output_raw": {
                    "size": len(target_raw),
                    "sha256": sha256_bytes(target_raw),
                },
                "numeric_boundary_count": len(findings),
                "changed_boundary_count": len(changed),
                "already_correct_boundary_count": len(findings) - len(changed),
                "changed_row_count": len(changed_ids),
                "changed_ids": changed_ids,
                "family_counts": dict(sorted(family_counts.items())),
                "symbolic_boundary_count": len(symbolic_before),
                "symbolic_boundary_policy": "preserved_exactly",
                "layout_audit": {
                    "measurement": "raw_g1n_48_24_scaled_to_30px",
                    "threshold_px": 912,
                    "maximum_lines": 4,
                    "gate": (
                        "authoritative_static_patch_007"
                        if pin.relative == "MSG_PK/JP/msgev.bin"
                        else "informational_only_base_widget_not_established"
                    ),
                    "changed_rows": layouts,
                },
                "findings": findings,
            }
        )
        complete_signature.extend(signature)
        complete_symbolic_signature.extend(symbolic_before)

    require(len(complete_signature), 609, "total numeric boundary count")
    require(
        canonical_sha256(complete_signature),
        BOUNDARY_SIGNATURE_SHA256,
        "numeric boundary signature",
    )
    require(len(complete_symbolic_signature), 18, "total symbolic boundary count")
    require(
        canonical_sha256(complete_symbolic_signature),
        SYMBOLIC_SIGNATURE_SHA256,
        "symbolic boundary signature",
    )

    report = {
        "schema": SCHEMA,
        "event_id_range_inclusive": [EVENT_FIRST_ID, EVENT_LAST_ID],
        "scope": "numeric_fixed_person_tokens_only",
        "executable_patch_required": False,
        "numeric_boundary_signature_sha256": BOUNDARY_SIGNATURE_SHA256,
        "symbolic_boundary_signature_sha256": SYMBOLIC_SIGNATURE_SHA256,
        "total_numeric_boundary_count": sum(
            resource["numeric_boundary_count"] for resource in resources
        ),
        "total_changed_boundary_count": sum(
            resource["changed_boundary_count"] for resource in resources
        ),
        "total_already_correct_boundary_count": sum(
            resource["already_correct_boundary_count"] for resource in resources
        ),
        "total_symbolic_boundary_count": sum(
            resource["symbolic_boundary_count"] for resource in resources
        ),
        "symbolic_boundary_policy": "preserve_original_18_without_rewording",
        "resources": resources,
    }
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--input-root", type=Path, required=True)
    value.add_argument("--output-root", type=Path, required=True)
    value.add_argument("--audit", type=Path)
    return value


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(argv)
    audit = args.audit or (args.output_root / "event_static_particles.v1.json")
    try:
        report = build(args.input_root, args.output_root, audit)
    except (OSError, ValueError, EventStaticParticleError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"output_root={args.output_root}")
    print(f"audit={audit}")
    print(f"numeric_boundaries={report['total_numeric_boundary_count']}")
    print(f"changed_boundaries={report['total_changed_boundary_count']}")
    print(f"already_correct={report['total_already_correct_boundary_count']}")
    print(f"symbolic_preserved={report['total_symbolic_boundary_count']}")
    print("executable_patch_required=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
