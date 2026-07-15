# Steam PK v1.1.7 일본어 경로 10파일 후보

Steam build `18823764`, PK 버전 `1.1.7`의 순정 일본어 리소스에서 직접
재빌드한 파일 전용 후보를 한곳에 조립한다. 출력 `candidate` 폴더에는 게임에
덮어쓸 원래 상대 경로와 파일명 그대로 정확히 10개만 존재한다.

- `MSG/JP/strdata.bin`
- `MSG_PK/JP/`의 `msgui.bin`, `msgev.bin`, `msgdata.bin`, `msgbre.bin`,
  `msgire.bin`, `msgstf.bin`, `msggame.bin`
- `RES_JP/res_lang.bin`
- `RES_JP_PK/res_lang_pk.bin`

모든 메시지는 Steam 순정 JP 구조에서 다시 만들어지고, 두 폰트는 같은 Steam
순정을 predecessor로 한 서울한강 EB/B 후보를 사용한다. 기존 v0.5 메시지
바이너리나 SC 컨테이너는 조립 입력이 아니다.

```powershell
python workstreams/steam_jp_117_candidate_v1/build_steam_jp_117_candidate_v1.py `
  --output-root tmp/steam_jp_117_candidate_v1
```

ZIP도 같은 10개 상대 경로만 포함하며 원본 게임 파일은 쓰지 않는다. 실제
적용은 `tools/pk_file_only_transaction.py`로 별도 manifest와 백업을 만든 뒤
게임 및 공식 런처가 모두 종료된 상태에서 수행한다.

`runtime_qa.v1.json`은 Steam PK v1.1.7 실설치 적용, 원본 백업 10개, 목표 해시
10개와 한글 타이틀·메인 메뉴 화면 검증 결과를 기록한다. `verification.v1.json`의
`steam_files_written: false`는 후보 조립기 자체가 게임 폴더를 쓰지 않는다는 뜻이다.
