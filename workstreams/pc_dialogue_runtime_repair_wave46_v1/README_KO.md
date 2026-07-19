# Wave 46 런타임 대사 3개 계열 보정 후보

이 작업은 Steam PC판의 현재 `msggame.bin` 두 파일만 읽어, 런타임 토큰을 가진 대사 3개 계열·물리 레코드 6개를 비공개 후보로 만든다. Steam 설치 파일, Git, 네트워크, GitHub 릴리즈에는 쓰지 않는다.

| 계열 | Base | PK | 화면에 보이는 목표 문장 |
| --- | ---: | ---: | --- |
| 난이도+주의 | `15:220` | `15:223` | `다소 어려운 일입니다.`<br>`신중히 판단하십시오.` |
| 난이도 단문 | `15:270` | `15:273` | `다소 어려운 일입니다.` |
| 성 정무 런타임 슬롯 | `6:4410` | `6:4469` | `당분간 전투에 나설 성이 아니니`<br>`[런타임 성명]의 정무 역량을`<br>`활용하려는 뜻은 압니다만…` |

입력은 반드시 다음 현재 Steam PC 패킹 프로필이어야 한다.

- Base `MSG/JP/msggame.bin`: `F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB` (1,504,410 bytes)
- PK `MSG_PK/JP/msggame.bin`: `0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092` (1,806,538 bytes)

정확한 후보 출력 프로필은 다음과 같다.

- Base packed: `0B5AFDFC8B54FEE826C0923F8A566C34CCBCF6F8857EFA87462EEEB1D572E8A3` (1,504,354 bytes), raw: `A6A175CC803654B45A8BDF63EDF11886C46712F2CC3CCDB29C6777CD83B036EC` (1,498,452 bytes)
- PK packed: `1C8F404C7D68AA15D93E8260BBFF1578F370EDCA688E5C57700DDAF53EA16F64` (1,806,482 bytes), raw: `9AB5CE89D7FEBA9EE1B3B3CE4D2F4AD20CACD93A47C851F83F4569F079454805` (1,799,400 bytes)

각 레코드는 원래 literal-slot 수, marker topology, 수동 줄바꿈 수, `05 05 05` terminator를 유지한다. A/B는 명시된 일본어 `01 43` 굴절 명령만 제거한다. C는 `01 43 01 00 00 00` 런타임 슬롯을 바이트 그대로 보존하고, 마지막 일본어 굴절 명령 하나만 제거한다. 모든 후보는 글꼴 폭, 3줄 제한, opaque span, 02xx opcode 불변성, 정확한 변경 레코드 집합을 검사한다.

후보 생성 및 검증은 아래처럼 한다.

```powershell
py -3 -B workstreams\pc_dialogue_runtime_repair_wave46_v1\build_pc_dialogue_runtime_repair_wave46_v1.py build
py -3 -B workstreams\pc_dialogue_runtime_repair_wave46_v1\build_pc_dialogue_runtime_repair_wave46_v1.py verify-private
py -3 -B -m unittest workstreams\pc_dialogue_runtime_repair_wave46_v1\test_pc_dialogue_runtime_repair_wave46_v1.py -v
```

생성물은 `tmp/pc_dialogue_runtime_repair_wave46_v1/candidate/` 아래에만 존재한다. 특히 C 계열은 실제 런타임 성명 폭을 포함한 게임 화면 QA를 통과하기 전에는 Steam 적용 대상이 아니다.
