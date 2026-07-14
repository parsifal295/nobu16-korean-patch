# 역사 이벤트 대사 batch6 v0.6

번역 속도를 우선해 msgev ID 3689~3818의 실제 표시 대사 130개를 한국어 초벌로 옮긴 독립 배치다. 기존 v0.1~v0.5, 루트 README와 진행률 파일, 다른 작업선, 현재 글꼴, 설치기와 설치된 게임 파일은 수정하지 않았다.

## 범위

| 묶음 | ID 범위 | 번역 수 |
|---|---:|---:|
| 가와고에 야전 | 3689~3706 | 18 |
| 오다 노부나가의 원복 | 3707~3709 | 3 |
| 제13대 쇼군과 막부 재흥의 꿈 | 3710~3737 | 28 |
| 노부나가와 기쓰노 | 3738~3763 | 26 |
| 나가오 가문의 당주 교체 | 3764~3798 | 35 |
| 라이키리마루 전승 | 3799~3818 | 20 |
| 합계 | 3689~3818 | 130 |

이 범위에는 SC·JP·EN에 공통으로 들어 있는 내부 키가 없다. ID 3688은 v0.5의 마지막 대사이며, ID 3819부터 미요시 가문의 별도 사건이 시작된다.

## 번역·검수 상태

- 130개 모두 translated 초벌이며 사람 문체 검수와 런타임 검수가 필요하다.
- SC·JP·EN의 같은 ID를 대조했다. 공개 근거에는 원문 대신 390개 UTF-16LE SHA-256과 제어 구조만 기록했다.
- ESC 색상 코드, 줄바꿈, 앞뒤 공백, 제어문자, PUA, printf 토큰을 모두 보존했다.
- [b1251], [bm790], [bm75], [bm1773], [bm1448], [b1448], [b1730], [bm1730] 자리표시자의 종류와 순서를 130회 별도로 검사했다.
- 가변 이름 뒤에는 공, 님 같은 고정 명사를 두어 한국어 조사 충돌을 피했다.
- ESC 코드를 뺀 작성 줄의 최대 길이는 32코드포인트이며 32자를 넘는 항목은 없다.
- 지키하치만, 가와고에 야전, 호소카와 게이초, 구쓰키다니, 기쓰노, 쓰카하라 보쿠덴, 이코마 이에무네, 우에스기 사다자네, 덴시쓰 고이쿠, 라이키리마루 관련 용어와 독음은 용어집 검수가 필요하다.
- ID 3692·3694의 친족 관계는 SC의 단순 아우 표기보다 구체적인 JP·EN의 매제 의미를 반영했다.
- ID 3703은 SC의 [bm790]과 JP의 [b790]이 다르므로 SC 기반 오버레이 원칙에 따라 [bm790]을 보존했다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| public/msgev_ko_historical_events_3689_3818.v0.6.json | 4111FA3388E3AC52234EAD5288BEE0959E90CFE9A3B0DB4A0DCE9A5DBE758D2E |
| evidence/alignment_evidence.v0.6.json | 782E6C3460559569B54490BE77C7AD44F8D6B10A94A8355014963BFD372C6CC0 |
| review/review_index.v0.6.json | CB0DFF25C7A035EE0783D3D725E6D2029700CB095DC5FC22EF0FC07431D6D982 |
| validation.v0.6.json | 1FBA570797EE49AA15874D1D3EA42AE94536FE790921D620A72413BCA49EED03 |

위 네 파일은 독립 A/B 생성과 최종 경로에서 바이트 단위로 같았다. 공개 오버레이·정렬 근거·검수 인덱스의 통합 한자 영역 문자와 히라가나·가타카나는 모두 0개다.

## 통합 제한

이번 배치는 번역량 확보를 위한 후속 릴리스 입력이다. 현재 글꼴과 설치기에는 포함하지 않는다. 실제 배포 전에는 v0.1~v0.6과 장수명 오버레이를 순정 SC 기준으로 병합하고, 새 글리프 수요를 계산한 뒤 후속 글꼴을 만들어야 한다.

## 재생성

    $Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    $Script = "workstreams\dialogue\build_event_dialogue_batch6.py"

    foreach ($Out in @(
      "tmp\dialogue_batch6_a",
      "tmp\dialogue_batch6_b",
      "workstreams\dialogue"
    )) {
      & $Python -B $Script --out-root $Out
      if ($LASTEXITCODE -ne 0) { throw "dialogue batch6 build failed: $Out" }
    }

    & $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch6.py"
    if ($LASTEXITCODE -ne 0) { throw "dialogue batch6 tests failed" }
