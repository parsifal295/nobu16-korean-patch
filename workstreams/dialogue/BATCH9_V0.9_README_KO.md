# 역사 이벤트 대사 batch9 v0.9

`msgev` ID 4032~4160의 실제 표시 대사 129개를 한국어 초벌로 작성한 독립 배치다. 기존 v0.1~v0.8, 루트 README와 진행률 파일, 공통 빌더, 다른 작업선, 폰트·설치기·게임 파일은 수정하지 않았다.

## 범위

| 묶음 | ID 범위 | 번역 수 |
|---|---:|---:|
| 우에스기 노리마사의 에치고 망명 | 4032~4055 | 24 |
| 무라카미 요시키요의 몰락과 망명 | 4056~4087 | 32 |
| 가이즈성 축성과 딱따구리 전법 | 4088~4104 | 17 |
| 히라테 마사히데의 간언과 자결 | 4105~4127 | 23 |
| 우에스기 마사토라, 데루토라로 개명 | 4128~4133 | 6 |
| 아사쿠라 소테키의 승리관 | 4134~4138 | 5 |
| 아사쿠라 소테키의 죽음 | 4139~4160 | 22 |
| 합계 | 4032~4160 | 129 |

ID 4031은 v0.8의 마지막 대사다. ID 4160에서 소테키 사후담이 끝나며, 다음 번역 시작점인 ID 4161부터 아마고 신구토 숙청 사건이 시작된다. 이번 범위에는 SC·JP·EN에서 공통으로 비표시 처리되는 내부 항목이 없다.

## 번역·검증 상태

- 129개 모두 자동 초벌이며 사람 문체 검수와 실제 게임 화면 검수가 필요하다.
- 같은 ID의 SC·JP·EN을 대조했고, 공개 근거에는 원문 대신 387개의 UTF-16LE SHA-256과 제어 구조만 기록했다.
- ESC 색상 코드, 줄바꿈, 앞뒤 공백, 제어문자, PUA, printf 토큰을 SC 기준으로 보존했다.
- `[bm1251]`, `[bs1448]`, `[b1251]`, `[b1448]`, `[bm1448]` 같은 동적 이름 자리표시자의 종류와 순서를 항목별로 검사했다.
- 4053·4079의 가게토라와 4080의 두 번째 인명은 SC에서 고정 문자열이므로 동적 자리표시자로 바꾸지 않았다. 4060은 SC의 `[bm1251]`을 그대로 보존했다.
- 공개 오버레이·근거·검수 인덱스·검증 JSON의 한자 및 가나 수는 모두 0이다.
- 모든 작성 줄은 ESC 코드를 뺀 32코드포인트 이하이며, 32자를 넘는 레이아웃 예외는 없다.
- 간토 간레이·가마쿠라 구보, 우에스기 분가, 교토쿠·조쿄의 난, 오타테, 젠코지다이라, 고소슨 삼국동맹, 나카쓰카사노조, 세이슈지, 데루토라 관련 독음과 용어는 최종 용어집 검수가 필요하다.
- 두 개의 격리 출력과 최종 출력에서 아래 네 파일이 바이트 단위로 동일했다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_4032_4160.v0.9.json` | `C5781DC398C09C776888577F3831F9C853440C5A1A0C0BC450384E4505911F9A` |
| `evidence/alignment_evidence.v0.9.json` | `DFEAC5B69599C239A02E5A3C1801382312691A51FF6F9A4E3F7D8D207C9426D6` |
| `review/review_index.v0.9.json` | `42E2DA83B1391451A55B14AD06F6407D1A4F8C705B783257DD02F39A12ABEA08` |
| `validation.v0.9.json` | `0F23B1D2B02985CDCB5E2F674630CEC250977EC830A1EC1D683364723FE97C1C` |

## 통합 제한

이 배치는 번역 검수용 독립 공개 입력이다. 현재 글꼴이나 설치기에 포함되지 않으며 게임 파일에도 적용되지 않았다. 배포본에 넣기 전에 v0.1~v0.9와 장수명 오버레이를 확정 SC 기준으로 병합하고, 재패킹·글리프 수요 계산·게임 내 UI 검수를 거쳐야 한다.

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch9.py"

foreach ($Out in @(
  "tmp\dialogue_batch9_a",
  "tmp\dialogue_batch9_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch9 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch9.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch9 tests failed" }
```
