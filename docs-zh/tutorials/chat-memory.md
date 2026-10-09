# 聊天记忆

手动维护和管理 `ChatMessage` 是一件繁琐的事情。
因此，LangChain4j 提供了 `ChatMemory` 抽象以及多个开箱即用的实现。

`ChatMemory` 可以作为独立的底层组件使用，
也可以作为 [AI 服务](ai-services.md) 等高层组件的一部分。

`ChatMemory` 充当 `ChatMessage` 的容器（由 `List` 支持），并提供以下附加功能：
- 驱逐策略
- 持久化
- 对 `SystemMessage` 的特殊处理
- 对[工具](tools.md)消息的特殊处理

## 记忆与历史

请注意，"记忆"和"历史"是相似但不同的概念。
- 历史**完整**地保留用户与 AI 之间的**所有**消息。历史是用户在 UI 中看到的内容，它代表了实际说过的内容。
- 记忆保留**部分信息**，这些信息呈现给 LLM，使其表现得好像"记住"了对话。
记忆与历史有很大不同。根据所使用的记忆算法，记忆可以以多种方式修改历史：
驱逐某些消息、将多条消息总结为一条、单独总结各条消息、从消息中移除不重要的细节，
向消息注入额外信息（例如用于 RAG）或指令（例如用于结构化输出），等等。

LangChain4j 目前只提供"记忆"，不提供"历史"。如果需要保留完整的历史，请手动实现。

## 驱逐策略

出于以下几个原因，需要驱逐策略：
- 以适应 LLM 的上下文窗口。LLM 一次能处理的 token 数量是有上限的。
对话最终可能超过这个限制。在这种情况下，应该驱逐一些消息。
通常驱逐最旧的消息，但如有需要，也可以实现更复杂的算法。
- 以控制成本。每个 token 都有成本，使得每次对 LLM 的调用越来越昂贵。
驱逐不必要的消息可以降低费用。
- 以控制延迟。发送给 LLM 的 token 越多，处理它们所需的时间就越长。

目前，LangChain4j 提供 2 个开箱即用的实现：
- 较简单的 `MessageWindowChatMemory` 作为滑动窗口运行，
保留最近 `N` 条消息，并驱逐不再放得下的较旧消息。
不过，由于每条消息可能包含不同数量的 token，
`MessageWindowChatMemory` 主要用于快速原型开发。
- 更精细的选项是 `TokenWindowChatMemory`，
它同样作为滑动窗口运行，但专注于保留最近 `N` 个 **token**，
并视需要驱逐较旧的消息。
消息是不可分割的。如果一条消息放不进去，它就会被完全驱逐。
`TokenWindowChatMemory` 需要一个 `TokenCountEstimator` 来计算每条 `ChatMessage` 中的 token 数。

## 持久化

默认情况下，`ChatMemory` 实现将 `ChatMessage` 存储在内存中。

如果需要持久化，可以实现自定义的 `ChatMemoryStore`，
将 `ChatMessage` 存储在你选择的任何持久化存储中：
```java
class PersistentChatMemoryStore implements ChatMemoryStore {

        @Override
        public List<ChatMessage> getMessages(Object memoryId) {
          // TODO: Implement getting all messages from the persistent store by memory ID.
          // ChatMessageDeserializer.messageFromJson(String) and 
          // ChatMessageDeserializer.messagesFromJson(String) helper methods can be used to
          // easily deserialize chat messages from JSON.
        }

        @Override
        public void updateMessages(Object memoryId, List<ChatMessage> messages) {
            // TODO: Implement updating all messages in the persistent store by memory ID.
            // ChatMessageSerializer.messageToJson(ChatMessage) and 
            // ChatMessageSerializer.messagesToJson(List<ChatMessage>) helper methods can be used to
            // easily serialize chat messages into JSON.
        }

        @Override
        public void deleteMessages(Object memoryId) {
          // TODO: Implement deleting all messages in the persistent store by memory ID.
        }
    }

ChatMemory chatMemory = MessageWindowChatMemory.builder()
        .id("12345")
        .maxMessages(10)
        .chatMemoryStore(new PersistentChatMemoryStore())
        .build();
```

