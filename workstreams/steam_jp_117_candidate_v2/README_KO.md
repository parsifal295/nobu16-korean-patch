# Steam PK 1.1.7 일본어 경로 v0.7.0 후보

Steam build `18823764`, PK 버전 `1.1.7`의 순정 일본어 파일을 predecessor로
사용해 파일 전용 한글 패치 후보를 조립한다. 후보는 SC 경로를 사용하지 않으며,
게임 폴더에 그대로 덮어쓸 수 있는 다음 JP 경로 12개만 포함한다.

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

배포 범위는 `MSG/JP`, `MSG_PK/JP`, `RES_JP`, `RES_JP_PK`,
`RES_JP_PK_PORT`의 정확히 5개 폴더다. `RES_JP_PK_PORT/res_lang_pk_port3.bin`은
후보에 포함하지 않고 덮어쓰지 않으며, 빌더의 exact-12 검증도 port3나 다른 추가
파일이 섞인 후보를 거부한다.

v0.7.0 후보의 번역 계수는 `strdata` 24,524개, 공통 메시지 39,507개,
`msgui` 매핑 4,036개(실제 변경 3,955개, 미매핑 1개), `msggame` 28,272개다.
`msggame`의 일본어 의미 문자열 잔여 계수는 0이다. 공통 메시지의 미해결 항목은
96개이며, `msgui`의 유일한 미매핑 ID 2657은 순정 데이터가 공백 한 글자인 항목이다.

폰트는 공식 서울한강 EB를 48px·96px급 테이블에, 서울한강 B를 32px·64px급
테이블에 배정한 JP 경로 후보를 사용한다. 검증된 글리프 수요는 124개
소스·88,062개 항목, 1,472개 코드포인트(한글 음절 1,251개)다. 다음 두 PORT 폰트
후보를 함께 적용한 조합으로 QHD 창 모드·보더리스 화면을 검증했다.

- `RES_JP_PK_PORT/res_lang_pk_port1.bin`: 79,243,911바이트,
  SHA-256 `00E9C1063ED164402AA70CB770100D8AE11A92B8024F20A4F1D89F2EA1A467F7`
- `RES_JP_PK_PORT/res_lang_pk_port2.bin`: 67,086,423바이트,
  SHA-256 `F18D99C4802AAB78C60C372FF0106ABD61ABDD8C026DC53CAE8FDE47C992C205`

```powershell
python workstreams/steam_jp_117_candidate_v2/build_steam_jp_117_candidate_v2.py build `
  --port-stock-root "F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.7.0-12file/originals/RES_JP_PK_PORT" `
  --output-root tmp/steam_jp_117_candidate_v2_port
```

`--port-stock-root`는 두 PORT 파일이 아직 순정인 게임 폴더 또는 별도 보존한 순정
스냅샷을 명시해야 한다. 적용된 라이브 파일을 순정 입력으로 오인하지 않도록 기본값은
두지 않는다.

빌더는 추적된 `verification.v2.json`과 결과가 정확히 일치할 때만 후보를 승격한다.
현재 검증 계약의 SHA-256은
`C98F6CDD5A7E1FDAD1F93DE4BCA2C95A47A9DF4D1371EC90A2523F8EFD4F52DD`다.
출력 ZIP 이름은
`NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.7.0.zip`으로 고정되고, 폴더 구조와
원래 파일명을 보존한다. 완성된 exact-12 ZIP은 356,144,243바이트이며 SHA-256은
`F245F23882BD9C676B705DCA9DA5E1443BEE05EA88A12F7BA9E7692BEA100584`다.

GitHub issue #41 회귀 검증에서 Steam 실기에 적용한 뒤 창모드 QHD와 보더리스 QHD
모두 한글 표시가 정상임을 확인했다. 게임을 완전히 종료하고 다시 실행한 콜드
재시작 뒤에는 보더리스 QHD의 한글 타이틀과 메인 메뉴가 PASS했다.
