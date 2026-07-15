# MSG_PK msggame UI 우선 번역 B01

`MSG_PK/SC/msggame.bin`의 미번역 대상 중 UI·도움말 성격이 분명하고, SC 레코드 하나가 문자열 리터럴 하나로 완결되는 150좌표를 번역한 격리 작업물입니다. 기존 등록 오버레이 10,149좌표와 겹치지 않으며 루트 진행률·README·실게임 파일은 수정하지 않습니다.

## 범위

- 전투 UI 및 시스템 도움말: 50
- 내정·외교 관리 툴팁과 튜토리얼: 42
- UI 제목·라벨: 29
- 설정·해금·구성 안내: 22
- 메뉴 이동·입력 안내: 7
- 합계: 150

이번 배치를 등록하면 PK `msggame` 기준 번역 좌표는 `10,149 → 10,299 / 16,482`, 잔여 좌표는 `6,183`이 됩니다. 이 수치는 작업물 자체의 검증 정보일 뿐 루트 진행률 파일에는 반영하지 않았습니다.

## `返回` 오탐 감사

좌표 `(7, 2076, 0)`은 독립적인 뒤로 가기 버튼이 아닙니다. SC/EN 레코드 골격상 두 문자열 사이에 런타임 동적 값이 삽입되는 서사 문장 조각으로 확인되어 번역 오버레이에서 제외했습니다. 실제 하단 버튼은 별도의 이미지/리소스 추적 대상입니다. 공개 증거에는 원문 대신 리터럴 해시, 레코드 골격 해시, 구조 정보만 기록했습니다.

## 산출물

- `public/msggame_ko_pk_ui_priority_b01_150.v1.json`: source-free 배포 오버레이
- `evidence/msggame_pk_ui_priority_b01_evidence.v1.json`: 좌표·구조·해시 증거
- `review/msggame_pk_ui_priority_b01_review.v1.json`: 150건 분류와 오탐 1건 제외 기록
- `msggame_pk_ui_priority_b01_validation.v1.json`: 재빌드·재추출·진행률 효과 검증
- `ui_translations.py`: 번역 좌표 원장
- `build_msggame_pk_ui_priority_b01.py`: 결정적 빌더
- `tests/test_msggame_pk_ui_priority_b01.py`: 7개 회귀 테스트

## 재현

```powershell
python -X utf8 workstreams/msggame_pk_ui_priority_b01/build_msggame_pk_ui_priority_b01.py
python -X utf8 -m unittest discover -s workstreams/msggame_pk_ui_priority_b01/tests -v
```

검증은 stock PK/SC에 이 오버레이만 오프라인 적용한 뒤 모든 리터럴 좌표가 보존되고 150개 결과가 정확히 재추출되는지 확인합니다. 실게임 파일, EXE, DLL, 레지스트리, 프로세스 메모리에는 접근하거나 기록하지 않습니다.
