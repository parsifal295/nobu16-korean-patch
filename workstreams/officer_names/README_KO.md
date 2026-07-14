# 장수명 한글화 작업 흐름

장수명은 한 파일에만 있지 않다.

- `MSG_PK/SC/msgdata.bin`: 성과 이름을 분리해서 사용하는 편집·선택 UI의 사전
- `MSG_PK/SC/msgev.bin`: 일반 목록과 이벤트에서 사용하는 합성명 슬롯

따라서 한 장수의 표시를 완성하려면 두 리소스를 함께 다뤄야 한다. `msgdata`에는 같은
표기가 여러 블록에 중복될 수 있으므로, 다국어 정렬 결과가 같은 이름임을 확인한 슬롯만
명시적으로 추가한다. 영문 표기가 같은 `Oda`라도 `小田`과 `織田`처럼 서로 다른 성은
절대 일괄 치환하지 않는다.

## 공개 데이터 규칙

`data/public/*_ko_officer_names_*.json`은 다음 정보만 포함한다.

- 숫자 문자열 ID
- 공식 SC 원문의 UTF-16LE SHA-256
- 프로젝트가 작성한 한국어 번역

공식 원문 문자열과 완성된 게임 리소스는 Git 및 공개 패키지에 넣지 않는다. 개발 중
사용하는 다국어 원문 카탈로그와 완성 대상 파일은 각각 `data/translations/`, `tmp/`에만
둔다.

## Probe v0.1

첫 검증 묶음은 다음 세 명이다.

| 한국어 합성명 | 용도 |
|---|---|
| 아츠지 사다유키 | 실존 무장 편집 화면 첫 행에서 즉시 확인 |
| 이시다 미츠나리 | 긴 이름 조합 및 사용자 지정 표기 확인 |
| 오다 노부나가 | 대표 장수와 동음이성 `小田` 비치환 확인 |

한국어 표기는 사용자 예시인 `미츠나리`에 맞춰 일본어 `つ`를 `츠`로 적는다. 합성명에는
성·이름 사이 ASCII 공백 하나를 둔다. `msgdata`의 성 번역에는 후행 ASCII 공백 하나를
넣어 게임이 성과 이름을 직접 이어 붙이는 화면에서도 같은 결과가 되게 했다. 실제 편집
화면에서 분리 칸은 `아츠지` / `사다유키`, 우측 합성 표시는 `아츠지 사다유키`로 정상
표시됐다. 전체 명단 적용 전에는 다른 화면에서 후행 공백의 부작용이 없는지 추가 검수한다.

## 재현 빌드

stock 파일이 있는 게임 루트와 별도 출력 폴더를 지정한다. 빌더는 설치된 파일을 덮어쓰는
출력 경로를 거부한다.

```powershell
python tools/build_common_message_overlay.py build `
  --game-root <GAME_ROOT> `
  --overlay data/public/msgdata_ko_officer_names_probe.v0.1.json `
  --output-root <OUTPUT_ROOT>/msgdata

python tools/build_common_message_overlay.py build `
  --game-root <GAME_ROOT> `
  --overlay data/public/msgev_ko_officer_names_probe.v0.1.json `
  --output-root <OUTPUT_ROOT>/msgev
```

생성된 `*_sc.recipe.json`은 기존 `build_file_only_msg_recipe.py apply`와 호환된다. 최종
사용자용 배포본에서는 Python을 요구하지 않도록 현재 C#/PowerShell 파일 전용 설치기를
다중 메시지 리소스 거래로 확장한다.

`probe_v0.1/public/`에는 완성 게임 리소스가 아니라 결정적으로 재생성된 manifest와
공개 레시피만 고정한다.

## 전체 장수명 초안 v0.1

실제 장수 슬롯은 `msgev` ID `0..2206`의 연속 2,207개다. ID `2207..2399`는 언어별
dummy이며, 그 뒤의 부족 두목·이벤트 화자·일반 NPC는 장수명 패치에서 제외한다.

`tools/generate_officer_name_catalog.py`는 정렬된 비공개 SC/JP/EN JSONL과 비공개
후리가나 QA 자료를 읽어 한국어 초안을 만든다. 후리가나와 게임 EN 독음이 일치하는
경우만 교차 확정하고, 불일치하면 공식 EN 독음을 우선한다. `tools/export_common_message_overlay.py`
는 비공개 원문을 stock 파일과 다시 대조한 뒤 ID·원문 해시·한국어만 포함한 공개
오버레이를 내보낸다.

