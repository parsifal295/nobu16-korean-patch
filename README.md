# 신장의 야망·신생 with 파워업키트 비공식 한글 패치

Windows Steam판 `NOBU16PK.exe`용 일본어 리소스 경로 기반 파일 전용 한글
패치입니다. 메모리 패치, DLL 주입, 후킹, EXE·레지스트리 변조는 사용하지
않습니다.

## 다운로드와 호환 버전

- 기준 버전: **Steam PK v1.1.7** (`Update 1.1.7`, Steam build `18823764`)
- 배포 버전: **v0.6.0**
- 패치 파일: [NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.6.0.zip](https://github.com/parsifal295/nobu16-korean-patch/releases/download/v0.6.0/NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.6.0.zip)
- ZIP SHA-256: `1762265CD011D8476B8B90C87E3CA3F5F1D920B46C4A97460147A5FEEDA373D0`

다른 게임 버전이나 Microsoft Store·비Steam판은 이 배포본의 호환 대상이
아닙니다. 번역은 아직 진행 중이므로 일부 화면에는 일본어가 남아 있습니다.

## 설치

1. Steam 게임 속성의 언어와 공식 런처 왼쪽 위 언어를 모두
   **`日本語 / Japanese`**로 설정합니다.
2. 게임과 공식 런처를 완전히 종료합니다.
3. ZIP 안의 `MSG`, `MSG_PK`, `RES_JP`, `RES_JP_PK` 네 폴더를 Steam 게임
   폴더(`...\SteamLibrary\steamapps\common\NOBU16`)에 그대로 덮어씁니다.
4. 공식 런처에서 PK판을 실행합니다.

ZIP에는 원래 폴더와 파일명을 유지한 실제 게임 적용 파일 10개가 들어 있으며,
폰트 파일인 `RES_JP/res_lang.bin`과 `RES_JP_PK/res_lang_pk.bin`도 포함됩니다.

## 현재 진행률

<!-- translation-progress:start -->
| 영역 | 적용 현황 | 남은 작업 |
|---|---:|---:|
| PK UI `msgui.bin` | 안전 이식 3,693 / 4,037 (91.5%) | 344 |
| PK 공용 메시지 5종 | 적용 39,507 / 39,603 (99.8%) | 96 |
| PK 본문 `msggame.bin` | 적용 24,211 / 28,272 (85.6%) | 4,061 |
| 공용 `strdata.bin` | 안전 이식 24,524 / 24,525 | 1 |
| 일본어 경로 한글 폰트 | 2 / 2 실기 확인 | 0 |

`msgui.bin`의 안전 이식 3,693건 중 실제 문구 변경은 3,614건이고, 79건은 원문과
동일합니다. 공용 메시지의 중복 문맥 50건은 동일 대상으로 합쳐졌습니다. 수치는
구조를 보존해 현재 Steam 1.1.7 파일에 안전하게 이식된 항목 기준이며, 줄바꿈·잘림·
문맥 검수 완료율을 뜻하지는 않습니다.

Steam PK v1.1.7 실기에서 일본어 런처, 한글 타이틀 안내, 한글 메인 메뉴와 두 한글
폰트 컨테이너를 확인했습니다. 종료 확인창 등 아직 번역되지 않은 일본어 UI가
남아 있습니다.
<!-- translation-progress:end -->

## 원상 복구

덮어쓰기 전 원본 10개 파일을 별도로 보관하는 것을 권장합니다. 원본 백업이
없다면 Steam의 **설치된 파일 → 게임 파일 무결성 확인**으로 정식 파일을 다시
받을 수 있습니다.

## 글꼴과 권리

한글 글리프는 [서울한강체(서울시)](https://www.seoul.go.kr/seoul/font.do)를
사용하며 [공공누리 제1유형](https://www.kogl.or.kr/info/licenseType1.do) 조건을
따릅니다.

이 프로젝트는 팬이 제작한 비공식·비영리 한글화 프로젝트이며 KOEI TECMO
GAMES의 공식 제품이나 지원물이 아닙니다. 게임, 상표, 로고 및 원저작물에 관한
모든 권리는 KOEI TECMO GAMES 및 각 권리자에게 있습니다.
