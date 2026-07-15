#!/usr/bin/env python3
"""Build source-free PK/SC msggame Korean translation batch 20."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = SCRIPT_PATH.parent


def _load_isolated_engine() -> Any:
    """Load batch 19 privately so its public import state stays untouched."""

    engine_path = WORKSTREAM_ROOT / "build_translation_batch19.py"
    spec = importlib.util.spec_from_file_location("_msggame_batch20_engine", engine_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load generator engine: {engine_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_template = _load_isolated_engine()
_engine = _template._engine

# Batch 19 privately widened its scan only to preserve three earlier trailing
# empty slots.  Restore the original visible-literal predicate before selecting
# this strictly next PK range; no public batch-19 module is changed.
if not hasattr(_template, "_engine_previous"):
    raise RuntimeError("batch 19 engine no longer exposes its original visible-literal reader")
_engine.previous = _template._engine_previous

BATCH_ID = "msggame_pk_system_messages_b06r3478_3697.v0.20"
OVERLAY_NAME = "msggame_ko_system_messages_b06r3478_3697.v0.20.json"
EVIDENCE_NAME = "translation_alignment_evidence.v0.20.json"
REVIEW_NAME = "translation_review_index.v0.20.json"
VALIDATION_NAME = "translation_validation.v0.20.json"
RESOURCE = _engine.RESOURCE
LANGUAGES = _engine.LANGUAGES
SOURCE_PATHS = _engine.SOURCE_PATHS
WORKSPACE_ROOT = _engine.WORKSPACE_ROOT
previous = _engine.previous
NEXT_COORDINATE = (6, 3698, 0)


# Project-authored Korean only.  Each tuple preserves the SC record's literal
# slot count, line-break sequence, and leading/trailing whitespace around
# dynamic name, office, and treasure insertions.
TRANSLATIONS: dict[tuple[int, int], tuple[str, ...]] = {
    (6, 3478): (
        "대인을 위해 힘쓸 수 있어\n더없이 영광입니다.\n상으로",
        "이나 관직 등을 내려 주셔도 됩니다.",
    ),
    (6, 3479): (
        "대인을 위해 힘쓸 수 있어\n더없이 영광입니다.\n상으로",
        "이나 관직 등을 내려 주셔도 됩니다.",
    ),
    (6, 3483): (
        "대인을 위해 힘쓸 수 있어\n더없이 영광입니다.\n상으로",
        "이나 관직 등을 내려 주셔도 됩니다.",
    ),
    (6, 3489): (
        "말하자면:",
        "은 그야말로 가신의 얼굴……\n공훈 1위를 차지하지 못해서야\n도저히",
        "의 패업을 받들기엔 역부족이겠지.",
    ),
    (6, 3490): (
        "대인께서 중용해 주신 덕에\n제가 이 자리에 설 수 있었습니다.\n앞으로도 대인을 위해 힘쓰는 것을 사명으로 삼겠습니다.",
    ),
    (6, 3491): ("공훈 1위라……\n뭐, 거드름 피우는 데 질려서\n제 직분의 일을 했을 뿐이오.",),
    (6, 3495): (
        "대인께서 중용해 주신 덕에\n제가 이 자리에 설 수 있었습니다.\n앞으로도 대인을 위해 힘쓰는 것을 사명으로 삼겠습니다.",
    ),
    (6, 3499): ("평소의 노력이 인정받은 모양이군요.\n앞으로도 더욱 정진하겠습니다.",),
    (6, 3500): (
        "오,",
        "께서",
        "이 되셨군요……\n그러나",
        "의 판단을 후회하게 하지 않도록\n이 직위에 걸맞게 힘쓰겠습니다.",
    ),
    (6, 3501): ("승진할 기회를 받다니,\n더없이 감사할 따름입니다.",),
    (6, 3502): ("발탁 직위:", "에 발탁되다니……\n우쭐해하지 않고\n더 큰 공훈을 세우겠습니다."),
    (6, 3503): ("새 직위:", "이 된다면\n그에 걸맞은 책임도 따르겠지요.\n마음 단단히 먹겠습니다."),
    (6, 3504): ("마침내", "이 되었습니다……!\n이 은혜는 평생을 걸고 갚겠습니다."),
    (6, 3505): ("일한 보람이 있군요.\n충성을 다한 것도 헛되지 않았습니다.\n더욱 본가를 번영시키겠습니다.",),
    (6, 3506): ("승진 직위:", "이 되는 일이\n이토록 기쁠 줄이야."),
    (6, 3507): ("가신 모두가 더욱 충성을 다해\n본가를 일으켜 세워야 합니다……",),
    (6, 3508): ("공이 많은 자, 적은 자……\n논공행상은 자신의 공적을 돌아보는\n좋은 계기가 되겠군요.",),
    (6, 3509): ("상벌을 분명히 하는 것은 나라의 근본.\n공을 세운 자에게 합당한 상을 내리는 것은\n당연한 일입니다.",),
    (6, 3514): ("의", "가 공훈 1위라니……\n기쁘기도 하지만,\n더욱", "의 오른팔이 되겠습니다."),
    (6, 3515): ("공훈 1위라니 참으로 기쁩니다.\n아직 미숙하지만 한 걸음씩 나아가며\n본가에 공헌하겠습니다.",),
    (6, 3516): ("제가 공훈 1위라니……\n미숙한 제게 과분한 평가입니다.\n황송할 따름입니다.",),
    (6, 3517): ("공훈 1위라니 정말 기쁩니다.\n앞으로도 이 영예에 자만하지 않고\n스스로를 엄히 다스리겠습니다.",),
    (6, 3518): ("공훈 1위라니……\n부하들은 제 무모함에\n진땀을 빼고 있을 줄 알았는데…… ",),
    (6, 3524): ("공훈 1위라니요?!\n이를 계기로,\n다음에도 힘껏 뛰겠습니다!",),
    (6, 3525): ("아직 한참 더 일할 수 있습니다!\n더 많은 일을 맡겨 주십시오!",),
    (6, 3536): ("공훈 수석이 되다니,\n더없이 영광입니다.\n앞으로도 본가의 번영을 위해 힘쓰겠습니다!",),
    (6, 3537): ("가신은 그야말로 가문의 얼굴……\n공훈 1위를 차지하지 못한다면\n도저히", "의 패업을 뒷받침하기엔 역부족이겠지."),
    (6, 3538): ("의", "가 공훈 1위라니……\n더없이 기쁘지만,\n부하들도 더욱 힘써 주었으면 좋겠군."),
    (6, 3539): ("신하의 도를 닦는 길에는 끝이 없습니다……\n본가의 앞날을 지켜보는 것이야말로\n", "의 천명입니다."),
    (6, 3540): ("오, 공훈 1위라……\n직위", "이 되면 할 일이 많으니,\n마땅히 열심히 해야지."),
    (6, 3541): ("공훈 1위라……\n뭐, 거드름 피우는 데 질려서\n제 직분의 일을 했을 뿐이오.",),
    (6, 3548): ("좋아!", "의 체면은 지켰군.\n……", "라고 하면 나이 든 것 같아\n썩 기분 좋지는 않지만……"),
    (6, 3549): ("공훈 1위라니……\n최고의 영예라 할 만하군.\n항상 이 마음을 잊지 말아야지!",),
    (6, 3558): ("참으로 경사로군요.\n앞으로도 본가를 잘 부탁드립니다.",),
    (6, 3559): ("앞으로는 두 분이 힘을 합쳐\n본가를 지켜 주십시오.",),
    (6, 3560): ("경사로다, 경사로다.\n앞으로도 잘 부탁한다.",),
    (6, 3564): ("두 분 모두 그 재능을 살려\n본가를 지켜 주십시오.",),
    (6, 3570): ("예, 기대를 저버리지 않는 활약을\n보여 드리겠습니다.",),
    (6, 3571): ("반드시 도움이 되어 보이겠습니다.",),
    (6, 3572): ("예, 어떤 일이든 제게 맡겨 주십시오.",),
    (6, 3576): ("예, 반드시 기대에\n부응하겠습니다.",),
    (6, 3582): ("신분:", "으로서\n보필할 대상:"),
    (6, 3583): ("부부로서 서로 굳게 의지하며\n살아가면 좋겠군.",),
    (6, 3584): ("오늘부터 부부로구나.\n경사로다, 경사로다.",),
    (6, 3588): ("신분:", "으로서\n보필할 대상:"),
    (6, 3594): ("예, 미력하나마\n힘이 되고 싶습니다.",),
    (6, 3595): ("예, 미력하나마\n힘이 되고 싶습니다.",),
    (6, 3596): ("예, 미력하나마\n힘이 되고 싶습니다.",),
    (6, 3600): ("미력하나마\n힘이 되고 싶습니다.",),
    (6, 3606): ("예, 이 목숨을 바쳐서라도\n지키겠습니다.",),
    (6, 3607): ("무슨 일이 있어도\n마지막까지 곁을 지키겠습니다.",),
    (6, 3608): ("예, 목숨이 다할 때까지\n싸워 나가겠습니다!",),
    (6, 3612): ("예, 이 목숨이 다할 때까지\n온 힘을 다하겠습니다.",),
    (6, 3616): ("이제\n", "의 가보를 빼앗게 됩니다.\n그래도 진행하시겠습니까?"),
    (6, 3617): ("입력한 내용이 폐기됩니다.\n그래도 진행하시겠습니까?",),
    (6, 3618): ("대상:", "의 관직은\n조정에 반납됩니다.\n그래도 진행하시겠습니까?"),
    (6, 3621): ("마음은 고맙지만\n비교 대상:", "이 가진\n", "보다 더 좋은 것을 받고 싶습니다……"),
    (6, 3622): ("받는다고 해도", "\n하지만 비교 대상:", "이 가진", "과 비교하면\n조금 아쉽군요……"),
    (6, 3623): ("제안 품목:", "\n을 주고\n", "을 돌려받겠다는 뜻이었군……\n그런 셈이었나."),
    (6, 3627): ("교환 품목:", "/소유자:", "이 가진\n", "\n아, 아닙니다. 아무것도……"),
    (6, 3633): ("물건:", "이군요……\n소유자:", "이 손에 넣어야 할 운명인 듯합니다."),
    (6, 3634): ("물건:", "……\n이유는 알 수 없지만,\n묘한 인연이 느껴집니다."),
    (6, 3635): ("물건:", "이군요……\n참으로 제 마음에 드는 물건입니다."),
    (6, 3639): ("물건:", "이군요……\n대상:", "과 강한 인연이 느껴집니다."),
    (6, 3645): ("혹시\n", "의 취향을 알고 계시는군요."),
    (6, 3646): ("설마\n", "의 취향을 알고 계신 겁니까?"),
    (6, 3647): ("오, 이건 마음에 드는군! ",),
    (6, 3651): ("이런 진귀한 물건을:", "에게 주시다니……\n정말 마음에 듭니다."),
    (6, 3655): ("오랫동안 바라던", "을 이렇게 내려 주시다니……\n감사의 말씀도 부족합니다."),
    (6, 3656): ("수령자:", "의 취향에 꼭 맞는 일품……\n기쁘지 않을 리가 있겠습니까?"),
    (6, 3657): ("뭣,", "을……!\n수령자:", "의 취향을 알고 계시다니,\n놀라움을 감출 수 없습니다."),
    (6, 3660): ("감사하기 그지없습니다.\n앞으로 더욱 활약하겠습니다.",),
    (6, 3661): ("선물:", "\n더없이 기쁩니다."),
    (6, 3662): ("받은 은혜는\n반드시 갚겠습니다.",),
    (6, 3666): ("선물:", "\n정말 감사합니다."),
    (6, 3672): ("설마", "의", "을 빼앗다니,\n대체 무슨 속셈입니까……"),
    (6, 3673): ("설마", "의", "을 빼앗다니,\n농담이 아니었군요."),
    (6, 3674): ("설마", "의", "을 빼앗다니,\n이런 일은 결코 용납할 수 없습니다."),
    (6, 3678): ("잠깐만요.\n빼앗지 말아 주세요:", "의"),
    (6, 3684): ("추천 대상:", "/추천 직책:", "\n감사한 마음을 이루 말할 수 없습니다."),
    (6, 3685): ("정말 감사합니다.\n추천 대상:", "/추천 직책:"),
    (6, 3686): ("님께서", "을", "으로 추천해 주시다니,\n감사한 마음을 이루 말할 수 없습니다."),
    (6, 3690): ("뜻밖에도\n추천 대상:", "/추천 직책:", "\n뜻밖의 기쁨입니다."),
    (6, 3696): ("동맹 상대:", "와의 동맹은 이제 두 달 남았습니다.\n동맹을 이어 갈지 끝낼지,\n신중히 생각해 주십시오."),
    (6, 3697): ("동맹 상대:", "와의 동맹은 이제 두 달 남았습니다.\n동맹을 이어 갈지 끝낼지,\n잘 생각해 주십시오."),
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
    if selected[0] != (6, 3478, 0) or selected[-1] != (6, 3697, 1):
        raise ValueError("translation batch boundaries changed")
    if len(selected) != 150 or len(keys) != 85:
        raise ValueError("translation batch scope changed")
    if SKIPPED_CANDIDATES:
        raise ValueError("translation batch unexpectedly contains skips")


_engine.SCRIPT_PATH = SCRIPT_PATH
_engine.BATCH_ID = BATCH_ID
_engine.OVERLAY_NAME = OVERLAY_NAME
_engine.EVIDENCE_NAME = EVIDENCE_NAME
_engine.REVIEW_NAME = REVIEW_NAME
_engine.VALIDATION_NAME = VALIDATION_NAME
_engine.NEXT_COORDINATE = NEXT_COORDINATE
_engine.LAST_COORDINATE = (6, 3697, 1)
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
