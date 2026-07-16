# Switch v2.x 이미지 델타 감사 v1

이 작업 스트림은 공개된 Switch 한글 패치 `v2.0`부터 `v2.4`까지의
`RES_JP/res_lang.bin`을 **읽기 전용**으로 비교한다. 목적은 Steam 일본어판
1.1.7에서 PC 전용으로 다시 그려야 할 휠·버튼 계열 이미지의 정확한 컨테이너
경로와 우선순위를 고정하는 것이다.

특히 v2.1에서 추가된 메인 화면 원형 명령 휠(`/8/0`)과 v2.2에서 함께 바뀐
시스템·내비게이션 버튼 계열을 같은 감사 범위로 묶는다. Switch의 LINK,
LZ4, G1T, BC3 또는 완성 리소스는 PC 파일로 복사하지 않는다.

## 범위

- Switch 공개 배포본: `v2.0`, `v2.1`, `v2.2`, `v2.3`, `v2.4`
- Switch 파일: `NobunagaShinsei_KR/romfs/RES_JP/res_lang.bin`
- PC 입력: Steam 일본어판 1.1.7 `RES_JP/res_lang.bin`
- v2.1 → v2.2 이미지 델타: outer `/5`, `/8`, `/12`, `/13`, `/16`, `/24`

private atlas 검토로 아래의 Switch v2.2 변경 텍스처를 식별했다. 이 목록은
PC 포팅 후보의 우선순위이며, Switch 바이트를 복사하라는 의미가 아니다.

| 우선순위 | Switch 경로 | 확인된 용도 |
| --- | --- | --- |
| P0 | `/8/0`, texture `0` | 메인 화면 원형 명령 휠 |
| P1 (다음) | `/5/0`, texture `1` | 시스템·내비게이션 행동 버튼/상태 아틀라스 |
| P1 | `/12/0`, texture `0` | 군평정·승리·패배·전공 오버레이 |
| P1 | `/13/0`, textures `48..56` | 합전 시작 배너 9종 |
| P1 | `/16/0`, texture `0` | 튜토리얼 흐름도 |
| P2 | `/24/0`, texture `0` | 타이틀 화면 우상단 `追加 → 추가` 라벨만; 타이틀 로고 보존 |

v2.0 → v2.1에서 변경된 outer 항목은 `/8` 하나뿐이므로, 메인 원형 메뉴에
새로 추가된 휠/명령 버튼 이미지는 `/8/0`이 유일하다. `/5/0/texture 1`은
원형 메뉴와 별개의 일반 시스템 버튼 묶음이며 휠 다음 순서로 처리한다.

## 실행

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'

& $py -B workstreams\switch_v2_image_delta_audit_v1\build_switch_v2_image_delta_audit_v1.py audit
& $py -B workstreams\switch_v2_image_delta_audit_v1\build_switch_v2_image_delta_audit_v1.py verify
& $py -B -m unittest workstreams\switch_v2_image_delta_audit_v1\test_switch_v2_image_delta_audit_v1.py -v
```

선택적인 `preview` 명령은 Switch 및 PC 입력을 해독한 PNG를 반드시
`tmp/switch_v2_image_delta_audit_v1/private/` 아래에만 만든다. 공개
workstream에는 SHA-256, 크기, 컨테이너 구조, 델타와 구현 게이트만 보관한다.

## 안전 경계

- 게임 파일·실행 파일·레지스트리·메모리·DLL은 수정하지 않는다.
- Switch raw 파일, G1T, BC3 payload, PNG는 Git에 넣지 않는다.
- 후보 생성 및 적용은 이 감사의 후속 작업이며, 각 outer 항목은 Steam JP의
  PC 구조에서만 재구성하고 나머지 항목을 바이트 보존해야 한다.
