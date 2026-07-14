# NOBU16 Korean Patch

목적: `신장의 야망 : 신생 파워업키트`의 한글 패치 제작

번역을 작은 ID 배치로 나눠 병렬로 진행하고, 원문 해시·제어코드·필요 글리프를 자동
검증해 **번역 속도와 배포 안전성**을 함께 확보하는 비공식 개발 프로젝트다.

<!-- translation-progress:start -->
## 현재 한글화 진행 현황

파싱이 끝난 10개 메시지 리소스 기준 **번역 완료 15,164 / 111,463 (13.6%)**, 초벌 커버리지는 **15,164개**다.
`msggame.bin` 2개는 18블록 바이트코드에서 확인한 표시 가능한 SC 리터럴 후보를 분모에 포함했다.
후속 사람 분류에서 코드용 문자열이 확인되면 대상 분모를 보수적으로 조정한다.
번역 대상은 표시 가능한 비공백 문자열과 의도적으로 활성화한 UI 빈 슬롯만 센다.
완료는 공개 오버레이의 `translated`·`reviewed` 고유 ID·`msggame` 좌표 합집합이다. 최종 화면 QA 완료를 뜻하지 않는다.

| 한글화 대상 파일 | 번역 완료 / 대상 | 초벌 커버리지 | 전체 슬롯·레코드 | 진행률 | 현재 상태 |
|---|---:|---:|---:|---|---|
| `MSG_PK/SC/msgui.bin` | 4,037 / 4,037 | 4,037 | 5,100 슬롯 | 100.0% `██████████` | UI v0.2 목표 4,037개; v0.1 대상에서 86개 확장 |
| `MSG_PK/SC/msgev.bin` | 3,544 / 12,906 | 3,544 | 17,910 슬롯 | 27.5% `███░░░░░░░` | 장수명 2,207 + 대사 1,337 |
| `MSG_PK/SC/msgdata.bin` | 4,223 / 25,534 | 4,223 | 29,210 슬롯 | 16.5% `██░░░░░░░░` | 장수 구성요소 + 성 이름 + 옛 지방명; 검수 대기 0 |
| `MSG_PK/SC/msgbre.bin` | 566 / 2,217 | 566 | 3,000 슬롯 | 25.5% `███░░░░░░░` | 장수 열전 ID 0–565, 566개 초벌; 다음 ID 566 |
| `MSG_PK/SC/msgire.bin` | 122 / 122 | 122 | 122 슬롯 | 100.0% `██████████` | 물품·명물 설명 122개 번역 완료 |
| `MSG_PK/SC/msgstf.bin` | 8 / 8 | 8 | 20 슬롯 | 100.0% `██████████` | 크레디트 직책·분야 8개 완료; 빈 구조 슬롯 12개 제외 |
| `MSG_PK/SC/msggame.bin` | 450 / 16,482 | 450 | 25,598 슬롯 | 2.7% `░░░░░░░░░░` | 좌표 기반 450개 초벌; 다음 좌표 (2,566,0), 블록 0 문법 조각 93개 문맥 검수 보류 |
| `MSG/SC/msggame.bin` | 0 / 12,268 | 0 | 21,225 슬롯 | 0.0% `░░░░░░░░░░` | 18블록·19,152레코드 파싱 및 가변 길이 재패킹 완료; 표시 후보 12,268개, 번역 미착수 |
| `MSG/SC/strdata.bin` | 0 / 26,690 | 0 | 32,311 슬롯 | 0.0% `░░░░░░░░░░` | 5개 블록 파싱 완료; 번역 미착수 |
| `MSG/SC/ev_strdata.bin` | 2,214 / 11,199 | 2,214 | 17,868 슬롯 | 19.8% `██░░░░░░░░` | 장수명 ID 0–2206 2,207개 + 이벤트 라벨 7개 완료; ID 2207–3200 내부 placeholder 488개는 대상 제외; 다음 ID 2407 |
| `RES_SC/res_lang.bin` | 1 / 4 게이트 | — | — | 25.0% `██░░░░░░░░` | Font-v6 정적 재현 PASS; 최신 초벌 글리프 갱신·런타임·통합 설치 대기 |
| `RES_SC/res_lang_exp.bin` | 1 / 2 조사 게이트 | — | — | 50.0% `█████░░░░░` | 재귀 스캔에서 글꼴 시그니처 0; 런타임 의존성 확인 대기 |

이 표는 `tools/update_readme_progress.py`가 공개 오버레이를 다시 집계해 만든다. 모든
커밋은 표를 갱신한 뒤 `--check`를 통과해야 한다.
<!-- translation-progress:end -->

