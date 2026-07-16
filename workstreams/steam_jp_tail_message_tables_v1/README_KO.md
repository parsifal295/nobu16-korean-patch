# Steam JP 소형 잔여 텍스트 후보

대상은 활성 Steam 일본어 기준의 아래 세 파일뿐이다.

- `MSG/JP/ev_strdata.bin`: 5건
- `MSG_PK/JP/msgbre.bin`: 1건
- `MSG_PK/JP/msgstf.bin`: 1건

각 대상은 개별 Steam 기준 해시, 원문 UTF-16LE 해시, 좌표 계약, 메시지 테이블 구조를 먼저 확인한다. 앞의 두 파일은 이미 동결된 한국어 카탈로그와 **동일 원문 해시**가 일치할 때만 재사용하며, 크레딧 한 건은 줄바꿈·전각 공백·제어 토큰을 보존한 프로젝트 번역이다.

공개 산출물은 `public/`, `validation/`, 파일별 `source_free_contract.*.json`이며 일본어 원문이나 완전한 게임 리소스를 포함하지 않는다. 완전한 `bin` 후보는 `KR_PATCH_WORK/tmp/steam_jp_tail_message_tables_v1/<target>/candidate/` 아래에만 생성된다.

```powershell
python build_steam_jp_tail_message_tables_v1.py freeze --target all
python build_steam_jp_tail_message_tables_v1.py build --target all
python test_steam_jp_tail_message_tables_v1.py
```

빌더는 Steam 설치 경로, GitHub, 릴리즈 자산을 쓰지 않는다.
