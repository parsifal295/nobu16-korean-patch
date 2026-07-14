# `ev_strdata` 인물 표기·역사 사건 서술 Batch 16 v0.16

- 리소스: `MSG/SC/ev_strdata.bin`
- 구조 검사 범위: ID `3007`~`3276`, 총 `270`개
- 실제 번역: `174`개
- 구성: 인물명 `97`개, 지명 `1`개, 범용 화자 `1`개, 역사 사건 서술 `75`개
- 번역 제외: 더미 `94`개, 런타임 인물 참조 `1`개, 빈 슬롯 `1`개
- v0.15 제외 목록과 중복: `0`개
- 다음 실제 표시 후보: ID `3277`

ID `3007`부터 SC·JP·TC를 같은 번호로 정렬해 인물의 본명·통칭·법명과 사건 서술을 번역했다. 먼저 ID `3007`~`3117`의 실제 인물·화자·지명 표기 99개를 처리했다. 뒤이어 반복 더미 구간을 건너뛴 뒤 ID `3202`~`3276`의 고소슨 삼국 동맹, 이쓰쿠시마 전투, 가네가사키 퇴각, 히에이산 소각, 미카타가하라 전투 서술 75개를 사건 경계에 맞춰 처리했다.

ID `3105`~`3201` 사이의 더미·배우 참조·빈 문자열은 화면용 번역 대상이 아니므로 overlay에서 제외했다. 정확한 ID 집합과 SC·JP·TC 원본 해시는 evidence와 validation에 기록했다. v0.15에서 제외한 43개 ID와 이번 제외 96개 ID의 교집합도 계산해 중복이 없음을 고정했다.

반복되는 원문 8개 그룹은 반드시 같은 한국어를 쓰도록 검증한다. 희귀 인명·법명 독음 6개에는 `rare_person_or_alias_reading` 플래그를, 역사 사건 서술 75개에는 `historical_narration_runtime_layout` 플래그를 남겼다. 번역은 제어코드와 개행 구조를 보존했지만 실제 게임의 글상자 폭과 장면 흐름은 추후 런타임 검수가 필요하다.

설치본에는 EN `ev_strdata.bin`이 없으므로 세 번째 대조 언어로 TC를 사용했다. 공개 산출물에는 상용 원문을 넣지 않고 ID, 해시, 문자열 구조, 한국어만 기록한다.

## 배치 산출물

- `public/ev_strdata_ko_labels_and_narration_3007_3276.v0.16.json`
- `evidence/alignment_evidence.v0.16.json`
- `review/review_index.v0.16.json`
- `validation.v0.16.json`
- `build_ev_strdata_batch16.py`
- `tests/test_ev_strdata_batch16.py`
- `BATCH16_V0.16_README_KO.md`

## 재생성

```powershell
python -B workstreams/ev_strdata/build_ev_strdata_batch16.py `
  --game-root .. `
  --out-root workstreams/ev_strdata

python -B -m unittest workstreams.ev_strdata.tests.test_ev_strdata_batch16
```

생성기는 SC·JP·TC 설치 원본의 고정 해시와 LZ4 해제 후 raw 메시지 테이블의 parse/rebuild 바이트 동일성을 검사한다. offline 패치 바이너리는 임시 디렉터리에만 만들며, 격리 A/B와 최종 실행의 공개 산출물이 바이트 단위로 같은지 확인한다. 설치 파일, 폰트, 실행 파일, 레지스트리, 프로세스 메모리는 수정하지 않는다.