> **현재 상태: 개발 중 — `release_eligible=false`**
>
> 장수명 범위의 RC는 설치·복원과 실제 게임 표시까지 검증했지만, 전체 UI·성 이름·대사·
> Font-v6를 묶는 일반 사용자용 통합 설치기는 아직 완성되지 않았다. 개발 산출물을 설치
> 파일에 직접 덮어쓰지 말 것.

## 패치가 작동하는 방식

- 공식 **간체중문(SC) 리소스 경로**를 기반으로 한다. 일반 UI는 가로쓰기이며, 한글
  글리프를 추가한 메시지·글꼴 파일을 오프라인에서 재구성한다.
- 프로세스 메모리 패치, DLL 주입, 후킹, 프록시 DLL, EXE 수정, 레지스트리 변경을
  사용하지 않는다. 게임을 대신 실행하는 상주 프로그램도 두지 않는다.
- 설치 시 지원하는 순정 파일의 크기와 SHA-256을 먼저 확인하고, 백업·저널·원자적 교체·
  해시 검증·완전 복원을 한 거래로 처리하는 구조를 사용한다.
- 공개 저장소와 배포본에는 상용 원문이나 완성된 게임 리소스를 넣지 않는다. 공개
  오버레이는 숫자 ID, 순정 문자열 해시, 프로젝트가 작성한 한국어만 담는다.

파일 전용·상용 원문 비공개·완전 복원 원칙은 이 공개 README와 각 작업선 README에만
요약한다. 역공학 메모와 내부 조사 문서는 로컬 작업 자료로 두고 공개 저장소에서 제외한다.

## 지금까지 된 것

