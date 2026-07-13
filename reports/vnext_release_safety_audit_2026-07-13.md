# vNext 파일 전용 공개 배포 최종 안전 감사

감사 일자: 2026-07-13
감사 대상: `msgui-p3-font-v3-v0.2` 공개 후보

## 최종 판정

**PASS — 아래에 고정한 ZIP SHA-256을 별도의 신뢰 가능한 배포 채널에도 게시한다는 조건으로 공개 배포 가능하다.**

이 판정은 공식 Simplified Chinese(SC) 경로의 P3 UI 메시지 279개와 Font-v3 한글 글리프 226자 범위에 한정된다. 메모리 패치, 프로세스 주입·후킹, 게임 실행, EXE/DLL 수정, 레지스트리 변경 또는 상주 구성요소는 포함하지 않는다. 완성된 상용 게임 리소스도 배포본에 들어 있지 않다.

최종 후보는 다음과 같다.

- 폴더: `KR_PATCH_WORK/releases/msgui_p3_file_only_v0.2_2026-07-13`
- 폴더 파일 수: 16개(매니페스트가 열거한 15개 파일 + 매니페스트 자체)
- 매니페스트 SHA-256: `0ACD79C83464F6306C2910C253EE3E022965CCFF5DDE570DF31D64648003B7FC`
- ZIP: `KR_PATCH_WORK/releases/msgui_p3_file_only_v0.2_2026-07-13.zip`
- ZIP 크기: 181,648바이트
- ZIP SHA-256: `58A66AF9311D120EA77E0E1F31D6D29E0D0E1CF8E15A28A51223B065214805F8`
- SHA sidecar: `KR_PATCH_WORK/releases/msgui_p3_file_only_v0.2_2026-07-13.zip.sha256`
- sidecar SHA-256: `D977FA4223ED5C94CEE5E24103DCC24028213388C1AD784D4D80A043DFF8636C`

sidecar 본문은 위 ZIP SHA-256과 파일명을 정확히 기록한다.

## 공개 구성의 재배포 적합성

### 메시지 레시피

- 경로: `components/message/msgui_sc.recipe.json`
- SHA-256: `49570FE246028113C19AE2DFCB12633DC9EC23401A02EDA3B95245EB611E070D`
- operation: 279개, ID 중복 없음
- 정렬된 operation ID 배열 SHA-256: `A3B42B27D59F325D9FBB276D36E5DAD5255E34FA82E789C5ECCFE12CA9979854`
- 상용 SC 원문은 문자열로 보관하지 않고 각 원문의 UTF-16LE SHA-256만 보관한다.
- 공식 SC stock에서 재조립한 target은 86,298바이트이며 SHA-256은 `B3203C89A99840AEC736936268803F685A7F2575E766AFB4C9D6E052383E86E6`이다.

### Font-v3 레시피와 payload

- 레시피 SHA-256: `1A2B882AF265D599974B5278C409CE76B4435DF9CE5BB0FDC751B6881F0BE691`
- 한글 raster codepoint: 정렬·고유 226자
- entry 6 payload: 520,704바이트, `BBBEE931A8F856C220BFC1489BC8DF5B026C687E78C64A926A750DAC3B68F96B`
- entry 7 payload: 231,424바이트, `A3319739970E41A39FBDCE1FE6DB4AF7EE91A8F165C8F741DBC524653442B3B1`
- payload는 Noto KR에서 raster한 프로젝트 소유 글리프 픽셀만 담고 있으며 완성 G1N/LINK/상용 atlas 또는 TTF는 아니다.
- Noto Sans KR 및 Noto Serif KR의 OFL 원문을 함께 포함한다.
- 공식 SC stock에서 재조립한 `res_lang.bin` target SHA-256은 `73E3759BF1886E95C769A95EB212F7ED34B7546E9A3DFA1EB49F542A7018E6B7`이다.

공개 폴더에는 완성 `msgui.bin`, 완성 `res_lang.bin`, 완성 G1N, 원본 상용 폰트, 게임 EXE/DLL이 없다.

## 결정적 재빌드

