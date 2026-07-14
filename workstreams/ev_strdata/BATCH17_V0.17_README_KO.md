# `ev_strdata` 사건·엔딩 번역 Batch 17 v0.17

- 리소스: `MSG/SC/ev_strdata.bin`
- 구조 확인 범위: ID `3277`~`3484`, 총 `208`개
- 실제 표시문 번역: `190`개
- 내부 이벤트 키 제외: `18`개
- 다음 실제 표시 후보: ID `3485`

ID `3277`부터 SC·JP·TC를 같은 번호로 정렬해 하비에르의 일본 상륙, 기후와 천하포무, 지방 통일 엔딩, 조정 관직 선택, 전국 통일 뒤의 여러 결말, 쇼군의 교토 귀환 시도, 오다 노부카쓰 최후 사건까지 번역했다. ID `3484`에서 마지막 사건이 완결되므로 이 지점을 배치 경계로 삼았다.

번역 구성은 지방 통일 엔딩 `27`개, 조정 관직 대화 `31`개, 전국 통일 엔딩 `56`개, 역사 사건 대화·서술 `76`개다. 제어 색상, 동적 인물·가문 표식, 개행, 앞뒤 공백은 SC 원문 구조와 같은 순서로 보존했다. 같은 SC 원문이 반복되는 두 묶음은 동일한 한글 문장을 사용한다.

ID `3309`~`3350` 사이의 영문 이벤트 조회 키 `18`개는 화면 표시문이 아니므로 번역 수와 오버레이에서 제외했다. v0.13~v0.16에서 제외한 기존 `531`개 ID와 이번 제외 목록의 교집합은 `0`개다. 각 배치별 제외 수와 ID 해시, 합집합 해시, 교집합 결과는 evidence와 validation에 기록했다.

공개 산출물에는 상용 원문을 넣지 않는다. 원문 대응은 숫자 ID, 해시, 문자열 구조 정보만으로 검증한다. 한글 문장은 아직 실제 게임 화면에서 길이와 문맥을 검수하지 않았으므로 전 항목에 런타임 배치 검수 표시를 남겼다.

## 배치 산출물

- `public/ev_strdata_ko_events_and_endings_3277_3484.v0.17.json`
- `evidence/alignment_evidence.v0.17.json`
- `review/review_index.v0.17.json`
- `validation.v0.17.json`
- `build_ev_strdata_batch17.py`
- `tests/test_ev_strdata_batch17.py`
- `BATCH17_V0.17_README_KO.md`

## 재생성

```powershell
python -B workstreams/ev_strdata/build_ev_strdata_batch17.py `
  --game-root .. `
  --out-root workstreams/ev_strdata

python -B -m unittest workstreams.ev_strdata.tests.test_ev_strdata_batch17
```

생성기는 설치된 SC·JP·TC 원본의 고정 해시와 메시지 테이블 재구성 일치 여부를 먼저 확인한다. 그 뒤 오프라인 임시 바이너리를 만들고, 격리 A/B와 최종 실행에서 네 공개 산출물이 바이트 단위로 같은지 검증한다. 설치 파일, 글꼴, 실행 파일, 설치기, 루트 진행 문서는 수정하지 않는다.
