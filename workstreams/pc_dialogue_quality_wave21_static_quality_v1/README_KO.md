# PC 인물 대사 품질 Wave 21 — static quality v1

이 workstream은 검증된 Wave 19 **private 11파일 candidate만** 읽기 전용 입력으로
사용한다. PK `msggame.bin`의 확정 후보 두 literal만 바꾸며, Steam 설치본 적용,
Git 작업, 푸시, 릴리스 생성 기능은 없다. 산출물은 이 workstream의 `tmp` 아래에만
기록된다.

## 대상

| 좌표 | 기존 | 후보 | 근거 |
| --- | --- | --- | --- |
| `MSG_PK/JP/msggame.bin:2:249:1` | `테니\n걱정은 무용이다.` | `테니\n걱정할 필요 없다.` | JP와 PC EN/SC/TC 모두 재해를 최소화하므로 걱정할 필요가 없다는 의미다. |
| `MSG_PK/JP/msggame.bin:2:321:1` | `\n반드시 훌륭한 성하마을로 만들어 보이겠다!` | `\n반드시 훌륭한 성하마을을 만들어 보이겠다!` | PC JP/EN/SC/TC 모두 성하마을을 건설한다는 의미이며, 한국어 목적격이 필요하다. |

## 고정 preimage와 출력

Wave 19 candidate 전체 11파일 profile이 정확히 일치해야 한다. 특히 입력 Base
`msggame.bin`은 `C00B78165B06A5A9D2BFBE134E847E4B00EC3E5243EE9A1981BA1BB68CFA79C6`,
입력 PK `msggame.bin`은
`7D7826A575E4BA80FEE1E4FE920CBD7E16A48F0DA529D06514EDB59B11422FBC`다.

Wave 21 후보 PK `msggame.bin`은
`0C3C2196E59BCBC1A066DF7097B37C281F8A6236DE70876CCD7BCAB44459BEA9`다.
다른 10파일은 입력 해시와 바이트 단위로 동일해야 한다. Issue 61로 이미 적용된
`MSG/JP/strdata.bin`과 `MSG_PK/JP/msgdata.bin`도 그대로 보존한다.

## 검증 계약

- PC 순정 JP 및 PC EN/SC/TC 각 대응 레코드를 whole-record SHA-256, literal 해시,
  opaque span, 문맥 해시로 고정한다.
- 각 대상은 literal 하나만 바꾸며 marker 토폴로지, opaque 바이트, `05 05 05` 종결자,
  수동 줄바꿈과 선행/후행 공백을 보존해야 한다.
- 실제 `RES_JP/res_lang.bin` 글리프 폭과 fallback을 검증한다.
  - `2:249`: `[696, 384]` → `[696, 408]`, 최대 696px로 912px 이하다.
  - `2:321`: `[696, 432, 984]`가 불변이다. 기존 3줄 984px이므로 새 폭 위험은 없지만,
    적용 전 실제 게임 화면 QA는 필요하다.
- Switch 입력/출력, Steam 쓰기, Git/릴리스 조작 경로는 구현하지 않는다.

## 실행

작업 루트 `KR_PATCH_WORK`에서 실행한다.

```powershell
& py -B workstreams\pc_dialogue_quality_wave21_static_quality_v1\build_pc_dialogue_quality_wave21_static_quality_v1.py hash
& py -B -m unittest workstreams\pc_dialogue_quality_wave21_static_quality_v1\test_pc_dialogue_quality_wave21_static_quality_v1.py
& py -B workstreams\pc_dialogue_quality_wave21_static_quality_v1\build_pc_dialogue_quality_wave21_static_quality_v1.py build
& py -B workstreams\pc_dialogue_quality_wave21_static_quality_v1\build_pc_dialogue_quality_wave21_static_quality_v1.py verify-private --candidate-root tmp\pc_dialogue_quality_wave21_static_quality_v1\candidate
```

성공한 build는 다음 private 산출물만 만든다.

```text
tmp/pc_dialogue_quality_wave21_static_quality_v1/candidate/
tmp/pc_dialogue_quality_wave21_static_quality_v1/audit.v1.json
tmp/pc_dialogue_quality_wave21_static_quality_v1/build_manifest.v1.json
```

실게임 QA에서 해상도를 바꿨다면 `NOBU16PK.exe`를 완전히 종료한 뒤 재실행하고,
선택 해상도와 재시작 완료 여부를 결과에 기록해야 한다.
