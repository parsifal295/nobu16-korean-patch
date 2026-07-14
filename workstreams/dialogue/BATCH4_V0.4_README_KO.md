# 역사 이벤트 대사 batch4 v0.4

번역 속도를 우선해 msgev ID 3441~3564의 실제 표시 대사 124개를 한국어 초벌로 옮긴 독립 배치다. 기존 v0.1~v0.3, 현재 글꼴, 설치기와 설치된 게임 파일은 수정하지 않았다.

## 범위

| 묶음 | ID 범위 | 번역 수 |
|---|---:|---:|
| 아시카가·미요시 화의와 결렬 | 3441~3460 | 20 |
| 오다 노부카쓰의 두 번째 모반 | 3461~3484 | 24 |
| 가토의 난과 가와고에 위기 | 3485~3524 | 40 |
| 다케다 노부시게의 가훈 | 3525~3549 | 25 |
| 나베시마 나오시게와 히코쓰루 | 3550~3564 | 15 |
| 합계 | 3441~3564 | 124 |

이 범위에는 SC·JP·EN에 공통으로 들어 있는 내부 키가 없다. ID 3440은 v0.3의 마지막 대사이며, ID 3565부터 미노의 사이토 가문을 다루는 별도 사건이 시작된다.

## 번역·검수 상태

- 124개 모두 translated 초벌이며 사람 문체 검수와 런타임 검수가 필요하다.
- SC·JP·EN의 같은 ID를 대조했다. 공개 근거에는 원문 대신 372개 UTF-16LE SHA-256과 제어 구조만 기록했다.
- ESC 색상 코드, 줄바꿈, 앞뒤 공백, 제어문자, PUA, printf 토큰을 모두 보존했다.
- [bm75], [b1251], [bm1251], [b790], [bm790] 자리표시자의 종류와 순서를 124회 별도로 검사했다.
- 가변 이름 뒤에는 가능한 한 공, 측, 본인, 일행 같은 고정 명사를 두어 한국어 조사 충돌을 피했다.
- ESC 코드를 뺀 작성 줄의 최대 길이는 32코드포인트이며 32자를 넘는 항목은 없다.
- 오토모슈, 료젠성, 노부카쓰·가쓰이에 독음, 가이도 제일의 무사, 가토의 난, 간토 관직·지명, 마고쿠로의 인물 식별, 쓰쓰지가사키관, 덴큐, 고슈 법도지차제, 히코쓰루히메·노토미 독음은 용어집 검수가 필요하다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| public/msgev_ko_historical_events_3441_3564.v0.4.json | 31A05234F6E5CCC40BF40E7AE9A19BFE5E3A229A27725B17AA21EB932811C854 |
| evidence/alignment_evidence.v0.4.json | 35EE8A8A3DC5EFF888B32F423884E22F67C8140213EE200A8B30391F3E03C491 |
| review/review_index.v0.4.json | 7650A7831B8F12215AE951049EACAEE08B24119666B1DB7F74EB7ABE07002C9B |
| validation.v0.4.json | 35FDFB30F42D4081C0334C793F4E49988D1F1CCDA7FDB05BB40045882F35C936 |

위 네 파일은 독립 A/B 생성과 최종 경로에서 바이트 단위로 같았다. 공개 오버레이·정렬 근거·검수 인덱스의 통합 한자 영역 문자와 히라가나·가타카나는 모두 0개다.

## 통합 제한

이번 배치는 번역량 확보를 위한 후속 릴리스 입력이다. 현재 글꼴과 설치기에는 포함하지 않는다. 실제 배포 전에는 v0.1~v0.4와 장수명 오버레이를 순정 SC 기준으로 병합하고, 새 글리프 수요를 계산한 뒤 후속 글꼴을 만들어야 한다.

## 재생성

    $Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
    $Script = "workstreams\dialogue\build_event_dialogue_batch4.py"

    foreach ($Out in @(
      "tmp\dialogue_batch4_a",
      "tmp\dialogue_batch4_b",
      "workstreams\dialogue"
    )) {
      & $Python -B $Script --out-root $Out
      if ($LASTEXITCODE -ne 0) { throw "dialogue batch4 build failed: $Out" }
    }

    & $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch4.py"
    if ($LASTEXITCODE -ne 0) { throw "dialogue batch4 tests failed" }
