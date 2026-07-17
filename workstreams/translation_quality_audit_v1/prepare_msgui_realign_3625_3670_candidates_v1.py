#!/usr/bin/env python3
"""Prepare direct PC-source fixes for the verified msgui misalignment slice.

The listed current Korean strings describe unrelated UI actions.  Each new
Korean value was reviewed against the same-coordinate pristine PC Japanese
text plus PC EN/SC/TC context.  No Switch Korean text is read by this tool.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
INPUT = REPO / "tmp" / "translation_quality_audit_v1" / "semantic_inventory_v3" / "private_full_pairs.jsonl"
OUTPUT = REPO / "tmp" / "translation_quality_audit_v1" / "semantic" / "msgui_realign_3625_3670.v1.jsonl"

# Coordinates are limited to the confirmed bad mappings in this interval.
# Values are Korean editorial translations, not copied from Switch text.
FIXES = {
    3625: "모든 이벤트 발생이 비활성화되어 있습니다.",
    3626: "출진 중이 아닙니다.",
    3627: "가보를 보유하고 있지 않습니다.",
    3628: "명성 있는 무장이 없습니다.",
    3629: "영주가 없습니다.",
    3633: "가보를 보유한 세력이 없습니다.",
    3634: "세력에 소속되어 있지 않습니다.",
    3635: "영지가 적 세력에게 빼앗겼습니다.",
    3639: "국인중 부대입니다.",
    3640: "파견할 무장을 선택하십시오.",
    3641: "성하 방침을 설정할 성을 선택하십시오.",
    3643: "성주가 부재중이므로 선택할 수 없습니다.",
    3644: "파견할 수 있는 측근 또는 인근 성주가 없습니다.",
    3645: "국인중의 종속도가 오를 때까지 기다려야 합니다.",
    3647: "대관을 임명할 수 있는 군이 없습니다.",
    3649: "영지를 빼앗겨 성에서 대기 중입니다. 되찾으면 영주로 복귀합니다.",
    3650: "영지에 임명할 무장을 선택하십시오.",
    3651: "영지로 줄 군을 선택하십시오.",
    3653: "정책이 철회되어 다음 항목이 제한됩니다.",
    3654: "・설정된 성하 방침을 모두 해제",
    3656: "・구매 가능한 가보 등급 제한",
    3659: "・일부 성에서 마구간 건설 불가",
    3662: "지배하는 군이 없는 성에는 선동할 수 없습니다.",
    3665: "※상황에 따라 소속 세력의 본거지에 등장합니다.",
    3667: "본거지 외에는 장악할 여지가 있는 성이 없습니다.",
    3668: "출진 중이므로 회유할 수 없습니다.",
}
RUNTIME_RE = re.compile(r"\[([a-z]+\d+)\]")
PRINTF_RE = re.compile(r"%(?:\d+\$)?[-+#0 ]*\d*(?:\.\d+)?[A-Za-z]")
ESC_RE = re.compile(r"\x1bC.", re.DOTALL)
KANA_OR_HAN_RE = re.compile(r"[\u3041-\u3096\u30a1-\u30fa\u30fc-\u30ff\u31f0-\u31ff\uff66-\uff9d\uff9f\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-16-le")).hexdigest().upper()


def format_profile(text: str) -> dict[str, object]:
    return {
        "runtime": RUNTIME_RE.findall(text),
        "printf": PRINTF_RE.findall(text),
        "esc": ESC_RE.findall(text),
        "linebreaks": re.findall(r"\r\n|\n|\r", text),
        "leading_whitespace": text[: len(text) - len(text.lstrip())],
        "trailing_whitespace": text[len(text.rstrip()) :],
        "private_use": [f"U+{ord(char):04X}" for char in text if 0xE000 <= ord(char) <= 0xF8FF],
    }


def atomic_write(path: Path, text: str) -> None:
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    tmp_root = (REPO / "tmp").resolve()
    output = args.output.resolve()
    if output == tmp_root or tmp_root not in output.parents:
        raise SystemExit("output must remain below tmp")
    rows = {
        int(row["coordinate"]): row
        for row in map(json.loads, args.input.read_text(encoding="utf-8").splitlines())
        if row["resource"] == "msgui"
    }
    if set(FIXES) - set(rows):
        raise SystemExit("review coordinate is absent from msgui inventory")
    output_rows: list[dict[str, object]] = []
    for entry_id, ko in sorted(FIXES.items()):
        row = rows[entry_id]
        jp_profile = format_profile(row["jp"])
        ko_profile = format_profile(ko)
        if jp_profile != ko_profile:
            raise SystemExit(f"format mismatch against pristine JP at msgui:{entry_id}")
        if KANA_OR_HAN_RE.search(ko):
            raise SystemExit(f"Korean proposal retains Japanese/CJK at msgui:{entry_id}")
        if ko == row["ko"]:
            raise SystemExit(f"proposal is not an effective correction at msgui:{entry_id}")
        output_rows.append({
            "id": entry_id,
            "issue_type": "coordinate_semantic_misalignment",
            "proposed_ko": ko,
            "source_current_hash": text_hash(row["ko"]),
            "pristine_jp_hash": text_hash(row["jp"]),
            "format_profile": jp_profile,
        })
    if len(output_rows) != 26:
        raise SystemExit("unexpected proposal count")
    atomic_write(output, "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in output_rows))
    print(json.dumps({"entry_count": len(output_rows), "output": str(output), "switch_korean_translation_used": False, "game_files_written": False}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
