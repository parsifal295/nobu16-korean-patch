# KR_PATCH_WORK Git 저장소·정리 감사 — 2026-07-14

## 결론

`KR_PATCH_WORK`는 현재 3,667파일, 19,899,775,911바이트(18.533 GiB)다. 이 중
`tmp` 13.821 GiB, Ghidra DB/캐시 1.449 GiB, `backups` 0.993 GiB가 차지한다.
Git에 그대로 넣을 트리가 아니다.

이번 감사에서는 파일 삭제·이동, `.gitignore` 작성, `git init/add/commit`을 하지
않았다. 현재 기준으로 다음 네 상태를 구분한다.

- **TRACK**: 공개 저장소에서 보존해야 하는 프로젝트 소스·번역·레시피·문서·증거
- **LOCAL-LOCK**: Git에서는 제외하지만 현재 런타임 판정이 끝날 때까지 로컬 보존
- **DELETE-AFTER-COPY**: 작은 최종 증거만 TRACK 위치로 옮긴 뒤 삭제 가능한 생성물
- **MIGRATE-FIRST**: 고유 번역 또는 공개 가능한 메타를 먼저 이관해야 하는 구형 자료

P3/P4 및 v0.3-dev 동결물, 최신 Font-v4 직접 한글 후보, wide-glyph 후보는
보존 대상으로 잠근다. 특히 wide-glyph는 아직 실제 지도 판정 전이므로 완성 로컬
후보를 지금 삭제하면 안 된다.

## 용량 스냅샷

| 경로 | 파일 | 바이트 | GiB | 판정 |
|---|---:|---:|---:|---|
| `tmp` | 2,197 | 14,839,692,221 | 13.821 | 대부분 생성물, 일부 후보 LOCAL-LOCK |
| `workstreams` | 198 | 2,048,692,536 | 1.908 | 소스/공개 레시피와 private 빌드 분리 |
| Ghidra DB/캐시 | 223 | 1,555,885,347 이상 | 1.449 | DELETE-AFTER-COPY |
| `backups` | 101 | 1,065,819,863 | 0.993 | Git 제외, 설치본 stock 확인 후 삭제 가능 |
| `releases` | 122 | 154,208,315 | 0.144 | 동결 file-only만 TRACK |
| `data` | 159 | 143,992,000 | 0.134 | 번역만 TRACK, raw/extracted 제외 |
| `patches` | 100 | 41,579,588 | 0.039 | 구형 생성물, 삭제 가능 |
| `vendor/noto` | 4 | 34,218,746 | 0.032 | OFL+정확한 입력 폰트 보존 |

## 반드시 TRACK할 것

### 1. 정책·아키텍처·문서·테스트

- `README.md`는 UTF-8 표시를 고치고 현행 file-only 상태만 남긴다.
- `docs/ARCHITECTURE_FILE_ONLY.md`, `docs/DISTRIBUTION_POLICY.md` 및 나머지 문서
- `tests/`, `release_templates/`
- `ghidra_scripts/`의 분석 스크립트 28개. Ghidra 프로젝트 DB와 혼동하지 않는다.
- 모든 작성형 핵심 Markdown 보고서와 소형 감사 JSON
- `reports/screenshots/`의 선별된 실제 화면 증거

핵심 보고서에는 적어도 다음이 포함되어야 한다.

- `korean_localization_breakthrough_2026-07-13.md`
- `file_only_independent_safety_audit_2026-07-13.md`
- `p4_message_independent_audit_2026-07-13.md`
- `font_v4_independent_audit_2026-07-13.md`
- `v03_dev_offline_independent_audit_2026-07-14.md`
- P3 동결/런타임/배포 보고서
- `single_glyph_castle_probe_2026-07-14.md`
- `single_glyph_castle_wrapped_candidate_2026-07-14.md`
- `castle_name_layout_file_only_probe_2026-07-14.md`
- 0401–2100 번역 검증 보고서

`reports/*.txt`의 대형 Ghidra 후보 덤프(예: 1.62 MiB
`main_font_codepoint_candidates.txt`)는 생성 가능 원시 로그다. 결론 Markdown과 생성
스크립트가 있으면 Git에서 제외할 수 있다. 장기 증거로 필요하면 일반 소스와 섞지
말고 별도 압축 연구 아티팩트로 보관한다.

