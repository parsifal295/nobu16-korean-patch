#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1016 decisions."""

from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch004_segment1013 as PRIOR
import build_base_batch005_segment1015 as PREVIOUS_SEGMENT
import build_base_batch005_segment1017 as NEXT_SEGMENT


ENGINE = PRIOR.ENGINE
GENERAL = PRIOR.GENERAL
UTIL = PRIOR.UTIL
GRAPH = PRIOR.GRAPH
FIXED = PRIOR.FIXED
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B005_S1016.private.v1.jsonl"
)
SEGMENT = 1016
QUEUE_BATCH_ID = "base_msggame-B005"
BLOCK_ID = 0

# Hidden record 2083 is deliberately outside the visible decision universe.
RECORD_IDS = tuple(range(2084, 2151))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
FULL_RECORD_IDS = tuple(range(2072, 2163))
HIDDEN_BOUNDARY_RECORD_IDS = (2079, 2081, 2083)
HIDDEN_EMPTY_RAW_SHA256 = (
    "0038CA1937A1B5DCFBA94D6308D6CD50F2C8D89CE23746AD51EE896ABC552850"
)

# These are actual 014A closure roots, not ordinally inferred IDs.
FULL_TERMINAL_GROUPS = {
    718: tuple(range(2072, 2079)),
    724: tuple(range(2079, 2086)),
    730: tuple(range(2086, 2093)),
    736: tuple(range(2093, 2100)),
    742: tuple(range(2100, 2107)),
    748: tuple(range(2107, 2114)),
    754: tuple(range(2114, 2121)),
    760: tuple(range(2121, 2128)),
    766: tuple(range(2128, 2135)),
    772: tuple(range(2135, 2142)),
    778: tuple(range(2142, 2149)),
    784: tuple(range(2149, 2156)),
    790: tuple(range(2156, 2163)),
}

# Each PK group was found by an independent exact seven-literal reverse search.
# The resulting record delta happens to be uniform, but no fixed offset is used
# to construct the mapping.
PK_FULL_TERMINAL_GROUPS = {
    730: tuple(range(2140, 2147)),
    736: tuple(range(2147, 2154)),
    742: tuple(range(2154, 2161)),
    748: tuple(range(2161, 2168)),
    754: tuple(range(2168, 2175)),
    760: tuple(range(2175, 2182)),
    766: tuple(range(2182, 2189)),
    772: tuple(range(2189, 2196)),
    778: tuple(range(2196, 2203)),
    784: tuple(range(2203, 2210)),
    790: tuple(range(2210, 2217)),
    796: tuple(range(2217, 2224)),
    802: tuple(range(2224, 2231)),
}
PK_ROOT_BY_BASE = {
    718: 730,
    724: 736,
    730: 742,
    736: 748,
    742: 754,
    748: 760,
    754: 766,
    760: 772,
    766: 778,
    772: 784,
    778: 790,
    784: 796,
    790: 802,
}
PK_RECORD_MAP = {
    base_record_id: pk_record_id
    for base_root, base_record_ids in FULL_TERMINAL_GROUPS.items()
    for base_record_id, pk_record_id in zip(
        base_record_ids,
        PK_FULL_TERMINAL_GROUPS[PK_ROOT_BY_BASE[base_root]],
        strict=True,
    )
}

EXPECTED_SOURCE_MATRICES = {
    718: ("ね", "な", "ね", "な", "ね", "な", "な"),
    724: ("", "な", "", "な", "", "な", "な"),
    730: (
        "ありません",
        "ない",
        "ございません",
        "ございませぬ",
        "ありません",
        "ござらぬ",
        "ない",
    ),
    736: (
        "ません",
        "ぬ",
        "ませぬ",
        "ませぬ",
        "ません",
        "ませぬ",
        "ぬ",
    ),
    742: (
        "ありません",
        "ない",
        "ありません",
        "ありませぬ",
        "ありません",
        "ありませぬ",
        "ない",
    ),
    748: ("ない", "ぬ", "ない", "ぬ", "ない", "ぬ", "ぬ"),
    754: (
        "ありませんでした",
        "なかった",
        "ございませんでした",
        "ございませなんだ",
        "ありませんでした",
        "ございませんでした",
        "なかった",
    ),
    760: (
        "ませんでした",
        "なかった",
        "ませんでした",
        "ませなんだ",
        "ませんでした",
        "ませんでした",
        "なかった",
    ),
    766: (
        "ないでしょう",
        "なかろう",
        "ござりますまい",
        "ござりますまい",
        "ないでしょう",
        "ありますまい",
        "なかろう",
    ),
    772: (
        "なければ",
        "なければ",
        "なければ",
        "なければ",
        "なきゃ",
        "なければ",
        "なければ",
    ),
    778: (
        "なされ",
        "なされ",
        "なされ",
        "なされ",
        "なされ",
        "なされ",
        "す",
    ),
    784: (
        "なされて",
        "なされて",
        "なされて",
        "なされて",
        "なされて",
        "なされて",
        "して",
    ),
    790: ("なぞ", "など", "なぞ", "なぞ", "など", "など", "ごとき"),
}
EXPECTED_FULL_BASE_JP = {
    record_id: source
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, source in zip(
        record_ids,
        EXPECTED_SOURCE_MATRICES[root],
        strict=True,
    )
}

