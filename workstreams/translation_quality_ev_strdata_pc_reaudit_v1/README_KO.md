# PC-only `ev_strdata` 재감사 v1

이 작업물은 `ev_strdata` 17,868 좌표를 순정 PC JP, 현재 PC KO, PC SC/TC만으로
다시 대조한다. 기존 generic quality overlay의 한국어 본문이나 generic builder는
읽지 않는다. 중복 방지를 위해 `tmp`의 source-free 좌표 ledger에서 ID와 상태만
읽고, 기존 작업물이 점유한 289개 좌표에는 새 후보를 만들지 않는다.

- 새 후보는 고확신 독음 수정 5건뿐이다.
- 후보는 현재 줄바꿈, ESC 색상 태그, runtime/printf token, 제어문자, PUA, 바깥
  공백을 정확히 보존한다. 모든 치환은 같은 줄의 같은 수만큼의 한글 글자를
  바꾸므로, `ev_strdata` UI 폭이 확정되지 않은 상태에서 줄 재배치를 만들지 않는다.
- 줄바꿈을 옮겨야 하는 사안은 후보로 넣지 않는다. 기존 source-free ledger의
  linebreak HOLD 좌표도 중복 생성하지 않는다.
- 후보와 전체 좌표 ledger는 `tmp`에만 쓴다. Steam 설치본, generic builder,
  커밋, 릴리스 산출물에는 쓰지 않는다.

실행:

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py -B workstreams\translation_quality_ev_strdata_pc_reaudit_v1\build_ev_strdata_pc_reaudit_v1.py --write
& $py -B workstreams\translation_quality_ev_strdata_pc_reaudit_v1\build_ev_strdata_pc_reaudit_v1.py --validate
```

`validation.v1.json`과 전체 좌표 ledger는 source-free다. 실제 JP/SC/TC/KO 문구는
private candidate JSONL에만 들어간다. 이 pass는 게임 맥락 전부를 자동으로 판정했다는
주장을 하지 않는다.
