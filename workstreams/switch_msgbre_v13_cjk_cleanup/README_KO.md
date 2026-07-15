# Switch v1.3 `msgbre` 잔존 문자 정리 3건

Switch v1.3의 `strdata.bin`은 v1.1과 바이트 단위로 같습니다. 기존 엄격 이식에서
원문 문자 표기가 1~2자 남아 제외된 PK 열전 ID `944`, `1104`, `1238`만 다룹니다.

문장 전체를 다시 번역하지 않습니다. 깃발 이름의 뜻풀이, 투구 글자의 음가,
오래되었다는 뜻의 괄호 표기만 한글로 최소 치환합니다. 세 결과는 모두 다음을
통과해야 생성됩니다.

- 기존 공개 `msgbre` 오버레이 2,203건과 불겹침
- pristine SC에서 실제 문자가 있는 번역 목표 내부
- `printf`, 퍼센트, 이스케이프, 제어 문자, 개행, 사용자 영역 문자, 앞뒤 공백 보존
- 공개 오버레이와 근거, 검토 색인, 검증 자료에 한자 및 가나가 없음
- 완성 게임 파일과 상용 원문이 배포 자료에 없음
- 격리 2회와 최종 1회의 산출물이 바이트 단위로 같음

재생성:

```powershell
python -B workstreams/switch_msgbre_v13_cjk_cleanup/build_switch_msgbre_v13_cjk_cleanup.py
python -B -m unittest workstreams.switch_msgbre_v13_cjk_cleanup.tests.test_switch_msgbre_v13_cjk_cleanup -v
```

생성기는 저장소 내부 작업물만 쓰며 게임 설치 파일은 수정하지 않습니다. 실제 화면
검토 전이므로 검토 색인의 `runtime_reviewed` 값은 `false`입니다.
