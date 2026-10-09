# OpenAI

- [OpenAI Decisions API 指南](https://developers.openai.com/api/docs/guides/decisions)

OpenAI Decisions API（`POST /v1/decisions`）针对文本或图像输入回答是非题、选择题和量表题，并附带概率。它在两个模块中实现了 [`DecisionModel`](../../tutorials/decision-models.md) API：

- `langchain4j-open-ai` 中的 `OpenAiDecisionModel`，使用 LangChain4j 的 HTTP 客户端
- `langchain4j-open-ai-official` 中的 `OpenAiOfficialDecisionModel`，使用官方 OpenAI Java SDK

!!! note
    Decisions API 处于公开测试阶段，此集成为实验性质，可能会在将来版本中发生变化。

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai</artifactId>
    <version>1.22.0</version>
</dependency>
```

或者，如果使用官方 SDK：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-official</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## 用法

```java
DecisionModel decisionModel = OpenAiDecisionModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName(OpenAiDecisionModelName.GPT_6_LUNA)
        .build();

DecisionRequest request = DecisionRequest.builder()
        .input("Help! My payouts have been failing for 3 days and nobody answers my emails.")
        .question("team", ChoiceQuestion.builder()
                .text("Which team should handle this ticket?")
                .option("billing", "Payments, payouts, invoices, refunds")
                .option("support", "Problems using the product")
                .option("sales", "Pricing, upgrades, new accounts")
                .build())
        .question("urgent", YesNoQuestion.of("Does this need attention today?"))
        .build();

DecisionResponse response = decisionModel.decide(request);

response.choice("team").value();          // "billing"
response.yesNo("urgent").probability();   // 0.93
```

使用官方 SDK 时，使用 `OpenAiOfficialDecisionModel`，它以 `String` 形式接收模型名称：

```java
DecisionModel decisionModel = OpenAiOfficialDecisionModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-6-luna")
        .build();
```

它具有与该模块中其他模型相同的客户端设置，例如 `baseUrl`、`timeout`、`maxRetries`
和 `openAIClient`。

## Spring Boot

添加你所使用模块的 starter：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-spring-boot4-starter</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

官方 SDK 则使用 `langchain4j-open-ai-official-spring-boot4-starter`。在 Spring Boot 3 上，请改用
`langchain4j-open-ai-spring-boot-starter` 或 `langchain4j-open-ai-official-spring-boot-starter`
（参见 [Spring Boot 集成](../../tutorials/spring-boot-integration.md#支持的版本)）。

当在 `application.properties` 中设置其 API 密钥时，会创建一个 `OpenAiDecisionModel` bean：

```properties
# Mandatory properties:
langchain4j.open-ai.decision-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.decision-model.model-name=gpt-6-luna

# Optional properties:
langchain4j.open-ai.decision-model.base-url=...
langchain4j.open-ai.decision-model.organization-id=...
langchain4j.open-ai.decision-model.project-id=...
langchain4j.open-ai.decision-model.timeout=...
langchain4j.open-ai.decision-model.max-retries=...
langchain4j.open-ai.decision-model.log-requests=...
langchain4j.open-ai.decision-model.log-responses=...
langchain4j.open-ai.decision-model.custom-headers...=...
langchain4j.open-ai.decision-model.custom-query-params...=...
```

使用官方 SDK starter 时，则会创建 `OpenAiOfficialDecisionModel` bean：

```properties
# Mandatory properties:
langchain4j.open-ai-official.decision-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai-official.decision-model.model-name=gpt-6-luna

# Optional properties:
langchain4j.open-ai-official.decision-model.base-url=...
langchain4j.open-ai-official.decision-model.organization-id=...
langchain4j.open-ai-official.decision-model.timeout=...
langchain4j.open-ai-official.decision-model.max-retries=...
langchain4j.open-ai-official.decision-model.custom-headers...=...
```

`DecisionModelListener` bean 会自动注册到决策模型上。

使用 `langchain4j-open-ai` 时，starter 使用 Spring 的 `RestClient`，它不支持非阻塞调用：
此时 `decideAsync(...)` 会因 `AsyncNotSupportedException` 而失败。若要异步决策，请提供一个支持非阻塞调用、
名为 `openAiDecisionModelHttpClientBuilder` 的 `HttpClientBuilder` bean，例如
`JdkHttpClient.builder()`。

## 输入

输入可以是：
- 文本；
- 具名值的 `Map`：每个值都会作为带有其名称标签的文本部分发送，值以 JSON 形式表示
  （`comment: "..."`），每张图片紧跟在持有其名称的文本部分（`photo:`）之后；
- `TextContent` 和 `ImageContent` 的列表，例如一张照片加上描述：

```java
DecisionRequest request = DecisionRequest.builder()
        .input(List.of(
                TextContent.from("The customer says the package arrived like this."),
                ImageContent.from(base64Image, "image/jpeg")))
        .question("damaged", YesNoQuestion.of("Is the item visibly damaged?"))
        .build();
```

图片必须是内联形式：base64 数据或 `data:` URL。API 不支持通过 `http` 或 `https` URL 引用的图片，
调用前会以 `UnsupportedFeatureException` 拒绝。支持 `LOW`、`HIGH` 和 `AUTO` 级别；
`MEDIUM` 和 `ULTRA_HIGH` 会以 `UnsupportedFeatureException` 被拒绝。

## 问题与答案

| `DecisionModel` | OpenAI | 备注 |
|---|---|---|
| `YesNoQuestion` | `predicate` | `yesWhen` 和 `noWhen` 会附加到问题后面 |
| `ChoiceQuestion` | `choice` | 选项名称作为值发送，并附带其描述 |
| `ScaleQuestion` | `score` | 级别作为标签发送 |

选择题和量表题的答案包含每个选项或级别的概率，以及置信度。

API 可能拒绝回答某一个单一问题，例如因为它违反了 OpenAI 的使用政策。其他问题的答案仍会返回，
且对于被拒绝的问题，`response.isRefused(name)` 返回 `true`
（参见 [拒绝回答](../../tutorials/decision-models.md#拒答)）。

## Token 使用情况

`response.tokenUsage()` 是 `OpenAiTokenUsage`（或 `OpenAiOfficialTokenUsage`），其中包含
缓存的输入 token 数量。
