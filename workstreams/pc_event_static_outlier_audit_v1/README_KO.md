# PK 이벤트 폭 초과 3행 UI 경로 감사

최신 Wave101 private candidate의 `MSG_PK/JP/msgev.bin` 전체 정적 스캔에서 raw G1N 1440px(실효 912px)를 넘는 한 줄은 17862–17864 세 행뿐이다. 이 작업물은 세 행에 개행을 임의로 넣지 않고, 해당 문자열이 Static Patch 007의 4줄 이벤트 대사 상자인지 별도 조건·결과 UI인지 판정하기 위한 읽기 전용 감사다.

Wave101은 Wave100 대비 3489–3526 범위의 15행만 바꾼 후보다. 빌더는 실제 변화 ID가 그 15행과 정확히 일치하고, 17862–17864가 Wave100과 바이트상 문자열 단위로 동일함을 매번 검증한다.

## 판정

- 세 행은 각각 raw/실효 `1896/1185`, `1464/915`, `1512/945`로 912px 대사 기준을 한 줄에서 넘는다.
- 그러나 인접 구간은 날짜·외교·신분·병량·금전·관계 상태, 역사 이벤트 제목, 결과 수 선택, `취임`/`해임`, `결과에 변동` 안내 등 조건·결과 UI 문자열로 구성돼 있다. 연속 이벤트 대사 장면이 아니다.
- 순정 PC JP와 PC EN/SC/TC는 모두 같은 “무장이 이탈하고 새 가문이 탄생” 의미를 보이며, 줄바꿈은 없다. JP 원문 개행을 한국어 규칙으로 이식하지 않았다.
- 동일 JP 문구가 Base `MSG/JP/ev_strdata.bin`의 17814–17816에도 있다. 이는 공용 조건·결과 문자열 풀의 근거지만, Base와 PK의 렌더러가 같다는 근거는 아니다.
- 따라서 현재 정적 근거만으로는 세 행이 Static Patch 007 대사 상자를 탄다고 증명되지 않는다. 반대로 다른 위젯이라고 완전히 확정한 것도 아니다.

결론은 **`renderer_path_hold`**다. 문장 축약·삭제·수동 개행은 하지 않았고 후보 바이너리도 만들지 않았다. 실제 표시 경로/대사 상자 폭이 확인되기 전까지 한 줄을 보존한다.

## 산출물과 검증

- 공개 ledger: [pc_event_static_outlier_audit.v1.json](public/pc_event_static_outlier_audit.v1.json)
- 입력: `tmp/pc_event_kanto_quality_wave101_v1/candidate-final/`
- Steam 설치본·Git·릴리스·네트워크에는 쓰지 않는다.

```powershell
python workstreams\pc_event_static_outlier_audit_v1\build_pc_event_static_outlier_audit_v1.py build
python workstreams\pc_event_static_outlier_audit_v1\build_pc_event_static_outlier_audit_v1.py verify
python workstreams\pc_event_static_outlier_audit_v1\test_pc_event_static_outlier_audit_v1.py
```
