# PC-only `ev_strdata` manual-linebreak repair v1

`ev_strdata`의 수동 개행 보류 9건(4558, 4769, 5155, 5403, 5492, 6365,
6401, 9580, 9585)을 별도 검토하는 격리 작업물이다.

- 번역 문맥은 순정 PC JP, PC SC, PC TC만 사용한다. 이 리소스에는 현재 PC
  EN `ev_strdata.bin`이 없으므로 부재를 검증 결과에 명시한다.
- 현재 PC 한국어는 수정 전 원문 hash gate로만 읽는다. Switch 한국어와 과거
  한국어 번역은 열거나 참조하지 않는다.
- 각 후보는 ESC 색상 태그, printf/runtime token, 제어문자, PUA, 문자열 바깥
  공백을 보존한다.
- 최대 3줄이라는 텍스트 제약은 지키고, 현재 PC 이벤트 폰트(`RES_JP/res_lang.bin`,
  entry 6 / table 0)의 실제 advance와 `[b1448]`의 런타임 이름 예약폭은 기록한다.
  그러나 이 값들은 `ev_strdata` 대화창의 폭을 증명하지 않는다. MSGEV의 912 px
  예산은 이 리소스에 재사용하지 않으며, 명시적 PC 이벤트 UI/container/renderer
  폭 근거가 생길 때까지 9건 전부를 layout hold로 유지한다.
- 후보와 hold 목록은 `tmp`에만 생성한다. Steam 파일, generic builder, 커밋,
  릴리스에는 쓰지 않는다.

실행:

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py -B workstreams\translation_quality_ev_manual_linebreak_repair_v1\build_ev_manual_linebreak_repair_v1.py --write
& $py -B workstreams\translation_quality_ev_manual_linebreak_repair_v1\build_ev_manual_linebreak_repair_v1.py --validate
```

`validation.v1.json`은 한국어 원문/후보를 싣지 않는 source-free 검증 계약이며,
실제 문구와 PC JP/SC/TC 문맥은 private JSONL에만 남긴다. private 후보는
의미·서식 검토용일 뿐 적용 후보가 아니다.
