# MSGUI 전체 한글화 진행 보고 — 2026-07-13

## 결론

공식 간체중문(SC) 가로쓰기 경로를 바탕으로 `msgui` 전체 5,100개 ID의 개발 카탈로그와 안전한 빌드/레시피 파이프라인을 만들었다. 현재 p3 기준 279개 UI 문자열을 1차 번역했으며, 원본 게임 파일은 변경하지 않았다.

이 p3는 아직 배포본이 아니다. 226개 한글 음절을 포함하는 Noto KR 폰트 v3와 실제 게임 화면 검수가 끝나야 첫 확장 마일스톤 배포 후보가 된다.

## 현재 수치

- 전체 ID: 5,100
- 완전 공백: 1,038
- 1차 번역: 279
- 비공백 잔여 미번역: 3,783
- p3 비공백 요구 문자: 238
- p3 한글 음절: 226
- 카탈로그 검증 오류/경고: 0/0
- 단위 테스트: 6/6 통과

## 구현 내용

### 카탈로그 v2

`tools/msgui_catalog_v2.py`가 다음을 수행한다.

- EN/JP/SC/TC 네 언어의 5,100개 ID 정렬 및 원문 해시 고정
- 개발용 JSONL 초기화와 기존 번역 seed 병합
- compact 번역 batch의 ID/영문 원문/SC 해시 게이트 병합
- `%d`, `%s`, 폭 지정자 순서 검증
- ESC 색상 코드, PUA 아이콘, 줄바꿈 불변성 검증
- 별도 작업 디렉터리로만 SC `msgui.bin` 재구축
- 번역 코퍼스 기반 `glyph_demand.json` 생성

### 공개용 메시지 레시피

`tools/build_file_only_msg_recipe.py export-build` 경로를 추가했다.

- 개발 카탈로그 및 전체 상용 원문을 포함하지 않음
- 원문은 ID별 UTF-16LE SHA-256만 저장
- 번역 문자열과 원본 파일 해시만으로 대상 파일을 재현
- 고정 대상과 바이트 단위 동일성 확인

### 번역 묶음

- 기존 메인 메뉴 seed: 9개
- `msgui_core_ui_0003_0100.v0.1.json`: 공통 버튼/시스템 메뉴 89개
- `msgui_core_ui_0101_0190.v0.1.json`: 무장 편집/군단/성 관리 87개
- `msgui_core_terms_0301_0400.v0.1.json`: 핵심 시스템 용어/상태 94개

용어 기준은 `workstreams/msgui_full/GLOSSARY_KO.md`에 기록했다. 영문판의 `Province`가 실제 원문 `軍団`인 사례처럼 EN 표기와 원뜻이 다르면 JP/SC 공통 의미를 우선한다.

## p3 고정값

| 산출물 | SHA-256 |
|---|---|
| `tools/msgui_catalog_v2.py` | `9310505FE993D5D954DC181081B2D466B7BEBC170F0C2DC8902EAC3B04BBCE47` |
| `tools/build_file_only_msg_recipe.py` | `2BD3B1B0A18CD504622C758D738F49680E75280306B7F8C2EE1E62268719B8B2` |
| `catalog_v2/msgui.meta.json` | `997586BC67C788821352192116C195EE753E58FE91FC825669C7E151374C8B9E` |
| `catalog_v2/msgui.catalog.p3.jsonl` | `80E1B46F829F810FA4E55C412D92ED8FC8B48CEFB11FC826C3CD81FED83232BA` |
| `catalog_v2/validation.p3.json` | `D666B50E0AE333DDDF9BEAB5EC2E2E222BAA4FDABBF47C505007C8201C46A859` |
| `build_p3_core_terms/glyph_demand.json` | `43C23F44A9794A1461BA84AEB919FDC661B97D285BA96AE3102F8A3842C5D8DA` |
| `build_p3_core_terms/msgui.build-manifest.json` | `9E943FBA8EC4C6F5C0CE84BD69900A90D532502E2B41C2E68AE0AE9AD5262182` |
| p3 개발 대상 `msgui.bin` | `B3203C89A99840AEC736936268803F685A7F2575E766AFB4C9D6E052383E86E6` |
| 공개용 메시지 레시피 | `49570FE246028113C19AE2DFCB12633DC9EC23401A02EDA3B95245EB611E070D` |

279개 operation의 오름차순 ID 배열(UTF-8 compact JSON) SHA-256은 `A3B42B27D59F325D9FBB276D36E5DAD5255E34FA82E789C5ECCFE12CA9979854`다.

위 값은 `능력·기타`를 stock 전 맵에서 지원되는 `능력/기타`로 교정한 뒤 다시 생성한 현재 p3 고정값이다.

## 검증 결과

- 네 언어 원본 packed/raw SHA: 통과
- 원문 ID/문자열 해시: 통과
- 번역 토큰/제어문자 invariant: 통과
- raw 테이블 재파싱: 통과
- wrapper 재압축 후 해제: 통과
- 공개 레시피 → p3 대상 바이트 동일 재현: 통과
- 새 작업 파일의 프로세스/주입/레지스트리/게임 실행 API 정적 검색: 0건
- 설치된 `MSG_PK/SC/msgui.bin`: stock SHA 유지
- 설치된 `RES_SC/res_lang.bin`: stock SHA 유지

## 인벤토리에서 확인한 위험

- SC printf: 641행, 987개
- ESC 스타일 코드: 26행, 54개
- LF: 128행, 180개
- PUA: 20행, 23자
- SC가 비어 있지만 다른 언어에 문구가 있는 ID: 119개 — 자동 제외 금지
- SC 중복 문자열만으로 자동 전파하면 의미 충돌 가능: 다국어 튜플 해시까지 같아야 제안 가능
- ID 3904는 SC/TC의 printf 순서가 다르므로 SC 순서를 기준으로 수동 검수 필요

