# NOBU16 Korean Patch

목적: `신장의 야망 : 신생 파워업키트`의 한글 패치 제작

번역을 작은 ID 배치로 나눠 병렬로 진행하고, 원문 해시·제어코드·필요 글리프를 자동
검증해 **번역 속도와 배포 안전성**을 함께 확보하는 비공식 개발 프로젝트다.

외부 Switch v1.1·v1.3 번역 원천의 선별 이식·검증 기준과 출처는 [외부 번역 원천 고지](THIRD_PARTY_NOTICES.md)에 기록합니다. v1.3의 세 메시지 파일은 v1.1과 바이트 동일하며, 새 이미지 자산은 PC 포맷·내용 검증을 따로 통과한 항목만 사용합니다. 최신 v1.4의 신규분은 Switch 실행파일 `exefs/main` 6문장뿐이므로 EXE 변조 금지 정책에 따라 이식 대상에서 제외합니다.

Switch `strdata.bin`도 전체 파일을 복사하지 않고, PC 순정 SC와 같은 블록·슬롯에서 형식이 안전한 한국어 좌표만 source-free 오버레이로 옮깁니다.

<!-- translation-progress:start -->
PK 실행 경로 `MSG_PK/SC`의 7개 메시지 리소스 기준 **번역 완료 48,612 / 61,306 (79.3%)**, 대상 초벌 커버리지는 **48,612개**다. 대상 밖에서 활성화된 커버리지는 **2,382개**로 별도 집계한다.
PK 실행에서 함께 로드되는 공용 경로 `MSG/SC/strdata.bin`의 1개 문자열 리소스는 **번역 완료 24,425 / 26,690 (91.5%)**, 대상 초벌 커버리지는 **24,425개**다.
PK 공용 글꼴·리소스 경로 `RES_SC`의 2개 검증 단계는 **3 / 6** 완료다.

## 현재 한글화 진행 현황

PK 실행 기준 7개 메시지 리소스 **번역 완료 48,612 / 61,306 (79.3%)**, 대상 초벌 커버리지는 **48,612개**다. 비대상 활성 커버리지는 **2,382개**(그중 완료 상태 2,382개)로 분리했다.
PK가 실제로 함께 읽는 공용 본편 표 `MSG/SC/strdata.bin`는 **24,425 / 26,690 (91.5%)** 완료, 대상 초벌 커버리지 **24,425개**, 비대상 활성 **0개**(그중 완료 상태 0개)로 별도 집계한다.
PK `msggame.bin`은 18블록 바이트코드에서 확인한 표시 가능한 SC 리터럴 후보를 분모에 포함했다.
후속 사람 분류에서 코드용 문자열이 확인되면 대상 분모를 보수적으로 조정한다.
번역 대상은 표시 가능한 비공백 문자열과 의도적으로 활성화한 UI 빈 슬롯만 센다.
완료·초벌 커버리지는 source-free target-key 카탈로그와 공개 오버레이 고유 ID·`msggame` 좌표·공용 표 블록/슬롯 좌표 합집합의 교집합만 센다.
target-key 밖에서 새로 활성화한 ID는 번역 대상 완료율에 넣지 않고 비대상 활성 커버리지로 별도 표시한다. 최종 화면 QA 완료를 뜻하지 않는다.

