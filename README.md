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
### v0.10.0 공개 현황

`v0.10.0`은 Steam JP 1.1.7용 공개 배포본이며, JP 경로 14개 파일을 설치합니다.

| 항목 | 현황 |
|---|---|
| 활성 텍스트 10개 테이블 | 고신뢰 좌표 2,489 / 2,498 한글 반영 |
| 의도적 원문 유지 | 9건 (공식 크레딧 6 · 런타임 구조 3) |
| 추가 수동 검토 | 394건 (혼합 한글/가나 207 · 한자 중심 187) |
| 표시·글꼴 | 이벤트 줄바꿈 정리 · 기존 글꼴 폭 유지 |

수치는 자동 판정 가능한 활성 텍스트 기준이며, 게임 전체의 번역 완료율은 아닙니다.
참고: 마지막 이벤트 줄바꿈 조정 뒤 해당 이벤트 장면은 다시 확인하지 않았습니다.
<!-- translation-progress:end -->

## 글꼴과 권리

한글 글리프는 서울한강체를 사용하며, 32–64px 계열은 서울한강 B, 48–96px 계열은 서울한강 EB로 렌더링합니다.

이 프로젝트는 비공식 팬메이드 한글 패치입니다. KOEI TECMO GAMES의 공식 제품이나 지원물이 아니며, 게임·상표·로고·원본 데이터에 관한 모든 권리는 KOEI TECMO GAMES 및 각 권리자에게 있습니다.