동일한 builder와 고정된 offline/runtime evidence를 사용하여, 최종 후보와 다른 부모 디렉터리 아래에 동일 basename으로 독립 재빌드했다.

- 두 폴더의 16개 상대 경로·크기·SHA-256 차이: 0개
- 매니페스트 byte-exact: PASS
- ZIP byte-exact: PASS
- sidecar byte-exact: PASS
- 독립 재빌드 매니페스트 SHA-256: `0ACD79C83464F6306C2910C253EE3E022965CCFF5DDE570DF31D64648003B7FC`
- 독립 재빌드 ZIP SHA-256: `58A66AF9311D120EA77E0E1F31D6D29E0D0E1CF8E15A28A51223B065214805F8`
- 독립 재빌드 sidecar SHA-256: `D977FA4223ED5C94CEE5E24103DCC24028213388C1AD784D4D80A043DFF8636C`

메시지 target 및 font entry/archive의 별도 2회 재조립 결과도 각각 고정 target hash와 일치했다.

## 패키지 변조 방어 검증

동결된 최종 후보에서 패키지 내부 `Verify`와 외부 독립 `Audit-ReleaseVNext.ps1`를 다시 실행했고 둘 다 정상 후보를 PASS로 판정했다. 외부 감사 결과는 `nobu16.file-only-public-audit.v2`, `passed=true`, `package_file_count=16`이다.

공격성 fixture 28개를 별도로 생성해 모두 거부되는지 확인했다.

1. 완성 상용 리소스 은닉 3건
   - 완성 P3 target의 이름 변경
   - JSON 추가 필드에 완성 target을 base64로 삽입
   - 중첩 ZIP에 완성 target 삽입
   - 결과: 패키지 Verify와 외부 Audit 모두 3/3 거부
2. JSON 중복 키 16건
   - 대상: 매니페스트, validation evidence, 메시지 레시피, 폰트 레시피
   - 변형: 동일 레벨 direct, nested, `\uXXXX` escaped-equivalent, 대소문자만 다른 키
   - 결과: 패키지 Verify와 외부 Audit 모두 16/16 거부
3. 실행 코드 신뢰 경계 변조 4건
   - installer + 재계산한 매니페스트
   - Apply wrapper + 재계산한 매니페스트
   - `FileRecipeCore.cs` + 재계산한 매니페스트
   - `JsonKeyGuard.cs` + 재계산한 매니페스트
   - 결과: 외부 Audit가 4/4를 패키지 코드 실행 전에 거부
   - installer fixture에 넣은 무해한 marker 생성 코드는 실행되지 않았고 marker는 존재하지 않음
4. ZIP 구조 공격 5건
   - duplicate member, case collision, traversal, nested archive, symlink
   - 결과: 외부 Audit가 5/5 거부

총 결과는 **28/28 hostile fixture 거부**이다.

재현 자료:

- probe: `KR_PATCH_WORK/tests/probe_vnext_release_defenses.py`
- probe SHA-256: `A3DB1ADC703E8692F07FB61FE85BAC1F904526326DA1E9B62EF44B68267F0F22`
- 결과: `KR_PATCH_WORK/tmp/release_safety_audit/vnext_defenses/probe_report.json`
- 결과 SHA-256: `A8EC916C8C82DDF8F1EAF4AC6C38FF1A685971F9F142C622FD2A9A0B63B3B982`

이 방어 검증은 기존 감사기의 이름 변경, base64 추가 필드, 중첩 ZIP 우회를 실제로 재현한 뒤 vNext가 세 우회를 모두 차단하는 방식으로 수행했다.

## 설치·복원 안전성

격리 game root에서 수행한 offline suite는 다음을 모두 PASS했다.

- 패키지 Verify
- 공식 SC stock에서 Apply 후 두 target hash 일치
- 검증된 두 stock backup 생성
- transaction journal이 `applied`에 도달
- Restore 후 두 stock hash 일치
- 손상된/미지원 stock 거부 및 기존 파일 보존
- message/font 혼합 상태를 검증된 backup으로 stock/stock 복구
- 게임 프로세스가 감지될 때 작업 거부 및 기존 파일 보존
- 패키지 변조 거부
- 개발 마일스톤 gate 거부
- 실제 설치본 파일이 격리 시험 전후 변하지 않음

