# Steam JP `strdata` P0-01 (350좌표) 번역 후보

이 스트림은 Steam 1.1.7의 활성 일본어 경로 `MSG/JP/strdata.bin`에서, 잔여 감사 계약의 첫 P0 묶음 350좌표만 다룬다. 범위는 `p0-MSG_JP_strdata-01`의 좌표 SHA-256 `5DA0F1C55931DDC450755E7E6197F1B5B91E7AD9E11805DA4AA7B9287D427B65`로 고정된다.

번역은 Switch v1.3의 같은 좌표를 참고하되, 다음 세 조건이 모두 성립할 때만 채택한다.

1. 활성 Steam JP 파일과 원시 데이터의 SHA-256이 실제 v6 기준값과 일치한다.
2. 각 350좌표의 활성 JP 원문이, 핀된 공식 JP 백업과 글자 단위로 완전히 같다.
3. Switch의 한국어 값은 제어문자·줄바꿈·서식 토큰을 보존하고 일본어 가나·한자가 남지 않는다.

`public/strdata_ko_steam_jp_p0_b01_350.v1.json`에는 좌표, 원문 SHA-256, 한국어와 한국어 SHA-256만 있다. 원문 텍스트나 완전한 게임 리소스는 포함하지 않는다.

후보 생성은 항상 핀된 Steam JP 원본에서 시작하며, 결과는 `tmp/steam_jp_strdata_p0_b01_v1/` 아래에만 쓸 수 있다. 설치 폴더·릴리즈·GitHub에는 쓰지 않는다.

```powershell
$py='C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py workstreams\steam_jp_strdata_p0_b01_v1\build_steam_jp_strdata_p0_b01_v1.py derive-overlay
& $py workstreams\steam_jp_strdata_p0_b01_v1\build_steam_jp_strdata_p0_b01_v1.py build --output-dir tmp\steam_jp_strdata_p0_b01_v1\candidate
& $py workstreams\steam_jp_strdata_p0_b01_v1\build_steam_jp_strdata_p0_b01_v1.py determinism --output-dir tmp\steam_jp_strdata_p0_b01_v1\determinism
```

이 스트림은 로고·타이틀·브랜드 아트와 무관한 텍스트 데이터만 변경한다.
