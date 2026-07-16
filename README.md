# 노부나가의 야망 신생 PK 한글 패치

Windows Steam판 `NOBU16PK.exe`의 일본어(JP) 리소스 경로를 사용하는 파일 전용 한글 패치입니다. 메모리 패치, DLL 주입, 후킹, EXE·레지스트리 변조는 사용하지 않습니다.

## 대상과 설치

- 대상: Steam PK v1.1.7 (`Update 1.1.7`, Steam build `18823764`)
- 게임 언어: Steam/런처에서 반드시 **Japanese**를 선택합니다.
- 게임과 Steam을 완전히 종료한 뒤 ZIP의 `MSG`, `MSG_PK`, `RES_JP`, `RES_JP_PK`, `RES_JP_PK_PORT` 폴더를 게임 폴더에 덮어씁니다.
- 일반적인 Steam 설치 경로: `...\SteamLibrary\steamapps\common\NOBU16`

현재 공개 안정판은 [v0.9.0](https://github.com/parsifal295/nobu16-korean-patch/releases/tag/v0.9.0)입니다. [v0.9.0 ZIP](https://github.com/parsifal295/nobu16-korean-patch/releases/download/v0.9.0/NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.9.0.zip)을 받아 설치하면 됩니다.

## 진행 현황

<!-- translation-progress:start -->
| 영역 | 안전 이식/검증 현황 | 별도 검토 |
|---|---:|---:|
| PK UI `msgui.bin` | 4,036 / 4,037 (99.98%) | 1 |
| PK 공용 메시지 5종 | 한국어 변경 40,581 · 구조 확인 1,796 / 원천 합집합 43,169 | 792 |
| PK 본문 `MSG_PK/JP/msggame.bin` | 28,272 / 28,272 (100.0%) | 0 |
| 기본 지도·튜토리얼 `MSG/JP/msggame.bin` | 23,194 / 23,256 | 62 |
| 기본 이벤트 `MSG/JP/ev_strdata.bin` | 13,085 / 13,090 | 5 |
| 공용 `MSG/JP/strdata.bin` | 24,524 / 24,525 | 1 |
| 일본어 경로 한글 폰트 | 4 / 4 | 0 |

v0.9.0 정식 배포본은 기존 PK 12파일에 기본판 대사 파일 2개를 더한 정확히 14파일입니다. 이번 버전은 지도·튜토리얼 잔여 대사 270건과 기본 이벤트 잔여 대사 40건을 추가로 반영합니다.
후보 ZIP SHA-256: `1BCC92A3CD7025D307AF9B193BDDD8F1448451024630C8414FC218F0C49FE829`. Steam 실적용과 14개 복원 백업, 실제 한글 화면 검증을 모두 완료했습니다.
표의 수치는 원문 해시·줄바꿈·제어문자 계약을 통과한 안전 이식 수입니다. 전체 번역 완료율을 뜻하지 않습니다.
<!-- translation-progress:end -->

<!-- active-text-audit:start -->
### v0.10.0 Steam 적용 후보 — GitHub 릴리스 대기

v0.9.0 공개본을 기준으로 활성 Steam JP 텍스트 10개 테이블을 다시 감사한 결과입니다.
아래는 고신뢰 ‘가나가 남고 한글이 없는’ 좌표만의 폐쇄 검증이며, 게임 전체 번역 완료율이 아닙니다.

| 후보 감사 결과 | 좌표 수 | 처리 |
|---|---:|---|
| 한국어 적용 | 2,489 | 원문·형식 계약과 재파싱 검증 통과 |
| 공식 크레딧 보존 | 6 | 의도적으로 원문 유지 |
| 런타임 구조 보존 | 3 | 동적 구조라 번역 대상에서 제외 |
| 합계 | 2,498 | 후보 잔존 고신뢰 가나 9개 = 위 보존 9개 |

`strdata.bin`의 공백 보정 1건은 기존 P0 1,400건 안에 포함되어 중복 집계하지 않았습니다. 혼합 한글/가나 207건과 한자 전용 187건은 자동 완료율에 넣지 않고 별도 수동 검토 대상으로 유지합니다.
후보는 JP 경로 정확히 14파일입니다. 글꼴 폭 조정은 포함하지 않고, 원래 글꼴 리소스 4파일을 유지했습니다.
기본 이벤트 `ev_strdata.bin`은 수동 강제 줄바꿈을 4개 좌표에서 6개만 공백으로 리베이스해 자동 줄바꿈을 쓰도록 했습니다.
후보 ZIP SHA-256: `B18A5B2B4AE40BBD80BB8613BE3E6CD81DF7EDD3B7E7434A9446AFD576E2C117` (356,864,822 bytes).
Steam 설치본에는 적용했지만, 글꼴 복원·이벤트 리베이스 뒤 해당 이벤트 화면 QA는 다시 하지 않았고 GitHub 릴리스도 아직 올리지 않았습니다. 상태는 설치=True, 화면 QA=NOT_RERUN_AFTER_FONT_ROLLBACK_AND_EVENT_REBASE, 배포=False입니다.
이 ZIP은 현재 `RES_JP`의 비글꼴 payload도 보존하므로, GitHub 공개 범위 확인이 남아 있습니다.
<!-- active-text-audit:end -->

## 글꼴과 권리

한글 글리프는 서울한강체를 사용하며, 32–64px 계열은 서울한강 B, 48–96px 계열은 서울한강 EB로 렌더링합니다.

이 프로젝트는 비공식 팬메이드 한글 패치입니다. KOEI TECMO GAMES의 공식 제품이나 지원물이 아니며, 게임·상표·로고·원본 데이터에 관한 모든 권리는 KOEI TECMO GAMES 및 각 권리자에게 있습니다.
