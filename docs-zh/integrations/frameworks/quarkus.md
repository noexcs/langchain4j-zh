# Quarkus

Quarkus [LangChain4j 扩展](https://quarkus.io/extensions/io.quarkiverse.langchain4j/quarkus-langchain4j-core/)与 Quarkus 编程模型以及现有的 Quarkus 运行时组件无缝集成。

与在 Quarkus 中使用原生 LangChain4j 库相比，该扩展提供了以下优势：

- 与 Quarkus 编程模型集成
    - 用于声明式 AI 服务的新 `@RegisterAiService` 注解
    - LangChain4j 模型的可注入 CDI bean
- 能够编译为 GraalVM 原生二进制文件
- 用于配置模型的标准配置属性
- 内置可观测性（指标、链路追踪和审计）
- 构建时装配。在构建时做更多工作可以减小 LangChain4j 库的占用，并启用构建时可用性提示。


## Dev UI

在 Dev 模式下，quarkus-langchain4j 项目在 Dev UI 中提供了几个页面，以方便 LangChain4j 开发：

- AI 服务页面：提供应用程序中检测到的所有 AI 服务的表格，以及它们声明使用的工具列表。
- 向量存储访问：允许将嵌入添加到向量存储中并进行搜索。
- 工具页面：提供应用程序中检测到的工具列表。
- 聊天页面：允许你手动与聊天模型进行对话。仅当应用程序包含聊天模型时，此页面才可用。
- 图像页面：允许你测试图像模型的输出并调整其参数（对于支持的模型）。
- 内容审核页面：允许你测试内容审核模型的输出——你提交一个提示词，并接收每个适当性类别的分数列表（对于支持的模型）。


有关扩展功能的更详细说明，请参阅 langchain4j 扩展的 [Quarkus 文档](https://docs.quarkiverse.io/quarkus-langchain4j/dev/)。
