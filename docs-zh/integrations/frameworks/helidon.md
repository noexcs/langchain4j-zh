# Helidon

[Helidon](https://helidon.io/) 提供了 LangChain4j 集成模块，在沿用 Helidon 编程模型和风格的同时，简化 AI 驱动应用的构建。

与手动添加 LangChain4j 库相比，Helidon 的 LangChain4j 集成提供了以下优势：

- 与 Helidon Inject 集成
    - 根据配置，自动在 Helidon 服务注册表中创建并注册所选的 LangChain4j 组件。
- 约定优于配置
    - 通过提供合理的默认值来简化配置，减少常见用例中的手动设置。
- 声明式 AI 服务
    - 在声明式编程模型中支持 LangChain4j 的 AI 服务，实现整洁、易于管理的代码结构。
- 与 CDI 集成
    - 借助 Helidon Inject 到 CDI 的桥接，CDI 环境（例如 Helidon MP（MicroProfile）应用）中也可以使用 LangChain4j 组件。

这些功能显著降低了将 LangChain4j 引入 Helidon 应用的复杂性。

有关 LangChain4j 集成功能的详细说明和使用方法，请参阅 [Helidon 文档](https://helidon.io/docs/latest/se/integrations/langchain4j/langchain4j)。