| 작업선 | 현재 결과 | 남은 게이트 |
|---|---|---|
| 장수명 | 2,207개 합성명과 보수적으로 확정한 분리 슬롯을 포함한 4리소스 RC. `오다 노부나가` 등 실제 화면 표시, 적용·복원 검증 완료 | 전체 인명 표기의 사람 전수 교정 |
| MSGUI v0.2 | 5,100개 ID 분류 완료. 번역·검수 4,037개, 실제 교체 3,922개, 일반 SC 비공백 미번역 0개 | 새로 활성화한 SC 공백 슬롯 86개의 화면·전투 문맥 QA |
| 성·거점 이름 v0.2 | ID 9151–9542, 392개 전수 검수 완료. v0.1에서 53개 표기를 교정하고 source-free 결정성 검증 통과 | 장수명·옛 지방명 `msgdata`와 병합, 실제 지도 QA |
| 옛 지방명 v0.2 | ID 13975–14046, 72개 전수 검수 완료. v0.1 표기를 모두 유지하고 source-free 결정성 검증 통과 | 장수명·성 이름 `msgdata`와 병합, 실제 지도 QA |
| `msgire` v0.1 | 물품·명물 설명 ID 0–121, 122개 전체 번역. 3언어 ID 정렬·형식 불변조건·A/B 결정성 검증 완료 | 최신 글꼴과 통합 설치본에 편입, 실제 설명창 QA |
| `msgstf` v0.1 | 크레디트 ID 0–7, 8개 직책·분야 번역. 인명·회사명은 라틴 표기 유지, 빈 구조 슬롯 12개 제외 | 최신 글꼴과 통합 설치본에 편입, 실제 크레디트 QA |
| 장수 열전 v0.1–v0.5 | `msgbre` ID 0–565, 566개 초벌. SC·JP·EN 정렬, 형식 불변조건, 소스 비공개와 A/B 결정성 검증 완료 | 고유명사·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 566 |
| 본편 `ev_strdata` v0.1–v0.12 | 파일 선두 장수 전체 이름표 ID 0–2206, 2,207개 전부 완료. 기존 장수명 해시 일치 2,205개를 재사용하고 SC 표기 변형 2개를 독립 대조했으며 SC·JP·TC 정렬·A/B 결정성 검증 완료 | 사람 검수 후 다음 글꼴·통합 배포본에 편입; 후속 이벤트 제목·라벨 분류는 v0.13에서 계속 |
| 본편 `ev_strdata` 이벤트 라벨 v0.13 | ID 2207–2406 200개 조사. 내부 placeholder 193개를 보류하고 실제 표시용 지역 국인중 두령 라벨 ID 2400–2406, 7개 번역. ID 2207–3200 전체 분류에서 placeholder 488개를 번역 대상에서 제외 | 나머지 지역 라벨과 표시 후보 번역; 다음 ID 2407 |
| `msggame` 구조·번역 v0.1–v0.3 | PK 21,581·본편 19,152레코드의 18블록 바이트코드를 파싱. SC 표시 후보 16,482 + 12,268개를 확정하고 7개 언어 파일 byte-exact 재구축 및 더 긴 한글 리터럴 재패킹 성공. PK 450개 초벌 완료 | 코드용 문자열 사람 분류, 블록 0 문법 조각 문맥 검수, 후속 번역과 실제 게임 화면 QA; 다음 좌표 `(2,566,0)` |
| 이벤트 대사 v0.1 | ID 3202–3229, 28개 초벌. 제어코드·개행 보존과 A/B 빌드 검증 완료 | 문체·고유명·실제 대화창 QA |
| 이벤트 대사 v0.2 | ID 3230–3308, 후속 79개 초벌. 5개 사건, 3언어 해시 237개와 형식 불변조건 검증 완료 | 사람 검수 후 다음 글꼴·통합 배포본에 편입 |
| 이벤트 대사 v0.3 | ID 3309–3440에서 내부 키 18개를 제외한 후속 114개 초벌. 지역 통일·조정 관직·천하 통일·장기 정권 결말을 3언어 정렬과 형식 불변조건으로 검증 | 용어·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입 |
| 이벤트 대사 v0.4 | ID 3441–3564, 후속 124개 초벌. 5개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료 | 용어·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입 |
| 이벤트 대사 v0.5 | ID 3565–3688, 후속 124개 초벌. 6개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료 | 용어·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입 |
| 이벤트 대사 v0.6 | ID 3689–3818, 후속 130개 초벌. 6개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료 | 용어·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입 |
| 이벤트 대사 v0.7 | ID 3819–3929, 후속 111개 초벌. 6개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료 | 용어·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입 |
| 이벤트 대사 v0.8 | ID 3930–4031, 후속 102개 초벌. 6개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료 | 용어·문체 사람 검수와 ID 3968 긴 문장의 실제 줄바꿈 QA 후 다음 글꼴·통합 배포본에 편입 |
| 이벤트 대사 v0.9 | ID 4032–4160, 후속 129개 초벌. 7개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료, 모든 줄 32자 이하 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 4161 |
| 이벤트 대사 v0.10 | ID 4161–4279, 후속 119개 초벌. 7개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료, 모든 줄 32자 이하 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 4280 |
| 이벤트 대사 v0.11 | ID 4280–4417, 후속 138개 초벌. 7개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 4418 |
| 이벤트 대사 v0.12 | ID 4418–4556, 후속 139개 초벌. 8개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료, 최대 줄 길이 30자 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 4557 |
| Font-v6 | MSGUI v0.2 + 장수명 + 대사 v0.1 28개 + 성 이름 v0.1 392개의 700자 수요를 오프라인 A/B 빌드와 공개 레시피 재생으로 검증 | 최신 글리프 갱신과 런타임 화면·종료 QA. 성 이름 v0.2 교정분, 대사 v0.2~v0.12 1,309개, 장수 열전 566개, 본편 장수명 2,207개, 본편 이벤트 라벨 7개, `msggame` 450개, 옛 지방명 72개, 소형 테이블 130개는 아직 미포함 |

세부 근거와 재현 절차:

