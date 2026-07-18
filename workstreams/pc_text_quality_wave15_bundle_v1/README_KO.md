# Wave 15 + Wave 16 JP_TEXT_AUDIT private bundle

이 작업물은 이미 검증된 두 private 후보를 조립해 정확히 11개 파일의
JP_TEXT_AUDIT 후보를 만든다.

- Wave 16: Base/PK 대화 정적 보정 후보
- Wave 15: PK 이벤트 인물명 후보

Steam 게임 파일, Git, 릴리즈, 트랜잭션을 만들거나 적용하는 기능은 없다.
빌더가 읽는 것은 두 source candidate와 그 고정 audit/manifest뿐이며,
출력은 이 작업물 전용 tmp 아래에서만 허용한다.

## 최종 11파일 프로필

Wave 14 기준 11파일 프로필에서 아래 3파일만 바뀐다.

| 파일 | 최종 SHA-256 |
| --- | --- |
| MSG/JP/msggame.bin | EEA622999F38C72F2088467E04D4A885B684D3FD3CF99FB72879A72079CF9351 |
| MSG_PK/JP/msgev.bin | CE1A61E6C0F85A3E7F0FD4C1DD1BF0349A99CC134A9D73B7DE1917DB6646A0C3 |
| MSG_PK/JP/msggame.bin | 9EB0FD80E7A6D50BC2A6073FDBF213E7BDB685D81DFCD9191C9C86E415D7EFCC |

나머지 8파일은 Wave 14 current SHA-256를 그대로 유지해야 한다.
Wave 16 source profile과 비교하면 PK MSGEV 하나만 교체된다.

## source candidate 고정값

| source | 검증 범위 |
| --- | --- |
| Wave 16 | 11파일 프로필 전체의 경로, 크기, SHA-256 및 audit/manifest SHA-256 |
| Wave 15 | MSG_PK/JP/msgev.bin의 크기 994,711 bytes, SHA-256 CE1A… 및 audit/manifest SHA-256 |

Wave 16의 Base MSGGAME과 PK MSGGAME은 그대로 복사한다. Wave 15의
MSGEV만 Wave 16의 기존 MSGEV 위에 교체한다. 최종 프로필은 다시
파일별 hash map으로 검사하며, Wave 14 대비 변경 경로가 정확히 3개인지
fail-closed로 확인한다.

MSGEV 안에서는 Wave 15의 텍스트 차이가 ID 3015, 3016, 3084 세 건뿐인지
현재/후보 UTF-16LE SHA-256으로 다시 확인한다.

## 사용

~~~powershell
$py = 'C:\Users\melse\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $py -B workstreams\pc_text_quality_wave15_bundle_v1\build_pc_text_quality_wave15_bundle_v1.py hash
& $py -B -m unittest workstreams\pc_text_quality_wave15_bundle_v1\test_pc_text_quality_wave15_bundle_v1.py
& $py -B workstreams\pc_text_quality_wave15_bundle_v1\build_pc_text_quality_wave15_bundle_v1.py build
& $py -B workstreams\pc_text_quality_wave15_bundle_v1\build_pc_text_quality_wave15_bundle_v1.py verify-private --candidate-root tmp\pc_text_quality_wave15_bundle_v1\candidate-v1
~~~

build는 tmp/pc_text_quality_wave15_bundle_v1/candidate-v1 아래에 11파일,
audit.v1.json, bundle_manifest.v1.json만 새로 만든다. 이미 존재하는 출력
디렉터리는 덮어쓰지 않으며 tmp 밖 경로는 거부한다.