| 한글화 대상 파일 | 번역 완료 / 대상 | 초벌 커버리지 | 전체 슬롯·레코드 | 진행률 | 현재 상태 |
|---|---:|---:|---:|---|---|
| `MSG_PK/SC/msgui.bin` | 4,037 / 4,037 | 4,037 | 5,100 슬롯 | 100.0% `██████████` | UI v0.2 목표 4,037개; v0.1 대상에서 86개 확장 |
| `MSG_PK/SC/msgev.bin` | 11,580 / 12,906 | 11,580 (+1,598 비대상 활성) | 17,910 슬롯 | 89.7% `█████████░` | 실제 PK/SC 대상 11,580개 완료 + 순정 빈 슬롯 Switch 활성화 1,598개; 잔여 대상 1,326개 |
| `MSG_PK/SC/msgdata.bin` | 20,296 / 25,534 | 20,296 (+784 비대상 활성) | 29,210 슬롯 | 79.5% `████████░░` | 실제 PK/SC 대상 20,296개 완료 + 순정 빈 슬롯 Switch 활성화 784개; 잔여 대상 5,238개 |
| `MSG_PK/SC/msgbre.bin` | 2,217 / 2,217 | 2,217 | 3,000 슬롯 | 100.0% `██████████` | 장수 열전 2,217 / 2,217 완료; Switch 이식·정리 뒤 PK 전용 잔여 11개 직접 번역으로 target 100% |
| `MSG_PK/SC/msgire.bin` | 122 / 122 | 122 | 122 슬롯 | 100.0% `██████████` | 물품·명물 설명 122개 번역 완료 |
| `MSG_PK/SC/msgstf.bin` | 8 / 8 | 8 | 20 슬롯 | 100.0% `██████████` | 크레디트 직책·분야 8개 완료; 빈 구조 슬롯 12개 제외 |
| `MSG_PK/SC/msggame.bin` | 10,352 / 16,482 | 10,352 | 25,598 슬롯 | 62.8% `██████░░░░` | 좌표 기반 + Switch 엄격·형식 복구·검토 + UI 우선 배치 10,352개 완료; UI 우선 203개 추가, 잔여 6,130개 |
| `MSG/SC/strdata.bin` | 24,425 / 26,690 | 24,425 | 32,311 슬롯 | 91.5% `█████████░` | PK 실행이 실제로 함께 읽는 공용 본편 표: Switch v1.3 직접 이식 24,424개 + 확인된 공용 UI 1개, 비공백 대상 26,690개 중 24,425개 완료; 잔여 2,265개와 실제 화면 QA 대기 |
| `RES_SC/res_lang.bin` | 2 / 4 게이트 | — | — | 50.0% `█████░░░░░` | PK 공용 RES_SC 경로: 서울한강체 v1 G1N 및 화면 제목 108개 PC BC3/G1T/LINK 후보의 로컬 A/B 결정성 PASS; 실제 PK 화면·저장·종료 QA 대기 |
| `RES_SC/res_lang_exp.bin` | 1 / 2 조사 게이트 | — | — | 50.0% `█████░░░░░` | PK 공용 RES_SC 경로: 재귀 스캔에서 글꼴 시그니처 0; 런타임 의존성·역할 확인 대기 |

이 표는 `tools/update_readme_progress.py`가 공개 오버레이를 다시 집계해 만든다. 모든
커밋은 표를 갱신한 뒤 `--check`를 통과해야 한다.
<!-- translation-progress:end -->

> **현재 상태: 개발 중 — `release_eligible=false`**
>
> 장수명 범위의 RC는 설치·복원과 실제 게임 표시까지 검증했지만, 전체 UI·성 이름·대사·
> 서울한강체 v1를 묶는 일반 사용자용 통합 설치기는 아직 완성되지 않았다. 개발 산출물을 설치
> 파일에 직접 덮어쓰지 말 것.

## 패치가 작동하는 방식

- 공식 **간체중문(SC) 리소스 경로**를 기반으로 한다. 일반 UI는 가로쓰기이며, 한글
  글리프를 추가한 메시지·글꼴 파일을 오프라인에서 재구성한다.
