# Wave 20 JP_TEXT_AUDIT private bundle

이 작업물은 검증된 private 후보 두 개를 조합해 최종 11파일 `JP_TEXT_AUDIT` 후보를 만든다.

- Wave 21: 인물 대사 정적 품질 보정이 반영된 11파일 전체 프로필
- Wave 18: `MSG_PK/JP/msgev.bin`의 이벤트 정적 표기 8건 보정 후보

Wave 20은 Wave 21 프로필을 기준으로 `MSG_PK/JP/msgev.bin` 하나만 Wave 18 출력으로 교체한다. 나머지 10파일은 Wave 21 바이트를 그대로 유지하며, 특히 Issue 61 보존 경로인 아래 두 파일은 해시와 바이트 동등성을 별도로 검증한다.

- `MSG/JP/strdata.bin`
- `MSG_PK/JP/msgdata.bin`

## 고정 입력과 최종 프로필

입력 후보의 audit/manifest 바이트, 11파일 경로·크기·SHA-256, Wave 18의 8개 이벤트 ID와 UTF-16LE 텍스트 해시를 모두 고정 검증한다. 최종 프로필은 Wave 21과 비교해 `MSG_PK/JP/msgev.bin`만 달라야 한다.

| 파일 | 최종 SHA-256 |
| --- | --- |
| `MSG/JP/ev_strdata.bin` | `BF224468BFBCF3CC71DFF4609142A60D75091813281EE6F2333645413AD81B80` |
| `MSG/JP/msggame.bin` | `C00B78165B06A5A9D2BFBE134E847E4B00EC3E5243EE9A1981BA1BB68CFA79C6` |
| `MSG/JP/strdata.bin` | `6E7DD096A999299C43A9A23D9E99F75C81D6A9C8116488EC541A43423871B933` |
| `MSG_PK/JP/msgbre.bin` | `E3FA61B46E6E08F9FE57A36C1F11C367DD448A9BA63003CA5AB0F2D2BDBBB939` |
| `MSG_PK/JP/msgdata.bin` | `73CF194E4EF81C20692A245DAC75C3B2A9FCF1A997B7F6755D89DBB59149F2ED` |
| `MSG_PK/JP/msgev.bin` | `D922E7C2B0BD4078A5DB14C87973ECB7BB1A62A4CA2EA30A03A231AB40C1E86B` |
| `MSG_PK/JP/msggame.bin` | `0C3C2196E59BCBC1A066DF7097B37C281F8A6236DE70876CCD7BCAB44459BEA9` |
| `MSG_PK/JP/msgire.bin` | `46244B588B6B3E39CEF67E1145E561DD5F4CBC177D2EDF98178FFC474E536DAB` |
| `MSG_PK/JP/msgstf.bin` | `13A3D3452A226090045372F4676615AFA51B60593D048400045AE4892B90929B` |
| `MSG_PK/JP/msgstf_ce.bin` | `06D0C248CB50BB5A1D131FDB8DE0951C719AA638F2B59AC765E72DEF5541FC63` |
| `MSG_PK/JP/msgui.bin` | `5266AEBE9A0B39C6C85A226F2787179F404899A09B286A77036060FDA99AF0A7` |

## 실행

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_text_quality_wave20_bundle_v1\build_pc_text_quality_wave20_bundle_v1.py hash
& $py -B -m unittest workstreams\pc_text_quality_wave20_bundle_v1\test_pc_text_quality_wave20_bundle_v1.py
& $py -B workstreams\pc_text_quality_wave20_bundle_v1\build_pc_text_quality_wave20_bundle_v1.py build
& $py -B workstreams\pc_text_quality_wave20_bundle_v1\build_pc_text_quality_wave20_bundle_v1.py verify-private --candidate-root tmp\pc_text_quality_wave20_bundle_v1\candidate-v1
```

`build`는 `tmp/pc_text_quality_wave20_bundle_v1/candidate-v1` 아래에만 새 후보를 만들고, 기존 출력은 덮어쓰지 않는다. Steam 게임 파일, Git, 푸시, 릴리즈, 트랜잭션, 네트워크 작업은 구현되어 있지 않다.
