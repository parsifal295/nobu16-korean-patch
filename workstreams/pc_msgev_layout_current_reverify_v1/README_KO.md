# 현재 Steam 이벤트 4,003건 레이아웃 재검증

v2의 4,003개 검토 좌표를 적용 직후 Steam `MSGEV`와 폰트로 다시 측정하는 읽기 전용 검증기다. 이전 후보의 해시를 억지로 재사용하지 않는다.

- 동적 이름 토큰은 현재 `MSGEV`의 같은 숫자 ID 이름 폭으로 예약한다.
- 기대한 설치본 `MSGEV`·폰트 SHA-256과 다르면 측정을 시작하지 않고 검증을 거부한다.
- 검토 대상 ID 4,003개의 좌표 SHA-256도 고정 대조하므로, 원본 감사의 분류·개수가 같아도 대상 행이 바뀌면 검증을 거부한다.
- 4,002건은 3줄·912px 제한을 확인한다.
- ID `16402`는 printf 치환 길이를 정적으로 알 수 없어 별도 보존 항목으로 기록하며, 정적 문자열 폭만 출력한다.

```powershell
$py='C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams/pc_msgev_layout_current_reverify_v1/revalidate_pc_msgev_layout_current_v1.py --write
```
