# `pk_msggame` PC 원문 재감사 v1

이 작업물은 `MSG_PK/JP/msggame.bin`의 남은 품질 문제를 순정 PC 원문으로만
재검토한다. 대상은 관계 상태 라벨의 반전과 문장 끝의 명백한 누락 30개다.

- 판단 근거는 순정 backup PC JP와 Steam PC EN/SC/TC의 같은 레코드 문맥이다.
- 현재 Steam PC JP 경로의 한글은 수정 전 문자열 hash gate로만 사용한다.
- `F:\Games\NOBU16\MSG_PK\SC`는 한글이 섞인 별도 파일임이 확인되어 절대 읽지
  않는다. Switch 한글·과거 한글·generic 한글 본문도 읽거나 참조하지 않는다.
- 각 후보는 리터럴의 runtime/printf/ESC/개행/앞뒤 공백과 해당 레코드의 비문자
  bytecode skeleton을 보존한다. `6:2733`은 기존 수동 줄바꿈을 이동하지 않는다.
  `6:3846`·`6:3847`의 한 칸 공백은 인접 두 리터럴 사이에서만 보존한다.
- 출력은 `tmp/`의 private JSONL과 source-free 검증 결과뿐이다. Steam 게임 파일,
  generic builder, 커밋, 릴리스에는 쓰지 않는다.

실행:

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py -B workstreams\translation_quality_msggame_pc_reaudit_v1\build_msggame_pc_reaudit_v1.py --write --validate
```
