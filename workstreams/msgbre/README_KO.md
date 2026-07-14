# msgbre 장수 열전 한글화 배치 1

`MSG_PK/SC/msgbre.bin`의 장수 열전 가운데 ID 0~128에 해당하는 비공백 항목 129개를 한글 초벌 번역한 작업선이다. 같은 ID의 SC·JP·EN 리소스를 기존 공통 메시지 파서로 정렬해 의미를 교차 확인했다. 아마고 계열 항목 묶음이 끝나는 ID 128에서 배치를 닫았으며 다음 시작점은 ID 129다.

## 공개 범위

- 오버레이 항목에는 `id`, SC 원문의 UTF-16LE SHA-256, 프로젝트가 작성한 한국어만 들어간다.
- 공식 SC·JP·EN 문장은 저장소 산출물에 넣지 않는다.
- 전체 게임 리소스나 재배포 가능한 원본 바이너리는 포함하지 않는다.
- 129개 전부 초벌 번역 상태이며 사람 검수와 게임 화면 검수는 아직 필요하다.

## 산출물

- `public/msgbre_ko_biographies_0000_0128.v0.1.json`: 소스 비포함 한국어 오버레이
- `evidence/alignment_evidence.v0.1.json`: SC·JP·EN 동일 ID의 해시·구조 근거
- `review/review_index.v0.1.json`: 항목별 검수 상태와 주의 표식
- `validation.v0.1.json`: 보존 규칙·원문 누출·재현성·안전성 검증 기록
- `build_msgbre_batch1.py`: 고정 소스 핀을 사용하는 결정적 생성기
- `tests/test_msgbre_batch1.py`: 공개 산출물과 격리 A/B 생성을 검사하는 단위 테스트

최종 산출물 SHA-256은 다음과 같다.

| 산출물 | SHA-256 |
|---|---|
| 오버레이 | `DDD87FDF972F4EE907D310387074D0879E620C61B15C26B7F8A7FBA40BE52E00` |
| 정렬 근거 | `1E6AE3EC563338F371CA0C4E02DEB6B6EC3AA78DF5AAC7E4446174F6C1E052F6` |
| 검수 색인 | `8D5003CAFDF9BCCC460A52B2125B549C8B9EE6CE31B4203D56D49F6855E45438` |
| 생성 검증 | `FE86E50A1F006DA4773862E2923AF78DDF3521D5C73E1153EE8E0A0586A70812` |

## 생성과 검증

게임 설치 루트를 기준으로 고정된 순정 SC·JP·EN 리소스가 있을 때 다음과 같이 다시 만든다.

```powershell
python -B workstreams/msgbre/build_msgbre_batch1.py --out-root workstreams/msgbre
python -B -m unittest workstreams.msgbre.tests.test_msgbre_batch1
```

생성기는 세 언어 모두 3,000개 슬롯인지, 선택한 129개가 모두 비어 있지 않은지, 파싱 후 무변경 재구성이 원본과 바이트 단위로 같은지 확인한다. 한국어 교체문은 다음 요소를 SC 기준으로 보존한다.

- 제어 코드와 이스케이프 시퀀스 순서
- 개행 순서
- 앞뒤 공백
- `printf` 토큰과 해석되지 않은 `%`
- 사설 영역 코드포인트
- 대괄호 자리표시자 순서

공개 JSON 전체에서 한자·가나 누출이 0인지 검사하며, 격리된 A/B 생성과 최종 생성 결과 네 파일이 모두 바이트 단위로 같음을 확인했다. 생성 과정은 게임 파일, 폰트, 설치기, 루트 README 및 다른 작업선을 수정하지 않는다.

## 다음 작업

다음 번역 배치는 ID 129부터 시작한다. 현재 배치의 고유명사·유파·관직 표기는 `review_index.v0.1.json`의 주의 표식을 우선 검수한다.
