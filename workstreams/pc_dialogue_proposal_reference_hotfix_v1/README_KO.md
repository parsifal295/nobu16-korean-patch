# 건의 참조 대사 핫픽스

지도 화면의 건의 안내 대사가 `필요 시 참조해저것`으로 조립되는 문제를
교정한다. 원인은 `참조해` 뒤에서 실행되는 공용 어미 선택기이며, 해당
한국어 분기 하나가 `저것`을 출력한다.

이 작업은 Base `MSG/JP/msggame.bin`의 `15:2255`와 PK
`MSG_PK/JP/msggame.bin`의 `15:2286`만 수정한다. 첫 문장의 정상적인 말투
선택기는 유지하고, 이후의 불필요한 선택기 두 개를 같은 길이의 빈 문자열
바이트코드로 교체한다. 따라서 레코드 및 파일 크기는 변하지 않는다.

현재 확인된 인물 말투에서 최종 표시는 다음과 같다.

```text
조금이나마 참고가 된다면 다행이오
잊지 않도록 건의해 두었으니
필요할 때 참조해 보시오.
```

빌더는 고정된 입력 해시만 받고 `tmp/pc_dialogue_proposal_reference_hotfix_v1/`
아래에만 후보를 쓴다. Steam 설치본이나 배포 ZIP을 직접 수정하지 않는다.

```powershell
python -B workstreams\pc_dialogue_proposal_reference_hotfix_v1\build_pc_dialogue_proposal_reference_hotfix_v1.py verify-input
python -B workstreams\pc_dialogue_proposal_reference_hotfix_v1\build_pc_dialogue_proposal_reference_hotfix_v1.py build
python -B -m unittest -v workstreams\pc_dialogue_proposal_reference_hotfix_v1\test_pc_dialogue_proposal_reference_hotfix_v1.py
```
