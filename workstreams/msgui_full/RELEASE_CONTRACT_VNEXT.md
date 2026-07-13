# MSGUI 확장 마일스톤 배포 계약

이 문서는 메인 메뉴 9개 전용 v0.1 배포본을 임의 개수의 검증된 `msgui` 번역으로 확장할 때 지켜야 할 계약이다. 기존 v0.1 공개 ZIP은 변경하지 않는다.

## 허용 구성

- `components/message/msgui_sc.recipe.json`
  - stock/target 크기와 SHA-256
  - 문자열 ID
  - 원문 UTF-16LE SHA-256
  - 한국어 교체 문자열
- `components/font/recipe.json`
  - SC entry 6/7 append-tail 구조 레시피
  - 프로젝트가 Noto KR에서 생성한 글리프 픽셀 payload
- Noto Sans/Serif KR OFL 원문과 provenance
- PowerShell 설치/검증/복원 스크립트 및 C# 소스 코어
- `release_manifest.json`, `VALIDATION_EVIDENCE.json`, 사용자 문서

## 금지 구성

- 전체 stock 또는 전체 수정 `msgui.bin`, `res_lang.bin`
- 개발용 5,100행 다국어 카탈로그
- 원본 게임 EXE/DLL 또는 수정본
- Python 실행 파일/모듈, 네이티브 DLL/EXE
- 메모리 패치, 프로세스 핸들, 주입, 후킹, 프록시 DLL
- 게임 실행 기능
- 레지스트리 읽기/쓰기 및 언어 자동 변경

## manifest 고정값

`release_manifest.json`은 최소한 다음을 고정해야 한다.

- 패키지 스키마/버전/아키텍처 `file-only-offline`
- 대상 경로 정확히 `MSG_PK/SC/msgui.bin`, `RES_SC/res_lang.bin`
- 메시지·폰트 레시피 및 모든 payload의 크기/SHA-256
- 설치기/코어/배치 wrapper의 크기/SHA-256
- 메시지 operation 개수와 정렬된 ID 목록의 SHA-256
- 메시지 stock/target SHA-256
- 폰트 stock/target SHA-256
- `process_memory_access=false`
- `executable_modified=false`
- `registry_modified=false`
- `launches_game=false`
- `resident_component=false`
- `commercial_full_files_included=false`
- `requires_process_running=false`
- `payload_format=recipes-and-deltas-only`

JSON 구성은 필드 허용 목록이 고정된 strict schema여야 한다. 알 수 없는 필드,
중복 키, 허용되지 않은 base64/hex 바이트 필드, 추가 중첩 객체는 거부한다. 알려진
완성 리소스 해시만 막는 방식은 이름 변경이나 JSON 내부 인코딩을 막지 못하므로
충분하지 않다.

모든 JSON은 `ConvertFrom-Json`보다 먼저 raw UTF-8 파서로 전체 문법과 객체 키를
재귀 검사한다. JSON escape를 해제한 뒤 동일한 키뿐 아니라 Windows PowerShell의
대소문자 비구분 속성 접근과 충돌하는 `OrdinalIgnoreCase` 키도 거부한다.

## 독립 감사기의 신뢰 경계

- 독립 감사기는 패키지에 든 PowerShell/C# 또는 배치 파일을 검증 전에 실행하지 않는다.
- 감사기가 처음 컴파일하는 JSON guard는 감사기 자체에 고정된 크기/SHA-256과 정확히
  일치해야 한다.
- 패키지 inventory, raw JSON, manifest 파일 해시, file-only 플래그를 독립 코드로 먼저
  검사한다.
- 설치기, C# recipe core, JSON guard, 배치 wrapper는 감사기 밖의 신뢰된 template과
  고정 크기/SHA-256이 모두 일치해야만 packaged `Verify`를 실행할 수 있다.
- 변조 설치기에 무해한 marker 생성을 삽입하고 manifest도 함께 다시 계산한 공격
  fixture에서 감사가 실행 전 거부되고 marker가 생기지 않아야 한다.
