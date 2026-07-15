#!/usr/bin/env python3
"""Build source-free base-game SC msggame Korean translation batch 1."""

from __future__ import annotations

import argparse
import importlib.util
import inspect
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


# The PK helpers are loaded privately, then pointed at the separately pinned
# base-game resources.  This prevents PK batch modules from being mutated when
# this generator or its tests are imported in the same Python process.
previous = _load_private_module(
    "_msggame_base_batch1_helpers", WORKSTREAM_ROOT / "build_translation_batch1.py"
)
RESOURCE = "MSG/SC/msggame.bin"
LANGUAGES = ("SC", "JP", "TC")
SOURCE_PATHS = {language: f"MSG/{language}/msggame.bin" for language in LANGUAGES}
previous.RESOURCE = RESOURCE
previous.LANGUAGES = LANGUAGES
previous.SOURCE_PATHS = SOURCE_PATHS
WORKSPACE_ROOT = previous.WORKSPACE_ROOT

# Reuse the verified variable-length overlay/repack path in a second private
# module.  The replacement below changes only batch-specific wording and the
# continuation assertion; all binary validation remains the established path.
_engine = _load_private_module(
    "_msggame_base_batch1_engine", WORKSTREAM_ROOT / "build_translation_batch18.py"
)

BATCH_ID = "msggame_base_system_messages_b00r1194_b02r0138.v0.1"
OVERLAY_NAME = "msggame_base_ko_system_messages_b00r1194_b02r0138.v0.1.json"
EVIDENCE_NAME = "translation_alignment_evidence.base.v0.1.json"
REVIEW_NAME = "translation_review_index.base.v0.1.json"
VALIDATION_NAME = "translation_validation.base.v0.1.json"
NEXT_COORDINATE = (2, 139, 0)


# Dialogue grammar and honorific fragments are real display literals in the
# base SC route.  They are retained as individual coordinates so the game's
# dynamic concatenation bytecode stays untouched.
BLOCK0_TRANSLATIONS: dict[int, str] = {
    1194: "나",
    1195: "이 몸",
    1196: "나",
    1197: "나",
    1198: "이 몸",
    1199: "소인",
    1200: "나",
    1201: "저",
    1202: "소승",
    1204: "놈",
    1206: "놈",
    1208: "놈",
    1209: "우리",
    1210: "우리",
    1211: "우리",
    1212: "우리",
    1213: "너",
    1214: "너",
    1215: "그대",
    1216: "그대",
    1217: "네놈",
    1218: "그대",
    1219: "당신",
    1220: "당신",
    1221: "그대",
    1222: "당신",
    1223: "당신",
    1224: "아버님",
    1225: "어머님",
    1226: "할아버님",
    1227: "할머님",
    1228: "형님",
    1229: "누님",
    1230: "숙부님",
    1231: "숙모님",
    1232: "나리",
    1233: "나리",
    1234: "나리",
    1235: "쇼군님",
    1236: "관주님",
    1237: "스님",
    1238: "대전",
    1239: "대전",
    1240: "노대인",
    1241: "도련님",
    1242: "공주님",
    1243: "마님",
    1244: "원숭이",
    1246: "놈",
    1249: "놈",
    1250: "님",
    1251: "나리",
    1252: "님",
    1253: "나리",
    1254: "님",
    1255: "나리",
    1256: "그자",
    1257: "그놈",
    1258: "그놈",
    1259: "녀석",
    1260: "녀석",
    1261: "이놈",
    1262: "이놈",
    1263: "그분",
    1264: "그 어르신",
    1266: "놈",
    1269: "놈",
    1270: "님",
    1271: "나리",
    1272: "님",
    1273: "나리",
    1274: "님",
    1275: "나리",
    1277: "놈",
    1280: "놈",
    1281: "님",
    1282: "나리",
    1283: "님",
    1284: "나리",
    1285: "님",
    1286: "나리",
    1288: "놈",
    1291: "놈",
    1292: "님",
    1293: "나리",
    1294: "님",
    1295: "나리",
    1296: "님",
    1297: "나리",
    1298: "음……",
    1299: "음……",
    1300: "하하하",
    1301: "후후후",
}

