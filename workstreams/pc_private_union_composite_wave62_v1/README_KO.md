# PC 비공개 통합 후보 W62

W62는 W61 위에 직접 PC 일본어 원문으로 다시 확인한 Base `msggame.bin` 대사 4건과 PK `msgev.bin` 이벤트 20건만 덧씌우는 후보다. Switch 또는 다른 플랫폼/언어의 번역 파일은 읽지 않는다.

| 좌표 | 현재 한국어 | 수정 한국어 | 직접 PC 일본어 |
| --- | --- | --- | --- |
| `16:3:0` | `노력이 남는다면\n성하의 시설을…` | `여력이 남는다면\n성하의 시설을…` | `労力が余るならば\n城下の施設を…` |
| `16:14:0` | `서둘러 싸움에 대비해\n수하를 정비해야겠군` | `서둘러 싸움에 대비해\n병력을 정비해야겠군` | `急ぎ、戦に向けて\n手勢を整えねば` |
| `16:19:0` | `때는 지금…아니\n아직, 이겠지` | `때는 지금…아니\n아직은 아니겠지` | `時は今…いや\nまだ、だろうな` |
| `16:22:0` | `큭큭, 다음엔 무엇을\n걸어 볼까` | `큭큭, 다음엔 무엇을\n꾸며 볼까` | `くっく、次は何を\n仕掛けてやろうか` |

네 record는 모두 `literal marker + UTF-16 텍스트 + end`만 가진 단일 정적 literal이다. 수동 줄바꿈의 위치와 개수, 그리고 literal 밖 제어 바이트는 그대로 보존한다. `16:48`의 `영내 제책`은 `0143` 제어 명령이 있어 이 후보에 넣지 않고 실게임 조립 검증 대상으로 보류한다.

## 이벤트 20건

- `6408`: `飼い殺し`를 ‘쓸모없다’로 축소한 부분을 ‘유폐된 채’로 바로잡고, `元親`에게의 종속 관계를 복원한다. 기존 3줄과 색상 태그 순서는 그대로다.
- `6588`: `国替え`의 대상인 ‘전봉’을 복원한다. 기존 3줄과 `[b1871]` 런타임 토큰은 그대로다.
- `9811`, `9813`, `9851`, `9877`, `9878`, `9910`, `9912`, `9913`, `9921`, `9924`, `9932`, `10482`, `10486`, `10487`, `10493`, `10507`, `10508`, `10532`: 직함 `内府`의 기존 프로젝트 표기인 `내대신`으로 통일한다. 각 문자열에서 `나이후` 한 번만 바꾸며 태그·개행은 보존한다.

이벤트 `4960`, `10386`, `10483`, `10484`는 이름/색상 태그가 서로 뒤섞인 것이 확인됐지만 런타임 조립과 실제 이벤트 화면 확인이 필요하므로 이번 정적 후보에서 제외한다. 전체 이벤트를 재대조한 결과 새로 확정된 색상 태그 내부 개행·미종결 태그·CR/CRLF 오류는 없었다.

후보는 `tmp/pc_private_union_composite_wave62_v1/candidate/` 아래에만 생성한다. 이 빌더 자체는 Steam 파일, Git, 네트워크, 공개 릴리즈를 조작하지 않는다.

```powershell
python -B -X utf8 workstreams\pc_private_union_composite_wave62_v1\test_pc_private_union_composite_wave62_v1.py
python -B -X utf8 workstreams\pc_private_union_composite_wave62_v1\build_pc_private_union_composite_wave62_v1.py profile
python -B -X utf8 workstreams\pc_private_union_composite_wave62_v1\build_pc_private_union_composite_wave62_v1.py build
python -B -X utf8 workstreams\pc_private_union_composite_wave62_v1\build_pc_private_union_composite_wave62_v1.py verify-private
python -B -X utf8 workstreams\pc_private_union_composite_wave62_v1\build_pc_private_union_composite_wave62_v1.py diff-check
```
