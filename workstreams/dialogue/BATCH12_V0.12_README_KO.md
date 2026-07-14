# 역사 이벤트 대사 batch12 v0.12

`msgev` ID 4418~4556의 실제 표시 대사 139개를 한국어 초벌로 작성한 입력 배치다. 기존 v0.1~v0.11, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일은 수정하지 않는다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 미키 가문의 아네가코지 계승 | 4418~4442 | 25 |
| 다케나카 한베에의 원복 | 4443~4445 | 3 |
| 아시카가 요시테루의 환교 | 4446~4460 | 15 |
| 오다 노부나가의 상경 | 4461~4474 | 14 |
| 가게토라와 요시테루의 대면 | 4475~4493 | 19 |
| 요시모토의 수급과 소자 사몬지 | 4494~4510 | 17 |
| 모토치카의 첫 출진 문답 | 4511~4527 | 17 |
| 조소카베 구니치카의 죽음 | 4528~4556 | 29 |
| 합계 | 4418~4556 | 139 |

ID 4417은 v0.11의 마지막 대사다. ID 4556에서 조소카베 구니치카의 죽음과 계승 사건이 끝나며, 다음 번역 시작점인 ID 4557부터는 마쓰나가 히사히데의 시기산성 축성 사건이 시작한다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 내부 키를 가리키는 항목이 없다.

## 번역·검증 상태

- 139개 모두 자동 초벌이며 사람 문체 검수와 실제 게임 화면 검수가 필요하다.
- 같은 ID의 고정된 SC·JP·EN을 대조했다. 공개 근거에는 원문 대신 417개의 UTF-16LE SHA-256과 제어구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이며, 최댓값은 30이다. 길이 예외와 원문 고정 개행 예외는 없다.
- 미키 요시요리·아네가코지 요리쓰나, 세이가케·다이진케, 금공명, 승군산·쇼군산의 동음 말장난, 고노에 사키히사, 이마가와 지부타이후, 소자 사몬지와 도신 명문, 진젠지 야스코레, 히메와코, 조소카베 가네쓰구, 이치료구소쿠 관련 독음·용어·문체는 최종 용어집과 역사 검수가 필요하다.
- 공개 overlay·근거·검토 인덱스·validation의 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.11 공개 overlay·근거·검토 인덱스·validation 44개를 개별 SHA-256으로 고정했다.
- 그 44개 경로·해시의 결정적 manifest SHA-256은 `6CED726D019874E79E91469144B53833F54D5B1C3A9A38518B58EC8F518BC670`이다.
- 빌드 전후 설치본 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256을 비교하며, 빌더는 어느 게임 파일에도 쓰지 않는다.
- 이 검증은 현재 작업 시점의 설치본 불변을 증명한다. v0.12는 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_4418_4556.v0.12.json` | `AF0061757E9E6B4220A0AC55C9E0C617260746F9098C2EBCEC39301AD5265248` |
| `evidence/alignment_evidence.v0.12.json` | `B0C1BA9A4A48ACFDA9233ED2ABF450F64C0D172B57BEA6FBE96076AB279ADF70` |
| `review/review_index.v0.12.json` | `C9D7D8901C2888301402DF624FBA8C84FB9CA760DFDDB5A0D21D68D3822BDE93` |
| `validation.v0.12.json` | `E5F2D94BD7E1B654143ED8C12DBC68B554734EDEFE0D853FE3D0F1AD52155CA1` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch12.py"

foreach ($Out in @(
  "tmp\dialogue_batch12_a",
  "tmp\dialogue_batch12_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch12 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch12.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch12 tests failed" }
```

세 번의 출력에서 overlay·근거·검토 인덱스·validation은 각각 바이트 단위로 같아야 한다.
