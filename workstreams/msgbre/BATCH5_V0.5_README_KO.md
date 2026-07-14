# msgbre 장수 열전 한국어 배치 5

`MSG_PK/SC/msgbre.bin`의 ID 458~565에 있는 연속 비공백 장수 열전 108개를 한국어 초벌 번역한 source-free 배치다. ID 540~565의 오다 가문 항목을 끝까지 포함하며, 마지막 항목은 오다 요리나가이고 다음 ID 566은 오치 이에마스로 시작한다.

## 공개 산출물

- `public/msgbre_ko_biographies_0458_0565.v0.5.json`: 숫자 ID, SC UTF-16LE SHA-256, 한국어만 수록
- `evidence/alignment_evidence.v0.5.json`: SC·JP·EN 동일 ID의 해시와 구조 정보
- `review/review_index.v0.5.json`: 항목별 초벌 검수 상태와 주의 표식
- `validation.v0.5.json`: 원문 비포함, 보존 규칙, 결정성, 안전성 검증 결과
- `build_msgbre_batch5.py`: 결정적 산출물 생성기
- `tests/test_msgbre_batch5.py`: 범위·해시·source-free·이전 배치 불변·A/B/최종 생성을 검증하는 테스트

공식 SC·JP·EN 문장과 완성 게임 리소스는 포함하지 않는다. 108개 번역은 모두 사람 검수와 게임 화면 검수가 필요한 초벌 번역이다.

| 산출물 | SHA-256 |
|---|---|
| 오버레이 | `941D6B235708E4E8247CD0E4508DBDADBBA5D46A6A7F5406F047C4187B19A8F0` |
| 정렬 근거 | `149CCA5AC5B421870318CBA08954F1059ED0B6991C8DDE8381276279571FE3E3` |
| 검수 색인 | `B2371FD63BE2749B0F39D5362D167C3B13846DB93BC6B4F19639D7F183D319B8` |
| 생성 검증 | `23FAD627AB732D65F31099F5A32E5ED349CA659B6E965AACE536878E624EA0A3` |

## 검증 결과

- 선택 범위 108개는 SC·JP·EN에서 모두 비공백이며 각 언어 문자열 수는 3,000개다.
- 제어 코드, 개행 순서, 앞뒤 공백, `printf` 토큰, 해석되지 않은 `%`, 사설 영역 코드포인트, 대괄호 자리표시자를 SC 기준으로 보존했다.
- 공개 JSON의 한자·가나 원문 누출은 0건이다.
- 격리 A/B 생성물과 체크인한 최종 생성물은 바이트 단위로 같다.
- 기존 v0.1~v0.4 산출물 16개는 SHA-256이 바뀌지 않았다.
- 전체 `msgbre` 회귀 테스트 32개가 통과했다.
- 설치본 `MSG_PK/{SC,JP,EN}/msgbre.bin`, 폰트, 설치기, 루트 README, 공통 빌더, 다른 작업 스트림은 수정하지 않았다.
- 성명·성곽·전투·관직·다도 용어 29개 항목에는 후속 용어집 검수 표식을 남겼다.

```powershell
python -B workstreams/msgbre/build_msgbre_batch5.py --out-root workstreams/msgbre
python -B -m unittest discover -s workstreams/msgbre/tests -p "test_*.py"
```

다음 번역 배치는 ID 566부터 시작한다.