- 패키지 내부 검증은 패키지 전체의 악성 교체를 스스로 인증할 수 없다. 최종 ZIP
  SHA-256과 `.zip.sha256` sidecar를 패키지와 분리된 신뢰 경로에 게시하고, 사용자는
  압축 해제 전에 이를 대조한다.

## 설치기 검증 순서

1. 패키지 루트가 링크/정션이 아닌 일반 디렉터리인지 확인한다.
2. manifest의 허용 목록 외 파일이 없는지 확인한다.
   - `manifest.files`와 실제 일반 파일 집합이 경로·개수까지 정확히 같아야 한다.
   - 허용 경로/확장자 이외의 파일과 ZIP/7z/RAR 등 중첩 archive를 거부한다.
3. 모든 구성 파일을 읽기 전에 크기와 SHA-256을 검사한다.
4. 레시피 스키마, file-only 플래그, 대상 경로, stock/target 해시를 검사한다.
5. 메시지 operation ID가 중복 없이 오름차순이며 manifest의 ID 목록 해시와 일치하는지 검사한다.
   - 레시피와 manifest의 operation 개수, ID 목록, source/target 크기·해시를 서로
     교차 검증한다.
6. 게임 프로세스가 실행 중이면 거부한다.
7. 설치 루트의 stock 또는 이미 설치된 target 상태만 허용한다. 그 외 혼합/미지원 상태는 안전 복구 경로 외에는 거부한다.
8. 원본을 패키지 밖 게임 하위 백업 디렉터리에 해시와 함께 보존한다.
9. journal을 먼저 기록하고 두 대상 파일을 임시 파일에서 검증한 후 원자적으로 교체한다.
10. 중단 시 journal을 이용해 stock 또는 완전한 target 한 상태로만 복구한다.

## 복원 계약

- 설치 당시 백업의 크기/SHA-256이 manifest의 stock과 같아야 한다.
- 복원 전 현재 파일이 target 또는 복구 가능한 혼합 상태인지 확인한다.
- 두 파일 모두 원자적으로 stock으로 되돌린 뒤 해시를 재검사한다.
- 게임 설정과 레지스트리는 건드리지 않는다. 사용자가 공식 런처에서 간체중문을 선택한다.

## 배포 게이트

다음 증거가 모두 참일 때만 `release_eligible=true`로 조립한다.

- 메시지 catalog/recipe 단위 검증
- 폰트 append-tail 독립 검증
- 메시지·폰트 recipe의 pinned target 바이트 재현
- 격리 테스트 설치/복원
- bad-stock 거부
- 혼합 상태 journal 복구
- 실행 중 프로세스 거부
- 실제 게임 화면에서 대표 UI의 한글 표시, 누락 글리프, 잘림 확인
- 공개 폴더 strict audit 오류 0건
- manifest/evidence/message recipe/font recipe 각각의 직접·중첩·escape 동치·대소문자
  충돌 중복 키 공격 거부
- 설치기/Core/JSON guard/wrapper 변조를 packaged code 실행 전에 거부

화면 검수 전 산출물은 `development_milestone=true`, `release_eligible=false`로만 취급한다.

## ZIP 배포 추가 게이트

- ZIP entry 이름은 정규화된 상대 경로여야 하며 절대 경로, `..`, 빈 구성요소,
  역슬래시 우회, 드라이브 접두사, 중복/대소문자 충돌 entry를 거부한다.
- ZIP 해제 후 폴더를 다시 감사하고 manifest와 실제 트리의 완전 일치를 확인한다.
- 공개 폴더와 ZIP 재해제본의 각 파일 크기/SHA-256 집합이 동일해야 한다.
- 같은 입력과 같은 ZIP 최상위 폴더명으로 두 번 조립한 ZIP 및 manifest가 바이트 단위로
  동일해야 한다.
- 전체 stock/target `msgui.bin`, `res_lang.bin`, G1N, LINK/LZ4 wrapper 및 이를
  포함한 중첩 archive나 JSON 인코딩 필드가 없는지 별도 누출 probe로 확인한다.
