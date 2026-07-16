# Steam PK 1.1.7 일본어 경로 v0.8.0 후보 v4

이 작업공간은 Steam build `18823764`, PK `1.1.7`의 일본어(`JP`) 경로만
대상으로 하는 v0.8.0 exact-12 후보를 재현한다. 설치된 게임 파일을 읽거나
바꾸지 않으며, 후보와 ZIP은 저장소 `tmp` 아래에서만 생성한다.

v4는 고정된 v3 후보를 먼저 재현한 뒤, 아래의 검증된 후속 수정만 순서대로
조합한다.

- `MSG_PK/JP/msgui.bin`: 시나리오 선택의 기간·개월 표기 ID 1051 1건 보정.
- `MSG_PK/JP/msgdata.bin`: 이벤트 가문 표기 159건 정규화.
- `MSG_PK/JP/msgdata.bin`: 전법 독음 10건 보정 및 활성 독음 슬롯의 Latin 문자
  부재 검증.
- `MSG_PK/JP/msgdata.bin`: 관직 표시명 113건과 독음 8건, 총 121건 보정.
  표시명은 한글 관직명으로, 독음은 일본어 발음의 한글 표기로 구분한다.
  고정 앵커는 `관백/간파쿠`, `우대신/우다이진`, `대납언/다이나곤`,
  `정이대장군/세이이다이쇼군`이다.
- `MSG_PK/JP/msgev.bin`: 이벤트 잔여 문장 50건과 분기·조건 표기 16건, 총
  66건 보정.

관직의 지리 범주와 막부 범위 `16614..16624`는 이번 범위에서 의도적으로
보류한다. `strdata.bin`, `msggame.bin`, 나머지 공용 메시지, 서울한강 글꼴
4경로는 v3/v0.7 검증 후보와 바이트 단위로 동일해야 한다.

후보 ZIP에는 아래 게임 폴더 기준 12개 JP 경로만 들어간다.

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
- `RES_JP_PK_PORT/res_lang_pk_port1.bin`
- `RES_JP_PK_PORT/res_lang_pk_port2.bin`

고정 자산명은 `NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.8.0.zip`이다.
재현 검증 결과는 다음과 같다.

- ZIP: 356,142,112 bytes, SHA-256
  `D1C2D91E65D03DC3A57EF7D5D45A4B7381EA7752024062CD91D069F02E2BE354`
- 추적 검증 파일 `verification.v4.json`: SHA-256
  `E900CE49E42CB12B99E1CB4D6E148B2D421AE1D87DCDBA0933571711BB1F69D1`
- 최종 `msgui.bin`: SHA-256
  `29D0C6CCC262E7AB757AA5D0819224370DEDEF4CF250E89FC88B24E600EF2169`
- 최종 `msgdata.bin`: SHA-256
  `2D1BEFF03972777FBA5EE0B8FEF24E6A03B285DA466A4DA439794D21587A0F69`
- 최종 `msgev.bin`: SHA-256
  `A8835C3520B29A076A21014E17B17D7AAABF4AC99D37D65C891415AC17BBF3F5`

검증에는 Steam 1.1.7 원본 포트 글꼴 백업 경로가 필요하다. 아래 명령은
설치 게임 파일을 수정하지 않고 임시 스테이지만 만들었다가 제거한다.

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\steam_jp_117_candidate_v4\build_steam_jp_117_candidate_v4.py verify `
  --port-stock-root "F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.7.0-12file/originals/RES_JP_PK_PORT"
& $py -B workstreams\steam_jp_117_candidate_v4\test_steam_jp_117_candidate_v4.py
```

`build`는 검증 성공 뒤에만 exact-12 후보를 `tmp`에 보존한다. SC 컨테이너,
메모리 패치, DLL 주입, 후킹, EXE·레지스트리 변경은 사용하지 않는다.
