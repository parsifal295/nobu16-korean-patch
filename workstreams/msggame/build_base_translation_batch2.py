#!/usr/bin/env python3
"""Build source-free base-game SC msggame Korean translation batch 2."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent


def _load_private_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load private module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Load the preceding base batch only through a private module name.  Its
# private SC/JP/TC reader and repack engine remain separate from all public PK
# and base modules imported by other batch tests in the same Python process.
_template = _load_private_module(
    "_msggame_base_batch2_template", WORKSTREAM_ROOT / "build_base_translation_batch1.py"
)
previous = _template.previous
_engine = _template._engine
RESOURCE = _template.RESOURCE
LANGUAGES = _template.LANGUAGES
SOURCE_PATHS = _template.SOURCE_PATHS
WORKSPACE_ROOT = _template.WORKSPACE_ROOT

if RESOURCE != "MSG/SC/msggame.bin" or LANGUAGES != ("SC", "JP", "TC"):
    raise RuntimeError("base batch 1 template is no longer pinned to base SC/JP/TC resources")

BATCH_ID = "msggame_base_system_messages_b02r0139_0217.v0.2"
OVERLAY_NAME = "msggame_base_ko_system_messages_b02r0139_0217.v0.2.json"
EVIDENCE_NAME = "translation_alignment_evidence.base.v0.2.json"
REVIEW_NAME = "translation_review_index.base.v0.2.json"
VALIDATION_NAME = "translation_validation.base.v0.2.json"
NEXT_COORDINATE = (2, 218, 0)


# These are complete SC display-literal replacements, including dynamic-name
# join fragments and the visible '+' indicators in records 204, 207 and 208.
# JP and TC are consulted by the builder only as same-record semantic context;
# literal slots are intentionally never cross-language matched.
TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    (2, 139): ("변경 전 세력명:", ", 변경 후 세력명:", "가문", "."),
    (2, 140): ("의 멸망 원인 세력:", "입니다."),
    (2, 141): ("의 멸망 원인 세력:", "입니다."),
    (2, 142): ("이(가) 병에 걸렸습니다.",),
    (2, 143): ("등 발병 인원:", "명이 병에 걸렸습니다."),
    (2, 144): ("이(가) 회복했습니다.",),
    (2, 145): ("등 회복 인원:", "명이 회복했습니다."),
    (2, 146): ("공략 대상 세력:", "을(를) 공략하여 공략 방침을 달성했습니다."),
    (2, 147): ("공략 대상 세력:", "이(가) 멸망하여 공략 방침이 해제되었습니다."),
    (2, 148): ("공략 대상 세력:", "이(가) 아군이 되어 공략 방침이 해제되었습니다."),
    (2, 149): (
        "공략 대상 세력:",
        "으로 향하는 행군로가 사라져 공략 방침이 해제되었습니다.",
    ),
    (2, 150): ("공략 대상 세력:", "과(와) 휴전하여 공략 방침이 해제되었습니다."),
    (2, 151): ("공략 대상 성:", "을(를) 공략했습니다."),
    (2, 152): ("의 소속 세력이 바뀌어 공략 대상 성에서 해제되었습니다.",),
    (2, 153): ("의 소속 세력이 아군이 되어 공략 대상 성에서 해제되었습니다.",),
    (2, 154): (
        "행군로 소실 대상:",
        "으로 향하는 길이 사라져 공략 대상 성에서 해제되었습니다.",
    ),
    (2, 155): (
        "휴전 대상 성:",
        "의 소속 세력과 휴전하여 공략 대상 성에서 해제되었습니다.",
    ),
    (2, 156): ("지배 중인 성하에 막부의 권위를 나타내는 시설이 없습니다.",),
    (2, 157): ("지배 중인 성하에 막부의 권위를 나타내는 시설이 있습니다.",),
    (2, 158): ("당주는 정이대장군으로서 무사의 영수입니다.",),
    (2, 159): ("당주가 막부의 직책에 취임하지 않았습니다.",),
    (2, 160): ("당주의 막부 직책:", "입니다."),
    (2, 161): ("막부 창시자의 혈통을 잇는 가문:", "의 당주입니다."),
    (2, 162): ("막부와 인연이 있는 가문:", "의 당주입니다."),
    (2, 163): ("지배 중인 성하에 조정의 권위를 나타내는 시설이 없습니다.",),
    (2, 164): ("지배 중인 성하에 조정의 권위를 나타내는 시설이 있습니다.",),
    (2, 165): ("당주가 관직에 취임하지 않았습니다.",),
    (2, 166): ("당주의 조정 관직:", "입니다."),
    (2, 167): ("조정과 인연이 있는 가문:", "의 당주입니다."),
    (2, 168): ("지배 중인 성하에 종교·문화적 가치가 있는 시설이 없습니다.",),
    (2, 169): ("지배 중인 성하에 종교·문화적 권위를 나타내는 시설이 있습니다.",),
    (2, 170): ("일향종을 통솔하는 세력:", "의 종주입니다."),
    (2, 171): ("권위 있는 가문:", "의 당주입니다."),
    (2, 172): ("막부의 정당성을 드러내는 정책을 채택하지 않았습니다.",),
    (2, 173): ("막부의 정당성을 드러내는 정책을 채택했습니다.",),
    (2, 174): ("조정의 위광을 드러내는 정책을 채택하지 않았습니다.",),
    (2, 175): ("조정의 위광을 드러내는 정책을 채택했습니다.",),
    (2, 176): ("종교·문화 등 천하에 존재감을 드러내는 정책을 채택하지 않았습니다.",),
    (2, 177): ("종교·문화 등 천하에 존재감을 드러내는 정책을 채택했습니다.",),
    (2, 178): ("지배 중인 군에 종교·문화적 가치가 있는 취락이 없습니다.",),
    (2, 179): ("지배 중인 군에 종교·문화적 권위를 나타내는 취락이 있습니다.",),
    (2, 180): ("본가가 지배하는 성:", "개입니다."),
    (2, 181): ("이(가) 지배하는 지역:", "의 모든 성을 지배하고 있습니다."),
    (2, 182): (
        "옛 본거지:",
        "에서 이전하려는 목적지는\n",
        "입니다. 옮길 수 없는 시설이 있습니다.\n그래도 이전하시겠습니까?",
    ),
    (2, 183): (
        "본거지 이전 대상:",
        "에서 재이전할 목적지는\n",
        "입니다. 옮길 수 없는 시설이 있습니다.\n그래도 이전하시겠습니까?",
    ),
    (2, 184): (
        "시설 이전 출발지:",
        ", 목적지:",
        "입니다.\n건설 칸이 부족합니다.\n이전을 포기할 시설을 선택하십시오.",
    ),
    (2, 185): ("본거지 이전:", "→", "(으)로\n이전이 완료되었습니다."),
    (2, 186): ("옛 본거지:", "이(가) 함락되어 본거지를\n", "(으)로 옮겼습니다."),
    (2, 187): ("「", "」 등 정책 수:", "개. 해당 정책을 철회했습니다."),
    (2, 188): ("정책 「", "」을 철회했습니다."),
    (2, 189): ("위신이 하락하여 정책 「", "」을 철회했습니다."),
    (2, 190): ("다이묘의 방침과 맞지 않아 정책 「", "」을 철회했습니다."),
    (2, 191): ("정책 「", "」을 철회했습니다."),
    (2, 192): ("「", "」 등", "개 정책을 시행했습니다."),
    (2, 193): ("정책「", "」LV", "을 시행했습니다."),
    (2, 194): ("「", "」 등", "개 정책을 시행했습니다."),
    (2, 195): ("정책「", "」LV", "을 시행했습니다."),
    (2, 196): ("다음 달부터 정책「", "」을 철회할 예정입니다."),
    (2, 197): ("다음 달부터 「", "」 등", "개 정책을 철회할 예정입니다."),
    (2, 198): ("정책「", "」LV", "의 시행 준비를 시작했습니다."),
    (2, 199): ("「", "」 등", "개 정책의 시행 준비를 시작했습니다."),
    (2, 200): ("정책「", "」LV", "의 시행 준비를 시작했습니다."),
    (2, 201): ("「", "」 등", "개 정책의 시행 준비를 시작했습니다."),
    (2, 202): ("본가의 위신이", "으로 상승했습니다."),
    (2, 203): ("본가의 위신이", "으로 감소했습니다."),
    (2, 204): ("아군:", "을 제압했습니다. ", "+"),
    (2, 205): ("이(가) 함락되었습니다. ",),
    (2, 206): ("세력이 분단되어 위신이 변동했습니다.",),
    (2, 207): ("역직「", "」에 취임했습니다. ", "+"),
    (2, 208): ("관직「", "」에 취임했습니다. ", "+"),
    (2, 209): ("의 건설 가능 칸이 늘었습니다.",),
    (2, 210): ("의 건설 가능 칸이 줄었습니다.",),
    (2, 211): ("내 힘을 똑똑히 보아라!",),
    (2, 212): ("백성을 다스리는 비결은 진심뿐이다.\n이 군은 내가 장악하겠다!",),
    (2, 213): ("때가 왔다:", "이(가) 쌓아 온 인맥을\n본가에 보탤 때가 온 모양이군."),
    (2, 214): (
        "인맥의 힘:",
        "이(가) 쌓아 온 인맥으로,\n보좌할 대상:",
        "의 움직임을 도와,\n본가에 새바람을 일으키자.",
    ),
    (2, 215): ("사람을 쓰는 일에는 제법 자신이 있지……\n부하 지휘는 내게 맡겨라.",),
    (2, 216): ("말솜씨 하나는 자신 있다.\n내 언변으로 신뢰를 얻어 내지!",),
    (2, 217): ("언변으로 보좌할 대상:", ".\n반드시 신뢰를 얻어 내겠다!"),
}

SKIPPED_CANDIDATES: dict[tuple[int, int, int], str] = {}
EXPECTED_RECORD_KEYS = tuple(TRANSLATIONS)


def selected_record_keys() -> list[tuple[int, int]]:
    return sorted(TRANSLATIONS)


def selected_coordinates() -> list[tuple[int, int, int]]:
    return [
        (block_id, record_id, literal_id)
        for (block_id, record_id), replacements in sorted(TRANSLATIONS.items())
        for literal_id, replacement in enumerate(replacements)
        if replacement is not None
    ]


def validate_static_scope() -> None:
    keys = selected_record_keys()
    selected = selected_coordinates()
    if keys != sorted(EXPECTED_RECORD_KEYS):
        raise ValueError("translation scan record set changed")
    if selected[0] != (2, 139, 0) or selected[-1] != (2, 217, 1):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 79:
        raise ValueError("translation batch scope changed")
    if SKIPPED_CANDIDATES:
        raise ValueError("translation batch unexpectedly contains skips")


_engine.previous = previous
_engine.RESOURCE = RESOURCE
_engine.LANGUAGES = LANGUAGES
_engine.SOURCE_PATHS = SOURCE_PATHS
_engine.SCRIPT_PATH = SCRIPT_PATH
_engine.BATCH_ID = BATCH_ID
_engine.OVERLAY_NAME = OVERLAY_NAME
_engine.EVIDENCE_NAME = EVIDENCE_NAME
_engine.REVIEW_NAME = REVIEW_NAME
_engine.VALIDATION_NAME = VALIDATION_NAME
_engine.NEXT_COORDINATE = NEXT_COORDINATE
_engine.LAST_COORDINATE = (2, 217, 1)
_engine.TRANSLATIONS = TRANSLATIONS
_engine.SKIPPED_CANDIDATES = SKIPPED_CANDIDATES
_engine.EXPECTED_RECORD_KEYS = EXPECTED_RECORD_KEYS
_engine.validate_static_scope = validate_static_scope
build = _engine.build


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for language in LANGUAGES:
        parser.add_argument(
            f"--stock-{language.lower()}",
            type=Path,
            default=WORKSPACE_ROOT / Path(SOURCE_PATHS[language]),
        )
    parser.add_argument("--out-root", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    try:
        result = build(parse_args())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"out_root={result['out_root']}")
    print(f"records={result['record_count']}")
    print(f"entries={result['entry_count']}")
    print(f"skipped={result['skipped_count']}")
    print("next_coordinate=" + ",".join(map(str, result["next_coordinate"])))
    print(f"target_packed_sha256={result['target_packed_sha256']}")
    for name, artifact in result["artifacts"].items():
        print(f"{name}_sha256={artifact['sha256']}")
    print("contains_commercial_source_text=False")
    print("installed_game_files_modified=False")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
