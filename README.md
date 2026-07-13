# NOBU16 Korean File-Only Patch

`NOBUNAGA'S AMBITION: Awakening with Power Up Kit`의 한글 패치를 만드는 작업 저장소다.
목표는 게임이 설치된 디스크의 공식 언어 리소스만 오프라인으로 변환하고, 검증 가능한
레시피와 복원 절차를 포함한 배포본을 만드는 것이다.

## 절대 조건

- 프로세스 메모리 읽기·쓰기, DLL 주입, 후킹, 프록시 DLL을 사용하지 않는다.
- 실행 파일을 수정하지 않는다.
- 패치가 레지스트리를 읽거나 쓰지 않으며 게임을 대신 실행하지 않는다.
- 공식 파일의 stock SHA-256을 확인한 뒤에만 적용한다.
- 백업, 잠금, 저널, 원자적 교체, 실패 시 롤백, 완전 복원을 제공한다.
- 상용 게임의 완전한 리소스 파일은 Git이나 공개 배포본에 넣지 않는다.

## 현재 돌파구와 알려진 제한

- 공식 간체중문(SC) 경로는 파일 전용 리소스 교체만으로 한글 글리프를 표시할 수 있다.
- 일반 UI는 가로쓰기이므로 메뉴·대화·정보 화면의 한글화 기반으로 사용할 수 있다.
- 전략지도 성 이름은 SC 실행 경로에서 문자 종류와 무관하게 세로 배치된다.
- 2026-07-14 실제 지도에서 ID 9168을 `오다성`으로 바꾼 시험도 세로 표시됨을 확인했다.
- 설정 파일로 영어 가로쓰기 분기를 활성화할 수 없고, 교체 가능한 외부 레이아웃도 찾지 못했다.
- 2026-07-14 사용자 결정에 따라 이 세로 표시는 공개 배포를 막는 결함이 아니라 알려진
  표시 제한으로 수용한다. 메뉴·대화·정보 화면의 번역 완성과 배포본 제작을 우선한다.
- `single-wide-glyph` 가로쓰기 실험은 보류하며 공개 패치의 필수 구성에 포함하지 않는다.

상세 근거는 다음 문서에 있다.

- `docs/ARCHITECTURE_FILE_ONLY.md`
- `docs/DISTRIBUTION_POLICY.md`
- `reports/castle_name_layout_file_only_probe_2026-07-14.md`
- `reports/single_glyph_castle_wrapped_candidate_2026-07-14.md`
- `reports/wide_castle_ab_runtime_2026-07-14.md`

## 저장소 구성

- `tools/`: 추출, 빌드, 검증, 안전 적용·복원 도구
- `data/public/`: 상용 원문 없이 배포 가능한 ID·원문 해시·한국어 오버레이
- `data/translations/`: 검수용 원문이 포함된 로컬 개발 배치(Git 제외)
- `workstreams/msgui_full/`: 전체 UI 카탈로그, 폰트, 배포 레시피의 소스
- `docs/`: 구조, 정책, 작업 절차
- `reports/`: 재현 가능한 분석·검증 결과
- `tests/`: 파일 형식과 안전장치 회귀 테스트
- `vendor/noto/`: OFL 라이선스의 고정 폰트 입력과 라이선스

`tmp`, `backups`, Ghidra 프로젝트 DB, 추출 원문, 완성 게임 리소스, 빌드 산출물은
로컬 작업용이며 Git 추적 대상이 아니다.

## 현재 번역 상태

`msgui` ID 1–3300 범위에서 3,092개 항목이 배치 번역과 형식 검증을 통과했다.
공개 오버레이를 stock 카탈로그에 병합한 빌드는 개발용 누적 빌드와 바이트 단위로
일치했다. 후속 배치는 같은 규칙으로 계속 확장하며, printf 토큰·개행·공백·PUA
코드를 원문과 동일하게 보존한다.

현재 공개 오버레이는 `data/public/msgui_ko_0001_3300.v0.1.json`이며 상용 영문·중문
원문을 포함하지 않는다.

## 기준 파일

- `MSG_PK/SC/msgui.bin` stock SHA-256:
  `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- `MSG_PK/SC/msgdata.bin` stock SHA-256:
  `0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E`
- `RES_SC/res_lang.bin` stock SHA-256:
  `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`

설치본에 직접 쓰기 전에 반드시 해당 도구의 `Status`와 독립 검증 보고서를 확인한다.
