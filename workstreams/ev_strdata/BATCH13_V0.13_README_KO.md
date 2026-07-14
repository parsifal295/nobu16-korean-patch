# `ev_strdata` 이벤트 라벨 Batch 13 v0.13

- 리소스: `MSG/SC/ev_strdata.bin`
- 조사 범위: ID `2207`~`2406`, 총 `200`개
- 번역: ID `2400`~`2406`, 화면 표시용 지역 국인중 두령 라벨 `7`개
- 보류: ID `2207`~`2399`, 반복 내부 placeholder `193`개
- 다음 시작 ID: `2407`

장수명 구간이 끝난 뒤 ID `2207`~`2399`는 SC·JP·TC 모두에서 동일하게 반복되는 내부 placeholder다. 화면 표시 번역 대상이 아니므로 공개 overlay와 번역 진행률에서 제외하고 evidence/review에 `deferred/code_placeholder` 범위로만 기록했다. ID `2400`~`2406`은 세 언어의 같은 ID를 대조해 실제 표시용 지역 국인중 두령 라벨로 분류했고, SC UTF-16LE SHA-256을 고정한 뒤 한국어 7개를 넣었다. 설치본에는 EN `ev_strdata.bin`이 없어 TC를 세 번째 참조로 사용한다.

추가로 ID `2207`~`3200`의 구조를 분석했다. source-free 분류 결과는 `code_placeholder` 488개, `regional_group_leader_label` 178개, `other_display_candidate` 328개다. 원문은 공개 파일에 싣지 않고 구간·개수·해시·제어 구조만 남긴다.

## 배치 산출물

- `public/ev_strdata_ko_event_labels_2207_2406.v0.13.json`
- `evidence/alignment_evidence.v0.13.json`
- `review/review_index.v0.13.json`
- `validation.v0.13.json`
- `build_ev_strdata_batch13.py`
- `tests/test_ev_strdata_batch13.py`
- `BATCH13_V0.13_README_KO.md`

## 재생성

```powershell
python -B workstreams/ev_strdata/build_ev_strdata_batch13.py `
  --game-root .. `
  --out-root workstreams/ev_strdata

python -B -m unittest workstreams.ev_strdata.tests.test_ev_strdata_batch13
```

생성기는 SC·JP·TC 원본의 LZ4 해제와 raw parse/rebuild 바이트 동일성을 먼저 검증한다. 이어 source-free 공개 산출물을 격리 A/B와 최종 실행에서 재현하고, offline 출력만 만들어 설치본·폰트·설치기·실행 파일·레지스트리·프로세스 메모리를 수정하지 않는다. printf, ESC, 제어문자, 개행, PUA, `[token]` 구조도 번역 7개 전부 검증한다.
