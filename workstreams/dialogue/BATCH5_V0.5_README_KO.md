# 역사 이벤트 대사 batch5 v0.5

번역 속도를 우선해 msgev ID 3565~3688의 실제 표시 대사 124개를 한국어 초벌로 옮긴 독립 배치다. 기존 v0.1~v0.4, 다른 작업선, 현재 글꼴, 설치기와 설치된 게임 파일은 수정하지 않았다.

## 범위

| 묶음 | ID 범위 | 번역 수 |
|---|---:|---:|
| 사이토 가문의 미노 상실 | 3565~3575 | 11 |
| 사이토 다카마사의 잇시키 개성 | 3576~3594 | 19 |
| 가토 화의와 가와고에 귀환 | 3595~3622 | 28 |
| 호조 우지야스의 여우 와카 | 3623~3641 | 19 |
| 도라치요의 환속과 첫 출진 | 3642~3661 | 20 |
| 모리 다카모토의 교육 | 3662~3688 | 27 |
| 합계 | 3565~3688 | 124 |

이 범위에는 SC·JP·EN에 공통으로 들어 있는 내부 키가 없다. ID 3564는 v0.4의 마지막 대사이며, ID 3689부터 가와고에 야전을 다루는 별도 사건이 시작된다.

## 번역·검수 상태

- 124개 모두 translated 초벌이며 사람 문체 검수와 런타임 검수가 필요하다.
- SC·JP·EN의 같은 ID를 대조했다. 공개 근거에는 원문 대신 372개 UTF-16LE SHA-256과 제어 구조만 기록했다.
- ESC 색상 코드, 줄바꿈, 앞뒤 공백, 제어문자, PUA, printf 토큰을 모두 보존했다.
- [bm924], [b75] 자리표시자의 종류와 순서를 124회 별도로 검사했다. SC에서 고정 이름이고 JP에서만 자리표시자인 항목은 SC 기반 구조를 유지했다.
- 가변 이름 뒤에는 공 또는 에게 같은 고정 표현을 사용해 한국어 조사 충돌을 피했다.
- ESC 코드를 뺀 작성 줄의 최대 길이는 32코드포인트이며 32자를 넘는 항목은 없다.
- 슈고다이·호코슈·오쇼반슈·사시키, 잇시키 계보, 야마노우치·오기야쓰, 기쓰네바시, 고소슨 삼국동맹, 아즈마카가미, 개구리 바위 전승, 덴시쓰·도치오·묘큐·시지 히로요시 독음은 용어집 검수가 필요하다.
- ID 3630~3634의 와카는 원문의 기쓰·네 말장난을 한국어 본문과 다음 대사의 해설로 전달했으며 전문 검수가 필요하다.
- ID 3673의 SC 인명 순서는 JP·EN과 어긋나므로 두 언어와 문맥에 따라 다카모토로 번역하고 검수 표식을 남겼다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| public/msgev_ko_historical_events_3565_3688.v0.5.json | 1E5D5E874439C7D0FC0BD93D6EB2FBAC6C249DF18A9BFBCBBE2200BCC45F75AC |
| evidence/alignment_evidence.v0.5.json | 0D561160DBDA0CACC38DCA729A5B315603ED75B9DC94889C5B0A4DBF900AE085 |
| review/review_index.v0.5.json | 582C7F2930496F36CA460370DD3CA47C611F4794C8DFD7A6EA1028008D921C20 |
| validation.v0.5.json | F6AE6830D94549DB9D917D2F65DAE0A8BDAA59A956A10ECE17428B4BA565203A |

위 네 파일은 독립 A/B 생성과 최종 경로에서 바이트 단위로 같았다. 공개 오버레이·정렬 근거·검수 인덱스의 통합 한자 영역 문자와 히라가나·가타카나는 모두 0개다.

## 통합 제한

이번 배치는 번역량 확보를 위한 후속 릴리스 입력이다. 현재 글꼴과 설치기에는 포함하지 않는다. 실제 배포 전에는 v0.1~v0.5와 장수명 오버레이를 순정 SC 기준으로 병합하고, 새 글리프 수요를 계산한 뒤 후속 글꼴을 만들어야 한다.

## 재생성

    $Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    $Script = "workstreams\dialogue\build_event_dialogue_batch5.py"

    foreach ($Out in @(
      "tmp\dialogue_batch5_a",
      "tmp\dialogue_batch5_b",
      "workstreams\dialogue"
    )) {
      & $Python -B $Script --out-root $Out
      if ($LASTEXITCODE -ne 0) { throw "dialogue batch5 build failed: $Out" }
    }

    & $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch5.py"
    if ($LASTEXITCODE -ne 0) { throw "dialogue batch5 tests failed" }
