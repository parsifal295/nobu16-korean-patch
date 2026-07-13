# 전체 MSGUI / Font-v4 v0.3 런타임 검증 시도

날짜: 2026-07-14 (KST)

> 상태: **최종 판정 보류.** 후속 독립 검수에서 창 모드 캡처의 하단 조작부가 이미지
> 경계에 잘린 점과 시나리오 날짜 `1543년9개월` 오역을 확인했다. 날짜 번역은
> 교정했으며, 사용자 결정에 따라 추가 화면 검수는 번역 확대 뒤로 미룬다. 아래 해시와
> 화면은 첫 런타임 시도의 역사적 기록이며 최종 배포 승인 증거로 사용하지 않는다.

## 첫 관찰 결과

간체중문(SC) 파일 경로의 전체 `msgui` 0–5099 레시피와 Font-v4 조합은 실제 게임에서 부팅, 한국어 표시, 정상 종료, 순정 복원을 통과했다. 관찰 화면의 한국어 글리프에는 두부나 공백이 없었다. 다만 하단 프레이밍 때문에 잘림 검사는 최종 통과로 판정하지 않는다. 성 이름 세로 표시는 사용자 결정에 따라 알려진 제한으로 수용한다.

이 판정은 현재 `msgui` UI 범위에 대한 기술적 배포 승격이다. 시나리오 설명, 무장 이름 등 별도 `msgdata`·고유명사 리소스의 번역 완성을 뜻하지 않는다.

## 검증 환경

- 설치본: Steam에서 받은 설치본이 아닌 비 Steam PC 설치본
- 게임 루트: `F:\Games\NOBU16`
- 실행 파일: `NOBU16PK.exe`
- 프로세스 작업 폴더: 게임 설치 루트
- 언어 리소스 경로: SC
- `ERROR:-9001`: 발생하지 않음
- 메모리 패치, DLL 주입, 후킹, EXE·레지스트리 변경: 사용하지 않음

작업 폴더를 게임 루트로 지정하지 않으면 순정·수정 리소스와 무관하게 `ERROR:-9001`이 재현된다는 별도 기록은 `error_9001_working_directory_2026-07-14.md`에 있다.

## 적용 대상

- 수정 `MSG_PK/SC/msgui.bin`: `50875851C3F87F7D83DC5C1AF41D93D4E14043FE841D28A429644F60CDD13BA5`
- 수정 `RES_SC/res_lang.bin`: `9E0FFEAFCF3C50060E1E223988FD01BA2470987FB97A3B6DA75E0B7E3591AE9A`
- 메시지 작업: 3,836개
- 폰트 래스터 코드포인트: 563개

## 화면 증거

Xbox Game Bar의 게임 캡처로 현재 DirectX 프레임을 1600×900 PNG로 저장했다. GDI 또는 클립보드의 과거 프레임은 증거로 사용하지 않았다.

| 화면 | SHA-256 |
|---|---|
| `screenshots/runtime_v03_main_menu_2026-07-14.png` | `9F19604355878F0062A891C97A99CAA0350365A5C4D76999FE6523A26A115586` |
| `screenshots/runtime_v03_settings_root_2026-07-14.png` | `ADDF5F843CFD41CAFAD94E4F4381DE7E67C4CEA49CEC819B2840690CDE926BA0` |
| `screenshots/runtime_v03_settings_detail_2026-07-14.png` | `D30E13965C5E48348AB81E92448A614ADDB285967D7BD7B709E2EEA6DDA3F401` |
| `screenshots/runtime_v03_scenario_select_2026-07-14.png` | `31124B92BC0F127F0030DE58E5C7DD71821AFC71DB790FCDFBC0B7AB97492E76` |
| `screenshots/runtime_v03_officer_detail_2026-07-14.png` | `4255212EE16CEB660621B3242AD4C57F4536BD2BAE6CBC7AFBFC83E695BEE24C` |
| `screenshots/runtime_v03_exit_prompt_2026-07-14.png` | `C03CACD595C683434EC0C4966A354CE945C1F5FCE00A29FBF77A1DE7368E9BC0` |

관찰한 대표 한국어에는 `새 게임`, `무장 편집`, `추가 콘텐츠`, `환경 설정`, `튜토리얼 표시`, `역사 이벤트`, `시작할 연대를 선택하십시오.`, `등록 무장`, `얼굴 선택`, `통솔`, `지략`, `무용`, `정무`, `게임을 종료하시겠습니까?`가 포함된다.

- 캡처한 화면에서 공백 한국어 레이블이나 두부 문자는 보이지 않았다.
- 대표 장문 자체는 읽을 수 있었지만 창 모드 캡처에서 하단 조작부가 이미지 경계에
  잘렸으므로 전체 화면 잘림 검사는 보류한다.
- 중문 타이틀·버튼 그림, 시나리오 설명, 무장 이름·일부 값은 현재 `msgui` 레시피가 소유하지 않는 별도 리소스이므로 남아 있다.
- 모든 3,836개 문자열과 실제 캠페인 전 화면을 눈으로 확인한 것은 아니다.
- `속목표 건의`처럼 자연스러움의 추가 교정이 필요한 번역은 후속 품질 작업 대상으로 남긴다.

## 종료와 복원

종료 확인창의 `게임을 종료하시겠습니까?`를 확인하고 정상 종료했으며, 종료 뒤 `NOBU16PK` 프로세스가 사라진 것을 확인했다. 이후 배포 설치기의 `Restore`를 실행해 다음 순정 해시로 복구했다.

- 순정 `MSG_PK/SC/msgui.bin`: `C2C69FDF09D9BE06E14F03C4F40562ADD0CA247EE0D50FC3E06EF501524B5E82`
- 순정 `RES_SC/res_lang.bin`: `916759185E9D64E487530DCA760CD36AE1FCFF021F39CEB1658837FE60AE0D99`

## 당시 산출물 — 배포 금지

- 폴더: `releases/msgui_full_file_only_v0.3_2026-07-14`
- manifest SHA-256: `EFF5A932B0A6E0458D953B5F0AE707D9ACAA1EFAD620391EB0ABFA5909507E25`
- ZIP SHA-256: `67F70FC8C298951F5588FDAA3CE2154975DFF3F3CB1D171958364DFE3AABAA01`
- SHA sidecar SHA-256: `E2F72593AE806E8553CAC6B27F2E1C0DD944A6AF23E98E82BA15BB14DCB5F8CE`
- 당시 manifest는 `version=0.3`, `release_eligible=true`, `runtime_validation=passed`였으나
  후속 독립 검수로 이 승격 근거를 철회했다.
- 독립 공개 감사: 통과, 패키지 파일 17개

이 당시 산출물은 공개 배포하지 않는다. 후속 개발 후보는 날짜 오역이 수정된 새 메시지
레시피로 다시 만들며, 최종 배포 승격은 번역 확대 뒤 별도 런타임 검수에서 수행한다.
