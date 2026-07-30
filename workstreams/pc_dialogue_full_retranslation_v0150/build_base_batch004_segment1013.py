#!/usr/bin/env python3
"""Build Base block-0 runtime-terminal segment 1013 decisions."""

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

import build_base_batch003_segment1010 as FIXED
import build_base_batch003_segment1011 as PRIOR
import build_base_batch004_segment1012 as PREVIOUS_SEGMENT


ENGINE = PRIOR.ENGINE
GENERAL = PRIOR.GENERAL
UTIL = PRIOR.UTIL
GRAPH = PRIOR.GRAPH
OUTPUT = (
    REPO
    / "tmp"
    / WORKSTREAM.name
    / "decisions"
    / "base_msggame_B004_S1013.private.v1.jsonl"
)
SEGMENT = 1013
QUEUE_BATCH_ID = "base_msggame-B004"
BLOCK_ID = 0
RECORD_IDS = tuple(range(1881, 1948))
RECORD_KEYS = tuple((BLOCK_ID, record_id) for record_id in RECORD_IDS)
FULL_RECORD_IDS = tuple(range(1876, 1953))

# These are actual 014A closure roots, not ordinally inferred IDs.
FULL_TERMINAL_GROUPS = {
    550: tuple(range(1876, 1883)),
    556: tuple(range(1883, 1890)),
    562: tuple(range(1890, 1897)),
    568: tuple(range(1897, 1904)),
    574: tuple(range(1904, 1911)),
    580: tuple(range(1911, 1918)),
    586: tuple(range(1918, 1925)),
    592: tuple(range(1925, 1932)),
    598: tuple(range(1932, 1939)),
    604: tuple(range(1939, 1946)),
    610: tuple(range(1946, 1953)),
}

