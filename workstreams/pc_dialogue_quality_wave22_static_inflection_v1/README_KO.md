# PC 대화 품질 Wave 22 — 정적 `01 43` 종결 복구

Wave 22는 Wave 20의 완전한 11파일 private candidate만 입력으로 고정한다. Base/PK `msggame.bin`의 고신뢰 대화 13쌍(26 records)만 다시 만들며, Steam 설치본·원본 게임·Git·릴리스에는 쓰지 않는다.

각 대상은 PC Base/PK JP와 PK EN/SC/TC의 동일 좌표 whole-record SHA-256으로 의미 앵커를 고정한다. 입력 record의 marker 개수·순서는 유지하고, 각 opaque span에서는 완전한 `01 43 <u32>` 명령만 제거한다. 그 밖의 opaque 바이트와 최종 `05 05 05`는 byte-identical로 보존한다.

## 적용 13쌍

| Base → PK | 정적 한국어 결과 |
| --- | --- |
| `2:557 → 2:574` | 배웅해 주셔서 감사하오. / 좋은 소식을 기다려 주시오. |
| `6:4151 → 6:4181` | 주위에 공략할 성이 없어 / 영내 발전에 힘쓰고 있습니다. / 모든 취락은 이미 장악했습니다. |
| `6:4178 → 6:4208` | 알겠습니다. / 반드시 주명에 걸맞은 성과를 / 가문에 가져오겠습니다. |
| `6:4179 → 6:4209` | 알겠습니다. / 당가를 위해 주명을 완수하고자 / 전력을 다하겠습니다. |
| `6:4181 → 6:4211` | 적성 공략의 뜻을 각 성주에게 전했더니 / 다음 성에서 구체안이 나왔습니다. / 어느 성주의 계책을 쓸지 명해 주십시오. |
| `6:4391 → 6:4450` | 알겠습니다. |
| `6:4392 → 6:4451` | 알겠습니다. / 임무와 전투가 끝나는 대로 / 착수하겠습니다. |
| `6:4393 → 6:4452` | 알겠습니다. / 전투에서 돌아오는 대로 / 착수하겠습니다. |
| `6:4394 → 6:4453` | 알겠습니다. / 임무를 마치는 대로 / 착수하겠습니다. |
| `6:4404 → 6:4463` | 과연, 창을 다룰 이를 원하시는군요. / 하지만… 인선은 재고해 주십시오. |
| `6:4439 → 6:4498` | 후방에서 백성을 섬기는 것이 본분이오. / 부디 영주로 임명해 주시오. |
| `6:4456 → 6:4515` | 어느 땅에서든 당가를 위해 / 전력을 다하겠습니다. |
| `6:4460 → 6:4519` | 혹시 저를 해임하려 하십니까? / 부디 다시 생각해 주십시오… |

모든 줄은 실제 PC JP 폰트의 advance로 재측정하며 최대 912px을 넘지 않는다.

## 보류 7쌍

- `1:21 → 1:21`: JP placeholder 및 빈 다국어 문맥
- `6:2253 → 6:2259`: 주어·목적어 결손
- `6:4225 → 6:4255`: 행위자 없는 조사 시작 fragment
- `6:4441 → 6:4500`: 주어와 시점이 다국어별로 불일치
- `6:4458 → 6:4517`: 동적 행위자·문법 의존
- `7:263 → 7:267`: 대상 토큰 결손
- `7:265 → 7:269`: 대상 토큰 결손

`derive_wave22_specs.py`는 builder 상수의 근거를 읽기 전용으로 재추출한다. Windows CP949 stdout에서도 UTF-8 재설정 및 ASCII JSON으로 실행할 수 있으며, regression test가 이를 확인한다.

## 실행

```powershell
python -B .\build_pc_dialogue_quality_wave22_static_inflection_v1.py hash
python -B .\test_pc_dialogue_quality_wave22_static_inflection_v1.py
python -B .\build_pc_dialogue_quality_wave22_static_inflection_v1.py build
python -B .\build_pc_dialogue_quality_wave22_static_inflection_v1.py verify-private `
  --candidate-root ..\..\tmp\pc_dialogue_quality_wave22_static_inflection_v1\candidate
```