TRANSLATIONS: dict[tuple[int, int], tuple[str | None, ...]] = {
    **{(0, record_id): (ko,) for record_id, ko in BLOCK0_TRANSLATIONS.items()},
    (1, 3): ("그야말로 청천벽력입니다.\n",),
    (2, 80): ("성인식을 마친 공주가 있군.\n공주의 앞날도 생각해 봐야겠어……",),
    (2, 81): ("성인식을 마친 공주가 있는 모양이군요.\n공주의 앞날도 생각해 봐야겠습니다……",),
    (2, 82): ("성인식을 마친 공주가 있습니다.\n공주의 앞날도 헤아려 주십시오……",),
    (2, 83): ("성인식을 마친 공주가 있습니다.\n공주의 앞날도 헤아려 주십시오……",),
    (2, 84): ("이름과 읽는 법을 입력해 주십시오.",),
    (2, 85): ("이름에 사용할 수 없는 문자가 포함되어 있습니다.",),
    (2, 86): ("내용을 확인한 뒤 확인을 눌러 주십시오.",),
    (2, 87): ("무장으로 키울지 공주로 키울지 선택한 뒤 확인을 눌러 주십시오.",),
    (2, 88): ("부인:", "이(가) 무장으로 원복했습니다."),
    (2, 89): ("딸:", "이(가) 무장으로 원복했습니다."),
    (2, 90): ("부인:", "이(가) 성인식을 마치고 성인이 되었습니다."),
    (2, 91): ("딸:", "이(가) 성인식을 마치고 성인이 되었습니다."),
    (2, 92): ("가신의 딸:", "이(가) 성인이 되었습니다."),
    (2, 97): (
        "성인식을 마쳐 저도 어엿한 성인이 되었습니다.\n"
        "무가의 아내로서 맡은 바를 다하도록,\n앞으로도 정진하겠습니다.",
    ),
    (2, 98): (
        "마침내 어엿한 성인이 되었으니,\n앞으로 주군을 훌륭히 보필하고,\n"
        "본가의 번영에 조금이나마 힘이 되겠습니다.",
    ),
    (2, 103): (
        "님, 찾아뵈었습니다.\n성인식도 마쳤으니 이제부터\n충성을 바칠 대상:",
        "입니다.",
    ),
    (2, 104): (
        "성인식을 마친 무가의 딸로서,\n충성을 바칠 대상:",
        "에게 힘을 보탤 날을 맞아,\n오랫동안 기다려 온 보람을 느낍니다.",
    ),
    (2, 105): ("원복 완료 인원:", "명.\n어엿한 무장으로 성장했습니다."),
    (2, 106): ("휘하 합류 인원:", "명.\n원복을 마치고 휘하의 무장이 되었습니다."),
    (2, 107): ("의 적대 목표를 갱신했습니다.",),
    (2, 108): ("의 수입이 부족하여 금전 공납량이 감소했습니다.",),
    (2, 109): ("의 수입이 부족하여 군량 공납량이 감소했습니다.",),
    (2, 110): ("의 수입이 부족하여 군마 공납량이 감소했습니다.",),
    (2, 111): ("의 수입이 부족하여 철포 공납량이 감소했습니다.",),
    (2, 112): ("플레이어 세력이 멸망했습니다.\n게임을 종료합니다.",),
    (2, 113): ("혼인 동맹 파기 대상:", "입니다.\n실행하시겠습니까?"),
    (2, 114): ("혼인 동맹 파기 대상:", "등입니다.\n실행하시겠습니까?"),
    (2, 115): (
        "혈연관계가 없는 대상:",
        ".\n이로 인해 출가하려는 공주가 있습니다. 허락하시겠습니까?",
    ),
    (2, 120): (
        "나머지는 제게 맡겨주십시오.\n후임 당주:",
        "이(가) 본가를 패자로 만들겠습니다.",
    ),
    (2, 121): (
        "라는 이름은 무겁지만 자랑스럽기도 하여,\n마음이 절로 다잡아집니다.\n"
        "앞으로는 제게 맡겨주십시오.",
    ),
    (2, 122): ("제게 맡겨주십시오.\n본가는 제가 지켜내겠습니다.",),
    (2, 123): (
        "안심하십시오. 전 당주:",
        "가 지켜 온 본가:",
        "입니다.\n제 지략과 무용으로 가문을 이어가겠습니다……\n"
        "아니, 더욱 번영시키겠다고 맹세합니다.",
    ),
    (2, 124): ("전 당주:", "\n그 뒤를 이어 이 가문을 다시 일으키겠습니다."),
    (2, 125): ("님, 지금까지 본가의 주인으로서\n정말 수고 많으셨습니다.\n후임:", "에게 맡겨주십시오."),
    (2, 132): ("편히 쉬십시오.\n본가는…… 제가 반드시 지켜내겠습니다.",),
    (2, 137): ("이(가) 당주가 된 가문:", "입니다."),
    (2, 138): ("에서 출가한 인물:", "입니다."),
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
    if selected[0] != (0, 1194, 0) or selected[-1] != (2, 138, 1):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 131:
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
_engine.LAST_COORDINATE = (2, 138, 1)
_engine.TRANSLATIONS = TRANSLATIONS
_engine.SKIPPED_CANDIDATES = SKIPPED_CANDIDATES
_engine.EXPECTED_RECORD_KEYS = EXPECTED_RECORD_KEYS
_engine.validate_static_scope = validate_static_scope

_engine_build_source = inspect.getsource(_engine.build)
_replacements = {
    "if selected[-1] != (6, 3298, 0) or NEXT_COORDINATE not in sc_literals:": "if selected[-1] != LAST_COORDINATE or NEXT_COORDINATE not in sc_literals:",
    "same_pk_resource_role": "same_base_resource_role",
    "assistant_generated_draft_from_pinned_sc_jp_en_tc_record_context": "assistant_generated_draft_from_pinned_sc_jp_tc_record_context",
}
for old, new in _replacements.items():
    if old not in _engine_build_source:
        raise RuntimeError(f"batch engine source changed: missing {old!r}")
    _engine_build_source = _engine_build_source.replace(old, new)
exec(compile(_engine_build_source, str(SCRIPT_PATH), "exec"), _engine.__dict__)
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
