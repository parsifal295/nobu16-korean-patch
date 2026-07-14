# 역사 이벤트 대사 batch16 v0.16

`msgev` ID 4977~5108의 실제 표시 대사 132개를 한국어 초벌로 작성한 입력 배치다. 기존 v0.1~v0.15, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일은 수정하지 않는다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 야마나카 시카노스케와 녹각 투구 | 4977~4991 | 15 |
| 미요시 요시오키의 죽음 | 4992~5021 | 30 |
| 미카와 잇코잇키 | 5022~5045 | 24 |
| 다케다 요시노부 사건 | 5046~5077 | 32 |
| 신겐의 오분승 철학 | 5078~5108 | 31 |
| 합계 | 4977~5108 | 132 |

ID 4976은 v0.15의 마지막 대사다. ID 5108에서 오분승·칠분승·십분승을 통해 완벽을 경계하는 신겐의 철학을 설명하는 사건이 끝난다. 다음 번역 시작점인 ID 5109부터는 히다로 진군한 다케다군이 산중의 유황 가스에 쓰러지는 사건이 시작한다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 내부 키를 가리키는 항목이 없다.

## 번역·검증 상태

- 132개 모두 자동 초벌이며 사람 문체 검수와 실제 게임 화면 검수가 필요하다.
- 같은 ID의 고정된 SC·JP·EN을 대조했다. 공개 근거에는 원문 대신 396개의 UTF-16LE SHA-256과 제어구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이며, 최댓값은 32다. 길이 예외와 원문 고정 개행 예외는 없다.
- 시카노스케 이름과 녹각 투구 유래, 마나세 도산, 미요시 간간석, 슈고시 불입, 도쿠가와 십육신장, 하치야 한노조, 칩거, 적비 부대, 도코지, 오분승·칠분승·십분승 및 역사 인용문의 독음·용어·맥락은 최종 용어집과 역사 검수가 필요하다.
- 기존 인명·지명 표기의 미요시 나가요시·요시오키·마쓰나가 히사히데, 마쓰다이라 모토야스·이에야스, 다케다 요시노부·가쓰요리, 사나다 마사유키, 주고쿠·미카와·스루가·쓰쓰지가사키관을 따랐다.
- 공개 overlay·근거·검토 인덱스·validation의 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.15 공개 overlay·근거·검토 인덱스·validation 60개를 개별 SHA-256으로 고정했다.
- 그 60개 경로·해시의 결정적 manifest SHA-256은 `974F502DCD3751AAE01F0F18B7FBCF03AA663C9AF9F42470C6398F405F69C441`다.
- 빌드 전후 설치본 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256을 비교하며, 빌더는 어느 게임 파일에도 쓰지 않는다.
- 이 검증은 현재 작업 시점의 설치본 불변을 증명한다. v0.16은 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_4977_5108.v0.16.json` | `2C84A767E44C53AA2C903242634B134D4FEC89A0B8897BF2E3357581E292A0EF` |
| `evidence/alignment_evidence.v0.16.json` | `B2ACF15590D6F56CD649281FE56801BDC70693F7BAF2CADB71C2D9E24ECD15B5` |
| `review/review_index.v0.16.json` | `0B916057D9D3C538A9EFB9CC2036D63097D8A6B93BDA648E505740B64A1AACB3` |
| `validation.v0.16.json` | `0A2F79C2CEAF7A3D494D2AC23B014BD75D3D08E0A67DA742BA0E14DC46AF2B18` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch16.py"

foreach ($Out in @(
  "tmp\dialogue_batch16_a",
  "tmp\dialogue_batch16_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch16 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch16.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch16 tests failed" }
```

세 번의 출력에서 overlay·근거·검토 인덱스·validation은 각각 바이트 단위로 같아야 한다.
