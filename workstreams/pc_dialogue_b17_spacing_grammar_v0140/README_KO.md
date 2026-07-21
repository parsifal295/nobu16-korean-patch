# B17 인물 대사 공백·조사 보정

현재 Steam PC의 Base·PK `msggame.bin` B17을 순정 PC 일본어와 대조해, 실제 화면에서 단어가 붙거나 조사가 틀리는 16개 레코드만 고친다. 예를 들어 `소인도시마즈일문`은 `소인도 시마즈 일문`으로, `퇴로을`은 `퇴로를`로 바로잡는다.

문장을 축약하지 않고 기존 수동 개행·색상/런타임 토큰·불투명 바이트코드를 보존한다. 후보는 `private/candidate`에만 생성하며 Steam 설치 파일을 수정하지 않는다.

```powershell
python -X utf8 workstreams/pc_dialogue_b17_spacing_grammar_v0140/build_pc_dialogue_b17_spacing_grammar_v0140.py build
python -X utf8 workstreams/pc_dialogue_b17_spacing_grammar_v0140/build_pc_dialogue_b17_spacing_grammar_v0140.py verify
python -X utf8 -m unittest -v workstreams/pc_dialogue_b17_spacing_grammar_v0140/test_pc_dialogue_b17_spacing_grammar_v0140.py
```
