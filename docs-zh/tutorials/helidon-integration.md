# Helidon 集成

[Helidon](https://helidon.io/) 提供了一个 LangChain4j 集成模块，在利用 Helidon 编程模型和风格的同时，
简化了构建 AI 驱动型应用程序。

你可以在[此处](https://helidon.io/docs/latest/se/integrations/langchain4j/langchain4j)找到关于 LangChain4j 集成功能的详细说明和使用方法。

## 支持的版本

Helidon 的 LangChain4j 集成需要 Java 21 和 Helidon 4.2。

## 示例

我们创建了一些示例应用程序供你探索。这些示例展示了在 Helidon 应用程序中使用 LangChain4j 的各个方面。

### 咖啡店助手
咖啡店助手是一个演示应用程序，展示了如何为咖啡店构建一个 AI 助手。该助手可以回答有关菜单的问题、
提供推荐并创建订单。它使用从 JSON 文件初始化的向量存储。

主要功能：
- 与 OpenAI 聊天模型集成
- 使用嵌入模型、向量存储、摄入器和内容检索器
- 使用 Helidon Inject 进行依赖注入
- 从 JSON 文件初始化向量存储
- 支持回调函数以增强交互

去看看：
- [Helidon SE 的咖啡店助手](https://github.com/helidon-io/helidon-examples/tree/helidon-4.x/examples/integrations/langchain4j/coffee-shop-assistant-se)
- [Helidon MP 的咖啡店助手](https://github.com/helidon-io/helidon-examples/tree/helidon-4.x/examples/integrations/langchain4j/coffee-shop-assistant-mp)

### 实践实验室

我们还提供了一个实践实验室，包含如何构建咖啡店助手的分步说明：

[HOL：使用 Helidon 和 LangChain4j 构建 AI 驱动型应用程序](https://github.com/helidon-io/helidon-labs/tree/main/hols/langchain4j)
