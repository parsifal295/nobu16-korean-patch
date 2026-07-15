# Steam JP 런타임 10파일 스켈레톤 감사

이 작업은 Steam PK v1.1.7(build `18823764`)의 일본어 리소스만 읽는다. 간체중문 컨테이너는 입력하지 않으며 설치된 게임 파일과 후보 바이너리는 쓰지 않는다.

- `MSG/JP/strdata.bin`: 기존 소스 비포함 한국어 카탈로그를 같은 좌표의 Steam JP 원문 SHA-256으로 다시 고정하고, JP 원본에서 직접 재빌드 가능한 항목만 공개 오버레이에 넣는다.
- `RES_JP/res_lang.bin`: 최신 서울한강 글리프 후보를 사용하고 LINK 6·7번만 달라지는지 검증한다.
- `RES_JP_PK/res_lang_pk.bin`: 최신 서울한강 글리프 후보를 사용하고 LINK 16·17번만 달라지는지 검증한다.
- `contract.v1.json`: 정확한 JP 10파일 상대 경로, 순정 predecessor 해시, 확보된 후보와 아직 없는 후보를 분리한다.

`dry-run`은 10개 후보가 모두 원래 상대 경로로 별도 candidate-root에 준비되고, 게임과 런처 프로세스가 모두 종료되며, 설치본 10개의 predecessor 해시가 전부 일치할 때만 가능하다. 현재 계약은 누락 후보가 하나라도 있으면 fail-closed한다.

재현:

```powershell
python workstreams/steam_jp_runtime_skeleton_v1/build_steam_jp_runtime_skeleton_v1.py
python workstreams/steam_jp_runtime_skeleton_v1/build_steam_jp_runtime_skeleton_v1.py --verify
python -m unittest workstreams/steam_jp_runtime_skeleton_v1/test_steam_jp_runtime_skeleton_v1.py -v
```
