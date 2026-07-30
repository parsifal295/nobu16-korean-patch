#!/usr/bin/env python3
"""Close Korean sentences in direct-render ``msggame.bin`` records.

These records contain no selector, call, or jump.  The Japanese source often
ends a line in a continuative form, but that form is not completed elsewhere
at runtime.  Translating it as a Korean bare stem therefore exposes text such
as ``건설하`` or ``도움이 될 것`` verbatim.

The coordinate pairs below cover the shared Base/PK records found by the
direct-render audit.  Every replacement is predecessor-pinned, preserves the
record's non-literal bytes, and is followed by an archive-wide bare-stem gate.
"""

from __future__ import annotations

import hashlib
import sys
import unicodedata
from pathlib import Path
from typing import Any, Mapping


SCRIPT = Path(__file__).resolve()
REPO = SCRIPT.parents[2]
sys.path.insert(0, str(REPO / "workstreams" / "msggame"))

from msggame_format import (  # noqa: E402
    MsgGameRecord,
    parse_packed_msggame,
    parse_record_literals,
    rebuild_packed_with_literals,
)


class DirectStaticClosureError(ValueError):
    """Raised when a direct-render sentence-closure invariant drifts."""


RewriteMap = dict[tuple[int, int, int], tuple[str, str]]
BASE_REWRITES: RewriteMap = {}
PK_REWRITES: RewriteMap = {}


def add_pair(
    base: tuple[int, int],
    pk: tuple[int, int],
    literal_id: int,
    before: str,
    after: str,
) -> None:
    BASE_REWRITES[(*base, literal_id)] = (before, after)
    PK_REWRITES[(*pk, literal_id)] = (before, after)


def add_base(
    coordinate: tuple[int, int, int],
    before: str,
    after: str,
) -> None:
    BASE_REWRITES[coordinate] = (before, after)


def add_pk(
    coordinate: tuple[int, int, int],
    before: str,
    after: str,
) -> None:
    PK_REWRITES[coordinate] = (before, after)


