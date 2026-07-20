# PC 원문 기반 W68: PK 이벤트 정식 표제 복원

W68은 W67 사설 후보와 순정 Steam PC 일본어 `msgev.bin`만 읽어, 가타카나
음역으로 남은 PK 이벤트 제목을 같은 PC 리소스 안의 정식 표제 앵커 한국어로
복원한다. 대상은 **23개 정적 제목**이며, 그중 세 제목은 동일 JP 표제가 두
좌표에 있어 함께 수정한다.

## 범위와 보존 조건

- 각 대상의 가타카나 JP 제목과 한자 정식 표제 JP 앵커를 함께 고정한다.
- 대상 한국어는 해당 앵커의 현재 PC 한국어와 정확히 같아야 한다. 새 번역문을
  합성하지 않는다.
- `라이진`은 추측 음역이 아니라 PC 앵커 `雷神を継ぐ者`의 기존 표제인
  `뇌신을 잇는 자`를 사용한다.
- `14386=14622`, `14391=14621`, `14403=14627`의 같은 제목은 동일한 한국어로
  함께 고친다.
- 모든 대상은 LF, ESC/tag, 런타임 토큰, printf 토큰, 기타 제어 바이트가 없고,
  실제 활성 글꼴의 최대 폭은 `528px`로 912px 기준 안이다.

후보는 `tmp/pc_event_title_canonical_wave68_v1/candidate-final/` 아래에만
생성된다. Steam 적용·트랜잭션·Git·네트워크·릴리즈 기능은 없다.

```powershell
python -B -X utf8 workstreams\pc_event_title_canonical_wave68_v1\build_pc_event_title_canonical_wave68_v1.py profile
# profile 결과를 EXPECTED_FINAL_* 상수에 먼저 고정한다.
python -B -X utf8 workstreams\pc_event_title_canonical_wave68_v1\test_pc_event_title_canonical_wave68_v1.py
python -B -X utf8 workstreams\pc_event_title_canonical_wave68_v1\build_pc_event_title_canonical_wave68_v1.py build
python -B -X utf8 workstreams\pc_event_title_canonical_wave68_v1\build_pc_event_title_canonical_wave68_v1.py diff-check
```
