# base 이벤트 ID 9332 문맥형 3줄 재배치

실게임에서 확인된 base 이벤트 `MSG/JP/ev_strdata.bin` ID 9332은 현재
한글 문장을 단순히 줄바꿈만 옮겨서는 3줄에 넣을 수 없다. 이 작업은
문맥을 보존한 짧은 한국어 문장과 세 개의 명시적 줄 경계를 사용한다.

- Steam 현재 파일의 SHA-256과 ID 9332 UTF-16LE preimage를 모두 고정한다.
- 이름/지명 색상 제어코드는 균형을 검증한다.
- 런타임 토큰·printf·숨은 제어 문자는 바꾸지 않는다.
- 실제 글꼴 advance 기준으로 각 줄이 보수적인 912px 이하인지 검증한다.
- Steam 설치본에는 절대 직접 쓰지 않고, 11파일 transaction profile 후보만
  `tmp` 아래에 만든다.

실행:

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_ev_strdata_9332_semantic_reflow_v1\build_pc_ev_strdata_9332_semantic_reflow_v1.py build
& $py -B workstreams\pc_ev_strdata_9332_semantic_reflow_v1\build_pc_ev_strdata_9332_semantic_reflow_v1.py verify
```
