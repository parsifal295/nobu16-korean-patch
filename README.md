# 신생 한글화 — NOBU16 Korean Patch

`NOBUNAGA'S AMBITION: Awakening with Power Up Kit`(신생 PK)의 한국어 패치를
만드는 비공식 개발 프로젝트다. 번역을 작은 ID 배치로 나눠 병렬로 진행하고, 원문 해시·
제어코드·필요 글리프를 자동 검증해 **번역 속도와 배포 안전성**을 함께 확보하는 것이
목표다.

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

설계 원칙은 [파일 전용 아키텍처](docs/ARCHITECTURE_FILE_ONLY.md)와
[배포 정책](docs/DISTRIBUTION_POLICY.md)에 정리되어 있다.

## 지금까지 된 것

| 작업선 | 현재 결과 | 남은 게이트 |
|---|---|---|
| 장수명 | 2,207개 합성명과 보수적으로 확정한 분리 슬롯을 포함한 4리소스 RC. `오다 노부나가` 등 실제 화면 표시, 적용·복원 검증 완료 | 전체 인명 표기의 사람 전수 교정 |
| MSGUI v0.2 | 5,100개 ID 분류 완료. 번역·검수 4,037개, 실제 교체 3,922개, 일반 SC 비공백 미번역 0개 | 새로 활성화한 SC 공백 슬롯 86개의 화면·전투 문맥 QA |
| 성·거점 이름 v0.1 | ID 9151–9542, 392개 source-free 한글 초벌과 A/B 결정성 검증 완료 | 공식 EN 로마자 기반 초벌의 사람 교정, 장수명 `msgdata`와 병합, 실제 지도 QA |
| 이벤트 대사 v0.1 | ID 3202–3229, 28개 초벌. 제어코드·개행 보존과 A/B 빌드 검증 완료 | 문체·고유명·실제 대화창 QA |
| 이벤트 대사 v0.2 | ID 3230–3308, 후속 79개 초벌. 5개 사건, 3언어 해시 237개와 형식 불변조건 검증 완료 | 사람 검수 후 다음 글꼴·통합 배포본에 편입 |
| Font-v6 | MSGUI v0.2 + 장수명 + 대사 v0.1 28개 + 성 이름 392개의 700자 수요를 오프라인 A/B 빌드와 공개 레시피 재생으로 검증 | 런타임 화면·종료 QA. 대사 v0.2 79개는 아직 미포함 |

세부 근거와 재현 절차:

- [장수명](workstreams/officer_names/README_KO.md)
- [전체 UI](workstreams/msgui_full/README.md)
- [성 이름 392개](workstreams/castle_names/README_KO.md)
- [대사 28개 + 79개](workstreams/dialogue/README_KO.md)
- [Font-v6](workstreams/font_v6/README_KO.md)

## 아직 배포본이 아닌 이유

오프라인 해시와 A/B 결정성 검증은 실제 화면 검수를 대신하지 않는다. 현재 통합 후보에는
다음 작업이 남아 있다.

1. 성 이름과 장수명 `msgdata` 변경을 하나의 순정 기준 레시피로 병합한다.
2. 장수명·대사 v0.1·대사 v0.2의 `msgev` 변경도 ID 오름차순으로 다시 병합한다.
3. 후속 대사 79개의 새 한글 수요를 다음 글꼴 리비전에 넣고 네 글꼴 표 누락 0개를
   재검증한다.
4. MSGUI v0.2, 메시지 병합본, 새 글꼴을 다중 파일 설치·복원 거래로 조립한다.
5. 대표 메뉴·장수명·대화창·지도에서 누락 글리프, 잘림, 겹침, 정상 종료와 완전 복원을
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

자세한 재현 기록은 [`ERROR:-9001` 작업 폴더 보고서](reports/error_9001_working_directory_2026-07-14.md)와
[성 이름 배치 조사](reports/castle_name_layout_file_only_probe_2026-07-14.md)에 있다.

## 가장 빠르게 기여하는 법

큰 파일 하나를 오래 붙잡기보다, 검토 가능한 작은 배치를 끝내는 기여를 권장한다.

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
| `docs/` | 아키텍처와 저장소·배포 정책 |
| `reports/` | 정적 분석, 런타임 QA, 실패 재현 기록 |
| `vendor/noto/` | 고정 Noto KR 입력과 SIL OFL 라이선스 |

`tmp/`, `backups/`, Ghidra 프로젝트, 추출 원문, 완성 `msg*.bin`, `res_lang.bin`, G1N/G1T,
로컬 빌드 후보는 공개 추적 대상이 아니다.

## 공개·배포 원칙

이 저장소는 게임 파일 저장소가 아니라 **재현 가능한 패치 소스**다.

- 공개 패키지는 프로젝트 소유 번역, 구조 레시피, 델타/글리프 픽셀, 해시, 검증기와
  라이선스만 포함한다.
- 전체 순정·수정 게임 리소스, 실행 파일, 추출 원문, 중첩 archive는 배포하지 않는다.
- Python, Ghidra, 폰트 도구와 Noto 원본 폰트는 개발 단계 입력이다. 최종 사용자용
  설치·검증·복원은 별도 Python이나 Ghidra를 요구하지 않는 것을 목표로 한다.
- 설치기는 게임과 런처가 실행 중이면 중단하고, 미지원·혼합 해시 상태를 임의로 덮어쓰지
  않아야 한다.

공개 기여 전에는 [저장소 정책](docs/REPOSITORY_POLICY.md)을 읽고 `git status --ignored`로
상용 원문·전체 리소스·로컬 백업이 staged되지 않았는지 확인한다.
