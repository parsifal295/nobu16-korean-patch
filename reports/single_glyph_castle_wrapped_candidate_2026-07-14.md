# 오다와라 U+D792 wide-glyph 실제 SC 래퍼 후보

## 결과

`小田原`의 SC `msgdata` ID `9168`만 `U+D792` 한 글자로 바꾸고, SC font
entry 6/7의 두 테이블에 `U+D792` wide bitmap을 각각 한 record씩 추가한
**실제 게임 래퍼 형식의 비설치 후보**를 완성했다.

- 메시지: stock 8-byte prefix를 보존한 raw-LZ4 `MSG_PK/SC/msgdata.bin`
- 폰트: 42-entry LINK 형식의 `RES_SC/res_lang.bin`
- 공용 `城` 접미사 ID `9936`: 변경하지 않음
- 설치 파일, 실행 파일, 프로세스 메모리, 레지스트리, canonical/release 폴더:
  이 작업에서는 접근·변경하지 않음
- 게임 실행: 하지 않음
- Apply/Restore harness: 작성·정적 파싱만 하고 실행하지 않음

이 후보는 complete commercial resource를 포함하므로 `tmp`의 비공개 로컬 시험
산출물이다. 배포본에 넣을 수 없으며 `release_eligible=false`,
`redistributable=false`로 고정했다.

## 최종 비설치 후보

루트:
`KR_PATCH_WORK/tmp/single_glyph_castle_probe/wrapper_candidate`

| 대상 | 크기 | SHA-256 |
|---|---:|---|
| `MSG_PK/SC/msgdata.bin` | 501,741 | `165353713703A2A1D72C24D6C9A7D5709F21FA3D2B641993BE786BA14B2B17CC` |
| `RES_SC/res_lang.bin` | 179,188,060 | `AFBB287B5418FBCB44B083F7D77E5F53426AE7E1AB23C6B69F17EC98E0EB7258` |

stock gates:

| 대상 | 크기 | SHA-256 |
|---|---:|---|
| SC `msgdata.bin` | 267,385 | `0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E` |
| SC `res_lang.bin` | 160,318,119 | `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99` |

`msgdata`는 프로젝트의 결정적 literal-only raw-LZ4 encoder로 만들었기 때문에
stock의 최적화 압축보다 크다. wrapper prefix는 stock과 같은
`01 01 C4 C1 FA 7F 00 00`, uncompressed size는 499,756,
compressed size는 501,717이다. 압축 해제·재압축·재해제 왕복을 통과했다.

## 정확한 메시지 변경

래퍼에서 raw를 다시 추출한 뒤 29,210개 문자열을 stock과 전부 비교했다.

| ID | stock | 후보 |
|---:|---|---|
| 9168 | `小田原` | `U+D792` 한 글자 |

변경 ID 목록은 정확히 `[9168]`이다. ID `9936`의 공용 `城`은 stock과 동일하며,
나머지 29,209개 문자열도 의미상 동일하다. 문자열 길이가 줄어들어 뒤쪽 offset
table 값과 물리 string pool 위치는 재계산되지만, parse 결과의 텍스트 차이는
9168 하나뿐이다.

재추출 raw:

- 크기: 499,756
- SHA-256:
  `2F83D99CAFD4E0291A2C33DFAFC9AB79B4DB2FE37CD5FD8DD6C101B4D724C48E`
- `nobu16_msg_table.py verify`: 29,210 strings, byte-identical parse/rebuild PASS

wide bitmap 자체에는 이전 단일 후보와 같은 `오다와라성` 전체가 들어 있다. 공용
`城`을 그대로 두었으므로 실제 화면에서는 wide quad 방향을 먼저 확인하기 위한
name-only 진단이다. 별도 접미사가 함께 보이거나 아래에 남을 수 있으며, 이는 최종
번역 모양이 아니라 renderer가 넓은 한 글리프를 가로로 그리는지 확인하는 목적이다.

## 정확한 폰트/LINK 변경

stock과 후보 LINK를 모두 parse/rebuild하여 byte-identical임을 확인했다.

- LINK entry count: 42
- version: 1
- reserved: 0
- 변경 payload entry: 정확히 `[6, 7]`
- 나머지 40개 entry payload: 모두 byte-identical
- 모든 entry trailer/gap: stock과 동일
- entry table의 뒤쪽 offset은 6/7 payload 크기 증가에 맞춰 정상 재계산

후보 archive에서 entry 6/7을 다시 압축 해제한 결과:

| entry | raw 크기 | raw SHA-256 |
|---:|---:|---|
| 6 | 25,829,480 | `22E253653364A0F1F4FC6F597D2EBFA0B5B1B8A12B84F0380046C2C8106570A1` |
| 7 | 11,776,680 | `E239E92F7F4E2AC866B9918D553EBE8FB657633B5875DA9B3664787EBD22C795` |

`validate_g1n_surgical.py --mode append-tail --expect-codepoints U+D792`를
두 재추출 entry에 다시 실행했고 모두 PASS했다.

