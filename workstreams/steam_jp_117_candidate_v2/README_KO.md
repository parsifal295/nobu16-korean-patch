# Steam PK 1.1.7 일본어 경로 v0.7.0 후보

Steam build `18823764`, PK 버전 `1.1.7`의 순정 일본어 파일을 predecessor로
사용해 파일 전용 한글 패치 후보를 조립한다. 후보는 SC 경로를 사용하지 않으며,
게임 폴더에 그대로 덮어쓸 수 있는 다음 JP 경로 10개만 포함한다.

- `MSG/JP/strdata.bin`
- `MSG_PK/JP/msgbre.bin`
- `MSG_PK/JP/msgdata.bin`
- `MSG_PK/JP/msgev.bin`
- `MSG_PK/JP/msggame.bin`
- `MSG_PK/JP/msgire.bin`
- `MSG_PK/JP/msgstf.bin`
- `MSG_PK/JP/msgui.bin`
- `RES_JP/res_lang.bin`
- `RES_JP_PK/res_lang_pk.bin`

v0.7.0 후보의 번역 계수는 `strdata` 24,524개, 공통 메시지 39,507개,
`msgui` 매핑 4,036개(실제 변경 3,955개, 미매핑 1개), `msggame` 28,272개다.
`msggame`의 일본어 의미 문자열 잔여 계수는 0이다. 공통 메시지의 미해결 항목은
96개이며, `msgui`의 유일한 미매핑 ID 2657은 순정 데이터가 공백 한 글자인 항목이다.

폰트는 공식 서울한강 EB를 48px급 테이블에, 서울한강 B를 32px급 테이블에
배정한 JP 경로 후보를 사용한다. 검증된 글리프 수요는 124개 소스·88,062개 항목,
1,472개 코드포인트(한글 음절 1,251개)다.

```powershell
python workstreams/steam_jp_117_candidate_v2/build_steam_jp_117_candidate_v2.py build `
  --output-root tmp/steam_jp_117_candidate_v2
```

빌더는 추적된 `verification.v2.json`과 결과가 정확히 일치할 때만 후보를 승격한다.
출력 ZIP 이름은
`NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.7.0.zip`으로 고정되고, 폴더 구조와
원래 파일명을 보존한다. 이 작업공간의 검증은 오프라인 후보 조립과 ZIP 무결성만
다룬다. 실제 Steam 폴더 적용 및 화면 검증 결과는 별도 런타임 QA에 기록한다.
