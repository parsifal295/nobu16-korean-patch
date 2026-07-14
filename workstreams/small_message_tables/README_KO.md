# `msgire` · `msgstf` 소형 메시지 테이블 한글화

`MSG_PK/SC/msgire.bin`과 `MSG_PK/SC/msgstf.bin`을 대상으로 하는 파일 전용 한글화 작업선이다. 설치된 게임 파일을 직접 수정하지 않으며, 공개 파일에는 정식판 원문을 넣지 않는다.

## 진행 현황

| 대상 | 완료 / 번역 대상 | 전체 슬롯 | 상태 |
|---|---:|---:|---|
| `MSG_PK/SC/msgire.bin` | **122 / 122** | 122 | 물품·명물 설명문 전체 번역 |
| `MSG_PK/SC/msgstf.bin` | **8 / 8** | 20 | 크레디트의 직책·분야 제목 번역, 고유 인명·회사명 유지 |
| 합계 | **130 / 130** | 142 | 번역 대상 완료 |

`msgstf`의 ID 8~19는 SC·EN·JP 세 판 모두 빈 문자열인 구조 슬롯이다. 번역할 표시 문자열이 아니므로 오버레이에는 넣지 않았고, 완료 수에도 더하지 않았다. 번역 대상 분모 8과 전체 슬롯 수 20은 모두 검증 파일에 고정되어 있다.

## 원문 비공개 형식

공개 오버레이의 각 항목에는 다음 정보만 있다.

- 안정적인 정수 ID
- 해당 SC 문자열의 UTF-16LE SHA-256
- 프로젝트가 작성한 한국어 문자열

SC·EN·JP 원문은 로컬에서 같은 ID로 대조했으며 공개 오버레이에는 싣지 않았다. `msgstf`의 고유 인명과 회사명은 번역 결과의 일부로 라틴 표기를 유지하되, 직책과 제작 분야 제목은 한국어로 바꿨다. 공개 한국어 문자열의 한자·히라가나·가타카나 유출 수는 0이다.

## 파일

- `public/msgire_ko_0000_0121.v0.1.json`: ID 0~121, 122개
- `public/msgstf_ko_0000_0007.v0.1.json`: ID 0~7, 8개
- `build_small_message_tables.py`: 기존 공통 메시지 빌더를 제한적으로 재사용하는 빌드·검증 진입점
- `validation.json`: 소스 핀, 세 언어 ID 정렬, A/B 결정성, 산출물 해시
- `tests/test_small_message_tables.py`: 공개 형식·분모·구조 슬롯·실데이터 A/B 회귀 테스트

## 검증 및 빌드

게임 파일 없이 공개 오버레이 형식만 검사한다.

```powershell
python -B workstreams/small_message_tables/build_small_message_tables.py validate-public
```

설치본을 읽기 전용 입력으로 삼아 별도 출력 폴더에 후보 파일을 만든다.

```powershell
python -B workstreams/small_message_tables/build_small_message_tables.py build `
  --game-root .. `
  --output-root tmp/small-message-build
```

SC·EN·JP 정렬, 원본 핀, 제어문자·공백·자리표시자 보존, 두 번의 바이트 동일 빌드를 한꺼번에 검증한다.

```powershell
python -B workstreams/small_message_tables/build_small_message_tables.py verify `
  --game-root .. `
  --output workstreams/small_message_tables/validation.json

python -B -m unittest workstreams.small_message_tables.tests.test_small_message_tables
```

## 현재 고정 해시

| 항목 | SHA-256 |
|---|---|
| `msgire` 공개 오버레이 | `4DEC23040A1E7B13AE31937545C90D74E783FFBF1140DDF668978C1032AEC4D7` |
| `msgstf` 공개 오버레이 | `1AFB95F0D7B9F5F5CF23CFF1FCCE08CEC8A42FC5BF3A497AA76E8099F31D8CD4` |
| 빌드된 `msgire.bin` 후보 | `045B6ADDD7CF01401A3C10FA69A737B6C32259FA95007584E6A3E32CF2142D2A` |
| 빌드된 `msgstf.bin` 후보 | `C4A18BC5F7F7FCB8D9913D1AABC0C775059B09CE41261AFE38FB23F15146C195` |

`validation.json` 기준으로 A/B 빌드는 바이트 단위로 같고, 설치 게임 파일 변경·프로세스 메모리 접근·실행 파일 변경·레지스트리 변경은 모두 발생하지 않았다.
