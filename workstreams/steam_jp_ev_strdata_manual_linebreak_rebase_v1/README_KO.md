# Steam JP `ev_strdata` 수동 줄바꿈 4좌표 현재상태 리베이스

현재 Steam JP `MSG/JP/ev_strdata.bin` 한 파일만 입력으로 고정하고, 검증된 네 좌표에서만 CRLF/CR/LF를 ASCII 공백 하나로 바꾼다. 기존 수동 번역 payload를 다시 주입하지 않으므로 현재 한국어 문구는 그대로 보존한다.

- 입력 packed SHA-256: `109E0B3D11E4942FD56F5C785CC3824884B8830DF14FF398476D6CBFEDEE584E`
- 대상 좌표: `3917, 7260, 8818, 8904` / 줄바꿈 토큰 6개
- 결과 packed SHA-256: `6A7D90C1A95AD42DCAE2D3C3719508EDD00588288659A1D192B680CF70EAE6E4`
- Steam 설치본, 폰트, 다른 리소스는 쓰지 않는다. 후보는 `tmp` 아래에만 만든다.

실행:

```powershell
& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B KR_PATCH_WORK\workstreams\steam_jp_ev_strdata_manual_linebreak_rebase_v1\build_steam_jp_ev_strdata_manual_linebreak_rebase_v1.py verify
& C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe -B KR_PATCH_WORK\workstreams\steam_jp_ev_strdata_manual_linebreak_rebase_v1\build_steam_jp_ev_strdata_manual_linebreak_rebase_v1.py build
```

`verification.v1.json`은 현재 입력 파일과 네 셀의 UTF-16LE hash, 줄바꿈 벡터, 보호 토큰 벡터를 고정한다. `verify`와 `build`는 이 계약과 후보의 변경 도메인(정확히 네 셀)을 모두 확인한다.