- [장수명](workstreams/officer_names/README_KO.md)
- [전체 UI](workstreams/msgui_full/README.md)
- [성 이름 392개](workstreams/castle_names/README_KO.md)
- [옛 지방명 72개](workstreams/province_names/README_KO.md)
- [`msgire`·`msgstf` 소형 테이블](workstreams/small_message_tables/README_KO.md)
- [장수 열전 v0.1 129개](workstreams/msgbre/README_KO.md) · [v0.2 122개](workstreams/msgbre/BATCH2_V0.2_README_KO.md)
- [장수 열전 v0.3 100개](workstreams/msgbre/BATCH3_V0.3_README_KO.md)
- [장수 열전 v0.4 107개](workstreams/msgbre/BATCH4_V0.4_README_KO.md)
- [장수 열전 v0.5 108개](workstreams/msgbre/BATCH5_V0.5_README_KO.md)
- [본편 `ev_strdata` v0.1–v0.2 350개](workstreams/ev_strdata/README_KO.md) · [v0.3 200개](workstreams/ev_strdata/BATCH3_V0.3_README_KO.md)
- [본편 `ev_strdata` v0.4 200개](workstreams/ev_strdata/BATCH4_V0.4_README_KO.md)
- [본편 `ev_strdata` v0.5 200개](workstreams/ev_strdata/BATCH5_V0.5_README_KO.md)
- [본편 `ev_strdata` v0.6 200개](workstreams/ev_strdata/BATCH6_V0.6_README_KO.md)
- [본편 `ev_strdata` v0.7 200개](workstreams/ev_strdata/BATCH7_V0.7_README_KO.md)
- [본편 `ev_strdata` v0.8 200개](workstreams/ev_strdata/BATCH8_V0.8_README_KO.md)
- [본편 `ev_strdata` v0.9 200개](workstreams/ev_strdata/BATCH9_V0.9_README_KO.md)
- [본편 `ev_strdata` v0.10 200개](workstreams/ev_strdata/BATCH10_V0.10_README_KO.md)
- [본편 `ev_strdata` v0.11 200개](workstreams/ev_strdata/BATCH11_V0.11_README_KO.md)
- [본편 `ev_strdata` v0.12 장수명 마감 57개](workstreams/ev_strdata/BATCH12_V0.12_README_KO.md)
- [본편 `ev_strdata` v0.13 이벤트 라벨 7개](workstreams/ev_strdata/BATCH13_V0.13_README_KO.md)
- [`msggame` 18블록 구조·가변 길이 오버레이](workstreams/msggame/README_KO.md)
- [`msggame` PK 첫 번역 150개](workstreams/msggame/BATCH1_V0.1_README_KO.md)
- [`msggame` PK 후속 번역 150개](workstreams/msggame/BATCH2_V0.2_README_KO.md)
- [`msggame` PK 후속 번역 v0.3 150개](workstreams/msggame/BATCH3_V0.3_README_KO.md)
- [대사 v0.1·v0.2](workstreams/dialogue/README_KO.md) · [대사 v0.3 114개](workstreams/dialogue/BATCH3_V0.3_README_KO.md)
- [대사 v0.4 124개](workstreams/dialogue/BATCH4_V0.4_README_KO.md) · [대사 v0.5 124개](workstreams/dialogue/BATCH5_V0.5_README_KO.md)
- [대사 v0.6 130개](workstreams/dialogue/BATCH6_V0.6_README_KO.md)
- [대사 v0.7 111개](workstreams/dialogue/BATCH7_V0.7_README_KO.md)
- [대사 v0.8 102개](workstreams/dialogue/BATCH8_V0.8_README_KO.md)
- [대사 v0.9 129개](workstreams/dialogue/BATCH9_V0.9_README_KO.md)
- [대사 v0.10 119개](workstreams/dialogue/BATCH10_V0.10_README_KO.md)
- [대사 v0.11 138개](workstreams/dialogue/BATCH11_V0.11_README_KO.md)
- [대사 v0.12 139개](workstreams/dialogue/BATCH12_V0.12_README_KO.md)
- [Font-v6](workstreams/font_v6/README_KO.md)

## 아직 배포본이 아닌 이유

오프라인 해시와 A/B 결정성 검증은 실제 화면 검수를 대신하지 않는다. 현재 통합 후보에는
다음 작업이 남아 있다.

1. 성 이름·옛 지방명과 장수명 `msgdata` 변경을 하나의 순정 기준 레시피로 병합한다.
2. 장수명·대사 v0.1~v0.12의 `msgev` 변경과 장수 열전 v0.1~v0.5의 `msgbre` 변경을 각 순정
   기준 레시피로 병합한다.
3. `msggame` 표시 후보 28,750개를 코드용 문자열과 실제 문장으로 계속 분류하고 PK 첫 450개 뒤의 번역을 진행한다.
4. 후속 대사 1,309개, 장수 열전 566개, 본편 장수명 2,207개, 본편 이벤트 라벨 7개, `msggame` 450개, 옛 지방명 72개, 소형 테이블 130개의 새 한글 수요를 다음 글꼴
   리비전에 넣고 네 글꼴 표 누락 0개를 재검증한다.
5. MSGUI v0.2, 메시지 병합본, `msgire`·`msgstf`, 새 글꼴을 다중 파일 설치·복원 거래로
   조립한다.
6. 대표 메뉴·장수명·대화창·지도에서 누락 글리프, 잘림, 겹침, 정상 종료와 완전 복원을
   실제 게임으로 확인한다.

이 게이트가 끝날 때까지 프로젝트 전체 상태는 `release_eligible=false`다. 과거 개발 ZIP이나
개별 workstream 후보가 존재하더라도 최신 통합 패치로 간주하지 않는다.

## 확인된 실행 조건

- 현재 개발·런타임 검증 환경은 **Steam판이 아닌 Windows PC 설치본**이다. Steam판
  호환성은 아직 검증하거나 보장하지 않는다.
