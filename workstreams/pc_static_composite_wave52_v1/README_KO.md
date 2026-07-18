# Wave 52: W45 기반 정적 텍스트 합성 후보

이 작업물은 현재 Steam 설치본의 정확한 W45 프로필을 기준으로, 아래 여섯 **private 정적 후보**의 변경 레코드만 다시 추출해 하나로 합친다. 각 컴포넌트의 완성된 packed 파일을 통째로 복사하지 않고, W45와 비교한 변경 레코드만 합쳐 재빌드한다.

| 리소스 | 합성 변경 수 | 출력 packed SHA-256 | 출력 raw SHA-256 |
| --- | ---: | --- | --- |
| `MSG/JP/msggame.bin` | 59 | `367FBCD48FA824955508747A49FD4424798262C3BE75D7A67A10D859CB46B319` | `54F18AB680E94783E3A8D24D982236AC0FCC7D39DE76C4C9DBFA993A4CB92F35` |
| `MSG_PK/JP/msggame.bin` | 157 | `8864670A0CFB2E55C031E0A72C64FAD19D172A556123082E9E75223BD07DC106` | `CDA0FD14D0C84AE7ACA81A74A1E51951274AD9ADDD6E6C755F645F17FDBD02F6` |
| `MSG_PK/JP/msgev.bin` | 33 | `AC9C0F7FE72ADA6FA4604C1359A3FFA155BB5C166A590C3FC77BAD7C390CC90B` | `F43E2742C8D9CDAA59861C5FC9011C68C3807641D97AFDAF46AFE2521BB9AA86` |

총 249건이다.

포함 범위는 다음 후보의 실제 변경 레코드뿐이다.

- Wave 47: 전투 대사 정적 34건
- Wave 48: 정적 `0143` UI 계열 32건
- Wave 49: 이벤트 정적 33건
- Wave 50: 블록 9–12 정적 대사 56건
- Wave 51: 블록 13–14 정적 튜토리얼/도움말 54건
- Wave 51: 정적 terminal `0143` 40건

빌더는 모든 컴포넌트가 W45 입력 프로필에서 출발했는지, 컴포넌트 output hash와 manifest/audit 결합이 맞는지, 실제 바뀐 좌표가 선언 범위와 같은지 확인한다. 좌표가 한 번이라도 겹치면(내용이 같아도) 중단한다.

`pc_dialogue_runtime_repair_wave46_v1`는 명시적으로 제외한다. 또한 위 여섯 후보의 실제 output에 없는 런타임 이름·어미, 수동 줄바꿈 재배치, 색상 태그, 화면 폭/실게임 QA 보류 행은 이 합성 후보에 들어갈 수 없다. 이 후보가 존재한다고 실게임 화면 QA가 끝난 것은 아니다.

이 빌더에는 Steam 적용, transaction, Git, 네트워크, 릴리즈 기능이 없다. 출력은 다음 private 경로로만 생성된다.

`tmp/pc_static_composite_wave52_v1/candidate`

실행:

```powershell
py -3 -X utf8 workstreams\pc_static_composite_wave52_v1\build_pc_static_composite_wave52_v1.py build
py -3 -X utf8 workstreams\pc_static_composite_wave52_v1\build_pc_static_composite_wave52_v1.py verify-private
py -3 -X utf8 -m unittest workstreams\pc_static_composite_wave52_v1\test_pc_static_composite_wave52_v1.py -v
```
