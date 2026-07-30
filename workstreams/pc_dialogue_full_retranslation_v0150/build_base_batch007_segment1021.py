#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1021 decisions."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT = Path(__file__).resolve()
WORKSTREAM = SCRIPT.parent
REPO = WORKSTREAM.parents[1]
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))

import build_base_batch005_segment1016 as AUDIT
import build_base_batch006_segment1020 as PRIOR


ENGINE = PRIOR.ENGINE
GENERAL = PRIOR.GENERAL
UTIL = PRIOR.UTIL
GRAPH = PRIOR.GRAPH
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B007_S1021.private.v1.jsonl"
)
SEGMENT = 1021
QUEUE_BATCH_ID = "base_msggame-B007"
BLOCK_ID = 0
RECORD_IDS = tuple(range(2419, 2486))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
FULL_RECORD_IDS = tuple(range(2415, 2492))
PK_RECORD_OFFSET = 68
PK_ROOT_SHIFT = 12

FULL_TERMINAL_GROUPS = {
    1000: tuple(range(2415, 2422)),
    1006: tuple(range(2422, 2429)),
    1012: tuple(range(2429, 2436)),
    1018: tuple(range(2436, 2443)),
    1024: tuple(range(2443, 2450)),
    1030: tuple(range(2450, 2457)),
    1036: tuple(range(2457, 2464)),
    1042: tuple(range(2464, 2471)),
    1048: tuple(range(2471, 2478)),
    1054: tuple(range(2478, 2485)),
    1060: tuple(range(2485, 2492)),
}
PK_FULL_TERMINAL_GROUPS = {
    root + PK_ROOT_SHIFT: tuple(
        record_id + PK_RECORD_OFFSET for record_id in record_ids
    )
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
}
PK_ROOT_BY_BASE = {
    root: root + PK_ROOT_SHIFT for root in FULL_TERMINAL_GROUPS
}
ACTUAL_CALL_ROOTS_BY_BASE = {
    root: ((root, root + 1) if root == 1060 else (root,))
    for root in FULL_TERMINAL_GROUPS
}
ACTUAL_CALL_ROOTS_BY_PK = {
    root: tuple(
        actual_root + PK_ROOT_SHIFT
        for actual_root in ACTUAL_CALL_ROOTS_BY_BASE[root]
    )
    for root in FULL_TERMINAL_GROUPS
}
PK_RECORD_MAP = {
    record_id: record_id + PK_RECORD_OFFSET
    for record_id in FULL_RECORD_IDS
}

