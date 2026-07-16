# Steam PK 1.1.7 일본어 경로 v0.8.0 후보

이 작업 스트림은 Steam build `18823764`, PK `1.1.7`, 일본어(`JP`) 경로용
v0.8.0 파일 전용 후보를 재현한다. v0.7.0 후보는 수정하지 않고 읽기 전용
기준점으로 사용한다.

v0.8.0은 v0.7.0의 `strdata`, `msgui`, `msggame`과 고해상도 서울한강체
4개 경로를 바이트 단위로 유지한다. 공통 메시지 5개만 wave08 통합 결과로
교체한다. 기존 적용 39,507개에 검토 완료 의미 항목 94개와 Steam 일본어판
장수 성씨 980개를 더해 실제 한국어 변경은 40,581개다. 대표 조합
`msgdata` ID 84 `오다 `와 ID 1266 `노부나가`가 `오다 노부나가`로 이어지는
것도 빌드에서 검증한다.

wave08에서 선별한 의미 항목 94개는 전부 처리했다. 이것은 전체 공용 메시지의
미검토 항목이 0개라는 뜻이 아니다. 원본과 값이 같은 구조 계약 1,796개는 실제
한국어 변경 수에서 분리하며, 추가 검토 대기는 형식 계약 차단 730개와 정렬 간극
62개를 합친 792개다. 내부 더미 2개는 정렬 간극에 포함되며 원문 그대로 둔다.
전체 좌표는 `40,581 + 1,796 + 730 + 62 = 43,169`로 닫힌다.

후보는 다음 JP 경로 12개만 포함한다.

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

폰트는 v0.7.0에서 검증한 서울한강 EB(48px·96px급)와 서울한강 B
(32px·64px급)를 그대로 사용한다. 네 후보의 크기와 SHA-256이 하나라도
달라지면 빌드가 중단된다.

고정 ZIP 이름은
`NOBU16_PK_Korean_Patch_Steam_1.1.7_v0.8.0.zip`이다. ZIP은 원래 게임
폴더 구조와 파일명을 보존하며, `RES_JP_PK_PORT/res_lang_pk_port3.bin` 또는
SC 경로를 포함하지 않는다.

임시 exact-12 재현 결과의 ZIP 크기는 356,142,573바이트, SHA-256은
`5F2E6641BDC7BCF615CA7AC697881DA94E61CA95CAE147A053B2C0DFD871F8E9`다.
공개 추적 검증 파일 `verification.v3.json`의 SHA-256은
`7B05C0F44AE4849BAB65E55FD32CF62B37931E66EE41D6CC743BDC083F7D1FC8`다.

검증 핀 제안은 후보를 임시 구성한 뒤 삭제하며 Steam 설치 폴더를 쓰지 않는다.

```powershell
python workstreams/steam_jp_117_candidate_v3/build_steam_jp_117_candidate_v3.py bootstrap `
  --port-stock-root "F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.7.0-12file/originals/RES_JP_PK_PORT"
```

추적 핀과의 전체 재현 검증도 산출물을 남기거나 게임 파일을 변경하지 않는다.

```powershell
python workstreams/steam_jp_117_candidate_v3/build_steam_jp_117_candidate_v3.py verify `
  --port-stock-root "F:/SteamLibrary/steamapps/common/NOBU16/KR_PATCH_BACKUP/file_only_transaction/steam-jp-1.1.7-v0.7.0-12file/originals/RES_JP_PK_PORT"
```

현재 추적 검증 핀과 임시 exact-12 재현은 통과했다. 임시 후보와 ZIP은 검증 직후
삭제했으며, 아직 게임 적용·배포·릴리스를 수행하지 않았다. 실제 배포 전에는 보존
후보 빌드, Steam 설치 적용, 게임 화면 검증을 별도로 통과해야 한다.
