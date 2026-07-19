# PC PK 이벤트 색상 태그 내부 LF safe reflow 후보

이 workstream은 Steam PC의 현재 W45 한국어 `MSG_PK/JP/msgev.bin`에서 정확히 7개 레코드만 다시 조립하는 **private 후보**다. 색상 태그 내부에서 단어·인명·가문명이 LF로 갈라져 보이는 문제를, 검토한 절 경계로만 재배치한다. Steam 설치 파일, 트랜잭션, Git, 네트워크, release에는 쓰지 않는다.

- W45 입력 packed SHA-256: `01287E2ECC5328C85348657EFF06553353CB8664B0FB7E1669DB9FC591D53EBE`
- W45 입력 raw SHA-256: `F3716AB98D60931CEC0FE61976D8DAD386C05B30B7167BD1BDB2CDF02EC55ACC`
- 후보 packed SHA-256: `AC1398EA909295AFA966D29E98F49F4F1B6C65D0BA870A51024721F91AB30D79`
- 후보 raw SHA-256: `1A65DB1B7206B98D5A2600261064862A2E49DE52409DEB18EB4D07B955F25EC9`
- private 출력: `tmp/pc_event_color_tag_reflow_v1/candidate/`

## 근거와 범위

입력은 오직 `F:\SteamLibrary\steamapps\common\NOBU16\MSG_PK\JP\msgev.bin`의 W45 pin이다. 일본어는 같은 `msgev.bin`의 pristine PC JP backup만 읽어 표기와 자연스러운 절 경계를 다시 확인했다.

- pristine PC JP packed SHA-256: `03426B59D32EB628021DE43BC02FF82B56B04D97C25CE37F735630EA7C4E2002`
- PC EN/SC/TC는 각 레코드와 파일 hash로 묶은 **context evidence only**이며, 새 한국어 문구를 생성하는 입력으로 쓰지 않는다.
- Nintendo Switch 경로나 파일, 번역은 읽지 않는다. 빌더도 경로 성분에 `switch`가 있으면 읽기 전에 중단한다.
- W49 정적 후보의 선언 ID set과 빌더 hash를 pin하고, 하나라도 겹치면 중단한다.

변경 ID는 `3237, 3477, 3832, 3896, 3919, 4011, 4020`뿐이다. 일곱 target은 빌더에 literal로 고정되어 있으며, 자동 폭 맞춤·일괄 reflow·문자열 치환은 없다.

| ID | PC JP 재확인 초점 | actual font widths (px) |
| --- | --- | --- |
| 3237 | 浅井家·朝倉의 맹우 관계 | 672 / 888 / 600 |
| 3477 | 織田家와 天下의 대조 | 600 / 816 / 168 |
| 3832 | 細川晴元 인명과 주군 조건 | 432 / 456 / 504 |
| 3896 | 吉川家 양자·吉川元春 개명 절 | 720 / 480 / 768 |
| 3919 | 小早川家·元就·大内義隆의 행동 순서 | 696 / 480 / 912 |
| 4011 | 細川家에서 三好家로의 탈바꿈 | 504 / 432 / 768 |
| 4020 | 尾張の虎·織田信秀의 죽음과 織田家 동요 | 408 / 720 / 912 |

각 target은 다음을 전부 검증한다.

- 현재 W45 preimage UTF-16LE hash와 target exact hash
- pristine PC JP 및 PC EN/SC/TC의 해당 source/context UTF-16LE hash
- JP anchor와 절 경계 재검토 기록
- ESC 순서, runtime token, printf token, C0 control, 앞뒤 공백 불변
- 모든 비공백 문자 불변; 검토된 내부 공백/LF topology만 변경
- 정확히 3줄, active PC event font 실제 폭으로 줄당 최대 912px
- 재압축 packed/raw pin, raw table 및 packed round trip, 변경 ID scope exact

## 명시적 hold

다음 hard hold는 어떤 경우에도 이 후보에 넣지 않으며, 후보 조립 뒤에도 원문과 같음을 확인한다.

`3202, 3900, 3934, 4140, 8723, 9359, 10045`

`8510`은 reflow가 아닌 semantic hold로 별도 보류한다. 이 후보는 hold를 포함하지 않고, 앞의 7개 literal target 이외의 blind reflow를 수행하지 않는다.

## 실행 및 검증

```powershell
python .\workstreams\pc_event_color_tag_reflow_v1\build_pc_event_color_tag_reflow_v1.py build
python .\workstreams\pc_event_color_tag_reflow_v1\build_pc_event_color_tag_reflow_v1.py verify-private
python -m unittest -v .\workstreams\pc_event_color_tag_reflow_v1\test_pc_event_color_tag_reflow_v1.py
git diff --check
```

`build`는 기존 candidate를 덮어쓰지 않는다. 출력은 private tmp root 아래에만 생기며, `verify-private`는 파일 집합·packed 후보·audit·manifest가 모두 pin과 같은지 확인한다.

실게임 적용이나 이미지 QA는 이 workstream의 범위가 아니며 수행하지 않았다.