### 2. 번역 소스

`data/translations/`의 ID 단위 JSON 21개를 모두 TRACK한다. 감사 시점에
`msgui_core_ui_terms_2001_2100.v0.1.json`까지 존재한다. 이들이 프로젝트 소유의
정식 번역 원본이다.

반대로 `data/extracted/`, 전체 `msgui.catalog*.jsonl`,
`inventory/records.jsonl`은 순정 언어 원문이 포함된 생성물이다. 공개 Git에 넣지
않는다. 번역 JSON과 공개 file-only recipe로 재구성한다.

### 3. 현행 file-only 소스

다음 계열은 대표적인 필수 TRACK 대상이다.

- `tools/nobu16_lz4.py`, `tools/nobu16_msg_table.py`
- `tools/msgui_catalog_v2.py`, `tools/build_msgui_full_inventory.py`
- `tools/build_file_only_msg_recipe.py`, `tools/build_file_only_font_recipe.py`
- `tools/validate_g1n_surgical.py`
- `tools/FileRecipeCore.cs`, `tools/Invoke-FileOnlyPatch.ps1`
- `tools/audit_file_only_release.py`, `tools/assemble_final_file_only_release.py`
- 현행 번역 병합·검증·배포 조립 도구
- `workstreams/msgui_full/font_v3` 및 `font_v4`의 빌더·래스터라이저·결정성 검사 소스
- 각 canonical `build/public`, `manifest.json`, `validation.json`
- P1–P4의 `glyph_demand.json`, manifest, 공개 message recipe

완성 `msgui.bin`, G1N, LINK `res_lang.bin` 및 private recipe replay는 소스가 아니다.

### 4. 동결 배포 증거

다음 세 디렉터리는 작고 배포 경계가 감사된 동결 자료이므로 보존한다.

- `releases/msgui_p3_file_only_v0.2_2026-07-13` — 1.06 MiB
- `releases/msgui_p3_file_only_v0.2-dev_2026-07-13` — 1.05 MiB
- `releases/msgui_p4_file_only_v0.3-dev_2026-07-13` — 2.10 MiB

v0.3-dev는 공개 배포 가능 상태가 아니다. 감사 보고서가 고정한 핵심 핀은 P4 메시지
`5E4B26FC...E6984`, Font-v4 SC archive `3BC57379...6D1A9`, Font-v4 canonical tree
`1C52B0EA...EEE2F`이며 `release_eligible=false`를 유지한다.

ZIP/tar는 빌드 산출물로 Git에서 제외하고 배포 시스템의 release artifact로 만드는
편이 낫다. sidecar와 manifest는 TRACK할 수 있다.

### 5. 폰트 입력

Noto Sans/Serif KR TTF와 두 OFL은 최신 Font-v4를 결정적으로 재현하는 입력이다.
권장안은 TTF 두 개를 Git LFS로 추적하고 OFL·출처 URL·버전·SHA-256을 일반 Git에
추적하는 것이다. LFS를 사용하지 않으면 TTF를 무시하되 같은 해시의 파일만 받는
bootstrap 도구가 먼저 있어야 한다. 현재 입력을 아무 대안 없이 삭제하면 안 된다.

## 최신 후보 잠금

### Font-v4 직접 한글

`workstreams/msgui_full/font_v4/build`의 공개 6파일, manifest, validation 및 소스는
TRACK한다. `build/private`의 완성 후보 420.7 MiB는 최신 직접 한글 후보이므로
현재 LOCAL-LOCK한다.

`font_v4_independent_audit_2026-07-13.md`는 `build`와
`build_determinism_2`의 23/23 파일이 byte-exact임을 증명한다. 따라서
`build_determinism_2` 전체 422.6 MiB는 canonical `build`와 보고서를 남긴 뒤
삭제 가능하다.

Font-v3도 P3 공개 레시피·소스·감사 결과를 TRACK한다. 두 번째 결정성 트리
419.3 MiB는 생성 중복이다. 첫 private 후보까지 지우려면 P3 공개 recipe를 stock에
재생해 핀 해시와 일치하는 것을 한 번 확인한다.

### wide-glyph

