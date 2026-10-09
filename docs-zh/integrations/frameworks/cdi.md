# LangChain4J CDI

[LangChain4J CDI](https://github.com/langchain4j/langchain4j-cdi) 可以将 AI 服务直接注入到你的 Jakarta EE 和 MicroProfile 应用中。

## 文档

完整文档见 **[langchain4j.github.io/langchain4j-cdi](https://langchain4j.github.io/langchain4j-cdi/)**。

## 功能

- **AI 服务注入** — 使用 `@RegisterAIService` 将 AI 服务声明为 CDI 托管 Bean
- **智能体拓扑** — 11 个按拓扑划分的注解（`@RegisterSimpleAgent`、`@RegisterSequenceAgent`、`@RegisterLoopAgent` 等），用于多智能体工作流
- **MCP 服务器** — 将 CDI 托管 Bean 暴露为模型上下文协议（Model Context Protocol）服务器
- **基于属性的配置** — 通过 MicroProfile Config 或自定义 SPI 配置 LLM 组件
- **容错** — 使用 `@Retry`、`@Timeout`、`@CircuitBreaker`、`@Fallback` 实现弹性
- **遥测** — 基于 OpenTelemetry 的 AI 操作可观测性
- **表达式语言** — 在注解中解析 `${...}`（MicroProfile Config）和 `#{...}`（Jakarta EL）表达式
- **护栏** — 对 AI 服务交互进行输入和输出校验

## 支持的运行时

| 运行时 | 扩展类型 |
|---------|---------------|
| Quarkus | 构建时兼容 |
| Helidon | 两者均兼容 |
| WildFly | 可移植 |
| Payara | 可移植 |
| GlassFish | 可移植 |
| Liberty | 可移植 |

关于 LangChain4j CDI 功能的详细说明和使用方法，请参阅 [LangChain4J CDI 文档](https://langchain4j.github.io/langchain4j-cdi/)。
