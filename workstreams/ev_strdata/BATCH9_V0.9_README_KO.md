# `ev_strdata` 장수명 Batch 9 v0.9

- 리소스: `MSG/SC/ev_strdata.bin`
- 범위: ID `1550`–`1749`
- 번역 수: 연속 표시 문자열 `200`개
- 누적 범위: ID `0`–`1749`, `1,750`개
- 다음 시작 ID: `1750`
- 현재 상태: 기존 장수명 번역 재사용 초안, 인명·표기·화면 검수 대기

SC·JP·TC의 같은 ID를 정렬했으며 설치본에는 EN `ev_strdata.bin`이 없으므로 TC를 세 번째
참조로 사용한다. 이번 200개는 모두 기존 공개 장수명 오버레이의 SC UTF-16LE SHA-256과
정확히 일치할 때만 번역을 재사용했다. 불일치는 0개다. 공개 파일에는 공식 원문을 기록하지
않는다. 이후 배치에서 불일치가 생기면 SC·JP·TC를 독립 대조하고 실제 SC 해시를 별도로
고정해야만 생성기가 통과한다.

## 배치 산출물

- `public/ev_strdata_ko_officer_names_1550_1749.v0.9.json`
- `evidence/alignment_evidence.v0.9.json`
- `review/review_index.v0.9.json`
- `validation.v0.9.json`
- `build_ev_strdata_batch9.py`
- `tests/test_ev_strdata_batch9.py`
- `BATCH9_V0.9_README_KO.md`

## 재생성

```powershell
python -B workstreams/ev_strdata/build_ev_strdata_batch9.py `
  --game-root .. `
  --out-root workstreams/ev_strdata

python -B -m unittest workstreams.ev_strdata.tests.test_ev_strdata_batch9
```

생성기는 SC·JP·TC 원본의 LZ4 해제와 메시지 표 raw parse→rebuild 바이트 동일성을 검증한다.
패치 후보는 임시 디렉터리의 A/B/final 세 번에만 만들며 설치본 게임 파일, 폰트, 설치기,
실행 파일, 레지스트리와 프로세스 메모리를 수정하지 않는다. printf 토큰, ESC, 제어문자,
개행, 앞뒤 공백, PUA와 `[token]` 자리표시자의 순서도 보존한다.