`tmp/single_glyph_castle_probe` 전체는 256,642,203바이트(244.8 MiB)다. 실제 wrapper
후보와 재추출 G1N은 complete commercial resource이므로 Git 금지이며 지도 화면
판정이 끝날 때까지 LOCAL-LOCK한다.

처음에는 240,814바이트(235.2 KiB)를 공개 가능한 compact 세트로 보았으나 내용
검사 결과 그대로 추적할 수 없다.

- `proxy_reservation_9151_9542.json` 100,630바이트에는 SC 성명 392개의
  `source_sc` 원문이 들어 있다.
- `candidate_summary.json`과 `wrapper_candidate/WRAPPER_AUDIT.json`에는
  `小田原` 원문 1건씩이 들어 있다.

원본 그대로 즉시 TRACK 가능한 것은 아래 13파일, 127,213바이트다.

- `Audit-WrappedCandidate.py`
- `Build-SingleGlyphCastleProbe.ps1`
- `Invoke-WideCastleNameOnlyProbe.ps1`
- `preview_entry6_table0.png`, `preview_entry6_table1.png`
- `preview_entry7_table0.png`, `preview_entry7_table1.png`
- `raster_request.json`
- `raster/glyph_pixels_entry_6.bin`, `raster/glyph_pixels_entry_7.bin`
- `raster/raster_result.json`
- `wrapper_candidate/CANDIDATE_MANIFEST.json`
- `wrapper_candidate/HARNESS_STATIC_AUDIT.json`

이 텍스트 파일들에는 CJK 원문 적중이 0건이었다. 두 pixel payload는 고정 Noto KR로
`오다와라성`만 래스터한 11,520/5,120바이트의 프로젝트 생성 데이터이고,
`_N1G0000` 및 `LINK` signature로 시작하지 않는다. 완성 G1N/LINK가 아니다.

예약표는 `id`, `proxy`, `proxy_character`만 남긴 공개용 파생본을 만들고
`source_sc`를 제거해야 한다. summary/audit도 원문 필드를 제거한 공개판만 추적한다.
이후 세트를 `workstreams/castle_wide_glyph/` 같은 TRACK 경로로 옮긴다. 이 이관과
runtime 판정 전에는 `tmp/single_glyph_castle_probe`를 삭제하지 않는다.

## 삭제 가능 산출물

### A. 작은 증거를 먼저 복사한 뒤 고신뢰 삭제 — 약 11.426 GiB

| 그룹 | 크기 | 근거/선행 조건 |
|---|---:|---|
| `tmp/font_review_*` 19개 | 5.008 GiB | 선택 폰트·최종 비교 PNG와 보고서만 보존 |
| `tmp/runtime_latin_entry7_*_frames` 25개 | 0.406 GiB | 최종 2–3장만 `reports/screenshots`로 이동 |
| superseded runtime/font probes 11개 | 3.354 GiB | Font-v4/file-only 경로가 대체, runtime patch는 정책상 폐기 |
| Ghidra DB/캐시 + `__pycache__` | 1.449 GiB | 스크립트·최종 보고서로 재생성 가능 |
| 확장 release hostile fixtures | 0.517 GiB | 최종 audit JSON/Markdown만 보존 |
| 번역 검증 tmp 1401–2100 | 477,881,727 B | 번역 JSON·최종 validation/report 고정 후 삭제 |
| `patches`, retired mainmenu runtime release, v15/v16, audit rebuild | 약 0.18 GiB | 구형/금지 경로 또는 생성 중복 |
| `tmp/castle_layout_probe` | 약 74.6 MiB | 새 결론 보고서 보존; 재사용할 scanner 2개만 도구로 이관 가능 |

여기서 superseded 11개는 `font_alias_probe`, `font_normalized_probe`, `font_probe`,
`latin_glyph_probe`, `sc_hangul_n_alias_probe`, `hangul_phrase_probe`,
`jp_proxy_ga_probe`, `codepoint_bytepath_probe`, `codepoint_gate_probe`,
`zero_advance_probe`, `runtime_probe_backup`이다.

프레임 삭제 전 아래 세 파일을 선별 보존해야 한다.

- `tmp/font_review_ingame_compare.png` — SHA-256 `42FC3B97...6446`
- `tmp/runtime_latin_entry7_EN_PhraseUnified_frames/entry7_EN_PhraseUnified_final.png`
  — SHA-256 `61A3C1E2...733F`
