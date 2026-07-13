# Git 저장소 정리 실행 보고서 — 2026-07-14

## 결과

- Git 저장소 위치: `F:\Games\NOBU16\KR_PATCH_WORK`
- 삭제한 로컬 산출물: 19,095,343,230바이트(약 17.784 GiB)
- 정리 직후 작업 트리: 902,524,351바이트(약 0.841 GiB, Git 메타데이터 제외)
- 과거 프로세스 메모리 패처, 게임 자동 실행기, 직접 교체 시험 스크립트는 최초
  소스 커밋 전에 삭제했다.
- 완성 게임 리소스, 추출 원문, 백업, Ghidra DB, 실패한 폰트 후보는 Git에 넣지 않았다.

## 삭제 전 안전 확인

- 실행 중인 `NOBU16*` 프로세스: 없음
- `MSG_PK/SC/msgui.bin`:
  `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- `MSG_PK/SC/msgdata.bin`:
  `0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E`
- `RES_SC/res_lang.bin`:
  `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`
- `MSG_PK/EN/msgui.bin`:
  `FB9C4698989319AE9A9BF138F6DC963DC106124FC60D19308D0BF1AD35BE3965`
- `RES_EN/res_lang.bin`:
  `CA05180FD6EE9F2877649716B34B61F056B222BC893711E68B39C500E94E8F80`

## 용량 정리 내역

| 구분 | 삭제 바이트 | 판단 |
|---|---:|---|
| `tmp`의 실패·중복 프로브와 캡처 | 14,572,159,181 | 최신 wide-glyph 후보와 진행 중 번역만 보존 |
| 구형 `backups` | 1,065,819,863 | 설치본 stock 해시 및 무프로세스 확인 후 삭제 |
| Ghidra DB·캐시 5개 트리 | 1,555,885,347 | 스크립트와 분석 보고서는 별도 보존 |
| 중복 폰트·카탈로그 빌드 | 1,557,706,314 | Font-v4 최신 private 후보 한 벌만 로컬 보존 |
| 폐기·중복 release | 150,713,427 | P3/P4/v0.3 증거만 보존 |
| 구형 `patches` | 41,579,588 | 완성 리소스 중심의 폐기 트리 |
| 제3자 checkout·무허가 archive | 7,877,250 | URL·commit·license만 `docs/THIRD_PARTY.md`에 핀 |
| 추출 상용 원문·unpacked 자료 | 138,889,374 | 재생성 가능하며 공개 Git 금지 |
| 레거시 번역 템플릿 | 4,712,886 | 고유 이름 초안 63건 이관 후 삭제 |

## 보존한 로컬 전용 자료

- `tmp/single_glyph_castle_probe`: 실제 지도 판정을 기다리는 완성 후보. Git 제외.
- `workstreams/msgui_full/font_v4/build`: 최신 direct-Hangul 폰트 후보. Git 제외.
- `workstreams/msgui_full/catalog_v2`: 상용 다국어 원문이 든 개발 카탈로그. Git 제외.
- P3/P4/v0.3 frozen release 증거. `releases/` 전체는 Git 제외.

## 번역 자산 정리

개발 배치 `data/translations`는 검수용 영문 원문을 포함하므로 Git에서 제외했다.
대신 `tools/export_public_translation_overlay.py`가 이를 검증한 뒤 다음 항목만 공개한다.

- 안정적인 숫자 ID
- stock SC 문자열의 UTF-16LE SHA-256
- 프로젝트가 작성한 한국어 번역

레거시 템플릿 107개를 전수 비교한 결과, `msgui` 번역 49건은 현행 카탈로그에
모두 존재했다. 이름 초안 63건만 `data/public/legacy_names_needs_review.v0.1.json`으로
보존했고 자동 병합하지 않도록 `needs_review` 상태를 유지했다.

## 최초 커밋 전 제거한 금지 방식

- `OpenProcess`, `ReadProcessMemory`, `WriteProcessMemory`, `VirtualAllocEx` 기반 도구
- 런타임 코드포인트·글리프·분류기·캐시 후킹 프로브
- 게임 실행을 대신하던 PowerShell 런처
- 직접 apply/restore 시험 배치와 v1–v16 구형 패치 스크립트

감사기의 금지 문자열 패턴과 게임 실행 중 적용을 거부하는 테스트 fixture는 실제
런타임 패치 코드가 아니므로 소스에 남긴다.
