# `ev_strdata` 이벤트 라벨 Batch 14 v0.14

- 리소스: `MSG/SC/ev_strdata.bin`
- 번역 범위: ID `2407`~`2580`, 총 `174`개
- 구성: 지역 국인중 두령 `171`개, 후마 일당 두령 `1`개, 수군 두령 `2`개
- 다음 placeholder: ID `2581`~`2779`, `199`개
- 다음 실제 표시 후보: ID `2780`

로컬에서 대조한 초벌 174개를 SC·JP·TC 같은 ID와 다시 맞춰 사용했다. ID `2450`은 프로젝트의 기존 지명 표기와 맞지 않는 명백한 독음 오타 한 건만 `가와치중 두령`으로 교정했다. 희귀 지명 독음 20개는 번역을 유지하되 review에 `rare_place_reading` flag를 남겼다. 이 배치로 ID `2400`~`2580`의 지역 국인중·후마·수군 두령 라벨 구간이 끝난다.

뒤따르는 ID `2581`~`2779`는 SC·JP·TC에서 각각 같은 해시가 199회 반복되는 내부 placeholder다. 공개 overlay와 번역 진행률에서 제외하고 evidence/review에 deferred 범위로만 기록했다. 설치본에는 EN `ev_strdata.bin`이 없어 TC를 세 번째 참조로 사용한다. 공식 원문은 공개 파일에 싣지 않는다.

## 배치 산출물

- `public/ev_strdata_ko_event_labels_2407_2580.v0.14.json`
- `evidence/alignment_evidence.v0.14.json`
- `review/review_index.v0.14.json`
- `validation.v0.14.json`
- `build_ev_strdata_batch14.py`
- `tests/test_ev_strdata_batch14.py`
- `BATCH14_V0.14_README_KO.md`

## 재생성

```powershell
python -B workstreams/ev_strdata/build_ev_strdata_batch14.py `
  --game-root .. `
  --out-root workstreams/ev_strdata

python -B -m unittest workstreams.ev_strdata.tests.test_ev_strdata_batch14
```

생성기는 174개 SC 원문 해시와 전체 SC·JP·TC 정렬 해시를 고정한다. 세 언어의 LZ4 해제와 raw parse/rebuild 바이트 동일성을 검증하고, 격리 A/B와 최종 실행에서 source-free 산출물 재현성을 확인한다. offline 출력만 만들며 설치본·폰트·설치기·실행 파일·레지스트리·프로세스 메모리를 수정하지 않는다. printf, ESC, 제어문자, 개행, PUA, `[token]` 구조도 전 항목 검증한다.
