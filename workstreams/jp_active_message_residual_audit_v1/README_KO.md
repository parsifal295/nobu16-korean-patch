# 활성 Steam JP 메시지 잔여 감사 v1

이 작업은 Steam PK 실행 시 실제 참조되는 JP 리소스만 읽어, 남아 있는 일본어를 정량화하는 감사 도구다. 게임 설치본, 후보 게임 파일, 릴리즈, GitHub에는 쓰지 않는다.

## 범위와 판정

- 대상: `MSG/JP/{msggame,strdata,ev_strdata}.bin`, `MSG_PK/JP/{msgbre,msgdata,msgev,msggame,msgire,msgstf,msgui}.bin`
- `MSG/SC`, `MSG_PK/SC` 카탈로그는 과거 경로이므로 적용 근거나 잔량 수치에 사용하지 않는다.
- 가나가 있고 한글이 없는 문자열만 **고신뢰 잔여 일본어**로 센다.
- 한자만 있는 문자열과 한글·가나 혼합 문자열은 자동 번역 대상이 아닌 검토 항목으로 분리한다.
- 결과물에는 원문·번역문을 기록하지 않고 좌표와 UTF-16LE SHA-256만 기록한다.

스크린샷의 국력 안내 대사는 `MSG/JP/msggame.bin`의 `block=13, record=217, literal=0`이며, PK 실행 중에도 기본 리소스 경로가 사용된다는 근거는 [튜토리얼 경로 추적](../tutorial_dialogue_trace_msggame_v1/README_KO.md)에 있다. 감사 시 해당 좌표가 현재 한글 해시와 일치하는지 별도로 확인한다.

## 실행

```powershell
$py = 'C:\Users\melse\AppData\Local\Programs\Python\Python312\python.exe'
& $py -B workstreams\jp_active_message_residual_audit_v1\build_jp_active_message_residual_audit_v1.py `
  --steam-root 'F:\SteamLibrary\steamapps\common\NOBU16'
& $py -B -m unittest workstreams\jp_active_message_residual_audit_v1\test_jp_active_message_residual_audit_v1.py -q
```

생성 파일:

- `validation.active_steam.v1.json`: 활성 파일 해시, 파서 결과, 잔량 집계, 튜토리얼 앵커, 병렬 작업 제안
- `public/active_jp_remaining_coordinates.v1.json`: 상용 원문 없이 좌표·해시만 담은 번역 작업 계약

## 안전한 다음 적용 경로

번역자는 공개 좌표 계약을 기준으로 새 JP 전용 오버레이를 만든다. 통합자는 활성 파일 해시를 먼저 고정하고, 각 좌표의 JP 원문 해시를 확인한 뒤 스테이징 후보만 재조립한다. 파서 왕복·미변경 좌표 보존 검증을 통과한 뒤에만 별도 승인된 배포 단계로 넘긴다. 이 감사 작업 자체는 Steam 설치본 또는 릴리즈를 변경하지 않는다.