- `tmp/runtime_latin_entry7_EN_FontNotoSansBoldGray94_frames/entry7_EN_FontNotoSansBoldGray94_final.png`
  — SHA-256 `A33BB40E...5B6`

### B. canonical 핀 확인 후 삭제 — 약 3.621 GiB

다음은 P3/P4의 중간 full-resource 빌드·회귀 그림자다. 동결 release/public recipe와
Font-v3/v4 canonical 빌드가 존재하고 해시가 보고서에 고정되어 있으므로, 해당 핀을
한 번 재검사한 뒤 삭제할 수 있다.

- `tmp/sc_noto_raster_v2`
- `tmp/sc_tc_pinned_noto_raw`
- `tmp/sc_noto_v1_regression`
- `tmp/sc_noto_metric_v2`
- `tmp/file_only_font_recipe`
- `tmp/final_file_only_release_build`
- `tmp/v1_regression_shadow_20260713`

최신 Font-v4 canonical `build/private`와 wide wrapper 후보는 이 그룹에 포함하지 않는다.

### C. 별도 조건부 정리

- `backups` 0.993 GiB: 감사 시점의 설치 SC `msgui`, SC `msgdata`, SC `res_lang`,
  EN `msgui`, EN `res_lang`은 모두 문서의 stock SHA-256과 일치했다. active journal이나
  lock이 없는 것을 확인하면 구형 backup은 삭제 가능하다. Git에는 절대 넣지 않는다.
- `data/raw` + `data/extracted` 0.129 GiB: 언팩 EXE 및 추출 상용 원문이다. 재현
  명령·해시·요약 보고서를 남기고 삭제 가능하다.
- `data/work_templates*`: 구형 CSV에 아직 이관되지 않은 한국어 행이 있을 수 있다.
  바로 삭제하지 말고 `data/translations`와 비교하여 고유 번역을 먼저 이관한다.
- `reference/G1N-Font-Editor`: upstream은
  `https://github.com/lehieugch68/G1N-Font-Editor.git`, 로컬 commit은
  `62d5468a5bc12f777e531be8bfd38f391009d0a1`이다. URL/commit/license만
  `THIRD_PARTY.md`에 핀하고 nested `.git`, `bin`, `obj`, clone은 삭제 가능하다.
- `reference/NOBU15_msg_editor_v0.13*`: 라이선스가 명확하지 않아 공개 Git 금지다.
  현행 file-only 파이프라인 의존성이 없음을 확인한 뒤 로컬 참조본도 삭제한다.

## releases 판정

| 경로 | 판정 | 이유 |
|---|---|---|
| `msgui_p3_file_only_v0.2*` | TRACK/동결 | public recipe·font payload·installer source·감사 증거 |
| `msgui_p4_file_only_v0.3-dev*` | TRACK/동결 | 최신 v0.3 개발 증거, release 불가 상태 포함 |
| `mainmenu_file_only_v0.1_2026-07-13` | 역사적 소형 seed | 보존 가능하나 현행 release와 혼동 금지 |
| `mainmenu_v0.1_2026-07-13` | 삭제/Git 금지 | 정책이 명시한 retired memory proof, complete `res_lang.bin`과 runtime patcher 포함 |
| `v15_*`, `v16_*` | 삭제/Git 금지 | 2026-03 구형 byte-overwrite 계열, 새 구조 파이프라인과 혼용 금지 |
| `_audit_rebuild_independent` | 삭제 | 독립 감사 재빌드 생성 중복 |
| `*.zip`, `*.tar.gz` | Git 제외 | 재현 빌드 후 release artifact로 발행 |

## 구형 tools 판정과 의존성 위험

다음은 공개 Git에서 제외하고 보고서만 남긴 뒤 삭제/별도 폐기 연구 보관할 수 있다.

- `runtime_*`, `nobu16_ko_runtime_patch.py`
- `direct_*_apply.ps1`, `direct_*_restore.ps1`
- `APPLY_*_TEST.bat`, `RESTORE_*_TEST.bat`
- `apply_master_v*.sh`, `restore_master_v*.sh`
- 구형 `master_v*` catalog/patch 생성 도구
- root의 retired `run_korean_phrase_demo.ps1`, `restore_korean_phrase_demo.ps1`

