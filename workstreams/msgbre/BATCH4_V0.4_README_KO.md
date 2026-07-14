# msgbre 장수 열전 한글화 배치 4

`MSG_PK/SC/msgbre.bin` ID 351~457의 연속 비공백 장수 열전 107개를 한글 초벌 번역한 소스 비포함 배치다. 기존 공개 장수명 오버레이와 동일 ID를 교차 확인했고, ID 447~457의 오타 가문 항목을 모두 포함해 성씨 묶음이 끝나는 곳에서 닫았다. 다음 ID 458은 오타카 가문으로 시작한다.

## 공개 산출물

- `public/msgbre_ko_biographies_0351_0457.v0.4.json`: 각 항목에 ID, SC UTF-16LE SHA-256, 한국어만 수록
- `evidence/alignment_evidence.v0.4.json`: SC·JP·EN 동일 ID의 해시와 구조 정보
- `review/review_index.v0.4.json`: 항목별 초벌 검수 상태와 주의 표식
- `validation.v0.4.json`: 소스 핀, 보존 규칙, 원문 누출, 결정성, 안전성 결과
- `build_msgbre_batch4.py`: 결정적 생성기
- `tests/test_msgbre_batch4.py`: 산출물·이전 세 배치 불변성·격리 A/B/최종 생성을 검증하는 테스트

공식 SC·JP·EN 문장과 완성 게임 리소스는 포함하지 않는다. 107개 모두 사람 검수와 게임 화면 검수가 필요한 초벌 번역이다.

| 산출물 | SHA-256 |
|---|---|
| 오버레이 | `30E38BE8C8F0D0E48FAFB828A88765AFF52BF607F1D8D22985E88CD0B810109E` |
| 정렬 근거 | `9343B6EF3978356E33ABFB17FED9C7C36F5903CDF2F31FDA197158554CAE0513` |
| 검수 색인 | `2530714A9AACBFEF30B39F2E0F83430B22D3DAC263636A52A5CF16BB1F585C54` |
| 생성 검증 | `F5CB3B62A9E96912E80DA7A683D749ECDD8924C5554F102F27E37D89A2281DDD` |

## 검증 결과

- 선택 범위 107개가 SC·JP·EN에서 모두 비공백이며 각 언어 슬롯 수는 3,000개다.
- 제어 코드, 개행, 앞뒤 공백, `printf` 토큰, 해석되지 않은 `%`, 사설 영역 코드포인트, 대괄호 자리표시자를 SC 기준으로 보존했다.
- 공개 JSON의 한자·가나 원문 누출은 0이다.
- 격리 A/B와 체크인된 최종 생성의 네 산출물은 모두 바이트 단위로 같다.
- 기존 v0.1·v0.2·v0.3 산출물 12개 파일의 SHA-256은 변하지 않았다.
- 게임 파일, 폰트, 설치기, 루트 README, 진행률, 공통 빌더 및 다른 작업선은 수정하지 않았다.

```powershell
python -B workstreams/msgbre/build_msgbre_batch4.py --out-root workstreams/msgbre
python -B -m unittest workstreams/msgbre/tests/test_msgbre_batch4.py
```

다음 배치는 ID 458부터 시작한다.
