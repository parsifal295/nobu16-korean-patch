# Steam PC 인물 대사 블록 15 감사

## 범위와 입력 경계

현 W45 Steam Korean `msggame.bin`의 블록 15를 PC 원문과 대조했다.

- Base Korean: 2,423 records / 4,485 literal slots / 표시 literal 4,360개
- PK Korean: 2,601 records / 5,035 literal slots / 표시 literal 4,888개
- PK pristine Japanese: 2,601 records / 5,039 literal slots / 표시 literal 4,892개
- PK EN/SC/TC와 Base SC/TC를 PC 문맥 보조로 사용했다.
- pristine Base JP/EN은 현 로컬 백업에 없었다. 따라서 Base는 PK와 현재
  Korean record·PC 보조 원문이 전체 바이트까지 같은 family가 아니면
  source-gap hold로 남겼다.
- Nintendo Switch 한국어는 읽거나 참조하지 않았다.

PK에서 Japanese와 opaque topology까지 완전히 같은 무표식 정적 레코드
183개를 별도로 재검토했다. 이 범위에서는 새 고확신 정적 교체 후보를
확정하지 못했다. 이는 블록 15 전체가 사람이 완독한 번역 완료 판정이 아니라,
안전하게 빌드할 수 있는 추가 정적 변경이 없다는 감사 결과다.

## 의미상 문제지만 정적 후보에서 제외한 항목

| 좌표 | 검토한 대안 | PC 원문 근거 | 제외 사유 |
| --- | --- | --- | --- |
| PK `15:1520:2`, `1521:0`, `1522:0`; Base `15:1505:2`, `1506:0`, `1507:0` | `조장` → `조두` | JP `組頭`, EN *chief*, SC/TC `组头`/`組頭`; PK `15:1673`은 이미 `조두` | `1520`은 `0143`, `1522`는 `02xx+0143`; `1521`은 current KO가 무표식이지만 pristine JP command topology가 달라 UI/source-topology hold. Base는 source-gap hold. |
| PK `15:2060:1`, `2144:1`; Base `15:2030:1`, `2114:1` | `을 용서해 주십시오` → `을 허락해 주십시오` | JP `をお許しください`, EN *approve it*, SC `请您同意`, TC `請大人准許` | opaque `1b434d023c1b435a` 안의 `02 3c` 런타임 삽입값 때문에 실화면 QA hold. |
| PK `15:2161:1`; Base `15:2131:1` | `을 용서하시오` → `을 허락하시오` | JP `をお許しあれ` | `026432` 및 `02 3c` 런타임 token hold. |
| PK `15:2285:1`; Base `15:2254:1` | `헌언의 용서,` → `헌언의 허락,` | JP `献言の許し、` | `0143` command topology hold; Base/PK control ID도 다름. |
| PK `15:253:0`; Base `15:250:0` | `우선 아닐는지요` 조사 보완 | JP `先決`, SC/TC `首要`, EN priority 문맥 | JP/KR literal topology 차이, `0143`, 폭 변화가 함께 있어 UI hold. |

`용서해` → `허락해` family는 Korean Base/PK raw record가 동일하고 교체 전후
literal 길이도 같지만, runtime token을 보존한 채 실제 이름·조사·폭을 확인하지
않은 정적 치환은 하지 않는다.

## 줄바꿈과 문체 보류

아래 단어 내부 LF는 원문 쪽에도 강제 배치가 있어 자동 병합하지 않았다.

- Base `15:500:0` / PK `15:507:0`: `보내서\n라도`
- Base `15:637:1` / PK `15:644:1`: `일치\n하고`, `모르오\n만`
- Base `15:638:1` / PK `15:645:1`: `교섭\n을`
- Base `15:645:1` / PK `15:652:1`: `분들\n을`
- Base `15:657:0` / PK `15:664:0`: `교섭하\n면`
- Base `15:997:0` / PK `15:1004:0`: `필연\n하여`

`영매`(PK `15:440:0`, Base `15:433:0`)는 JP `英邁`의 유효한 한자음이다.
현대어에서의 동음이의 혼동은 별도 문체 재번역 검토 대상일 수 있으나, 오탈자로
자동 수정하지 않는다.

이 감사는 Steam 파일, 백업, Git 원격, 푸시, 릴리즈를 변경하지 않는다.
