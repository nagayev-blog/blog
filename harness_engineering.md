# Harness Engineering для AI-агентов

**Harness** — это инфраструктурный слой, который оборачивает агента и управляет всем, что вокруг него: входами, выходами, инструментами, памятью, ограничениями и наблюдаемостью. Агент пишет логику — harness обеспечивает среду выполнения.

Аналогия: если агент — это процесс, то harness — это операционная система для него.

---

## Из чего состоит harness

### 1. Tool Registry

Центральный реестр инструментов с контролем доступа. Агент не вызывает инструменты напрямую — он запрашивает их через harness, который валидирует вызов, логирует его и применяет политики.

```python
class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._policies: list[Policy] = []

    def call(self, agent_id: str, tool_name: str, **kwargs) -> ToolResult:
        tool = self._tools[tool_name]
        for policy in self._policies:
            policy.check(agent_id, tool, kwargs)  # raises if denied
        result = tool.execute(**kwargs)
        self._audit_log(agent_id, tool_name, kwargs, result)
        return result
```

### 2. Context Manager / Memory Broker

Управляет тем, что агент "видит" в каждый момент времени. Разделяет рабочую память (in-context), эпизодическую (vector store) и семантическую (knowledge graph).

### 3. Execution Controller

Контролирует жизненный цикл шага агента: таймауты, ретраи, circuit breakers, budget (токены, деньги, время).

```python
@dataclass
class ExecutionBudget:
    max_tokens: int
    max_wall_time: float
    max_tool_calls: int
    max_cost_usd: float

class ExecutionController:
    async def step(self, agent: Agent, budget: ExecutionBudget) -> StepResult:
        async with asyncio.timeout(budget.max_wall_time):
            return await agent.think(budget)
```

### 4. Observation Bus

Все события агента публикуются в шину — traces, метрики, аномалии. Это основа для debugging и evaluation.

### 5. Sandbox / Isolation Layer

Изоляция side-effects: файловая система, сеть, subprocess. Особенно критично в MAS, где агенты могут влиять друг на друга.

---

## В контексте MAS: Harness как координационный слой

В мультиагентных системах harness решает проблему **inter-agent trust и coordination**:

```
┌─────────────────────────────────────────────┐
│              MAS Harness                     │
│                                              │
│  ┌──────────┐    Message    ┌──────────┐    │
│  │ Agent A  │◄─── Bus ────►│ Agent B  │    │
│  └──────────┘               └──────────┘    │
│       │                          │          │
│  ┌────▼──────────────────────────▼────┐    │
│  │         Shared Tool Registry        │    │
│  │  + Resource Locks + Rate Limits     │    │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

Harness контролирует:
- кто кому может писать сообщения
- shared resource locking (агенты не конкурируют за одни данные)
- версионирование состояния между агентами

---

## Ключевые паттерны

### Capability Manifests

Агент декларирует что ему нужно, harness решает что дать:

```yaml
agent: researcher
requires:
  tools: [web_search, file_read]
  memory: [episodic]
  budget: {tokens: 50000, cost_usd: 0.5}
```

### Checkpoint / Restore

Harness сериализует состояние агента между шагами. Критично для long-running задач и отказоустойчивости.

### Evaluation Hooks

Harness перехватывает каждый вывод агента и прогоняет через eval pipeline до того, как результат идёт дальше.

---

## Что это даёт на практике

| Без harness | С harness |
|---|---|
| Агент сам управляет инструментами | Централизованный контроль и аудит |
| Отладка через print/logs | Structured traces, replay |
| Hard-coded ограничения | Динамические политики |
| Агенты не изолированы | Fault isolation между агентами |
| Eval — отдельный скрипт | Eval встроен в цикл выполнения |

---

## Практический совет для Python

Для highload стоит смотреть в сторону **async-first harness** с отдельными event loops на агента, где harness живёт в основном loop и координирует через очереди.

Из готовых кирпичей:
- `asyncio` — основной event loop и coordination primitives
- `structlog` — structured logging для observation bus
- `opentelemetry` — distributed tracing
- `Redis` — message bus и lock manager

Эта связка уже даёт 80% нужной инфраструктуры без тяжёлых фреймворков.