TRANSLATION_MATRICES = {
    718: ("지요", "군", "지요", "군", "지요", "군", "군"),
    724: ("", "군", "", "군", "", "군", "군"),
    730: (
        "없습니다",
        "없다",
        "없사옵니다",
        "없사옵니다",
        "없습니다",
        "없소",
        "없다",
    ),
    736: (
        "하지 않습니다",
        "하지 않는다",
        "하지 않사옵니다",
        "하지 않사옵니다",
        "하지 않습니다",
        "하지 않사옵니다",
        "하지 않는다",
    ),
    742: (
        "없습니다",
        "없다",
        "없습니다",
        "없사옵니다",
        "없습니다",
        "없사옵니다",
        "없다",
    ),
    748: (
        "하지 않는다",
        "하지 않는다",
        "하지 않는다",
        "하지 않는다",
        "하지 않는다",
        "하지 않는다",
        "하지 않는다",
    ),
    754: (
        "없었습니다",
        "없었다",
        "없었사옵니다",
        "없었사옵니다",
        "없었습니다",
        "없었사옵니다",
        "없었다",
    ),
    760: (
        "하지 않았습니다",
        "하지 않았다",
        "하지 않았습니다",
        "하지 않았사옵니다",
        "하지 않았습니다",
        "하지 않았습니다",
        "하지 않았다",
    ),
    766: (
        "없겠지요",
        "없으리",
        "없겠사옵니다",
        "없겠사옵니다",
        "없겠지요",
        "없겠소",
        "없으리",
    ),
    772: (
        "지 않으면",
        "지 않으면",
        "지 않으면",
        "지 않으면",
        "지 않으면",
        "지 않으면",
        "지 않으면",
    ),
    778: ("하시", "하시", "하시", "하시", "하시", "하시", "하"),
    784: (
        "하시는 것",
        "하시는 것",
        "하시는 것",
        "하시는 것",
        "하시는 것",
        "하시는 것",
        "하는 것",
    ),
    790: ("따위", "따위", "따위", "따위", "따위", "따위", "따위"),
}
FULL_TRANSLATION_POLICY = {
    record_id: translation
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, translation in zip(
        record_ids,
        TRANSLATION_MATRICES[root],
        strict=True,
    )
}
TRANSLATIONS_BY_RECORD = {
    record_id: FULL_TRANSLATION_POLICY[record_id]
    for record_id in RECORD_IDS
}
TRANSLATIONS = {
    f"0:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}
BOUNDARY_TRANSLATION_POLICY = {
    record_id: FULL_TRANSLATION_POLICY[record_id]
    for record_id in FULL_RECORD_IDS
    if record_id not in RECORD_IDS
}

TARGET_ARCHIVE_DIGESTS = {
    "base_jp": "7D234FA98393822E5D5F13F250A63731593C04D77AF2578C8F07B0BA0F5DCD5E",
    "base_current": "AD182398530EE0769D7607347A2DC7F918D07335062B1F4E127A648CF0D1F8D0",
    "base_sc": "D8544639C9E53495FB72855C7B7DCD183BA860C44A62012D46E936C46862A3BB",
    "base_tc": "D8544639C9E53495FB72855C7B7DCD183BA860C44A62012D46E936C46862A3BB",
    "pk_jp": "9800B033CE229D8B662E78BB39DC0F4266D06ACB80BE1572729A07EE2F758624",
    "pk_current": "7CCE4C960517365F975D76B907B117BC70D208A77CD5EC03F794287AC526B23C",
    "pk_sc": "0B3520A12D102ADF2520280F1D6553A4FCCC2793C90D6A29DD1AB2D065031950",
    "pk_tc": "0B3520A12D102ADF2520280F1D6553A4FCCC2793C90D6A29DD1AB2D065031950",
    "pk_en": "0B3520A12D102ADF2520280F1D6553A4FCCC2793C90D6A29DD1AB2D065031950",
}
FULL_ARCHIVE_DIGESTS = {
    "base_jp": "FECD395CCAC24F5E9635660C037F594778B3BD95D9D6181522FBCBB0BE33DE88",
    "base_current": "908B0518852726F7CE07DBFD5AF242782A3E802630249CE3BA09D3EF0A376E90",
    "base_sc": "7515A5ABC7FDA0A9B4BA95E94D03318A3DB32B44DE555C7EBA4E74D5C3602D77",
    "base_tc": "7515A5ABC7FDA0A9B4BA95E94D03318A3DB32B44DE555C7EBA4E74D5C3602D77",
    "pk_jp": "4437DE6CA840E513947D0BC019B8CC7A3C8F8EA2EEEA1E57C0E0EEC557F95092",
    "pk_current": "7F4BD1AC7FCB95C48250794ECBF6724100E3B7A3C75C0DD7072ACC79E1B6CB63",
    "pk_sc": "C5FCD8F0BC25DA0EF8C83E2D7C71543FAE26620934FAF0606E64BF754987BF70",
    "pk_tc": "C5FCD8F0BC25DA0EF8C83E2D7C71543FAE26620934FAF0606E64BF754987BF70",
    "pk_en": "C5FCD8F0BC25DA0EF8C83E2D7C71543FAE26620934FAF0606E64BF754987BF70",
}
JUMP_EVIDENCE = {
    "base_jp": {
        "target": (67, "C7F90E7D6CE337991F379F69558A9856CB3CED11E1BEBBA211D62607930E9616"),
        "full": (91, "5FF6F2A4DEFC1600AB6A20C54425E7CB6410DA0F45C824162445DBE6F165F078"),
    },
    "base_current": {
        "target": (67, "C7F90E7D6CE337991F379F69558A9856CB3CED11E1BEBBA211D62607930E9616"),
        "full": (91, "5FF6F2A4DEFC1600AB6A20C54425E7CB6410DA0F45C824162445DBE6F165F078"),
    },
    "pk_jp": {
        "target": (67, "584CE2583C0BE79D9F95EC19662CC453B88ADA319482B36F9DB5DA7964D69AC3"),
        "full": (91, "BE3922836AE71F56C76B3614F9907B2225DB3CB07FF4EF4EE5E4C9D09A684647"),
    },
    "pk_current": {
        "target": (67, "584CE2583C0BE79D9F95EC19662CC453B88ADA319482B36F9DB5DA7964D69AC3"),
        "full": (91, "BE3922836AE71F56C76B3614F9907B2225DB3CB07FF4EF4EE5E4C9D09A684647"),
    },
}

EMPTY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EMPTY_EVIDENCE = (0, EMPTY_SHA256)
EVIDENCE_ROOTS = (
    718,
    724,
    730,
    731,  # live two-terminal subroot inside Base root 730
    736,
    742,
    748,
    754,
    760,
    766,
    772,
    778,
    784,
    790,
)
ACTUAL_CALL_ROOT = {
    "base": {
        718: 718,
        724: 724,
        730: 730,
        731: 731,
        736: 736,
        742: 742,
        748: 748,
        754: 754,
        760: 760,
        766: 766,
        772: 772,
        778: 778,
        784: 784,
        790: 790,
    },
    "pk": {
        718: 730,
        724: 736,
        730: 742,
        731: 743,
        736: 748,
        742: 754,
        748: 760,
        754: 766,
        760: 772,
        766: 778,
        772: 784,
        778: 790,
        784: 796,
        790: 802,
    },
}
CALLER_ROW_EVIDENCE = {
    "base_jp": (216, "8DFF2558DF0F8DD273A683BD1DCC7ECC480574FCE3EC1797DAA1AF447D75448C"),
    "base_current": (174, "75ED72BD54586BA898AB04CF9A258E33062294BB1AB926C5B2224256BF9C6453"),
    "pk_jp": (387, "AF15705C53FB33C89ADA764742E552A701F8E0DFFDCDEA388DE6FB003CDC55EC"),
    "pk_current": (340, "C84FDC74F7E802B51C7F12268E6D147B01B9362083F7D2D0BC5828CED3AE6FDF"),
}


def evidence(
    overrides: dict[int, tuple[int, str]],
) -> dict[int, tuple[int, str]]:
    return {
        root: overrides.get(root, EMPTY_EVIDENCE)
        for root in EVIDENCE_ROOTS
    }


CALL_EVIDENCE = {
    "base_jp": evidence(
        {
            718: (9, "CE5C532CCE1DE24720CEEA5D59EB39FB43F5564B01C822EA37A13EC0B03A6F70"),
            724: (3, "AB93F4C33B23A605E62FA3F284BF083AA9C0128191C82F6D51A0A9B4283FEC77"),
            730: (71, "7D56EAF67A2959D80ACE5B21CC1007008DD5838ACE12029A8FED0E372DC6779F"),
            731: (2, "71C25D82AF66B5D22A7774452E920C7E4819B7CD38B8AC4B71899AA644B8A003"),
            736: (68, "76F5C6CE1BCCE421A512C56E09FD7CF9C02836DFAF75DFA5329A3E453C3FBF35"),
            742: (6, "4C0823E6EC256A95C29914B3C7D087611EBDFA8D78D9D407074C268934D19E1F"),
            748: (6, "A44A03ADD615387F4A9E07C32F22D62EFA846586D3F583D306091E4E79642741"),
            754: (5, "06865F117F3E53D635D3116146D7E0660639BD2782EB8B433B49977A91758AFD"),
            760: (29, "4ADD4BC582B9D9FC033D832DFE26994E4D4A7DAA2B74A8DA49FD2083D495F5F9"),
            766: (6, "CF660E4CE2E86D401E4C66276C24157F50989D113F02F0C0FB599D7288DFECC8"),
            772: (9, "04BC20487C36B321263F20020015927535AD0A2ACC16DE43691C891DA66F14F8"),
            784: (2, "6EF436FBF42971915C6AFA547E7A886746CDD3DA4E76669FD6CCCCA3DD9FD1EF"),
        }
    ),
    "base_current": evidence(
        {
            718: (5, "157F7EC4497100F26301EEEC63FEF966E18D3A8BD6F73CED070070FC15650FEB"),
            724: (3, "AB93F4C33B23A605E62FA3F284BF083AA9C0128191C82F6D51A0A9B4283FEC77"),
            730: (50, "978C67CF805A93DCDA093E6E8764794D248DAF000BB8483936EF737032C49ECA"),
            731: (2, "71C25D82AF66B5D22A7774452E920C7E4819B7CD38B8AC4B71899AA644B8A003"),
            736: (57, "CF5115068001C7492D337DB463A080E97526D25F17ADB5834A3C63CDB9817E1C"),
            742: (6, "4C0823E6EC256A95C29914B3C7D087611EBDFA8D78D9D407074C268934D19E1F"),
            748: (5, "1A175AA43F4DB446EFBCA83954C61236898E8840B0FE83D4A547EA9885FD4FC5"),
            754: (5, "06865F117F3E53D635D3116146D7E0660639BD2782EB8B433B49977A91758AFD"),
            760: (28, "14C9FE6EAB0FD93AA2E573172DCFC6D04FB2A484C88D8E20D679838298382FBC"),
            766: (4, "EC2E3E1B8B4B2AAC2372045B2393AC50EACA81B76D690687F61870F945AAB10A"),
            772: (7, "63E4ECE2E12F1730C85B7A9EA0CB571C675523E3FC0CB5F7AB48D3251143818C"),
            784: (2, "6EF436FBF42971915C6AFA547E7A886746CDD3DA4E76669FD6CCCCA3DD9FD1EF"),
        }
    ),
    "pk_jp": evidence(
        {
            718: (46, "C69AC1D5E9BCC9FDC5733E2A0D96F57B82C92B0B8D2BE1BBC1972E95DE728280"),
            724: (17, "40C04B6B875A70DF08569BEE4F89E2AFC298B678F8D6F8C36DA28DC5EF26502D"),
            730: (80, "53AAD0CBE99A1A5A9ED8E225D8E23B93B46979F2DAAEA126612E47642E38DE73"),
            731: (2, "9562371C8B4A1C7C93BC429DBED974BD2D3D8A1FD958009DC14B73E71E9D860D"),
            736: (114, "00DC836BA744263C2A00A85C36C8B23C3772D822B9B76F94394557E6A74D26E2"),
            742: (30, "695C929EE4AA938833BC7F97AFDA68A92FF4B816593E27121EB78BC5548C7C1D"),
            748: (35, "B2CE7295728A1168A9BD45609B7F304980B6DDFFFA383F6359F5E9A93FA6704D"),
            754: (5, "027F786DC58C3B7C8D7B9DA7C3E5978CB91D88191B406425FDDF5B64809E9D5E"),
            760: (33, "94382B25A628A5BE4243B5F198ADA66B1803EA4673E8E1F5BFDAE273CB2BDF99"),
            766: (13, "75EC8745832553109ACACB168AD862E730772E0F586D4DA8976F6DA0B15C975B"),
            772: (9, "EC3B6DA57FF4475C5D24120D8D7A8510992AC171F6EC11F01A441E55F953CA87"),
            778: (1, "CF510AE5391094378664DFDDB202659EC03E34C4F16492C41DEBBCFE4AB3C4D2"),
            784: (2, "B4AE21D29A6BBEEABFDAB2E3F57DDC755ED7A76AB7B55B8DE25E98AEDAB5EC5C"),
        }
    ),
    "pk_current": evidence(
        {
            718: (41, "1B3D50BB1C47C6C093F9A6A64532111463AD02E2C18BB96E18FE7B3C60B10694"),
            724: (17, "40C04B6B875A70DF08569BEE4F89E2AFC298B678F8D6F8C36DA28DC5EF26502D"),
            730: (59, "C6E3CF79B76541C3BE52E7E8F7C9C262887FDC3D59328EA698FA0ED34C3B4E9F"),
            731: (2, "9562371C8B4A1C7C93BC429DBED974BD2D3D8A1FD958009DC14B73E71E9D860D"),
            736: (102, "9CD022CF7F43F7D8986D66E545CF9F5A22F710A4EB2FA0B15822F5F0EBD80BAC"),
            742: (29, "FC5E46EF777A7586D63DAA3DBC467CEB5FC86C33221788A2B93814A43ACD5290"),
            748: (32, "D320D959EE2DBDE90442202F907D3E1AF65F1AFAFE83D5D2BE81E0A370CB462B"),
            754: (5, "027F786DC58C3B7C8D7B9DA7C3E5978CB91D88191B406425FDDF5B64809E9D5E"),
            760: (32, "A750564C629533F420CA8E078722C9652B3CDA4A2DDA7C1D5B75322508295A61"),
            766: (11, "9E090D97080EA7A30951E7412E78EC3DE71E4CBFA1F8B41397655651161499B0"),
            772: (7, "AEC299065F3EC471CF221987B2B0093F42E2CECEC647B81CEB41F5B548A1A33A"),
            778: (1, "CF510AE5391094378664DFDDB202659EC03E34C4F16492C41DEBBCFE4AB3C4D2"),
            784: (2, "B4AE21D29A6BBEEABFDAB2E3F57DDC755ED7A76AB7B55B8DE25E98AEDAB5EC5C"),
        }
    ),
}

FLATTEN_EVIDENCE = {
    "base": evidence(
        {
            718: (4, "91AA6D900BFDCDBAB0693052C6012497360777B51F8C205F633242A0D60AF23D"),
            730: (21, "E2EB1282A2505847BFAF4A9EA89E4BC138E3770657CF181DB716D7B1551AD417"),
            736: (11, "3CA552F9C94ED3D06DC32F44F895D08DED6CA5E7FF5B0D711842436FF4C3595B"),
            748: (1, "30FF88E9F47DB0929FFEE23DBE03463F1D08BA14589DD9B42E99D8A4E3DCC2E6"),
            760: (1, "9C8820A26C8C70321A45DC263588A18638244E5B89342C0B7746F77AD963F7D0"),
            766: (2, "3628D3FAF8A4DC442F19FAFD3B02B83016059D82146B45D7671BAFB479C7230A"),
            772: (2, "55BEB68054C71AC2F623AD6A0BB7B3F5A1F6BBE90EF1858F30824902965E7485"),
        }
    ),
    "pk": evidence(
        {
            718: (5, "A1FA1443A8605C8642C1825189E74991BA2ADBDB8E678EBFC0EDA29BB6DBEDCD"),
            730: (21, "346B4C43D38C2FE09F455F067DAF52C94CA7F4C765D02C7EC069E39F1398973B"),
            736: (12, "508BB684B1B5F96846A3B628F176095B970618F3164DF61DCA71F3E9AA14BA38"),
            742: (1, "A195F35993E10200923779D6F4203E519B8EB07FC48EDD9D6318630594D7EE75"),
            748: (3, "7D62C6B8C935E9D16E911FB95C09792A0ED8DC816863608EC74DFE8AEF3C32FE"),
            760: (1, "C23C7D84AA16D7D3DBD12233E08451D8890FEA9538A13A47A8D1EC449285AD54"),
            766: (2, "219E27426E47A127C78DA487C590729C34225F8D026E23AB7032178AC0430EBD"),
            772: (2, "6306094EA2C956FAA6E89C4FFDDC124240E8118E2F0B369B27DD8F75767DAF23"),
        }
    ),
}

FIXED_FOLLOWING_EVIDENCE = {
    "base_jp": evidence(
        {
            730: (16, "E7C69CD0D8688DB96C4C7CBBC967DE743E70770218B3EFB8246A46292151D908"),
            736: (19, "EFDF0D6C7AF25B03CAB841D154A9D22A4BC1B3B4860C205891BA86C36EBF0DEC"),
            748: (6, "3FB8460FDA0DD4D0FB769677DAF9280DAB5F5EF3E42E8C1406752494AEB6C27E"),
            760: (25, "7D10CA0B8024DB549E870CB3818CEF9CE03449359A1A0FF4201414865FAA0B46"),
            772: (3, "69F7A756ABBEC7E1EE4F73D112EF67E55C27F07B7D9A99932880C0262EFCA5DB"),
            784: (2, "C95A20692040E75783BDD318E9B06CF12DC42FCC048FBF101673920B9C0DE3A7"),
        }
    ),
    "base_current": evidence(
        {
            730: (13, "792EB9EA9EA76CA5B0FAFE79502926454CFB02BC21CD594220D021EABE5E8C4D"),
            736: (19, "EFDF0D6C7AF25B03CAB841D154A9D22A4BC1B3B4860C205891BA86C36EBF0DEC"),
            748: (5, "FFEC47229B54C36C477B88C1B9E14DB856A525BAE847292C8349DD820A0C9E78"),
            760: (25, "7D10CA0B8024DB549E870CB3818CEF9CE03449359A1A0FF4201414865FAA0B46"),
            772: (3, "69F7A756ABBEC7E1EE4F73D112EF67E55C27F07B7D9A99932880C0262EFCA5DB"),
            784: (2, "C95A20692040E75783BDD318E9B06CF12DC42FCC048FBF101673920B9C0DE3A7"),
        }
    ),
    "pk_jp": evidence(
        {
            730: (19, "465884CD157F01689150709FA7BA4F76D64F6EAD1AF354FE984CF35765A40238"),
            736: (46, "E4554CB3FC9640CA6225A141F825F6AB3FD053075B6E4B7529D59E02C6B85DBB"),
            742: (9, "0184B5B183B9FD317F1DCC12AAD65BFFD8782E16E4BFBCA682CD38BCA675AFA2"),
            748: (31, "829EB42C02854AD0CE42865293382CECA3949624EFE0EBDC27324607523D3B38"),
            760: (26, "70ECB87879BB47BCB6885DA4D7FEA229BD19C78E63C961F6417139FFF1ED25A8"),
            766: (1, "A03DA1EC07174025B191DC8173029BC2E24E3906A4A384BA47E1D1A711E4981A"),
            772: (3, "542C0FE35420972D2C2F6457F3A2CF6661EBD3069D469D9D3BA4C8D7ADC03AAB"),
            778: (1, "CC1E14E2062D07FF5DD63C0B6C7FA6E975EC9DECD8BCEC1DF8E68472D1C60550"),
            784: (2, "884ECF78E730DFC56EBAD7B68F553A7031E7EF7E565C856FAB82524A9EE9EE43"),
        }
    ),
    "pk_current": evidence(
        {
            724: (1, "F30C384CD12042D6F322A90F8479D2121D168FC4BCAEECD057705F1BEB870F94"),
            730: (16, "595F422DA6A8F60A8F001C206C32FF070177135F88662A1F862E190B6E8132DC"),
            736: (44, "7631FE96D1416C8BB39EDD71AB52583B7374C0A411D26DBADFFBE850B0DD01AE"),
            742: (8, "5DA185AC42921037BA5AF4ECA31D339B904E263C68F331AF52B7E674BB863476"),
            748: (29, "6FD91C5DBAB3691277DD2D39D3D6945293524FC91EE6CE5282228A5180D3C342"),
            760: (26, "70ECB87879BB47BCB6885DA4D7FEA229BD19C78E63C961F6417139FFF1ED25A8"),
            766: (1, "A03DA1EC07174025B191DC8173029BC2E24E3906A4A384BA47E1D1A711E4981A"),
            772: (3, "542C0FE35420972D2C2F6457F3A2CF6661EBD3069D469D9D3BA4C8D7ADC03AAB"),
            778: (1, "CC1E14E2062D07FF5DD63C0B6C7FA6E975EC9DECD8BCEC1DF8E68472D1C60550"),
            784: (2, "884ECF78E730DFC56EBAD7B68F553A7031E7EF7E565C856FAB82524A9EE9EE43"),
        }
    ),
}

INTEGRATION_NOTE_BY_ROOT = {
    718: (
        "confirmation particle; preserve soft jiyo versus plain geun "
        "register after caller normalization"
    ),
    724: (
        "sentence-final na particle; hidden voice slots remain byte-exact "
        "and visible slots use plain geun"
    ),
    730: (
        "existential absence predicate; normalize each caller to a Korean "
        "noun or existential frame before attaching the complete ending"
    ),
    736: (
        "generic negative predicate; rewrite caller lexical material before "
        "attaching the complete Korean action-negative ending"
    ),
    742: (
        "existential absence predicate; preserve ordinary versus archaic "
        "polite register in the seven-voice matrix"
    ),
    748: (
        "plain generic negative predicate; caller-specific lexical rewrite "
        "is required before the complete Korean ending"
    ),
    754: (
        "past existential absence predicate; preserve ordinary, plain, and "
        "archaic-polite voice distinctions"
    ),
    760: (
        "past generic negative predicate; source/current flattened callers "
        "and fixed following text require caller-specific rewrites"
    ),
    766: (
        "negative conjectural existential predicate; live callers express "
        "no fault, no alternative, no prospect, or no possibility"
    ),
    772: (
        "conditional negative suffix; retain the caller's Korean lexical "
        "stem and attach ji aneumyeon during integration"
    ),
    778: (
        "attributive honorific/plain verb stem, not an imperative; the live "
        "PK caller must change fixed left text from chuljinhada stem to the "
        "noun chuljin before hashi/ha plus fixed neun"
    ),
    784: (
        "proposal nominalization, not a sequential connective; live fixed "
        "assembly is jeopgyeon + hasineun geot/haneun geot + eun(neun) "
        "eotteo"
    ),
    790: (
        "disparaging comparison particle; all seven attested forms are "
        "covered by ttawi"
    ),
}

BASIS = (
    "review_queue_base_msggame_B005_pristine_base_pc_jp_sole_authority_"
    "block0_visible_runtime_terminal_records2084_2150_hidden2083_excluded_"
    "and_raw_exact_complete_thirteen_seven_voice_groups2072_2162_actual_"
    "base_roots718_790_pk_roots730_802_unique_exact_seven_literal_tuple_"
    "reverse_search_without_fixed_offset_assumption_discovered_uniform_"
    "delta68_nonordinal_live_subroot731_743_target_and_boundary_014a_"
    "closures_0143_caller_rows_source_current_flattening_fixed_following_"
    "digests_no_relevant_valid_standalone_014c_existential_generic_"
    "negative_past_conjectural_conditional_register_matrices_nasare_"
    "attributive_not_imperative_nasarete_proposal_nominalization_"
    "runtime_caller_integration_pending_pc_pk_auxiliary_context_only_no_"
    "historic_or_switch_korean_authority_one_line_reverse_overlay_no_"
    "steam_write"
)


def literal_texts(
    records: dict[tuple[int, int], Any],
    key: tuple[int, int],
) -> tuple[str, ...]:
    return PRIOR.literal_texts(records, key)


def gap_bytes(record: Any) -> tuple[bytes, ...]:
    return PRIOR.gap_bytes(record)


def archive_records(
    prepared: Any,
) -> dict[str, dict[tuple[int, int], Any]]:
    return PRIOR.archive_records(prepared)


def digest_json(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, separators=(",", ":")).encode("ascii")
    ).hexdigest().upper()


