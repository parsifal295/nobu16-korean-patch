# 역사 이벤트 대사 batch24 v0.24

`msgev` ID 6020~6141의 실제 표시 대사 122개를 한국어 초벌 번역했다. 기존 v0.1~v0.23 산출물, 루트 README와 진행률 파일, 공통 빌더, 폰트·설치기·게임 파일은 수정하지 않았다.

## 범위

| 사건 | ID 범위 | 번역 수 |
|---|---:|---:|
| 히데요시의 나가하마 축성 | 6020~6045 | 26 |
| 가타쿠라 고주로의 원복 | 6046~6048 | 3 |
| 무로마치 막부의 실질적 멸망 | 6049~6064 | 16 |
| 신겐의 상경 출진 | 6065~6094 | 30 |
| 풍림화산 군기 | 6095~6118 | 24 |
| 겐신이 애도한 신겐의 죽음 | 6119~6141 | 23 |
| 합계 | 6020~6141 | 122 |

다음 번역 시작점은 ID 6142다. 이 ID부터 미카타가하라 전투에서 패한 이에야스의 하마마쓰성 후퇴 사건이 새로 시작된다. 선택 범위에는 SC·JP·EN에서 공통으로 같은 번호를 가리키는 실제 표시 대사만 포함했다.

## 번역·검증 상태

- 122개 모두 사람이 세 언어의 문맥을 대조해 작성한 초벌 번역이며, 실제 게임 화면 검수는 아직 필요하다.
- 각 ID의 SC·JP·EN 참조를 대조했다. 공개 근거에는 원문 대신 366개의 UTF-16LE SHA-256과 제어 구조만 기록했다.
- ESC 색상 코드, 개행 수와 순서, printf·미확인 `%`, 일반 제어문자, PUA, 앞뒤 공백, 동적 대괄호 토큰의 종류와 순서를 항목별로 보존했다.
- ESC 코드를 제외한 모든 작성 줄은 32코드포인트 이하이고 최댓값은 32다. 길이 예외는 없다.
- 인명·지명·관직·군기·불교 용어 등 판단이 필요한 항목 20개는 검수 색인에 별도로 표시했다.
- 공개 overlay·근거·검수 색인·validation에서 CJK 통합한자와 가나 검출 수는 모두 0이다.

## 기존 파일 불변 증거

- v0.1~v0.23 공개 overlay·근거·검수 색인·validation 92개를 개별 SHA-256으로 고정했다.
- 그 92개 경로·해시의 결정론적 manifest SHA-256은 `68DC617B54A0AF178238F889F900EBFDFE3CB498043D6BFA704E15022CD0E567`이다.
- 빌드 전후 설치본 `MSG_PK/SC/msgev.bin`, `MSG_PK/JP/msgev.bin`, `MSG_PK/EN/msgev.bin`의 크기와 SHA-256이 같음을 검증했다.
- v0.24는 아직 공통 병합·폰트·설치기에 포함되지 않은 번역 입력이다.

## 공개 산출물

| 파일 | SHA-256 |
|---|---|
| `public/msgev_ko_historical_events_6020_6141.v0.24.json` | `C9FC4A48DE817074F33751BACE29C5A86C46B1008147AEFEE8A9B29CC9EB06C3` |
| `evidence/alignment_evidence.v0.24.json` | `6AD7755A3DFE83545EE9F3F94ADBCE56B4ECD06E4A4ACDAFBACDB18FBC0E1FFE` |
| `review/review_index.v0.24.json` | `3F82FEC995A2AE0D6BD70D487875DEA076EB9010A699A081E3C83CB352DB4F12` |
| `validation.v0.24.json` | `9E22D24DE965117384ED890D5ACD9520E8A3C25C9A08F7A2E7AACC8A6382993E` |

## 재생성

```powershell
$Python = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"
$Script = "workstreams\dialogue\build_event_dialogue_batch24.py"

foreach ($Out in @(
  "tmp\dialogue_batch24_a",
  "tmp\dialogue_batch24_b",
  "workstreams\dialogue"
)) {
  & $Python -B $Script --out-root $Out
  if ($LASTEXITCODE -ne 0) { throw "dialogue batch24 build failed: $Out" }
}

& $Python -B -m unittest "workstreams\dialogue\tests\test_event_dialogue_batch24.py"
if ($LASTEXITCODE -ne 0) { throw "dialogue batch24 tests failed" }
```

세 번의 출력에서 overlay·근거·검수 색인·validation은 각각 바이트 단위로 같아야 한다.
