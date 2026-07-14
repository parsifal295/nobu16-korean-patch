# `ev_strdata` 인물·화자 표기 Batch 15 v0.15

- 리소스: `MSG/SC/ev_strdata.bin`
- 번역 범위: ID `2780`~`2971`에서 실제 표시 문자열 `184`개
- 구성: 실명·고유 인물 표기 `121`개, 범용 화자·직책 표기 `63`개
- 구조 검사 범위: ID `2780`~`3006`, 총 `227`개
- 번역 제외: 런타임 인물 참조·더미·내부 역할 키 `43`개
- 다음 실제 표시 후보: ID `3007`

SC·JP·TC의 같은 ID를 대조해 이벤트 인물명과 범용 화자명을 번역했다. 번역 구간 안에 섞여 있는 `[b...]` 계열 런타임 인물 참조 8개는 화면에 그대로 노출할 문장이 아니므로 overlay에 넣지 않았다. 이어지는 참조 26개, 더미 2개, 내부 역할 키 7개도 같은 원칙으로 제외했다. 이 43개는 번역 완료 수에 포함하지 않으며, 정확한 ID 집합과 원본 해시만 evidence와 validation에 기록했다.

같은 원문이 반복되는 세 그룹은 같은 한국어를 사용하도록 검증한다. 희귀 인명 독음 8개에는 `rare_person_reading` 검수 플래그를 남겼다. 현재 번역은 런타임 검수 전 초안이며, 실제 게임에서 폭·맥락·호칭을 확인한 뒤 교정할 수 있다.

설치본에는 EN `ev_strdata.bin`이 없으므로 세 번째 대조 언어로 TC를 사용했다. 배포 산출물에는 상용 원문을 넣지 않고 ID, 원본 해시, 문자열 구조, 한국어만 기록한다.

## 배치 산출물

- `public/ev_strdata_ko_event_labels_2780_2971.v0.15.json`
- `evidence/alignment_evidence.v0.15.json`
- `review/review_index.v0.15.json`
- `validation.v0.15.json`
- `build_ev_strdata_batch15.py`
- `tests/test_ev_strdata_batch15.py`
- `BATCH15_V0.15_README_KO.md`

## 재생성

```powershell
python -B workstreams/ev_strdata/build_ev_strdata_batch15.py `
  --game-root .. `
  --out-root workstreams/ev_strdata

python -B -m unittest workstreams.ev_strdata.tests.test_ev_strdata_batch15
```

생성기는 설치된 SC·JP·TC 원본의 고정 해시를 확인하고, LZ4 해제 뒤 raw 메시지 테이블의 parse/rebuild 바이트 동일성을 검증한다. 이어서 offline 패치 바이너리를 임시 디렉터리에만 만들고 격리 A/B와 최종 실행의 산출물이 바이트 단위로 같은지 확인한다. 설치 파일, 폰트, 실행 파일, 레지스트리, 프로세스 메모리는 수정하지 않는다.
