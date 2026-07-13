# MSGUI P3 / Font-v3 파일 전용 v0.2 배포 기록

배포 일자: 2026-07-13

## 판정

`msgui-p3-font-v3-v0.2`는 공식 Simplified Chinese(SC) 가로쓰기 경로에서 실제
게임 화면 QA, 격리 설치/복원, 중단 복구, 결정론 재빌드, 공개 폴더/ZIP 독립 감사를
통과했다. 외부에 게시한 ZIP SHA-256을 사용자가 먼저 대조한다는 조건으로
`release_eligible=true`다.

이 배포본은 메모리 패치, 프로세스 부착, DLL 주입, 후킹, 프록시 DLL, EXE/런처
수정, 레지스트리 변경, 게임 자동 실행을 사용하지 않는다.

## 배포 산출물

- 폴더: `KR_PATCH_WORK/releases/msgui_p3_file_only_v0.2_2026-07-13/`
- ZIP: `KR_PATCH_WORK/releases/msgui_p3_file_only_v0.2_2026-07-13.zip`
- ZIP 크기: 181,648바이트
- ZIP SHA-256: `58A66AF9311D120EA77E0E1F31D6D29E0D0E1CF8E15A28A51223B065214805F8`
- sidecar: `KR_PATCH_WORK/releases/msgui_p3_file_only_v0.2_2026-07-13.zip.sha256`
- sidecar SHA-256: `D977FA4223ED5C94CEE5E24103DCC24028213388C1AD784D4D80A043DFF8636C`
- manifest SHA-256: `0ACD79C83464F6306C2910C253EE3E022965CCFF5DDE570DF31D64648003B7FC`
- 공개 파일: 16개

## 범위

- P3 `msgui` operation: 279개
- Font-v3 한글 raster codepoint: 226개
- P3 메시지 target: `B3203C89A99840AEC736936268803F685A7F2575E766AFB4C9D6E052383E86E6`
- Font-v3 `res_lang.bin` target: `73E3759BF1886E95C769A95EB212F7ED34B7546E9A3DFA1EB49F542A7018E6B7`
- 공개 구성: 원문 hash 기반 메시지 recipe, OFL 글꼴에서 생성한 글리프 픽셀,
  font recipe, OFL 원문, 파일 전용 설치/검증/복원 코드
- 제외: 전체 stock/수정 상용 리소스, 개발용 4개 언어 카탈로그, TTF, EXE/DLL

## 검증

- 동일 basename 독립 재빌드: 폴더 16/16 파일, manifest, ZIP, sidecar byte-exact
- 격리 stock → Apply → target/target → Restore → stock/stock: 통과
- bad stock, mixed journal recovery, 실행 중 게임/런처: 안전 거부/복구 통과
- 완성 리소스 은닉, JSON 중복 키, 코드 변조, ZIP 공격 hostile fixture: 28/28 거부
- 변조 installer marker: 감사 전에 실행되지 않음
- PowerShell 문법 및 금지 API 정적 검사: 통과
- 실게임 SC 대표 화면: 한글 직접 조회, 가로쓰기, 대표 missing glyph/clipping, 정상 종료 통과
- 설정/갤러리 전체 하위 화면, 279개 문자열 전수, 226개 생성 글리프 전수는 미검수

독립 보고서:

- `KR_PATCH_WORK/reports/vnext_release_safety_audit_2026-07-13.md`
- 보고서 SHA-256: `4DF6F442305684F114E622B002B6C4E0CE36D4941D5172B102AFFF1E1FA73B4B`

## 사용자 설치 순서

1. 신뢰된 배포 게시물의 ZIP SHA-256과 받은 ZIP을 대조한다.
2. 압축을 게임 폴더 바로 아래에 푼다.
3. 게임과 공식 런처를 종료한다.
4. `VERIFY_PACKAGE.bat`, `APPLY_KOREAN_PATCH.bat` 순서로 실행한다.
5. 공식 런처를 직접 열어 언어를 **Simplified Chinese**로 선택한다.
6. 복원할 때는 게임/런처를 종료하고 `RESTORE_ORIGINALS.bat`를 실행한다.

## 감사 종료 상태

- `MSG_PK/SC/msgui.bin`: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- `RES_SC/res_lang.bin`: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`
- 두 설치 파일 모두 stock, NOBU 게임 프로세스 0개

## 다음 마일스톤

v0.2와 P3/Font-v3는 동결한다. 별도 검증된 ID 401–1100 배치를 합친 P4는
buildable 971개, 예상 메시지 target
`5E4B26FC465F4F0F4C046462714E7B677D7B479FDA6023086EF7F9A8817E6984`,
요구 문자 387개(한글 음절 342개)다. P4 canonical/Font-v4를 별도 구축한 뒤 같은
설치·복원·공개 감사·실게임 회귀 QA를 반복한다.
