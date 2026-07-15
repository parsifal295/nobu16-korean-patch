# Steam JP 공통 메시지 구조 재배치 v1

현재 스팀 설치본 `F:/SteamLibrary/steamapps/common/NOBU16`의 순정
`MSG_PK/JP` 구조를 기준으로 다음 5개 파일을 다시 빌드한다.

- `msgev.bin`: 13,794개 대상 ID 적용 / 중복 병합 2건 / 실제 미해결 71건
- `msgdata.bin`: 23,369개 대상 ID 적용 / 중복 병합 48건 / 실제 미해결 24건
- `msgbre.bin`: 2,216개 대상 ID 적용 / 실제 미해결 0건
- `msgire.bin`: 122개 대상 ID 적용 / 실제 미해결 0건
- `msgstf.bin`: 6개 대상 ID 적용 / 실제 미해결 1건

합계는 기존 JP-native 유효 변경 39,653건 중 스팀 대상 ID 39,507개에
적용했다. 좌표가 직접 남지 않은 146건 가운데 50건은 같은 JP 해시와 같은
한국어가 살아남은 대상 ID에 이미 적용된 중복 병합이고, 실제 미해결은 96건이다.
미해결 항목은 원문이 변경되었거나 중복 문맥을 안전하게 확정할 수 없어 순정
JP로 유지한다.

## 구조 원칙

- SC 바이너리·SC 좌표를 읽거나 사용하지 않는다.
- 검증 완료된 이전 JP-native 후보 A/B와 그 JP 순정 입력의 차이에서만
  `JP UTF-16LE 해시 → 한국어`를 얻는다.
- 이전 JP와 현재 스팀 JP의 전체 해시 시퀀스에서 동일한 순서 블록만 이식한다.
- 스팀 순정 packed/raw 해시와 문자열 ID 수를 고정한다.
- 문자열 ID 영역, 비대상 문자열, 불투명 비문자열 메타데이터, LZ4 wrapper
  prefix를 보존한다.
- 공개 JSON에는 한국어 결과와 JP 원문 해시만 있고 JP 원문 문자열과 완성
  게임 바이너리는 없다.
- 후보 바이너리는 `KR_PATCH_WORK/tmp` 아래에만 생성하며 게임 폴더를 덮어쓰지
  않는다.

## 재현 및 후보 생성

```powershell
python workstreams/steam_jp_common_messages_v1/build_steam_jp_common_messages_v1.py verify
python workstreams/steam_jp_common_messages_v1/build_steam_jp_common_messages_v1.py build `
  --output-root tmp/steam_jp_common_messages_v1_candidate
```

`bootstrap`은 고정된 이전 JP 순정 백업과 JP-native 후보 A/B가 있는 개발
환경에서 공개 오버레이를 재생성하는 감사 명령이다. 일반 후보 빌드에는 해당
사설 입력이 필요하지 않다.

검증 근거는 `validation.v1.json`, 미매핑 좌표와 해시는
`review/steam_jp_common_message_unmapped.v1.json`에 기록한다.
