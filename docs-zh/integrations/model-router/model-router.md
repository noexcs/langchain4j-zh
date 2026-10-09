# 模型路由器

!!! tip
    `langchain4j-core` 还提供了 `RoutingChatModel` 和 `RoutingStreamingChatModel`，它们使用
    `ChatModelRouter` 为每个请求进行路由，例如基于[决策模型](../../tutorials/decision-models.md)。
    参阅[模型路由](../../tutorials/model-routing.md)。

这是 `ModelRouter` 的文档，它作为发往多个 ChatModel 实例的消息的路由器，并使用可插拔的 RoutingStrategy。
该模块自带两个默认实现：FailoverStrategy 和 LowestTokenUsageRoutingStrategy。


## Maven 依赖

`langchain4j-community-model-router` 库可在 Maven Central 上获取。

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-model-router</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```
## FailoverStrategy

`FailoverStrategy` 按注册顺序将消息发送给第一个可用的模型。如果该模型失败（出现错误），消息会立即发送给下一个模型。该策略会在一段冷却期内忽略失败的 ChatModel，之后再重试它们。默认冷却时间为 1 分钟。如果所有模型都失败，则抛出 `NoMatchingModelFoundException`。


```java
	ChatModel firstModel = AzureOpenAiChatModel.builder()
		...
         .build();

    ChatModel secondModel = OpenAiOfficialChatModel.builder()
		...
         .build();

    ModelRouter router = ModelRouter.builder()
        .addRoutes(firstModel, secondModel)
        .routingStrategy(new FailoverStrategy(Duration.ofMinutes(5)))
        .build();
            
   router.chat(new UserMessage("Provide 3 short bullet points explaining why Java is awesome"));
	   
	   
```

此时，如果第一个模型失败，消息会被发送给第二个模型。

!!! note
    由于 FailoverStrategy 会将消息发送给下一个模型，因此当一个模型失败时，该模型抛出的异常将对调用代码隐藏。如果你想跟踪这些异常，需要注册一个错误监听器。


## LowestTokenUsageRoutingStrategy

`LowestTokenUsageRoutingStrategy` 将消息发送给整体 token 消耗最少的模型。

```java
ChatModel firstModel = AzureOpenAiChatModel.builder()
	...
     .build();

ChatModel secondModel = OpenAiOfficialChatModel.builder()
	...
     .build();

ModelRouter router = ModelRouter.builder()
        .addRoutes(firstModel, secondModel)
        .routingStrategy(new LowestTokenUsageRoutingStrategy())
        .build();


ChatResponse first = router.chat(new UserMessage("Hello")); // uses first model    

ChatResponse second = router.chat(new UserMessage("Hello")); // uses second model

ChatResponse third = router.chat(new UserMessage("Hello")); // uses first model  
	   	   
```
## 自定义实现

你可以通过实现函数式接口 ModelRoutingStrategy 来编写自己的策略。

```java
interface ModelRoutingStrategy {

    /**
     * Determines the route key to use for the given chat messages.
     *
     * @param availableModels
     *            all configured models, including any routing metadata
     * @param chatRequest
     *            the incoming chat request
     * @return the key of the route to use
     */
    ChatModelWrapper route(List<ChatModelWrapper> availableModels, ChatRequest chatRequest);
}
```

例如，如果你有一个上下文窗口较小的模型和一个上下文窗口更大但更昂贵的模型，你可以构建一个简单的路由器，将消息长度纳入考虑。
此示例将少于 500 个字符的消息路由到小模型，其余路由到大模型。

```java
ChatModel smallModel = AzureOpenAiChatModel.builder()
        // ...
        .build();

ChatModel largeModel = OpenAiOfficialChatModel.builder()
        // ...
        .build();

ModelRouter router = ModelRouter.builder()
        .addRoutes(smallModel, largeModel)
        .routingStrategy((availableModels, chatRequest) -> {
           int totalChars = chatRequest.messages().stream()
                    .filter(UserMessage.class::isInstance)
                    .map(UserMessage.class::cast)
                    .filter(UserMessage::hasSingleText)
                    .mapToInt(m -> m.singleText().length())
                    .sum();

            return totalChars < 500 ? availableModels.get(0) : availableModels.get(1);
        })
        .build();

ChatResponse shortMsg = router.chat(new UserMessage("Quick summary?")); // smallModel
ChatResponse longMsg = router.chat(new UserMessage("...very long prompt...")); // largeModel
```


## 示例

- [ModelRouter 示例](https://github.com/langchain4j/langchain4j-examples/tree/main/model-router-examples/src/main/java)