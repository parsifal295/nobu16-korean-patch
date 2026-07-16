#!/usr/bin/env python3
"""P0-04 configuration and source-safe Korean cleanup for Steam JP strdata.

The workstream owns the fourth, non-overlapping 350-coordinate P0 contract.
It uses the already audited pinned binary engine, while correcting only
verified Switch-reference remnants: Japanese bullets/long marks, six Hanja
parentheticals, and one missing trailing space.  No official source string is
serialized into the public overlay.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any, Iterable


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPOSITORY = SCRIPT.parents[2]
ENGINE_PATH = (
    REPOSITORY
    / "workstreams"
    / "steam_jp_strdata_p0_b01_v1"
    / "build_steam_jp_strdata_p0_b01_v1.py"
)
SPEC = importlib.util.spec_from_file_location("steam_jp_strdata_p0_engine", ENGINE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load shared pinned strdata engine: {ENGINE_PATH}")
engine = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = engine
SPEC.loader.exec_module(engine)


WORKSTREAM_ID = "steam-jp-strdata-p0-b04-350-v1"
BUNDLE_ID = "p0-MSG_JP_strdata-04"
OVERLAY_NAME = "strdata_ko_steam_jp_p0_b04_350.v1.json"
EXPECTED_COORDINATE_COUNT = 350
EXPECTED_COORDINATE_SHA256 = "E676D17E1541F9F6B94887F8C1EF4502F54B3BCE2A0A4F2254FB1491FBD4C510"
DEFAULT_OVERLAY = WORKSTREAM / "public" / OVERLAY_NAME
SAFE_TMP_ROOT = REPOSITORY / "tmp" / "steam_jp_strdata_p0_b04_v1"
REAL_HANGUL = re.compile(r"[\uac00-\ud7a3]")

BULLET_REPAIRS = frozenset((0, slot_id) for slot_id in range(23584, 23591))
ALLOWED_NON_HANGUL = frozenset({(1, 876), (1, 1608)})
SAFE_KO_OVERRIDES = {
    # A visual separator and its single Korean middle-dot counterpart.
    (1, 876): "─────",
    (1, 1608): "·",
    # Hanja parentheticals in otherwise Korean biographies are converted to
    # Korean wording.  Formatting controls/line breaks are absent here and
    # are still compared to the active JP source below.
    (2, 805): "난부 가신. 노부자네의 장남. 구노헤성주. 우쿄라 칭했다. 구노헤가는 난부가의 서류로, 난부 유키쓰라(난부가의 시조 미쓰유키의 여섯째 아들)를 시조로 한다고 한다. 하치노헤 노부나가의 딸을 아내로 맞았다.",
    (2, 944): "도쿠가와 가신. 도쿠가와 사천왕의 한 사람. \"무\"의 깃발을 내걸고 전장을 질주하며 각지에서 발군의 공을 세웠다. 만년에 \"노신이 권세를 다투는 것은 망국의 조짐\"이라며 로주 취임을 사퇴했다.",
    (2, 1104): "다테 가신. 데루무네·마사무네 2대를 섬겨 각지의 합전에서 공을 세웠다. 스리아게하라 합전에서는 다테 시게자네와 함께 다테 군의 주력을 이루었다. 투구에 금색 \"야\" 자의 큰 장식물을 사용했다.",
    (2, 1238): "미마사카의 호족. 이치노세성주. 우키타 나오이에의 미마사카 침공군에 패하여 그 신하가 되었다. 전장에서 맞붙어 싸우는 기술을 기본으로 한 일본에서 가장 오래된 유술 유파, 다케우치류 유술을 창시했다.",
    (3, 60): "나오에 가네쓰구가 쓰던 투구. 앞장식의 애 자는 우에스기 겐신이 후도묘오 앞장식 투구를 애용한 것을 본떠 아이젠묘오 혹은 아타고곤겐에서 딴 것이라 하나 진상은 알 수 없다.",
    (3, 92): "고대 중국의 병법서. 무경칠서의 하나. 정치와 전술, 용병, 전략에 관한 선인의 지혜를 6권으로 정리한 것이다. 도란 병법서를 넣는 가죽 주머니를 뜻한다.",
    # The active source intentionally ends in one ordinary space.
    (2, 1950): "아마고 가신. 주가가 모리 가문 공격에 패하자 오우치 가문으로 돌아섰다. 그러나 오우치 가문이 아마고 가문 공격에 실패하자 다시 아마고 가문에 귀속했으나, 그 후 또 모리 가문에 항복했다. ",
}


def configure_engine() -> None:
    engine.WORKSTREAM = WORKSTREAM
    engine.WORKSTREAM_ID = WORKSTREAM_ID
    engine.BUNDLE_ID = BUNDLE_ID
    engine.OVERLAY_NAME = OVERLAY_NAME
    engine.EXPECTED_COORDINATE_COUNT = EXPECTED_COORDINATE_COUNT
    engine.EXPECTED_COORDINATE_SHA256 = EXPECTED_COORDINATE_SHA256
    engine.DEFAULT_OVERLAY = DEFAULT_OVERLAY
    engine.SAFE_TMP_ROOT = SAFE_TMP_ROOT
    # Two deliberately non-word UI values (middle dot, box-drawing divider)
    # are whitelisted by their coordinate below.  This extension lets the
    # shared source-free overlay schema parse those values without accepting
    # Japanese glyphs.
    engine.HANGUL = re.compile(r"[\uac00-\ud7a3\u00b7\u2500]")


def repaired_korean(key: tuple[int, int], switch_value: str) -> tuple[str, bool]:
    if key in BULLET_REPAIRS:
        value = switch_value.replace(chr(0x30FB), "·")
        if value == switch_value:
            raise engine.StrdataP0Error(f"expected Japanese bullet not found at {key}")
        return value, True
    if key in SAFE_KO_OVERRIDES:
        return SAFE_KO_OVERRIDES[key], True
    return switch_value, False


def derive_overlay(active_input: Path, old_jp_input: Path, switch_zip: Path, output: Path) -> dict[str, Any]:
    engine.require_workstream_output(output)
    _, _, active = engine.parse_pinned_archive(active_input, engine.ACTIVE_PIN, "active Steam JP")
    _, _, old = engine.parse_pinned_archive(old_jp_input, engine.OLD_JP_PIN, "official JP reference backup")
    switch_packed = engine.switch_member_bytes(switch_zip)
    switch_raw = engine.verify_packed_pin(switch_packed, engine.SWITCH_MEMBER_PIN, "Switch v1.3 JP member")
    switch = engine.parse_raw_strdata(switch_raw)
    coordinates, source_hashes, _ = engine.load_coordinate_contract()
    active_text = engine.coordinate_texts(active)
    old_text = engine.coordinate_texts(old)
    switch_text = engine.coordinate_texts(switch)
    entries: list[dict[str, Any]] = []
    repaired_coordinates: list[dict[str, int]] = []
    for coordinate in coordinates:
        key = (coordinate["block_id"], coordinate["slot_id"])
        source, previous, reference = active_text[key], old_text[key], switch_text[key]
        if source != previous:
            raise engine.StrdataP0Error(f"active JP source differs from official JP reference at {key}")
        if engine.text_hash(source) != source_hashes[key]:
            raise engine.StrdataP0Error(f"active JP source hash differs from P0 contract at {key}")
        korean, repaired = repaired_korean(key, reference)
        if repaired:
            repaired_coordinates.append({"block_id": key[0], "slot_id": key[1]})
        mismatches = engine.common.invariant_mismatches(source, korean)
        if mismatches:
            raise engine.StrdataP0Error(f"Korean invariant mismatch at {key}: {mismatches!r}")
        if engine.KANA_OR_CJK.search(korean):
            raise engine.StrdataP0Error(f"Japanese or CJK glyph remains at {key}")
        if not REAL_HANGUL.search(korean) and key not in ALLOWED_NON_HANGUL:
            raise engine.StrdataP0Error(f"non-Hangul value is not explicitly allowed at {key}")
        entries.append(
            {
                "block_id": key[0],
                "slot_id": key[1],
                "source_jp_utf16le_sha256": engine.text_hash(source),
                "ko": korean,
                "ko_utf16le_sha256": engine.text_hash(korean),
                "status": "translated",
            }
        )
    expected_repairs = BULLET_REPAIRS | set(SAFE_KO_OVERRIDES)
    actual_repairs = {(item["block_id"], item["slot_id"]) for item in repaired_coordinates}
    if actual_repairs != expected_repairs:
        raise engine.StrdataP0Error("B04 repair scope differs from its explicit allowlist")
    overlay = {
        "schema": engine.OVERLAY_SCHEMA,
        "overlay_id": WORKSTREAM_ID,
        "resource": engine.RESOURCE,
        "base_language": "JP",
        "entry_count": len(entries),
        "distribution_policy": {
            "contains_commercial_source_text": False,
            "contains_complete_game_resource": False,
        },
        "stock_jp": engine.ACTIVE_PIN,
        "coordinate_contract": {
            "path": engine.COORDINATE_CONTRACT.relative_to(engine.REPOSITORY).as_posix(),
            "bundle_id": BUNDLE_ID,
            "coordinate_count": EXPECTED_COORDINATE_COUNT,
            "coordinate_sha256": EXPECTED_COORDINATE_SHA256,
        },
        "defaults": {"status": "translated"},
        "entries": entries,
    }
    engine.atomic_write(output, engine.json_bytes(overlay))
    checked, blob = engine.load_overlay(output)
    if checked != overlay:
        raise engine.StrdataP0Error("serialized B04 overlay did not round-trip exactly")
    return {
        "action": "derive-overlay",
        "output": str(output),
        "output_size": len(blob),
        "output_sha256": engine.sha256(blob),
        "translated_entries": len(entries),
        "exact_active_to_official_jp_source_matches": len(entries),
        "formatting_repairs": repaired_coordinates,
        "game_install_modified": False,
        "release_modified": False,
        "github_modified": False,
    }


def main(argv: Iterable[str] | None = None) -> int:
    configure_engine()
    engine.derive_overlay = derive_overlay
    return engine.main(argv)


configure_engine()
engine.derive_overlay = derive_overlay


if __name__ == "__main__":
    raise SystemExit(main())
