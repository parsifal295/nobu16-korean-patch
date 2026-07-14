# 역사 이벤트 대사 초벌 배치 v0.26

## 범위

- 리소스: MSG_PK/SC/msgev.bin
- ID: 6269~6372 연속 104개
- 상태: 한국어 초벌 번역. 사람 문체·용어와 실제 화면 검수는 아직 필요하다.

| 사건 | ID | 수량 |
|---|---:|---:|
| 요시아키와 노부나가의 결별 | 6269~6287 | 19 |
| 아사쿠라 가문의 멸망 | 6288~6300 | 13 |
| 미쓰히데의 호코슈 편입 | 6301~6322 | 22 |
| 마쓰나가 히사히데의 노부나가 귀순 | 6323~6348 | 26 |
| 사키치와 세 잔의 차 | 6349~6372 | 24 |

ID 6268은 앞 배치의 마지막 항목이고, 6373은 조소카베 모토치카의 새 사건이 시작되는 지점이라 이 배치에서 제외했다.

## 형식 보존

- SC 원문의 ESC 색상 토큰은 68개 항목, 총 282개를 순서대로 유지한다.
- 동적 bracket 토큰은 6279 [b1251], 6280 [bm1251], 6303·6306 [bm1773], 6349 [b754]만 존재하며 순서까지 보존한다.
- 줄바꿈은 0개 4항목, 1개 33항목, 2개 67항목으로 원문 SC와 같다.
- printf 토큰, 미지 %, 일반 제어문자, PUA, 앞뒤 공백은 이 범위에서 모두 없다.
- ESC를 제외한 작성 줄의 최대 길이는 32 코드포인트다. 런타임 레이아웃 검수는 별도로 필요하다.

## 우선 검수 항목

- 6272·6274: 이견 17개조와 전중어정
- 6311~6314: 호코슈·직신의 제도·신분 용어
- 6338~6341: 관용구, 구주쿠가미 가지, 야마토 하사
- 6346: 신여 비유
- 6365: 세 잔의 차 일화
- 6372: 능리 표현

## 산출물

| 파일 | SHA-256 |
|---|---|
| public/msgev_ko_historical_events_6269_6372.v0.26.json | 2B2DC3E2939685B636603D476FBBF3B851619A5FA7B9E1E26F7CCBB899AD7E9E |
| evidence/alignment_evidence.v0.26.json | 9ABA4A871D9D53274E185A076FF185961D78CCD3CDF626E703CD1AD605E02BEA |
| review/review_index.v0.26.json | 698371DB4FB43459E48DD628DDFC035CFC0C7D25F1E9EBCB360386A2D48F0FFF |
| validation.v0.26.json | 24B7C8C964FA5C963F9CAFD6AA9FC02C8CED40B2AF0EDB754633AEA17E2FCFE3 |

공개 JSON은 한국어 번역, 안정 ID, 원문 해시와 제어 구조만 담는다. 정식판 원문·완전한 리소스·실행 파일은 포함하지 않는다.

## 좁은 검증

PowerShell:

    $Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    & $Python -B -m unittest KR_PATCH_WORK\workstreams\dialogue\tests\test_event_dialogue_batch26.py
    if ($LASTEXITCODE -ne 0) { throw 'dialogue batch26 test failed' }

이 배치는 기존 v0.1~v0.25 산출물과 설치된 msgev.bin의 고정 해시를 읽기 전용으로 확인한다.
