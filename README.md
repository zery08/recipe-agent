# DeepAgent CLI GLM Example

아주 작은 DeepAgents CLI 예제입니다.

포함된 것:

- `deepagents.create_deep_agent`
- env role 기반 `ChatOpenAI(base_url=...)`
- `stream_events(..., version="v3")`
- reasoning/text delta 분리 출력
- Phoenix/OpenTelemetry tracing
- SQLDatabaseToolkit 기반 SQLite/ClickHouse tool
- `deep_query` subagent

## 1. 설치

```bash
uv sync
```

또는 pip를 쓰면:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U deepagents langchain langchain-community langchain-openai python-dotenv rich clickhouse-connect arize-phoenix-otel openinference-instrumentation-langchain
```

## 2. 설정

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

# Phoenix/OpenTelemetry
PHOENIX_ENABLED=true
PHOENIX_ENDPOINT=http://localhost:4317
PHOENIX_PROJECT_NAME=recipe-agent

# Local test SQLite DB
CLICKHOUSE_URI=sqlite:///data/recipe_agent_test.db
```

`SUPERVISOR`는 DeepAgent supervisor가 쓰는 모델이고, `TOOL`은 tool/subagent 내부에서 LLM을 호출할 때 쓸 모델입니다.

`CLICKHOUSE_URI`를 설정하면 [clickhouse.py](src/recipe_agent/tools/clickhouse.py)가 LangChain `SQLDatabaseToolkit` tools를 생성합니다. 로컬 테스트는 SQLite DB를 쓰고, 실제 ClickHouse는 `clickhousedb://default:password@localhost:8123/default` 같은 URI를 쓰면 됩니다.

OpenRouter reasoning은 `SUPERVISOR_BASE_URL`에 `openrouter.ai`가 들어 있으면 기본으로 `extra_body={"reasoning": {"enabled": true}}`를 보냅니다.

## 3. Phoenix

로컬 Phoenix를 볼 때는 먼저 Phoenix 서버를 띄웁니다.

```bash
uvx --from arize-phoenix phoenix serve
```

기본 gRPC collector endpoint는 `.env.example`처럼 `http://localhost:4317`입니다.

## 4. 실행

한 번만 질문:

```bash
uv run python main.py "RCP_ALPHA_V1과 RCP_BETA_V2의 CD_IH 평균을 비교해줘"
```

대화형 CLI:

```bash
uv run python main.py
```

## 5. Streaming

[cli.py](src/recipe_agent/cli.py)의 `stream_answer()`에서 아래처럼 분리합니다.

- `reasoning-delta` -> `[thinking]`으로 흐리게 출력
- `text-delta` -> `[answer]`로 스트리밍 출력
- `stream.tool_calls` -> tool 실행 로그 출력

OpenRouter는 streaming reasoning을 `delta.reasoning` 또는 `delta.reasoning_details`로 보낼 수 있습니다. [model.py](src/recipe_agent/model.py)의 `ReasoningChatOpenAI` wrapper가 이 값을 LangChain v3 content-block stream에서 읽을 수 있게 보정합니다.

## 6. 코드 구조

- `main.py`: 로컬 실행용 얇은 entrypoint
- `src/recipe_agent/agent.py`: `create_recipe_agent()`
- `src/recipe_agent/cli.py`: argv 처리, 대화형 loop, v3 stream 출력
- `src/recipe_agent/model.py`: env 기반 모델 생성, OpenRouter reasoning chunk 보정
- `src/recipe_agent/otel.py`: Phoenix/OpenTelemetry tracing 초기화
- `src/recipe_agent/prompts.py`: supervisor/subagent prompt와 known schema context
- `src/recipe_agent/tools/`: SQL toolkit, glossary tool
- `src/recipe_agent/subagents/`: `deep_query` subagent spec
- `src/recipe_agent/skills/*/SKILL.md`: 작업별 progressive-disclosure skill
- `src/recipe_agent/memory/AGENTS.md`: 항상 적용되는 agent memory
- `data/recipe_agent_test.db`: 로컬 테스트 SQLite DB
