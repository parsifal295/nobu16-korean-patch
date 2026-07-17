#!/usr/bin/env python3
"""Account for every PC core-table coordinate without trusting Switch Korean.

This is a conservative *coordinate-accounting* closure for ``strdata``,
``msgdata``, and ``msgev``.  It pins pristine PC Japanese, pairs every live
PC Korean coordinate with PC EN/SC/TC context, and emits a disposition for
each coordinate.  A no-signal result is deliberately not a semantic approval:
static text pairing cannot prove that a Korean translation reads naturally in
its game context.

The only project artifact read in addition to the PC tables is the public
quality overlay's resource/coordinate list.  Its Korean replacement text is
not consulted; this merely prevents an already-covered coordinate from being
reported as a fresh finding.  No Switch or other Korean translation is read.

All text-bearing artifacts stay beneath ``tmp``.  The script never writes a
game resource, Steam installation, source table, or public overlay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP = REPO / "tmp"
TOOLS = REPO / "tools"
STRDATA_TOOLS = REPO / "workstreams" / "strdata"

sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(STRDATA_TOOLS))

from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table, rebuild_message_table  # noqa: E402
from strdata_format import coordinate_texts, parse_raw_strdata, rebuild_raw_strdata  # noqa: E402


DEFAULT_STEAM_ROOT = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
DEFAULT_ORIGINAL_ROOT = (
    DEFAULT_STEAM_ROOT
    / "KR_PATCH_BACKUP"
    / "file_only_transaction"
    / "steam-jp-1.1.7-v0.6.0"
    / "originals"
)
DEFAULT_OUTPUT = TMP / "translation_quality_pc_core_closure_v1"
PUBLIC_OVERLAY = REPO / "workstreams" / "translation_quality_corrections_v1" / "public" / "translation_quality_corrections.v1.json"

# These pristine PC v1.1.7 Japanese originals correspond to the installed
# Korean patch.  The live local ``strdata`` file is intentionally not used:
# its current hash differs from the pinned original, while the archived PC
# Japanese original below matches the source pin.  This is a Japanese source
# choice, not a Korean translation reference.
LOCAL_PC_JP: dict[str, Path] = {}
PRISTINE_PC_JP_SHA256 = {
    "MSG/JP/strdata.bin": "FF172741A7ADC0F8C9E903A4BB3F4482639CE5AB80EA44C8CC458C300940DEE0",
    "MSG_PK/JP/msgdata.bin": "13498FBFFF6D33F0BFB0915B6F365F076FE8E78046EE411BB8478235C86C2C9E",
    "MSG_PK/JP/msgev.bin": "A9D4434F589C231298D824617847574AEBE2E3302389517B322BE18E85050A84",
}

KANA_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f]")
HAN_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
HANGUL_RE = re.compile(r"[\uac00-\ud7a3\u1100-\u11ff\u3130-\u318f]")
RUNTIME_RE = re.compile(r"\[([a-z]+\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
PLACEHOLDER_DUMMY_RE = re.compile(r"^dummy\d*$", re.IGNORECASE)
LOCALIZATION_IDENTIFIER_RE = re.compile(r"^(?:[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+|[A-Z][A-Z0-9_]{5,})$")


class ClosureError(ValueError):
    """A source pin, format invariant, or coordinate contract changed."""


@dataclass(frozen=True)
class CoreSpec:
    name: str
    relative: str
    parser: str
    context_languages: tuple[str, ...]


@dataclass(frozen=True)
class ParsedTable:
    path: Path
    packed_sha256: str
    raw_sha256: str
    packed_size: int
    raw_size: int
    texts: Mapping[str, str]


SPECS = (
    CoreSpec("strdata", "MSG/JP/strdata.bin", "strdata", ("SC", "TC")),
    CoreSpec("msgdata", "MSG_PK/JP/msgdata.bin", "common", ("EN", "SC", "TC")),
    CoreSpec("msgev", "MSG_PK/JP/msgev.bin", "common", ("EN", "SC", "TC")),
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-16-le"))


def coordinate_sort_key(value: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in value.split(":"))
    except ValueError as exc:
        raise ClosureError(f"invalid coordinate: {value!r}") from exc


def language_path(relative: str, language: str) -> Path:
    parts = list(Path(relative).parts)
    try:
        index = parts.index("JP")
    except ValueError as exc:
        raise ClosureError(f"resource has no JP component: {relative}") from exc
    parts[index] = language
    return Path(*parts)


def source_path(spec: CoreSpec, original_root: Path) -> Path:
    return LOCAL_PC_JP.get(spec.relative, original_root / spec.relative)


def parse_table(path: Path, parser: str) -> ParsedTable:
    """Parse and byte-check one packed PC table without modifying it."""

    if not path.is_file():
        raise ClosureError(f"resource is absent: {path}")
    packed = path.read_bytes()
    _header, raw = decompress_wrapper(packed)
    if parser == "common":
        table = parse_message_table(raw)
        if rebuild_message_table(table, table.texts) != raw:
            raise ClosureError(f"unchanged common-table rebuild differs: {path}")
        texts = {str(index): text for index, text in enumerate(table.texts)}
    elif parser == "strdata":
        archive = parse_raw_strdata(raw)
        if rebuild_raw_strdata(archive) != raw:
            raise ClosureError(f"unchanged strdata rebuild differs: {path}")
        texts = {f"{block}:{slot}": text for (block, slot), text in coordinate_texts(archive).items()}
    else:
        raise ClosureError(f"unsupported parser: {parser}")
    return ParsedTable(
        path=path,
        packed_sha256=sha256_bytes(packed),
        raw_sha256=sha256_bytes(raw),
        packed_size=len(packed),
        raw_size=len(raw),
        texts=texts,
    )


def format_profile(text: str) -> dict[str, Any]:
    return {
        "runtime": RUNTIME_RE.findall(text),
        "printf": PRINTF_RE.findall(text),
        "escape": ESC_RE.findall(text),
        "line_break_count": len(re.findall(r"\r\n|\n|\r", text)),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
    }


def visible_text(text: str) -> str:
    return re.sub(r"\[[a-z]+\d+\]|%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]|\x1bC.", "", text)


def review_flags(jp: str, ko: str) -> list[str]:
    """Return static PC-pair review signals, never semantic proof."""

    flags: list[str] = []
    if KANA_RE.search(ko):
        flags.append("target_kana_residual")
    if HAN_RE.search(ko):
        if HANGUL_RE.search(ko):
            flags.append("target_han_mixed_with_hangul_requires_review")
        else:
            flags.append("target_han_residual")
    jp_format = format_profile(jp)
    ko_format = format_profile(ko)
    if jp_format["runtime"] != ko_format["runtime"]:
        flags.append("runtime_token_mismatch_against_pristine_jp")
    if jp_format["printf"] != ko_format["printf"]:
        flags.append("printf_token_mismatch_against_pristine_jp")
    if jp_format["escape"] != ko_format["escape"]:
        flags.append("escape_tag_mismatch_against_pristine_jp")
    if jp_format["line_break_count"] != ko_format["line_break_count"]:
        flags.append("linebreak_count_mismatch_against_pristine_jp")
    if (
        jp_format["leading_whitespace"] != ko_format["leading_whitespace"]
        or jp_format["trailing_whitespace"] != ko_format["trailing_whitespace"]
    ):
        flags.append("external_whitespace_mismatch_against_pristine_jp")
    source_visible = jp.strip()
    target_visible = ko.strip()
    if source_visible and not target_visible:
        flags.append("empty_target_for_nonempty_jp")
    if source_visible and target_visible and target_visible != source_visible:
        if PLACEHOLDER_DUMMY_RE.fullmatch(target_visible):
            flags.append("target_dummy_placeholder_for_nonempty_jp")
        if LOCALIZATION_IDENTIFIER_RE.fullmatch(target_visible):
            flags.append("target_localization_identifier_for_nonempty_jp")
    jp_visible = visible_text(jp).strip()
    ko_visible = visible_text(ko).strip()
    if len(jp_visible) >= 30 and 0 < len(ko_visible) <= 3:
        flags.append("possible_semantic_truncation")
    return flags


def reason_codes_for_flags(flags: list[str]) -> list[str]:
    categories: list[str] = []
    if any("token_mismatch" in flag or "tag_mismatch" in flag for flag in flags):
        categories.append("runtime_or_format_contract_needs_route_review")
    if "linebreak_count_mismatch_against_pristine_jp" in flags:
        categories.append("localized_layout_or_manual_break_needs_render_review")
    if "external_whitespace_mismatch_against_pristine_jp" in flags:
        categories.append("external_whitespace_or_padding_needs_ui_context")
    if any("residual" in flag for flag in flags):
        categories.append("residual_script_needs_name_or_ime_context")
    if "target_han_mixed_with_hangul_requires_review" in flags:
        categories.append("mixed_hanja_needs_style_or_name_context")
    if "empty_target_for_nonempty_jp" in flags:
        categories.append("empty_target_needs_runtime_visibility_review")
    if "target_dummy_placeholder_for_nonempty_jp" in flags or "target_localization_identifier_for_nonempty_jp" in flags:
        categories.append("placeholder_or_identifier_needs_runtime_route_review")
    if "possible_semantic_truncation" in flags:
        categories.append("possible_truncation_needs_contextual_translation_review")
    if "same_pristine_jp_has_multiple_korean_renderings" in flags:
        categories.append("same_source_divergence_needs_contextual_terminology_review")
    return categories


def classify_coordinate(flags: list[str], covered_by_overlay: bool, jp: str, ko: str) -> tuple[str, str, list[str]]:
    """Assign an honest, non-semantic-completion disposition."""

    if covered_by_overlay:
        return (
            "covered_by_existing_quality_overlay_coordinate",
            "inherited_coordinate_coverage_not_reassessed_here",
            ["existing_overlay_coordinate_excluded_from_new_candidate_detection"],
        )
    if not jp.strip() and not ko.strip():
        return (
            "empty_coordinate_no_translation_content",
            "high_for_empty_content_fact",
            ["both_pristine_jp_and_current_ko_are_empty"],
        )
    if flags:
        return (
            "pc_only_hold_requires_contextual_or_runtime_review",
            "high_for_static_hold_assignment_not_for_translation_correctness",
            reason_codes_for_flags(flags),
        )
    return (
        "pc_pair_screened_no_automatic_signal_not_semantic_approval",
        "structural_screen_only_not_semantic_approval",
        ["no_static_pc_pair_signal", "semantic_context_not_exhaustively_interpreted"],
    )


def read_overlay_coordinates() -> dict[str, set[str]]:
    """Read only existing overlay coordinate coverage, never its Korean text."""

    if not PUBLIC_OVERLAY.is_file():
        raise ClosureError(f"quality overlay is absent: {PUBLIC_OVERLAY}")
    payload = json.loads(PUBLIC_OVERLAY.read_text(encoding="utf-8"))
    policy = payload.get("distribution_policy")
    if not isinstance(policy, dict) or policy.get("switch_korean_translation_used") is not False:
        raise ClosureError("quality overlay does not assert Switch-Korean exclusion")
    resources = payload.get("resources")
    if not isinstance(resources, list):
        raise ClosureError("quality overlay resource list is invalid")
    result = {spec.name: set() for spec in SPECS}
    for resource in resources:
        if not isinstance(resource, dict):
            raise ClosureError("quality overlay resource is invalid")
        name = resource.get("name")
        if name not in result:
            continue
        entries = resource.get("entries")
        if not isinstance(entries, list):
            raise ClosureError(f"quality overlay entries are invalid: {name}")
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("coordinate"), str):
                raise ClosureError(f"quality overlay coordinate is invalid: {name}")
            coordinate = entry["coordinate"]
            coordinate_sort_key(coordinate)
            if coordinate in result[name]:
                raise ClosureError(f"duplicate quality overlay coordinate: {name}:{coordinate}")
            result[name].add(coordinate)
    return result


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def atomic_write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
                stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def output_path_is_private(output: Path) -> None:
    resolved_output = output.resolve()
    resolved_tmp = TMP.resolve()
    if resolved_output == resolved_tmp or resolved_tmp not in resolved_output.parents:
        raise ClosureError(f"output must stay beneath {resolved_tmp}")


def file_metadata(table: ParsedTable, relative_path: str) -> dict[str, Any]:
    return {
        "relative_path": relative_path.replace("\\", "/"),
        "packed_sha256": table.packed_sha256,
        "raw_sha256": table.raw_sha256,
        "packed_size": table.packed_size,
        "raw_size": table.raw_size,
        "coordinate_count": len(table.texts),
        "unchanged_parse_rebuild": "OK",
    }


def duplicate_coordinates(jp_texts: Mapping[str, str], ko_texts: Mapping[str, str]) -> set[str]:
    """Mark coordinates where one nontrivial PC Japanese source has divergent KO."""

    renderings: dict[str, set[str]] = defaultdict(set)
    locations: dict[str, list[str]] = defaultdict(list)
    for coordinate, jp in jp_texts.items():
        if len(jp.strip()) < 2:
            continue
        renderings[jp].add(ko_texts[coordinate])
        locations[jp].append(coordinate)
    result: set[str] = set()
    for jp, values in renderings.items():
        if len(values) > 1:
            result.update(locations[jp])
    return result


def audit_resources(steam_root: Path, original_root: Path) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, set[str]],
    dict[str, set[str]],
]:
    """Load all PC inputs, prove alignment, and return parsed-table state."""

    overlay_coordinates = read_overlay_coordinates()
    resources: dict[str, dict[str, Any]] = {}
    duplicate_map: dict[str, set[str]] = {}
    for spec in SPECS:
        jp_path = source_path(spec, original_root)
        jp = parse_table(jp_path, spec.parser)
        expected_jp = PRISTINE_PC_JP_SHA256[spec.relative]
        if jp.packed_sha256 != expected_jp:
            raise ClosureError(
                f"pristine PC Japanese hash differs for {spec.name}: expected {expected_jp}, got {jp.packed_sha256}"
            )
        ko_path = steam_root / spec.relative
        ko = parse_table(ko_path, spec.parser)
        if set(jp.texts) != set(ko.texts):
            raise ClosureError(f"coordinate mismatch between pristine JP and PC Korean: {spec.name}")
        contexts: dict[str, ParsedTable] = {}
        for language in spec.context_languages:
            relative = language_path(spec.relative, language)
            context = parse_table(steam_root / relative, spec.parser)
            if set(context.texts) != set(jp.texts):
                raise ClosureError(f"coordinate mismatch for PC {language} context: {spec.name}")
            contexts[language] = context
        unknown_overlay = sorted(overlay_coordinates[spec.name].difference(jp.texts), key=coordinate_sort_key)
        if unknown_overlay:
            raise ClosureError(f"quality overlay has absent coordinate(s) for {spec.name}: {unknown_overlay[:5]!r}")
        duplicate_map[spec.name] = duplicate_coordinates(jp.texts, ko.texts)
        resources[spec.name] = {"spec": spec, "jp": jp, "ko": ko, "contexts": contexts}
    return resources, overlay_coordinates, duplicate_map


def make_record(
    resource: Mapping[str, Any],
    coordinate: str,
    overlay_coordinates: set[str],
    duplicate_coordinates_for_resource: set[str],
    private: bool,
) -> dict[str, Any]:
    spec = resource["spec"]
    jp = resource["jp"].texts[coordinate]
    ko = resource["ko"].texts[coordinate]
    flags = review_flags(jp, ko)
    if coordinate in duplicate_coordinates_for_resource:
        flags.append("same_pristine_jp_has_multiple_korean_renderings")
    disposition, confidence, reasons = classify_coordinate(flags, coordinate in overlay_coordinates, jp, ko)
    context_texts = {language: table.texts[coordinate] for language, table in resource["contexts"].items()}
    base: dict[str, Any] = {
        "schema": "nobu16.kr.pc-core-coordinate-disposition.v1",
        "resource": spec.name,
        "relative_path": spec.relative,
        "coordinate": coordinate,
        "jp_utf16le_sha256": sha256_text(jp),
        "current_ko_utf16le_sha256": sha256_text(ko),
        "context_utf16le_sha256": {language: sha256_text(text) for language, text in context_texts.items()},
        "flags": flags,
        "disposition": disposition,
        "evidence_confidence": confidence,
        "hold_or_screen_reason_codes": reasons,
        "existing_quality_overlay_coordinate": coordinate in overlay_coordinates,
        "new_high_confidence_candidate": False,
        "switch_korean_translation_used": False,
    }
    if private:
        base["source_jp"] = jp
        base["current_ko"] = ko
        base["pc_reference_contexts"] = context_texts
    return base


def iter_records(
    resources: Mapping[str, Mapping[str, Any]],
    overlay_coordinates: Mapping[str, set[str]],
    duplicate_map: Mapping[str, set[str]],
    private: bool,
) -> Iterator[dict[str, Any]]:
    for spec in SPECS:
        resource = resources[spec.name]
        for coordinate in sorted(resource["jp"].texts, key=coordinate_sort_key):
            yield make_record(
                resource,
                coordinate,
                overlay_coordinates[spec.name],
                duplicate_map[spec.name],
                private,
            )


def resource_summary(
    resource: Mapping[str, Any],
    overlay_coordinates: set[str],
    duplicate_coordinates_for_resource: set[str],
) -> dict[str, Any]:
    spec: CoreSpec = resource["spec"]
    dispositions: Counter[str] = Counter()
    flag_counts: Counter[str] = Counter()
    for coordinate in sorted(resource["jp"].texts, key=coordinate_sort_key):
        row = make_record(resource, coordinate, overlay_coordinates, duplicate_coordinates_for_resource, private=False)
        dispositions[row["disposition"]] += 1
        flag_counts.update(row["flags"])
    return {
        "relative_path": spec.relative,
        "parser": spec.parser,
        "coordinate_count": len(resource["jp"].texts),
        "pristine_pc_japanese": {
            "path_class": "local_pristine_pc_japanese",
            **file_metadata(resource["jp"], spec.relative),
        },
        "current_pc_korean": file_metadata(resource["ko"], spec.relative),
        "pc_reference_contexts": {
            language: file_metadata(table, str(language_path(spec.relative, language)))
            for language, table in sorted(resource["contexts"].items())
        },
        "existing_quality_overlay_coordinate_count": len(overlay_coordinates),
        "same_pristine_jp_divergence_coordinate_count": len(duplicate_coordinates_for_resource),
        "disposition_counts": dict(sorted(dispositions.items())),
        "flag_counts": dict(sorted(flag_counts.items())),
        "new_high_confidence_candidate_count": 0,
    }


def audit(steam_root: Path, original_root: Path, output: Path, write: bool) -> dict[str, Any]:
    steam_root = steam_root.resolve()
    original_root = original_root.resolve()
    output = output.resolve()
    output_path_is_private(output)
    resources, overlay_coordinates, duplicate_map = audit_resources(steam_root, original_root)

    summaries = {
        spec.name: resource_summary(resources[spec.name], overlay_coordinates[spec.name], duplicate_map[spec.name])
        for spec in SPECS
    }
    total_coordinates = sum(summary["coordinate_count"] for summary in summaries.values())
    total_dispositions: Counter[str] = Counter()
    total_flags: Counter[str] = Counter()
    for summary in summaries.values():
        total_dispositions.update(summary["disposition_counts"])
        total_flags.update(summary["flag_counts"])

    private_ledger = output / "private_pc_paired_coordinate_dispositions.v1.jsonl"
    source_free_ledger = output / "pc_coordinate_dispositions.source_free.v1.jsonl"
    high_confidence_candidates = output / "new_high_confidence_candidates.v1.jsonl"
    summary_path = output / "summary.source_free.json"
    summary = {
        "schema": "nobu16.kr.translation-quality-pc-core-closure.v1",
        "scope": "coordinate-accounting closure for PC strdata, msgdata, and msgev; pristine PC Japanese with PC EN/SC/TC context",
        "coordinate_count": total_coordinates,
        "resources": summaries,
        "total_disposition_counts": dict(sorted(total_dispositions.items())),
        "total_flag_counts": dict(sorted(total_flags.items())),
        "new_high_confidence_candidate_count": 0,
        "new_high_confidence_candidate_policy": "No automatic semantic wording is emitted without an exact reviewed Korean replacement supported by PC-only evidence; this static closure found no such fresh replacement.",
        "translation_completion_claim": "not_made: coordinates without an automatic signal are structurally screened, not semantically approved.",
        "existing_overlay_policy": "Only existing overlay resource/coordinate coverage was read; existing Korean proposal text was not used as a translation authority.",
        "switch_korean_translation_used": False,
        "non_pc_korean_translation_sources_read": False,
        "private_text_bearing_ledger": str(private_ledger.relative_to(REPO)).replace("\\", "/"),
        "source_free_coordinate_ledger": str(source_free_ledger.relative_to(REPO)).replace("\\", "/"),
        "new_high_confidence_candidate_jsonl": str(high_confidence_candidates.relative_to(REPO)).replace("\\", "/"),
        "private_files_contain_commercial_source_text": True,
        "game_resource_candidate_generated": False,
        "steam_installation_written": False,
        "source_or_public_overlay_written": False,
        "output_written": write,
    }
    if write:
        atomic_write_jsonl(private_ledger, iter_records(resources, overlay_coordinates, duplicate_map, private=True))
        atomic_write_jsonl(source_free_ledger, iter_records(resources, overlay_coordinates, duplicate_map, private=False))
        # Deliberately an empty JSONL: a candidate artifact exists separately,
        # but no unreviewed semantic wording is silently promoted to a patch.
        atomic_write_jsonl(high_confidence_candidates, ())
        atomic_write_text(summary_path, json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steam-root", type=Path, default=DEFAULT_STEAM_ROOT)
    parser.add_argument("--original-root", type=Path, default=DEFAULT_ORIGINAL_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--write", action="store_true", help="write private ledgers under tmp; default is validation-only")
    args = parser.parse_args()
    try:
        summary = audit(args.steam_root, args.original_root, args.output, args.write)
        print(
            json.dumps(
                {
                    "coordinate_count": summary["coordinate_count"],
                    "new_high_confidence_candidate_count": summary["new_high_confidence_candidate_count"],
                    "output_written": summary["output_written"],
                    "steam_installation_written": summary["steam_installation_written"],
                    "switch_korean_translation_used": summary["switch_korean_translation_used"],
                    "total_disposition_counts": summary["total_disposition_counts"],
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0
    except (ClosureError, OSError, ValueError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