## 다음 게이트

1. p3 `glyph_demand.json`을 입력으로 SC Noto KR 폰트 v3 생성
2. append-tail 구조/맵/기존 atlas 보존 독립 검증
3. 메시지+폰트 레시피를 격리된 테스트 게임 사본에 결합
4. 실제 화면에서 잘림, 문맥, 누락 글리프를 확인
5. 통과한 문자열만 `reviewed`로 승격
6. 파일 전용 설치/복원/중단 복구를 포함한 마일스톤 배포본 조립

## 후속 진행 업데이트

- Font-v3 결정론 빌드 완료: 요구 238자, 생성 한글 226자
- 독립 2회 빌드와 기존 파일 전용 applier 재구성의 바이트 동일성 통과
- P3 개발 후보 적용 해시 통과
  - 메시지: `B3203C89A99840AEC736936268803F685A7F2575E766AFB4C9D6E052383E86E6`
  - 폰트: `73E3759BF1886E95C769A95EB212F7ED34B7546E9A3DFA1EB49F542A7018E6B7`
- 올바른 작업 디렉터리에서 게임 실행 시 오류 9001 없음
- 실제 실행은 일본어 경로(`初めから`, `武将編集`, `設定`)였으므로 SC/P3 런타임 판정에서는 제외
- 게임 정상 종료 후 두 설치 파일을 stock SHA로 정확히 복원
- 런타임 시도 보고서: `reports/msgui_p3_runtime_attempt_2026-07-13.md`
- 일본어 경로 증거 화면: `reports/screenshots/msgui_p3_blocked_japanese_path_2026-07-13.png`

이후 공식 런처에서 간체중문을 선택해 동일 P3를 재적용했고 실제 화면 QA에 통과했다.

- SC 표지 `请点击鼠标` 확인
- 메인 메뉴 상·하단, 무장 편집 상세, 새 게임 공통 UI 스크린샷 4장 고정
- 화면에 실제 표시된 14개 ID만 `surface_evidence`로 기록
- 한글 직접 Unicode 조회, 가로쓰기, 대표 글리프, 명백한 버튼 잘림: 통과
- 빈 한글/대체 글리프/명백한 손상: 0건
- 게임 정상 종료와 stock 원복: 통과
- 런타임 증거: `reports/msgui_p3_runtime_pass_2026-07-13.json`

메시지/Font-v3의 대표 화면 `runtime_verified`는 참이다. 다만 설정·갤러리 하위 화면,
279개 번역 전수, 226개 생성 글리프 전수는 아직 검수하지 않았다. 이 시점에는 vNext
설치기와 독립 안전 감사가 남아 있어 전체 공개 배포본의 `release_eligible`을 거짓으로 유지했다.

## vNext 파일 전용 배포 및 후속 번역 업데이트

P3 메시지 279개와 Font-v3 226개 한글 음절을 결합한 첫 확장 배포 후보를 조립했다.
이 후보는 게임 실행·메모리 접근·DLL 주입·후킹·EXE/레지스트리 변경 없이 종료된
게임의 SC 메시지/폰트 파일만 레시피로 재구성한다.

- 배포 폴더: `releases/msgui_p3_file_only_v0.2_2026-07-13/`
- ZIP: `releases/msgui_p3_file_only_v0.2_2026-07-13.zip`
- 파일 수: 16개
- manifest SHA-256: `0ACD79C83464F6306C2910C253EE3E022965CCFF5DDE570DF31D64648003B7FC`
- ZIP SHA-256: `58A66AF9311D120EA77E0E1F31D6D29E0D0E1CF8E15A28A51223B065214805F8`
- sidecar SHA-256: `D977FA4223ED5C94CEE5E24103DCC24028213388C1AD784D4D80A043DFF8636C`
- 동일 basename 독립 재조립: 16파일/manifest/ZIP/sidecar byte-exact
- 격리 설치/복원, bad stock, 혼합 journal 복구, 실행 중 프로세스 거부: 통과
- 완성 리소스 은닉, JSON 중복 키, 실행 코드 변조, ZIP 경로 공격 hostile probe: 28/28 거부
- 변조 installer marker: 감사 전에 실행되지 않음
- package/ZIP 정적 금지 API 검색: 0건
- 최종 설치본 두 파일: stock SHA 유지

이 결과로 v0.2 manifest의 `release_eligible=true`가 활성화되었다. 패키지 내부 검증은
전체 패키지의 악성 교체를 스스로 인증할 수 없으므로, 실제 배포에서는 ZIP 밖의
`.zip.sha256`과 신뢰된 배포 페이지의 ZIP 해시를 먼저 대조해야 한다.

동시에 canonical P3를 바꾸지 않는 별도 배치로 ID 401–1100 번역을 확장했다.

- 추가 번역: 692개
- 구조용 공백 보류: 8개 (`513`, `689`, `691`, `712–714`, `733`, `734`)
- P3와 결합한 임시 누적 buildable: 971개
- 실제 바이너리 변경: 931개
- 임시 대상 SHA-256: `5E4B26FC465F4F0F4C046462714E7B677D7B479FDA6023086EF7F9A8817E6984`
- 요구 문자: 387개, 한글 음절 342개
- 카탈로그 검증 오류/경고: 0/0

이 401–1100 배치는 아직 v0.2에 들어 있지 않다. 다음 마일스톤에서 canonical 병합,
새 글리프 폰트 생성, 격리 설치/복원, 실제 화면 회귀 QA를 다시 수행한다.
