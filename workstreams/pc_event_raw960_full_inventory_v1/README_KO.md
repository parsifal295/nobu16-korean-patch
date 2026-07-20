# Steam PC PK 이벤트 raw 960px 전수 인벤토리 v1

이 작업물은 현재 Steam 개발 설치본 `MSG_PK/JP/msgev.bin`을 **읽기 전용**으로
조사한다. 대상은 실제 PK 이벤트 본문으로 확인된 ID `3000–11009` 중 한국어와
직접 PC 일본어가 모두 비어 있지 않은 8,006행이다.

## 현재 라이브 정책

- 이벤트 위젯의 줄바꿈 측정은 원본 G1N advance 그대로다.
  - 전각(한글·한자): 48px
  - 반각(공백·영문·일반 문장부호): 24px
  - 한 줄 한도: raw 960px
- 대사창은 최대 4줄이다.
- `ceil(raw × 30 / 48)`은 static patch 007의 30px 표시 크기를 참고로 기록할
  뿐, 줄바꿈 pass/fail 기준이 아니다.
- 일본어 원문의 LF는 줄바꿈 근거로 사용하지 않는다. 인벤토리는 JP·KO LF 수를
  모두 기록하지만 `jp_lf_policy`는 항상 `ignored`다.

## 정직한 상태 표기

동적 인명 토큰(`b`/`bm`/`bs`)은 사건 시기·별칭·사용자 개명에 따라 실제 표시명이
바뀐다. 과거처럼 숫자 ID가 같은 `msgev` 행의 이름이라고 가정하지 않는다.

- W71 아네가와 56행의 세 토큰만 당시 장면에서 확인한 보수적 표시명으로 측정한다.
- 그 밖의 동적 토큰 행은 폭을 억지로 통과시키지 않고 `runtime_reservation_hold`로
  남긴다.
- 토큰이 없는 행도 사람의 문맥 개행 검수가 끝나기 전에는
  `semantic_layout_review_pending`이다.

따라서 이 인벤토리는 전수 완료 선언이 아니라, 현재 hash에 고정된 실제 남은 범위와
각 행의 측정 근거를 만드는 P0 산출물이다.

## 생성물

`tmp/pc_event_raw960_full_inventory_v1/` 아래에만 생성한다.

- `inventory.v1.jsonl`: 행별·표시줄별 문자열, 폭, 전각/반각 수, 제어 시그니처,
  런타임 토큰 상태, review 상태
- `summary.v1.json`: 입력 hash, topology, 상태별 집계, 토큰 집계

## 실행

```powershell
python -B -X utf8 workstreams\pc_event_raw960_full_inventory_v1\build_pc_event_raw960_full_inventory_v1.py write
python -B -X utf8 workstreams\pc_event_raw960_full_inventory_v1\build_pc_event_raw960_full_inventory_v1.py validate
python -B -X utf8 workstreams\pc_event_raw960_full_inventory_v1\test_pc_event_raw960_full_inventory_v1.py
```

이 스크립트에는 Steam 파일 쓰기, 후보 적용, Git, 푸시, 릴리스 기능이 없다.