add_pair(
    (2, 557),
    (2, 574),
    0,
    "배웅해 주셔서 감사하",
    "배웅해 주셔서 감사하오",
)
add_pair(
    (6, 2378),
    (6, 2384),
    0,
    "어렵군요…\n그쪽에 큰 기대를 하기도 어려운 듯하고",
    "어렵군요……\n그쪽에 큰 기대를 걸기도 어려워 보입니다",
)
add_pair(
    (6, 3531),
    (6, 3538),
    0,
    "훈공의 선두에 서게 되다니\n더없는 영광으로 여기",
    "훈공의 선두에 서게 되다니\n더없는 영광입니다",
)
add_pair(
    (6, 3531),
    (6, 3538),
    1,
    "\n앞으로도 우리 가문을 더욱 융성케 하",
    "\n앞으로도 우리 가문을 더욱 융성하게 하겠습니다!",
)
add_pk(
    (6, 3562, 0),
    "경사로다, 경사로다\n앞으로도 부탁하",
    "경사로다, 경사로다\n앞으로도 잘 부탁하네",
)
add_pair(
    (6, 4146),
    (6, 4176),
    0,
    "영내의 병력이 줄어들고 있어\n병력 확보를 추진해",
    "영내의 병력이 줄어들고 있어\n병력 확보를 추진하고 있습니다",
)
add_pair(
    (6, 4150),
    (6, 4180),
    0,
    "주변에 공략할 수 있는 성이 없어\n영지 발전에 힘써",
    "주변에 공략할 수 있는 성이 없어\n영지 발전에 힘쓰고 있습니다",
)
add_pair(
    (6, 4151),
    (6, 4181),
    0,
    "주변에 공략할 수 있는 성이 없어\n영내 발전에 주력하",
    "주변에 공략할 수 있는 성이 없어\n영내 발전에 주력하고 있으며",
)
add_pair(
    (6, 4151),
    (6, 4181),
    1,
    "\n이미 모든 취락을 장악하",
    "\n이미 모든 취락을 장악했습니다",
)
add_pair(
    (6, 4171),
    (6, 4201),
    0,
    "우리 군단에서\n일부 부대를 파견하",
    "우리 군단에서\n일부 부대를 파견했습니다",
)
add_base(
    (6, 4179, 0),
    ", 알겠",
    "예, 알겠습니다",
)
add_base(
    (6, 4179, 1),
    "\n우리 가문을 위해 주명을 완수하도록\n전력을 다하",
    "\n우리 가문을 위해 주명을 완수하도록\n전력을 다하겠습니다",
)
for base_record, pk_record, before, after in (
    (
        4186,
        4216,
        "적성에 대한 조략을\n검토하도록 지시하",
        "적성에 대한 조략을\n검토하도록 지시했습니다",
    ),
    (
        4187,
        4217,
        "강한 불만을 품은 무장에게\n우리 가문으로 돌아서도록 권유하",
        "강한 불만을 품은 무장에게\n우리 가문으로 돌아서도록 권유했습니다",
    ),
    (
        4188,
        4218,
        "유사시에 원군을 요청할 수 있도록\n국인중을 회유하",
        "유사시에 원군을 요청할 수 있도록\n국인중을 회유했습니다",
    ),
    (
        4189,
        4219,
        "국인중을 우리 가문의 산하에\n편입하도록 지시하",
        "국인중을 우리 가문의 산하에\n편입하도록 지시했습니다",
    ),
    (
        4190,
        4220,
        "적 영지의 백성을 선동해\n잇키를 일으켜 움직임을 봉쇄하",
        "적 영지의 백성을 선동해\n잇키를 일으켜 움직임을 봉쇄했습니다",
    ),
    (
        4192,
        4222,
        "가보를 마련해\n외교 자세를 개선하",
        "가보를 마련해\n외교 자세를 개선했습니다",
    ),
    (
        4195,
        4225,
        "석고를 늘리기 위해\n농촌을 장악하",
        "석고를 늘리기 위해\n농촌을 장악했습니다",
    ),
    (
        4196,
        4226,
        "금전 수입을 늘리기 위해\n상업을 진흥하",
        "금전 수입을 늘리기 위해\n상업을 진흥했습니다",
    ),
    (
        4197,
        4227,
        "침공에 대비해 외벽 수복을 명하고\n성의 내구를 회복하",
        "침공에 대비해 외벽 수복을 명하고\n성의 내구를 회복했습니다",
    ),
    (
        4198,
        4228,
        "세력 내 유망한 낭인을\n찾아내 등용하",
        "세력 내 유망한 낭인을\n찾아내 등용했습니다",
    ),
    (
        4224,
        4254,
        "조정과의 교섭을\n중단하",
        "조정과의 교섭을\n중단했습니다",
    ),
):
    add_pair(
        (6, base_record),
        (6, pk_record),
        0,
        before,
        after,
    )
add_pair(
    (7, 262),
    (7, 266),
    0,
    "권유에 감사",
    "권유에 감사하오",
)
add_pair(
    (7, 262),
    (7, 266),
    1,
    "\n포박의 치욕을\n공을 세워 씻어 내 보이",
    "\n포박의 치욕을\n공을 세워 씻어 내 보이겠소",
)
add_pair(
    (7, 2766),
    (7, 2832),
    0,
    "……목숨을 바칠 만한 주군도 아니다\n모두, 철수하",
    "……목숨을 바칠 만한 주군도 아니다\n모두, 철수하라!",
)