SOURCE_MATRICES = {
    1000: (
        "あげました",
        "やった",
        "さしあげました",
        "やりました",
        "あげました",
        "やりました",
        "やった",
    ),
    1006: (
        "やめなさい",
        "やめよ",
        "おやめください",
        "やめなされ",
        "やめてください",
        "やめなされ",
        "やめよ",
    ),
    1012: (
        "あげます",
        "やる",
        "さしあげます",
        "さしあげる",
        "あげます",
        "いただく",
        "やる",
    ),
    1018: (
        "あげなさい",
        "やれ",
        "あげなさい",
        "やりなさい",
        "あげなさい",
        "やるがよい",
        "やれ",
    ),
    1024: (
        "あげましょう",
        "やろう",
        "さしあげましょう",
        "さしあげよう",
        "あげましょう",
        "進ぜよう",
        "やろう",
    ),
    1030: ("ね", "よ", "ね", "よ", "ね", "よ", "よ"),
    1036: (
        "よい",
        "よい",
        "よろしい",
        "よろしい",
        "よろしい",
        "よろしい",
        "よい",
    ),
    1042: (
        "良いですね",
        "良いな",
        "良うございますね",
        "良うございますな",
        "良いですね",
        "良いですな",
        "良いな",
    ),
    1048: (
        "よろしいか",
        "よいか",
        "よろしゅうございますか",
        "よろしゅうございますか",
        "よいでしょうか",
        "ようござるか",
        "よいか",
    ),
    1054: (
        "ましょう",
        "よう",
        "ましょう",
        "ましょう",
        "ましょう",
        "ましょう",
        "よう",
    ),
    1060: (
        "良いでしょう",
        "良かろう",
        "良いでしょう",
        "良いでしょう",
        "良いでしょう",
        "良いでしょう",
        "良かろう",
    ),
}
CURRENT_MATRICES = {
    1000: (
        "주었습니다",
        "해냈다",
        "드렸습니다",
        "해냈습니다",
        "주었습니다",
        "해냈습니다",
        "해냈다",
    ),
    1006: (
        "그만두시오",
        "그만두어라",
        "그만두십시오",
        "그만두시게",
        "그만하십시오",
        "그만두시게",
        "그만두어라",
    ),
    1012: (
        "드립니다",
        "한다",
        "드립니다",
        "드리다",
        "드립니다",
        "받다",
        "한다",
    ),
    1018: (
        "주시오",
        "하라",
        "주시오",
        "하시오",
        "주시오",
        "하는 것이 좋다",
        "하라",
    ),
    1024: (
        "드리겠습니다",
        "하자",
        "드리겠습니다",
        "드리겠소",
        "드리겠습니다",
        "내리겠노라",
        "하자",
    ),
    1030: ("군", "여", "군", "여", "군", "여", "여"),
    1036: ("좋다", "좋다", "좋다", "좋다", "좋다", "좋다", "좋다"),
    1042: (
        "좋군요",
        "좋구나",
        "좋군요",
        "좋습니다그려",
        "좋군요",
        "좋습니다그려",
        "좋구나",
    ),
    1048: (
        "괜찮은가",
        "좋은가",
        "괜찮으시겠습니까",
        "괜찮으시겠습니까",
        "괜찮을까요",
        "괜찮으시겠소",
        "좋은가",
    ),
    1054: (
        "합시다",
        "듯",
        "합시다",
        "합시다",
        "합시다",
        "합시다",
        "듯",
    ),
    1060: (
        "좋겠지요",
        "좋겠다",
        "좋겠지요",
        "좋겠지요",
        "좋겠지요",
        "좋겠지요",
        "좋겠다",
    ),
}
TRANSLATION_MATRICES = {
    1000: (
        "주었습니다",
        "주었다",
        "드렸습니다",
        "주었습니다",
        "주었습니다",
        "주었습니다",
        "주었다",
    ),
    1006: (
        "그만두십시오",
        "그만두어라",
        "그만두십시오",
        "그만두시오",
        "그만두십시오",
        "그만두시오",
        "그만두어라",
    ),
    1012: (
        "줍니다",
        "준다",
        "드립니다",
        "드린다",
        "줍니다",
        "받는다",
        "준다",
    ),
    1018: (
        "주시오",
        "주어라",
        "주시오",
        "주시오",
        "주시오",
        "주도록 하라",
        "주어라",
    ),
    1024: (
        "주겠습니다",
        "주겠다",
        "드리겠습니다",
        "드리겠소",
        "주겠습니다",
        "드리겠소",
        "주겠다",
    ),
    1030: (
        "이군요",
        "이로다",
        "이군요",
        "이옵니다",
        "이군요",
        "이구려",
        "이로다",
    ),
    1036: (
        "좋습니다",
        "좋다",
        "좋사옵니다",
        "좋사옵니다",
        "좋습니다",
        "좋소",
        "좋다",
    ),
    1042: (
        "좋군요",
        "좋구나",
        "좋사옵니다",
        "좋사옵니다",
        "좋군요",
        "좋소",
        "좋구나",
    ),
    1048: (
        "괜찮습니까",
        "괜찮은가",
        "괜찮겠사옵니까",
        "괜찮겠사옵니까",
        "괜찮겠습니까",
        "괜찮겠소",
        "괜찮은가",
    ),
    1054: (
        "하겠습니다",
        "하겠다",
        "하겠사옵니다",
        "하겠사옵니다",
        "하겠습니다",
        "하겠소",
        "하겠다",
    ),
    1060: (
        "좋겠지요",
        "좋겠다",
        "좋겠사옵니다",
        "좋겠사옵니다",
        "좋겠지요",
        "좋겠소",
        "좋겠다",
    ),
}
EXPECTED_FULL_BASE_JP = {
    record_id: source
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, source in zip(
        record_ids,
        SOURCE_MATRICES[root],
        strict=True,
    )
}
EXPECTED_FULL_CURRENT_KO = {
    record_id: current
    for root, record_ids in FULL_TERMINAL_GROUPS.items()
    for record_id, current in zip(
        record_ids,
        CURRENT_MATRICES[root],
        strict=True,
    )
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
    "base_jp": "E4DDC664DB5B3C82754F861F9B9C4FB1AC3B9C4DBC8BE95087D7EE93B38645EE",
    "base_current": "C024C4523E6BCEB4AB5A4F0F25285B57A5E7ABE71E64BCE2554A17F438621D5C",
    "base_sc": "41B322EA8B250C9ACBBAC77048B6E2D1BD5B39C656DB5180C46229FDA89E164B",
    "base_tc": "41B322EA8B250C9ACBBAC77048B6E2D1BD5B39C656DB5180C46229FDA89E164B",
    "pk_jp": "B588979F3BD57F508B2928DD92DC2B8956C7264179078C6FEEF934B6C9EBB5B2",
    "pk_current": "FBABCF29EDCBB2A5C31E4E270971AA39541328DC9B54D8F7BB417CEE414E8148",
    "pk_sc": "A7E5ED34E8EF40CAA25E74E45FD75EE776ABCB5A217D85302E3B0BFAE92998B9",
    "pk_tc": "A7E5ED34E8EF40CAA25E74E45FD75EE776ABCB5A217D85302E3B0BFAE92998B9",
    "pk_en": "A7E5ED34E8EF40CAA25E74E45FD75EE776ABCB5A217D85302E3B0BFAE92998B9",
}
FULL_ARCHIVE_DIGESTS = {
    "base_jp": "4B162969868D04D62560A8119CD72F7C4761257F98524E9582F6BB5C8B5701DD",
    "base_current": "0869CE9E37A642750750AA3A3171B45022CB1AB802BDB6B5C31EC40425B8F0C1",
    "base_sc": "D8CAB52A1E221C9F65FC94BCE9643C44C58BCAF5BCBF507B2D3B55A88A1885CF",
    "base_tc": "D8CAB52A1E221C9F65FC94BCE9643C44C58BCAF5BCBF507B2D3B55A88A1885CF",
    "pk_jp": "014D49AE3226B8056AB14CCEC216D280ABE75BEB8F37B1B9FCBE532899A84FF8",
    "pk_current": "067C22B10B9FBBDD3DB782C716D6D3C747D0BF2065AAA4611781BBFA63CD6644",
    "pk_sc": "C97C37A323F945D30B9AF8E687CF4664B0B620088896D395F14AA0AB81ED4319",
    "pk_tc": "C97C37A323F945D30B9AF8E687CF4664B0B620088896D395F14AA0AB81ED4319",
    "pk_en": "C97C37A323F945D30B9AF8E687CF4664B0B620088896D395F14AA0AB81ED4319",
}
JUMP_EVIDENCE = {
    "base_jp": {
        "target": (67, "56C843F04069B236DDC1DC4C8A6D13E970D72D6ACB18767366FC267178E9AC59"),
        "full": (77, "8D54686F137F28AF989B80983BCB2B9C4CD733AB93F273665A7224DB45DCA6AC"),
    },
    "base_current": {
        "target": (67, "56C843F04069B236DDC1DC4C8A6D13E970D72D6ACB18767366FC267178E9AC59"),
        "full": (77, "8D54686F137F28AF989B80983BCB2B9C4CD733AB93F273665A7224DB45DCA6AC"),
    },
    "pk_jp": {
        "target": (67, "4AD70F6878C61EE652D6F7EFE937988342E1AEB169D873C2F41ADF934E5C6511"),
        "full": (77, "0CC4D0F2A0E7CB2CCDE81A9E1CEB76B97D386C67DF8314E52E2922196BD3E481"),
    },
    "pk_current": {
        "target": (67, "4AD70F6878C61EE652D6F7EFE937988342E1AEB169D873C2F41ADF934E5C6511"),
        "full": (77, "0CC4D0F2A0E7CB2CCDE81A9E1CEB76B97D386C67DF8314E52E2922196BD3E481"),
    },
}
CALLER_ROW_EVIDENCE = {
    "base_jp": (308, "8000BDEEEF8BB31850B4B69D62412FF0670D1CB76846C747F52A614B35FBA63F"),
    "base_current": (272, "0E0F98864A0B13EE964FFB0407F9DD1B1099C82DB55B047513BD79F94AF60380"),
    "pk_jp": (412, "36B58C8C2CD4587260EC7AD0FA5868546F0C38FC38829C73E34E4034A8BA355E"),
    "pk_current": (364, "EC7D5EA48189E07ABBD20439FF8287828A24FDE7BFF8F17D6EF2FE480701FBF0"),
}
EMPTY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EMPTY_EVIDENCE = (0, EMPTY_SHA256)
EVIDENCE_ROOTS = tuple(FULL_TERMINAL_GROUPS)


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
            1000: (3, "FBFB157407D1B60C1494FAE28FB65E881F699B3679120E55083E25FDC44A45F8"),
            1006: (1, "E386653520878F99A5E1CA3F152F06714B3CF7A1F4D06EDB991041C33850AA16"),
            1024: (6, "A952B34316FEE888CE298659D55F1D3F9CB91870B21B6896E8E77E3147DA0B25"),
            1030: (1, "99E2B39205EEC1F066659A429F67329B56A73B4B707049F1DFF3537BAC87BD29"),
            1036: (10, "D429DF480FBAC58CE4C775C9A274908D73D886326518614CB0D1F942875C50A2"),
            1048: (1, "B0BAC903771BD46F0800EE67FD62A5D80B10F6651BA2D56325C56EB19E82173F"),
            1054: (273, "2ACD353A5A33AF670E5A758AD31D8BC0D60F0AA0FCA525871112A92B678CEBBD"),
            1060: (13, "4C1F5E9755BAB337E747506D460BBFF4BEF7DE7C81C7B4AD2CA799FCEFBEB518"),
        }
    ),
    "base_current": evidence(
        {
            1000: (3, "FBFB157407D1B60C1494FAE28FB65E881F699B3679120E55083E25FDC44A45F8"),
            1006: (1, "E386653520878F99A5E1CA3F152F06714B3CF7A1F4D06EDB991041C33850AA16"),
            1024: (5, "86957D27F15E0834D06FBF872349ED187CCDDBE382431114C6DBA3C86EDDEA8E"),
            1030: (1, "99E2B39205EEC1F066659A429F67329B56A73B4B707049F1DFF3537BAC87BD29"),
            1036: (9, "3231B3D4F91E9A48A5499C6403F7574151EC600A0BA5A932E6A2A77D708EB616"),
            1048: (1, "B0BAC903771BD46F0800EE67FD62A5D80B10F6651BA2D56325C56EB19E82173F"),
            1054: (241, "DC0122A5333756B49546BF975AFFA5B24D4DB61376F8F6B15267006A8D8DAAA0"),
            1060: (11, "9F0106D36CA7B132389826152D833F38A35BFC7B56247E3F59F86997A2CA4B63"),
        }
    ),
    "pk_jp": evidence(
        {
            1000: (3, "A718A22308B7BAD177F6B6C50EA8A92C8EC453C96C01C0767C0DEE99483C5023"),
            1006: (1, "E386653520878F99A5E1CA3F152F06714B3CF7A1F4D06EDB991041C33850AA16"),
            1024: (8, "8D193B30EA98330A8545CF2EC978D606DEA6FD8149610F758F7CE33F3E2ED481"),
            1030: (10, "CFB2C2021D6A376D4B9CE712DAD6E4597F5C9A19A0663CB6DF9147E7E6AE68DC"),
            1036: (22, "67248EB5B82B23B395045439C14971D5C089F945D20D03A59973ACC83D062B81"),
            1048: (3, "CD7D8852E5FCB516EEAEBEE5E37F45653311B96B20E4C4DCE2A4F809EAE788F1"),
            1054: (347, "CE49E2861DAC122781CB8A8F6308075C6BB7D72F6CDE8FA0E6F8ECE16FC2602A"),
            1060: (18, "271E21962115C713859CB323A5E24CAF63FD2416CBDE91C2BA6E5B58329C0491"),
        }
    ),
    "pk_current": evidence(
        {
            1000: (3, "A718A22308B7BAD177F6B6C50EA8A92C8EC453C96C01C0767C0DEE99483C5023"),
            1006: (1, "E386653520878F99A5E1CA3F152F06714B3CF7A1F4D06EDB991041C33850AA16"),
            1024: (6, "1C8361C2B4E7DB056BAC185D1E3E65EBD1FEE27EF51421E9985F208C4096B855"),
            1030: (10, "CFB2C2021D6A376D4B9CE712DAD6E4597F5C9A19A0663CB6DF9147E7E6AE68DC"),
            1036: (21, "BE88845CD6A8BF6B08AEB77CED2E8A5FFCFBCED7279D9CD1E3B05296CA9140A8"),
            1048: (3, "CD7D8852E5FCB516EEAEBEE5E37F45653311B96B20E4C4DCE2A4F809EAE788F1"),
            1054: (304, "285372B1F22D15FA1B5CDD7045A427B3B5BD9073C1FE0365912CFA067217CC30"),
            1060: (16, "0DF2CCFA9F2A99F5AD2DF813B8B4B84DB70967FF802C0EC860F8B73E4693B996"),
        }
    ),
}
FIXED_FOLLOWING_EVIDENCE = {
    "base_jp": evidence(
        {
            1000: (3, "FBFB157407D1B60C1494FAE28FB65E881F699B3679120E55083E25FDC44A45F8"),
            1036: (10, "D429DF480FBAC58CE4C775C9A274908D73D886326518614CB0D1F942875C50A2"),
            1054: (15, "41A48BB25463963EF69D46C7A376B7E7E76D91A6984928C6BA924C3C7D1A57B6"),
        }
    ),
    "base_current": evidence(
        {
            1000: (3, "FBFB157407D1B60C1494FAE28FB65E881F699B3679120E55083E25FDC44A45F8"),
            1036: (9, "3231B3D4F91E9A48A5499C6403F7574151EC600A0BA5A932E6A2A77D708EB616"),
            1054: (14, "81E7B0924970D9119F1919025C39476CCE3D5E69F27CBA62B65C1C7EB9EF594E"),
        }
    ),
    "pk_jp": evidence(
        {
            1000: (3, "A718A22308B7BAD177F6B6C50EA8A92C8EC453C96C01C0767C0DEE99483C5023"),
            1030: (5, "36FF17AAEC8E9EE76A14C5BC65E5424053A98664C6D5EDFE2490A0F44EAE7F48"),
            1036: (16, "9736CB62089266039BABDB64C53A31324A6464306F8E03E12C4EFD2613FB8207"),
            1054: (27, "734DE83AF8EEAB86D8A3DD62C8161C5597A55A99C68DD33FD5AFF488DA990BC8"),
        }
    ),
    "pk_current": evidence(
        {
            1000: (3, "A718A22308B7BAD177F6B6C50EA8A92C8EC453C96C01C0767C0DEE99483C5023"),
            1030: (5, "36FF17AAEC8E9EE76A14C5BC65E5424053A98664C6D5EDFE2490A0F44EAE7F48"),
            1036: (15, "146ECCF4AFC0029110FA022FE83F1C68B77B661FCD1791F14E0F1D1B1871871D"),
            1054: (24, "E946DA83ED961E36BC50BA5FE27BEAC84EFDDE3AD06620513B13B7A06A2DAD97"),
        }
    ),
}
FLATTEN_EVIDENCE = {
    "base": evidence(
        {
            1024: (1, "3C5878DE832EBC8BF1406A2216AEEA2853A34364EBC4BD2D82ED7F39694137BA"),
            1036: (1, "3A908DDF6FC33D8031DD11408C801A0EEECF295B889807DF4349A38674C88F15"),
            1054: (32, "25E664F9C2ECA4B7FCBCB8303FB5E856822D10065EA0D6A6CAA2CC78B832D157"),
            1060: (2, "E63B1A4D8FBA93148B5B3FFD226E9BE20C50CE840348CA68D81CC31E0ABA66C1"),
        }
    ),
    "pk": evidence(
        {
            1024: (2, "185F714130B228FE9050E5972EF3F7E2496DBA96CA2A610D1EA6E8BC8DFBE4E1"),
            1036: (1, "6CCB2BBAF4949BD2BD63216B9C9E6228A4891C36FBCB289292EDB1B4FE8C5422"),
            1054: (43, "C7D6C7A7BDFB42F987A6461BD2EB7D630987872C67A0E83B19744B8AB9DE4604"),
            1060: (2, "E63B1A4D8FBA93148B5B3FFD226E9BE20C50CE840348CA68D81CC31E0ABA66C1"),
        }
    ),
}
INTEGRATION_NOTE_BY_ROOT = {
    1000: (
        "imported S1020 benefactive-past policy; three callers have fixed "
        "sentence-final zo and require joint Korean rewriting"
    ),
    1006: (
        "single peace-command caller supplies tatakai o; the seven forms "
        "preserve polite, plain, and archaic stop-command registers"
    ),
    1012: (
        "no live Base or PK caller remains; literal give/receive nonpast "
        "semantics are preserved without inventing a context"
    ),
    1018: (
        "no live caller remains; yaru is interpreted within the surrounding "
        "give-command family rather than as unrelated accomplishment"
    ),
    1024: (
        "all live callers use te plus the benefactive terminal, so Korean "
        "caller integration must produce hae/jwo or deuryeo promises"
    ),
    1030: (
        "ne/yo follows nominal predicates in live callers; Korean needs an "
        "integrated copular exclamation, especially in PK-only contexts"
    ),
    1036: (
        "yoi/yoroshii serves adjective, recommendation, and permission "
        "contexts, and all live calls have fixed following material"
    ),
    1042: (
        "no live caller remains; the complete positive evaluation matrix "
        "retains neutral, plain, courtly, and archaic voices"
    ),
    1048: (
        "live callers ask permission after te mo; Korean must integrate the "
        "preceding action with the complete permission question"
    ),
    1054: (
        "mashou/you has hundreds of callers and is polysemous across first-"
        "person resolve, inclusive proposal, question, potential, and "
        "conjecture; every site requires caller-level Korean integration"
    ),
    1060: (
        "next-segment boundary group expresses recommendation/conjecture; "
        "the full seven-voice policy is exported for S1022; root1061 "
        "(PK1073) is a genuine two-leaf alias caller of the same group"
    ),
}
BASIS = (
    "review_queue_base_msggame_B007_S1021_pristine_base_pc_jp_sole_"
    "authority_block0_records2419_2485_67_visible_full_boundary_groups_"
    "2415_2491_S1020_root1000_imported_S1022_root1060_exported_unique_"
    "exact_seven_literal_tuple_reverse_search_without_offset_premise_"
    "discovered_pk_plus68_roots_plus12_base_pk_jp_current_sc_tc_exact_"
    "pk_en_blank_014a_closures_0143_call_rows_source_current_flattening_"
    "fixed_following_and_no_standalone_014c_benefactive_stop_give_"
    "nominal_particle_evaluation_permission_polysemous_volitional_and_"
    "recommendation_semantics_runtime_caller_integration_pending_one_"
    "line_gap_skeleton_reverse_outside_exact_no_steam"
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
        target_keys = target_pk_keys if label.startswith("pk_") else target_base_keys
        full_keys = full_pk_keys if label.startswith("pk_") else full_base_keys
        if GENERAL.subset_digest(records, target_keys) != TARGET_ARCHIVE_DIGESTS[label]:
            raise RuntimeError(
                f"segment {SEGMENT} {label} target corpus drifted"
            )
        if GENERAL.subset_digest(records, full_keys) != FULL_ARCHIVE_DIGESTS[label]:
            raise RuntimeError(
                f"segment {SEGMENT} {label} full corpus drifted"
            )

    prior_root1000 = tuple(
        PRIOR.FULL_TRANSLATION_POLICY[record_id]
        for record_id in FULL_TERMINAL_GROUPS[1000]
    )
    if (
        prior_root1000 != TRANSLATION_MATRICES[1000]
        or PRIOR.FULL_TRANSLATION_POLICY[2419] != "주었습니다"
        or PRIOR.FULL_TRANSLATION_POLICY[2420] != "주었습니다"
        or PRIOR.FULL_TRANSLATION_POLICY[2421] != "주었다"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} S1020 root1000 boundary drifted"
        )

    for root, base_record_ids in FULL_TERMINAL_GROUPS.items():
        expected = SOURCE_MATRICES[root]
        pk_root = PK_ROOT_BY_BASE[root]
        pk_record_ids = PK_FULL_TERMINAL_GROUPS[pk_root]
        if AUDIT.sequence_starts(records_by_label["base_jp"], expected) != (
            base_record_ids[0],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} unique Base tuple drifted: {root}"
            )
        if AUDIT.sequence_starts(records_by_label["pk_jp"], expected) != (
            pk_record_ids[0],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} unique PK tuple drifted: {root}"
            )
        if tuple(PK_RECORD_MAP[value] for value in base_record_ids) != pk_record_ids:
            raise RuntimeError(
                f"segment {SEGMENT} explicit PK map drifted: {root}"
            )

    for record_id in FULL_RECORD_IDS:
        base_key = (BLOCK_ID, record_id)
        pk_key = (BLOCK_ID, PK_RECORD_MAP[record_id])
        if literal_texts(records_by_label["base_jp"], base_key) != (
            EXPECTED_FULL_BASE_JP[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} pristine Base JP drifted: {record_id}"
            )
        if literal_texts(records_by_label["base_current"], base_key) != (
            EXPECTED_FULL_CURRENT_KO[record_id],
        ):
            raise RuntimeError(
                f"segment {SEGMENT} Base current drifted: {record_id}"
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
                or gap_bytes(records_by_label[f"base_{language}"][base_key])
                != gap_bytes(records_by_label[f"pk_{language}"][pk_key])
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} Base/PK drifted: "
                    f"{language}/{record_id}"
                )
        if (
            literal_texts(records_by_label["base_sc"], base_key) != ("",)
            or literal_texts(records_by_label["base_tc"], base_key) != ("",)
            or literal_texts(records_by_label["pk_en"], pk_key) != ("",)
        ):
            raise RuntimeError(
                f"segment {SEGMENT} contextual corpus appeared: {record_id}"
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
                    f"segment {SEGMENT} {label} {scope} 014A drifted"
                )

        edges = GRAPH.graph_edges(records)
        for root, base_record_ids in FULL_TERMINAL_GROUPS.items():
            actual_root = PK_ROOT_BY_BASE[root] if edition == "pk" else root
            expected_ids = (
                set(PK_FULL_TERMINAL_GROUPS[PK_ROOT_BY_BASE[root]])
                if edition == "pk"
                else set(base_record_ids)
            )
            closure = GRAPH.graph_closure(edges, actual_root).intersection(
                full_ids
            )
            if closure != expected_ids:
                raise RuntimeError(
                    f"segment {SEGMENT} {label} closure drifted: {root}"
                )

        caller_rows, caller_sites = GRAPH.caller_rows(records, full_ids)
        expected_count, expected_sha256 = CALLER_ROW_EVIDENCE[label]
        if (
            len(caller_rows) != expected_count
            or digest_json(caller_rows) != expected_sha256
        ):
            raise RuntimeError(
                f"segment {SEGMENT} {label} 0143 caller rows drifted"
            )
        actual_roots_by_logical = (
            ACTUAL_CALL_ROOTS_BY_PK
            if edition == "pk"
            else ACTUAL_CALL_ROOTS_BY_BASE
        )
        expected_roots = {
            actual_root
            for root, (count, _) in CALL_EVIDENCE[label].items()
            if count
            for actual_root in actual_roots_by_logical[root]
        }
        if set(caller_sites) != expected_roots:
            raise RuntimeError(
                f"segment {SEGMENT} {label} caller roots drifted"
            )
        for root in EVIDENCE_ROOTS:
            actual_roots = actual_roots_by_logical[root]
            sites = tuple(
                site
                for actual_root in actual_roots
                for site in caller_sites.get(actual_root, ())
            )
            call_count, call_sha256 = CALL_EVIDENCE[label][root]
            if (
                len(sites) != call_count
                or digest_sites(sites) != call_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} calls drifted: {root}"
                )
            blockers = tuple(
                blocker
                for actual_root in actual_roots
                for blocker in PRIOR.fixed_following_blockers(
                    records,
                    actual_root,
                )
            )
            fixed_count, fixed_sha256 = FIXED_FOLLOWING_EVIDENCE[
                label
            ][root]
            if (
                len(blockers) != fixed_count
                or digest_sites(blockers) != fixed_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {label} fixed following "
                    f"drifted: {root}"
                )
        if AUDIT.relevant_standalone_014c(records, full_ids):
            raise RuntimeError(
                f"segment {SEGMENT} {label} standalone 014C appeared"
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
        for root in EVIDENCE_ROOTS:
            actual_roots = (
                ACTUAL_CALL_ROOTS_BY_PK[root]
                if edition == "pk"
                else ACTUAL_CALL_ROOTS_BY_BASE[root]
            )
            source_root_sites = {
                site
                for actual_root in actual_roots
                for site in source_sites.get(actual_root, ())
            }
            current_root_sites = {
                site
                for actual_root in actual_roots
                for site in current_sites.get(actual_root, ())
            }
            flattened = tuple(
                sorted(source_root_sites - current_root_sites)
            )
            current_only = current_root_sites - source_root_sites
            expected_count, expected_sha256 = FLATTEN_EVIDENCE[
                edition
            ][root]
            if (
                current_only
                or len(flattened) != expected_count
                or digest_sites(flattened) != expected_sha256
            ):
                raise RuntimeError(
                    f"segment {SEGMENT} {edition} flattening drifted: "
                    f"{root}"
                )


def assert_semantics(translations: dict[str, str]) -> None:
    if (
        translations != TRANSLATIONS
        or len(translations) != 67
        or set(TRANSLATIONS_BY_RECORD) != set(RECORD_IDS)
        or set(FULL_TRANSLATION_POLICY) != set(FULL_RECORD_IDS)
        or set(SOURCE_MATRICES) != set(FULL_TERMINAL_GROUPS)
        or set(TRANSLATION_MATRICES) != set(FULL_TERMINAL_GROUPS)
        or set(INTEGRATION_NOTE_BY_ROOT) != set(FULL_TERMINAL_GROUPS)
    ):
        raise RuntimeError(f"segment {SEGMENT} translation universe drifted")

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
        TRANSLATIONS_BY_RECORD[2419] != "주었습니다"
        or TRANSLATIONS_BY_RECORD[2420] != "주었습니다"
        or TRANSLATIONS_BY_RECORD[2421] != "주었다"
        or TRANSLATIONS_BY_RECORD[2422] != "그만두십시오"
        or TRANSLATIONS_BY_RECORD[2443] != "주겠습니다"
        or TRANSLATIONS_BY_RECORD[2450] != "이군요"
        or TRANSLATIONS_BY_RECORD[2457] != "좋습니다"
        or TRANSLATIONS_BY_RECORD[2471] != "괜찮습니까"
        or TRANSLATIONS_BY_RECORD[2478] != "하겠습니다"
        or TRANSLATIONS_BY_RECORD[2485] != "좋겠지요"
        or FULL_TRANSLATION_POLICY[2486] != "좋겠다"
        or FULL_TRANSLATION_POLICY[2487] != "좋겠사옵니다"
        or FULL_TRANSLATION_POLICY[2490] != "좋겠소"
        or FULL_TRANSLATION_POLICY[2491] != "좋겠다"
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
                    "base_actual_call_roots": list(
                        ACTUAL_CALL_ROOTS_BY_BASE[root]
                    ),
                    "pk_actual_call_roots": list(
                        ACTUAL_CALL_ROOTS_BY_PK[root]
                    ),
                    "base_record_id": record_id,
                    "pk_semantic_record_id": PK_RECORD_MAP[record_id],
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
                    "pk_source_only_flattened_call_count": (
                        FLATTEN_EVIDENCE["pk"][root][0]
                    ),
                    "base_current_fixed_following_count": (
                        FIXED_FOLLOWING_EVIDENCE["base_current"][
                            root
                        ][0]
                    ),
                    "pk_current_fixed_following_count": (
                        FIXED_FOLLOWING_EVIDENCE["pk_current"][
                            root
                        ][0]
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
    print(
        ENGINE.json.dumps(
            {
                "status": "ok",
                "segment": "base_msggame_B007_S1021",
                "queue": QUEUE_BATCH_ID,
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
                "pk_mapping_method": (
                    "unique_exact_seven_literal_tuple_reverse_search"
                ),
                "discovered_base_pk_record_deltas": sorted(
                    {
                        PK_RECORD_MAP[record_id] - record_id
                        for record_id in FULL_RECORD_IDS
                    }
                ),
                "discovered_base_pk_root_deltas": sorted(
                    {
                        PK_ROOT_BY_BASE[root] - root
                        for root in FULL_TERMINAL_GROUPS
                    }
                ),
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
                "imported_s1020_boundary_policy": {
                    str(record_id): FULL_TRANSLATION_POLICY[record_id]
                    for record_id in range(2419, 2422)
                },
                "exported_s1022_boundary_policy": {
                    str(record_id): FULL_TRANSLATION_POLICY[record_id]
                    for record_id in range(2485, 2492)
                },
                "jump_evidence": JUMP_EVIDENCE,
                "caller_row_evidence": CALLER_ROW_EVIDENCE,
                "call_evidence": CALL_EVIDENCE,
                "flatten_evidence": FLATTEN_EVIDENCE,
                "fixed_following_evidence": FIXED_FOLLOWING_EVIDENCE,
                "relevant_valid_standalone_014c_count": 0,
                "candidate_sha256": candidate_sha256,
                "decision_sha256": hashlib.sha256(
                    OUTPUT.read_bytes()
                ).hexdigest().upper(),
                "builder_sha256": hashlib.sha256(
                    SCRIPT.read_bytes()
                ).hexdigest().upper(),
                "target_runtime_skeleton_exact": True,
                "full_boundary_runtime_skeleton_exact": True,
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
