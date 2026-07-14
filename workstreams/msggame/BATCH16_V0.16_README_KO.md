# msggame.bin 번역 배치 16 v0.16

`MSG_PK/SC/msggame.bin`의 좌표 기반 한국어 초벌 번역 배치다. 공개 산출물에는 원문이나 완성 게임 리소스를 넣지 않고, 좌표·SC UTF-16LE SHA-256·한국어 번역문만 기록한다.

## 범위와 상태

| 항목 | 값 |
|---|---:|
| 이번 번역 리터럴 | 150개 |
| 누적 번역 리터럴 | 2,400개 |
| 참조 레코드 | 117개 |
| 스캔된 표시 후보 | 150개 |
| 비언어 후보 보류 | 0개 |
| 첫 좌표 | `(6, 2436, 1)` |
| 마지막 좌표 | `(6, 2787, 0)` |
| 다음 연속 좌표 | `(6, 2787, 1)` |
| 런타임 검수 | 미실시 |

- 블록 6의 레코드 2436부터 2787까지에서 다음 표시 후보 150개를 번역했다.
- 지원 요청과 결과, 외교 교섭 및 거절, 세력 관계를 판단하는 독백, 세력명이 동적으로 삽입되는 전략 문장을 포함한다.
- 동적 세력명 앞뒤의 조각으로 나뉜 문장은 조각 순서와 줄바꿈·공백을 그대로 보존했다.
- 첫 레코드 `(6, 2436)`의 리터럴 0은 v0.15에 포함되며, 이번 배치는 리터럴 1부터 시작한다.
- 마지막 레코드 `(6, 2787)`에서는 리터럴 0만 포함하며, 리터럴 1은 다음 배치의 시작점이다.
- SC·JP·EN·TC의 동일한 `block_id`·`record_id` 전체 레코드를 대조했다. 언어별 `literal_id`가 같은 문장이라고 자동 가정하지 않았다.

## 산출물

이 배치가 새로 추가하는 파일은 정확히 다음 일곱 개다.

1. `BATCH16_V0.16_README_KO.md`: 배치 범위, 재생성 방법, 검증 요약.
2. `build_translation_batch16.py`: 고정 설치본을 확인한 뒤 공개 산출물과 오프라인 재패킹 검증 결과를 결정적으로 생성한다.
3. `public/msggame_ko_system_messages_b06r2436_2787.v0.16.json`: 원문 없는 좌표 번역 오버레이.
4. `evidence/translation_alignment_evidence.v0.16.json`: 원문 없이 기록한 언어별 동일 레코드 정렬 근거.
5. `review/translation_review_index.v0.16.json`: 좌표별 사람 검수 상태와 동적 결합 주의점.
6. `translation_validation.v0.16.json`: 재현성, 바이너리 구조, 안전성 검증 결과.
7. `tests/test_translation_batch16.py`: 범위·결정성·원문 부재·재패킹 회귀 테스트.

## 재생성 및 테스트

```powershell
python -B workstreams/msggame/build_translation_batch16.py `
  --out-root workstreams/msggame
python -B -m unittest workstreams.msggame.tests.test_translation_batch16 -v
python -B -m unittest discover -s workstreams/msggame/tests -p "test_*.py" -v
```

생성기는 설치된 SC·JP·EN·TC 파일의 크기와 packed/raw SHA-256을 먼저 확인한다. 고정 설치본과 다르면 생성 전에 중단하며, 설치 경로·실행 파일·폰트·메모리는 변경하지 않는다.

## 검증 항목

- v0.15의 다음 좌표부터 표시 후보 150개를 정확히 선택하며 v0.1~v0.15의 2,250개 좌표와 겹치지 않음
- 가변 길이 한국어를 적용한 오프라인 `msggame.bin`에서 블록·레코드·리터럴 좌표와 불투명 바이트코드 보존
- 줄바꿈, 앞뒤 공백, printf 토큰, 이스케이프, 제어문자, PUA 코드포인트, 괄호 순서 보존
- A/B/final 공개 산출물과 오프라인 재패킹 바이너리가 바이트 단위로 동일함
- 공개 JSON에서 상용 원문 한자·가나 유출 0건
- 작업 전후 설치된 SC·JP·EN·TC 파일의 SHA-256이 동일함

## 후속 검수

이번 150개 항목은 모두 사람 검수가 필요하며 런타임 검수 완료 항목은 0개다. 특히 세력명이 가운데 삽입되는 문장의 조사, 앞뒤 공백, 줄바꿈과 지원·외교 결과 문장의 말투를 게임 화면에서 우선 확인해야 한다.