def digest_sites(sites: tuple[str, ...]) -> str:
    return hashlib.sha256(
        "\n".join(sites).encode("ascii")
    ).hexdigest().upper()


def sequence_starts(
    records: dict[tuple[int, int], Any],
    expected: tuple[str, ...],
) -> tuple[int, ...]:
    block_ids = sorted(
        record_id
        for block_id, record_id in records
        if block_id == BLOCK_ID
    )
    single = {
        record_id: literal_texts(records, (BLOCK_ID, record_id))[0]
        for record_id in block_ids
        if len(literal_texts(records, (BLOCK_ID, record_id))) == 1
    }
    return tuple(
        start
        for start in block_ids
        if all(
            single.get(start + index) == text
            for index, text in enumerate(expected)
        )
    )


def assert_corpora(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    target_base_keys = tuple((BLOCK_ID, value) for value in RECORD_IDS)
    target_pk_keys = tuple(
        (BLOCK_ID, PK_RECORD_MAP[value]) for value in RECORD_IDS
    )
    full_base_keys = tuple((BLOCK_ID, value) for value in FULL_RECORD_IDS)
    full_pk_keys = tuple(
        (BLOCK_ID, PK_RECORD_MAP[value]) for value in FULL_RECORD_IDS
    )
    for label, records in records_by_label.items():
        target_keys = (
            target_pk_keys if label.startswith("pk_") else target_base_keys
        )
        full_keys = (
            full_pk_keys if label.startswith("pk_") else full_base_keys
        )
        if (
            GENERAL.subset_digest(records, target_keys)
            != TARGET_ARCHIVE_DIGESTS[label]
            or GENERAL.subset_digest(records, full_keys)
            != FULL_ARCHIVE_DIGESTS[label]
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} target/boundary corpus drifted"
            )

    if (
        set(PK_RECORD_MAP) != set(FULL_RECORD_IDS)
        or 2083 in RECORD_IDS
        or len(RECORD_IDS) != 67
    ):
        raise RuntimeError(f"segment {SEGMENT} record universe drifted")

    for base_root, base_record_ids in FULL_TERMINAL_GROUPS.items():
        expected_tuple = EXPECTED_SOURCE_MATRICES[base_root]
        pk_root = PK_ROOT_BY_BASE[base_root]
        pk_record_ids = PK_FULL_TERMINAL_GROUPS[pk_root]
        starts = sequence_starts(records_by_label["pk_jp"], expected_tuple)
        if starts != (pk_record_ids[0],):
            raise RuntimeError(
                f"segment {SEGMENT} unique PK tuple search drifted: "
                f"{base_root}/{starts}"
            )
        if tuple(
            PK_RECORD_MAP[record_id] for record_id in base_record_ids
        ) != pk_record_ids:
            raise RuntimeError(
                f"segment {SEGMENT} explicit PK group map drifted: "
                f"{base_root}/{pk_root}"
            )

    for record_id in FULL_RECORD_IDS:
        base_key = (BLOCK_ID, record_id)
        pk_key = (BLOCK_ID, PK_RECORD_MAP[record_id])
        if literal_texts(
            records_by_label["base_jp"],
            base_key,
        ) != (EXPECTED_FULL_BASE_JP[record_id],):
            raise RuntimeError(
                f"segment {SEGMENT} pristine Base JP drifted: {base_key}"
            )
        for label, key in (
            ("base_jp", base_key),
            ("base_current", base_key),
            ("base_sc", base_key),
            ("base_tc", base_key),
            ("pk_jp", pk_key),
            ("pk_current", pk_key),
            ("pk_sc", pk_key),
            ("pk_tc", pk_key),
            ("pk_en", pk_key),
        ):
            if (
                len(literal_texts(records_by_label[label], key)) != 1
                or gap_bytes(records_by_label[label][key])
                != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} skeleton drifted: {label}/{key}"
                )
        for language in ("jp", "current", "sc", "tc"):
            if (
                literal_texts(
                    records_by_label[f"base_{language}"],
                    base_key,
                )
                != literal_texts(
                    records_by_label[f"pk_{language}"],
                    pk_key,
                )
                or gap_bytes(
                    records_by_label[f"base_{language}"][base_key]
                )
                != gap_bytes(
                    records_by_label[f"pk_{language}"][pk_key]
                )
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base/PK auxiliary mapping "
                    f"drifted: {language}/{base_key}/{pk_key}"
                )
        if literal_texts(records_by_label["pk_en"], pk_key) != ("",):
            raise RuntimeError(
                f"segment {SEGMENT} PK EN context drifted: {pk_key}"
            )

    for record_id in HIDDEN_BOUNDARY_RECORD_IDS:
        for label, records in records_by_label.items():
            actual_id = (
                PK_RECORD_MAP[record_id]
                if label.startswith("pk_")
                else record_id
            )
            key = (BLOCK_ID, actual_id)
            if (
                hashlib.sha256(records[key].data).hexdigest().upper()
                != HIDDEN_EMPTY_RAW_SHA256
                or literal_texts(records, key) != ("",)
                or gap_bytes(records[key]) != (b"", b"\x05\x05\x05")
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} hidden boundary record drifted: "
                    f"{label}/{key}"
                )