STATIC_FAMILIES = (
    (
        1033,
        1045,
        (
            ("교역항이 완성되", "교역항이 완성되어"),
            (
                "\n곧바로 각지에서 배가 모여들어\n크게 붐비",
                "\n곧바로 각지에서 배가 모여들어\n크게 붐빕니다",
            ),
        ),
    ),
    (
        1034,
        1046,
        (
            ("금산 마을을 건설하", "금산 마을을 건설하여"),
            (
                "\n새로운 수입원을 얻은 덕분에\n우리 가문의 재정도 넉넉해지",
                "\n새로운 수입원을 얻은 덕분에\n우리 가문의 재정도 넉넉해졌습니다",
            ),
        ),
    ),
    (
        1035,
        1047,
        (
            ("은산 마을을 건설하", "은산 마을을 건설하여"),
            (
                "\n우리 가문의 새 수입원이 되어\n영내는 더욱 발전할 것",
                "\n우리 가문의 새 수입원이 되어\n영내는 더욱 발전할 것입니다",
            ),
        ),
    ),
    (
        1036,
        1048,
        (
            ("마목장을 건설하", "마목장을 건설하여"),
            (
                "\n이로써 많은 준마가 자라나\n기병도 한층 정예해질 것",
                "\n이로써 많은 준마가 자라나\n기병도 한층 정예해질 것입니다",
            ),
        ),
    ),
    (
        1037,
        1049,
        (
            ("대장간 마을을 건설하", "대장간 마을을 건설하여"),
            (
                "\n철포를 충분히 갖출 수 있게 되어\n전장에서도 마음껏 활용할 수 있을 듯",
                "\n철포를 충분히 갖출 수 있게 되어\n전장에서도 마음껏 활용할 수 있습니다",
            ),
        ),
    ),
    (
        1038,
        1050,
        (
            ("절을 건설하", "절을 건설하여"),
            (
                "\n백성들이 마음을 기댈 곳이 되어\n승려들도 기쁨을 감추지 못하는 듯 보이",
                "\n백성들이 마음을 기댈 곳이 되어\n승려들도 기쁨을 감추지 못하는 듯합니다",
            ),
        ),
    ),
    (
        1039,
        1051,
        (
            ("남만사를 건설하", "남만사를 건설하여"),
            (
                "\n포교가 진전됨에 따라\n새로운 문화가 뿌리내릴지도……",
                "\n포교가 진전됨에 따라\n새로운 문화가 뿌리내릴지도 모릅니다……",
            ),
        ),
    ),
    (
        1040,
        1052,
        (
            ("온천향을 건설하", "온천향을 건설하여"),
            (
                "\n아무래도 부상 치료에 효험이 있어\n병사들의 요양에도 도움이 될 것",
                "\n아무래도 부상 치료에 효험이 있어\n병사들의 요양에도 도움이 될 것입니다",
            ),
        ),
    ),
    (
        1041,
        1053,
        (
            ("대농촌을 건설하", "대농촌을 건설하여"),
            (
                "\n광활한 농지를 본 백성들도 의욕이 넘치니\n수확량은 물론 병사 수도 기대할 수 있을 듯",
                "\n광활한 농지를 본 백성들도 의욕이 넘치니\n수확량은 물론 병사 수도 기대할 수 있습니다",
            ),
        ),
    ),
    (
        1042,
        1054,
        (
            ("대시장을 건설하", "대시장을 건설하여"),
            (
                "\n벌써 장사가 활발해진 모습이니\n큰 수입을 기대할 수 있",
                "\n벌써 장사가 활발해진 모습이니\n큰 수입을 기대할 수 있습니다",
            ),
        ),
    ),
    (
        1043,
        1055,
        (
            (
                "전쟁으로 황폐해진 마을의\n복구를 지원하",
                "전쟁으로 황폐해진 마을의\n복구를 지원하니",
            ),
            (
                "\n백성들도 무척 감사하고 있",
                "\n백성들도 무척 감사하고 있습니다",
            ),
        ),
    ),
    (
        1044,
        1056,
        (
            (
                "전쟁에 휘말린 상인들을 위해\n살아갈 터전을 마련하",
                "전쟁에 휘말린 상인들을 위해\n살아갈 터전을 마련하니",
            ),
            (
                "\n상인들도 감사하고 있",
                "\n상인들도 감사하고 있습니다",
            ),
        ),
    ),
    (
        1045,
        1057,
        (
            (
                "전쟁에 휘말린 마을로 가서\n도적을 토벌하고 오",
                "전쟁에 휘말린 마을로 가서\n도적을 토벌하고 오니",
            ),
            (
                "\n이로써 백성들도 안심하고 살 수 있",
                "\n이로써 백성들도 안심하고 살 수 있습니다",
            ),
        ),
    ),
    (
        1047,
        1059,
        (
            (
                "피해를 입은 백성들을 위해\n살 집을 새로 마련하",
                "피해를 입은 백성들을 위해\n살 집을 새로 마련하니",
            ),
            (
                "\n예전의 활기를 되찾은 듯",
                "\n예전의 활기를 되찾은 듯합니다",
            ),
        ),
    ),
    (
        1048,
        1060,
        (
            (
                "토사를 치우고 가도를 정비하",
                "토사를 치우고 가도를 정비하니",
            ),
            (
                "\n사람들의 왕래가 늘고\n장사도 활기를 띠",
                "\n사람들의 왕래가 늘고\n장사도 활기를 띱니다",
            ),
        ),
    ),
    (
        1049,
        1061,
        (
            (
                "피해를 입은 마을을 복구하고\n제방도 수리하",
                "피해를 입은 마을을 복구하고\n제방도 수리했으니",
            ),
            (
                "\n더 이상의 피해는 생기지 않을 것",
                "\n더 이상의 피해는 생기지 않을 것입니다",
            ),
        ),
    ),
    (
        1051,
        1063,
        (
            ("파괴된 취락을\n재건하", "파괴된 취락을\n재건했으니"),
            (
                "\n백성들도 예전처럼 지낼 수 있을 것",
                "\n백성들도 예전처럼 지낼 수 있을 것입니다",
            ),
        ),
    ),
    (
        1052,
        1064,
        (
            (
                "잔해를 치우고 가도를\n정비하",
                "잔해를 치우고 가도를\n정비하니",
            ),
            (
                "\n이로써 사람들의 왕래도 늘어나",
                "\n이로써 사람들의 왕래도 늘어날 것입니다",
            ),
        ),
    ),
    (
        1053,
        1065,
        (
            ("성벽을 수리하", "성벽을 수리하여"),
            (
                "\n백성들이 노역에서 풀려나\n불만도 줄어든 듯",
                "\n백성들이 노역에서 풀려나\n불만도 줄어든 듯합니다",
            ),
        ),
    ),
    (
        1055,
        1067,
        (
            (
                "식량을 제공하고\n습격으로 불탄 마을을 지원하",
                "식량을 제공하고\n습격으로 불탄 마을을 지원하니",
            ),
            (
                "\n백성들도 감사하고",
                "\n백성들도 감사하고 있습니다",
            ),
        ),
    ),
    (
        1056,
        1068,
        (
            ("시장을 재건하", "시장을 재건하니"),
            (
                "\n사람들이 많이 모여들고\n장사도 활기를 띠고 있",
                "\n사람들이 많이 모여들고\n장사도 활기를 띠고 있습니다",
            ),
        ),
    ),
    (
        1057,
        1069,
        (
            (
                "굶주린 백성의 불만을 달래려고\n식량을 베풀",
                "굶주린 백성의 불만을 달래려고\n식량을 베푸니",
            ),
            (
                "\n백성의 불만도 누그러지고 있",
                "\n백성의 불만도 누그러지고 있습니다",
            ),
        ),
    ),
    (
        1059,
        1071,
        (
            (
                "굶주린 백성들을 위해\n식량을 배급하",
                "굶주린 백성들을 위해\n식량을 배급하니",
            ),
            (
                "\n모두 무척 감사하고",
                "\n모두 무척 감사하고 있습니다",
            ),
        ),
    ),
)
for base_record, pk_record, literals in STATIC_FAMILIES:
    for literal_id, (before, after) in enumerate(literals):
        add_pair(
            (8, base_record),
            (8, pk_record),
            literal_id,
            before,
            after,
        )

