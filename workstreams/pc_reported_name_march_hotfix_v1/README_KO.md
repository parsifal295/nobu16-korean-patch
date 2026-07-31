# v0.90.1 제보 성씨·진군 알림 핫픽스

제보 화면의 두 현상을 v0.90.1 최종 리소스에서 추적한 작업이다.

- 동적 성씨 조각 ID `757`이 Wave 29에서 `초 `에서 일반명사 `부족`으로 잘못 덮였다. Base `MSG/JP/strdata.bin` 블록 0과 PK `MSG_PK/JP/msgdata.bin`의 같은 ID를 모두 `초 `로 복원한다. 뒤 공백은 이름 조합에 필요한 데이터이므로 유지한다.
- Base `MSG/JP/msggame.bin`의 알림 `6:4137`은 v0.90.1 최종 리소스에서 이미 `오노데라 가문의 요코테성으로 / 진군 중입니다`로 교정되어 있다. 이 파일은 바꾸지 않고, 두 선택자와 종결 호출 `0:556`, 세 리터럴, 정중형 최종 조합을 회귀 계약으로 고정한다.

빌더는 v0.90.1의 정확한 10파일 해시를 입력 계약으로 사용한다. 격리된 `tmp/pc_reported_name_march_hotfix_v1/` 아래에만 후보를 쓸 수 있으며 Steam 설치본 적용, 번들 생성, 배포 기능은 없다.

```powershell
python -B workstreams\pc_reported_name_march_hotfix_v1\build_pc_reported_name_march_hotfix_v1.py verify-input
python -B workstreams\pc_reported_name_march_hotfix_v1\build_pc_reported_name_march_hotfix_v1.py build
python -B -m unittest -v workstreams\pc_reported_name_march_hotfix_v1\test_pc_reported_name_march_hotfix_v1.py
```
