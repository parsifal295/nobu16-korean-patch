#!/usr/bin/env python3
"""Read-only evidence extractor for the Wave 22 static-dialogue candidate.

This helper is intentionally not a builder.  It records the exact Wave 20
preimages, PC-language anchors, proposed static target records, and active
font widths used to create the pinned Wave 22 builder.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import argparse
from pathlib import Path


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
TOOLS = REPO / "tools"
MSGGAME_TOOLS = REPO / "workstreams" / "msggame"
for root in (TOOLS, MSGGAME_TOOLS):
    sys.path.insert(0, str(root))

from msggame_format import LITERAL_END, LITERAL_START, parse_packed_msggame, parse_record_literals


STEAM = Path(r"F:\SteamLibrary\steamapps\common\NOBU16")
WAVE20 = REPO / "tmp" / "pc_text_quality_wave20_bundle_v1" / "candidate-v1"
BASE = "MSG/JP/msggame.bin"
PK = "MSG_PK/JP/msggame.bin"

# Each tuple keeps the original literal-marker count while concatenating to
# the user-approved Korean text and manual line breaks exactly.
FAMILIES = (
    ("farewell_good_news", (2, 557), (2, 574), ("배웅해 주셔서 감사하오", ".\n좋은 소식을 기다려 주시오.")),
    ("territory_development", (6, 4151), (6, 4181), ("주위에 공략할 성이 없어\n영내 발전에 힘쓰고 있습니다.", "\n모든 취락은 이미 장악했습니다.")),
    ("orders_worthy_result", (6, 4178), (6, 4208), ("알겠습니다.", "\n반드시 주명에 걸맞은 성과를\n가문에 가져오겠습니다.")),
    ("clan_order_pledge", (6, 4179), (6, 4209), ("알겠습니다.", "\n당가를 위해 주명을 완수하고자\n전력을 다하겠습니다.")),
    ("enemy_castle_stratagem", (6, 4181), (6, 4211), ("적성 공략의 뜻을 각 성주에게 전했더니\n다음 성에서 구체안이 나왔습니다.", "\n어느 성주의 계책을 쓸지", " 명해 주십시오.")),
    ("acknowledgement", (6, 4391), (6, 4450), ("알겠습니다.",)),
    ("start_after_mission_and_battle", (6, 4392), (6, 4451), ("알겠습니다.", "\n임무와 전투가 끝나는 대로\n착수하겠습니다.")),
    ("start_after_return_from_battle", (6, 4393), (6, 4452), ("알겠습니다.", "\n전투에서 돌아오는 대로\n착수하겠습니다.")),
    ("start_after_mission", (6, 4394), (6, 4453), ("알겠습니다.", "\n임무를 마치는 대로\n착수하겠습니다.")),
    ("spear_recruitment_reconsider", (6, 4404), (6, 4463), ("과연, 창을 다룰 이를", " 원하시는군요.", "\n하지만… 인선은 재고해 주십시오.")),
    ("rear_service_landholder", (6, 4439), (6, 4498), ("후방에서 백성을 섬기는 것이 본분이오.\n부디 영주로 임명해 주시오.",)),
    ("serve_clan_anywhere", (6, 4456), (6, 4515), ("어느 땅에서든 당가를 위해\n전력을 다하겠습니다.",)),
    ("dismissal_reconsider", (6, 4460), (6, 4519), ("혹시 저를 해임하려 하십니까?", "\n부디", " 다시 생각해 주십시오…")),
)

REFERENCE_PATHS = {
    "BASE_JP": Path(r"I:\Workspaces\NOBU16-Korean\private-inputs\legacy-pc-root\MSG\JP\msggame.bin"),
    "PK_JP": STEAM / "KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.6.0/originals/MSG_PK/JP/msggame.bin",
    "EN": STEAM / "MSG_PK/EN/msggame.bin",
    "SC": STEAM / "MSG_PK/SC/msggame.bin",
    "TC": STEAM / "MSG_PK/TC/msggame.bin",
}


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def records(path: Path):
    return {
        (record.block_id, record.record_id): record
        for block in parse_packed_msggame(path.read_bytes()).archive.blocks
        for record in block.records
    }


def literals(record):
    return tuple(item.text for item in parse_record_literals(record))


def spans(record):
    cursor = 0
    values = []
    for item in parse_record_literals(record):
        values.append(record.data[cursor:item.marker_offset])
        cursor = item.marker_end
    values.append(record.data[cursor:])
    return tuple(values)


def commands(record):
    result = []
    for span in spans(record):
        cursor = 0
        while cursor < len(span):
            if span[cursor:cursor + 2] == b"\x01\x43":
                result.append(span[cursor:cursor + 6].hex().upper())
                cursor += 6
            else:
                cursor += 1
    return tuple(result)


def report(record):
    values = literals(record)
    return {
        "sha256": sha(record.data),
        "size": len(record.data),
        "literals": list(values),
        "literal_utf16le_sha256": [sha(value.encode("utf-16-le")) for value in values],
        "opaque_spans_hex": [value.hex().upper() for value in spans(record)],
        "morphology_commands_hex": list(commands(record)),
    }


def strip_0143(span):
    output = bytearray()
    cursor = 0
    while cursor < len(span):
        if span[cursor:cursor + 2] == b"\x01\x43":
            if cursor + 6 > len(span):
                raise ValueError("truncated 0143 command")
            cursor += 6
        else:
            output.append(span[cursor])
            cursor += 1
    return bytes(output)


def target_record(source, values):
    source_spans = spans(source)
    if len(source_spans) != len(values) + 1:
        raise ValueError("target changes literal-marker count")
    payload = bytearray()
    for index, value in enumerate(values):
        payload.extend(strip_0143(source_spans[index]))
        payload.extend(LITERAL_START)
        payload.extend(value.encode("utf-16-le"))
        payload.extend(LITERAL_END)
    payload.extend(strip_0143(source_spans[-1]))
    raw = bytes(payload)
    class Record:
        data = raw
        block_id = 0
        record_id = 0
    return Record()


def load_wave19_font_widths(values):
    global _WAVE19_FONT
    try:
        module = _WAVE19_FONT
    except NameError:
        module = None
    if module is not None:
        return list(module.font_line_widths_px(values))
    path = REPO / "workstreams" / "pc_dialogue_quality_wave19_static_inflection_v1" / "build_pc_dialogue_quality_wave19_static_inflection_v1.py"
    spec = importlib.util.spec_from_file_location("wave19_font_probe", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _WAVE19_FONT = module
    return list(module.font_line_widths_px(values))


def main(argv: list[str] | None = None) -> int:
    # This script is also run directly from Windows shells whose default
    # CP949 output cannot encode the PC EN apostrophe glyph (Ö).  Force a
    # known stream and retain ASCII JSON as a second independent safeguard.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="strict")
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", type=int, action="append", default=[])
    args = parser.parse_args(argv)
    selected = (
        tuple(FAMILIES[index] for index in args.index)
        if args.index
        else FAMILIES
    )
    ko_base = records(WAVE20 / BASE)
    ko_pk = records(WAVE20 / PK)
    refs = {key: records(path) for key, path in REFERENCE_PATHS.items()}
    payload = {
        "input_file_sha256": {
            relative: sha((WAVE20 / relative).read_bytes())
            for relative in (BASE, PK)
        },
        "reference_file_sha256": {key: sha(path.read_bytes()) for key, path in REFERENCE_PATHS.items()},
        "families": [],
    }
    for name, base_coordinate, pk_coordinate, target_literals in selected:
        target = target_record(ko_base[base_coordinate], target_literals)
        if target.data != target_record(ko_pk[pk_coordinate], target_literals).data:
            raise ValueError(f"Base/PK target opaque spans differ: {name}")
        payload["families"].append({
            "name": name,
            "base_coordinate": f"{base_coordinate[0]}:{base_coordinate[1]}",
            "pk_coordinate": f"{pk_coordinate[0]}:{pk_coordinate[1]}",
            "target_literals": list(target_literals),
            "target": report(target),
            "font_line_widths_px": load_wave19_font_widths(target_literals),
            "base_preimage": report(ko_base[base_coordinate]),
            "pk_preimage": report(ko_pk[pk_coordinate]),
            "base_jp": report(refs["BASE_JP"][base_coordinate]),
            "pk_jp": report(refs["PK_JP"][pk_coordinate]),
            "contexts": {key: report(refs[key][pk_coordinate]) for key in ("EN", "SC", "TC")},
        })
    print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