add_pair(
    (8, 1060),
    (8, 1072),
    0,
    "백성들을 설득하",
    "백성들을 설득했습니다",
)
add_pair(
    (8, 1060),
    (8, 1072),
    1,
    "\n어려운 일일수록 모두 힘을 모아\n함께 이겨 내",
    "\n어려운 일일수록 모두 힘을 모아\n함께 이겨 내야 합니다",
)
add_pair(
    (8, 1181),
    (8, 1197),
    0,
    "교역의 이익을 더욱 늘리고자\n하역에 알맞은 교역항을\n이 땅에 건설하고자 하",
    "교역의 이익을 더욱 늘리고자\n하역에 알맞은 교역항을\n이 땅에 건설하고자 합니다",
)
add_pair(
    (8, 1183),
    (8, 1199),
    0,
    "새로운 은 광상이 발견되",
    "새로운 은 광상이 발견되어",
)
add_pair(
    (8, 1183),
    (8, 1199),
    1,
    "\n대규모 공사를 벌여\n채굴 체제를 정비하고자 하",
    "\n대규모 공사를 벌여\n채굴 체제를 정비하고자 합니다",
)
add_pair(
    (8, 1187),
    (8, 1203),
    0,
    "남만 수도사의 요청에 응하여\n남만사를 이 땅에 세우고\n민심을 달래고자 하",
    "남만 수도사의 요청에 응하여\n남만사를 이 땅에 세우고\n민심을 달래고자 합니다",
)


