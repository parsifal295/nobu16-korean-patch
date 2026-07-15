# `ev_strdata` 역사 사건 번역 Batch 23 v0.23

- 리소스: `MSG/SC/ev_strdata.bin`
- 구조 확인 범위: ID `4387`~`4556`, 총 `170`개
- 실제 표시문 번역: `170`개
- 내부 키·자리표시자·인물 참조·빈 슬롯 제외: `0`개
- 다음 실제 표시 후보: ID `4557`

ID `4387`부터 SC·JP·TC를 같은 번호로 정렬해 아카마쓰 하루마사의 추방, 우키타 나오이에의 죽음, 하루노부의 신겐 개명, 미키 가문의 아네가코지 계승, 다케나카 한베에의 원복, 아시카가 요시테루의 환교, 오다 노부나가의 상경, 가게토라와 요시테루의 대면, 요시모토의 수급과 소자 사몬지, 모토치카의 첫 출진 문답, 조소카베 구니치카의 죽음까지 번역했다. ID `4556`에서 구니치카의 죽음과 계승 사건이 완결되므로 이 지점을 배치 경계로 삼았다.

이번 범위의 SC·JP·TC 문자열은 모두 실제 표시문이었다. 내부 이벤트 키, 독립 인물 참조, 더미 자리표시자, 빈 슬롯은 발견되지 않았다. v0.13~v0.22에서 제외한 기존 `549`개 ID와 이번 빈 제외 집합의 교집합도 `0`개다. 기존 배치별 제외 수와 ID 해시, 합집합 해시, 교집합 결과는 evidence와 validation에 기록했다.

같은 사건을 담은 기존 `msgev` v0.11·v0.12의 소스 비의존 한국어 번역 `170`개를 재사용하고, 설치된 `ev_strdata`의 SC·JP·TC와 전 항목을 다시 정렬·검증했다. 제어코드·동적 인물 표식·개행·앞뒤 공백 구조가 다른 항목은 없었다. 반복 SC 원문 세 그룹도 각 그룹 안에서 같은 한국어 문장으로 고정돼 있다. 공개 산출물에는 상용 원문을 넣지 않고 숫자 ID, 해시, 문자열 구조 정보만 기록한다.

모든 번역은 색상 코드, 동적 인물 표식, 개행, 앞뒤 공백을 SC 기준과 같은 순서로 보존했다. 화면 길이와 희귀 인명·공가 격식·도검 명칭·사세구·이치료구소쿠 용어는 실제 게임에서 추가 검수가 필요하므로 review에 런타임 배치 및 용어 검수 표시를 남겼다.

## 배치 산출물

- `public/ev_strdata_ko_historical_events_4387_4556.v0.23.json`
- `evidence/alignment_evidence.v0.23.json`
- `review/review_index.v0.23.json`
- `validation.v0.23.json`
- `build_ev_strdata_batch23.py`
- `tests/test_ev_strdata_batch23.py`
- `BATCH23_V0.23_README_KO.md`

## 재생성

```powershell
python -B workstreams/ev_strdata/build_ev_strdata_batch23.py `
  --game-root .. `
  --out-root workstreams/ev_strdata

python -B -m unittest workstreams.ev_strdata.tests.test_ev_strdata_batch23
```

생성기는 설치된 SC·JP·TC 원본의 고정 해시와 메시지 테이블 재구성 일치 여부를 먼저 확인한다. 이어 오프라인 임시 바이너리를 만들고, 격리 A/B와 최종 실행에서 네 공개 산출물이 바이트 단위로 같은지 검증한다. 설치 파일, 글꼴, 실행 파일, 설치기, 루트 진행 문서는 수정하지 않는다.
