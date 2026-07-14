# 옛 지방명 72개 한국어 오버레이 v0.1

`MSG_PK/SC/msgdata.bin`의 ID `13975..14046`은 에조부터 쓰시마까지 옛 지방명
72개가 SC·JP·EN에서 같은 순서로 정렬된 연속 블록이다. 이 작업선은 해당 표시명을
한국어로 옮긴 source-free 오버레이이며 게임 파일이나 설치기를 수정하지 않는다.

## 표기 정책

- 성·지명과 같은 지리 명칭은 일본어 `つ`를 표준 한국어 `쓰`로 적는다.
- 일본어 장음은 별도 모음을 덧붙이지 않는다.
- 서로 다른 지방인 ID `13986`과 `14034`는 모두 `아와`로 표시되는 것이 정상이다.
- 장수 개인명의 `츠` 표기 정책과 지명 정책은 서로 분리한다.

현재 72개는 번역 초벌 완료 상태이며, 실제 지도·정보창에서의 글꼴과 폭은 아직
검수하지 않았다. Font-v6와 현재 설치 후보에도 포함하지 않는다.

## 공개 범위

- `public/province_names_ko_13975_14046.v0.1.json`: ID와 한국어만 포함
- `tests/test_province_names.py`: 범위·형식·source-free 검증

정식판 SC·JP·EN 문자열과 완성 `msgdata.bin`은 배포하지 않는다. 최종 패치에서는
장수명·성 이름·지방명 오버레이를 같은 순정 SC `msgdata.bin`에 ID 오름차순으로
병합해야 한다.

## 검증

```powershell
python -B -m unittest workstreams/province_names/tests/test_province_names.py
```
