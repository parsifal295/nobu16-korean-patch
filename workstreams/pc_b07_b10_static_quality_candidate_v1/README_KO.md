# PC B07–B10 정적 품질 후보 v1

이 작업물은 B07–B10 감사에서 고신뢰로 확정한 **6개 literal**만 담은 PC 전용 private 후보입니다. Steam 게임 파일, Git, 네트워크, 커밋, 태그, 릴리스는 건드리지 않습니다.

## 고정 입력과 출력

입력은 아래 W45 PC 리소스 두 개뿐입니다.

| 리소스 | 입력 packed SHA-256 | 입력 raw SHA-256 | 후보 packed SHA-256 | 후보 raw SHA-256 |
| --- | --- | --- | --- | --- |
| Base `MSG/JP/msggame.bin` | `F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB` | `27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D` | `C13090B0D004D54E44872480DE13FA9CF0C0288EAF195B76E7C668F7B198AC74` | `F843DA9D2A37F8C857CC5209A4311806019A07B9538B7C3A3283356A6071F292` |
| PK `MSG_PK/JP/msggame.bin` | `0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092` | `737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E` | `618086A21438F61EB31397F94271DBF62EEEEE3D3ADCC0F31D884E17C4E64E8B` | `7518C7D55D7382B3B8336F0DC6990576458D348A5C192AB92D9538B090647966` |

후보는 오직 다음 private 경로에 생성됩니다.

`tmp/pc_b07_b10_static_quality_candidate_v1/candidate/`

## 변경 범위

| 리소스 | literal 좌표 | 고정 preimage | 후보 텍스트 |
| --- | --- | --- | --- |
| Base | `9:3640:0` | `이것으로 당분간 싸움은 하지 못하리라...` | `이것으로 당분간 싸움은 하지 못하리라…` |
| Base | `9:3776:0` | `강화 사자가 통했군요\n방침을 두고 반목한 것이겠지요` | `강화 사절이 통했군요\n방침을 두고 반목한 것이겠지요` |
| Base | `9:3796:0` | `설마 간파당하다니···` | `설마 간파당하다니…` |
| PK | `9:4094:0` | `강화 사자가 통했군요\n방침을 두고 반목한 것이겠지요` | `강화 사절이 통했군요\n방침을 두고 반목한 것이겠지요` |
| PK | `9:4113:0` | `복병이 있었다!혼란한 틈에 쳐부수자!` | `복병이 있었다! 혼란한 틈에 쳐부수자!` |
| PK | `9:4114:0` | `설마 간파당하다니···` | `설마 간파당하다니…` |

각 대상은 UTF-16LE preimage/target SHA-256을 고정합니다. LF 시퀀스, 제어 코드, 런타임 토큰, literal 외의 record bytecode skeleton을 보존하며, 변경 record/literal 집합이 정확히 위 6개인지 검사합니다.

## 실행과 검증

```powershell
py -3 -B -m unittest workstreams\pc_b07_b10_static_quality_candidate_v1\test_pc_b07_b10_static_quality_candidate_v1.py -v
py -3 -B workstreams\pc_b07_b10_static_quality_candidate_v1\build_pc_b07_b10_static_quality_candidate_v1.py profile
py -3 -B workstreams\pc_b07_b10_static_quality_candidate_v1\build_pc_b07_b10_static_quality_candidate_v1.py build
py -3 -B workstreams\pc_b07_b10_static_quality_candidate_v1\build_pc_b07_b10_static_quality_candidate_v1.py verify-private
py -3 -B workstreams\pc_b07_b10_static_quality_candidate_v1\build_pc_b07_b10_static_quality_candidate_v1.py diff-check
```

`build`는 기존 private 후보를 덮어쓰지 않습니다. 생성된 `audit.v1.json`과 `candidate_manifest.v1.json`도 후보 바이트와 함께 재검증합니다.

이 후보는 위 6개 정정의 정적 범위만 보증합니다. 전체 인물 대사나 문학 품질 전수조사가 완료되었다는 선언은 아닙니다.
