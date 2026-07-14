# msgbre 장수 열전 한글화 배치 3

`MSG_PK/SC/msgbre.bin` ID 251~350의 연속 비공백 장수 열전 100개를 한글 초벌 번역한 소스 비포함 배치다. ID 345~350의 우지이에 가문 항목을 모두 포함해 성씨 묶음이 끝나는 곳에서 닫았으며 다음 시작점은 ID 351이다.

## 공개 산출물

- `public/msgbre_ko_biographies_0251_0350.v0.3.json`: 각 항목에 ID, SC UTF-16LE SHA-256, 한국어만 수록
- `evidence/alignment_evidence.v0.3.json`: SC·JP·EN 동일 ID의 해시와 구조 정보
- `review/review_index.v0.3.json`: 항목별 초벌 검수 상태와 주의 표식
- `validation.v0.3.json`: 소스 핀, 보존 규칙, 원문 누출, 결정성, 안전성 결과
- `build_msgbre_batch3.py`: 결정적 생성기
- `tests/test_msgbre_batch3.py`: 산출물·이전 배치 불변성·격리 A/B 생성을 검증하는 테스트

공식 SC·JP·EN 문장과 완성 게임 리소스는 포함하지 않는다. 100개 모두 사람 검수와 게임 화면 검수가 필요한 초벌 번역이다.

| 산출물 | SHA-256 |
|---|---|
| 오버레이 | `1253609BC246DB4A63D1A5658476756AB89A0660FA683262CFFA444E3678132B` |
| 정렬 근거 | `1AEEBEB457679CC12A01310D80EB405C6B296726330833DEA36EAB5391F88985` |
| 검수 색인 | `D1DE1B7F08E6EA7AE9B12058813EEA7C65CE4A872E9F6B1257BD7D7DE83FBACD` |
| 생성 검증 | `AD4949BAE85C21071E642234580183497FE75BED63BA818FF29B9944FDCEFE49` |

## 검증 결과

- 선택 범위 100개가 SC·JP·EN에서 모두 비공백이며 각 언어 슬롯 수는 3,000개다.
- 제어 코드, 개행, 앞뒤 공백, `printf` 토큰, 해석되지 않은 `%`, 사설 영역 코드포인트, 대괄호 자리표시자를 SC 기준으로 보존했다.
- 공개 JSON의 한자·가나 원문 누출은 0이다.
- 격리 A/B와 최종 생성의 네 산출물은 모두 바이트 단위로 같다.
- 이전 v0.1·v0.2 산출물 여덟 파일의 SHA-256은 변하지 않았다.
- 게임 파일, 폰트, 설치기, 루트 README, 진행률, 공통 빌더 및 다른 작업선은 수정하지 않았다.

```powershell
python -B workstreams/msgbre/build_msgbre_batch3.py --out-root workstreams/msgbre
python -B -m unittest workstreams/msgbre/tests/test_msgbre_batch3.py
```

다음 배치는 ID 351부터 시작한다.
