# `ev_strdata` 역사 사건 번역 Batch 19 v0.19

- 리소스: `MSG/SC/ev_strdata.bin`
- 구조 확인 범위: ID `3662`~`3839`, 총 `178`개
- 실제 표시문 번역: `178`개
- 내부 키·자리표시자·인물 참조·빈 슬롯 제외: `0`개
- 다음 실제 표시 후보: ID `3840`

ID `3662`부터 SC·JP·TC를 같은 번호로 정렬해 모리 다카모토의 교육, 가와고에 야전, 오다 노부나가의 원복, 아시카가 요시테루의 쇼군 취임, 이코마 기쓰노와의 혼인, 나가오 가독 계승, 라이키리마루 전승, 미요시 나가요시의 이반까지 번역했다. ID `3839`에서 미요시 사건이 완결되므로 이 지점을 배치 경계로 삼았다.

이번 범위의 SC·JP·TC 문자열은 모두 실제 표시문이었다. 내부 이벤트 키, 독립 인물 참조, 더미 자리표시자, 빈 슬롯은 발견되지 않았다. v0.13~v0.18에서 제외한 기존 `549`개 ID와 이번 빈 제외 집합의 교집합도 `0`개다. 기존 배치별 제외 수와 ID 해시, 합집합 해시, 교집합 결과는 evidence와 validation에 기록했다.

같은 사건을 담은 기존 `msgev` v0.5·v0.6·v0.7의 소스 비의존 한국어 번역 `178`개를 재사용하고, 설치된 `ev_strdata`의 SC·JP·TC와 전 항목을 다시 정렬·검증했다. ID `3689`, `3694`, `3767`은 `msgev`와 색상 코드 수 또는 순서가 달라 한국어 문장 구조를 `ev_strdata` SC에 맞췄다. 같은 SC 문자열을 쓰는 ID `3794`와 `3837`은 같은 한국어 문장으로 고정했다. 공개 산출물에는 상용 원문을 넣지 않고 숫자 ID, 해시, 문자열 구조 정보만 기록한다.

모든 번역은 색상 코드, 동적 인물 표식, 개행, 앞뒤 공백을 SC 기준과 같은 순서로 보존했다. 화면 길이와 희귀 인명·제도 용어는 실제 게임에서 추가 검수가 필요하므로 review에 런타임 배치 및 용어 검수 표시를 남겼다.

## 배치 산출물

- `public/ev_strdata_ko_historical_events_3662_3839.v0.19.json`
- `evidence/alignment_evidence.v0.19.json`
- `review/review_index.v0.19.json`
- `validation.v0.19.json`
- `build_ev_strdata_batch19.py`
- `tests/test_ev_strdata_batch19.py`
- `BATCH19_V0.19_README_KO.md`

## 재생성

```powershell
python -B workstreams/ev_strdata/build_ev_strdata_batch19.py `
  --game-root .. `
  --out-root workstreams/ev_strdata

python -B -m unittest workstreams.ev_strdata.tests.test_ev_strdata_batch19
```

생성기는 설치된 SC·JP·TC 원본의 고정 해시와 메시지 테이블 재구성 일치 여부를 먼저 확인한다. 이어 오프라인 임시 바이너리를 만들고, 격리 A/B와 최종 실행에서 네 공개 산출물이 바이트 단위로 같은지 검증한다. 설치 파일, 글꼴, 실행 파일, 설치기, 루트 진행 문서는 수정하지 않는다.
