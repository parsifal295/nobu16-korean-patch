# Steam 1.1.7 일본어 `msggame.bin` 직접 재빌드

대상은 Steam PK v1.1.7(build ID `18823764`)의
`F:/SteamLibrary/steamapps/common/NOBU16/MSG_PK/JP/msggame.bin`이다.
기존 패치 바이너리를 복사하거나 SC 컨테이너를 JP 폴더에 미러링하지 않는다.

빌더는 정확한 Steam JP 순정 packed/raw 해시를 확인한 뒤 JP 원문 해시가
일치하는 공개 한국어 overlay만 적용한다. 현재 구조 후보에는 검증된 기존
번역 24,211개가 들어가며, 신규 번역이 필요한 JP 의미 문자열 4,061개는
순정 그대로 남긴다.

검증 계약:

- 18 blocks, 21,751 records, 29,524 literal coordinates 보존
- 모든 block별 record 수와 literal 좌표 집합 보존
- literal 텍스트를 제거해 정규화한 모든 비문자 bytecode/marker 구조 보존
- 변경하지 않은 literal은 byte-exact 보존
- JP source hash와 제어코드·printf·ESC·PUA·개행·공백 invariant 확인
- SC 컨테이너·SC 좌표·SC 원문 입력 없음
- A/B 결과 바이트와 manifest 일치
- 후보는 repository `tmp` 아래에만 출력하고 Steam 파일은 쓰지 않음

```powershell
python workstreams/steam_jp_msggame_v1/build_steam_jp_msggame_v1.py build
```

실제 게임 적용은 10파일 통합 후보와 트랜잭션 dry-run이 끝난 뒤에만 한다.
