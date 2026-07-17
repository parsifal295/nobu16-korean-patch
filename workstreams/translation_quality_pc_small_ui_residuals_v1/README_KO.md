# PC 전용 소규모 UI·메시지 잔여 품질 감사

대상은 `msgui`(5,100), `msgbre`(3,000), `msgire`(122), `msgstf`(20),
`msgstf_ce`(20)다.

이 감사는 순정 PC 일본어, 현재 Steam PC 한글 경로, Steam PC EN/SC/TC만 직접
읽는다. Switch·스위치 레포·과거 한글·generic overlay·`F:/Games/NOBU16/MSG_PK/SC`는
읽거나 근거로 사용하지 않는다.

자동 후보는 현재 한글의 일본어/한자/병음형 ASCII/깨짐 신호를 찾은 뒤에도,
같은 리소스 안에서 **동일한 순정 PC 일본어 원문**, 해당 ID의 PC EN/SC/TC 원문까지
완전히 같은 슬롯, 그리고 **유일한 현재 한글 정식 표기**가 확인되는 경우만 만든다.
후보의 printf, ESC, PUA, 제어문자, 줄바꿈, 탭 및 앞·뒤 공백 프로필은 원래 행과
정확히 같아야 한다. UI 용어 취향이나 문맥 추정은 후보로 만들지 않는다.

`tmp/translation_quality_pc_small_ui_residuals_v1/private_candidates.v1.jsonl`에는
검토용 상용 텍스트가 있을 수 있으므로 공개·커밋 대상이 아니다.
`validation.v1.json`은 텍스트를 포함하지 않는 해시·좌표·포맷 검증 보고서다.

실행:

```powershell
$env:PYTHONIOENCODING='utf-8'
& 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe' -B `
  workstreams/translation_quality_pc_small_ui_residuals_v1/audit_pc_small_ui_residuals.py --write --validate
```
