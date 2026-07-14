# `ev_strdata` 장수명 Batch 5 v0.5

- 리소스: `MSG/SC/ev_strdata.bin`
- 범위: ID `750`–`949`
- 번역 수: 연속 표시 문자열 `200`개
- 누적 범위: ID `0`–`949`, `950`개
- 다음 시작 ID: `950`
- 현재 상태: 기존 장수명 번역 재사용 초안, 인적·런타임 검수 대기

기존 장수명 source-free 오버레이는 SC UTF-16LE SHA-256이 정확히 일치하는
항목만 재사용한다. 설치본에는 EN 파일이 없으므로 SC·JP·TC의 같은 ID를 정렬하고
TC를 세 번째 참조로 사용한다. 공개 파일에는 공식 문자열 원문을 기록하지 않는다.

## 배치 산출물

- `public/ev_strdata_ko_officer_names_0750_0949.v0.5.json`
- `evidence/alignment_evidence.v0.5.json`
- `review/review_index.v0.5.json`
- `validation.v0.5.json`
- `build_ev_strdata_batch5.py`
- `tests/test_ev_strdata_batch5.py`
- `BATCH5_V0.5_README_KO.md`

## 재생성

```powershell
python -B workstreams/ev_strdata/build_ev_strdata_batch5.py `
  --game-root .. `
  --out-root workstreams/ev_strdata

python -B -m unittest workstreams.ev_strdata.tests.test_ev_strdata_batch5
```

생성기는 SC·JP·TC 원본 LZ4와 메시지 표의 바이트 동일 parse/rebuild를 확인한다.
패치 후보는 임시 디렉터리의 A/B/final에서만 만들며 설치본, 폰트, 설치기, 실행 파일,
레지스트리와 프로세스 메모리를 수정하지 않는다. printf 토큰, ESC, 제어문자,
개행, 앞뒤 공백, PUA와 `[token]` 자리표시자의 순서를 보존한다.