def relevant_standalone_014c(
    records: dict[tuple[int, int], Any],
    target_ids: set[int],
) -> tuple[tuple[int, int, int, int, int], ...]:
    edges = GRAPH.graph_edges(records)
    relevant: list[tuple[int, int, int, int, int]] = []
    for (block_id, record_id), record in sorted(records.items()):
        for gap_id, gap in enumerate(gap_bytes(record)):
            jump_spans = [
                range(match.start(), match.end())
                for match in GRAPH.MORPHOLOGY_JUMP_RE.finditer(gap)
            ]
            for match in GRAPH.MORPHOLOGY_014C_RE.finditer(gap):
                if any(match.start() in span for span in jump_spans):
                    continue
                operand = struct.unpack("<I", match.group(1))[0]
                if GRAPH.graph_closure(edges, operand).intersection(
                    target_ids
                ):
                    relevant.append(
                        (
                            block_id,
                            record_id,
                            gap_id,
                            match.start(),
                            operand,
                        )
                    )
    return tuple(relevant)


def assert_runtime_graph(
    records_by_label: dict[str, dict[tuple[int, int], Any]],
) -> None:
    full_base_ids = set(FULL_RECORD_IDS)
    full_pk_ids = {PK_RECORD_MAP[value] for value in FULL_RECORD_IDS}
    target_base_ids = set(RECORD_IDS)
    target_pk_ids = {PK_RECORD_MAP[value] for value in RECORD_IDS}

    for label in ("base_jp", "base_current", "pk_jp", "pk_current"):
        edition = label.split("_", 1)[0]
        records = records_by_label[label]
        target_ids = target_pk_ids if edition == "pk" else target_base_ids
        full_ids = full_pk_ids if edition == "pk" else full_base_ids
        for scope, ids in (("target", target_ids), ("full", full_ids)):
            rows = GRAPH.incoming_jump_rows(records, ids)
            expected_count, expected_sha256 = JUMP_EVIDENCE[label][scope]
            if (
                len(rows) != expected_count
                or digest_json(rows) != expected_sha256
                or {row[4] for row in rows} != ids
                or any(
                    sum(row[4] == target for row in rows) != 1
                    for target in ids
                )
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} {scope} "
                    "incoming 014A drifted"
                )

        edges = GRAPH.graph_edges(records)
        for base_root, base_record_ids in FULL_TERMINAL_GROUPS.items():
            actual_root = (
                PK_ROOT_BY_BASE[base_root]
                if edition == "pk"
                else base_root
            )
            expected_ids = (
                set(
                    PK_FULL_TERMINAL_GROUPS[
                        PK_ROOT_BY_BASE[base_root]
                    ]
                )
                if edition == "pk"
                else set(base_record_ids)
            )
            closure = GRAPH.graph_closure(edges, actual_root).intersection(
                full_ids
            )
            if closure != expected_ids:
                raise RuntimeError(
                    f"segment {SEGMENT} {label} closure drifted: "
                    f"{base_root}/{actual_root}"
                )

        caller_rows, caller_sites = GRAPH.caller_rows(records, full_ids)
        expected_row_count, expected_row_sha256 = CALLER_ROW_EVIDENCE[label]
        if (
            len(caller_rows) != expected_row_count
            or digest_json(caller_rows) != expected_row_sha256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} 0143 caller rows drifted"
            )
        expected_actual_roots = {
            ACTUAL_CALL_ROOT[edition][logical_root]
            for logical_root, (count, _) in CALL_EVIDENCE[label].items()
            if count
        }
        if set(caller_sites) != expected_actual_roots:
            raise RuntimeError(
                f"segment {SEGMENT} {label} caller root universe drifted"
            )
        for logical_root in EVIDENCE_ROOTS:
            actual_root = ACTUAL_CALL_ROOT[edition][logical_root]
            sites = caller_sites.get(actual_root, ())
            expected_count, expected_sha256 = CALL_EVIDENCE[label][
                logical_root
            ]
            if (
                len(sites) != expected_count
                or digest_sites(sites) != expected_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} caller sites drifted: "
                    f"{logical_root}/{actual_root}"
                )

            blockers = FIXED.fixed_following_blockers(
                records,
                actual_root,
            )
            blocker_count, blocker_sha256 = FIXED_FOLLOWING_EVIDENCE[
                label
            ][logical_root]
            if (
                len(blockers) != blocker_count
                or digest_sites(blockers) != blocker_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} fixed-following "
                    f"drifted: {logical_root}/{actual_root}"
                )

        if relevant_standalone_014c(records, full_ids):
            raise RuntimeError(
                f"segment {SEGMENT} {label} relevant standalone "
                "014C appeared"
            )

    for edition in ("base", "pk"):
        full_ids = full_pk_ids if edition == "pk" else full_base_ids
        _, source_sites = GRAPH.caller_rows(
            records_by_label[f"{edition}_jp"],
            full_ids,
        )
        _, current_sites = GRAPH.caller_rows(
            records_by_label[f"{edition}_current"],
            full_ids,
        )
        for logical_root in EVIDENCE_ROOTS:
            actual_root = ACTUAL_CALL_ROOT[edition][logical_root]
            flattened = tuple(
                sorted(
                    set(source_sites.get(actual_root, ()))
                    - set(current_sites.get(actual_root, ()))
                )
            )
            current_only = (
                set(current_sites.get(actual_root, ()))
                - set(source_sites.get(actual_root, ()))
            )
            expected_count, expected_sha256 = FLATTEN_EVIDENCE[
                edition
            ][logical_root]
            if (
                current_only
                or len(flattened) != expected_count
                or digest_sites(flattened) != expected_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition} source/current "
                    f"flattening drifted: {logical_root}/{actual_root}"
                )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        len(RECORD_IDS) != 67
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or translations != TRANSLATIONS
        or set(FULL_TRANSLATION_POLICY) != set(FULL_RECORD_IDS)
        or set(TRANSLATION_MATRICES) != set(FULL_TERMINAL_GROUPS)
        or set(INTEGRATION_NOTE_BY_ROOT) != set(FULL_TERMINAL_GROUPS)
    ):
        raise RuntimeError(f"segment {SEGMENT} translation universe drifted")

    if (
        tuple(
            PREVIOUS_SEGMENT.FULL_TRANSLATION_POLICY[record_id]
            for record_id in range(2072, 2086)
        )
        != TRANSLATION_MATRICES[718] + TRANSLATION_MATRICES[724]
        or tuple(
            NEXT_SEGMENT.FULL_TRANSLATION_POLICY[record_id]
            for record_id in range(2149, 2163)
        )
        != TRANSLATION_MATRICES[784] + TRANSLATION_MATRICES[790]
    ):
        raise RuntimeError(
            f"segment {SEGMENT} adjacent boundary contract drifted"
        )

    for root, record_ids in FULL_TERMINAL_GROUPS.items():
        actual = tuple(
            FULL_TRANSLATION_POLICY[record_id]
            for record_id in record_ids
        )
        if actual != TRANSLATION_MATRICES[root]:
            raise RuntimeError(
                f"segment {SEGMENT} register matrix drifted: {root}"
            )

    if (
        FULL_TRANSLATION_POLICY[2072] != "지요"
        or FULL_TRANSLATION_POLICY[2079] != ""
        or FULL_TRANSLATION_POLICY[2083] != ""
        or TRANSLATIONS_BY_RECORD[2084] != "군"
        or TRANSLATIONS_BY_RECORD[2088] != "없사옵니다"
        or TRANSLATIONS_BY_RECORD[2095] != "하지 않사옵니다"
        or TRANSLATIONS_BY_RECORD[2117] != "없었사옵니다"
        or TRANSLATIONS_BY_RECORD[2124] != "하지 않았사옵니다"
        or TRANSLATIONS_BY_RECORD[2130] != "없겠사옵니다"
        or TRANSLATIONS_BY_RECORD[2135] != "지 않으면"
        or TRANSLATIONS_BY_RECORD[2142] != "하시"
        or TRANSLATIONS_BY_RECORD[2148] != "하"
        or TRANSLATIONS_BY_RECORD[2149] != "하시는 것"
        or FULL_TRANSLATION_POLICY[2155] != "하는 것"
        or FULL_TRANSLATION_POLICY[2162] != "따위"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic correction contract drifted"
        )

    for coordinate, translation in translations.items():
        if (
            not translation
            or "\r" in translation
            or "\n" in translation
            or translation != translation.strip()
            or ENGINE.KANA_OR_HAN_RE.search(translation)
            or UTIL.BANNED_FULLWIDTH_PUNCTUATION.intersection(translation)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} text residue drifted: {coordinate}"
            )