관용 표기 교정 12건은 명시적 manual override로 관리한다. 각 항목은 ID와 한국어 이름뿐
아니라 해당 ID의 SC·JP·EN 원문을 함께 고정하므로, 게임 데이터 판본이나 정렬이 달라지면
잘못 적용하지 않고 catalog 생성을 중단한다. ID 1674는 확정 단일명 `히코츠루`, ID 231은
조사까지 포함한 `이즈모노 오쿠니`로 고정했다.

공개 산출물은 다음과 같다.

- `data/public/msgev_ko_officer_names_0000_2399.v0.1.json`
- `data/public/msgdata_ko_officer_names_0000_2399.v0.1.json`
- `full_v0.1/public/msgev.build-manifest.json`
- `full_v0.1/public/msgev_sc.recipe.json`
- `full_v0.1/public/msgdata.build-manifest.json`
- `full_v0.1/public/msgdata_sc.recipe.json`

`tools/generate_officer_name_components.py`는 full `msgev` 이름을 SC/JP/EN 세 언어가 모두
일치하는 성·이름 조각으로만 분해한다. 동일한 영문 독음만으로 다른 한자 성을 한꺼번에
치환하지 않으며, 복수 후보와 번역 충돌은 적용하지 않는다. 이 기준으로 2,207명 중
2,151명의 `msgdata` 분리 슬롯을 확정했고, 성 1,050개와 이름 2,781개를 합쳐 총 3,831개
슬롯을 공개 오버레이에 수록했다. 성에는 합성 표시용 후행 ASCII 공백과
`allow_edge_whitespace_change=true`를 넣고, 이름에는 공백을 넣지 않았다.

나머지 56명은 단일명·칭호처럼 두 조각으로 나뉘지 않거나(40명), 세 언어 exact pair가
없거나(9명), 후보 간 표기가 충돌하거나(6명), 성·이름 ID가 겹쳐서(1명) `msgdata`
동기화에서만 보수적으로 제외했다. 이 56명도 full
`msgev` 오버레이에는 이미 모두 번역되어 있으므로 전체 이름 번역에서 누락된 것은 아니다.

`full_v0.1/public/`에는 완성 게임 리소스를 두지 않는다. 두 리소스의 source-free
manifest와 recipe만 두며, 공개 `msgev`·`msgdata` recipe가 격리된 stock에서 각 tmp 빌드
target을 바이트 단위로 재생하는지 검증했다. 상세 수치와 해시는
`reports/officer_name_components_2026-07-14.md`에 기록한다. 이 산출 시점에는 전체 음역을
런타임 검수 전 초안으로 분류했으며, 이후 Font-v5와 네 파일 설치·복원 거래를 통합해 아래
RC 검수를 진행했다.

## 장수명 RC v0.1

Font-v5는 장수명에 필요한 한글 125자를 포함하고 네 글꼴 테이블의 누락이 0자인 상태로
고정했다. 최종 배포 설치기는 아래 네 파일만 한 거래로 적용·원복한다.

1. `MSG_PK/SC/msgui.bin`
2. `MSG_PK/SC/msgdata.bin`
3. `MSG_PK/SC/msgev.bin`
4. `RES_SC/res_lang.bin`

실제 비 Steam 설치본을 게임 루트 작업 폴더에서 실행해 장수 편집 화면과 `오다 노부나가`의
성·이름 분리 칸, 우측 전체 이름 렌더링을 확인했다. 승인 실행에서는 `ERROR:-9001`이 없었고,
종료 뒤 네 설치 파일도 최종 target SHA-256과 일치했다. 직접 실행할 때는 게임 루트를 작업
폴더로 지정해야 한다.

배포 폴더는 `releases/officer_names_file_only_v0.1-rc`, ZIP은 같은 이름의 `.zip`이다.
ZIP SHA-256은 `F41147A2010C563E1E47987D00FABF174B8CBA4F1BC66A9BDE31857F98682824`이며,
새 디렉터리에 압축을 풀어 자체 검증기를 다시 실행했다. recipe E2E, runtime QA, RC 격리
적용·원복 결과는 `release_v0.1/QA_REPORT_KO.md`에 기록한다. 이 RC는 2,207개 장수명 초안의
배포·폰트·설치 경로를 검증한 것이며, 역사 인명 표기의 사람 전수 교정은 계속 진행한다.
