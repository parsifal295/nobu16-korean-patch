# 노부나가의 야망 신생 PK 한글 패치

Windows Steam판 `NOBU16PK.exe`의 일본어(JP) 리소스 경로를 사용하는 파일 전용 한글 패치입니다. 메모리 패치, DLL 주입, 후킹, EXE·레지스트리 변조는 사용하지 않습니다.

## 대상과 설치

- 대상: Steam PK v1.1.7 (`Update 1.1.7`, Steam build `18823764`)
- 게임 언어: Steam/런처에서 반드시 **Japanese**를 선택합니다.
- 게임과 Steam을 완전히 종료한 뒤 ZIP의 `MSG`, `MSG_PK`, `RES_JP`, `RES_JP_PK`, `RES_JP_PK_PORT` 폴더를 게임 폴더에 덮어씁니다.
- 일반적인 Steam 설치 경로: `...\SteamLibrary\steamapps\common\NOBU16`

현재 공개 안정판은 [v0.8.0](https://github.com/parsifal295/nobu16-korean-patch/releases/tag/v0.8.0)입니다. [v0.8.0 ZIP](https://github.com/parsifal295/nobu16-korean-patch/releases/download/v0.8.0/NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.8.0.zip)을 받아 설치하면 됩니다.

## 진행 현황

<!-- translation-progress:start -->
| 영역 | 안전 이식/검증 현황 | 별도 검토 |
|---|---:|---:|
| PK UI `msgui.bin` | 4,036 / 4,037 (99.98%) | 1 |
| PK 공용 메시지 5종 | 한국어 변경 40,581 · 구조 확인 1,796 / 원천 합집합 43,169 | 792 |
| PK 본문 `MSG_PK/JP/msggame.bin` | 28,272 / 28,272 (100.0%) | 0 |
| 기본 지도·튜토리얼 `MSG/JP/msggame.bin` | 22,924 / 23,256 | 332 |
| 기본 이벤트 `MSG/JP/ev_strdata.bin` | 13,045 / 13,090 | 45 |
| 공용 `MSG/JP/strdata.bin` | 24,524 / 24,525 | 1 |
| 일본어 경로 한글 폰트 | 4 / 4 | 0 |

v0.8.0 정식 배포본은 기존 PK 12파일에 기본판 대사 파일 2개를 더한 정확히 14파일입니다. 지도 조언·튜토리얼 대사가 빠졌던 원인은 기본판 `MSG/JP/msggame.bin`이 이전 후보에 없었던 것입니다.
후보 ZIP SHA-256: `8167B09DE5DC56C1F195AF0A913336F552D189B0DB320C2A4F5EC863BBC58D08`. Steam 실적용과 14개 복원 백업, 실제 한글 화면 검증을 모두 완료했습니다.
표의 수치는 원문 해시·줄바꿈·제어문자 계약을 통과한 안전 이식 수입니다. 전체 번역 완료율을 뜻하지 않습니다.
<!-- translation-progress:end -->

## 글꼴과 권리

한글 글리프는 서울한강체를 사용하며, 32–64px 계열은 서울한강 B, 48–96px 계열은 서울한강 EB로 렌더링합니다.

이 프로젝트는 비공식 팬메이드 한글 패치입니다. KOEI TECMO GAMES의 공식 제품이나 지원물이 아니며, 게임·상표·로고·원본 데이터에 관한 모든 권리는 KOEI TECMO GAMES 및 각 권리자에게 있습니다.
