#!/usr/bin/env python3
"""Regenerate the concise Steam-JP v1.1.7 progress block in ``README.md``."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
PROGRESS = ROOT / "data" / "public" / "steam_jp_117_progress.v1.json"
CANDIDATE_PROGRESS = ROOT / "data" / "public" / "steam_jp_117_candidate_v10_progress.v1.json"
START = "<!-- translation-progress:start -->"
END = "<!-- translation-progress:end -->"
CANDIDATE_START = "<!-- active-text-audit:start -->"
CANDIDATE_END = "<!-- active-text-audit:end -->"
SHA256_RE = re.compile(r"[0-9A-F]{64}\Z")
EXPECTED_RUNTIME = {
    "distribution": "Steam",
    "pk_version": "1.1.7",
    "steam_build_id": 18823764,
    "language_route": "JP",
    "launcher_language": "Japanese",
}


def load_progress() -> dict:
    payload = json.loads(PROGRESS.read_text(encoding="utf-8"))
    if payload.get("schema") != "nobu16.kr.steam-jp-1.1.7-progress.v1":
        raise ValueError("unsupported Steam JP progress schema")
    if payload.get("release") != "v0.9.0":
        raise ValueError("progress catalog is not the v0.9.0 release")
    if payload.get("runtime") != EXPECTED_RUNTIME:
        raise ValueError("unexpected Steam JP runtime contract")
    if not isinstance(payload.get("translation"), dict):
        raise ValueError("progress payload has no translation object")
    qa = payload.get("runtime_qa")
    if not isinstance(qa, dict):
        raise ValueError("progress payload has no runtime QA object")
    expected_qa = {
        "candidate_verification": "PASS",
        "candidate_file_count": 14,
        "steam_install_applied": True,
        "steam_apply_transaction": "PASS",
        "steam_apply_backup_entries": 14,
        "screen_qa": "PASS",
        "manual_korean_screen_output": "PASS",
        "release_published": True,
        "file_only": True,
        "memory_patch": False,
        "dll_injection": False,
        "hooking": False,
        "executable_modified": False,
        "registry_modified": False,
    }
    if any(qa.get(key) != value for key, value in expected_qa.items()):
        raise ValueError("release QA state differs from the final v0.9.0 contract")
    if not isinstance(qa.get("candidate_zip_sha256"), str) or not SHA256_RE.fullmatch(
        qa["candidate_zip_sha256"]
    ):
        raise ValueError("candidate ZIP SHA-256 is invalid")
    return payload


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_evidence(entry: object, *, path: str, schema: str, label: str) -> dict:
    """Load a hash-pinned JSON evidence file referenced by the candidate ledger."""

    if not isinstance(entry, dict) or entry.get("path") != path or entry.get("schema") != schema:
        raise ValueError(f"{label} reference differs")
    digest = entry.get("sha256")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise ValueError(f"{label} SHA-256 is invalid")
    evidence_path = ROOT / path
    if not evidence_path.is_file() or sha256_file(evidence_path) != digest:
        raise ValueError(f"{label} hash differs")
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if evidence.get("schema") != schema:
        raise ValueError(f"{label} schema differs")
    return evidence


def load_candidate_progress() -> dict:
    """Load the applied-but-unreleased v0.10 candidate from pinned evidence."""

    payload = json.loads(CANDIDATE_PROGRESS.read_text(encoding="utf-8"))
    if payload.get("schema") != "nobu16.kr.steam-jp-1.1.7-candidate-progress.v1":
        raise ValueError("unsupported Steam JP candidate progress schema")
    if payload.get("candidate_release") != "v0.10.0":
        raise ValueError("candidate progress is not v0.10.0")
    if payload.get("status") != "steam_applied_release_pending":
        raise ValueError("candidate status differs")
    if payload.get("baseline_release") != "v0.9.0":
        raise ValueError("candidate baseline release differs")
    if payload.get("runtime") != EXPECTED_RUNTIME:
        raise ValueError("unexpected Steam JP candidate runtime contract")

    verified = load_evidence(
        payload.get("translation_evidence"),
        path="workstreams/steam_jp_117_candidate_v7/verification.v7.json",
        schema="nobu16.kr.steam-jp-1.1.7-candidate-verification.v7",
        label="candidate text audit",
    )
    audited = load_evidence(
        payload.get("source_audit"),
        path="workstreams/jp_active_message_residual_audit_v1/validation.active_steam.v1.json",
        schema="nobu16.kr.jp-active-message-residual-audit.v1",
        label="source residual audit",
    )
    expected_verified_runtime = {
        key: EXPECTED_RUNTIME[key]
        for key in ("distribution", "pk_version", "steam_build_id", "language_route")
    }
    if verified.get("runtime") != expected_verified_runtime:
        raise ValueError("candidate text audit runtime differs")

    translation = payload.get("translation")
    expected_translation = {
        "active_text_tables": 10,
        "high_confidence_scope": 2498,
        "korean_applied": 2489,
        "official_credit_preserved": 6,
        "runtime_structure_preserved": 3,
        "manual_translation_hold": 0,
        "candidate_high_confidence_remaining": 9,
        "strdata_supersede_included_in_p0": 1,
        "mixed_hangul_kana_manual_review": 207,
        "hanja_only_manual_review": 187,
    }
    if translation != expected_translation:
        raise ValueError("candidate translation accounting differs")
    closure = verified.get("translation", {}).get("readme_residual_closure")
    expected_closure = {
        "translated_entry_count": translation["korean_applied"],
        "deferred_credit_entry_count": translation["official_credit_preserved"],
        "runtime_preservation_entry_count": translation["runtime_structure_preserved"],
        "manual_layout_hold_count": translation["manual_translation_hold"],
        "high_confidence_scope_count": translation["high_confidence_scope"],
        "strdata_supersede_count_included_in_p0": translation[
            "strdata_supersede_included_in_p0"
        ],
    }
    if closure != expected_closure:
        raise ValueError("candidate text audit residual closure differs")
    audit_summary = verified.get("provenance", {}).get("final_text_residual_audit", {}).get("summary")
    expected_audit_summary = {
        "active_text_table_count": translation["active_text_tables"],
        "source_high_confidence_count": translation["high_confidence_scope"],
        "translated_high_confidence_count": translation["korean_applied"],
        "preserved_high_confidence_count": translation["official_credit_preserved"]
        + translation["runtime_structure_preserved"],
        "candidate_high_confidence_count": translation["candidate_high_confidence_remaining"],
    }
    if audit_summary != expected_audit_summary:
        raise ValueError("candidate text audit ten-table accounting differs")
    remaining_summary = audited.get("remaining_summary")
    if not isinstance(remaining_summary, dict) or any(
        remaining_summary.get(key) != translation[value]
        for key, value in (
            ("high_confidence_japanese_kana_no_hangul", "high_confidence_scope"),
            ("mixed_hangul_kana_review", "mixed_hangul_kana_manual_review"),
            ("hanja_only_no_hangul_review", "hanja_only_manual_review"),
        )
    ):
        raise ValueError("source residual audit accounting differs")

    final = payload.get("final_composition")
    if not isinstance(final, dict):
        raise ValueError("candidate final composition is missing")
    rollback = load_evidence(
        final.get("original_font_rollback"),
        path="workstreams/steam_jp_117_v010_current_state_composite_rebase_v1/steam_original_font_rollback_transaction.v1.json",
        schema="nobu16.pk-file-only-transaction.v1",
        label="original-font rollback",
    )
    linebreak = load_evidence(
        final.get("event_linebreak_rebase"),
        path="workstreams/steam_jp_ev_strdata_manual_linebreak_rebase_v1/verification.v1.json",
        schema="nobu16.kr.steam-jp-ev-strdata-manual-linebreak-current-rebase-verification.v1",
        label="event linebreak rebase",
    )
    event_transaction = load_evidence(
        final.get("event_apply_transaction"),
        path="workstreams/steam_jp_ev_strdata_manual_linebreak_rebase_v1/steam_transaction.v1.json",
        schema="nobu16.pk-file-only-transaction.v1",
        label="event linebreak transaction",
    )
    expected_font_targets = {
        "RES_JP/res_lang.bin": "2F8048EC34B8B86CED54C0DC9A0879522D2717953805A4E4CC5EFF05407A4A45",
        "RES_JP_PK/res_lang_pk.bin": "EC758BC9B87F98B42E01CA6F841D963811BB944D113E2C65A1E9F5AE19F1DF08",
        "RES_JP_PK_PORT/res_lang_pk_port1.bin": "00E9C1063ED164402AA70CB770100D8AE11A92B8024F20A4F1D89F2EA1A467F7",
        "RES_JP_PK_PORT/res_lang_pk_port2.bin": "F18D99C4802AAB78C60C372FF0106ABD61ABDD8C026DC53CAE8FDE47C992C205",
    }
    if final.get("font_widths") != {
        "policy": "original_widths_retained",
        "resource_count": 4,
        "targets": expected_font_targets,
    }:
        raise ValueError("original-font rollback accounting differs")
    rollback_entries = {entry.get("path"): entry for entry in rollback.get("entries", [])}
    replaced_fonts = {
        path: entry
        for path, entry in rollback_entries.items()
        if isinstance(entry, dict) and entry.get("mode") == "replace"
    }
    if set(replaced_fonts) != set(expected_font_targets) or any(
        entry.get("target", {}).get("sha256") != expected_font_targets[path]
        for path, entry in replaced_fonts.items()
    ):
        raise ValueError("original-font rollback targets differ")

    linebreak_reference = final["event_linebreak_rebase"]
    operation = linebreak.get("operation", {})
    coordinates = operation.get("coordinates", [])
    if (
        linebreak_reference.get("coordinate_count") != 4
        or linebreak_reference.get("hard_break_token_count") != 6
        or [coordinate.get("id") for coordinate in coordinates] != [3917, 7260, 8818, 8904]
        or operation.get("hard_break_token_count") != 6
        or linebreak.get("scope", {}).get("font_resources_touched") is not False
        or linebreak.get("scope", {}).get("other_resources_touched") is not False
    ):
        raise ValueError("event linebreak rebase scope differs")
    event_target = linebreak.get("candidate", {}).get("packed", {}).get("sha256")
    transaction_entries = event_transaction.get("entries", [])
    replacements = [entry for entry in transaction_entries if entry.get("mode") == "replace"]
    if (
        len(transaction_entries) != 14
        or len(replacements) != 1
        or replacements[0].get("path") != "MSG/JP/ev_strdata.bin"
        or replacements[0].get("target", {}).get("sha256") != event_target
    ):
        raise ValueError("event linebreak transaction scope differs")
    if final.get("release_scope") != {
        "res_jp_non_font_payloads_from_current_state": True,
        "github_publication_confirmation": "pending",
    }:
        raise ValueError("candidate release scope differs")

    candidate = payload.get("candidate")
    expected_candidate = {
        "file_count": 14,
        "zip_name": "NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.10.0.zip",
        "zip_sha256": "B18A5B2B4AE40BBD80BB8613BE3E6CD81DF7EDD3B7E7434A9446AFD576E2C117",
        "zip_size": 356864822,
    }
    if candidate != expected_candidate:
        raise ValueError("candidate ZIP catalog differs")
    qa = payload.get("candidate_qa")
    expected_qa = {
        "translation_candidate_verification": "PASS",
        "event_linebreak_rebase": "PASS",
        "zip_rebuild": "PASS",
        "steam_install_applied": True,
        "screen_qa": "NOT_RERUN_AFTER_FONT_ROLLBACK_AND_EVENT_REBASE",
        "release_published": False,
        "file_only": True,
        "memory_patch": False,
        "dll_injection": False,
        "hooking": False,
        "executable_modified": False,
        "registry_modified": False,
    }
    if qa != expected_qa:
        raise ValueError("candidate QA state differs")
    return payload


def percent(done: int, total: int) -> float:
    if not isinstance(done, int) or not isinstance(total, int) or done < 0 or total <= 0 or done > total:
        raise ValueError(f"invalid progress fraction: {done}/{total}")
    return done * 100.0 / total


def render() -> str:
    payload = load_progress()
    translation = payload["translation"]
    msgui = translation["msgui"]
    common = translation["common_messages"]
    pk_msggame = translation["pk_msggame"]
    base_msggame = translation["base_msggame"]
    base_ev = translation["base_ev_strdata"]
    strdata = translation["strdata"]
    fonts = translation["fonts"]

    if msgui["safely_mapped"] != msgui["effective_changes"] + msgui["source_equal_noops"]:
        raise ValueError("msgui safe-map accounting mismatch")
    if msgui["catalog_entries"] != msgui["safely_mapped"] + msgui["withheld"]:
        raise ValueError("msgui catalog accounting mismatch")
    if pk_msggame["semantic_targets"] != pk_msggame["applied"] + pk_msggame["remaining"]:
        raise ValueError("PK msggame accounting mismatch")
    if strdata["safe_targets"] != strdata["applied"] + strdata["withheld"]:
        raise ValueError("strdata accounting mismatch")
    if fonts != {"containers": 4, "verified": 4}:
        raise ValueError("four-route font verification is incomplete")
    if (
        common["applied"]
        + common["source_equal_structural_noops"]
        + common["format_contract_blocked"]
        + common["alignment_gap"]
        != common["source_union_effective_coordinates"]
    ):
        raise ValueError("common-message accounting mismatch")
    if common["review_backlog"] != common["format_contract_blocked"] + common["alignment_gap"]:
        raise ValueError("common-message backlog accounting mismatch")
    for name, row in (("base_msggame", base_msggame), ("base_ev_strdata", base_ev)):
        if row["strict_switch_v13_transfer"] + row["residual"] != (
            row["source_script_literals"]
            if name == "base_msggame"
            else row["switch_hangul_candidates"]
        ):
            raise ValueError(f"{name} transfer accounting mismatch")

    qa = payload["runtime_qa"]
    lines = [
        START,
        "| 영역 | 안전 이식/검증 현황 | 별도 검토 |",
        "|---|---:|---:|",
        (
            f"| PK UI `msgui.bin` | {msgui['safely_mapped']:,} / {msgui['catalog_entries']:,} "
            f"({percent(msgui['safely_mapped'], msgui['catalog_entries']):.2f}%) | {msgui['withheld']:,} |"
        ),
        (
            f"| PK 공용 메시지 5종 | 한국어 변경 {common['applied']:,} · 구조 확인 "
            f"{common['source_equal_structural_noops']:,} / 원천 합집합 "
            f"{common['source_union_effective_coordinates']:,} | {common['review_backlog']:,} |"
        ),
        (
            f"| PK 본문 `MSG_PK/JP/msggame.bin` | {pk_msggame['applied']:,} / "
            f"{pk_msggame['semantic_targets']:,} ({percent(pk_msggame['applied'], pk_msggame['semantic_targets']):.1f}%) | "
            f"{pk_msggame['remaining']:,} |"
        ),
        (
            f"| 기본 지도·튜토리얼 `MSG/JP/msggame.bin` | "
            f"{base_msggame['strict_switch_v13_transfer']:,} / {base_msggame['source_script_literals']:,} | "
            f"{base_msggame['residual']:,} |"
        ),
        (
            f"| 기본 이벤트 `MSG/JP/ev_strdata.bin` | "
            f"{base_ev['strict_switch_v13_transfer']:,} / {base_ev['switch_hangul_candidates']:,} | "
            f"{base_ev['residual']:,} |"
        ),
        (
            f"| 공용 `MSG/JP/strdata.bin` | {strdata['applied']:,} / "
            f"{strdata['safe_targets']:,} | {strdata['withheld']:,} |"
        ),
        f"| 일본어 경로 한글 폰트 | {fonts['verified']} / {fonts['containers']} | 0 |",
        "",
        (
            "v0.9.0 정식 배포본은 기존 PK 12파일에 기본판 대사 파일 2개를 더한 정확히 14파일입니다. "
            "이번 버전은 지도·튜토리얼 잔여 대사 270건과 기본 이벤트 잔여 대사 40건을 추가로 반영합니다."
        ),
        (
            f"후보 ZIP SHA-256: `{qa['candidate_zip_sha256']}`. Steam 실적용과 "
            f"{qa['steam_apply_backup_entries']}개 복원 백업, 실제 한글 화면 검증을 모두 완료했습니다."
        ),
        (
            "표의 수치는 원문 해시·줄바꿈·제어문자 계약을 통과한 안전 이식 수입니다. "
            "전체 번역 완료율을 뜻하지 않습니다."
        ),
        END,
    ]
    return "\n".join(lines)


def render_candidate() -> str:
    """Render the separately labelled v0.10 Steam candidate without overstating QA."""

    payload = load_candidate_progress()
    translation = payload["translation"]
    final = payload["final_composition"]
    linebreak = final["event_linebreak_rebase"]
    font_widths = final["font_widths"]
    candidate = payload["candidate"]
    qa = payload["candidate_qa"]
    lines = [
        CANDIDATE_START,
        "### v0.10.0 Steam 적용 후보 — GitHub 릴리스 대기",
        "",
        "v0.9.0 공개본을 기준으로 활성 Steam JP 텍스트 10개 테이블을 다시 감사한 결과입니다.",
        "아래는 고신뢰 ‘가나가 남고 한글이 없는’ 좌표만의 폐쇄 검증이며, 게임 전체 번역 완료율이 아닙니다.",
        "",
        "| 후보 감사 결과 | 좌표 수 | 처리 |",
        "|---|---:|---|",
        f"| 한국어 적용 | {translation['korean_applied']:,} | 원문·형식 계약과 재파싱 검증 통과 |",
        f"| 공식 크레딧 보존 | {translation['official_credit_preserved']:,} | 의도적으로 원문 유지 |",
        f"| 런타임 구조 보존 | {translation['runtime_structure_preserved']:,} | 동적 구조라 번역 대상에서 제외 |",
        f"| 합계 | {translation['high_confidence_scope']:,} | 후보 잔존 고신뢰 가나 {translation['candidate_high_confidence_remaining']:,}개 = 위 보존 {translation['official_credit_preserved'] + translation['runtime_structure_preserved']:,}개 |",
        "",
        (
            f"`strdata.bin`의 공백 보정 {translation['strdata_supersede_included_in_p0']}건은 기존 P0 {1_400:,}건 안에 포함되어 중복 집계하지 않았습니다. "
            f"혼합 한글/가나 {translation['mixed_hangul_kana_manual_review']:,}건과 한자 전용 "
            f"{translation['hanja_only_manual_review']:,}건은 자동 완료율에 넣지 않고 별도 수동 검토 대상으로 유지합니다."
        ),
        (
            f"후보는 JP 경로 정확히 {candidate['file_count']}파일입니다. 글꼴 폭 조정은 포함하지 않고, "
            f"원래 글꼴 리소스 {font_widths['resource_count']}파일을 유지했습니다."
        ),
        (
            f"기본 이벤트 `ev_strdata.bin`은 수동 강제 줄바꿈을 {linebreak['coordinate_count']}개 좌표에서 "
            f"{linebreak['hard_break_token_count']}개만 공백으로 리베이스해 자동 줄바꿈을 쓰도록 했습니다."
        ),
        f"후보 ZIP SHA-256: `{candidate['zip_sha256']}` ({candidate['zip_size']:,} bytes).",
        (
            "Steam 설치본에는 적용했지만, 글꼴 복원·이벤트 리베이스 뒤 해당 이벤트 화면 QA는 다시 하지 않았고 "
            "GitHub 릴리스도 아직 올리지 않았습니다. "
            f"상태는 설치={qa['steam_install_applied']}, 화면 QA={qa['screen_qa']}, 배포={qa['release_published']}입니다."
        ),
        "이 ZIP은 현재 `RES_JP`의 비글꼴 payload도 보존하므로, GitHub 공개 범위 확인이 남아 있습니다.",
        CANDIDATE_END,
    ]
    return "\n".join(lines)


def replace_block(readme: str, block: str, start_marker: str = START, end_marker: str = END) -> str:
    start = readme.find(start_marker)
    end = readme.find(end_marker)
    if start < 0 or end < 0 or end < start:
        raise ValueError("README progress markers are missing or out of order")
    end += len(end_marker)
    return readme[:start] + block + readme[end:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if README is stale")
    args = parser.parse_args()
    current = README.read_text(encoding="utf-8")
    expected = replace_block(current, render())
    expected = replace_block(expected, render_candidate(), CANDIDATE_START, CANDIDATE_END)
    if args.check:
        if current != expected:
            print("README Steam JP progress is stale; run tools/update_readme_progress.py")
            return 1
        print("README Steam JP progress is current")
        return 0
    if current != expected:
        README.write_text(expected, encoding="utf-8", newline="\n")
        print("updated README Steam JP progress")
    else:
        print("README Steam JP progress already current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
