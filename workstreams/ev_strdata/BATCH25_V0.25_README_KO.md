# `ev_strdata` 역사 사건 번역 Batch 25 v0.25

- 리소스: `MSG/SC/ev_strdata.bin`
- 구조 확인 범위: ID `4751`~`4838`, 총 `88`개
- 실제 표시문 번역: `88`개
- 내부 키·자리표시자·인물 참조·빈 슬롯 제외: `0`개
- 다음 실제 표시 후보: ID `4839`

ID `4751`부터 SC·JP·TC를 같은 번호로 정렬해 가게토라의 간토 간레이 취임과 마사토라 개명, 미키·아네가코지 가문의 주나곤 자칭, 네네와 하시바 가문의 일화 및 구로다 조스이 서술, 마쓰다이라 독립과 기요스 동맹까지 번역했다. ID `4838`은 노부나가와의 협력 서술을 마무리하며, ID `4839`부터 오토모 요시시게의 새 사건이 시작되므로 이 지점을 배치 경계로 삼았다.

기존 `msgev` v0.14의 원문 없는 한국어 초안 88개를 재사용하되, 설치된 `ev_strdata` SC를 권위 기준으로 하여 ESC 색상·이름 표식, 대괄호 인물 자리표시자, 줄바꿈, 앞뒤 공백을 다시 검증했다. SC·JP·TC 세 언어 모두 이 범위에서 실제 표시문이며 내부 키·더미·독립 인물 참조·빈 슬롯은 없다.

## 배치 산출물

- `public/ev_strdata_ko_historical_events_4751_4838.v0.25.json`
- `evidence/alignment_evidence.v0.25.json`
- `review/review_index.v0.25.json`
- `validation.v0.25.json`
- `build_ev_strdata_batch25.py`
- `tests/test_ev_strdata_batch25.py`
- `BATCH25_V0.25_README_KO.md`

## 재생성 및 좁은 테스트

```powershell
python -B workstreams/ev_strdata/build_ev_strdata_batch25.py `
  --game-root .. `
  --out-root workstreams/ev_strdata

python -B -m unittest workstreams.ev_strdata.tests.test_ev_strdata_batch25 -v
```

생성기는 격리 A/B와 최종 산출물을 바이트 단위로 대조하고, 오프라인 재패킹 결과를 검증한다. 설치된 게임 파일·글꼴·실행 파일·설치기·전역 진행 문서는 수정하지 않는다.

## 검수 우선순위

- ESC 색상·이름 표식이 있는 53개 항목과 `[b754]`, `[bm754]`, `[b1871]`, `[bm1871]`, `[bs1871]` 자리표시자가 있는 ID `4801`~`4810`, `4814`~`4818`, `4824`, `4836`, `4838`
- 줄바꿈이 있는 71개 항목의 실제 대화창 폭과 전환
- SC와 JP 또는 TC의 줄바꿈·ESC·자리표시자 구조가 다른 ID `4761`, `4765`, `4768`, `4770`, `4772`, `4801`, `4802`, `4815`, `4816`, `4828`, `4836`
- 간토 간레이, 우린케, 주나곤·다이나곤, 기요스 동맹, 천하포무 등 역사 용어와 인명 표기
