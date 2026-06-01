# DeepAgent CLI GLM Example

아주 작은 DeepAgents CLI 예제입니다.

포함된 것:

- `deepagents.create_deep_agent`
- 임시 tool: `get_weather`
- `stream_events(..., version="v3")`
- `message.text`와 `message.reasoning` 분리 출력
- env role 기반 `ChatOpenAI(base_url=...)`

## 1. 설치

```bash
uv sync
```

또는 pip를 쓰면:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U deepagents langchain langchain-openai python-dotenv
```

## 2. 모델 설정

역할별 모델 설정은 `.env`에서 관리합니다. 변수 규칙은 `{ROLE}_{KEY}`이고, `TOOL_*`은 없으면 `SUPERVISOR_*` 값을 사용합니다.

```bash
cp .env.example .env
```

```env
SUPERVISOR_MODEL=z-ai/glm-4.7
SUPERVISOR_BASE_URL=https://openrouter.ai/api/v1
SUPERVISOR_API_KEY=

# 선택: tool 전용 모델을 쓰고 싶을 때만 설정
TOOL_MODEL=
TOOL_BASE_URL=
TOOL_API_KEY=
```

`SUPERVISOR`는 DeepAgent supervisor가 쓰는 모델이고, `TOOL`은 앞으로 tool 내부에서 LLM을 호출할 때 쓸 모델입니다. 코드에서는 `build_model("SUPERVISOR")`, `build_model("TOOL")`처럼 역할 이름으로 가져옵니다.

OpenRouter reasoning은 `SUPERVISOR_BASE_URL`에 `openrouter.ai`가 들어 있으면 기본으로 `extra_body={"reasoning": {"enabled": true}}`를 보냅니다.

`build_model()`에는 `ChatOpenAI` 파라미터를 그대로 덮어쓸 수 있습니다.

```python
model = build_model("SUPERVISOR", temperature=0.0, timeout=60, max_retries=1)
```

## 3. 실행

한 번만 질문:

```bash
uv run python main.py "서울 날씨 알려줘"
```

대화형 CLI:

```bash
uv run python main.py
```

그 다음:

```text
> 서울 날씨 알려줘
```

## 4. reasoning 분리

`src/recipe_agent/streaming.py`의 `stream_answer()`에서 아래처럼 분리합니다.

- `message.reasoning` → stderr에 `[thinking]`으로 출력
- `message.text` → stdout에 `[answer]`로 출력
- `stream.tool_calls` → stderr에 tool 실행 로그 출력

주의: OpenRouter는 streaming reasoning을 `delta.reasoning` 또는 `delta.reasoning_details`로 보낼 수 있습니다. `src/recipe_agent/model.py`의 `ReasoningChatOpenAI` wrapper가 이 값을 LangChain v3의 `message.reasoning` projection으로 변환합니다.

## 5. 코드 구조

- `main.py`: 로컬 실행용 얇은 entrypoint
- `src/recipe_agent/agent.py`: `create_recipe_agent()`
- `src/recipe_agent/cli.py`: argv 처리와 대화형 loop
- `src/recipe_agent/model.py`: env 기반 모델 생성, OpenRouter reasoning chunk 보정
- `src/recipe_agent/prompts.py`: supervisor/subagent prompt
- `src/recipe_agent/streaming.py`: v3 stream 출력
- `src/recipe_agent/tools/`: ClickHouse, glossary tool
- `src/recipe_agent/subagents/`: recipe comparison subagent spec
- `src/recipe_agent/skills/*/SKILL.md`: 작업별 progressive-disclosure skill
- `src/recipe_agent/memory/AGENTS.md`: 항상 적용되는 agent memory

## 6. 다음 단계

이 예제가 동작하면 다음 순서로 확장하면 됩니다.

1. `get_weather`를 `get_recipe_summary(recipe_id)`로 교체
2. DB 조회 tool 추가
3. tool wrapper에서 timeout, read-only, LIMIT 강제
4. CLI stream을 Web SSE/WebSocket으로 교체
5. `user_id + conversation_id + thread_id` 격리 추가
