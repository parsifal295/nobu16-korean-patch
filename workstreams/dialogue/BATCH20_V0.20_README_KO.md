# 역사 이벤트 대사 batch20 v0.20

`msgev` ID 5487~5628의 실제 표시 대사 142개를 한국어 초벌 번역했다. 입력 배치는 기존 v0.1~v0.19, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일을 수정하지 않는다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 적에게 소금을 보내다 | 5487~5509 | 23 |
| 다케나카 한베에의 등용 | 5510~5533 | 24 |
| 노부나가가 알아본 가모 우지사토 | 5534~5552 | 19 |
| 가모 야스히데의 은빛 메기꼬리 투구 | 5553~5574 | 22 |
| 바바 노부하루가 태운 이마가와 보물 | 5575~5593 | 19 |
| 바바 노부하루의 오개조 | 5594~5628 | 35 |
| 합계 | 5487~5628 | 142 |

ID 5486은 v0.19의 마지막 대사다. 다음 번역 시작점은 ID 5629이며, 다케다 가문이 이마가와 가문을 치기 위해 동맹을 모으는 새 사건이 시작된다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 의미를 가리키는 실제 표시 대사만 포함했다.

## 번역·검증 상태

- 142개 모두 자동 초벌 뒤 사람이 문체를 대조했으며 실제 게임 화면 검수는 아직 필요하다.
- 같은 ID의 SC·JP·EN을 대조했다. 공개 근거에는 원문 대신 426개의 UTF-16LE SHA-256과 제어 구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이며 최댓값은 32다. 길이 예외와 원문 고정 개행 예외는 없다.
- 고소슨 삼국 동맹, 비사문천, 적에게 소금을 보내다, 시오도메노타치, 요리키, 오니시바타, 은빛 메기꼬리 투구, 슨푸관, 다케다 사천왕, 오니미노의 오개조, 후키가에시, 상재전장은 최종 용어집과 실제 화면 검수가 필요하다.
- 공개 overlay·근거·검수 인덱스·validation에서 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.19 공개 overlay·근거·검수 인덱스·validation 76개를 개별 SHA-256으로 고정했다.
- 그 76개 경로·해시의 결정론적 manifest SHA-256은 `E92600B08DFC7A576D312F76DA8728A4B21332A72094E38695C7CC3EF6D3F885`다.
- 빌드 전후 설치별 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256을 비교했으며 빌더는 게임 파일에 쓰지 않는다.
- 이 검증은 현재 작업 시점의 설치별 불변만 증명한다. v0.20은 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_5487_5628.v0.20.json` | `6DC7501382513265CDB73C66AF7750508AFDA3488FE17E493A6C3978CAD10167` |
| `evidence/alignment_evidence.v0.20.json` | `985022FF073D4E0ABF3DCE1CFACEE19D987B2F1EFD9B54630B1E1D92A14C44E7` |
| `review/review_index.v0.20.json` | `9AE10934F16CEBB130C7EA3A477A583697BF97E3ECD83959C9FF1D166039AB1C` |
| `validation.v0.20.json` | `F6032C1D0DE4A251418323F3A1B64B29FF18755E957CEF0CFF80396A13759483` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch20.py"

foreach ($Out in @(
  "tmp\dialogue_batch20_a",
  "tmp\dialogue_batch20_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch20 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch20.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch20 tests failed" }
```

세 번의 출력에서 overlay·근거·검수 인덱스·validation은 각각 바이트 단위로 같아야 한다.
