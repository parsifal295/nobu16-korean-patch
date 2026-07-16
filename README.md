# 노부나가의 야망 신생 PK 한글 패치

Windows Steam판 `NOBU16PK.exe`의 일본어(JP) 리소스 경로를 사용하는 파일 전용 한글 패치입니다. 메모리 패치, DLL 주입, 후킹, EXE·레지스트리 변조는 사용하지 않습니다.

## 대상과 설치

- 대상: Steam PK v1.1.7 (`Update 1.1.7`, Steam build `18823764`)
- 게임 언어: Steam/런처에서 반드시 **Japanese**를 선택합니다.
- 게임과 Steam을 완전히 종료한 뒤 ZIP의 `MSG`, `MSG_PK`, `RES_JP`, `RES_JP_PK`, `RES_JP_PK_PORT` 폴더를 게임 폴더에 덮어씁니다.
- 일반적인 Steam 설치 경로: `...\SteamLibrary\steamapps\common\NOBU16`

현재 공개 안정판은 [v0.10.0](https://github.com/parsifal295/nobu16-korean-patch/releases/tag/v0.10.0)입니다. [v0.10.0 ZIP](https://github.com/parsifal295/nobu16-korean-patch/releases/download/v0.10.0/NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.10.0.zip)을 받아 설치하면 됩니다.

## 진행 현황

<!-- translation-progress:start -->
### v0.10.0 — 텍스트 번역 완료

`v0.10.0`은 Steam JP 1.1.7용 공개 배포본입니다. 게임 내 번역 대상 텍스트 번역을 완료했습니다.

공식 크레딧과 런타임 구조용 9건은 번역 대상이 아니므로 원문을 유지합니다. 남은 것은 번역 작업이 아니라 일부 표현·화면의 선택 검수입니다.
<!-- translation-progress:end -->

## 글꼴과 권리

한글 글리프는 서울한강체를 사용하며, 32–64px 계열은 서울한강 B, 48–96px 계열은 서울한강 EB로 렌더링합니다.

이 프로젝트는 비공식 팬메이드 한글 패치입니다. KOEI TECMO GAMES의 공식 제품이나 지원물이 아니며, 게임·상표·로고·원본 데이터에 관한 모든 권리는 KOEI TECMO GAMES 및 각 권리자에게 있습니다.