| entry | table별 신규 record | table별 변경 map | 크기/stride |
|---:|---|---|---|
| 6 | `[1, 1]` | table 0/1 각각 `U+D792` 한 칸 | `240x48`, advance 240, stride -120 |
| 7 | `[1, 1]` | table 0/1 각각 `U+D792` 한 칸 | `160x32`, advance 160, stride -80 |

여기서 “한 글리프”는 논리 codepoint `U+D792` 하나라는 뜻이다. 런타임이 접근할
수 있는 entry 6/7 × table 0/1을 모두 덮기 위해 물리 record/pixel 사본은 총
4개다. 각 G1N에서:

- 기존 map은 `U+D792` 셀 외 모두 exact
- 기존 record 전부 exact
- complete stock atlas는 exact prefix
- 신규 pixel만 atlas tail에 존재

## 독립 감사 결과

읽기 전용 wrapper 감사 스크립트가 다음을 한 번에 재검증했다.

1. stock/target 파일 hash gate
2. message wrapper prefix와 raw-LZ4 왕복
3. 메시지 차이가 정확히 ID 9168 하나인지
4. ID 9936 공용 접미사가 그대로인지
5. LINK 비대상 40개 payload와 모든 gap/trailer가 exact인지
6. entry 6/7 wrapper prefix와 재추출 raw hash
7. G1N append-tail 보존식과 `U+D792` 단일 변경
8. harness의 필수 안전 토큰 및 금지된 실행/메모리/레지스트리 동작 부재

결과:

| 증거 | SHA-256 | 결과 |
|---|---|---|
| `WRAPPER_AUDIT.json` | `F2724DABC2107B52F2AEAA4FA10C23E6F0F9DF8C4093D16D591F282E7B205288` | PASS |
| `HARNESS_STATIC_AUDIT.json` | `A90DA1CA4A8D48F507AF50AF4A7C84C65474333CD9BF9E5C2B8BB70B1BF5FC12` | PASS |
| `CANDIDATE_MANIFEST.json` | `234313C43DC99CE0BE2ABEFA1A09CDCEADCAC5B3F2FA357024DE77886BF3341A` | private/non-release |

감사 스크립트:
`KR_PATCH_WORK/tmp/single_glyph_castle_probe/Audit-WrappedCandidate.py`,
SHA-256
`52EA27D853A34F2B1CE1DA5A1D77B550EBA136EBFBD5C67FD4154FDE4E684417`.

## 안전 Apply/Restore harness

파일:
`KR_PATCH_WORK/tmp/single_glyph_castle_probe/Invoke-WideCastleNameOnlyProbe.ps1`

SHA-256:
`6932705E955C6899E700A6D60CB5A83909A0F2EA01784F5821636F1FF4F61CF1`

이 harness는 이번 작업에서 **한 번도 실행하지 않았다**. `Status`도 실행하지 않고
PowerShell AST parser로만 검사했다.

- parse errors: 0
- token count: 1,370
- actions: `Status`, `Apply`, `Restore`
- 경로는 `MSG_PK/SC/msgdata.bin`, `RES_SC/res_lang.bin` 두 개로 고정
- Apply는 두 파일이 정확한 stock hash일 때만 허용
- stock/이 후보 외의 설치 hash는 `unknown`으로 거부
- NOBU16 관련 프로세스가 하나라도 실행 중이면 변경 거부
- 후보와 backup을 모두 SHA-256으로 재검사
- 별도 backup root:
  `KR_PATCH_WORK/backups/single_glyph_castle_name_only_wrapper`
- exclusive `operation.lock`
- 단계별 `journal.json`
- 대상 디렉터리에서 stage 후 `File.Replace`로 same-volume atomic replace
- 두 번째 파일 적용 실패 시 앞서 적용한 파일 자동 원복
- Restore는 역순이며 이미 stock인 파일은 그대로 둠
- EXE 변경, 게임 실행, registry 접근, process memory 접근 코드 없음

현재 다른 시험 패치가 설치되어 있거나 일부 파일 hash가 예상과 다르면 harness는
그 상태를 stock으로 간주하거나 덮어쓰지 않는다. 먼저 그 시험의 전용 Restore로
정상 stock 상태를 회복해야만 이 후보의 Apply가 가능하도록 fail-closed 되어 있다.

## 판정

요구한 **실제 SC wrapper 형식의 name-only 비설치 후보와 원복 가능한 harness**는
완성됐다. 오프라인 구조 판정은 PASS다.

남은 유일한 핵심 판정은 런타임에서 세로 배치기가 240/160픽셀의 단일 glyph quad를
잘라내거나 회전시키지 않고 가로로 그리는지다. 이번 작업에서는 사용자 지시대로
후보 적용과 게임 실행을 하지 않았으므로 `runtime_verified=false`이며, 이 파일을
배포 가능 해결책으로 승격하지 않는다.