每当有新的 `ChatMessage` 添加到 `ChatMemory` 时，都会调用 `updateMessages()` 方法。
这通常发生在每次与 LLM 交互时的两次：
一次是在添加新的 `UserMessage` 时，另一次是在添加新的 `AiMessage` 时。
`updateMessages()` 方法被期望更新与给定记忆 ID 关联的所有消息。
`ChatMessage` 可以分开存储（例如，每条消息一条记录/行/对象）
或一起存储（例如，整个 `ChatMemory` 一条记录/行/对象）。

!!! note
   请注意，从 `ChatMemory` 中驱逐的消息也会从 `ChatMemoryStore` 中驱逐。
   当一条消息被驱逐时，会调用 `updateMessages()` 方法，
   传入的消息列表不包含被驱逐的消息。

每当 `ChatMemory` 的使用者请求所有消息时，都会调用 `getMessages()` 方法。
这通常发生在每次与 LLM 交互时一次。
`Object memoryId` 参数的值对应于
创建 `ChatMemory` 时指定的 `id`。
它可以用于区分多个用户和/或多个对话。
`getMessages()` 方法被期望返回与给定记忆 ID 关联的所有消息。

每当调用 `ChatMemory.clear()` 时，都会调用 `deleteMessages()` 方法。
如果你不使用此功能，可以保持此方法为空。

## `SystemMessage` 的特殊处理

`SystemMessage` 是一种特殊类型的消息，因此它与其他消息类型的处理方式不同：
- 一旦添加，`SystemMessage` 始终会被保留。
- 同一时间只能持有一条 `SystemMessage`。
- 如果添加一条内容相同的新的 `SystemMessage`，它会被忽略。
- 如果添加一条内容不同的新的 `SystemMessage`，它会替换之前那条。
  默认情况下，新的 `SystemMessage` 被添加到消息列表的末尾。创建 `ChatMemory` 时，你可以通过设置
  `alwaysKeepSystemMessageFirst` 属性来更改此行为。

## 工具消息的特殊处理

如果包含 `ToolExecutionRequest` 的 `AiMessage` 被驱逐，
随后的那些孤儿 `ToolExecutionResultMessage` 也会自动被驱逐，
以避免与某些 LLM 提供商（如 OpenAI）出现问题，
这些提供商禁止在请求中发送孤立的 `ToolExecutionResultMessage`。

!!! note
   执行 I/O 的 `ChatMemory` 或 `ChatMemoryStore` 可以实现异步对应的方法
   （`addAsync`/`messagesAsync`/`setAsync`、`getMessagesAsync`/`updateMessagesAsync`/`deleteMessagesAsync`），这样当
   AI 服务以非阻塞模式使用时，它就不会阻塞线程。
   参阅[非阻塞与响应式（Non-blocking and Reactive）](non-blocking.md)。

## 示例
- 使用 `AiServices`：
  - [聊天记忆](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ServiceWithMemoryExample.java)
  - [为每个用户使用独立的聊天记忆](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ServiceWithMemoryForEachUserExample.java)
  - [持久化聊天记忆](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ServiceWithPersistentMemoryExample.java)
  - [为每个用户使用持久化聊天记忆](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ServiceWithPersistentMemoryForEachUserExample.java)
- 使用遗留（旧版）的 `Chain`
  - [使用 ConversationalChain 的聊天记忆](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ChatMemoryExamples.java)
  - [使用 ConversationalRetrievalChain 的聊天记忆](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/ChatWithDocumentsExamples.java)

所有支持的聊天记忆存储都可以在[这里](../integrations/chat-memory-stores/index.md)找到。


## 相关教程
- [使用 LangChain4j ChatMemory 进行生成式 AI 对话](https://www.sivalabs.in/generative-ai-conversations-using-langchain4j-chat-memory/)，作者 [Siva](https://www.sivalabs.in/)
