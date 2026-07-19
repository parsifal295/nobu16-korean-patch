#!/usr/bin/env python3
"""Build a private direct-PC B17 static-quality candidate.

Only exact, pinned W45 Korean literals are replaced.  It opens current Steam
PC Korean resources and pristine Steam PC Japanese resources, then writes a
candidate only below ``tmp/pc_b17_direct_static_candidate_v2``.  It has no
Steam-apply, transaction, Git, network, push, or release operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


sys.dont_write_bytecode = True

SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
TMP_ROOT = REPO / "tmp" / WORKSTREAM.name
TOOLS_ROOT = REPO / "tools"
MSGGAME_ROOT = REPO / "workstreams" / "msggame"

BASE_RESOURCE = "MSG/JP/msggame.bin"
PK_RESOURCE = "MSG_PK/JP/msggame.bin"
RESOURCE_ORDER = (BASE_RESOURCE, PK_RESOURCE)
BLOCK_ID = 17

MSGA_FORMAT = MSGGAME_ROOT / "msggame_format.py"
MSGA_FORMAT_SHA256 = "5F2D8076335822BE49A4F84EC334254527F3766F046165C56B1BFB7E4DAE8458"
LZ4_HELPER = TOOLS_ROOT / "nobu16_lz4.py"
LZ4_HELPER_SHA256 = "96E7E934355F1B7B1764FAFA1B2809BA7D165E4ADA1DE16EA15C089790E77CFB"

for root in (TOOLS_ROOT, MSGGAME_ROOT):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from msggame_format import (  # noqa: E402
    LITERAL_END,
    LITERAL_START,
    MsgGameArchive,
    MsgGameRecord,
    parse_raw_msggame,
    parse_record_literals,
    rebuild_packed_msggame,
    rebuild_packed_with_literals,
    rebuild_raw_msggame,
)
from nobu16_lz4 import decompress_wrapper  # noqa: E402


AUDIT_SCHEMA = "nobu16.kr.pc-b17-direct-static-candidate-audit.v2"
MANIFEST_SCHEMA = "nobu16.kr.pc-b17-direct-static-candidate-manifest.v2"


class CandidateError(RuntimeError):
    """Raised when a pinned source, target, or private-output guard drifts."""


@dataclass(frozen=True)
class Profile:
    size: int
    sha256: str
    raw_size: int
    raw_sha256: str


@dataclass(frozen=True)
class ResourceSpec:
    name: str
    relative: str
    ko_path: Path
    jp_path: Path
    ko_profile: Profile
    jp_profile: Profile
    expected_b17_records: int
    expected_b17_literals: int


@dataclass(frozen=True)
class Target:
    resource: str
    block_id: int
    record_id: int
    literal_id: int
    current_ko: str
    target_ko: str
    pc_jp: str
    rationale: str

    @property
    def slot(self) -> tuple[int, int, int]:
        return (self.block_id, self.record_id, self.literal_id)

    @property
    def slot_text(self) -> str:
        return f"{self.block_id}:{self.record_id}:{self.literal_id}"


@dataclass(frozen=True)
class LoadedResource:
    spec: ResourceSpec
    packed: bytes
    raw: bytes
    archive: MsgGameArchive
    jp_packed: bytes
    jp_raw: bytes
    jp_archive: MsgGameArchive


@dataclass(frozen=True)
class ResourceCandidate:
    spec: ResourceSpec
    packed: bytes
    raw: bytes
    archive: MsgGameArchive
    changed_records: tuple[tuple[int, int], ...]
    changed_literals: tuple[tuple[int, int, int], ...]
    rows: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class CandidateBundle:
    sources: Mapping[str, LoadedResource]
    resources: Mapping[str, ResourceCandidate]
    audit: Mapping[str, Any]
    manifest: Mapping[str, Any]


BASE_SPEC = ResourceSpec(
    "base",
    BASE_RESOURCE,
    Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG\JP\msggame.bin"),
    Path(r"F:\Games\NOBU16\MSG\JP\msggame.bin"),
    Profile(
        1_504_410,
        "F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB",
        1_498_508,
        "27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D",
    ),
    Profile(
        610_163,
        "EDEC6E21FE663A815422A16C219C3429262606ECADA8E814F2E9864250A463C4",
        1_337_548,
        "353010B59A3E04BFE5541162229C1CFCAD181EF0E75FCC9B6DE2043BFC515F38",
    ),
    33,
    66,
)
PK_SPEC = ResourceSpec(
    "pk",
    PK_RESOURCE,
    Path(r"F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msggame.bin"),
    Path(
        r"F:\SteamLibrary\steamapps\common\NOBU16\KR_PATCH_BACKUP\file_only_transaction\steam-jp-1.1.7-v0.6.0\originals\MSG_PK\JP\msggame.bin"
    ),
    Profile(
        1_806_538,
        "0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092",
        1_799_456,
        "737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E",
    ),
    Profile(
        721_304,
        "31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210",
        1_599_324,
        "F052DA62C584C024C1EAF67A706253525421E6068976657DF6A6C07EFCA5D4E8",
    ),
    1_159,
    2_256,
)
RESOURCE_SPECS = (BASE_SPEC, PK_SPEC)


def t(
    resource: str,
    record_id: int,
    literal_id: int,
    current_ko: str,
    target_ko: str,
    pc_jp: str,
    rationale: str,
) -> Target:
    return Target(resource, BLOCK_ID, record_id, literal_id, current_ko, target_ko, pc_jp, rationale)


# Every current Korean preimage, target Korean literal, and Japanese evidence is
# spelled out in full.  No broad find/replace is used.
TARGETS = (
    t(
        BASE_RESOURCE,
        7,
        0,
        "강화 사자가 통했군요\n방침을 두고 반목한 것이겠지요",
        "강화 사절이 통했군요\n방침을 두고 반목한 것이겠지요",
        "講和の使者が効きましたな\n方針を巡って仲違いしたのでしょう",
        "use Korean envoy noun for 使者",
    ),
    t(BASE_RESOURCE, 12, 0, "북향", "호고", "北郷", "same-PC name normalization"),
    t(BASE_RESOURCE, 19, 0, "북향", "호고", "北郷", "same-PC name normalization"),
    t(BASE_RESOURCE, 20, 1, "기타키타", "다바루", "田北", "same-PC name normalization"),
    t(PK_RESOURCE, 5, 0, "기타키타", "다바루", "田北", "same-PC name normalization"),
    t(
        PK_RESOURCE,
        7,
        0,
        "강화 사자가 통했군요\n방침을 두고 반목한 것이겠지요",
        "강화 사절이 통했군요\n방침을 두고 반목한 것이겠지요",
        "講和の使者が効きましたな\n方針を巡って仲違いしたのでしょう",
        "use Korean envoy noun for 使者",
    ),
    t(
        PK_RESOURCE,
        8,
        0,
        "예정대로 조리노부세를 쓴다\n",
        "예정대로 쓰리노부세를 쓴다\n",
        "手筈通り、釣り野伏を使う\n",
        "same-PC term reading normalization",
    ),
    t(PK_RESOURCE, 12, 1, "북향", "호고", "北郷", "same-PC name normalization"),
    t(
        PK_RESOURCE,
        27,
        0,
        "복병이 있었다!혼란한 틈에 쳐부수자!",
        "복병이 있었다! 혼란한 틈에 쳐부수자!",
        "伏兵がおったぞ！混乱している内に蹴散らすぞ！",
        "restore missing Korean sentence space",
    ),
    t(PK_RESOURCE, 51, 1, "기타키타", "다바루", "田北", "same-PC name normalization"),
    t(
        PK_RESOURCE,
        54,
        0,
        "조리노부세가 실패했나…!\n어쩔 수 없다, 무슨 수를 써서라도 소린의 목을 베어라",
        "쓰리노부세가 실패했나…!\n어쩔 수 없다, 무슨 수를 써서라도 소린의 목을 베어라",
        "釣り野伏はしくじったか…！\n是非もなし、なんとしてでも宗麟の首を取れ",
        "same-PC term reading normalization",
    ),
    t(
        PK_RESOURCE,
        434,
        0,
        "요지의 절반 이상을 제압했다!\n공세를 늦추지 말고 나아가라!",
        "요충지의 절반 이상을 제압했다!\n공세를 늦추지 말고 나아가라!",
        "要所の過半を制した！\n攻めの手を緩めず、進め！",
        "use the established 要所 UI term",
    ),
    t(
        PK_RESOURCE,
        504,
        0,
        "오히려 내가 너구리 사냥에 질렸다…\n뭐, 이번에도 사냥당해 줘야겠지만",
        "오히려 우리 쪽이 너구리 사냥에 질렸다…\n뭐, 이번에도 사냥당해 줘야겠지만",
        "我が方こそ、狸狩りは飽き飽きじゃ…\nまあ、こたびも狩られていただくが",
        "restore 我が方 as the speaker's side",
    ),
    t(PK_RESOURCE, 659, 1, "의 요지를 확보하라", "의 요충지를 확보하라", "の要所を抑えよ", "use the established 要所 UI term"),
    t(PK_RESOURCE, 660, 1, "의 요지를 확보하라", "의 요충지를 확보하라", "の要所を抑えよ", "use the established 要所 UI term"),
    t(PK_RESOURCE, 661, 1, "의 요지를 확보하라", "의 요충지를 확보하라", "の要所を抑えよ", "use the established 要所 UI term"),
    t(
        PK_RESOURCE,
        852,
        0,
        "계속 싸우더라도 더 많은 생명을 잃을뿐입니다.\n더 이상 싸울 필요가 없습니다.",
        "계속 싸우더라도 더 많은 생명을 잃을 뿐입니다.\n더 이상 싸울 필요가 없습니다.",
        "戦い続けても失われる命が増えるのみ\nこれ以上の戦いは無意味だな",
        "repair Korean bound-noun spacing",
    ),
    t(
        PK_RESOURCE,
        871,
        0,
        "……흥, 또렷이 들리는군.\n이번만은 솔직히 감사하지.",
        "……흥, 기운찬 목소리로군.\n이번만은 솔직히 감사하지.",
        "…ふっ、生き生きとした声だな\nここは素直に感謝するとしよう",
        "restore 生き生きとした voice meaning",
    ),
    t(
        PK_RESOURCE,
        872,
        1,
        "는 아군이다. 적을 혼동하지 마라!",
        "는 아군이다. 적이라고 착각하지 마라!",
        "は味方だ、敵を違えるな！",
        "restore do-not-mistake-for-enemy meaning",
    ),
    t(
        PK_RESOURCE,
        894,
        0,
        "음, 안개가 걷혔군.\n좋다. 적이 내려오기만 기다리면……",
        "음, 안개가 걷혔군.\n좋다. 이러면 적을 놓칠 일도……",
        "霧が薄れてきたか…\n好都合よ、これなら敵を逃すことも…",
        "restore fog and enemy-escape inference",
    ),
    t(PK_RESOURCE, 939, 1, "퇴각 지점", "퇴로", "退き口", "use retreat-route term"),
    t(PK_RESOURCE, 950, 0, "선봉 격파", "선봉 ", "先鋒の", "restore token-adjacent possessive prefix"),
    t(PK_RESOURCE, 951, 0, "선봉 격파", "선봉 ", "先鋒の", "restore token-adjacent possessive prefix"),
    t(PK_RESOURCE, 952, 0, "선봉 격파", "선봉 ", "先鋒の", "restore token-adjacent possessive prefix"),
    t(PK_RESOURCE, 956, 1, "퇴각 지점", "퇴로", "退き口", "use retreat-route term"),
    t(PK_RESOURCE, 957, 1, "퇴각 지점", "퇴로", "退き口", "use retreat-route term"),
    t(PK_RESOURCE, 958, 1, "퇴각 지점", "퇴로", "退き口", "use retreat-route term"),
    t(
        PK_RESOURCE,
        971,
        0,
        "차륜진으로 간다, 먼저 선봉끼리 맞붙어라\n그 뒤 내가 적의 본진…　",
        "차륜진으로 간다, 먼저 선봉끼리 맞붙어라\n그 뒤 적의 본진…　",
        "車懸りでゆく、まず先鋒同士で当たれ\nその後、我が敵の本陣…　",
        "remove malformed 내가 while retaining the enemy-headquarters wording",
    ),
    t(
        PK_RESOURCE,
        972,
        0,
        "움직이지 말고 때를 기다린다.\n",
        "나는 움직이지 않고 때를 기다린다.\n",
        "我は動かず、機を待つ\n",
        "restore first-person resolve from Japanese",
    ),
    t(PK_RESOURCE, 981, 2, "퇴각 지점", "퇴로", "退き口", "use retreat-route term"),
    t(
        PK_RESOURCE,
        1004,
        0,
        "퇴각 지점을 빼앗기다니……\n과연",
        "퇴로를 빼앗기다니……\n과연",
        "退き口が取られるとは…\nさすが",
        "use retreat-route term with Korean object particle",
    ),
    t(PK_RESOURCE, 1005, 0, "퇴각 지점", "퇴로", "退き口", "use retreat-route term"),
    t(PK_RESOURCE, 1006, 0, "퇴각 지점", "퇴로", "退き口", "use retreat-route term"),
    t(PK_RESOURCE, 1007, 0, "퇴각 지점", "퇴로", "退き口", "use retreat-route term"),
    t(PK_RESOURCE, 1020, 1, "퇴각 지점", "퇴로", "退き口", "use retreat-route term"),
    t(PK_RESOURCE, 1021, 1, "퇴각 지점", "퇴로", "退き口", "use retreat-route term"),
    t(PK_RESOURCE, 1022, 1, "퇴각 지점", "퇴로", "退き口", "use retreat-route term"),
    t(PK_RESOURCE, 1051, 0, "주님, 죽음을 겪으십시오!", "주군, 각오하라!", "殿、覚悟せよ！", "restore lord address and challenge"),
    t(PK_RESOURCE, 1065, 0, "이기다! 이기다!", "이겼다! 이겼다!", "勝った！勝った！", "repair Korean conjugation"),
    t(
        PK_RESOURCE,
        1073,
        0,
        "의 기습으로 적을 끌어냈다.\n그자에게 중요한 임무였다고 전하라.\n그리고 철포 준비는 끝났나?",
        "의 기습으로 적을 끌어냈다.\n그자에게 임무를 훌륭히 해냈다고 전하라.\n그리고 철포 준비는 끝났나?",
        "の奇襲で敵を誘い出せたのだ\nあの者には役目大儀と伝えておけ\n…さて、鉄砲の準備は済んでおるな？",
        "restore 役目大儀 as praise for duty completed",
    ),
    t(
        PK_RESOURCE,
        1093,
        0,
        "요지보다 앞서지 말고 적 6개 부대를 격파하라(",
        "요충지 앞으로 나가지 말고 적 6개 부대를 격파하라(",
        "要所より前に出ず、敵を6部隊撃破せよ（",
        "restore 要所 term and movement direction; preserve existing parenthesis bytes",
    ),
    t(
        PK_RESOURCE,
        1120,
        0,
        "큭, 곧 울타리를 부술 수 있었는데……\n분하구나……",
        "큭, 이래서는 울타리를 부순다 해도……\n분하구나……",
        "くっ、これでは柵を壊したところで…\n無念なり…",
        "restore even-if-fence-breaks meaning",
    ),
    t(
        PK_RESOURCE,
        1132,
        0,
        "퇴각 지점을 지키려는 것이라 하면 된다.\n이런 싸움에 목숨을 걸 가치는 없다.",
        "퇴로를 확보하기 위해서라고 하면 된다.\n이런 싸움에 목숨을 걸 가치는 없다.",
        "退き口を確保するためと言えば良い\nこのような戦、命を賭ける価値もない",
        "restore retreat-route securing meaning",
    ),
    t(
        PK_RESOURCE,
        1137,
        0,
        "병사는 제게 맡기고 어서 물러나십시오.\n제가 후위를 맡겠습니다…… 부디 안녕히.",
        "그럼 후군은 제게 맡기십시오.\n…이것으로 작별이오!",
        "では、それがしに殿軍はお任せあれ\n…これにてお別れでござる！",
        "restore 殿軍 and farewell; remove unsupported withdrawal instruction",
    ),
)


EXPECTED_SCOPE = (
    (BASE_RESOURCE, 17, 7, 0),
    (BASE_RESOURCE, 17, 12, 0),
    (BASE_RESOURCE, 17, 19, 0),
    (BASE_RESOURCE, 17, 20, 1),
    (PK_RESOURCE, 17, 5, 0),
    (PK_RESOURCE, 17, 7, 0),
    (PK_RESOURCE, 17, 8, 0),
    (PK_RESOURCE, 17, 12, 1),
    (PK_RESOURCE, 17, 27, 0),
    (PK_RESOURCE, 17, 51, 1),
    (PK_RESOURCE, 17, 54, 0),
    (PK_RESOURCE, 17, 434, 0),
    (PK_RESOURCE, 17, 504, 0),
    (PK_RESOURCE, 17, 659, 1),
    (PK_RESOURCE, 17, 660, 1),
    (PK_RESOURCE, 17, 661, 1),
    (PK_RESOURCE, 17, 852, 0),
    (PK_RESOURCE, 17, 871, 0),
    (PK_RESOURCE, 17, 872, 1),
    (PK_RESOURCE, 17, 894, 0),
    (PK_RESOURCE, 17, 939, 1),
    (PK_RESOURCE, 17, 950, 0),
    (PK_RESOURCE, 17, 951, 0),
    (PK_RESOURCE, 17, 952, 0),
    (PK_RESOURCE, 17, 956, 1),
    (PK_RESOURCE, 17, 957, 1),
    (PK_RESOURCE, 17, 958, 1),
    (PK_RESOURCE, 17, 971, 0),
    (PK_RESOURCE, 17, 972, 0),
    (PK_RESOURCE, 17, 981, 2),
    (PK_RESOURCE, 17, 1004, 0),
    (PK_RESOURCE, 17, 1005, 0),
    (PK_RESOURCE, 17, 1006, 0),
    (PK_RESOURCE, 17, 1007, 0),
    (PK_RESOURCE, 17, 1020, 1),
    (PK_RESOURCE, 17, 1021, 1),
    (PK_RESOURCE, 17, 1022, 1),
    (PK_RESOURCE, 17, 1051, 0),
    (PK_RESOURCE, 17, 1065, 0),
    (PK_RESOURCE, 17, 1073, 0),
    (PK_RESOURCE, 17, 1093, 0),
    (PK_RESOURCE, 17, 1120, 0),
    (PK_RESOURCE, 17, 1132, 0),
    (PK_RESOURCE, 17, 1137, 0),
)

# Runtime token / particle, color markup, and cosmetic-parenthesis holds from
# the direct audit are intentionally disjoint from TARGETS.
EXCLUDED_HOLD_SLOTS = (
    (BASE_RESOURCE, 17, 5, 3),
    (PK_RESOURCE, 17, 226, 0),
    (PK_RESOURCE, 17, 226, 1),
    (PK_RESOURCE, 17, 226, 2),
    (PK_RESOURCE, 17, 226, 3),
    (PK_RESOURCE, 17, 282, 0),
    (PK_RESOURCE, 17, 510, 0),
    (PK_RESOURCE, 17, 510, 1),
    (PK_RESOURCE, 17, 510, 2),
    (PK_RESOURCE, 17, 920, 0),
    (PK_RESOURCE, 17, 920, 1),
    (PK_RESOURCE, 17, 991, 0),
    (PK_RESOURCE, 17, 991, 1),
    (PK_RESOURCE, 17, 296, 0),
    (PK_RESOURCE, 17, 296, 1),
    (PK_RESOURCE, 17, 300, 1),
    (PK_RESOURCE, 17, 300, 2),
    (PK_RESOURCE, 17, 304, 1),
    (PK_RESOURCE, 17, 304, 2),
    (PK_RESOURCE, 17, 463, 0),
    (PK_RESOURCE, 17, 463, 1),
    (PK_RESOURCE, 17, 467, 1),
    (PK_RESOURCE, 17, 467, 2),
    (PK_RESOURCE, 17, 471, 1),
    (PK_RESOURCE, 17, 471, 2),
    (PK_RESOURCE, 17, 696, 3),
    (PK_RESOURCE, 17, 696, 4),
    (PK_RESOURCE, 17, 790, 0),
    (PK_RESOURCE, 17, 790, 1),
    (PK_RESOURCE, 17, 1093, 1),
    (PK_RESOURCE, 17, 1157, 0),
    (PK_RESOURCE, 17, 1157, 1),
)

# Derived by the first no-write profile pass against the pinned W45 inputs.
# A build/verify/diff command refuses to run if either exact profile drifts.
EXPECTED_OUTPUT_PROFILES: dict[str, Profile] = {
    BASE_RESOURCE: Profile(
        1_504_406,
        "99B5096FB5532FB50DCD5C04C33E5CC38DA3DC1B959CF68A5547A77FF2C9A76B",
        1_498_504,
        "88091E502BC815E3553106D94C8B53EA2048017A0AAD15EED48582AC45234832",
    ),
    PK_RESOURCE: Profile(
        1_806_438,
        "E5029A774F7E287316DBA00A2A516E4A6A8E599673F4FBC44D195EC9EF7900A4",
        1_799_356,
        "D315325FC80D7517826C8B226CB904849C4E6609FB1F966768B1A3B809892780",
    ),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def text_hash(value: str) -> str:
    return sha256_bytes(value.encode("utf-16le"))


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def profile_dict(profile: Profile) -> dict[str, Any]:
    return {
        "size": profile.size,
        "sha256": profile.sha256,
        "raw_size": profile.raw_size,
        "raw_sha256": profile.raw_sha256,
    }


def observed_profile(packed: bytes, raw: bytes) -> Profile:
    return Profile(len(packed), sha256_bytes(packed), len(raw), sha256_bytes(raw))


def require_profile(packed: bytes, raw: bytes, profile: Profile, label: str) -> None:
    require(observed_profile(packed, raw) == profile, f"{label} profile differs")


def require_pc_path(path: Path, label: str) -> Path:
    resolved = path.resolve(strict=True)
    forbidden = {part for part in resolved.parts if part.casefold() == "sc" or "switch" in part.casefold()}
    require(not forbidden, f"non-PC path is forbidden for {label}: {resolved}")
    return resolved


def require_private(path: Path, label: str, *, strict: bool = False) -> Path:
    root = TMP_ROOT.resolve(strict=False)
    resolved = path.resolve(strict=strict)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise CandidateError(f"{label} escapes private tmp root: {resolved}") from exc
    require(resolved != root, f"{label} must be below private tmp root")
    return resolved


def literal_signature(value: str) -> dict[str, Any]:
    controls = [f"U+{ord(char):04X}" for char in value if char not in ("\r", "\n") and unicodedata.category(char) == "Cc"]
    return {"lf": value.count("\n"), "cr": value.count("\r"), "controls": controls}


def opaque_skeleton(record: MsgGameRecord) -> bytes:
    output = bytearray()
    cursor = 0
    for literal in parse_record_literals(record):
        output.extend(record.data[cursor : literal.marker_offset + len(LITERAL_START)])
        output.extend(b"<UTF16_LITERAL>")
        output.extend(record.data[literal.marker_end - len(LITERAL_END) : literal.marker_end])
        cursor = literal.marker_end
    output.extend(record.data[cursor:])
    return bytes(output)


def load_archive(path: Path, profile: Profile, label: str) -> tuple[bytes, bytes, MsgGameArchive]:
    packed = require_pc_path(path, label).read_bytes()
    _header, raw = decompress_wrapper(packed)
    require_profile(packed, raw, profile, label)
    archive = parse_raw_msggame(raw)
    require(rebuild_raw_msggame(archive) == raw, f"{label} raw parser round-trip differs")
    require(decompress_wrapper(rebuild_packed_msggame(packed))[1] == raw, f"{label} packed parser round-trip differs")
    return packed, raw, archive


def assert_b17_topology(ko: MsgGameArchive, jp: MsgGameArchive, spec: ResourceSpec) -> None:
    require(len(ko.blocks) > BLOCK_ID and len(jp.blocks) > BLOCK_ID, f"{spec.name} lacks B17")
    ko_block, jp_block = ko.blocks[BLOCK_ID], jp.blocks[BLOCK_ID]
    require(len(ko_block.records) == len(jp_block.records) == spec.expected_b17_records, f"{spec.name} B17 record count differs")
    literal_count = 0
    for ko_record, jp_record in zip(ko_block.records, jp_block.records):
        require(ko_record.record_id == jp_record.record_id, f"{spec.name} B17 record topology differs")
        ko_literals, jp_literals = parse_record_literals(ko_record), parse_record_literals(jp_record)
        require(len(ko_literals) == len(jp_literals), f"{spec.name} B17 literal topology differs")
        require(opaque_skeleton(ko_record) == opaque_skeleton(jp_record), f"{spec.name} B17 opaque skeleton differs")
        literal_count += len(ko_literals)
    require(literal_count == spec.expected_b17_literals, f"{spec.name} B17 literal count differs")


def load_sources() -> dict[str, LoadedResource]:
    require(sha256_path(MSGA_FORMAT) == MSGA_FORMAT_SHA256, "MSGGAME parser helper hash differs")
    require(sha256_path(LZ4_HELPER) == LZ4_HELPER_SHA256, "LZ4 helper hash differs")
    loaded: dict[str, LoadedResource] = {}
    for spec in RESOURCE_SPECS:
        packed, raw, archive = load_archive(spec.ko_path, spec.ko_profile, f"W45 PC Korean {spec.name}")
        jp_packed, jp_raw, jp_archive = load_archive(spec.jp_path, spec.jp_profile, f"pristine PC Japanese {spec.name}")
        assert_b17_topology(archive, jp_archive, spec)
        loaded[spec.relative] = LoadedResource(spec, packed, raw, archive, jp_packed, jp_raw, jp_archive)
    return loaded


def target_map(resource: str) -> dict[tuple[int, int, int], Target]:
    selected = [target for target in TARGETS if target.resource == resource]
    mapped = {target.slot: target for target in selected}
    require(len(mapped) == len(selected), f"duplicate target in {resource}")
    return mapped


def build_resource(source: LoadedResource) -> ResourceCandidate:
    targets = target_map(source.spec.relative)
    replacements: dict[tuple[int, int, int], str] = {}
    rows: list[dict[str, Any]] = []
    for slot, target in sorted(targets.items()):
        block, record, literal = slot
        current = parse_record_literals(source.archive.blocks[block].records[record])[literal].text
        jp_text = parse_record_literals(source.jp_archive.blocks[block].records[record])[literal].text
        require(current == target.current_ko, f"W45 Korean preimage differs at {target.slot_text}")
        require(jp_text == target.pc_jp, f"pristine PC Japanese evidence differs at {target.slot_text}")
        require(current != target.target_ko, f"target does not change at {target.slot_text}")
        require(literal_signature(current) == literal_signature(target.target_ko), f"LF/control signature differs at {target.slot_text}")
        replacements[slot] = target.target_ko
        rows.append(
            {
                "resource": source.spec.relative,
                "slot": target.slot_text,
                "current_ko": current,
                "target_ko": target.target_ko,
                "pc_jp": jp_text,
                "current_ko_utf16le_sha256": text_hash(current),
                "target_ko_utf16le_sha256": text_hash(target.target_ko),
                "pc_jp_utf16le_sha256": text_hash(jp_text),
                "manual_lf_count": current.count("\n"),
                "opaque_skeleton_unchanged": True,
                "rationale": target.rationale,
            }
        )
    packed = rebuild_packed_with_literals(source.packed, replacements)
    _header, raw = decompress_wrapper(packed)
    archive = parse_raw_msggame(raw)
    require(rebuild_raw_msggame(archive) == raw, f"{source.spec.name} candidate raw round-trip differs")
    require(decompress_wrapper(rebuild_packed_msggame(packed))[1] == raw, f"{source.spec.name} candidate packed round-trip differs")
    changed_records, changed_literals = validate_scope(source, archive, replacements)
    profile = observed_profile(packed, raw)
    expected_profile = EXPECTED_OUTPUT_PROFILES.get(source.spec.relative)
    if expected_profile is not None:
        require(profile == expected_profile, f"{source.spec.name} pinned output profile differs")
    return ResourceCandidate(source.spec, packed, raw, archive, changed_records, changed_literals, tuple(rows))


def validate_scope(
    source: LoadedResource,
    candidate: MsgGameArchive,
    replacements: Mapping[tuple[int, int, int], str],
) -> tuple[tuple[tuple[int, int], ...], tuple[tuple[int, int, int], ...]]:
    targets = target_map(source.spec.relative)
    changed_records: list[tuple[int, int]] = []
    changed_literals: list[tuple[int, int, int]] = []
    for before_block, after_block in zip(source.archive.blocks, candidate.blocks):
        require(before_block.block_id == after_block.block_id, f"{source.spec.name} block alignment differs")
        require(len(before_block.records) == len(after_block.records), f"{source.spec.name} record count differs")
        for before, after in zip(before_block.records, after_block.records):
            record_key = (before.block_id, before.record_id)
            old_literals, new_literals = parse_record_literals(before), parse_record_literals(after)
            require(len(old_literals) == len(new_literals), f"{source.spec.name} literal topology differs")
            allowed = {literal for block, record, literal in targets if (block, record) == record_key}
            if before.data != after.data:
                changed_records.append(record_key)
                require(allowed, f"{source.spec.name} changed unapproved record {record_key}")
                require(opaque_skeleton(before) == opaque_skeleton(after), f"{source.spec.name} changed opaque skeleton")
            else:
                require(not allowed, f"{source.spec.name} did not change approved record {record_key}")
            for old, new in zip(old_literals, new_literals):
                slot = (before.block_id, before.record_id, old.literal_id)
                if old.text != new.text:
                    changed_literals.append(slot)
                    require(slot in targets, f"{source.spec.name} changed unapproved literal {slot}")
                    require(new.text == replacements[slot], f"{source.spec.name} target differs at {slot}")
                    require(literal_signature(old.text) == literal_signature(new.text), f"{source.spec.name} changed LF/control signature")
                else:
                    require(slot not in targets, f"{source.spec.name} failed to change target {slot}")
    expected_literals = tuple(sorted(targets))
    expected_records = tuple(sorted({(block, record) for block, record, _ in targets}))
    require(tuple(changed_literals) == expected_literals, f"{source.spec.name} literal scope differs")
    require(tuple(changed_records) == expected_records, f"{source.spec.name} record scope differs")
    return tuple(changed_records), tuple(changed_literals)


def prepare_candidate() -> CandidateBundle:
    observed_scope = tuple((target.resource, *target.slot) for target in TARGETS)
    require(observed_scope == EXPECTED_SCOPE, "approved B17 static scope differs")
    require(set(observed_scope).isdisjoint(EXCLUDED_HOLD_SLOTS), "target overlaps runtime/color/cosmetic hold")
    sources = load_sources()
    resources = {resource: build_resource(sources[resource]) for resource in RESOURCE_ORDER}
    rows = [row for resource in RESOURCE_ORDER for row in resources[resource].rows]
    outputs = {resource: profile_dict(observed_profile(resources[resource].packed, resources[resource].raw)) for resource in RESOURCE_ORDER}
    audit: dict[str, Any] = {
        "schema": AUDIT_SCHEMA,
        "candidate_only": True,
        "source_policy": {
            "platform": "direct PC only",
            "current_w45_korean_opened": True,
            "pristine_pc_japanese_opened": True,
            "other_language_source_opened": False,
            "steam_game_resource_written": False,
            "transaction_capability": "absent",
            "git_operation_capability": "absent",
            "network_capability": "absent",
            "release_capability": "absent",
        },
        "input": {resource: profile_dict(sources[resource].spec.ko_profile) for resource in RESOURCE_ORDER},
        "pc_jp_evidence": {resource: profile_dict(sources[resource].spec.jp_profile) for resource in RESOURCE_ORDER},
        "output": outputs,
        "changed_literal_count": len(rows),
        "changed_record_count": sum(len(resources[resource].changed_records) for resource in RESOURCE_ORDER),
        "changed_literal_count_by_resource": {resource: len(resources[resource].changed_literals) for resource in RESOURCE_ORDER},
        "changed_record_count_by_resource": {resource: len(resources[resource].changed_records) for resource in RESOURCE_ORDER},
        "changed_literals": [row["slot"] for row in rows],
        "changed_records": {resource: [f"{block}:{record}" for block, record in resources[resource].changed_records] for resource in RESOURCE_ORDER},
        "excluded_hold_slots": [f"{resource}:{block}:{record}:{literal}" for resource, block, record, literal in EXCLUDED_HOLD_SLOTS],
        "validation": {
            "manual_lf_preserved": True,
            "opaque_skeleton_preserved": True,
            "whole_archive_target_only_scope_checked": True,
            "runtime_color_cosmetic_holds_excluded": True,
        },
        "records": rows,
    }
    manifest: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        "candidate_only": True,
        "candidate_output_must_be_under": TMP_ROOT.relative_to(REPO).as_posix(),
        "resources": {
            resource: {
                "input": audit["input"][resource],
                "output": outputs[resource],
                "changed_literals": [target.slot_text for target in TARGETS if target.resource == resource],
                "changed_records": audit["changed_records"][resource],
            }
            for resource in RESOURCE_ORDER
        },
        "changed_literal_count": len(rows),
        "changed_record_count": audit["changed_record_count"],
        "audit_sha256": sha256_bytes(canonical_json(audit)),
        "steam_game_resource_write": "absent",
        "transaction": "not_implemented",
        "git_operation": "not_implemented",
        "network": "not_implemented",
        "release": "not_implemented",
    }
    return CandidateBundle(sources, resources, audit, manifest)


def atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    with temp.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def private_file_set(root: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()}


def result_summary(bundle: CandidateBundle, output_root: Path) -> dict[str, Any]:
    return {
        "candidate_root": output_root.relative_to(REPO).as_posix(),
        "changed_literal_count": bundle.audit["changed_literal_count"],
        "changed_record_count": bundle.audit["changed_record_count"],
        "outputs": bundle.audit["output"],
        "steam_game_resource_written": False,
    }


def write_candidate(bundle: CandidateBundle, output_root: Path) -> dict[str, Any]:
    require(len(EXPECTED_OUTPUT_PROFILES) == len(RESOURCE_ORDER), "output profiles are not pinned")
    output_root = require_private(output_root, "candidate output")
    require(not output_root.exists(), f"refusing to overwrite private candidate: {output_root}")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    stage = require_private(Path(tempfile.mkdtemp(prefix="stage-", dir=TMP_ROOT)), "candidate staging", strict=True)
    for resource in RESOURCE_ORDER:
        atomic_write(stage / Path(resource), bundle.resources[resource].packed)
    atomic_write(stage / "audit.v2.json", canonical_json(bundle.audit))
    atomic_write(stage / "candidate_manifest.v2.json", canonical_json(bundle.manifest))
    require(sha256_path(stage / "audit.v2.json") == bundle.manifest["audit_sha256"], "written audit hash differs")
    os.replace(stage, output_root)
    return result_summary(bundle, output_root)


def verify_private(candidate_root: Path) -> dict[str, Any]:
    require(len(EXPECTED_OUTPUT_PROFILES) == len(RESOURCE_ORDER), "output profiles are not pinned")
    candidate_root = require_private(candidate_root, "candidate root", strict=True)
    bundle = prepare_candidate()
    expected = set(RESOURCE_ORDER) | {"audit.v2.json", "candidate_manifest.v2.json"}
    require(private_file_set(candidate_root) == expected, "candidate file set differs")
    for resource in RESOURCE_ORDER:
        require((candidate_root / Path(resource)).read_bytes() == bundle.resources[resource].packed, f"candidate resource differs: {resource}")
    require((candidate_root / "audit.v2.json").read_bytes() == canonical_json(bundle.audit), "candidate audit differs")
    require((candidate_root / "candidate_manifest.v2.json").read_bytes() == canonical_json(bundle.manifest), "candidate manifest differs")
    return result_summary(bundle, candidate_root)


def diff_check(candidate_root: Path) -> dict[str, Any]:
    require(len(EXPECTED_OUTPUT_PROFILES) == len(RESOURCE_ORDER), "output profiles are not pinned")
    candidate_root = require_private(candidate_root, "candidate root", strict=True)
    bundle = prepare_candidate()
    changed_literals: dict[str, list[str]] = {}
    changed_records: dict[str, list[str]] = {}
    for resource in RESOURCE_ORDER:
        source = bundle.sources[resource]
        packed = (candidate_root / Path(resource)).read_bytes()
        _header, raw = decompress_wrapper(packed)
        archive = parse_raw_msggame(raw)
        expected_profile = EXPECTED_OUTPUT_PROFILES[resource]
        require_profile(packed, raw, expected_profile, f"diff candidate {resource}")
        literals: list[str] = []
        records: list[str] = []
        for before_block, after_block in zip(source.archive.blocks, archive.blocks):
            for before, after in zip(before_block.records, after_block.records):
                if before.data != after.data:
                    records.append(f"{before.block_id}:{before.record_id}")
                for old, new in zip(parse_record_literals(before), parse_record_literals(after)):
                    if old.text != new.text:
                        literals.append(f"{before.block_id}:{before.record_id}:{old.literal_id}")
        expected_literals = [target.slot_text for target in TARGETS if target.resource == resource]
        expected_records = bundle.audit["changed_records"][resource]
        require(literals == expected_literals, f"diff literal scope differs: {resource}")
        require(records == expected_records, f"diff record scope differs: {resource}")
        changed_literals[resource] = literals
        changed_records[resource] = records
    return {
        "candidate_root": candidate_root.relative_to(REPO).as_posix(),
        "changed_literals": changed_literals,
        "changed_records": changed_records,
        "changed_literal_count": sum(len(values) for values in changed_literals.values()),
        "steam_game_resource_written": False,
    }


def profile_report() -> dict[str, Any]:
    bundle = prepare_candidate()
    return {
        "changed_literals": bundle.audit["changed_literals"],
        "changed_literal_count": bundle.audit["changed_literal_count"],
        "changed_record_count": bundle.audit["changed_record_count"],
        "input": bundle.audit["input"],
        "pc_jp_evidence": bundle.audit["pc_jp_evidence"],
        "output": bundle.audit["output"],
        "output_profiles_pinned": len(EXPECTED_OUTPUT_PROFILES) == len(RESOURCE_ORDER),
        "steam_game_resource_written": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("--output-root", type=Path, default=TMP_ROOT / "candidate")
    verify = sub.add_parser("verify-private")
    verify.add_argument("--candidate-root", type=Path, default=TMP_ROOT / "candidate")
    diff = sub.add_parser("diff-check")
    diff.add_argument("--candidate-root", type=Path, default=TMP_ROOT / "candidate")
    sub.add_parser("profile")
    args = parser.parse_args()
    if args.command == "build":
        result = write_candidate(prepare_candidate(), args.output_root)
    elif args.command == "verify-private":
        result = verify_private(args.candidate_root)
    elif args.command == "diff-check":
        result = diff_check(args.candidate_root)
    else:
        result = profile_report()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
