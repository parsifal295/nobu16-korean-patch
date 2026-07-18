# Wave 16: 정적 인물 대사 6개 활용 보정 후보

Wave 14가 적용된 현재 Steam PC 프로필을 입력으로 고정하고, 한국어 리터럴 뒤에 남아 문장을 미완성으로 만들던 일본어 `01 43 <u32>` 활용 명령을 정적 인물 대사 6개에서만 제거한다. 이 워크스트림은 **후보 생성 전용**이며 Steam 적용, Git 푸시·커밋, 릴리즈 생성 기능을 포함하지 않는다.

## 대상

| Base | PK | 최종 한국어 리터럴 |
| --- | --- | --- |
| `8:398` | `8:410` | `알겠습니다.` + `\n후임에게 모든 것을 인계하겠습니다.` |
| `8:969` | `8:981` | `몸소 개입하여\n이 조략을 막아 내겠습니다.` |
| `15:2261` | `15:2292` | `알겠습니다.` + `\n출진 채비에 들어가겠습니다.` |

각 레코드는 다음을 모두 고정 검증한다.

- 현재 Wave 14 Steam 입력 레코드 SHA-256·크기·한국어 리터럴·`01 43` 바이트열
- 입력 opaque span 전체와 `01 43` 제거 뒤의 정확한 opaque layout
- 리터럴 마커 수·토폴로지 보존 및 최종 `05 05 05` 종결자 보존
- 출력 레코드 SHA-256·크기, 출력 `msggame.bin` SHA-256·크기, 변경 좌표 정확히 6개
- 기존 수동 줄바꿈 수 유지 및 최종 명시 줄 수 3줄 이하

## PC 근거

근거는 순정 **PC 일본어** Base/PK와 Steam PC PK의 EN/SC/TC 레코드만 사용한다. Base에는 설치된 EN `msggame.bin`이 없으므로, 같은 일본어 리터럴을 가진 PK 대응 좌표를 통해 EN/SC/TC를 앵커로 삼는다.

| 대화 | PC JP | PK EN |
| --- | --- | --- |
| 후임 인계 | `かしこま` / `後任に引き継` | `Acknowledged. I shall impart everything to my successor.` |
| 직접 개입 | `自ら介入し\nこの調略を阻んで参` | `I shall step in myself to ensure that these schemes are put to an end.` |
| 출진 준비 | `かしこま` / `出陣の手配に移` | `Understood. We will begin preparations to march.` |

SC/TC도 해당 PK 좌표의 리터럴과 남아 있는 명령 바이트까지 고정한다. 특히 직접 개입 대화의 SC/TC에는 문장 의미와 별개로 `014301000000`이 남아 있으므로, 이를 지우거나 일반화하지 않고 앵커 상태 그대로 검증한다.

Switch 한국어·과거 한국어 번역본은 읽지 않는다.

## 입력·출력 고정값

| 파일 | Wave 14 입력 SHA-256 | Wave 16 후보 SHA-256 |
| --- | --- | --- |
| `MSG/JP/msggame.bin` | `4D147A4AD73466E882043D8A5E47F0D4DAF37473702A8CEABAEFFBF4E76F2EB8` | `EEA622999F38C72F2088467E04D4A885B684D3FD3CF99FB72879A72079CF9351` |
| `MSG_PK/JP/msggame.bin` | `BD789D1C5230159433BDB9F2FCBE4B0ABABF9D84FAD2FE1C16EED45B071CE860` | `9EB0FD80E7A6D50BC2A6073FDBF213E7BDB685D81DFCD9191C9C86E415D7EFCC` |

나머지 Steam 텍스트 프로필 9개도 Wave 14 입력 해시와 바이트 단위로 일치해야 빌드가 시작된다. 입력이 다르면 빌더는 재베이스하지 않고 실패한다.

## 검증과 후보 생성

```powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_dialogue_quality_wave16_static_inflection_v1\build_pc_dialogue_quality_wave16_static_inflection_v1.py hash
& $py -B -m unittest workstreams\pc_dialogue_quality_wave16_static_inflection_v1\test_pc_dialogue_quality_wave16_static_inflection_v1.py
& $py -B workstreams\pc_dialogue_quality_wave16_static_inflection_v1\build_pc_dialogue_quality_wave16_static_inflection_v1.py build
```

`build`는 `tmp/pc_dialogue_quality_wave16_static_inflection_v1/` 아래에만 11파일 후보 프로필, audit, manifest를 쓴다. Steam 경로를 쓰거나 변경하지 않으며, 이 워크스트림에는 적용 명령이 없다.
