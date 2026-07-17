# 노부나가의 야망 신생 PK 한글 패치

Windows Steam판 `NOBU16PK.exe`의 일본어(JP) 리소스 경로를 사용하는 파일 전용 한글 패치입니다. 메모리 패치, DLL 주입, 후킹, EXE·레지스트리 변조는 사용하지 않습니다.

## 대상과 설치

- 대상: Steam PK v1.1.7 (`Update 1.1.7`, Steam build `18823764`)
- 게임 언어: Steam/런처에서 반드시 **Japanese**를 선택합니다.
- 게임과 Steam을 완전히 종료한 뒤 ZIP의 `MSG`, `MSG_PK`, `RES_JP`, `RES_JP_PK`, `RES_JP_PK_PORT` 폴더를 게임 폴더에 덮어씁니다.
- 일반적인 Steam 설치 경로: `...\SteamLibrary\steamapps\common\NOBU16`

현재 공개 안정판은 [v0.10.2](https://github.com/parsifal295/nobu16-korean-patch/releases/tag/v0.10.2)입니다. [v0.10.2 ZIP](https://github.com/parsifal295/nobu16-korean-patch/releases/download/v0.10.2/NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.10.2.zip)을 받아 설치하면 됩니다.

## 진행 현황

### v0.10.2 — 일반 해상도 시스템 버튼 경로 보정

- v0.10.1에서 누락된 일반 해상도 실제 로딩 경로 `RES_JP/res_lang_exp.bin`을 배포본에 추가했습니다.
- 검수 완료된 고해상도 버튼 아틀라스를 premultiplied-alpha Lanczos3 방식으로 정확히 1/2 축소해 같은 서체·배치·상태를 유지했습니다.
- `승인`, `거절`, `뒤로`, `수락`, `예`, `아니오` 등 20종×6상태와 `개전` 7상태를 검증했습니다.
- 해상도 변경 뒤 게임을 완전히 종료·재시작하고 1280×720, 1920×1080, 3840×2160에서 한글 버튼 적용을 확인했습니다.

큰 일본어 타이틀 로고와 튜토리얼 예시 화면 안의 일본어는 별도 이미지 경로이므로 이번 버전에 포함하지 않았습니다.
배포 ZIP SHA-256: `CDB16198D3E254CB1699810CD79D6F43A42178B1E78CB32449145D30155A8CFB` (374,094,877 bytes).

<!-- translation-progress:start -->
### v0.10.0 — 텍스트 번역 완료

`v0.10.0`은 Steam JP 1.1.7용 공개 배포본입니다. 게임 내 번역 대상 텍스트 번역을 완료했습니다.
현재는 순정 PC 일본어 원문과 PC EN/SC/TC 대조로 번역 품질을 전수 감사하고 있으며, 스위치판 한글은 기준으로 사용하지 않습니다.

공식 크레딧·일본어 IME 등 번역 대상이 아닌 구조용 슬롯은 유지하고, 고확신 오역만 별도 검증 후 수정합니다.
이벤트 스크립트 줄바꿈 전수 검수·보정은 완료했습니다. 이미지 번역은 진행 중입니다.
<!-- translation-progress:end -->

## 글꼴과 권리

한글 글리프는 서울한강체를 사용하며, 32–64px 계열은 서울한강 B, 48–96px 계열은 서울한강 EB로 렌더링합니다.

이 프로젝트는 비공식 팬메이드 한글 패치입니다. KOEI TECMO GAMES의 공식 제품이나 지원물이 아니며, 게임·상표·로고·원본 데이터에 관한 모든 권리는 KOEI TECMO GAMES 및 각 권리자에게 있습니다.
