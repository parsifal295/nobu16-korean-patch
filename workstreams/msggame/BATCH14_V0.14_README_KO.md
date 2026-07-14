# msggame.bin 번역 배치 14 v0.14

`MSG_PK/SC/msggame.bin`의 좌표 기반 한국어 초벌 번역 배치다. 공개 산출물에는
상용 원문이나 완성 게임 리소스를 포함하지 않고, 좌표·SC UTF-16LE SHA-256·한국어
번역문만 기록한다.

## 범위와 상태

| 항목 | 값 |
|---|---:|
| 이번 번역 리터럴 | 150개 |
| 누적 번역 리터럴 | 2,100개 |
| 참조 레코드 | 96개 |
| 스캔한 표시 후보 | 150개 |
| 비언어 후보 보류 | 0개 |
| 첫 좌표 | `(6, 1993, 0)` |
| 마지막 좌표 | `(6, 2139, 1)` |
| 다음 연속 좌표 | `(6, 2139, 2)` |
| 런타임 검수 | 미실시 |

- 블록 6의 레코드 1993부터 2139까지 좌표순으로 다음 표시 후보 150개를
  번역했다.
- 성·군·관직·자원 교섭, 맹약 파기·종속·동맹·원군 안내와 방침 중단 및
  원군 결과 대사가 포함된다.
- 세력명, 성명, 방침명과 개수가 런타임 값으로 삽입되는 분할 레코드는 조각
  순서와 줄바꿈·앞뒤 공백·괄호를 그대로 보존했다.
- 마지막 레코드 `(6, 2139)`는 배치 경계에 걸쳐 리터럴 0~1만 포함한다.
  리터럴 2는 스킵으로 세지 않고 번역 오버레이에서도 제외하여 원본 그대로
  남겼다.
- SC·JP·EN·TC의 동일한 `block_id`·`record_id` 전체 레코드를 대조했으며 언어별
  `literal_id`가 같은 문장을 뜻한다고 가정하지 않았다.

## 산출물

- `build_translation_batch14.py`: 고정 설치본을 읽어 공개 산출물과 오프라인
  재패킹 검증 결과를 결정적으로 생성한다.
- `public/msggame_ko_system_messages_b06r1993_2139.v0.14.json`: source-free 좌표
  번역 오버레이.
- `evidence/translation_alignment_evidence.v0.14.json`: 원문을 싣지 않은 언어별
  동일 레코드 정렬 근거.
- `review/translation_review_index.v0.14.json`: 좌표별 사람 검수 상태와 동적 결합
  주의점.
- `translation_validation.v0.14.json`: 재현성, 바이너리 구조, 안전성 검증 결과.
- `tests/test_translation_batch14.py`: 범위·결정성·source-free·재패킹 회귀 테스트.

## 재생성 및 테스트

~~~powershell
python -B workstreams/msggame/build_translation_batch14.py `
  --out-root workstreams/msggame
python -B -m unittest workstreams.msggame.tests.test_translation_batch14 -v
python -B -m unittest discover -s workstreams/msggame/tests -p "test_*.py" -v
~~~

생성기는 설치된 SC·JP·EN·TC 파일의 크기와 packed/raw SHA-256을 먼저 확인한다.
고정 설치본과 다르면 생성 전에 중단하며 설치 경로, 실행 파일, 폰트, 메모리에는
어떠한 변경도 가하지 않는다.

## 검증 항목

- 다음 연속 표시 후보 150개를 정확히 선택하고 이전 v0.1~v0.13의 1,950개
  좌표와 중복되지 않음
- 배치 경계 밖인 `(6, 2139, 2)` 이후 리터럴이 재패킹 전후 동일함
- 가변 길이 한국어를 적용한 오프라인 `msggame.bin`의 블록·레코드·리터럴 좌표와
  불투명 바이트코드 보존
- 줄바꿈, 앞뒤 공백, printf 토큰, 이스케이프, 제어문자, PUA 코드포인트와 괄호
  순서 보존
- A/B/final 공개 산출물과 오프라인 재패킹 바이너리의 바이트 동일성
- 공개 JSON의 상용 원문 한자·가나 유출 0건
- 설치된 SC·JP·EN·TC 파일의 작업 전후 SHA-256 동일

## 후속 검수

이번 배치는 동적으로 결합되는 세력명·성명·방침명·개수 사이의 조사와 줄바꿈을
우선 확인해야 한다. `월경지`, `지행`, `맹약 파기`, `주가 변경`과
`칙명 강화`도 실제 화면 문맥과 용어집에 맞춰 최종 통일이 필요하다. 공개
오버레이의 150개 항목은 모두 사람 검수 필요, 런타임 검수 0개로 표시되어 있다.
