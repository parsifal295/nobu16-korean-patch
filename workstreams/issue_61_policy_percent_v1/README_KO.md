# Issue #61 정책 효과 퍼센트 리터럴 복구

이 작업은 Steam JP 1.1.7의 정책 효과 문자열에서 `％`(U+FF05)가
ASCII `%`(U+0025)로 바뀌어 단위가 사라지는 문제를 복구한다.
`%+d`는 printf 토큰이고, 그 뒤의 `％`은 화면에 표시해야 하는 리터럴이다.
따라서 `%+d%`의 마지막 ASCII `%`는 formatter에 유효하지 않다.

## 범위

- `MSG_PK/JP/msgdata.bin`: 정책 효과 ID `22506–22701` 전수 감사,
  해시 고정 복구 49개 ID
- `MSG/JP/strdata.bin`: block `0`, slot `22254–22387` 전수 감사,
  해시 고정 복구 39개 slot
- 총 88개 좌표만 수정한다. 나머지 9개의 JP text-audit 프로필 파일은 현재
  Steam 바이트를 그대로 retain한다.

복구 전후 모두 v0.9 원본 ZIP과 historical fullwidth-normalization 메타데이터의
UTF-16LE 해시로 검증한다. 각 복구 문자열은 v0.9 원본과 정확히 같아야 하며,
printf 토큰은 바뀌지 않고 unsafe ASCII `%`는 0개가 되어야 한다.

## 실행

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$repo = 'F:\Games\NOBU16\KR_PATCH_WORK'
$steam = 'F:\SteamLibrary\steamapps\common\NOBU16'
$tmp = "$repo\tmp\issue_61_policy_percent_v1\wave15_16_rebased"

Set-Location $repo
& $py -B -m unittest workstreams\issue_61_policy_percent_v1\test_issue_61_policy_percent_v1.py
& $py -B workstreams\issue_61_policy_percent_v1\build_issue_61_policy_percent_v1.py audit --steam-root $steam
& $py -B workstreams\issue_61_policy_percent_v1\build_issue_61_policy_percent_v1.py build --steam-root $steam --output-root "$tmp\candidate" --audit-path "$tmp\audit.v1.json" --manifest-path "$tmp\build_manifest.v1.json"
& $py -B workstreams\issue_61_policy_percent_v1\build_issue_61_policy_percent_v1.py verify --steam-root $steam --output-root "$tmp\candidate"
& $py -B tools\pk_file_only_transaction.py plan --game-root $steam --release-id issue-61-policy-percent-v2 --manifest "$tmp\transaction.v1.json" --candidate-root "$tmp\candidate"
& $py -B tools\pk_file_only_transaction.py dry-run --game-root $steam --manifest "$tmp\transaction.v1.json" --backup-root "$steam\KR_PATCH_BACKUP\issue-61-policy-percent-v2" --candidate-root "$tmp\candidate"
```

`build`, `verify`, `plan`, `dry-run`은 설치된 게임 리소스를 쓰지 않는다.
실제 적용은 별도 승인과 게임 종료 확인 뒤에만 transaction helper의 `apply`를
명시적으로 호출해야 한다. 이 workstream은 `apply`를 호출하지 않는다.

## 릴리스 체인 메모

현재 Steam의 `msggame` 두 파일과 `msgev.bin`은 Wave15/16 이후 v0.11.3
baseline과 다르므로, 기존 v0.11.3 전체 ZIP을 다시 덮어쓰는 방식은 사용하지
않는다. 이 작업은 그 세 파일을 retain한 현재 11파일 predecessor 해시를 고정해
두 메시지 리소스만 교체하는 최종 복구 overlay다.
향후 fullwidth normalizer 자체를 재생성할 때는 U+FF05→U+0025를 runtime 적용
map에서 제외해야 한다.
