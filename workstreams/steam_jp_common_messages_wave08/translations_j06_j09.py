#!/usr/bin/env python3
"""Project-authored Korean text for Steam JP wave08 batches j06-j09."""

from __future__ import annotations


J06_MSGDATA_LEGEND_NAMES = {
    26619: "미요시 전승",
    26620: "난부 전승",
    26621: "아마고 전승",
    26622: "사이토 전승",
    26623: "나미오카 전승",
    26624: "류조지 전승",
}


# These values are lookup/sort readings rather than labels.  Keep them
# whitespace-free so they behave like the neighboring internal reading keys.
J07_MSGDATA_LEGEND_READING_KEYS = {
    26875: "미요시전승",
    26876: "난부전승",
    26877: "아마고전승",
    26878: "사이토전승",
    26879: "나미오카전승",
    26880: "류조지전승",
}


J08_MSGDATA_LEGEND_DESCRIPTIONS = {
    entry_id: "%s 발령 가능, 이미 발령 가능하면 유지비 감소"
    for entry_id in range(27131, 27137)
}


J09_MSGSTF_CREDIT_UPDATE = {
    7: (
        "협력　　\n"
        "　　imagination\n"
        "　　alphaliez inc.\n"
        "　　IMAGICADIGITALSCAPE Co., Ltd.\n"
        "　　INSPION, Inc.\n"
        "　　KIZAWA studio\n"
        "　　CREEK & RIVER Co., Ltd.\n"
        "　　SHOWASHOTAI Co.,Ltd.\n"
        "　　DIGITAL HEARTS Co., Ltd.\n"
        "　　ReBIRTH Inc.\n"
        "　　Crowd Gate Co.,Ltd.\n"
        "　　Himawari Theatre Group Inc.\n"
        "　　C And T LLC\n"
        "　　PTS Group International Company Ltd.\n"
        "　　Fontworks, Inc.\n"
        "　　Levtech Co., Ltd.\n"
        "　　DDT ProWrestling\n"
        "　　PTW Japan Co., Ltd.\n"
        "　　SIDE London\n"
        "　　\n"
        "　　KOEI TECMO TAIWAN CO., LTD.\n"
        "　　KOEI TECMO TIANJIN SOFTWARE CO., LTD.\n"
        "　　KOEI TECMO BEIJING SOFTWARE CO., LTD.\n"
        "　　KOEI TECMO SINGAPORE Pte. Ltd.\n"
        "　　KOEI TECMO SOFTWARE VIETNAM CO., LTD.\n"
        "　　\n"
        "<FTB>　　\n"
    )
}

