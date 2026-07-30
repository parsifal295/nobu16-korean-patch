#!/usr/bin/env python3
"""Build source-redacted PK B048 segment 1157 residual decisions."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TEMPLATE_PATH = WORKSTREAM / "build_pk_batch047_segment1154.py"
DECISIONS_ROOT = REPO / "tmp" / WORKSTREAM.name / "decisions"
OUTPUT = DECISIONS_ROOT / "pk_msggame_B048_S1157.private.v1.jsonl"
PREFILL = DECISIONS_ROOT / "pk_msggame_base_exact_reuse_prefill.private.v1.jsonl"
BASE_PROMOTED = (
    REPO / "tmp" / WORKSTREAM.name
    / "base_msggame_runtime_vm_verified.private.v1.jsonl"
)
OPTIONAL_NEIGHBORS = (
    DECISIONS_ROOT / "pk_msggame_B048_S1155.private.v1.jsonl",
    DECISIONS_ROOT / "pk_msggame_B048_S1156.private.v1.jsonl",
)
STEAM_PK = Path(
    r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"
)

SEGMENT = 1157
QUEUE_BATCH_ID = "pk_msggame-B048"
QUEUE_START = 134
QUEUE_STOP = 200
QUEUE_FIRST_RECORD = 4627
QUEUE_LAST_RECORD = 4709
BLOCK_ID = 6
PK_RECORD_COUNT = 21_751
TARGET_COORDINATES = tuple(
    """
    6:4674:0 6:4674:1
    6:4675:0 6:4675:1 6:4675:2
    6:4676:0 6:4676:1 6:4676:2 6:4676:3
    6:4677:0
    6:4678:0 6:4678:1
    6:4679:0 6:4679:1
    6:4680:0
    6:4681:0 6:4681:1
    6:4682:0 6:4682:1
    6:4683:0
    6:4684:1 6:4684:2
    6:4685:0 6:4685:1
    6:4686:1
    6:4687:0
    6:4688:0
    6:4690:0 6:4690:1
    6:4691:0 6:4691:1 6:4691:2
    6:4692:0 6:4692:1
    6:4693:0 6:4693:1
    6:4694:0 6:4694:1
    6:4695:0 6:4695:1
    6:4696:0 6:4696:1
    6:4697:0
    6:4698:0
    6:4699:0
    6:4700:0
    6:4701:0 6:4701:1
    6:4702:0 6:4702:1
    6:4703:0 6:4703:1
    6:4704:0 6:4704:1
    6:4705:0
    6:4706:0 6:4706:1
    6:4707:0 6:4707:1
    6:4708:0 6:4708:1 6:4708:2
    6:4709:0
    """.split()
)
TRANSLATIONS = {
    "6:4674:0": "많은 것을 바라지는 않습니",
    "6:4674:1": "만, 굳이 말하자면…",
    "6:4675:0": "이제야 처지를 알고",
    "6:4675:1": "는 듯",
    "6:4675:2": "…",
    "6:4676:0": "그건 더없이 반가운 이야기",
    "6:4676:1": "만\n어떤 것을",
    "6:4676:2": "것",
    "6:4676:3": "?",
    "6:4677:0": "…그 성의가 어느 정도인지는\n이 눈으로 직접 보고 판단",
    "6:4678:0": "도 계속 싸울 뜻은",
    "6:4678:1": "\n그에 걸맞은 것은 제공",
    "6:4679:0": (
        "그쪽에도 나쁘지 않은 제안일 것이오\n"
        "그 점도 고려해 주길"
    ),
    "6:4679:1": "바라오",
    "6:4680:0": "보답은 기대",
    "6:4681:0": "의 바람이 이루어지리라\n기대해도 되는 것",
    "6:4681:1": "?",
    "6:4682:0": "이 바람은 양보하지",
    "6:4682:1": "\n안 된다면 거절할 뿐입니다",
    "6:4683:0": "이 휴전안을 받아들일 것인가…\n신중히 판단",
    "6:4684:1": "」과의 전쟁은\n피하고 싶은 것",
    "6:4684:2": "만…",
    "6:4685:0": ", 이 조건으로는\n응할 수",
    "6:4685:1": "…",
    "6:4686:1": "만…",
    "6:4687:0": "음, 이 조건이라면 받아들이겠다",
    "6:4688:0": "이 정도 조건이라면\n기꺼이 받아들이겠다",
    "6:4690:0": "바람은 이루어 줄 수 없",
    "6:4690:1": "는가…",
    "6:4691:0": "대체 무엇을",
    "6:4691:1": "것",
    "6:4691:2": "인가…",
    "6:4692:0": "저, 정말 이것으로 충분한 것",
    "6:4692:1": "!",
    "6:4693:0": "이건…! 정말 괜찮은 것",
    "6:4693:1": "?\n이 정도라면 누구도 불평하지",
    "6:4694:0": ", 정말 괜찮은 것",
    "6:4694:1": "?\n이 조건을 받고도 거절하면 어리석은 짓",
    "6:4695:0": "이래서는 가신들 앞에 체면이 서지",
    "6:4695:1": "…",
    "6:4696:0": "조금만 더 고려해 줄 수 없겠",
    "6:4696:1": "는가",
    "6:4697:0": "이 정도라면 가신들도 납득할 것",
    "6:4698:0": "이 정도 조건으로 응할 리가",
    "6:4699:0": "…아니, 이 정도로는 아직 충분하지",
    "6:4700:0": "어쩔 수 없군\n이 정도라면 받아 주지",
    "6:4701:0": "설마 이것뿐일 리는",
    "6:4701:1": "?",
    "6:4702:0": ", 참으로",
    "6:4702:1": "!",
    "6:4703:0": "…!\n정말 괜찮은 것",
    "6:4703:1": "?",
    "6:4704:0": "설마 이것뿐일 리는",
    "6:4704:1": "?",
    "6:4705:0": ", 확실히 나쁜 조건은",
    "6:4706:0": "설마…\n과연 말씀하실 만",
    "6:4706:1": "!",
    "6:4707:0": "이 정도로 용서해 줄 수 없겠\n",
    "6:4707:1": "는가",
    "6:4708:0": ", 역시 충분하지",
    "6:4708:1": "는 말인가?\n그렇게 호락호락할 수는",
    "6:4708:2": "…",
    "6:4709:0": (
        "이만큼이나 요구하시다니…\n"
        "그렇다면 기한을 연장하고 싶군…"
    ),
}
STATIC_COORDINATES = {
    "6:4687:0",
    "6:4688:0",
    "6:4700:0",
    "6:4709:0",
}
DYNAMIC_COORDINATES = set(TARGET_COORDINATES) - STATIC_COORDINATES
TARGET_RECORD_IDS = (
    4674,
    4675,
    4676,
    4677,
    4678,
    4679,
    4680,
    4681,
    4682,
    4683,
    4684,
    4685,
    4686,
    4687,
    4688,
    4690,
    4691,
    4692,
    4693,
    4694,
    4695,
    4696,
    4697,
    4698,
    4699,
    4700,
    4701,
    4702,
    4703,
    4704,
    4705,
    4706,
    4707,
    4708,
    4709,
)
DYNAMIC_RECORD_IDS = tuple(
    record_id
    for record_id in TARGET_RECORD_IDS
    if record_id not in {4687, 4688, 4700, 4709}
)
EXPECTED_ARITY = {
    4674: 2,
    4675: 3,
    4676: 4,
    4677: 1,
    4678: 2,
    4679: 2,
    4680: 1,
    4681: 2,
    4682: 2,
    4683: 1,
    4684: 3,
    4685: 2,
    4686: 2,
    4687: 1,
    4688: 1,
    4690: 2,
    4691: 3,
    4692: 2,
    4693: 2,
    4694: 2,
    4695: 2,
    4696: 2,
    4697: 1,
    4698: 1,
    4699: 1,
    4700: 1,
    4701: 2,
    4702: 2,
    4703: 2,
    4704: 2,
    4705: 1,
    4706: 2,
    4707: 2,
    4708: 3,
    4709: 1,
}
PREFILL_COMPANION_COORDINATES = ("6:4684:0", "6:4686:0")
SLICE_ONLY_PREFILL_COORDINATES = ("6:4689:0",)
EXACT_SEMANTIC_DONORS = {
    "6:4686:1": ("6:4590:1",),
}
EXPECTED_BASE_MATCHES = {
    4686: ((), ((6, 4590),), ((6, 4590),)),
}
RECORD_BASE_CONTEXT = {
    4674: ("6:4594:0", "6:4594:1"),
    4675: ("6:3006:0",),
    4676: ("6:1104:0",),
    4677: ("7:856:0",),
    4678: ("6:2288:0",),
    4679: ("15:681:0",),
    4680: ("6:3560:0", "6:2934:0"),
    4681: ("6:4594:0", "6:4594:1"),
    4682: ("7:1735:0",),
    4683: ("15:246:0", "15:246:1", "15:246:2"),
    4684: ("6:642:0", "9:667:0"),
    4685: ("6:4589:0", "6:4589:1"),
    4686: ("6:4590:0", "6:4590:1"),
    4687: ("6:4591:0",),
    4688: ("6:4592:0",),
    4690: ("6:4594:0", "6:4594:1"),
    4691: ("6:4595:0", "6:4595:1"),
    4692: (),
    4693: (),
    4694: ("6:4604:0", "7:395:0"),
    4695: ("6:4602:0",),
    4696: ("6:4603:0",),
    4697: ("6:4598:0",),
    4698: ("6:4599:0",),
    4699: ("6:4596:0", "6:4600:0"),
    4700: ("6:4601:0",),
    4701: ("6:2312:0", "6:2312:1"),
    4702: (),
    4703: ("6:1385:0",),
    4704: ("6:2312:0", "6:2312:1"),
    4705: (),
    4706: (),
    4707: ("6:4603:0",),
    4708: ("6:1067:0",),
    4709: ("7:728:0",),
}
CONTEXT_RECORD_IDS = tuple(range(QUEUE_FIRST_RECORD, QUEUE_LAST_RECORD + 1))
BOUNDARY_RECORD_IDS = (
    4626,
    4627,
    4646,
    4647,
    4672,
    4673,
    4674,
    4709,
    4710,
)
SOURCE_CALL_ROOTS = (
    1,
    7,
    68,
    69,
    184,
    214,
    237,
    238,
    268,
    280,
    424,
    430,
    466,
    508,
    568,
    610,
    730,
    736,
    742,
    748,
    754,
    760,
    778,
    838,
    886,
    898,
    928,
    1036,
    1042,
    1090,
    1096,
    1144,
    1198,
)
CURRENT_CALL_ROOTS = tuple(
    root for root in SOURCE_CALL_ROOTS if root not in {430, 1036}
)
SPEAKER_STYLE = tuple(
    (record_id, "diplomatic_truce_compensation_register")
    for record_id in TARGET_RECORD_IDS
)
TERMINOLOGY_POLICY = (
    ("position", "처지"),
    ("sincerity", "성의"),
    ("truce", "휴전"),
    ("compensation", "보답"),
    ("request", "바람"),
    ("condition", "조건"),
    ("retainer", "가신"),
    ("honor before retainers", "가신들 앞의 체면"),
    ("consider", "고려하다"),
    ("accept", "받아들이다"),
    ("deadline", "기한"),
)

EXPECTED_STEAM_PK_SHA256 = (
    "DA5048695253D12373DBD1418A7B017CCEDE9E5E0E4DFC77C5293815876A0766"
)
EXPECTED_PRISTINE_PK_SHA256 = (
    "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210"
)
EXPECTED_PREFILL_SHA256 = (
    "4E1F7B18F96C9E2B1F85A2E69176A4A67B9BF53B404281A55AAD39A83FE598FD"
)
EXPECTED_BASE_PROMOTED_SHA256 = (
    "D4A16DE987E182CF616DE175E4771DA828FA4794509454263170E82ABA3600CF"
)
EXPECTED_QUEUE_UNIVERSE_SHA256 = (
    "47A93463A20C0070B55540DE326647C8E9F8F4180D74DAFF330D12729DC022C5"
)
EXPECTED_QUEUE_SLICE_SHA256 = (
    "5ACDFB4EBCE0E6C42BBFD304C72AD3B95322B9D13B20C63124312C9ECC53C7C8"
)
EXPECTED_PREFILLED_COORDINATE_SHA256 = (
    "F43201A000847F0ED9A5063E837C0BE8B77D11A761B54AA595EA20418AD27521"
)
EXPECTED_PREFILL_SLICE_CONTEXT_SHA256 = (
    "9F60BF40DAF5DA3AA97933CC7DE748DA0E54EBDEF5D334ADD14CD2AFBF3279A5"
)
EXPECTED_TARGET_COORDINATE_SHA256 = (
    "5223F06337A7EE4A70D469B3D73528775C0066369B9EE6EB0DE6D549E037EBAF"
)
EXPECTED_SOURCE_TARGET_SHA256 = (
    "355318D4901AEE29EF92DD2E416872D230507285C578B7E680722A51A870D009"
)
EXPECTED_CURRENT_TARGET_SHA256 = (
    "1ECAF4FCA8916267B59642B612B61624AEC8CA2F008FBAD44A876A28B1CA915E"
)
EXPECTED_CONTEXT_CORPUS_SHA256 = (
    "60D8FE108186AEB0F5C5F8C01896DC8B793BADB4CA5AB82AEF33B36A2F1E2DC0"
)
EXPECTED_GAP_CONTRACT_SHA256 = (
    "B084032B32D679838A35C6669E647B74F7F79468665F05EF362EEF4090619A14"
)
EXPECTED_BOUNDARY_SHA256 = (
    "5ACE748CC088785227E5851ED64B5D77230B2E619FAAF1ACE890995F6D0B1D07"
)
EXPECTED_RUNTIME_CONTROL_SHA256 = (
    "572B7653D47EF045B132B1284E94C89A6A374DC72D7064AEAC9F5A9EFCA65290"
)
EXPECTED_BASE_SEARCH_SHA256 = (
    "4B525B22DD3B19060A5A2062084CE0C607C411B8FA03515FEAF1FB2ABBB61FC0"
)
EXPECTED_COMPLETE_ASSEMBLY_SHA256 = (
    "F9CD600BF68825D760D2DD54B0BC2007D45207728C05A727C9A07A837F3BEF1C"
)
EXPECTED_CALL_GRAPH_SHA256 = (
    "F217CDB980DD6E8AB933B902AD9DD593B51740CA828BF092333D69079064A793"
)
EXPECTED_SPEAKER_STYLE_SHA256 = (
    "F3C14108E8465F460D6E398C9EA0CE3EB10609B92C2A0430802CE4D8ED2D984D"
)
EXPECTED_TERMINOLOGY_POLICY_SHA256 = (
    "1864B5AAB3F0378A3460A7DF368F4DD4C599DEFC626FE4EECB727DDA9E9E3FF3"
)
EXPECTED_TRANSLATION_POLICY_SHA256 = (
    "E1383BAD178B11C076552F4FA309C0E34716934D726032542F6045E149C8AA37"
)
EXPECTED_CANDIDATE_SHA256 = (
    "E36D0279DB9762833E73C7A54F792D108338B76D0D62AC32F5D275EF38DAB5C8"
)
EXPECTED_CHANGED_LITERAL_COUNT = 56

BASIS = (
    "pristine PK PC source authoritative; current Korean and complete PC "
    "EN SC TC records across the full B048 queue are context only; all "
    "thirty-five complete target records are reviewed as PK multilingual "
    "assemblies; the complete promoted Base corpus is searched, one "
    "literal-and-operand-masked Base source record is pinned only as a "
    "semantic donor because its live call operand differs, and relevant "
    "truce, compensation, condition, acceptance, rejection and retainer "
    "honor rows are semantic wording context; all sixty-three targets and "
    "two same-record prefill companions form thirty-five complete records, "
    "while the third prefill is a separately complete queue record; "
    "diplomatic terminology and historically suitable officer register are "
    "reviewed; dynamic people, parties, calls, particles, punctuation, "
    "protected outer whitespace, line counts, pristine and current call "
    "graphs, the three intentionally flattened current call sites, runtime "
    "gaps, reverse-order overlay, reverse restoration, two-run "
    "reproduction, tamper rejection, outside-scope identity and Steam "
    "read-only state are guarded; fifty-six translations change and seven "
    "already match the reviewed wording; Base runtime verification is not "
    "inherited and every dynamic PK fragment remains runtime pending"
)


def load_template() -> Any:
    spec = importlib.util.spec_from_file_location(
        "pc_dialogue_full_retranslation_v0150_pk_s1157_template",
        TEMPLATE_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {TEMPLATE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


TEMPLATE = load_template()
ENGINE = TEMPLATE.ENGINE
sha256_bytes = TEMPLATE.sha256_bytes
canonical_sha256 = TEMPLATE.canonical_sha256
coordinate_key = TEMPLATE.coordinate_key
literal_texts = TEMPLATE.literal_texts
gap_bytes = TEMPLATE.gap_bytes
read_jsonl = TEMPLATE.read_jsonl
context_records = TEMPLATE.context_records
runtime_controls = TEMPLATE.runtime_controls
mask_call_operands = TEMPLATE.mask_call_operands


def patch_template_globals() -> None:
    values = {
        "SCRIPT": SCRIPT,
        "OUTPUT": OUTPUT,
        "PREFILL": PREFILL,
        "BASE_PROMOTED": BASE_PROMOTED,
        "SEGMENT": SEGMENT,
        "QUEUE_BATCH_ID": QUEUE_BATCH_ID,
        "QUEUE_START": QUEUE_START,
        "QUEUE_STOP": QUEUE_STOP,
        "BLOCK_ID": BLOCK_ID,
        "PK_RECORD_COUNT": PK_RECORD_COUNT,
        "TARGET_COORDINATES": TARGET_COORDINATES,
        "TRANSLATIONS": TRANSLATIONS,
        "DYNAMIC_COORDINATES": DYNAMIC_COORDINATES,
        "STATIC_COORDINATES": STATIC_COORDINATES,
        "TARGET_RECORD_IDS": TARGET_RECORD_IDS,
        "DYNAMIC_RECORD_IDS": DYNAMIC_RECORD_IDS,
        "EXPECTED_ARITY": EXPECTED_ARITY,
        "CONTEXT_RECORD_IDS": CONTEXT_RECORD_IDS,
        "BOUNDARY_RECORD_IDS": BOUNDARY_RECORD_IDS,
        "SOURCE_CALL_ROOTS": SOURCE_CALL_ROOTS,
        "CURRENT_CALL_ROOTS": CURRENT_CALL_ROOTS,
        "EXPECTED_CHANGED_LITERAL_COUNT": EXPECTED_CHANGED_LITERAL_COUNT,
        "EXPECTED_CANDIDATE_SHA256": EXPECTED_CANDIDATE_SHA256,
        "EXPECTED_TRANSLATION_POLICY_SHA256":
        EXPECTED_TRANSLATION_POLICY_SHA256,
    }
    for name, value in values.items():
        setattr(TEMPLATE, name, value)
    TEMPLATE.patch_template_globals()


def guarded_digest(label: str, value: Any, expected: str) -> str:
    actual = canonical_sha256(value)
    if actual != expected:
        raise RuntimeError(f"segment {SEGMENT} {label} drifted: {actual}")
    return actual


def queue_evidence(
    prepared: Any,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[Any, ...],
]:
    queue_rows = [
        json.loads(line)
        for line in prepared.queue.splitlines()
        if line and json.loads(line).get("batch_id") == QUEUE_BATCH_ID
    ]
    visible = tuple(
        str(target["coordinate"])
        for row in queue_rows
        for target in row["target_literals"]
        if target["visible"]
    )
    if (
        len(queue_rows) != 83
        or len(visible) != 200
        or visible[0] != "6:4627:0"
        or visible[-1] != "6:4709:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} B048 queue universe drifted")
    queue_slice = visible[QUEUE_START:QUEUE_STOP]
    if (
        len(queue_slice) != 66
        or queue_slice[0] != "6:4674:0"
        or queue_slice[-1] != "6:4709:0"
    ):
        raise RuntimeError(f"segment {SEGMENT} queue bounds drifted")
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    prefilled = tuple(
        coordinate for coordinate in queue_slice if coordinate in prefill_rows
    )
    if prefilled != (
        "6:4684:0",
        "6:4686:0",
        "6:4689:0",
    ):
        raise RuntimeError(f"segment {SEGMENT} prefill slice drifted")
    prefill_context = tuple(
        (
            coordinate,
            str(prefill_rows[coordinate]["translation"]),
            str(prefill_rows[coordinate]["source_record_raw_sha256"]),
            str(prefill_rows[coordinate]["current_ko_utf16le_sha256"]),
            str(prefill_rows[coordinate]["semantic_review"]),
            str(prefill_rows[coordinate]["runtime_review"]),
            str(prefill_rows[coordinate]["layout_review"]),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "base_coordinate"
                ]
            ),
            str(
                prefill_rows[coordinate]["base_exact_reuse_prefill"][
                    "translation_utf16le_sha256"
                ]
            ),
        )
        for coordinate in prefilled
    )
    return visible, queue_slice, prefilled, prefill_context


def assert_queue_and_residual_contract(prepared: Any) -> tuple[str, ...]:
    if (
        sha256_bytes(PREFILL.read_bytes()) != EXPECTED_PREFILL_SHA256
        or sha256_bytes(ENGINE.DEFAULT_PK_PRISTINE.read_bytes())
        != EXPECTED_PRISTINE_PK_SHA256
    ):
        raise RuntimeError(f"segment {SEGMENT} pinned source input drifted")
    ENGINE.validate_decisions(prepared, PREFILL, require_complete=False)
    visible, queue_slice, prefilled, prefill_context = queue_evidence(prepared)
    guarded_digest("queue universe", visible, EXPECTED_QUEUE_UNIVERSE_SHA256)
    guarded_digest("queue slice", queue_slice, EXPECTED_QUEUE_SLICE_SHA256)
    guarded_digest(
        "prefilled coordinate",
        prefilled,
        EXPECTED_PREFILLED_COORDINATE_SHA256,
    )
    guarded_digest(
        "prefill slice context",
        prefill_context,
        EXPECTED_PREFILL_SLICE_CONTEXT_SHA256,
    )
    existing: dict[str, str] = {}
    for path in sorted(
        DECISIONS_ROOT.glob("pk_msggame_*.private.v1.jsonl")
    ):
        if path.resolve(strict=False) == OUTPUT.resolve(strict=False):
            continue
        ENGINE.validate_decisions(prepared, path, require_complete=False)
        for row in read_jsonl(path):
            coordinate = row.get("coordinate")
            if (
                row.get("resource") != "pk_msggame"
                or not isinstance(coordinate, str)
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} mixed predecessor: {path}"
                )
            previous = existing.setdefault(coordinate, path.name)
            if previous != path.name:
                raise RuntimeError(
                    f"segment {SEGMENT} duplicate predecessor: {coordinate}"
                )
    residual = tuple(
        coordinate for coordinate in queue_slice if coordinate not in existing
    )
    if residual != TARGET_COORDINATES:
        raise RuntimeError(
            f"segment {SEGMENT} residual queue drifted: {len(residual)} rows"
        )
    optional_present: list[str] = []
    for path in OPTIONAL_NEIGHBORS:
        if path.is_file():
            ENGINE.validate_decisions(prepared, path, require_complete=False)
            optional_present.append(path.name)
    return tuple(optional_present)


def context_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> dict[str, Any]:
    patch_template_globals()
    return TEMPLATE.context_evidence(records_by_label)


def assert_context_contracts(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    values = context_evidence(records_by_label)
    for label, value, expected in (
        ("source target", values["source_target"], EXPECTED_SOURCE_TARGET_SHA256),
        ("current target", values["current_target"], EXPECTED_CURRENT_TARGET_SHA256),
        ("multilingual context", values["corpus"], EXPECTED_CONTEXT_CORPUS_SHA256),
        ("gap contract", values["gaps"], EXPECTED_GAP_CONTRACT_SHA256),
        ("boundary", values["boundary"], EXPECTED_BOUNDARY_SHA256),
        ("runtime control", values["controls"], EXPECTED_RUNTIME_CONTROL_SHA256),
    ):
        guarded_digest(label, value, expected)
    mismatched_gap_records = tuple(
        record_id
        for record_id, source, current in values["gaps"]
        if source != current
    )
    if (
        mismatched_gap_records != (4687, 4688, 4700)
        or any(
            ("pk_msggame", *coordinate_key(coordinate))
            not in prepared.visible_targets
            for coordinate in TARGET_COORDINATES
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} runtime layout drifted")


def base_and_assembly_evidence(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[tuple[Any, ...], tuple[Any, ...]]:
    base_source = ENGINE.archive_records(
        prepared.resources["base_msggame"].pristine_archive
    )
    base_rows = {
        str(row["coordinate"]): row for row in read_jsonl(BASE_PROMOTED)
    }
    prefill_rows = {
        str(row["coordinate"]): row for row in read_jsonl(PREFILL)
    }
    literal_index: dict[tuple[str, ...], list[tuple[int, int]]] = {}
    masked_index: dict[
        tuple[tuple[str, ...], tuple[str, ...]],
        list[tuple[int, int]],
    ] = {}
    raw_index: dict[bytes, list[tuple[int, int]]] = {}
    for key, record in base_source.items():
        literals = literal_texts(base_source, key)
        raw_index.setdefault(record.data, []).append(key)
        literal_index.setdefault(literals, []).append(key)
        masked_index.setdefault(
            (literals, mask_call_operands(record)),
            [],
        ).append(key)
    base_evidence: list[tuple[Any, ...]] = []
    assembly_evidence: list[tuple[Any, ...]] = []
    seen_target: set[str] = set()
    seen_prefill: set[str] = set()
    for record_id in TARGET_RECORD_IDS:
        key = (BLOCK_ID, record_id)
        source = records_by_label["jp"][key]
        source_literals = literal_texts(records_by_label["jp"], key)
        current_literals = literal_texts(records_by_label["current"], key)
        raw_matches = tuple(raw_index.get(source.data, ()))
        literal_matches = tuple(literal_index.get(source_literals, ()))
        masked_matches = tuple(
            masked_index.get(
                (source_literals, mask_call_operands(source)),
                (),
            )
        )
        expected_matches = EXPECTED_BASE_MATCHES.get(
            record_id,
            ((), (), ()),
        )
        if (
            len(source_literals) != EXPECTED_ARITY[record_id]
            or (
                raw_matches,
                literal_matches,
                masked_matches,
            )
            != expected_matches
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base search drifted: {record_id}"
            )
        context_rows: list[tuple[Any, ...]] = []
        for reference in RECORD_BASE_CONTEXT[record_id]:
            row = base_rows.get(reference)
            if (
                row is None
                or row.get("semantic_review") != "approved"
                or row.get("runtime_review")
                not in {"verified", "not_required"}
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} missing Base context: {reference}"
                )
            context_rows.append(
                (
                    reference,
                    str(row.get("translation", "")),
                    str(row["semantic_review"]),
                    str(row["runtime_review"]),
                )
            )
        owners: list[str] = []
        translations: list[str] = []
        literal_evidence: list[tuple[Any, ...]] = []
        for literal_id in range(EXPECTED_ARITY[record_id]):
            coordinate = f"6:{record_id}:{literal_id}"
            references = EXACT_SEMANTIC_DONORS.get(
                coordinate,
                RECORD_BASE_CONTEXT[record_id],
            )
            if coordinate in TRANSLATIONS:
                actual = TRANSLATIONS[coordinate]
                owner = "segment"
                seen_target.add(coordinate)
                if coordinate in EXACT_SEMANTIC_DONORS:
                    donor = base_rows[references[0]]
                    if actual != str(donor["translation"]):
                        raise RuntimeError(
                            f"segment {SEGMENT} semantic donor drifted"
                        )
            else:
                prefill_row = prefill_rows.get(coordinate)
                if prefill_row is None:
                    raise RuntimeError(
                        f"segment {SEGMENT} missing prefill companion: "
                        f"{coordinate}"
                    )
                actual = str(prefill_row["translation"])
                owner = "prefill"
                references = (
                    str(
                        prefill_row["base_exact_reuse_prefill"][
                            "base_coordinate"
                        ]
                    ),
                )
                donor = base_rows.get(references[0])
                if donor is None or actual != str(donor["translation"]):
                    raise RuntimeError(
                        f"segment {SEGMENT} prefill Base donor drifted"
                    )
                seen_prefill.add(coordinate)
            owners.append(owner)
            translations.append(actual)
            literal_evidence.append(
                (coordinate, owner, references, actual)
            )
        base_evidence.append(
            (
                record_id,
                sha256_bytes(source.data),
                source_literals,
                current_literals,
                tuple(
                    value.hex().upper() for value in gap_bytes(source)
                ),
                raw_matches,
                literal_matches,
                masked_matches,
                tuple(context_rows),
                tuple(literal_evidence),
            )
        )
        assembly_evidence.append(
            (
                record_id,
                tuple(owners),
                tuple(translations),
                runtime_controls(source),
                runtime_controls(records_by_label["current"][key]),
                "manual_multilingual_pk_only",
            )
        )
    if (
        seen_target != set(TARGET_COORDINATES)
        or seen_prefill != set(PREFILL_COMPANION_COORDINATES)
    ):
        raise RuntimeError(f"segment {SEGMENT} assembly ownership drifted")
    return tuple(base_evidence), tuple(assembly_evidence)


def assert_base_and_complete_assembly(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    if sha256_bytes(BASE_PROMOTED.read_bytes()) != EXPECTED_BASE_PROMOTED_SHA256:
        raise RuntimeError(f"segment {SEGMENT} Base promoted input drifted")
    base, assembly = base_and_assembly_evidence(prepared, records_by_label)
    guarded_digest("Base search", base, EXPECTED_BASE_SEARCH_SHA256)
    guarded_digest(
        "complete assembly",
        assembly,
        EXPECTED_COMPLETE_ASSEMBLY_SHA256,
    )


def call_graph_evidence(prepared: Any) -> tuple[Any, ...]:
    patch_template_globals()
    return TEMPLATE.call_graph_evidence(prepared)


def assert_call_graphs(prepared: Any) -> None:
    guarded_digest(
        "call graph",
        call_graph_evidence(prepared),
        EXPECTED_CALL_GRAPH_SHA256,
    )


def assert_semantics(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    guarded_digest(
        "target coordinate",
        TARGET_COORDINATES,
        EXPECTED_TARGET_COORDINATE_SHA256,
    )
    guarded_digest(
        "translation policy",
        tuple(TRANSLATIONS.items()),
        EXPECTED_TRANSLATION_POLICY_SHA256,
    )
    guarded_digest(
        "speaker style",
        SPEAKER_STYLE,
        EXPECTED_SPEAKER_STYLE_SHA256,
    )
    guarded_digest(
        "terminology policy",
        TERMINOLOGY_POLICY,
        EXPECTED_TERMINOLOGY_POLICY_SHA256,
    )
    if (
        tuple(TRANSLATIONS) != TARGET_COORDINATES
        or DYNAMIC_COORDINATES | STATIC_COORDINATES
        != set(TARGET_COORDINATES)
        or DYNAMIC_COORDINATES & STATIC_COORDINATES
        or ENGINE.KANA_OR_HAN_RE.search(SCRIPT.read_text(encoding="utf-8"))
    ):
        raise RuntimeError(f"segment {SEGMENT} semantic policy drifted")
    for coordinate, translation in TRANSLATIONS.items():
        key = coordinate_key(coordinate)
        current_text = literal_texts(
            records_by_label["current"],
            key[:2],
        )[key[2]]
        ENGINE.validate_translation_shape(
            current_text,
            translation,
            (
                "runtime_pending"
                if coordinate in DYNAMIC_COORDINATES
                else "unchanged_from_current"
            ),
            coordinate,
        )
        if (
            translation.count("\n") != current_text.count("\n")
            or ENGINE.protected_signature(translation)
            != ENGINE.protected_signature(current_text)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} shape drifted: {coordinate}"
            )


def unchecked_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_template_globals()
    return TEMPLATE.unchecked_candidate(prepared, records_by_label)


def build_candidate(
    prepared: Any,
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> tuple[bytes, str, int]:
    patch_template_globals()
    return TEMPLATE.build_candidate(prepared, records_by_label)


def runtime_evidence(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
    record_id: int,
) -> dict[str, Any]:
    source = records_by_label["jp"][(BLOCK_ID, record_id)]
    current = records_by_label["current"][(BLOCK_ID, record_id)]
    source_controls = runtime_controls(source)
    current_controls = runtime_controls(current)
    return {
        "runtime_category": dict(SPEAKER_STYLE)[record_id],
        "source_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(source))
        ),
        "current_record_gap_sha256": canonical_sha256(
            tuple(value.hex().upper() for value in gap_bytes(current))
        ),
        "source_direct_call_operands": source_controls[0],
        "current_direct_call_operands": current_controls[0],
        "source_inline_token_hex": source_controls[1],
        "current_inline_token_hex": current_controls[1],
        "source_current_runtime_gap_equal":
        gap_bytes(source) == gap_bytes(current),
        "base_complete_record_match_kind": (
            "literal_and_operand_masked_semantic_only"
            if record_id == 4686
            else "none"
        ),
        "source_and_current_call_graphs_reviewed": True,
        "complete_record_assembly_reviewed": True,
        "same_record_prefill_companions_reviewed":
        record_id in {4684, 4686},
        "manual_multilingual_context_reviewed": True,
        "completed_base_context_reviewed": True,
        "protected_outer_whitespace_preserved": True,
        "speaker_register_reviewed": True,
        "historical_terminology_reviewed": True,
        "base_runtime_state_inherited": False,
        "automatic_space_inserted": False,
        "pk_vm_specific_review_required": True,
        "runtime_review_required": True,
        "runtime_promotion_authorized": False,
    }


def build_rows() -> tuple[
    Any,
    list[dict[str, Any]],
    bytes,
    str,
    int,
    tuple[str, ...],
]:
    patch_template_globals()
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    optional_present = assert_queue_and_residual_contract(prepared)
    records = context_records(prepared)
    assert_context_contracts(prepared, records)
    assert_base_and_complete_assembly(prepared, records)
    assert_call_graphs(prepared)
    assert_semantics(records)
    candidate, candidate_sha256, changed = build_candidate(
        prepared,
        records,
    )
    rows: list[dict[str, Any]] = []
    style_map = dict(SPEAKER_STYLE)
    for coordinate in TARGET_COORDINATES:
        block_id, record_id, literal_id = coordinate_key(coordinate)
        dynamic = coordinate in DYNAMIC_COORDINATES
        current_text = literal_texts(
            records["current"],
            (block_id, record_id),
        )[literal_id]
        target = prepared.visible_targets[
            ("pk_msggame", block_id, record_id, literal_id)
        ]
        references = EXACT_SEMANTIC_DONORS.get(
            coordinate,
            RECORD_BASE_CONTEXT[record_id],
        )
        row: dict[str, Any] = {
            "schema": ENGINE.DECISION_SCHEMA,
            "resource": "pk_msggame",
            "coordinate": coordinate,
            "source_record_raw_sha256":
            target["source_record_raw_sha256"],
            "current_ko_utf16le_sha256":
            target["current_ko_utf16le_sha256"],
            "translation": TRANSLATIONS[coordinate],
            "semantic_review": "approved",
            "scope_classification": (
                "runtime_fragment_pending" if dynamic else "retranslated"
            ),
            "layout_review": (
                "runtime_pending" if dynamic else "unchanged_from_current"
            ),
            "runtime_review": (
                "pending" if dynamic else "not_required"
            ),
            "basis": BASIS,
            "historic_korean_used": False,
            "switch_korean_used": False,
            "base_exact_reuse_prefill_excluded": True,
            "all_available_predecessors_validated": True,
            "optional_neighbor_outputs_validated_if_present": True,
            "manual_multilingual_context_review": True,
            "adjacent_record_context_review": True,
            "complete_record_fragment_review": True,
            "prefill_companions_reviewed":
            record_id in {4684, 4686},
            "speaker_register_reviewed": True,
            "historical_terminology_reviewed": True,
            "protected_outer_whitespace_preserved": True,
            "completed_base_corpus_searched": True,
            "base_context_reference_coordinate":
            references[0] if references else None,
            "base_context_reference_coordinates": references,
            "base_context_is_automatic_reuse": False,
            "base_wording_contextually_adapted":
            coordinate not in EXACT_SEMANTIC_DONORS,
            "base_runtime_state_inherited": False,
            "speaker_style": style_map[record_id],
            "line_count_before": current_text.count("\n") + 1,
            "line_count_after":
            TRANSLATIONS[coordinate].count("\n") + 1,
            "line_count_preserved": True,
        }
        if dynamic:
            row["runtime_assembly_evidence"] = (
                runtime_evidence(records, record_id)
            )
        rows.append(row)
    return (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    )


def assert_tamper_rejection(
    prepared: Any,
    rows: list[dict[str, Any]],
    candidate: bytes,
) -> None:
    patch_template_globals()
    TEMPLATE.assert_tamper_rejection(prepared, rows, candidate)


def main() -> int:
    first = build_rows()
    second = build_rows()
    (
        prepared,
        rows,
        candidate,
        candidate_sha256,
        changed,
        optional_present,
    ) = first
    if (
        ENGINE.jsonl(rows) != ENGINE.jsonl(second[1])
        or candidate != second[2]
        or candidate_sha256 != second[3]
        or changed != second[4]
        or optional_present != second[5]
    ):
        raise RuntimeError(f"segment {SEGMENT} second-run reproduction drifted")
    steam_before = sha256_bytes(STEAM_PK.read_bytes())
    if steam_before != EXPECTED_STEAM_PK_SHA256:
        raise RuntimeError(
            f"segment {SEGMENT} Steam input drifted: {steam_before}"
        )
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    counts = Counter(
        str(row["scope_classification"]) for row in rows
    )
    if (
        len(rows) != 63
        or len(validated) != 63
        or counts
        != Counter(
            {
                "runtime_fragment_pending": 59,
                "retranslated": 4,
            }
        )
        or any(
            row["semantic_review"] != "approved"
            or row["historic_korean_used"] is not False
            or row["switch_korean_used"] is not False
            or row["base_runtime_state_inherited"] is not False
            or row["line_count_preserved"] is not True
            for row in rows
        )
        or any(
            row["runtime_review"] != "pending"
            or row["layout_review"] != "runtime_pending"
            or row["runtime_assembly_evidence"][
                "runtime_promotion_authorized"
            ]
            is not False
            for row in rows
            if row["scope_classification"] == "runtime_fragment_pending"
        )
        or any(
            row["runtime_review"] != "not_required"
            or row["layout_review"] != "unchanged_from_current"
            for row in rows
            if row["scope_classification"] == "retranslated"
        )
    ):
        raise RuntimeError(f"segment {SEGMENT} decision validation drifted")
    assert_tamper_rejection(prepared, rows, candidate)
    steam_after = sha256_bytes(STEAM_PK.read_bytes())
    if steam_after != steam_before:
        raise RuntimeError(f"segment {SEGMENT} wrote to Steam input")
    print(
        json.dumps(
            {
                "status": "ok",
                "segment": "pk_msggame_B048_S1157",
                "queue": QUEUE_BATCH_ID,
                "queue_zero_based_ordinals":
                [QUEUE_START, QUEUE_STOP - 1],
                "decision_count": len(rows),
                "scope_classification_counts": dict(counts),
                "queue_slice_visible_count": 66,
                "exact_reuse_prefill_count": 3,
                "residual_count": len(rows),
                "reviewed_complete_record_count":
                len(TARGET_RECORD_IDS),
                "same_record_prefill_companion_count":
                len(PREFILL_COMPANION_COORDINATES),
                "slice_only_prefill_count":
                len(SLICE_ONLY_PREFILL_COORDINATES),
                "literal_masked_semantic_donor_record_count":
                len(EXPECTED_BASE_MATCHES),
                "source_call_root_count": len(SOURCE_CALL_ROOTS),
                "current_call_root_count": len(CURRENT_CALL_ROOTS),
                "optional_neighbors_present": list(optional_present),
                "changed_literal_count": changed,
                "candidate_sha256": candidate_sha256,
                "translation_policy_sha256":
                EXPECTED_TRANSLATION_POLICY_SHA256,
                "decision_sha256": sha256_bytes(OUTPUT.read_bytes()),
                "builder_sha256": sha256_bytes(SCRIPT.read_bytes()),
                "source_and_current_hashes_guarded": True,
                "all_available_predecessors_validated": True,
                "optional_new_outputs_only": True,
                "completed_base_corpus_searched": True,
                "base_runtime_state_inherited": False,
                "queue_boundaries_guarded": True,
                "all_prefills_guarded": True,
                "same_record_prefill_companions_guarded": True,
                "complete_multi_literal_records_guarded": True,
                "source_and_current_call_graphs_guarded": True,
                "inline_runtime_tokens_guarded": True,
                "protected_outer_whitespace_guarded": True,
                "speaker_register_guarded": True,
                "historical_terminology_guarded": True,
                "outside_scope_records_exact": True,
                "current_runtime_gaps_exact": True,
                "protected_signatures_exact": True,
                "line_counts_preserved": True,
                "reverse_order_overlay_exact": True,
                "reverse_overlay_exact": True,
                "second_run_reproduction_exact": True,
                "tamper_tests_passed": True,
                "tracked_builder_source_redacted": True,
                "runtime_promotion_authorized": False,
                "steam_read_only": True,
                "steam_write_performed": False,
                "input_root": str(ENGINE.DEFAULT_STEAM_ROOT),
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
