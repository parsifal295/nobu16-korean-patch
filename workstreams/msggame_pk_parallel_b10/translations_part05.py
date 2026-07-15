"""Coordinate-only Korean translations for B10, unique source items 400-405."""

TRANSLATIONS: dict[tuple[int, int, int], str] = {}
STATUSES: dict[tuple[int, int, int], str] = {}


def _add(
    coordinates: list[tuple[int, int, int]],
    korean: str,
    status: str = "translated",
) -> None:
    for coordinate in coordinates:
        if coordinate in TRANSLATIONS:
            raise ValueError(f"duplicate coordinate: {coordinate}")
        TRANSLATIONS[coordinate] = korean
        STATUSES[coordinate] = status


_add([(17, 1151, 0)], "장점을 살리고 단점을 보완해 싸우면\n반드시 성과를 얻는다.")
_add([(17, 1152, 0)], "좋아, 이제")
_add([(17, 1152, 1)], "도 기세가 꺾여\n더는 우리의 적수가 아니다.")
_add([(17, 1153, 0)], "철포의 힘을 너무 믿었던 건가.\n아니면 계책이 좋지 않았던 걸까……")
_add([(17, 1155, 0)], "새로운 전법을 만들 수 있으리라\n생각했건만……")
_add([(17, 1157, 0)], "적 부대 6개 격파 (")