- SC 일반 UI는 가로쓰기지만 전략지도 성 이름은 현재 세로로 배치된다. 이는 알려진 표시
  제한으로 기록하고 번역·배포 작업을 계속한다.
- `NOBU16PK.exe`의 작업 폴더(바로가기의 `시작 위치`)는 게임 설치 루트여야 한다. 다른
  폴더에서 실행하면 순정 파일에서도 `ERROR:-9001`이 재현됐다. 이 오류가 보이면 패치
  손상을 의심하기 전에 작업 폴더부터 확인한다.

두 조건은 로컬 런타임 QA에서 재현해 확인했으며, 상세 조사 로그와 스크린샷은 공개
저장소가 아닌 내부 작업 자료로 보관한다.

## 가장 빠르게 기여하는 법

큰 파일 하나를 오래 붙잡기보다, 검토 가능한 작은 배치를 끝내는 기여를 권장한다.

모든 커밋 전에 `python -B tools/update_readme_progress.py`를 실행하고
`python -B tools/update_readme_progress.py --check`로 README 상단 수치가 현재 공개
오버레이와 일치하는지 확인한다.

1. `workstreams/*/review/`의 검수 항목이나 공개 한국어 오버레이에서 어색한 문장·인명·
   지명을 고른다.
2. 숫자 ID와 한국어만 수정하고, 공식 JP/EN/SC/TC 원문은 커밋하지 않는다. 원문 확인이
   필요하면 본인이 합법적으로 보유한 설치본을 로컬에서만 사용한다.
3. ESC 색상 코드, printf 토큰, PUA 아이콘, 개행, 앞뒤 공백을 원문 구조와 동일하게
   보존한다.
4. 20–100개 정도의 연속 ID 배치로 생성기·검증·검수 인덱스를 함께 갱신한다.
5. 새 글자가 생기면 glyph-demand를 다시 만들고, 통합 글꼴에 들어가기 전 누락 목록과
   canonical SHA-256을 고정한다.

빠른 source-free 회귀 검사는 설치 파일을 수정하지 않는다.

```powershell
python -B -m unittest tests.test_common_message_overlay tests.test_export_common_message_overlay
python -B -m unittest tests.test_generate_public_overlay_glyph_demand
python -B -m unittest discover -s workstreams/dialogue/tests -p "test_*.py"
python -B tools/generate_public_overlay_glyph_demand.py dialogue --check
python -B tools/generate_public_overlay_glyph_demand.py castle --check
```

순정 백업이 필요한 A/B 빌드와 recipe replay는 각 workstream README의 고정 해시와 출력
경로 규칙을 따른다. 설치된 게임 파일 자체를 빌드 입력이나 출력으로 사용하지 않는다.

## 저장소 구조

| 경로 | 내용 |
|---|---|
| `data/public/` | 원문 없는 공개 번역 오버레이: ID + 순정 문자열 해시 + 한국어 |
| `data/translations/` | 공식 원문을 대조하는 로컬 개발 자료. Git 제외 |
| `workstreams/` | UI, 장수명, 성 이름, 대사, 글꼴, 설치기 후보별 독립 작업선 |
| `tools/` | 추출·생성·레시피 재생·감사·안전 적용/복원 도구 |
| `tests/` | 포맷, 중복 키, 결정성, 배포 안전장치 회귀 테스트 |
| `vendor/noto/` | 고정 Noto KR 입력과 SIL OFL 라이선스 |

`tmp/`, `backups/`, `docs/`, `reports/`, `ghidra_scripts/`, Ghidra 프로젝트, 추출 원문,
완성 `msg*.bin`, `res_lang.bin`, G1N/G1T, 로컬 빌드 후보는 공개 추적 대상이 아니다.

## 공개·배포 원칙

이 저장소는 게임 파일 저장소가 아니라 **재현 가능한 패치 소스**다.

- 공개 패키지는 프로젝트 소유 번역, 구조 레시피, 델타/글리프 픽셀, 해시, 검증기와
  라이선스만 포함한다.
- 전체 순정·수정 게임 리소스, 실행 파일, 추출 원문, 중첩 archive는 배포하지 않는다.
- Python, Ghidra, 폰트 도구와 Noto 원본 폰트는 개발 단계 입력이다. 최종 사용자용
  설치·검증·복원은 별도 Python이나 Ghidra를 요구하지 않는 것을 목표로 한다.
- 설치기는 게임과 런처가 실행 중이면 중단하고, 미지원·혼합 해시 상태를 임의로 덮어쓰지
  않아야 한다.

공개 기여 전에는 `git status --ignored`로 상용 원문·전체 리소스·내부 문서·로컬 백업이
staged되지 않았는지 확인한다.
