# Steam JP `msggame` wave07 통합

Steam PK v1.1.7 일본어 순정 `MSG_PK/JP/msggame.bin`에 J01~J05 source-free
오버레이 4,061건을 합친다. 기존 24,211건과 합쳐 의미 번역 대상 28,272건을
모두 덮되, 원본의 18블록·21,751레코드·29,524리터럴과 비문자 바이트 구조는
그대로 유지한다.

통합기는 다섯 공개 오버레이가 기존 JP partition과 정확히 일치하는지, 좌표가
겹치지 않는지, JP UTF-16LE 해시·제어코드·printf·ESC·PUA·줄바꿈·앞뒤 공백이
현재 Steam 원본과 일치하는지 확인한다. 동일 JP 해시에 문맥상 서로 다른 한국어가
필요한 경우에는 원문 없이 해시·정확 좌표·허용 한국어를 적은
`contextual_variants.v1.json`에서 명시적으로 검토해야 한다.

```powershell
python -B workstreams/msggame_pk_jp_native_wave07_integration/build_wave07_integration.py check
python -B workstreams/msggame_pk_jp_native_wave07_integration/build_wave07_integration.py build
python -B workstreams/msggame_pk_jp_native_wave07_integration/test_wave07_integration.py
```

후보는 저장소 `tmp` 아래에만 생성하며 Steam 파일, EXE, DLL, 메모리와 레지스트리는
수정하지 않는다.
