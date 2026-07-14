# `MSG/SC/ev_strdata.bin` 한글화

## Batch 1 범위

- 리소스: `MSG/SC/ev_strdata.bin`
- 범위: ID `0`–`149`
- 번역 수: 표시 문자열 `150`개
- 내용: 파일 선두의 장수 전체 이름표
- 다음 시작 ID: `150`
- 전체 슬롯: `17,868`
- SC 표시 번역 대상: `11,687`

파일 선두는 사건 대사가 아니라 장수 전체 이름표이며, 이 기능 구간은 150개를
넘어서 계속된다. Batch 1은 요청된 배치 상한인 150개에서 끊었다. 번역은 기존
장수명 오버레이와 SC UTF-16LE 해시가 정확히 일치한 항목만 재사용했다.

## 언어 정렬

설치본 `MSG` 트리에는 `SC`, `JP`, `TC`만 있고 `EN/ev_strdata.bin`은 없다.
따라서 같은 `17,868`개 ID를 가진 SC·JP·TC를 정렬했고, TC를 EN 대신 세 번째
참조로 사용했다. 공개 증거에는 공식 문자열을 넣지 않고 ID, UTF-16LE SHA-256,
구조 서명만 기록한다.

## 산출물

- `public/ev_strdata_ko_officer_names_0000_0149.v0.1.json`: source-free 번역 오버레이
- `evidence/alignment_evidence.v0.1.json`: SC·JP·TC ID 정렬과 구조 증거
- `review/review_index.v0.1.json`: 150개 항목의 인적·런타임 검수 상태
- `validation.v0.1.json`: 원본 핀, A/B 결정성, 불변 조건, 안전성 결과
- `build_ev_strdata_batch1.py`: 결정적 생성 및 오프라인 바이너리 빌드 검증기
- `tests/test_ev_strdata_batch1.py`: 공개 산출물과 설치본 불변 회귀 테스트

## 재생성 및 검증

프로젝트 루트에서 다음을 실행한다.

```powershell
python -B workstreams/ev_strdata/build_ev_strdata_batch1.py `
  --game-root .. `
  --out-root workstreams/ev_strdata

python -B -m unittest workstreams/ev_strdata/tests/test_ev_strdata_batch1.py
```

생성기는 설치본을 읽기만 한다. 패치 후보 바이너리·manifest·recipe는 임시
디렉터리에 세 번(A/B/final) 만들어 바이트 동일성을 확인한 뒤 폐기한다.
게임 설치 파일, 폰트, 설치기, 실행 파일, 레지스트리, 프로세스 메모리는 수정하지
않는다.

## 보존 조건

각 교체 문자열은 원본과 다음 구조가 같아야 한다.

- printf 토큰과 알 수 없는 `%` 개수
- ESC 순서와 기타 제어문자
- 개행 순서와 앞뒤 공백
- PUA 코드포인트
- `[token]` 형태 자리표시자 순서

현재 150개는 이름 문자열이라 해당 특수 구조가 없지만, 동일 검사를 일반화해
다음 배치에도 그대로 적용한다. 번역은 런타임 검수 전 초안 상태다.
