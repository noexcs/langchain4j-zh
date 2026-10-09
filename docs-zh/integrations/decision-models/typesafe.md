# TypeSafe

- [TypeSafe 文档](https://docs.typesafe.ai)
- [System One API 参考](https://docs.typesafe.ai/api)

[TypeSafe](https://typesafe.ai) 通过其 System One API 提供决策模型（例如 Jev）。
`TypeSafeDecisionModel` 在其之上实现了 [`DecisionModel`](../../tutorials/decision-models.md) API。

其他服务器也实现了相同的 API，例如
[OpenRouter](https://openrouter.ai/docs/guides/community/jev) 以及运行开源模型的推理服务器（如
[SGLang](https://docs.sglang.io/docs/supported-models/decision_models)）。
通过设置基础 URL，`TypeSafeDecisionModel` 可以与其中任何一个搭配使用（见[下文](#其他服务器)）。

!!! note
    此集成为实验性质，可能会在将来版本中发生变化。

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-typesafe</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## 用法

```java
DecisionModel decisionModel = TypeSafeDecisionModel.builder()
        .apiKey(System.getenv("TYPESAFE_API_KEY"))
        .modelName("jev-1.13.0")
        .build();

DecisionRequest request = DecisionRequest.builder()
        .input("Help! My payouts have been failing for 3 days.")
        .question("team", ChoiceQuestion.builder()
                .text("Which team should handle this ticket?")
                .option("billing", "Payments, payouts, invoices, refunds")
                .option("support", "Problems using the product")
                .build())
        .question("urgent", YesNoQuestion.of("Does this need attention today?"))
        .build();

DecisionResponse response = decisionModel.decide(request);

ChoiceAnswer team = response.choice("team");
YesNoAnswer urgent = response.yesNo("urgent");
```

所有问题类型及如何使用答案，请参见[决策模型](../../tutorials/decision-models.md)教程。

## 配置

```java
TypeSafeDecisionModel decisionModel = TypeSafeDecisionModel.builder()
        .apiKey(...)              // required for api.typesafe.ai, optional for other servers
        .modelName(...)           // required here or on each request (otherwise decide() fails), e.g. "jev-1.13.0"
        .baseUrl(...)             // defaults to "https://api.typesafe.ai"
        .timeout(...)             // defaults to the HTTP client builder's timeouts, otherwise 15s connect / 60s read
        .maxRetries(...)          // retries after the first attempt; defaults to 2
        .customHeaders(...)       // additional HTTP headers, as a Map or a Supplier<Map>
        .listeners(...)           // DecisionModelListeners, see Observability in the Decision Models tutorial
        .logRequests(...)         // defaults to false
        .logResponses(...)        // defaults to false
        .logger(...)              // an alternate SLF4J logger for requests and responses
        .httpClientBuilder(...)   // see below
        .build();
```

可用模型列表见 [TypeSafe 文档](https://docs.typesafe.ai/models)。
诸如 `jev-latest` 之类的别名随时可能指向新版本；在生产环境中请使用固定版本。

HTTP 客户端可通过 `httpClientBuilder(...)` 自定义，参见[可自定义的 HTTP 客户端](../../tutorials/customizable-http-client.md)。

同时支持 `decide()` 和 `decideAsync()`。

该模型支持 `YesNoQuestion`、`ChoiceQuestion` 和 `ScaleQuestion` 问题类型。
在 TypeSafe 文档中，是非题被称为 "noul" 问题，量表题被称为 "score"
问题，输入则被称为 "state"。带描述的量表级别（`level(label, description)`）
会作为具有 `label` 和 `description` 的对象发送。
该 API 仅接受文本：文本内容按文本发送，图片则在不调用 API 的情况下抛出 `UnsupportedFeatureException`。
选择题和量表题答案的置信度由服务器计算。

答案会根据请求进行校验：缺失的答案、类型错误的答案、未提供的选项、
0 到 1 之外的概率，或超出级别范围之外的量表均值，都会抛出
`InvalidDecisionResponseException`。量表答案中未报告概率的级别，其概率为 0。

输入和问题会发送到你配置的服务器。使用托管服务时，请查看其数据处理
和保留条款，并参见[数据保护](../../tutorials/decision-models.md#数据保护)。

## 其他服务器

任何实现了 System One API（`POST /v1/systemone`）的服务器都可以通过设置基础 URL 来使用。
例如，使用 OpenRouter：

```java
DecisionModel decisionModel = TypeSafeDecisionModel.builder()
        .baseUrl("https://openrouter.ai/api")
        .apiKey(System.getenv("OPENROUTER_API_KEY"))
        .modelName("typesafe/jev-1.13")
        .build();
```

或者本地使用 [Ollama](https://docs.ollama.com/capabilities/decision)（v0.35.0 或更高版本），先执行
`ollama pull nimble`（或 `ollama pull tev1`）：

```java
DecisionModel decisionModel = TypeSafeDecisionModel.builder()
        .baseUrl("http://localhost:11434")
        .modelName("nimble")
        .build();
```

本地和自托管服务器通常无需 API 密钥。Ollama 的决策模型仅接受文本输入，提示词最多 2,048 token，
每个问题 2 到 26 个选项或级别，每个请求最多 64 个问题。
没有 GPU 时，一个请求可能需要几秒钟，因此考虑设置更长的 `timeout(...)`。如果工具有 64 个以上，
请在[工具选择](../../tutorials/decision-models.md#选择工具)组件上设置 `maxToolsPerDecisionRequest(64)`。
对于[重排](../../tutorials/decision-models.md#对检索内容进行重排)，请调低 `maxSegmentsPerRequest(...)`，
使一个请求的片段能容纳在提示词中。

`TypeSafeDecisionModel` 已在 TypeSafe API、OpenRouter 和 Ollama（`nimble` 和 `tev1`）上进行过测试。

不同服务器在应用的限制（例如最大选项数）、置信度的计算方式以及答案质量方面可能存在差异：
作为决策模型提供的小型模型和通用语言模型，通常比专用决策模型准确性更低、决策性更差。
请查看你所使用服务器的文档，并在自己的数据上评估答案。

无论基础 URL 是什么，该模型都会将 `ModelProvider.TYPESAFE` 报告为其提供商，例如在监听器和指标中。
