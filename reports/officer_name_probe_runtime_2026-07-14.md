# 장수명 파일 전용 Probe v0.1 검증

## 결론

SC 가로쓰기 경로에서 `msgdata`와 `msgev`를 함께 바꾸는 방식으로 장수명을 한글로 표시할
수 있다. 메모리 접근, DLL 주입, 후킹, EXE·레지스트리 변경은 사용하지 않았다.

2026-07-14 비 Steam PC 설치본에서 `NOBU16PK.exe`의 작업 폴더를
`F:\Games\NOBU16`으로 지정해 실행했다. 실존 무장 편집 화면에서 다음 표시를 확인했다.

- 목록 첫 행: `아츠지 사다유키`
- 성 입력칸: `아츠지`
- 이름 입력칸: `사다유키`
- 우측 인물 카드 합성명: `아츠지 사다유키`
- 한글 공백·글리프 누락·두부 문자는 관찰되지 않음

`오다 노부나가`, `이시다 미츠나리`도 동일한 파일에 적용했으며 사용자의 후속 화면 검수를
위해 게임을 해당 편집 화면에 둔 상태로 인계했다. 이 두 이름의 화면별 최종 판정은 아직
기록하지 않는다.

## 변경 범위

| 리소스 | 역할 | overlay 항목 | 실제 변경 |
|---|---|---:|---:|
| `MSG_PK/SC/msgdata.bin` | 분리 성·이름 및 중복 슬롯 | 9 | 9 |
| `MSG_PK/SC/msgev.bin` | 합성명 | 3 | 3 |

대상 장수는 `아츠지 사다유키`, `이시다 미츠나리`, `오다 노부나가` 세 명이다. `小田`은
영문판에서 `Oda`로 같게 보이지만 `織田`과 다른 성이므로 변경하지 않았다.

## stock 및 target 핀

| 리소스 | stock SHA-256 | target SHA-256 |
|---|---|---|
| `msgdata.bin` | `0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E` | `4BC5079DA4ADF787BFCF5D7B2479F659E6F57BFB13572A6B696D26CB45F5063F` |
| `msgev.bin` | `7221A53E6E5CF493A3FAFFFCE35280E8147898120EEC59E460A2429AA265C1F9` | `AFE9F0CCA5518F6BA04B44449971C004A9D674F0663DAF310780988C4A1977B9` |

raw stock 핀은 `msgdata` 499,760바이트
`1290BCDF6B00C6E4516061888C618BC66A246375E271C9D1330A9D168037FBCF`, `msgev`
750,584바이트 `99E0338A64FF4140AD6E27503B1BF138AC44F5B68F01973ED61D0C949619DC91`다.

두 독립 빌드는 target, manifest, recipe가 각각 바이트 단위로 일치했다.

| 산출물 | SHA-256 |
|---|---|
| `msgdata.build-manifest.json` | `52A4A532625C889B7276C88AF9EE49B02CC3CAC8B1617F4CAD337ABE042AC506` |
| `msgdata_sc.recipe.json` | `BEAC279B2A749CAC9156C8196EE204D648370B13D507D5AE31EBB3B91BF9B585` |
| `msgev.build-manifest.json` | `93CE706D3F5C5A935C372DB359529124636330B588CF56B479F44019C60A6177` |
| `msgev_sc.recipe.json` | `923414FCEB03552B5370ED495F4E29439AF38D33D888679B0377175C78FE93D1` |

## 안전·배포 검증

- 공개 overlay와 recipe에는 공식 원문 전체가 없고 원문 해시만 있음
- 완성된 `msgdata.bin`, `msgev.bin`은 `tmp/`에만 있으며 Git 제외
- 기존 recipe applier로 stock에서 target을 바이트 단위로 재생성함
- stock 입력은 빌드 전후 동일함
- 현재 Font-v4에 세 이름이 요구하는 한글 글리프가 모두 존재함
- 전체 unittest 25개 통과(신규 common-message 11개 포함)
- 로컬 원본 백업은 `backups/officer_name_probe_v0_1/`에 두고 stock SHA-256을 검증함

## 남은 작업

이 결과는 이름 저장 위치와 공백 조합을 검증하는 개발 probe다. 전체 약 3,000개 역사무장
합성명과 `msgdata` 성·이름 사전을 번역·검수하고, `msgui`·`msgdata`·`msgev`의 한국어
글리프 합집합으로 차기 폰트를 만든 뒤, 세 메시지와 폰트를 하나의 원자적 적용·복원 거래로
묶어야 공개 배포본이 된다.
