# 이슈 118 교섭 응답문 보정 v1

v0.93.0 및 초기 v0.94.0 RC의 PK `MSG_PK/JP/msggame.bin`에서 교섭 확인
응답이 `안이옵니다`로 조립되는 문제를 단일 리터럴 교정으로 수정한다.

- 대상: PK `(block 6, record 3778, literal 1)`
- 기존 리터럴 해시: `99ED549153C807F40832AC76895E9D17BFB659EFB80E88A959CDCC7BA5270DF4`
- 교정 리터럴: `\n좋은 방안`
- 예상 제보 말투 출력: `좋은 방안이옵니다`
- 최종 PK packed SHA-256:
  `F09D9CCE819E26E3B14E368DD4AA7A7254D7CB81CBB5EB3860D0D1A099C4CFC1`

Ghidra 정적분석에서 레코드의 `02 3C`는 교섭 대상을 출력하고, 두 `01 43`
호출은 각각 의문형과 서술형 말투 어미를 출력하는 것으로 확인됐다. 따라서 공통
`msgdata`나 어미 테이블을 수정하지 않고, 두 번째 리터럴만 완전한 명사구로 바꾼다.

빌더는 정확한 v0.93.0 리소스 해시를 입력으로 요구하며 다음을 검증한다.

1. `(6,3778,1)` 한 리터럴과 `(6,3778)` 한 레코드만 변경된다.
2. `02 3C`, `01 43 EE 00 00 00`, `01 43 26 02 00 00`, `05 05 05` 제어
   바이트가 보존된다.
3. packed/raw/record/literal 해시가 모두 고정된 결과와 일치한다.
4. 출력 경로가 Steam 설치 폴더이면 거부한다.

```powershell
python workstreams/issue_118_diplomacy_good_plan_v1/build_issue_118_diplomacy_good_plan_v1.py `
  --input-root I:/Workspaces/NOBU16-Korean/scratch/release-v0940-rc-20260819-01/resource-input/target `
  --output-root I:/Workspaces/NOBU16-Korean/scratch/issue118-v0940-candidate-20260819-01

python -m unittest tests/test_issue_118_diplomacy_good_plan_v1.py
```

생성 후보는 v0.94.0 리소스 명세의 필수 `TargetOverrideRoot`로만 사용한다.
`New-V0940ResourceSpec.ps1`은 해당 파일의 크기와 SHA-256을 다시 확인하고, 후보가
없거나 해시가 다르면 명세 생성을 거부한다. 이 작업은 Steam 설치본에 직접
적용하지 않는다.
