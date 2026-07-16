# Steam PK 1.1.7 JP 기본 메시지 경로 감사 v2

## 결론

v5의 exact-14 벡터는 `MSG/JP`의 세 메시지 파일을 모두 포함한다.
`strdata.bin`은 기존 v3 후보에서 계속 포함되고, `msggame.bin`과
`ev_strdata.bin`은 각각 별도의 Switch v1.3 전송 모듈로 새로 포함된다.

다만 이것은 **후보 패키지의 파일 범위** 판정이다. 이 감사는 실행 중인
`NOBU16PK.exe`의 파일 열기 추적을 수행하지 않았다. 따라서 특정 화면에서
어느 파일을 실제로 열었다고 단정하지 않는다.

화면 제보의 지도 보좌관 대사는 다음의 정적 증거로 `MSG/JP/msggame.bin`에
강하게 귀속된다.

- 제보 대사의 UTF-16LE SHA-256은
  `279D8D1246B6C655F8E6FEC0DA1CAA7848AAA1E0EB58C1AA13370EBF5E84BC5B`다.
- Steam JP 기본 `msggame.bin`의 좌표 `(block=13, record=217, literal=0)`에
  정확히 한 번만 있다.
- 같은 해시는 `MSG_PK/JP/msggame.bin`을 포함한 JP 메시지 파일 11개를
  원시 UTF-16LE로 대조했을 때 다른 파일에는 없다.

즉, 화면 제보와 정적 자원은 일치하지만, 이 결과는 여전히 파일 열기
트레이스가 아닌 정적 귀속이다. v5의 기본 `msggame.bin` 전송 모듈은 이
좌표를 포함한 22,924개 literal을 대상으로 하므로 이 화면의 미번역은
exact-12/기존 설치 범위가 기본 파일을 빠뜨린 결과와 일치한다.

## exact-14와 실제 Steam JP 메시지 토폴로지

`UpdateVer.txt`가 `1.1.7`인 Steam 설치를 읽기 전용으로 조사했다. v5의
목표 14개는 메시지 10개와 글꼴 4개다.

| 영역 | 실제 파일 수 | v5 포함 | 상태 |
|---|---:|---:|---|
| `MSG/JP` | 3 | 3 | 기본 메시지 전체 포함 |
| `MSG_PK/JP` | 8 | 7 | `msgstf_ce.bin` 1개 보류 |
| JP regular/PK/PORT 글꼴 | 7 | 4 | 확장 2개·PORT3 1개는 별도 판정 필요 |

v5 메시지 경로는 아래와 같다.

- `MSG/JP/ev_strdata.bin`
- `MSG/JP/msggame.bin`
- `MSG/JP/strdata.bin`
- `MSG_PK/JP/msgbre.bin`
- `MSG_PK/JP/msgdata.bin`
- `MSG_PK/JP/msgev.bin`
- `MSG_PK/JP/msggame.bin`
- `MSG_PK/JP/msgire.bin`
- `MSG_PK/JP/msgstf.bin`
- `MSG_PK/JP/msgui.bin`

### 기본 3개 파일의 후보 포함 근거

| 파일 | v5 상태 | 근거 |
|---|---|---|
| `MSG/JP/strdata.bin` | 포함 | v3의 고정 JP 대상이며 후보 SHA-256 `E77CD1F5…` |
| `MSG/JP/msggame.bin` | 포함 | `tutorial_dialogue_trace_msggame_v1`의 Switch v1.3 좌표-정확 전송, 22,924 literal |
| `MSG/JP/ev_strdata.bin` | 포함 | `base_ev_strdata_jp_switch_v13_transfer_v1`의 슬롯/원문 해시/제어문자 검증 전송, 13,045행 |

두 새 기본 전송은 독립 검증 산출물에서 PASS지만, v5 자체는 아직
`verification.v5.json`이나 완성 후보 ZIP을 만들지 않은 조립 준비 상태다.
따라서 이 감사는 배포 승인이나 런타임 PASS가 아니다.

## 남은 런타임 위험 항목

### P0 — `MSG_PK/JP/msgstf_ce.bin`

이 파일은 Steam JP PK 폴더에 실제로 존재하지만 v5 exact-14에는 없다.
표준 단일 블록 메시지 테이블로 파싱되며 20개 문자열 중 8개가 일본어
스크립트를 포함하고 한글 문자열은 0개다. 파일명만으로 화면·기능을
추정할 수 없고, 실행 중 로드 여부도 확인되지 않았다. 따라서 다음
작업은 이 8개를 번역하기 전에 호출 화면 또는 리소스 선택 조건을
추적하는 것이다.

### P1 — 확장 언어 아카이브와 PORT3

`RES_JP/res_lang_exp.bin`, `RES_JP_PK/res_lang_exp_pk.bin`,
`RES_JP_PK_PORT/res_lang_pk_port3.bin`도 Steam JP 설치에 존재하지만 v5
대상에는 없다. 실행 파일의 정적 문자열에는 regular·expansion·PORT1/2/3
파일명이 모두 보인다. 그러나 그 문자열만으로 선택 조건이나 실제
로드를 증명할 수는 없다.

현재 정적 검사에서는 PORT3 및 두 expansion 아카이브의 최상위 LINK
엔트리에 직접 G1N 글꼴 객체가 발견되지 않았다. 이는 현재 글꼴 교체
대상에서 제외할 근거일 뿐, 해당 아카이브가 절대로 로드되지 않는다는
증거는 아니다. 해상도/화면별 파일 열기 추적이나 안전한 재현 화면이
확보되기 전에는 v5 벡터를 성급하게 넓히지 않는다.

## 증거 한계와 다음 순서

1. v5 exact-14 조립 검증을 완료해 기본 3개 포함 후보를 확정한다.
2. `msgstf_ce.bin`의 8개 일본어 문자열을 기능/화면 단위로 분류한다.
3. 필요할 때만 해당 파일을 별도 source-free 전송/번역 모듈로 추가한다.
4. 파일 열기 증거가 생기면 이 보고서의 `정적 귀속` 등급을 `런타임 확인`으로
   승격한다.

`manifest.v2.json`은 원문·완성 게임 리소스·추출 바이너리를 포함하지 않는
기계 판독용 근거다.