def build_rows() -> tuple[Any, dict[str, str], list[dict[str, object]], str]:
    prepared = ENGINE.prepare_artifacts(
        ENGINE.DEFAULT_STEAM_ROOT,
        ENGINE.DEFAULT_BASE_PRISTINE,
        ENGINE.DEFAULT_PK_PRISTINE,
    )
    records_by_label = archive_records(prepared)
    assert_corpora(records_by_label)
    assert_runtime_graph(records_by_label)

    current = records_by_label["base_current"]
    translations = dict(TRANSLATIONS)
    assert_semantics(translations)
    for coordinate, translation in translations.items():
        _, record_id, _ = (int(value) for value in coordinate.split(":"))
        current_text = literal_texts(current, (BLOCK_ID, record_id))[0]
        if not ENGINE.is_visible_translation_candidate(current_text):
            raise RuntimeError(
                f"segment {SEGMENT} target became non-visible: "
                f"{coordinate}"
            )
        if UTIL.layout_signature(translation) != UTIL.layout_signature(
            current_text
        ):
            raise RuntimeError(
                f"segment {SEGMENT} layout signature drifted: "
                f"{coordinate}"
            )

    candidate_sha256 = GENERAL.assert_overlay_roundtrip(
        prepared,
        segment=SEGMENT,
        translations=translations,
        target_records=set(RECORD_KEYS),
    )
    root_by_record = {
        record_id: root
        for root, record_ids in FULL_TERMINAL_GROUPS.items()
        for record_id in record_ids
        if record_id in RECORD_IDS
    }
    rows: list[dict[str, object]] = []
    for coordinate, translation in translations.items():
        block_id, record_id, literal_id = (
            int(value) for value in coordinate.split(":")
        )
        target = prepared.visible_targets[
            ("base_msggame", block_id, record_id, literal_id)
        ]
        root = root_by_record[record_id]
        pk_root = PK_ROOT_BY_BASE[root]
        pk_record_id = PK_RECORD_MAP[record_id]
        rows.append(
            {
                "schema": ENGINE.DECISION_SCHEMA,
                "resource": "base_msggame",
                "coordinate": coordinate,
                "source_record_raw_sha256": target[
                    "source_record_raw_sha256"
                ],
                "current_ko_utf16le_sha256": target[
                    "current_ko_utf16le_sha256"
                ],
                "translation": translation,
                "semantic_review": "approved",
                "scope_classification": "runtime_fragment_pending",
                "layout_review": "unchanged_from_current",
                "runtime_review": "pending",
                "basis": BASIS,
                "historic_korean_used": False,
                "switch_korean_used": False,
                "runtime_assembly_evidence": {
                    "pk_mapping_method": (
                        "unique_exact_seven_literal_tuple_reverse_search"
                    ),
                    "base_root": root,
                    "pk_semantic_root": pk_root,
                    "base_record_id": record_id,
                    "pk_semantic_record_id": pk_record_id,
                    "automatic_space_inserted": False,
                    "full_terminal_record_ids": list(
                        FULL_TERMINAL_GROUPS[root]
                    ),
                    "pk_full_terminal_record_ids": list(
                        PK_FULL_TERMINAL_GROUPS[pk_root]
                    ),
                    "base_source_call_count": CALL_EVIDENCE[
                        "base_jp"
                    ][root][0],
                    "base_current_call_count": CALL_EVIDENCE[
                        "base_current"
                    ][root][0],
                    "pk_source_call_count": CALL_EVIDENCE[
                        "pk_jp"
                    ][root][0],
                    "pk_current_call_count": CALL_EVIDENCE[
                        "pk_current"
                    ][root][0],
                    "base_source_only_flattened_call_count": (
                        FLATTEN_EVIDENCE["base"][root][0]
                    ),
                    "base_source_only_flattened_call_sha256": (
                        FLATTEN_EVIDENCE["base"][root][1]
                    ),
                    "pk_source_only_flattened_call_count": (
                        FLATTEN_EVIDENCE["pk"][root][0]
                    ),
                    "pk_source_only_flattened_call_sha256": (
                        FLATTEN_EVIDENCE["pk"][root][1]
                    ),
                    "base_current_fixed_following_count": (
                        FIXED_FOLLOWING_EVIDENCE["base_current"][
                            root
                        ][0]
                    ),
                    "base_current_fixed_following_sha256": (
                        FIXED_FOLLOWING_EVIDENCE["base_current"][
                            root
                        ][1]
                    ),
                    "pk_current_fixed_following_count": (
                        FIXED_FOLLOWING_EVIDENCE["pk_current"][
                            root
                        ][0]
                    ),
                    "pk_current_fixed_following_sha256": (
                        FIXED_FOLLOWING_EVIDENCE["pk_current"][
                            root
                        ][1]
                    ),
                    "integration_note": INTEGRATION_NOTE_BY_ROOT[root],
                    "relevant_valid_standalone_014c_count": 0,
                    "runtime_integration_required": True,
                },
            }
        )
    return prepared, translations, rows, candidate_sha256


