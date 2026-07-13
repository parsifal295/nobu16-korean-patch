# MSGUI 전체 한글화 작업선

공식 간체중문(SC) 가로쓰기 경로를 기준으로 `MSG_PK/SC/msgui.bin` 5,100개 ID를 번역한다. 이 작업선은 파일 전용이며 프로세스 메모리, DLL 주입, 후킹, EXE, 레지스트리를 사용하지 않는다.

## 현재 기준점

- 메타데이터: `catalog_v2/msgui.meta.json`
- 최초 추출본: `catalog_v2/msgui.catalog.jsonl`
- 현재 누적 카탈로그: `catalog_v2/msgui.catalog.p3.jsonl`
- 현재 메시지 빌드: `build_p3_core_terms/`
- 누적 번역: 279개 (`translated`; 화면 검수 전)
- 완전 공백: 1,038개
- 잔여 비공백 미번역: 3,783개
- 현재 요구 한글 음절: 226개

개발 카탈로그에는 네 언어의 전체 상용 원문이 포함되므로 공개 패치에 넣지 않는다. 공개 배포에는 `msgui_sc.recipe.json`처럼 원문을 해시로만 보관하는 레시피만 포함한다.

## 안전 장치

- 네 언어 원본 파일의 SHA-256과 압축 해제본 SHA-256 고정
- 모든 ID의 원문 UTF-16LE 해시 고정
- `%d`, `%s`, 폭 지정자 순서 보존
- ESC 색상 코드, PUA 아이콘 순서 보존
- 줄바꿈 수 보존(검수 완료 명시적 예외만 허용)
- 출력은 작업 디렉터리에만 생성하며 설치 파일을 직접 덮어쓰지 않음
- 공개 레시피는 고정된 대상 파일을 바이트 단위로 재현해야 함

## 재현 명령

번역 카탈로그 검증:

```powershell
& $Python KR_PATCH_WORK\tools\msgui_catalog_v2.py validate `
  --game-root . `
  --meta KR_PATCH_WORK\workstreams\msgui_full\catalog_v2\msgui.meta.json `
  --catalog KR_PATCH_WORK\workstreams\msgui_full\catalog_v2\msgui.catalog.p3.jsonl
```

별도 메시지 빌드:

```powershell
& $Python KR_PATCH_WORK\tools\msgui_catalog_v2.py build `
  --game-root . `
  --meta KR_PATCH_WORK\workstreams\msgui_full\catalog_v2\msgui.meta.json `
  --catalog KR_PATCH_WORK\workstreams\msgui_full\catalog_v2\msgui.catalog.p3.jsonl `
  --output-root KR_PATCH_WORK\workstreams\msgui_full\build_p3_core_terms
```

공개용 메시지 레시피 생성:

```powershell
& $Python KR_PATCH_WORK\tools\build_file_only_msg_recipe.py export-build `
  --game-root . `
  --build-manifest KR_PATCH_WORK\workstreams\msgui_full\build_p3_core_terms\msgui.build-manifest.json `
  --target KR_PATCH_WORK\workstreams\msgui_full\build_p3_core_terms\MSG_PK\SC\msgui.bin `
  --output KR_PATCH_WORK\workstreams\msgui_full\build_p3_core_terms\msgui_sc.recipe.json
```

## 다음 작업

1. 화면에 실제 표시되어 통과한 P3 ID만 근거 화면과 함께 `reviewed`로 승격한다.
2. ID 401–1100 검증 배치를 다음 canonical 마일스톤으로 병합한다.
3. 누적 387자(한글 음절 342자) 수요로 다음 폰트를 결정론적으로 재생성한다.
4. 다음 메시지·폰트 후보를 격리 설치/복원과 실제 화면 회귀 QA에 통과시킨다.

P3 이후 대기열:

- ID 401–500: 100개 번역
- ID 501–600: 99개 번역, 공백 ID 513 보류
- ID 601–700: 98개 번역, 공백 ID 689·691 보류
- ID 701–800: 95개 번역, 구조용 공백 ID 712–714·733·734 보류
- ID 801–900: 100개 번역
- ID 901–1000: 100개 번역
- ID 1001–1100: 100개 번역
- ID 401–1100 누적 임시 빌드: buildable 971개, 실제 변경 931개,
  target `5E4B26FC465F4F0F4C046462714E7B677D7B479FDA6023086EF7F9A8817E6984`,
  요구 문자 387개(한글 음절 342자)
- 위 배치는 모두 오류·경고 0으로 검증했지만 아직 P3 canonical/Font-v3/v0.2에는 병합하지 않았다.

P3 첫 런타임 시도는 일본어 경로로 실행되어 판정에서 제외했다. 이후 공식 런처에서
간체중문을 선택해 같은 후보를 다시 검증했고, 메인 메뉴·무장 편집·새 게임 공통 UI의
한글 직접 렌더링을 확인했다. 실제 표시된 14개 ID만 화면 근거가 있는 것으로 기록했다.

- 런타임 증거: `reports/msgui_p3_runtime_pass_2026-07-13.json`
- 화면 QA: 메시지/Font-v3 `runtime_verified=true`
- vNext 공개 후보: `releases/msgui_p3_file_only_v0.2_2026-07-13.zip`
- manifest SHA-256: `0ACD79C83464F6306C2910C253EE3E022965CCFF5DDE570DF31D64648003B7FC`
- ZIP SHA-256: `58A66AF9311D120EA77E0E1F31D6D29E0D0E1CF8E15A28A51223B065214805F8`
- 파일 전용 설치/복원·결정론 재빌드·공개 폴더/ZIP 감사·악성 변조 probe를 통과해
  manifest의 `release_eligible=true`가 활성화되었다.

## 협업 번역팩

`export-batch`는 선택한 ID 범위의 EN/JP/SC/TC 원문, 원문 해시, 토큰 정보를 한 파일로 내보낸다. 이 파일에는 상용 원문이 들어 있으므로 개발 협업용이며 공개 패치에 포함하면 안 된다.

```powershell
& $Python KR_PATCH_WORK\tools\msgui_catalog_v2.py export-batch `
  --meta KR_PATCH_WORK\workstreams\msgui_full\catalog_v2\msgui.meta.json `
  --catalog KR_PATCH_WORK\workstreams\msgui_full\catalog_v2\msgui.catalog.p3.jsonl `
  --id-range 401:500 `
  --batch-id next_0401_0500.template `
  --output KR_PATCH_WORK\workstreams\msgui_full\translator_packs\next_0401_0500.template.json
```

번역자는 각 항목의 `ko`만 채우고 필요한 문맥 메모를 추가한다. 병합기는 ID·EN 원문·SC UTF-16LE 해시와 모든 제어 토큰을 다시 검사한다.
