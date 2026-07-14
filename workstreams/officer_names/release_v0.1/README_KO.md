# 장수명 v0.1 네 리소스 배포 골격

`Build-OfficerNamesReleaseV01.ps1`은 완성된 `msgui`, `msgdata`, `msgev`, Font-v5 공개
레시피를 source-free 패키지로 묶는다. 기존 `msgui_full/release_p4_vnext`의 고정 C# 재생성
코어와 strict JSON guard를 SHA-256으로 검증한 뒤 결과 패키지의 `tools/`에 복사한다. 기존
workstream 파일은 수정하지 않는다.

12건 장수명 교정과 Font-v5 재생성을 마친 최종 recipe/target SHA-256은
`inputs/final_pins.json`에 고정했다. 네 리소스 E2E와 실제 게임 검수 결과는 각각
`inputs/four_resource_recipe_e2e.json`, `inputs/runtime_qa.json`에 기록하며, 두 증명의
크기·SHA-256은 `inputs/candidate_pins.json`으로 다시 고정한다. 상세 기록은
`QA_REPORT_KO.md`에 있다. 입력 계약은 `inputs/README_KO.md`를 따른다.

빌드는 `Development`와 `ReleaseCandidate`를 분리한다. 기본값은 `Development`다.
`ReleaseCandidate`는 최종 네 리소스 recipe E2E와 실제 게임 runtime QA의 통과 증명 파일을
별도 SHA-256 핀으로 모두 검증하지 못하면 출력 폴더 생성 전에 실패한다.

설치기는 다음 네 고정 파일만 다룬다.

1. `MSG_PK/SC/msgui.bin`
2. `MSG_PK/SC/msgdata.bin`
3. `MSG_PK/SC/msgev.bin`
4. `RES_SC/res_lang.bin`

각 거래는 네 파일의 before/after SHA-256 벡터, sibling stage, rollback 파일, durable 저널을
사용한다. 중간 실패는 이미 바뀐 파일을 역순 복원한다. 기존 3명 probe/Font-v4 레시피
자체와 target 해시는 각각 exact size+SHA-256으로 predecessor에 고정하고,
`KR_PATCH_BACKUP` 내부의 exact size+hash stock 백업만 사용해 먼저
네 파일 stock으로 정규화한다. 최종 적용 실패 시 검증된 시작 벡터 snapshot으로 되돌린다.
정규화와 최종 적용 사이의 강제종료에도 시작 벡터를 잃지 않도록, 별도의 durable migration
저널이 네 snapshot의 고정 경로·크기·SHA-256을 기록한다. 재시작 시 내부 거래 저널을 먼저
복구한 뒤 이 상위 저널로 predecessor를 복원하거나 이미 완료된 final을 확정한다.
원복도 최종 벡터뿐 아니라 고정된 predecessor 벡터를 정확히 식별한 경우 네 stock 백업으로
한 거래에서 복원한다. 리소스별 허용 해시를 임의로 섞은 벡터는 적용과 원복 모두 거부한다.

격리 테스트:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File `
  .\workstreams\officer_names\release_v0.1\Test-OfficerNamesReleaseV01.ps1
```

테스트는 `KR_PATCH_WORK/tmp` 아래 합성 fixture만 만들며 설치된 게임과 실행 중인 게임
프로세스에 접근하지 않는다.