ALLOWED_COMPONENT_KINDS = frozenset(
    {"literal_boundary", "block_token", "padding_zero", "output_control"}
)
HIGH_CONFIDENCE_BARE_ENDINGS = (
    "보이",
    "붐비",
    "해지",
    "힘써",
    "있",
    "띠",
    "하",
)
ALLOWED_BARE_LINES = {
    "base_msggame": {
        ((6, 462), 0, "앞으로 더욱 힘써"),
        ((9, 2251), 0, "하하하"),
        ((16, 81), 0, "후방 성에서 정무에 힘써"),
    },
    "pk_msggame": {
        ((6, 464), 0, "앞으로 더욱 힘써"),
        ((9, 2331), 0, "하하하"),
        ((17, 783), 1, "후, 후후후……하하하!"),
    },
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def coordinate_digest(
    coordinates: Mapping[tuple[int, int, int], object],
) -> str:
    payload = "\n".join(
        f"{block_id}:{record_id}:{literal_id}"
        for block_id, record_id, literal_id in sorted(coordinates)
    ).encode("ascii")
    return sha256_bytes(payload)


def raw_g1n_width(value: str) -> int:
    width = 0
    for character in value:
        codepoint = ord(character)
        if codepoint < 0x20 or 0x7F <= codepoint < 0xA0:
            continue
        width += (
            48
            if unicodedata.east_asian_width(character) in {"W", "F", "A"}
            else 24
        )
    return width


def relative_width_growth_exceptions(
    resource: str,
) -> dict[tuple[str, int, int, int, int], dict[str, object]]:
    rewrites = BASE_REWRITES if resource == "base_msggame" else PK_REWRITES
    exceptions: dict[
        tuple[str, int, int, int, int],
        dict[str, object],
    ] = {}
    for coordinate, (before, after) in rewrites.items():
        before_lines = before.split("\n")
        after_lines = after.split("\n")
        if len(before_lines) != len(after_lines):
            raise DirectStaticClosureError(
                f"width contract line count drifted: {coordinate}"
            )
        for line_index, (before_line, after_line) in enumerate(
            zip(before_lines, after_lines)
        ):
            before_width = raw_g1n_width(before_line)
            after_width = raw_g1n_width(after_line)
            if after_width - before_width <= 24:
                continue
            key = (resource, *coordinate, line_index)
            exceptions[key] = {
                "before_width_px": before_width,
                "after_width_px": after_width,
                "after_literal_sha256": sha256_bytes(
                    after.encode("utf-16le")
                ),
                "reason":
                    "direct-render Korean sentence closure completes a "
                    "Japanese continuative form with no runtime suffix",
            }
    return exceptions


def records_from_blob(blob: bytes) -> dict[tuple[int, int], MsgGameRecord]:
    return {
        (record.block_id, record.record_id): record
        for block in parse_packed_msggame(blob).archive.blocks
        for record in block.records
    }


def nonliteral_gaps(record: MsgGameRecord) -> tuple[bytes, ...]:
    literals = parse_record_literals(record)
    gaps: list[bytes] = []
    cursor = 0
    for literal in literals:
        gaps.append(record.data[cursor:literal.marker_offset])
        cursor = literal.marker_end
    gaps.append(record.data[cursor:])
    return tuple(gaps)


def normalized_line(value: str) -> str:
    return value.strip().rstrip(".!?…。！？").rstrip()


def bare_line_issues(
    blob: bytes,
    resource: str,
    qa: Any,
) -> tuple[dict[str, object], ...]:
    records = records_from_blob(blob)
    allowed = ALLOWED_BARE_LINES[resource]
    issues: list[dict[str, object]] = []
    for coordinate, record in records.items():
        if coordinate[0] == 0:
            continue
        components = qa.tolerant_decode_record(record)
        kinds = frozenset(str(component["kind"]) for component in components)
        if kinds - ALLOWED_COMPONENT_KINDS:
            continue
        rendered = qa.TerminalRenderer(records).render(coordinate)
        if len(rendered) != 1:
            raise DirectStaticClosureError(
                f"direct record rendered multiple variants: {coordinate}"
            )
        for line_index, line in enumerate(rendered[0].split("\n")):
            core = normalized_line(line)
            endings = tuple(
                ending
                for ending in HIGH_CONFIDENCE_BARE_ENDINGS
                if core.endswith(ending)
            )
            if not endings:
                continue
            if (coordinate, line_index, line.strip()) in allowed:
                continue
            issues.append(
                {
                    "coordinate": f"{coordinate[0]}:{coordinate[1]}",
                    "line_index": line_index,
                    "ending": max(endings, key=len),
                    "line_utf16le_sha256": sha256_bytes(
                        line.encode("utf-16le")
                    ),
                }
            )
    return tuple(issues)


def apply(
    blob: bytes,
    resource: str,
    qa: Any,
) -> tuple[bytes, dict[str, object]]:
    if resource not in {"base_msggame", "pk_msggame"}:
        raise DirectStaticClosureError(f"unknown resource: {resource}")
    rewrites = BASE_REWRITES if resource == "base_msggame" else PK_REWRITES
    before_records = records_from_blob(blob)
    replacements: dict[tuple[int, int, int], str] = {}
    changed_records = {coordinate[:2] for coordinate in rewrites}
    for coordinate, (expected, replacement) in rewrites.items():
        record_coordinate = coordinate[:2]
        record = before_records.get(record_coordinate)
        if record is None:
            raise DirectStaticClosureError(
                f"rewrite record is absent: {coordinate}"
            )
        kinds = frozenset(
            str(component["kind"])
            for component in qa.tolerant_decode_record(record)
        )
        if kinds - ALLOWED_COMPONENT_KINDS:
            raise DirectStaticClosureError(
                f"rewrite is not a direct-render record: {coordinate} {kinds}"
            )
        literals = parse_record_literals(record)
        if coordinate[2] >= len(literals):
            raise DirectStaticClosureError(
                f"rewrite literal is absent: {coordinate}"
            )
        observed = literals[coordinate[2]].text
        if observed != expected:
            raise DirectStaticClosureError(
                f"rewrite predecessor drifted: {coordinate} "
                f"{sha256_bytes(observed.encode('utf-16le'))}"
            )
        if expected.count("\n") != replacement.count("\n"):
            raise DirectStaticClosureError(
                f"rewrite changes display line count: {coordinate}"
            )
        replacements[coordinate] = replacement

    before_issues = bare_line_issues(blob, resource, qa)
    candidate = rebuild_packed_with_literals(blob, replacements)
    after_records = records_from_blob(candidate)
    if before_records.keys() != after_records.keys():
        raise DirectStaticClosureError("record universe changed")
    for coordinate in before_records:
        if coordinate not in changed_records:
            if before_records[coordinate].data != after_records[coordinate].data:
                raise DirectStaticClosureError(
                    f"unowned record changed: {coordinate}"
                )
            continue
        if nonliteral_gaps(before_records[coordinate]) != nonliteral_gaps(
            after_records[coordinate]
        ):
            raise DirectStaticClosureError(
                f"non-literal bytes changed: {coordinate}"
            )
    for coordinate, replacement in replacements.items():
        observed = parse_record_literals(after_records[coordinate[:2]])[
            coordinate[2]
        ].text
        if observed != replacement:
            raise DirectStaticClosureError(
                f"replacement did not round-trip: {coordinate}"
            )
    after_issues = bare_line_issues(candidate, resource, qa)
    if after_issues:
        raise DirectStaticClosureError(
            f"bare direct-render endings survived: {after_issues[:5]}"
        )
    report = {
        "schema": "nobu16.kr.direct-static-sentence-closure.v1",
        "status": "PASS",
        "resource": resource,
        "replacement_count": len(replacements),
        "changed_record_count": len(changed_records),
        "coordinate_sha256": coordinate_digest(rewrites),
        "pre_gate_issue_count": len(before_issues),
        "post_gate_issue_count": len(after_issues),
        "relative_width_growth_exception_count": len(
            relative_width_growth_exceptions(resource)
        ),
        "candidate_sha256": sha256_bytes(candidate),
        "candidate_size": len(candidate),
        "nonliteral_bytes_preserved": True,
        "literal_line_counts_preserved": True,
        "steam_write_performed": False,
    }
    return candidate, report
