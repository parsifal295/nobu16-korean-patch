"""Exact active-JP source-hash reuse values for base msggame P2."""

from __future__ import annotations


# Values are keyed by the active JP UTF-16LE source hash.  They are accepted
# only when a pinned public catalogue provides the same value for that hash.
EXPECTED_REUSE_BY_SOURCE_HASH: dict[str, str] = {
    "41CF35172B8BC004510115DC4A64E1BB98C8DACD9E1C753FE94195BC14E361B2": "\n•",
    "FA433C89E61178902327DA13AF7DC0B09AEDE94A362DE11626C21700A658C353": "·",
    "BD968FADE7E7D38D92BC0425834A61D56BBF20610BC800178C5D30221154646A": "급류라니?!\n당했습니다……",
    "BA43EC8AEE249DF0066D1A67B918FA0E6F6727FAFF18C50C17B3F208F585D7FF": "첩자는 베었다!\n거짓 보고 계책은 실패했다",
    "912803B2BFDB79D48DB04BC0F17B91CF34E388FE99F9CE3EE962F60FA9E953DF": "주인 없는 땅이 있는 듯합니다.\n제게 영지를 맡겨 주십시오.\n전장에서 크게 활약하겠습니다.",
}