# Each PK group was found by an independent exact seven-literal reverse search.
# The resulting record delta happens to be uniform, but no fixed offset is used
# to construct the mapping.
PK_FULL_TERMINAL_GROUPS = {
    562: tuple(range(1944, 1951)),
    568: tuple(range(1951, 1958)),
    574: tuple(range(1958, 1965)),
    580: tuple(range(1965, 1972)),
    586: tuple(range(1972, 1979)),
    592: tuple(range(1979, 1986)),
    598: tuple(range(1986, 1993)),
    604: tuple(range(1993, 2000)),
    610: tuple(range(2000, 2007)),
    616: tuple(range(2007, 2014)),
    622: tuple(range(2014, 2021)),
}
PK_ROOT_BY_BASE = {
    550: 562,
    556: 568,
    562: 574,
    568: 580,
    574: 586,
    580: 592,
    586: 598,
    592: 604,
    598: 610,
    604: 616,
    610: 622,
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

EXPECTED_FULL_BASE_JP_SEQUENCE = (
    # 550
    "です",
    "だ",
    "でございます",
    "にございます",
    "です",
    "でござる",
    "だ",
    # 556
    "です",
    "だ",
    "です",
    "です",
    "です",
    "でござる",
    "だ",
    # 562
    "ですが",
    "だが",
    "なれど",
    "されど",
    "ですが",
    "しかし",
    "だが",
    # 568
    "たち",
    "あった",
    "がた",
    "ら",
    "たち",
    "ら",
    "ども",
    # 574
    "でした",
    "だった",
    "でございました",
    "でございました",
    "でした",
    "でござった",
    "であった",
    # 580
    "でした",
    "だった",
    "でした",
    "でした",
    "でした",
    "でござった",
    "であった",
    # 586
    "ですね",
    "だな",
    "でございますね",
    "でございますな",
    "ですね",
    "ですな",
    "だな",
    # 592
    "ですね",
    "だな",
    "ですね",
    "ですな",
    "ですね",
    "ですな",
    "だな",
    # 598
    "でしょう",
    "であろう",
    "でしょう",
    "でしょう",
    "でしょう",
    "でしょう",
    "だろう",
    # 604
    "でしょう",
    "であろう",
    "でございましょう",
    "でございましょう",
    "でありましょう",
    "でござろう",
    "であろう",
    # 610
    "ちます",
    "つ",
    "ちます",
    "ちます",
    "ちます",
    "ちます",
    "つ",
)
EXPECTED_FULL_BASE_JP = dict(
    zip(
        FULL_RECORD_IDS,
        EXPECTED_FULL_BASE_JP_SEQUENCE,
        strict=True,
    )
)

TRANSLATIONS_BY_RECORD = {
    1881: "이오",
    1882: "다",
    1883: "입니다",
    1884: "다",
    1885: "입니다",
    1886: "입니다",
    1887: "입니다",
    1888: "이오",
    1889: "다",
    1890: "입니다만",
    1891: "하지만",
    1892: "허나",
    1893: "그러나",
    1894: "입니다만",
    1895: "그러나",
    1896: "하지만",
    1897: "들",
    1898: "있었다",
    1899: "분들",
    1900: "들",
    1901: "들",
    1902: "들",
    1903: "들",
    1904: "였습니다",
    1905: "였다",
    1906: "였사옵니다",
    1907: "였사옵니다",
    1908: "였습니다",
    1909: "였소",
    1910: "였다",
    1911: "였습니다",
    1912: "였다",
    1913: "였습니다",
    1914: "였습니다",
    1915: "였습니다",
    1916: "였소",
    1917: "였다",
    1918: "이지요",
    1919: "이군",
    1920: "이옵지요",
    1921: "이옵니다그려",
    1922: "이지요",
    1923: "이군요",
    1924: "이군",
    1925: "이지요",
    1926: "이군",
    1927: "이지요",
    1928: "이군요",
    1929: "이지요",
    1930: "이군요",
    1931: "이군",
    1932: "이겠지요",
    1933: "이리라",
    1934: "이겠지요",
    1935: "이겠지요",
    1936: "이겠지요",
    1937: "이겠지요",
    1938: "이겠지",
    1939: "이겠지요",
    1940: "이리라",
    1941: "이겠사옵니다",
    1942: "이겠사옵니다",
    1943: "이겠지요",
    1944: "이리다",
    1945: "이리라",
    1946: "합니다",
    1947: "한다",
}
TRANSLATIONS = {
    f"0:{record_id}:0": translation
    for record_id, translation in TRANSLATIONS_BY_RECORD.items()
}

# Complete boundary matrices owned by adjacent segments are contracts only.
BOUNDARY_TRANSLATION_POLICY = {
    1876: "입니다",
    1877: "다",
    1878: "이옵니다",
    1879: "이옵니다",
    1880: "입니다",
    1948: "합니다",
    1949: "합니다",
    1950: "합니다",
    1951: "합니다",
    1952: "한다",
}
FULL_TRANSLATION_POLICY = {
    **BOUNDARY_TRANSLATION_POLICY,
    **TRANSLATIONS_BY_RECORD,
}

TARGET_ARCHIVE_DIGESTS = {
    "base_jp": "4B52660C6144411C80741EADAD403C27CC0897909EAE08FF15DA54EBA85447BE",
    "base_current": "B4F6C017B91D438776FC2FCFB053B76F1226FA3D5E7BEF136144E591834458D7",
    "base_sc": "B98E16997B8A20F4686B3A25B884C568CC31F663ED01CA7F35DF368A3325F7B4",
    "base_tc": "B98E16997B8A20F4686B3A25B884C568CC31F663ED01CA7F35DF368A3325F7B4",
    "pk_jp": "C3F4D0A941501F01792CF03879B2378092F5FB3227C11B7A87D79E3E4EAA5E18",
    "pk_current": "BA07FCA80A78181856B45032F2C6A4DA2CC43F08EF7A9BD71E00EF891804C447",
    "pk_sc": "A0396298754BD4EBCA7F3915059A2C0E2E0CC56D9E8E94CA9C950B2579D61515",
    "pk_tc": "A0396298754BD4EBCA7F3915059A2C0E2E0CC56D9E8E94CA9C950B2579D61515",
    "pk_en": "A0396298754BD4EBCA7F3915059A2C0E2E0CC56D9E8E94CA9C950B2579D61515",
}
FULL_ARCHIVE_DIGESTS = {
    "base_jp": "1D19446ECBF437087E57507A77D20611F10E04F6A67D0F2070B92FD99BD7C452",
    "base_current": "64AED4C1A1D7DB761ECF08ED47A3CB3A59C054D78F0DFEA1A99174CE92A47B3E",
    "base_sc": "88A64911185AFBA9EA2150EB397262B95B85393B2FC70576A71F25B18E44DD5F",
    "base_tc": "88A64911185AFBA9EA2150EB397262B95B85393B2FC70576A71F25B18E44DD5F",
    "pk_jp": "14BDDF37D229F84F62A2CC07040E747ED8DF394F4DB9AFD0A8EDBB6355757259",
    "pk_current": "C3E3BBF4CB4E6CB491BD4E409F1FC94C2995F13F3F50C5EADC786DA059BA4DF0",
    "pk_sc": "73BE1D6E92408AECEFF9C717531F142ED2E45769A9C78CDD117A1EBA279F5B2F",
    "pk_tc": "73BE1D6E92408AECEFF9C717531F142ED2E45769A9C78CDD117A1EBA279F5B2F",
    "pk_en": "73BE1D6E92408AECEFF9C717531F142ED2E45769A9C78CDD117A1EBA279F5B2F",
}

JUMP_EVIDENCE = {
    "base_jp": {
        "target": (67, "DF2140383E1E63CA0020E7557476E275F664B4C0BA89ED5FD8A41DAD702C4CD3"),
        "full": (77, "FADB267EFC2D22F908809AFF5DC66F2ADC8645CE811AA6459A545FF67C8AC109"),
    },
    "base_current": {
        "target": (67, "DF2140383E1E63CA0020E7557476E275F664B4C0BA89ED5FD8A41DAD702C4CD3"),
        "full": (77, "FADB267EFC2D22F908809AFF5DC66F2ADC8645CE811AA6459A545FF67C8AC109"),
    },
    "pk_jp": {
        "target": (67, "E2F3E769E3BAF1FD456B565BEC5D268A1B8741CC90AAD89F3EC5D398A0A976CF"),
        "full": (77, "344022561EBAA741CA0F20AF3B44885EFE90AD8E27E1A9E4F4D22AD6B830316B"),
    },
    "pk_current": {
        "target": (67, "E2F3E769E3BAF1FD456B565BEC5D268A1B8741CC90AAD89F3EC5D398A0A976CF"),
        "full": (77, "344022561EBAA741CA0F20AF3B44885EFE90AD8E27E1A9E4F4D22AD6B830316B"),
    },
}

EMPTY_SHA256 = (
    "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"
)
EVIDENCE_ROOTS = (
    550,
    556,
    557,  # live two-terminal subroot inside Base root 556
    562,
    568,
    574,
    580,
    586,
    592,
    598,
    604,
    610,
)
ACTUAL_CALL_ROOT = {
    "base": {
        550: 550,
        556: 556,
        557: 557,
        562: 562,
        568: 568,
        574: 574,
        580: 580,
        586: 586,
        592: 592,
        598: 598,
        604: 604,
        610: 610,
    },
    "pk": {
        550: 562,
        556: 568,
        557: 569,
        562: 574,
        568: 580,
        574: 586,
        580: 592,
        586: 598,
        592: 604,
        598: 610,
        604: 616,
        610: 622,
    },
}
CALLER_ROW_EVIDENCE = {
    "base_jp": (470, "1317A111F01497D19BFFFF8E3F3AFDFBB8BFF12550D08EF321A03A0ACFB0230C"),
    "base_current": (428, "D193E3ABC5F5FAD903206367EC7D7907298E40B79FDFA4CECBFD8BFEE7C82767"),
    "pk_jp": (639, "ED806ED9A7034998C0D5AE5E5AEA62D268F8E8CFC9CF8B2B0C1FD6699AC7BD8F"),
    "pk_current": (597, "2BBDC3CA581ABFB3E92DCF9433FDBB6BCCD0065D13C684DCDB30C365816255EB"),
}
CALL_EVIDENCE = {
    "base_jp": {
        550: (41, "4F68610E99C088B94FF976957188607DB9F4C315ADF579D9DBBCA40CB9101A81"),
        556: (136, "99064A556FA83C86AEB7CD6641F89B30E8A37BD4E88A2098EE87E7F9247DBBC8"),
        557: (1, "8F9E12622897FFF29F816D7A894B6FA065364245DFA91D91B4A96D3841090899"),
        562: (6, "CB59F5D5AC56064C6122E1D7FDF8B868277A435F5DB8558E75092FD46D01A693"),
        568: (0, EMPTY_SHA256),
        574: (13, "BA9D1BEA120A2C41C2BC3A87BC5112A0A3378AFC345FC9EF6C326E4284A29E57"),
        580: (7, "B1391A8DE3DEC234C84DE1C7BE491DF285171923A9710703FFE495A6A77703CD"),
        586: (43, "7DB7E71E90C696639DCE5793FAE715C992D2A218BFD2B7B2A05C1468CA219E7C"),
        592: (12, "2F520FE173437A2C98628F8998B042A1DA5D2BFCC24698B9BFB3EBCECE2253BA"),
        598: (202, "A3FEFA30347C6DFBA6AB5F526334F476BA811E5A9252BBBC2E1788C96C0B98A5"),
        604: (9, "4776B53AE4ADFD44963A91F7E741C79EDFBCFA7F55358430ACC75CC131B61451"),
        610: (0, EMPTY_SHA256),
    },
    "base_current": {
        550: (35, "F81F8FF1EDEB038C623BEDF2AEF122FC3846A8A96A6B35E8D5FBFBDF42301284"),
        556: (128, "741573051865487F87D51A6EE43B99B65CF6B564B91577FD0B8A6B951EF0B4EC"),
        557: (1, "8F9E12622897FFF29F816D7A894B6FA065364245DFA91D91B4A96D3841090899"),
        562: (6, "CB59F5D5AC56064C6122E1D7FDF8B868277A435F5DB8558E75092FD46D01A693"),
        568: (0, EMPTY_SHA256),
        574: (4, "F322E27674B8BF256417CF79252DAF67C57B632CA674056AC5087E2425262E93"),
        580: (7, "B1391A8DE3DEC234C84DE1C7BE491DF285171923A9710703FFE495A6A77703CD"),
        586: (39, "657D8A999F9C39B1E9E046DD7CB756AFAEFC35E7D58C17303028F34D591E88BA"),
        592: (12, "2F520FE173437A2C98628F8998B042A1DA5D2BFCC24698B9BFB3EBCECE2253BA"),
        598: (189, "0D18D2905B2B79BB5F4DE753641468C5EE7B668DAC72A826EBE4AD1624A6BA35"),
        604: (7, "FF56545351626ABD64BA210CE3747D92547CF2ED2579BE33BC2E5EAA4CAA846F"),
        610: (0, EMPTY_SHA256),
    },
    "pk_jp": {
        550: (60, "0520B7352890711D31B5184C3992FC7EEF43FCD5E4F1E4416E14D5500EA9127A"),
        556: (231, "FE4BFB8BAEEB0F5346340C8E4C7F10DE784FED7C361ACB862B92509D9D6A55EE"),
        557: (1, "911FE2B010D7D7A0224C18A5A4093B4E28F150FBF46EE5895A8EA2B5F87F3C86"),
        562: (7, "3BC4699CE1BCCE7C5DE3241DE929D615D12AC368FB3A0DBFBC1F43EAB7F23A6F"),
        568: (0, EMPTY_SHA256),
        574: (15, "C5CBB51C1BA68AF5EBFA2169D845E194A86B34788CFEF06764C855A140B64CD8"),
        580: (7, "DCDA7C70535E46A8D104F31AD34CC1D76813189153F583CCA6DEFD1E3AF280FD"),
        586: (43, "8FE22521D2A3585E474D75F8CDFE471C6BE6FFD7CE93D1EF3DDFDCA803987944"),
        592: (21, "CD418443D00BD923ED66E3141761F1CE3B110DCEA4447FBB7A46C04F07D89390"),
        598: (243, "0B0234F692CD1FAFB3E1B0BA14992A301FD8FEF0C5AF9A18A61565843CD6BFE0"),
        604: (11, "358192A7A4611E6CD20A6FC8C1077E5DA56A5742012056E96E2660198AA2857F"),
        610: (0, EMPTY_SHA256),
    },
    "pk_current": {
        550: (54, "9A3D12A6EE99549BB270D03BAD0D55D86F7255D2F4A9ADDA75DC3ED66253B665"),
        556: (222, "19C2CC26673895BF74C61FDF62473B80567E1428302F89A0FE06DE898D04ED15"),
        557: (1, "911FE2B010D7D7A0224C18A5A4093B4E28F150FBF46EE5895A8EA2B5F87F3C86"),
        562: (7, "3BC4699CE1BCCE7C5DE3241DE929D615D12AC368FB3A0DBFBC1F43EAB7F23A6F"),
        568: (0, EMPTY_SHA256),
        574: (6, "ED4DE1A406086EB14891D1A249352FEF107752D1CD627B33654A15CACBDD8786"),
        580: (7, "DCDA7C70535E46A8D104F31AD34CC1D76813189153F583CCA6DEFD1E3AF280FD"),
        586: (40, "7A345371B8DD9C5EA5752EB4B0C11D91F878E8A1323D3ED5118238265407185A"),
        592: (21, "CD418443D00BD923ED66E3141761F1CE3B110DCEA4447FBB7A46C04F07D89390"),
        598: (230, "E5E6A6654E877917006F2110971F458A5B4BD1D003A625C252EA4B53F346DFE0"),
        604: (9, "47560EC0D5B801FC9E5D7B9891469BC5848F4CC1B53123FB8663FBBB80FCCB99"),
        610: (0, EMPTY_SHA256),
    },
}

FLATTEN_EVIDENCE = {
    "base": {
        550: (6, "C1C9B8A7C167DD2BC1DAE44CA1B07DF97BE7F9F94FD13B033FF33667321347DC"),
        556: (8, "A39FC2C56F878AFFA782BA7A5F0E2F035DD0081C16BE83DD81848FD30538BBA5"),
        557: (0, EMPTY_SHA256),
        562: (0, EMPTY_SHA256),
        568: (0, EMPTY_SHA256),
        574: (9, "178AB60DB6280D21DC51A47CBC52C4858DD57FEDB1D533E8AA8568A0B0D430E8"),
        580: (0, EMPTY_SHA256),
        586: (4, "81DAFBA8314C1A0D1A4E1BAB9C301C414257F70EBDCFFDC1E4638703A130F91C"),
        592: (0, EMPTY_SHA256),
        598: (13, "D4FC178B11016FE8B16AEE9637C2E138A5E66775DB7AB3A04E1548E46E1EB3DC"),
        604: (2, "9744D37E48FF5E874588092810CEE42094032946D3CC307EF2C2E7B4BE9117DA"),
        610: (0, EMPTY_SHA256),
    },
    "pk": {
        550: (6, "CBD45A5118B7B021C5152E852F05656BDF0A680C8A732A47BC050A53E022C1B0"),
        556: (9, "1518C86F72453F53A8A9827912DCA36EAE616B3ED49F04953FD49B2C0C95FB50"),
        557: (0, EMPTY_SHA256),
        562: (0, EMPTY_SHA256),
        568: (0, EMPTY_SHA256),
        574: (9, "178AB60DB6280D21DC51A47CBC52C4858DD57FEDB1D533E8AA8568A0B0D430E8"),
        580: (0, EMPTY_SHA256),
        586: (3, "3CD2319B2C63C90871C7C60D95E73A8B407B3327C82928CF76C2555269A224D4"),
        592: (0, EMPTY_SHA256),
        598: (13, "BC9093580510D3FE1FE2B34B4215E3E02688ECC1186E998B66018661AFF6C683"),
        604: (2, "4F2D01FC415EF17076CD46165526C8AF86CF946A1D417F5C05AA4D625EA2BA79"),
        610: (0, EMPTY_SHA256),
    },
}

FIXED_FOLLOWING_EVIDENCE = {
    "base_jp": {
        550: (15, "65F51A382E4260FF6B11239AECB2716CDC34B40C9C89F99DC02F0F53C4716044"),
        556: (20, "46A485684575F7FDD03C6A66F17079AA7B6F6CE8FA4151A9A5D2C335A560FA79"),
        557: (0, EMPTY_SHA256),
        562: (2, "D76012811FD0D8612C99C77AF52CD3ED7EFB8C06A0CE6F27F3611C3F87E90706"),
        568: (0, EMPTY_SHA256),
        574: (0, EMPTY_SHA256),
        580: (1, "BA263908FBB9D85ABD082856F9725445802848BBAA8F7EBA4E51A1E2DE7ACE32"),
        586: (0, EMPTY_SHA256),
        592: (0, EMPTY_SHA256),
        598: (26, "5AA5895C06DD42EA82FB36590D03535D63FA47D0B81AFA80A4B8F6579C857003"),
        604: (5, "3F95CAF4E7EEC0EEAAF426DD4056B5EE7C3EA808A4A61D04C9ED836AA7AB4D50"),
        610: (0, EMPTY_SHA256),
    },
    "base_current": {
        550: (12, "AEE97F4198F22AD8394286447BCCFD64D3EC796BFB06A7BD91B7135197142D53"),
        556: (20, "46A485684575F7FDD03C6A66F17079AA7B6F6CE8FA4151A9A5D2C335A560FA79"),
        557: (0, EMPTY_SHA256),
        562: (2, "D76012811FD0D8612C99C77AF52CD3ED7EFB8C06A0CE6F27F3611C3F87E90706"),
        568: (0, EMPTY_SHA256),
        574: (0, EMPTY_SHA256),
        580: (1, "BA263908FBB9D85ABD082856F9725445802848BBAA8F7EBA4E51A1E2DE7ACE32"),
        586: (0, EMPTY_SHA256),
        592: (0, EMPTY_SHA256),
        598: (23, "A694EF458DD721D22AC39B7D843EFF36111F233688F738A4A43B55F73C2B04F6"),
        604: (4, "A0822D0950F0901161DC76CB0F939A2F17A75A84F721DDF0D2C9E4736080B374"),
        610: (0, EMPTY_SHA256),
    },
    "pk_jp": {
        550: (17, "40F8DF8D7513D6966C481804485AF4FC803150F7F3C7B2D2CFC7B6CD7059B943"),
        556: (55, "97A5D874BC4124AE03010E79CEC00E42908318E12622A955CB49442B32438A51"),
        557: (0, EMPTY_SHA256),
        562: (2, "8A5C000DE3F4E7979A4A024A01C55C0A9F6C680FDAC47FA20B659B2BC15E0662"),
        568: (0, EMPTY_SHA256),
        574: (0, EMPTY_SHA256),
        580: (1, "5FF552E847AA0D9A640B7FDEE784C9E9C9BB53990A5A673785AC21B175A23AEC"),
        586: (0, EMPTY_SHA256),
        592: (0, EMPTY_SHA256),
        598: (38, "B6FCFD6B76F15CF279272916405F8AFEC1FB2FBFE89CD61B1B9F3696E6F626EF"),
        604: (6, "16FF1A48387973F72EB19E6D386D73B41AC40108B35A53611711703826188ED6"),
        610: (0, EMPTY_SHA256),
    },
    "pk_current": {
        550: (14, "2A5FDB69DAC80F76A09E391E5F275AA6B78C909E893364B3F6CF4630BA664360"),
        556: (54, "474B9727DD7E0B4C125B3FE8F723F0711FCEE0AC186CDF5CE4CC9E6E233B948F"),
        557: (0, EMPTY_SHA256),
        562: (2, "8A5C000DE3F4E7979A4A024A01C55C0A9F6C680FDAC47FA20B659B2BC15E0662"),
        568: (0, EMPTY_SHA256),
        574: (0, EMPTY_SHA256),
        580: (1, "5FF552E847AA0D9A640B7FDEE784C9E9C9BB53990A5A673785AC21B175A23AEC"),
        586: (0, EMPTY_SHA256),
        592: (1, "A016F22355E4C7B52EB6B2F2B5D2C71D610D27244B0B28D8212904B897E684AE"),
        598: (34, "A2A9EDEE086BD78EF70E1543467DA043E5C203346C5E2B86C5D17E2366680157"),
        604: (5, "BA0F7D3D15DE91C25998DCD061EA252493DA8D8535D708679EB008E9BD6AF5F8"),
        610: (0, EMPTY_SHA256),
    },
}

BASIS = (
    "review_queue_base_msggame_B004_pristine_base_pc_jp_sole_authority_"
    "block0_visible_runtime_terminal_records1881_1947_exact_unique_seven_"
    "literal_pk_reverse_search_without_fixed_offset_assumption_actual_base_"
    "roots550_610_pk_roots562_622_nonordinal_live_subroot557_569_target_and_"
    "full_boundary_014a_closures_imported_S1012_boundary_contract_0143_"
    "caller_rows_source_current_flattening_"
    "fixed_following_digests_no_relevant_valid_standalone_014c_complete_"
    "boundary_matrices1876_1882_1946_1952_copular_connective_plural_past_"
    "confirmation_conjectural_and_tsu_verb_register_matrices_runtime_caller_"
    "integration_pending_pc_pk_auxiliary_context_only_no_korean_build_"
    "authority_one_line_reverse_overlay_no_steam_write"
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

    if set(PK_RECORD_MAP) != set(FULL_RECORD_IDS):
        raise RuntimeError(f"segment {SEGMENT} PK map universe drifted")

    for base_root, base_record_ids in FULL_TERMINAL_GROUPS.items():
        expected_tuple = tuple(
            EXPECTED_FULL_BASE_JP[record_id]
            for record_id in base_record_ids
        )
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
                for match in PRIOR.PRIOR.PREVIOUS.MORPHOLOGY_JUMP_RE.finditer(
                    gap
                )
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
    ):
        raise RuntimeError(f"segment {SEGMENT} translation universe drifted")

    expected_matrices = {
        550: ("입니다", "다", "이옵니다", "이옵니다", "입니다", "이오", "다"),
        556: ("입니다", "다", "입니다", "입니다", "입니다", "이오", "다"),
        562: ("입니다만", "하지만", "허나", "그러나", "입니다만", "그러나", "하지만"),
        568: ("들", "있었다", "분들", "들", "들", "들", "들"),
        574: ("였습니다", "였다", "였사옵니다", "였사옵니다", "였습니다", "였소", "였다"),
        580: ("였습니다", "였다", "였습니다", "였습니다", "였습니다", "였소", "였다"),
        586: ("이지요", "이군", "이옵지요", "이옵니다그려", "이지요", "이군요", "이군"),
        592: ("이지요", "이군", "이지요", "이군요", "이지요", "이군요", "이군"),
        598: ("이겠지요", "이리라", "이겠지요", "이겠지요", "이겠지요", "이겠지요", "이겠지"),
        604: ("이겠지요", "이리라", "이겠사옵니다", "이겠사옵니다", "이겠지요", "이리다", "이리라"),
        610: ("합니다", "한다", "합니다", "합니다", "합니다", "합니다", "한다"),
    }
    if (
        tuple(
            PREVIOUS_SEGMENT.FULL_TRANSLATION_POLICY[record_id]
            for record_id in range(1876, 1883)
        )
        != expected_matrices[550]
        or expected_matrices[550]
        != (
            "입니다",
            "다",
            "이옵니다",
            "이옵니다",
            "입니다",
            "이오",
            "다",
        )
        or expected_matrices[610]
        != (
            "합니다",
            "한다",
            "합니다",
            "합니다",
            "합니다",
            "합니다",
            "한다",
        )
    ):
        raise RuntimeError(
            f"segment {SEGMENT} adjacent boundary contract drifted"
        )
    for root, record_ids in FULL_TERMINAL_GROUPS.items():
        actual = tuple(
            FULL_TRANSLATION_POLICY[record_id]
            for record_id in record_ids
        )
        if actual != expected_matrices[root]:
            raise RuntimeError(
                f"segment {SEGMENT} register matrix drifted: {root}"
            )

    if (
        TRANSLATIONS_BY_RECORD[1899] != "분들"
        or TRANSLATIONS_BY_RECORD[1906] != "였사옵니다"
        or TRANSLATIONS_BY_RECORD[1907] != "였사옵니다"
        or TRANSLATIONS_BY_RECORD[1920] != "이옵지요"
        or TRANSLATIONS_BY_RECORD[1947] != "한다"
        or BOUNDARY_TRANSLATION_POLICY[1952] != "한다"
    ):
        raise RuntimeError(
            f"segment {SEGMENT} semantic correction contract drifted"
        )

    for coordinate, translation in translations.items():
        if (
            "\r" in translation
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
                "segment": "base_msggame_B004_S1013",
                "queue": QUEUE_BATCH_ID,
                "source_literal_count": 67,
                "decision_count": len(rows),
                "runtime_fragment_pending": len(rows),
                "changed_literal_count": changed,
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
