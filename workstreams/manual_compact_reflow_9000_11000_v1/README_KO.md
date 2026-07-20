# 9000~11000대 manual compact 이벤트 복원 검토

이 작업물은 23개 `manual_compact_korean_layout` 행의 검토표만 만든다.

- 기준 입력: 4000~5000대 복원 후보(Static Patch 007 후속 체인)
- 대조: 원본 JP 및 PC EN/SC/TC, v0.10.0 복원 전 한국어
- 출력: 의미를 삭제·축약하지 않은 한국어 문맥 개행안(최대 4줄, 줄당 실효 폭 912px 이하)
- 제외: 후보 바이너리 생성, Steam 적용, Git/릴리스 작업

`build_manual_compact_reflow_9000_11000_v1.py`를 실행하면 `review.v1.json`을 다시 생성하고, 입력 해시·제어 태그·동적 토큰 예약 폭·행별 레이아웃을 검증한다.
