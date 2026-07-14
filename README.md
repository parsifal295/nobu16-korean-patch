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

## 검증 환경과 실행 조건

- 현재 개발·검증 대상은 Steam에서 받은 설치본이 아닌 **비 Steam PC 설치본**이다.
- Steam 설치 경로, Steam 실행 옵션, Steam 런처 동작을 프로젝트의 전제로 삼지 않는다.
- `NOBU16PK.exe`를 실행할 때 프로세스 작업 폴더(바로가기의 `시작 위치`)는 반드시
  게임 설치 루트여야 한다. 이 저장소의 현재 검증 환경에서는 작업 폴더가 다르면
  순정·수정 리소스와 무관하게 `ERROR:-9001`이 재현됐다.
- 따라서 `ERROR:-9001`이 발생하면 패치 파일 손상으로 단정하기 전에 작업 폴더부터
  확인한다. 상세 재현 기록은 `reports/error_9001_working_directory_2026-07-14.md`에 있다.

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

`msgui` 실제 ID 0–5099 전체 5,100행의 의미 분류를 마쳤다. 현재 v0.2 후보는
4,037개를 한국어 번역 또는 검수 상태로 만들고, 1,041개를 canonical empty로 분류한다.
나머지 22개는 일본어 이름 읽기·IME 전용 슬롯이라 공식 SC 공백과 화면 구조를 의도적으로
보존한다. 따라서 일반 SC 비공백 UI의 미번역은 0개다.

- 현재 장수명 RC가 사용하는 안정 overlay:
  `data/public/msgui_ko_0000_5099.v0.1.json`(3,951개)
- 비대칭 공백 86개를 추가한 화면 검수 전 후보:
  `data/public/msgui_ko_0000_5099.v0.2.json`(4,037개)
- v0.2 메시지 recipe: 3,922 operation, target
  `C683AE9355A43F9A2104E49A6179363727CE0A550682F906C224A44F506826AC`

v0.2의 새 86개는 원래 SC가 공백이던 내부 슬롯이므로 실제 화면·전투 효과 QA 전에는
배포 승격하지 않는다. 두 overlay 모두 상용 영문·중문 원문이나 완성 게임 리소스를 담지
않는다. 상세 분류와 결정성 검증은 `workstreams/msgui_full/asymmetric_v02/`에 있다.

장수명은 전체 source-free 카탈로그와 Font-v5를 포함한 4리소스 RC까지 승격됐다.
`MSG_PK/SC/msgui.bin`, `msgdata.bin`, `msgev.bin`, `RES_SC/res_lang.bin`을 하나의
거래로 적용·복원하며, 실제 게임에서 `오다 노부나가`의 성·이름·합성명과 한글 글리프를
확인했다. ZIP SHA-256은
`F41147A2010C563E1E47987D00FABF174B8CBA4F1BC66A9BDE31857F98682824`다.

병렬 후속 초벌로 성 이름 392개와 역사 이벤트 대사 28개도 source-free 산출물로 만들었다.
이 둘은 사람 검수와 Font-vNext·4리소스 통합이 끝나기 전까지 설치본에 적용하지 않는다.

## 기준 파일

- `MSG_PK/SC/msgui.bin` stock SHA-256:
  `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- `MSG_PK/SC/msgdata.bin` stock SHA-256:
  `0586C269D381AA1FD75C39802AC01C697B5E8469A9C1ABE693BA5EDB2E658B3E`
- `MSG_PK/SC/msgev.bin` stock SHA-256:
  `7221A53E6E5CF493A3FAFFFCE35280E8147898120EEC59E460A2429AA265C1F9`
- `RES_SC/res_lang.bin` stock SHA-256:
  `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`

설치본에 직접 쓰기 전에 반드시 해당 도구의 `Status`와 독립 검증 보고서를 확인한다.
