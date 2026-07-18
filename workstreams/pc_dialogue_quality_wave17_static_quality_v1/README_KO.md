# PC 대사 품질 Wave 17 — static quality v1

이 workstream은 현재 Steam PC의 **Wave 15+16 및 이미 적용된 Issue 61 수리 후 11파일
프로필을 읽기 전용 입력**으로 삼아, Base `msggame.bin`의 확정 후보 3개만 바꾸는 private
candidate 생성기다.
Steam 설치본 적용, Git 작업, 푸시, 릴리스 생성 기능은 없다. 생성물은 이 workstream의
`tmp` 아래에만 기록되며, 실제 게임 QA와 별도 승인 전에는 배포 대상이 아니다.

## 후보 변경

| 좌표 | 기존 | 후보 | 판단 |
| --- | --- | --- | --- |
| `MSG/JP/msggame.bin:2:489:1` | `내리겠다!` | `주겠다!` | 보상/지급 문맥에 맞는 자연스러운 대사 |
| `MSG/JP/msggame.bin:2:519:0` | `포위병 마음대로 하게 두지 ` | `포위병들이 마음대로 하게 두지 ` | 주격 조사 보완. 끝 공백은 보존 |
| `MSG/JP/msggame.bin:13:328:0` | `중계점` | `경유점` | 같은 튜토리얼의 용어 사용과 통일 |

문맥상 검토가 더 필요한 용병 용어와 UI 표기 후보는 이 Wave에 넣지 않았다. NPC/무장 이름
변경도 포함하지 않는다.

## 고정 입력과 출력

현재 Steam 입력은 다음 11파일 프로필과 정확히 일치해야 한다. 핵심 앵커는 Base
`msggame.bin` `EEA622999F38C72F2088467E04D4A885B684D3FD3CF99FB72879A72079CF9351`,
PK `msgev.bin` `CE1A61E6C0F85A3E7F0FD4C1DD1BF0349A99CC134A9D73B7DE1917DB6646A0C3`,
PK `msggame.bin` `9EB0FD80E7A6D50BC2A6073FDBF213E7BDB685D81DFCD9191C9C86E415D7EFCC`다.

Issue 61로 이미 바뀐 retain 파일은 `MSG/JP/strdata.bin`
`6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933` 및
`MSG_PK/JP/msgdata.bin`
`73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED`다.

후보의 Base `msggame.bin`은
`C1B39C7344F8A095E179942A26FB4EBDECEAABC2D6A8966A0DB134B7EBE600AC`이며,
나머지 10파일은 입력 해시와 완전히 동일해야 한다.

PC의 JP 원본 및 Steam SC/TC 대응 레코드 앵커를 모두 검증한다. Base English 리소스는
존재하지 않으므로 검증 대상이 아니다.

## 안전 계약

- 세 literal 이외에는 Base `msggame.bin` 레코드 바이트가 변하지 않아야 한다.
- 각 대상 레코드의 opaque 바이트, marker 토폴로지, terminator, 수동 줄바꿈 및 선행/후행
  공백은 그대로여야 한다.
- 실제 사용 중인 `RES_JP/res_lang.bin`의 글리프 폭과 fallback을 검증한다.
  `2:489`은 672px → 624px, `2:519`은 792px → 888px (대화 한 줄 한계 912px 이하),
  `13:328`은 각 줄 폭이 변하지 않는다. 세 후보 모두 fallback 글리프가 없다.
- Switch 입력/출력, Steam 쓰기, Git/릴리스 조작 경로는 구현하지 않는다.

## 실행

작업 루트 `KR_PATCH_WORK`에서 실행한다.

```powershell
& py -B workstreams\pc_dialogue_quality_wave17_static_quality_v1\build_pc_dialogue_quality_wave17_static_quality_v1.py hash
& py -B -m unittest workstreams\pc_dialogue_quality_wave17_static_quality_v1\test_pc_dialogue_quality_wave17_static_quality_v1.py
& py -B workstreams\pc_dialogue_quality_wave17_static_quality_v1\build_pc_dialogue_quality_wave17_static_quality_v1.py build
& py -B workstreams\pc_dialogue_quality_wave17_static_quality_v1\build_pc_dialogue_quality_wave17_static_quality_v1.py verify-private --candidate-root tmp\pc_dialogue_quality_wave17_static_quality_v1\candidate
```

성공한 build는 다음 private 산출물만 생성한다.

```text
tmp/pc_dialogue_quality_wave17_static_quality_v1/candidate/
tmp/pc_dialogue_quality_wave17_static_quality_v1/audit.v1.json
tmp/pc_dialogue_quality_wave17_static_quality_v1/build_manifest.v1.json
```

실게임 검증 시 해상도를 바꿨다면 `NOBU16PK.exe`를 완전히 종료한 후 다시 실행하고,
선택 해상도와 재시작 완료 여부를 결과에 기록해야 한다.
