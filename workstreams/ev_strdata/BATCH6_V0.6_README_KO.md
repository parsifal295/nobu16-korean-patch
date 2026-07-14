# `ev_strdata` 장수명 Batch 6 v0.6

- 리소스: `MSG/SC/ev_strdata.bin`
- 범위: ID `950`–`1149`
- 번역 수: 연속 표시 문자열 `200`개
- 누적 범위: ID `0`–`1149`, `1150`개
- 다음 시작 ID: `1150`
- 현재 상태: 기존 장수명 번역 재사용 초안, 인명·음역·화면 검수 대기

SC·JP·TC의 같은 ID를 정렬했으며 설치본에는 EN `ev_strdata.bin`이 없으므로 TC를 세 번째
참조로 사용했다. 198개는 기존 공개 장수명 오버레이의 SC UTF-16LE SHA-256이 정확히
일치할 때만 재사용했다. ID `1096`과 `1097`은 SC 표기 변형 때문에 기존 해시가 달라서
SC·JP·TC를 별도로 대조해 번역하고 실제 SC 해시에 고정했다. 공개 파일에는 공식 문자열
원문을 기록하지 않는다.

## 배치 산출물

- `public/ev_strdata_ko_officer_names_0950_1149.v0.6.json`
- `evidence/alignment_evidence.v0.6.json`
- `review/review_index.v0.6.json`
- `validation.v0.6.json`
- `build_ev_strdata_batch6.py`
- `tests/test_ev_strdata_batch6.py`
- `BATCH6_V0.6_README_KO.md`

## 재생성

```powershell
python -B workstreams/ev_strdata/build_ev_strdata_batch6.py `
  --game-root .. `
  --out-root workstreams/ev_strdata

python -B -m unittest workstreams.ev_strdata.tests.test_ev_strdata_batch6
```

생성기는 SC·JP·TC 원본의 LZ4 해제와 메시지 표 raw parse→rebuild 바이트 동일성을
검증한다. 패치 후보는 임시 디렉터리의 A/B/final 세 번에만 만들며 설치본 게임 파일,
폰트, 설치기, 실행 파일, 레지스트리와 프로세스 메모리를 수정하지 않는다. printf 토큰,
ESC, 제어문자, 개행, 앞뒤 공백, PUA와 `[token]` 자리표시자의 순서를 보존한다.