다만 먼저 `README_KO_BREAKTHROUGH.md`의 실행 경로와 tmp frame 링크를 역사 보고서
링크로 고쳐야 한다. 구형 도구를 먼저 지우면 문서가 깨진다. 파일 전용 포맷 분석에
현재도 쓰이는 공통 parser/codec까지 이름만 보고 함께 지우면 안 된다.

## 제안 `.gitignore`

다음은 초안이다. `*.bin` 전체 무시는 금지한다. 공개 glyph pixel payload도 `.bin`이기
때문이다. `releases/` 전체와 `workstreams/` 전체도 무시하면 동결 증거와 소스를 잃는다.

```gitignore
# Local work, backups, logs
/tmp/
/backups/
/logs/
**/__pycache__/
*.py[cod]

# Reverse-engineering databases and application caches
/ghidra_headless/
/ghidra_appdata/
/ghidra_localappdata/
/ghidra_user/
/ghidra_game/

# Proprietary inputs, extracted source-language text, obsolete full patches
/data/raw/
/data/extracted/
/data/work_templates/
/data/work_templates_clean/
/patches/
/reference/
/workstreams/msgui_full/inventory/records.jsonl
/workstreams/msgui_full/catalog_v2/msgui.catalog*.jsonl
/workstreams/msgui_full/catalog_v2/p4_merge_work/

# Private/full-resource build products and deterministic duplicates
**/private/
/workstreams/msgui_full/font_v3/build_determinism_2/
/workstreams/msgui_full/font_v4/build_determinism_2/
/workstreams/msgui_full/build_*/MSG_PK/
/workstreams/msgui_full/build_*/build_repeat/

# Retired or generated release products
/releases/mainmenu_v0.1_2026-07-13/
/releases/v15_ko_full_token_fill_2026-03-05/
/releases/v16_ko_stable_safe_2026-03-05/
/releases/_audit_rebuild_independent/
/releases/*.zip
/releases/*.tar.gz

# Complete resources and native build by-products
*.g1n
*.exe
*.dll
*.pdb
*.7z
**/RES_*/res_lang*.bin
**/MSG_*/**/msgui.bin
**/MSG_*/**/msgdata.bin
**/MSG_*/**/msggame.bin
```

`data/work_templates*`는 최초 Git add에서 차단하되, 삭제 전 고유 한국어 행을
이관한다. `reference/`도 먼저 차단하고 공개 가능한 upstream 핀·license만 새
`docs/THIRD_PARTY.md`에 작성한다.

권장 `.gitattributes`는 다음과 같다.

```gitattributes
vendor/noto/*.ttf filter=lfs diff=lfs merge=lfs -text
```

## 안전한 정리 순서

1. `.gitignore`를 먼저 적용하고 `git status --ignored`로 금지 파일이 staging되지
   않는지 확인한다.
2. wide-glyph의 13개 안전 파일과 원문 제거 파생 JSON을 tracked workstream으로
   이관한다. 원본 392-name 예약표와 full candidate는 LOCAL-LOCK한다.
3. raw frame에서 최종 증거 3장을 `reports/screenshots`로 이관하고 보고서 링크를
   바꾼다.
4. 2001–2100까지 번역 JSON과 검증 보고서를 고정한다.
5. P3/P4/v0.3, Font-v3/v4 공개 레시피의 문서화된 핀을 다시 검사한다.
6. A 그룹을 삭제하고 용량·경로 목록을 기록한다.
7. B 그룹과 determinism duplicate를 삭제한다. 최신 canonical private 후보는 유지한다.
8. 구형 work template의 고유 번역을 비교 이관한 뒤 raw/extracted/reference/old tools를
   정리한다.
9. 실제 지도 wide-glyph 판정과 복원 해시가 고정된 뒤에만 wide full candidate의
   삭제 여부를 다시 결정한다.

이 순서를 따르면 우선 약 11.426 GiB를 정리할 수 있고, canonical 핀 확인 후
추가 3.621 GiB를 줄일 수 있다. backups, proprietary input, determinism duplicate는
별도 조건을 충족하면 더 줄일 수 있다. 최신 direct-Hangul 한 벌과 wide 후보 한 벌은
현재 보존 계산에 포함한다.