- PK 기능 메뉴 추적으로 본편 공용 `MSG/SC/strdata.bin`도 실제 PK 실행에서 로드됨을
  확인했다. 이 파일만 명시적 공유 런타임 예외로 다루며 `MSG/SC/ev_strdata.bin`은
  현재 PK 진행률·적용 대상에 포함하지 않는다.
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
| 장수 열전 v0.1–v0.11 + Switch 이식·PK 보완 | `msgbre` 번역 대상 2,217개 전부 완료. 기존 836개, Switch 엄격 이식 1,367개, CJK 잔존 3개 정리 뒤 PK 전용 잔여 11개를 직접 번역했다 | 고유명사·문체 사람 검수와 실제 열전 화면 QA |
| `msggame` 구조·번역 v0.1–v0.22 + Switch·UI 우선 배치 | PK 21,581레코드의 18블록 바이트코드를 파싱하고 SC 표시 후보 16,482개를 확정했다. 좌표 기반 이식·검토와 UI 우선 203개를 합쳐 10,352개 완료 | 잔여 6,130개 병렬 번역, 코드용 문자열 사람 분류, 실제 게임 화면 QA |
| PK 공용 `MSG/SC/strdata.bin` | 순정 5블록 32,311좌표 중 비공백 번역 대상 26,690개를 확정했다. Switch v1.3 안전 직접이식 24,424개와 실제 하단 버튼 `돌아가기` 1개를 합쳐 24,425개 완료 | 잔여 2,265개 문맥 번역, 최신 글꼴 후보 재적용, PK 공용 메뉴 화면 QA |
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
| 이벤트 대사 v0.13 | ID 4557–4690, 후속 134개 초벌. 6개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료, 모든 줄 32자 이하 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 4691 |
| 이벤트 대사 v0.14 | ID 4691–4838, 후속 148개 초벌. 7개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료, 모든 줄 32자 이하 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 4839 |
| 이벤트 대사 v0.15 | ID 4839–4976, 후속 138개 초벌. 6개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료, 모든 줄 32자 이하 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 4977 |
| 이벤트 대사 v0.16 | ID 4977–5108, 후속 132개 초벌. 5개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료, 모든 줄 32자 이하 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 5109 |
| 이벤트 대사 v0.17 | ID 5109–5237, 후속 129개 초벌. 5개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료, 최대 줄 길이 31자 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 5238 |
| 이벤트 대사 v0.18 | ID 5238–5358, 후속 121개 초벌. 6개 사건과 3언어 정렬·형식 불변조건·A/B 결정성 검증 완료, 모든 줄 32자 이하 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 5359 |
| 이벤트 대사 v0.19 | ID 5359–5486, 후속 128개 초벌. 스노마타 축성부터 노부나가의 간레이·부쇼군직 거절까지 6개 사건을 3언어 정렬·형식 불변조건·A/B 결정성으로 검증, 모든 줄 32자 이하 | 용어·독음·문체 사람 검수와 ID 5465의 개행 횡단 색상 범위 실제 화면 QA 후 다음 글꼴·통합 배포본에 편입; 다음 ID 5487 |
| 이벤트 대사 v0.20 | ID 5487–5628, 후속 142개 초벌. ‘적에게 소금을 보내다’부터 바바 노부하루의 오개조까지 6개 사건을 3언어 정렬·형식 불변조건·A/B 결정성으로 검증, 모든 줄 32자 이하 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 5629 |
| 이벤트 대사 v0.21 | ID 5629–5748, 후속 120개 초벌. 이마가와 협공 동맹부터 미마세토게 전투까지 7개 사건을 3언어 정렬·형식 불변조건·A/B 결정성으로 검증, 모든 줄 32자 이하 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 5749 |
| 이벤트 대사 v0.22 | ID 5749–5873, 후속 125개 초벌. 오토모의 모리 포위망부터 이마야마 전투 전야까지 6개 사건을 3언어 정렬·형식 불변조건·A/B 결정성으로 검증, 모든 줄 32자 이하 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 5874 |
| 이벤트 대사 v0.23 | ID 5874–6019, 후속 146개 초벌. 다테 가문의 덴분의 난 종결부터 모리 모토나리의 죽음까지 8개 사건을 3언어 정렬·형식 불변조건·A/B 결정성으로 검증, 모든 줄 32자 이하 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 6020 |
| 이벤트 대사 v0.24 | ID 6020–6141, 후속 122개 초벌. 히데요시의 나가하마 축성부터 겐신이 애도한 신겐의 죽음까지 6개 사건을 3언어 정렬·형식 불변조건·A/B 결정성으로 검증, 모든 줄 32자 이하 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 6142 |
| 이벤트 대사 v0.25 | ID 6142–6268, 후속 127개 초벌. 미카타가하라 패전부터 에치고 우에스기 가문의 단절까지 5개 사건을 3언어 정렬·형식 불변조건·A/B 결정성으로 검증, 모든 줄 30자 이하 | 용어·독음·문체 사람 검수 후 다음 글꼴·통합 배포본에 편입; 다음 ID 6269 |
| Switch v1.1 엄격 이식 + v1.3 재감사 | 기존 엄격 이식 뒤에 실제 PK/SC 대상 `msgev` 245개·`msgdata` 145개·`msgbre` 3개를 추가 복구했다. target-key 교집합만 진행률에 넣고 순정 빈 슬롯 2,382개는 별도 활성분으로 분리한다 | `msggame` 형식 차이 후보 병렬 복구, 실제 PK 화면에서 문맥·줄바꿈·누락 글리프 QA |
| Switch v1.3 화면 제목 이미지 | `/3/0..107` 108개를 전수 처리했다. 동일 인덱스 103개, 의미 재매핑 3개(0←3, 24←25, 25←24), 서울한강체 신규 렌더 2개(38 `부대 편성`, 74 `공주 정보`)를 PC 512×128·BC3·G1T·LINK로 재조립했다. 독립 A/B 후보 SHA-256과 108개 재추출 PNG가 모두 일치하며 PC 전용 꼬리 108·109와 비대상 outer 엔트리도 보존됐다 | 로컬 게임 파일에는 적용 완료. 실제 PK 화면에서 위치·잘림·용어의 전수 QA 대기 |
| 서울한강체 v1 | PK 전용 7개 메시지와 실제 로드가 확인된 공용 `strdata`의 공개 오버레이 수요를 PC `RES_SC` G1N 구조로 로컬 A/B 결정적 빌드 검증 | 최신 후보의 실제 PK 화면·저장·종료 QA. 공식 TTF·래스터·완성 `res_lang`은 저장소에 포함하지 않음 |

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
- [장수 열전 v0.9 45개](workstreams/msgbre/BATCH9_V0.9_README_KO.md) · [v0.10 45개](workstreams/msgbre/BATCH10_V0.10_README_KO.md) · [v0.11 45개](workstreams/msgbre/BATCH11_V0.11_README_KO.md)
- [`msggame` 18블록 구조·가변 길이 오버레이](workstreams/msggame/README_KO.md)
- [`msggame` PK 첫 번역 150개](workstreams/msggame/BATCH1_V0.1_README_KO.md)
- [`msggame` PK 후속 번역 150개](workstreams/msggame/BATCH2_V0.2_README_KO.md)
- [`msggame` PK 후속 번역 v0.3 150개](workstreams/msggame/BATCH3_V0.3_README_KO.md)
- [`msggame` PK 후속 번역 v0.4 150개](workstreams/msggame/BATCH4_V0.4_README_KO.md)
- [`msggame` PK 후속 번역 v0.5 150개](workstreams/msggame/BATCH5_V0.5_README_KO.md)
- [`msggame` PK 후속 번역 v0.6 150개](workstreams/msggame/BATCH6_V0.6_README_KO.md)
- [`msggame` PK 후속 번역 v0.7 150개](workstreams/msggame/BATCH7_V0.7_README_KO.md)
- [`msggame` PK 후속 번역 v0.8 150개](workstreams/msggame/BATCH8_V0.8_README_KO.md)
- [`msggame` PK 후속 번역 v0.9 150개](workstreams/msggame/BATCH9_V0.9_README_KO.md)
- [`msggame` PK 후속 번역 v0.10 150개](workstreams/msggame/BATCH10_V0.10_README_KO.md)
- [`msggame` PK 후속 번역 v0.11 150개](workstreams/msggame/BATCH11_V0.11_README_KO.md)
- [`msggame` PK 후속 번역 v0.12 150개](workstreams/msggame/BATCH12_V0.12_README_KO.md)
- [`msggame` PK 후속 번역 v0.13 150개](workstreams/msggame/BATCH13_V0.13_README_KO.md)
- [`msggame` PK 후속 번역 v0.14 150개](workstreams/msggame/BATCH14_V0.14_README_KO.md)
- [`msggame` PK 후속 번역 v0.15 150개](workstreams/msggame/BATCH15_V0.15_README_KO.md)
- [`msggame` PK 후속 번역 v0.16 150개](workstreams/msggame/BATCH16_V0.16_README_KO.md)
- [`msggame` PK 후속 번역 v0.17 150개](workstreams/msggame/BATCH17_V0.17_README_KO.md)
- [`msggame` PK 후속 번역 v0.18 150개](workstreams/msggame/BATCH18_V0.18_README_KO.md) · [v0.19 150개](workstreams/msggame/BATCH19_V0.19_README_KO.md)
- [`msggame` PK 후속 번역 v0.20 150개](workstreams/msggame/BATCH20_V0.20_README_KO.md) · [v0.21 150개](workstreams/msggame/BATCH21_V0.21_README_KO.md) · [v0.22 150개](workstreams/msggame/BATCH22_V0.22_README_KO.md)
- [대사 v0.1·v0.2](workstreams/dialogue/README_KO.md) · [대사 v0.3 114개](workstreams/dialogue/BATCH3_V0.3_README_KO.md)
- [대사 v0.4 124개](workstreams/dialogue/BATCH4_V0.4_README_KO.md) · [대사 v0.5 124개](workstreams/dialogue/BATCH5_V0.5_README_KO.md)
- [대사 v0.6 130개](workstreams/dialogue/BATCH6_V0.6_README_KO.md)
- [대사 v0.7 111개](workstreams/dialogue/BATCH7_V0.7_README_KO.md)
- [대사 v0.8 102개](workstreams/dialogue/BATCH8_V0.8_README_KO.md)
- [대사 v0.9 129개](workstreams/dialogue/BATCH9_V0.9_README_KO.md)
- [대사 v0.10 119개](workstreams/dialogue/BATCH10_V0.10_README_KO.md)
- [대사 v0.11 138개](workstreams/dialogue/BATCH11_V0.11_README_KO.md)
- [대사 v0.12 139개](workstreams/dialogue/BATCH12_V0.12_README_KO.md)
- [대사 v0.13 134개](workstreams/dialogue/BATCH13_V0.13_README_KO.md)
- [대사 v0.14 148개](workstreams/dialogue/BATCH14_V0.14_README_KO.md)
- [대사 v0.15 138개](workstreams/dialogue/BATCH15_V0.15_README_KO.md)
- [대사 v0.16 132개](workstreams/dialogue/BATCH16_V0.16_README_KO.md)
- [대사 v0.17 129개](workstreams/dialogue/BATCH17_V0.17_README_KO.md)
- [대사 v0.18 121개](workstreams/dialogue/BATCH18_V0.18_README_KO.md)
- [대사 v0.19 128개](workstreams/dialogue/BATCH19_V0.19_README_KO.md)
- [대사 v0.20 142개](workstreams/dialogue/BATCH20_V0.20_README_KO.md)
- [대사 v0.21 120개](workstreams/dialogue/BATCH21_V0.21_README_KO.md)
- [대사 v0.22 125개](workstreams/dialogue/BATCH22_V0.22_README_KO.md)
- [대사 v0.23 146개](workstreams/dialogue/BATCH23_V0.23_README_KO.md)
- [대사 v0.24 122개](workstreams/dialogue/BATCH24_V0.24_README_KO.md)
- [대사 v0.25 127개](workstreams/dialogue/BATCH25_V0.25_README_KO.md)
- [대사 v0.26 104개](workstreams/dialogue/BATCH26_V0.26_README_KO.md) · [v0.27 109개](workstreams/dialogue/BATCH27_V0.27_README_KO.md)
- [Switch v1.1 → PK `msgev` 엄격 이식 7,025개](workstreams/switch_msgev_v11/README_KO.md)
- [Switch v1.1 → PK `msgev` CJK·kana 정리 20개](workstreams/switch_msgev_v11_cjk_cleanup/README_KO.md)
- [Switch v1.3 재감사 → PK `msgev` 원문 해시 복구 245개](workstreams/switch_msgev_v13_jp_hash_recovery/README_KO.md)
- [Switch v1.1 → PK `msgdata` 엄격 이식 16,176개](workstreams/switch_msgdata_v11/README_KO.md)
- [Switch v1.3 재감사 → PK `msgdata` 형식 복구 145개](workstreams/switch_msgdata_v13_invariant_recovery/README_KO.md)
- [Switch v1.1 → PK `msggame` 엄격 이식 6,018개](workstreams/switch_msggame_v11/README_KO.md)
- [Switch v1.3 → PK `msggame` 형식 복구·사람 검토 831개](workstreams/switch_msggame_v13_invariant_recovery/README_KO.md) · [PK UI 우선 150개](workstreams/msggame_pk_ui_priority_b01/README_KO.md) · [후속 UI 53개](workstreams/msggame_pk_ui_priority_b02/README_KO.md)
- [Switch v1.1 → PK `msgbre` 엄격 이식 1,367개 검증](workstreams/switch_msgbre_v11/switch_v11_msgbre_validation.v0.1.json)
- [Switch v1.3 재감사 → PK `msgbre` CJK 잔존 정리 3개](workstreams/switch_msgbre_v13_cjk_cleanup/README_KO.md)
- [PK 전용 `msgbre` 잔여 11개 완료](workstreams/msgbre_pk_native_completion/README_KO.md)
- [PK 공용 `strdata` 하단 버튼](workstreams/strdata_pk_shared_ui/README_KO.md) · [Switch v1.3 안전 직접이식 24,424개](workstreams/switch_strdata_v13_direct_transfer/README_KO.md)
- [정확한 PK 번역 대상 key 카탈로그](data/public/translation_target_keys.v0.1.json)
- [Switch v1.3 화면 제목 108개 구조 카탈로그](workstreams/switch_title_images_v13_catalog/README_KO.md) · [PC BC3 재구축 코덱 검증](workstreams/pc_g1t_title_codec/README_KO.md) · [108개 PC PK 오프라인 후보 빌드](workstreams/pc_title_images_v13/README_KO.md)
- [서울한강체 v1 PC G1N 로컬 빌드](workstreams/font_seoulhangang_v1/README_KO.md)

## 아직 배포본이 아닌 이유

오프라인 해시와 A/B 결정성 검증은 실제 화면 검수를 대신하지 않는다. 현재 통합 후보에는
다음 작업이 남아 있다.

1. 성 이름·옛 지방명과 장수명 `msgdata` 변경을 하나의 순정 기준 레시피로 병합한다.
2. 장수명·대사 v0.1~v0.27 및 Switch 이식·정리의 `msgev` 변경과 장수 열전 v0.1~v0.11 및 Switch 이식의 `msgbre` 변경을 각 순정
   기준 레시피로 병합한다.
3. PK `msggame` 표시 후보 16,482개를 코드용 문자열과 실제 문장으로 계속 분류하고, 완료 10,352개 뒤의 잔여 6,130개를 병렬 번역한다.
4. PK가 함께 로드하는 `MSG/SC/strdata.bin`의 잔여 2,265개를 문맥 분류·번역하고 최신 서울한강체 후보로 실제 화면을 검증한다.
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