def main() -> int:
    prepared, translations, rows, candidate_sha256 = build_rows()
    ENGINE.atomic_write(OUTPUT, ENGINE.jsonl(rows))
    validated = ENGINE.validate_decisions(
        prepared,
        OUTPUT,
        require_complete=False,
    )
    if len(validated) != 67 or len(rows) != 67:
        raise RuntimeError(f"segment {SEGMENT} validation count drifted")
    if any(
        row["scope_classification"] != "runtime_fragment_pending"
        or row["runtime_review"] != "pending"
        or row["historic_korean_used"] is not False
        or row["switch_korean_used"] is not False
        for row in rows
    ):
        raise RuntimeError(
            f"segment {SEGMENT} runtime or authority flag drifted"
        )

    current = archive_records(prepared)["base_current"]
    changed = sum(
        translation
        != literal_texts(
            current,
            (BLOCK_ID, int(coordinate.split(":")[1])),
        )[0]
        for coordinate, translation in translations.items()
    )
    discovered_deltas = sorted(
        {
            PK_RECORD_MAP[record_id] - record_id
            for record_id in FULL_RECORD_IDS
        }
    )
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B005_S1016",
                "queue": QUEUE_BATCH_ID,
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "hidden_record_2083_excluded_and_exact": True,
                "hidden_boundary_record_ids": list(
                    HIDDEN_BOUNDARY_RECORD_IDS
                ),
                "pk_mapping_method": (
                    "unique_exact_seven_literal_tuple_reverse_search"
                ),
                "discovered_base_pk_record_deltas": discovered_deltas,
                "base_pk_literal_and_gap_divergence_records": [],
                "pk_en_visible_records": [],
                "full_terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in FULL_TERMINAL_GROUPS.items()
                },
                "pk_full_terminal_groups": {
                    str(root): list(record_ids)
                    for root, record_ids in PK_FULL_TERMINAL_GROUPS.items()
                },
                "pk_root_by_base": PK_ROOT_BY_BASE,
                "boundary_translation_policy": (
                    BOUNDARY_TRANSLATION_POLICY
                ),
                "jump_evidence": JUMP_EVIDENCE,
                "caller_row_evidence": CALLER_ROW_EVIDENCE,
                "call_evidence": CALL_EVIDENCE,
                "flatten_evidence": FLATTEN_EVIDENCE,
                "fixed_following_evidence": (
                    FIXED_FOLLOWING_EVIDENCE
                ),
                "relevant_valid_standalone_014c_count": 0,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
                "outside_scope_records_exact": True,
                "reverse_overlay_exact": True,
                "steam_write_performed": False,
                "output": str(OUTPUT),
            },
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
