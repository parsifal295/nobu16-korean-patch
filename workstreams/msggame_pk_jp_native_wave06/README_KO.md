# Steam JP-native `msggame` wave06

Steam 설치본 `F:/SteamLibrary/steamapps/common/NOBU16`의 일본어 PK 리소스를
직접 기준으로 삼는다. 대상 원본은 `MSG_PK/JP/msggame.bin` 721,304바이트,
SHA-256 `31D52FB797EA31CBD75646A2E1607829635AC51C288606FB2ADFBDCA940F4210`이며
21,751레코드·29,524리터럴이다.

간체중문 컨테이너나 SC 좌표는 사용하지 않는다. 기존 한국어 9,386개와
Switch v1.3의 PC 본편 JP 원문 해시 일치분 14,825개를 Steam JP 원문 해시로
다시 고정했다. 일본어 의미 문자열 28,272개 중 24,211개(85.6360%)가 확보됐고
신규 번역 잔여는 4,061개다.

| 배치 | JP 범위 | 수량 |
|---|---|---:|
| J01 | 블록 17 전반 | 970 |
| J02 | 블록 17 후반 | 969 |
| J03 | 블록 6 | 761 |
| J04 | 기타 블록 전반 | 680 |
| J05 | 기타 블록 후반 | 681 |

공개 JSON에는 JP 원문 대신 SHA-256과 한국어만 들어간다. 번역용 JP/EN/TC
레코드 문맥은 `tmp/msggame_pk_jp_native_steam_wave06_private` 아래에만 생성하며
커밋하지 않는다. Steam 게임 파일은 아직 수정하지 않았다.

```powershell
python build_jp_native_wave06.py build
python build_jp_native_wave06.py verify
python build_jp_native_wave06.py export-private
```