코드 감사상 installer는 다음 순서를 지킨다.

- 정확한 stock hash 확인
- 두 backup을 같은 파일시스템에 durable copy하고 크기·hash 검증
- 첫 resource 교체 전에 `apply_ready` journal을 atomic write
- 각 target을 대상 파일과 같은 디렉터리의 sibling temp에 durable write하고 hash 검증
- `File.Replace` 전후에 게임 정지 및 pair hash를 다시 확인
- 각 단계 journal 갱신
- 중간 실패 시 검증된 backup을 사용해 stock pair 복구 시도
- operation lock으로 동시 실행 거부
- Restore도 backup hash를 먼저 확인하고 같은 교체·검증·journal 절차 사용

offline evidence:

- `KR_PATCH_WORK/reports/release_vnext_offline_validation_2026-07-13.json`
- SHA-256: `C23532C5269E1EA903D7C4A075BF1BADF9A3E10018D35C1F19178C60BFE0CD37`

### 남은 비차단성 failure-injection 공백

정상 Apply/Restore, 미지원 stock, 혼합 상태, 실행 중 프로세스, 변조 패키지는 동적으로 검증했다. 다만 모든 파일 쓰기 지점별 전원 차단, 실제 디스크 고갈, 파일시스템 자체 손상, journal과 backup이 동시에 물리적으로 손상되는 경우까지 자동 주입한 것은 아니다. 이 경우 코드는 인식할 수 없는 상태를 임의로 덮지 않고 fail-closed하도록 작성되어 있으나, 극단적인 저장장치 손상에는 게임 파일 검증 또는 수동 지원이 필요할 수 있다.

## 런타임 증거와 최종 원복 상태

runtime evidence는 다음을 PASS로 기록한다.

- 정상 부팅
- P3 대표 화면의 한글 UI 표시
- 대표 화면 missing glyph 및 clipping 확인
- 정상 종료
- QA 후 stock 원복

runtime evidence:

- `KR_PATCH_WORK/reports/release_vnext_runtime_validation_2026-07-13.json`
- SHA-256: `6C0B0D9F858DC504948CCC04E52899C422E8BC05288F8695554F6845086C23AE`

관찰 범위에는 메인 메뉴, 무장 편집/상세, 공통 조작, 세력 목록 등이 포함된다. settings/gallery의 모든 하위 화면은 이번 P3 관찰 범위 밖이다.

감사 종료 시 실제 설치본은 stock이고 일치하는 게임 프로세스는 0개였다.

- `MSG_PK/SC/msgui.bin`: 60,829바이트, `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- `RES_SC/res_lang.bin`: 160,318,119바이트, `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`

## 외부 해시 신뢰 경계

패키지 내부의 매니페스트와 verifier는 우발적 손상 및 단일 파일 변조를 강하게 탐지한다. 개발 트리의 독립 Audit는 installer, wrapper, core, JSON guard를 외부 고정 hash와 비교한 다음에만 패키지 Verify를 실행하므로 감사 과정에서 변조된 installer가 먼저 실행되는 문제도 차단한다.

그러나 공격자가 ZIP, 매니페스트, verifier를 모두 함께 교체할 수 있는 배포 채널을 장악하면 패키지 내부의 자체 hash만으로 배포자 신원을 증명할 수 없다. 같은 서버에서 ZIP과 `.sha256`을 함께 바꾸는 공격에도 sidecar 단독으로는 충분하지 않다.

따라서 공개 배포 시 반드시 다음 중 하나를 시행해야 한다.

- ZIP SHA-256 `58A66AF9311D120EA77E0E1F31D6D29E0D0E1CF8E15A28A51223B065214805F8`을 배포 파일과 분리된 신뢰 가능한 게시물에 고정
- 가능하면 그 hash 또는 ZIP에 배포자 전자서명 추가
- 사용자는 Apply 전에 외부 게시 hash와 ZIP을 비교하고, 불일치하면 실행하지 않음

이 외부 고정 hash 조건을 충족할 때 현재 v0.2 후보는 파일 전용 공개 배포 기준을 만족한다.
