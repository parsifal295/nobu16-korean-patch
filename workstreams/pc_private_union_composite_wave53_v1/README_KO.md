# Wave 53 private union composite

이 workstream은 W45 private baseline에서 시작해 아래 네 private candidate의 실제 record-level diff만 합칩니다. Component packed output을 통째로 복사하지 않습니다.

| Component | 포함 record 수 | 제외 hold |
| --- | ---: | --- |
| `pc_static_composite_wave52_v1` | 249 | candidate 밖의 runtime/display/hold 범위 |
| `pc_block15_runtime_candidate_v1` | 17 apply rows | `MSG/JP/msggame.bin` `15:1121` |
| `pc_npc_name_quality_wave50_v1` | 16 | `msgev` `3956` |
| `pc_event_color_tag_reflow_v1` | 7 | hard 7건과 semantic `8510` |

확정 union은 289건입니다.

| Resource | 변경 record 수 |
| --- | ---: |
| `MSG/JP/msggame.bin` | 67 |
| `MSG_PK/JP/msggame.bin` | 166 |
| `MSG_PK/JP/msgdata.bin` | 4 |
| `MSG_PK/JP/msgev.bin` | 52 |

W45 input과 union target은 packed/raw size와 SHA-256까지 고정합니다.

| Resource | W45 packed / raw SHA-256 | Wave 53 packed / raw SHA-256 |
| --- | --- | --- |
| `MSG/JP/msggame.bin` | `F9342D73DE50FDFC97C1F8365A20FD5CEABD024CE63B82AF1F112D5EDEDCFCBB` / `27F2021CED9D7E36B89025EACCF3449D5E424EE5C38C758E5E0995C8234EEB6D` | `50E78AE5BE920454EC8F4B20A485FEF2A1237F593EBF97D205799A2AD705E2B8` / `8B14B76B1A3479C6261D4E2D8C8FD65877B4A3783EC8AF778C9F2B49679D3706` |
| `MSG_PK/JP/msggame.bin` | `0A92516BC4B0A7AE98FD66418AD0BE289682B9DEE2CB25A8A1740A9609288092` / `737DAEAB7CC9257BC0F9E15523D01A0C3E807912B8D44393F75512BFB4C2A11E` | `E470EA330510C571E7B142211C27C49E4E4508C1026FEA6BBC55F07675B71FD7` / `AC952E65D578F6E6DE554229B4A48AFF44703B81CD1810C0362EB4662D3B2673` |
| `MSG_PK/JP/msgdata.bin` | `8282F12A667E11F54054856035415C7297385ADD16EC261BD952BEBB8658952A` / `2D38396C29F7548A1C12691877FE9F3D5D4B2C27647D521CFEC975017977C077` | `34DAAAC9F8AE22445DD580FB5B8182FA9C6CD66C4DA78498E6B20286C5456215` / `9FB501A16D7DF7D84559612A68775D75B6C1E6C0B853123194B81B7FBA8C7BDC` |
| `MSG_PK/JP/msgev.bin` | `01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE` / `F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC` | `E088299D725472827D32B3F16541DD49663C5CD80FA8CA4FF3E5C9BCBCD0B2AF` / `6B313D7EA8AA86DA1E0AE25BFDC6DFEDBA6085EF465959F27E70475D0DB4F620` |

정확한 size 및 전체 hash는 생성된 `candidate_manifest.v1.json`과 `audit.v1.json`에 기록됩니다.

빌더는 다음을 모두 고정 검증합니다.

- private W45 baseline의 builder/audit/output hash와 packed/raw profile
- 네 component의 builder, manifest, audit, output hash 및 W45 input pin
- component의 declared scope와 W45 기준 실제 diff의 일치
- 어떤 coordinate overlap도 payload가 같아도 즉시 실패
- Block 15 width hold, NPC `3956`, reflow hard/semantic hold가 W45와 byte-identical이며 union에 없는지
- final input/target packed/raw hash와 final changed-coordinate scope

외부 게임 설치 경로와 Switch/SC 입력은 읽지 않습니다. Steam/Git/network/release/transaction/apply 기능은 구현하지 않았고, 출력은 아래 private 경로에만 생성됩니다.

`tmp/pc_private_union_composite_wave53_v1/candidate`

실행:

```powershell
py -3 -X utf8 workstreams\pc_private_union_composite_wave53_v1\build_pc_private_union_composite_wave53_v1.py build
py -3 -X utf8 workstreams\pc_private_union_composite_wave53_v1\build_pc_private_union_composite_wave53_v1.py verify-private
py -3 -X utf8 -m unittest workstreams\pc_private_union_composite_wave53_v1\test_pc_private_union_composite_wave53_v1.py -v
py -3 -X utf8 workstreams\pc_private_union_composite_wave53_v1\build_pc_private_union_composite_wave53_v1.py diff-check
```
