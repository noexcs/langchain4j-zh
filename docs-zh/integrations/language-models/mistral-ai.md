# MistralAI
[MistralAI 文档](https://docs.mistral.ai/)

## 项目配置

要在项目中安装 langchain4j，请添加以下依赖：

Maven 项目的 `pom.xml`

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j</artifactId>
    <version>1.22.0</version>
</dependency>

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-mistral-ai</artifactId>
    <version>1.22.0</version>
</dependency>
```

Gradle 项目的 `build.gradle`

```groovy
implementation 'dev.langchain4j:langchain4j:1.22.0'
implementation 'dev.langchain4j:langchain4j-mistral-ai:1.22.0'
```
### API 密钥配置
在你的项目中添加你的 MistralAI API 密钥，你可以使用以下代码创建一个类 ```ApiKeys.java```

```java
public class ApiKeys {
    public static final String MISTRALAI_API_KEY = System.getenv("MISTRAL_AI_API_KEY");
}
```
别忘了将你的 API 密钥设置为环境变量。
```shell
export MISTRAL_AI_API_KEY=your-api-key #For Unix OS based
SET MISTRAL_AI_API_KEY=your-api-key #For Windows OS
```
有关如何获取 MistralAI API 密钥的更多详情，请参见[此处](https://docs.mistral.ai/#api-access)

### 模型选择
你可以使用 `MistralAiChatModelName` 和 `MistralAiFimModelName` 这两个 Java 枚举来查找适用于你的使用场景的模型名称。
MistralAI 已根据性能与成本的权衡更新了新的模型选择和分类。

| 模型名称           | 部署方式或可用渠道                                                                                                                  | 描述                                                                                                                                                                                                                                                                                                              |
|-----------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| open-mistral-7b       | - Mistral AI La Plateforme。<br/>- 云平台（Azure、AWS、GCP）。<br/>- Hugging Face。<br/>- 自托管（本地机房、IaaS、docker、本地）。 | **开源**<br/>Mistral AI 发布的首个稠密模型，<br/>非常适合实验、<br/>自定义和快速迭代。<br/><br/>最大 tokens 32K<br/><br/>Java 枚举<br/>`MistralAiChatModelName.OPEN_MISTRAL_7B`                                                                                   |
| open-mixtral-8x7b     | - Mistral AI La Plateforme。<br/>- 云平台（Azure、AWS、GCP）。<br/>- Hugging Face。<br/>- 自托管（本地机房、IaaS、docker、本地）。 | **开源**<br/>非常适合处理多语言操作、<br/>代码生成和微调。<br/>出色的成本/性能权衡。<br/><br/>最大 tokens 32K<br/><br/>Java 枚举<br/>`MistralAiChatModelName.OPEN_MIXTRAL_8x7B`                                                                               |
| open-mixtral-8x22b    | - Mistral AI La Plateforme。<br/>- 云平台（Azure、AWS、GCP）。<br/>- Hugging Face。<br/>- 自托管（本地机房、IaaS、docker、本地）。 | **开源**<br/>具备 Mixtral-8x7B 的全部能力，并拥有强大的数学<br/>和编码能力，原生支持函数调用<br/><br/>最大 tokens 64K。<br/><br/>Java 枚举<br/>`MistralAiChatModelName.OPEN_MIXTRAL_8X22B`                                                                                             |
| open-mistral-nemo     | - Mistral AI La Plateforme。<br/>- 云平台（Azure、AWS、GCP）。<br/>- Hugging Face。<br/>- 自托管（本地机房、IaaS、docker、本地）。 | **开源**<br/>与 NVIDIA 合作构建的 12B 模型。<br/>其推理、世界知识和编码准确性在其规模类别中处于最先进水平。<br/><br/>最大 tokens 128K。<br/><br/>Java 枚举<br/>`MistralAiChatModelName.OPEN_MISTRAL_NEMO`                                                       |
| open-codestral-mamba  | - Mistral AI La Plateforme。<br/>- 云平台（Azure、AWS、GCP）。<br/>- Hugging Face。<br/>- 自托管（本地机房、IaaS、docker、本地）。 | **开源**<br/>一个专门用于代码生成的 Mamba2 语言模型。<br/>它以先进的代码和推理能力进行训练，使其性能可与 SOTA 基于 transformer 的模型相媲美。<br/><br/>最大 tokens 256K。<br/><br/>Java 枚举<br/>`MistralAiFimModelName.OPEN_CODESTRAL_MAMBA`           |
| mistral-small-latest  | - Mistral AI La Plateforme。<br/>- 云平台（Azure、AWS、GCP）。                                                                          | **商业**<br/>适合可批量处理的简单任务<br/>（分类、客户支持或文本生成）。<br/><br/>最大 tokens 32K<br/><br/>Java 枚举<br/>`MistralAiChatModelName.MISTRAL_SMALL_LATEST`                                                                                           |
| mistral-medium-latest | - Mistral AI La Plateforme。<br/>- 云平台（Azure、AWS、GCP）。                                                                          | **商业**<br/>非常适合需要适度<br/>推理的中级任务（数据提取、摘要、<br/>撰写电子邮件、撰写描述。<br/><br/>最大 tokens 32K<br/><br/>Java 枚举<br/>`MistralAiChatModelName.MISTRAL_MEDIUM_LATEST`                                                            |
| mistral-large-latest  | - Mistral AI La Plateforme。<br/>- 云平台（Azure、AWS、GCP）。                                                                          | **商业**<br/>非常适合需要强大推理<br/>能力或高度专业化的复杂任务<br/>（文本生成、代码生成、RAG 或智能体）。<br/><br/>最大 tokens 128K<br/><br/>Java 枚举<br/>`MistralAiChatModelName.MISTRAL_LARGE_LATEST`                                              |
| mistral-embed         | - Mistral AI La Plateforme。<br/>- 云平台（Azure、AWS、GCP）。                                                                          | **商业**<br/>将文本转换为 1024 维<br/>嵌入的数值向量。<br/>嵌入模型可支持检索和 RAG 应用。<br/><br/>最大 tokens 8K<br/><br/>Java 枚举<br/>`MistralAiEmbeddingModelName.MISTRAL_EMBED`                                                                   |
| codestral-latest      | - Mistral AI La Plateforme。<br/>- 云平台（Azure、AWS、GCP）。<br/>- Hugging Face。<br/>- 自托管（本地机房、IaaS、docker、本地）。 | **开源（非生产许可证）和商业**<br/>一款尖端生成模型，专为代码生成任务<br/>设计并优化，包括中间补全（fill-in-the-middle）和代码补全。<br/><br/>最大 tokens 32K<br/><br/>Java 枚举<br/>`MistralAiFimModelName.CODESTRAL_LATEST` |

`@Deprecated` 模型：
- mistral-tiny（`@Deprecated`）
- mistral-small（`@Deprecated`）
- mistral-medium（`@Deprecated`）

有关更多详情和各类用例及其对应的 Mistral 模型，请参见[此处](https://docs.mistral.ai/#model-selection)

## 聊天补全
聊天模型允许你使用经过对话数据微调的模型生成类人响应。

### 同步
创建一个类并添加以下代码。

```java
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.mistralai.MistralAiChatModel;

public class HelloWorld {
    public static void main(String[] args) {
        ChatModel model = MistralAiChatModel.builder()
                .apiKey(ApiKeys.MISTRALAI_API_KEY)
                .modelName(MistralAiChatModelName.MISTRAL_SMALL_LATEST)
                .build();

        String response = model.chat("Say 'Hello World'");
        System.out.println(response);
    }
}
```
运行该程序将生成如下输出的某种变体

```plaintext
Hello World! How can I assist you today?
```

### 流式
创建一个类并添加以下代码。

```java
import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.model.chat.response.StreamingChatResponseHandler;
import dev.langchain4j.model.mistralai.MistralAiStreamingChatModel;
import dev.langchain4j.model.output.Response;

import java.util.concurrent.CompletableFuture;

public class HelloWorld {
    public static void main(String[] args) {
        MistralAiStreamingChatModel model = MistralAiStreamingChatModel.builder()
                .apiKey(ApiKeys.MISTRALAI_API_KEY)
                .modelName(MistralAiChatModelName.MISTRAL_SMALL_LATEST)
                .build();

        CompletableFuture<ChatResponse> futureResponse = new CompletableFuture<>();         
        model.chat("Tell me a joke about Java", new StreamingChatResponseHandler() {
            
            @Override
            public void onPartialResponse(String partialResponse) {
                System.out.print(partialResponse);
            }

            @Override
            public void onCompleteResponse(ChatResponse completeResponse) {
                futureResponse.complete(completeResponse);
            }

            @Override
            public void onError(Throwable error) {
                futureResponse.completeExceptionally(error);
            }    
        });

        futureResponse.join();
    }
}
```
当 LLM 生成文本时，你会通过 `onPartialResponse` 方法接收到每一段文本（token）。

可以看到，下面的输出是实时流式传输的。

```plaintext
"Why do Java developers wear glasses? Because they can't C#"
```

当然，你可以将 MistralAI 聊天补全与其他功能结合使用，例如[设置模型参数](../../tutorials/model-parameters.md)和[聊天记忆](../../tutorials/chat-memory.md)，以获得更准确的响应。

在[聊天记忆](../../tutorials/chat-memory.md)中，你将学习如何传递你的聊天历史，以便 LLM 了解之前说过什么。如果你不传递聊天历史（就像这个简单的例子），LLM 将不知道之前说过什么，因此无法正确回答第二个问题（'What did I just ask?'）。

许多参数在幕后被设置，例如超时、模型类型和模型参数。
在[设置模型参数](../../tutorials/model-parameters.md)中，你将学习如何显式设置这些参数。

### 函数调用
函数调用允许 Mistral 聊天模型（[同步](#同步)和[流式](#流式)）连接外部工具。例如，你可以调用一个 `Tool` 来获取支付交易状态，如 Mistral AI 函数调用[教程](https://docs.mistral.ai/guides/function-calling/)所示。

<details>
<summary>支持哪些 mistral 模型？</summary>

!!! note
    目前，以下模型支持函数调用：

    - Mistral Small `MistralAiChatModelName.MISTRAL_SMALL_LATEST`
    - Mistral Large `MistralAiChatModelName.MISTRAL_LARGE_LATEST`
    - Mixtral 8x22B `MistralAiChatModelName.OPEN_MIXTRAL_8X22B`
    - Mistral Nemo `MistralAiChatModelName.OPEN_MISTRAL_NEMO`
</details>

#### 1. 定义一个 `Tool` 类以及如何获取支付数据

假设你有一个如下的支付交易数据集。在实际应用中，你应该注入数据库源或 REST API 客户端来获取数据。
```java
import java.util.*;

public class PaymentTransactionTool {

   private final Map<String, List<String>> paymentData = Map.of(
            "transaction_id", List.of("T1001", "T1002", "T1003", "T1004", "T1005"),
            "customer_id", List.of("C001", "C002", "C003", "C002", "C001"),
            "payment_amount", List.of("125.50", "89.99", "120.00", "54.30", "210.20"),
            "payment_date", List.of("2021.22.05", "2021.22.06", "2021.22.07", "2021.22.05", "2021.22.08"),
            "payment_status", List.of("Paid", "Unpaid", "Paid", "Paid", "Pending"));
   
    ...
}
```
接下来，让我们定义两个方法 `retrievePaymentStatus` 和 `retrievePaymentDate`，以从 `Tool` 类中获取支付状态和支付日期。

```java
// Tool to be executed to get payment status
@Tool("Get payment status of a transaction") // function description
String retrievePaymentStatus(@P("Transaction id to search payment data") String transactionId) {
    return getPaymentData(transactionId, "payment_status");
}

// Tool to be executed to get payment date
@Tool("Get payment date of a transaction") // function description
String retrievePaymentDate(@P("Transaction id to search payment data") String transactionId) {
   return getPaymentData(transactionId, "payment_date");
}

private String getPaymentData(String transactionId, String data) {
    List<String> transactionIds = paymentData.get("transaction_id");
    List<String> paymentData = paymentData.get(data);

    int index = transactionIds.indexOf(transactionId);
    if (index != -1) {
        return paymentData.get(index);
    } else {
        return "Transaction ID not found";
    }
}
```
它使用 `@Tool` 注解来定义函数描述，使用 `@P` 注解来定义包 `dev.langchain4j.agent.tool.*` 中的参数描述。更多信息请参见[此处](../../tutorials/tools.md#高层工具-api)

#### 2. 定义一个接口作为 `agent` 以发送聊天消息。

创建一个接口 `PaymentTransactionAgent`。

```java
import dev.langchain4j.service.SystemMessage;

interface PaymentTransactionAgent {
    @SystemMessage({
            "You are a payment transaction support agent.",
            "You MUST use the payment transaction tool to search the payment transaction data.",
            "If there a date convert it in a human readable format."
    })
    String chat(String userMessage);
}
```
#### 3. 定义一个 `main` 应用类，用于与 MistralAI 聊天模型对话

```java
import dev.langchain4j.memory.chat.MessageWindowChatMemory;
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.mistralai.MistralAiChatModel;
import dev.langchain4j.model.mistralai.MistralAiChatModelName;
import dev.langchain4j.service.AiServices;

public class PaymentDataAssistantApp {

    ChatModel mistralAiModel = MistralAiChatModel.builder()
            .apiKey(System.getenv("MISTRAL_AI_API_KEY")) // Please use your own Mistral AI API key
            .modelName(MistralAiChatModelName.MISTRAL_LARGE_LATEST) // Also you can use MistralAiChatModelName.OPEN_MIXTRAL_8X22B as open source model
            .logRequests(true)
            .logResponses(true)
            .build();
    
    public static void main(String[] args) {
        // STEP 1: User specify tools and query
        PaymentTransactionTool paymentTool = new PaymentTransactionTool();
        String userMessage = "What is the status and the payment date of transaction T1005?";

        // STEP 2: User asks the agent and AiServices call to the functions
        PaymentTransactionAgent agent = AiServices.builder(PaymentTransactionAgent.class)
                .chatModel(mistralAiModel)
                .tools(paymentTool)
                .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
                .build();
        
        // STEP 3: User gets the final response from the agent
        String answer = agent.chat(userMessage);
        System.out.println(answer);
    }
}
```

并期望得到如下的回答：

```shell
The status of transaction T1005 is Pending. The payment date is October 8, 2021.
```
### JSON 模式
你还可以使用 JSON 模式以 JSON 格式获取响应。为此，你需要在 `MistralAiChatModel` 构建器或 `MistralAiStreamingChatModel` 构建器中将 `responseFormat` 参数设置为 `ResponseFormat.JSON`。

同步示例：

```java
ChatModel model = MistralAiChatModel.builder()
                .apiKey(System.getenv("MISTRAL_AI_API_KEY")) // Please use your own Mistral AI API key
                .responseFormat(ResponseFormat.JSON)
                .build();

String userMessage = "Return JSON with two fields: transactionId and status with the values T123 and paid.";
String json = model.chat(userMessage);

System.out.println(json); // {"transactionId":"T123","status":"paid"}
```

流式示例：

```java
StreamingChatModel streamingModel = MistralAiStreamingChatModel.builder()
                .apiKey(System.getenv("MISTRAL_AI_API_KEY")) // Please use your own Mistral AI API key
                .responseFormat(MistralAiResponseFormatType.JSON_OBJECT)
                .build();

String userMessage = "Return JSON with two fields: transactionId and status with the values T123 and paid.";

CompletableFuture<ChatResponse> futureResponse = new CompletableFuture<>();

streamingModel.chat(userMessage, new StreamingChatResponseHandler() {

    @Override
    public void onPartialResponse(String partialResponse) {
        System.out.print(partialResponse);
    }

    @Override
    public void onCompleteResponse(ChatResponse completeResponse) {
        futureResponse.complete(completeResponse);
    }

    @Override
    public void onError(Throwable error) {
        futureResponse.completeExceptionally(error);
    }
});

String json = futureResponse.get().content().text();

System.out.println(json); // {"transactionId":"T123","status":"paid"}
```                

### 结构化输出

结构化输出确保模型的响应遵循 JSON schema。

!!! note
    在 LangChain4j 中使用结构化输出的文档可参见[此处](../../tutorials/structured-outputs.md)，在下面的部分中，你可以找到 MistralAI 特有的信息。

如果需要，可以为模型配置一个默认 JSON Schema，当请求中未提供 schema 时，将使用该 JSON Schema 作为回退。

```java
ChatModel model = MistralAiChatModel.builder()
        .apiKey(System.getenv("MISTRAL_AI_API_KEY"))
        .modelName(MISTRAL_SMALL_LATEST)
        .supportedCapabilities(Set.of(Capability.RESPONSE_FORMAT_JSON_SCHEMA)) // Enable structured outputs
        .responseFormat(ResponseFormat.builder() // Set the fallback JSON Schema (optional)
                .type(ResponseFormatType.JSON)
                .jsonSchema(JsonSchema.builder().rootElement(JsonObjectSchema.builder()
                                .addProperty("name", JsonStringSchema.builder().build())
                                .addProperty("capital", JsonStringSchema.builder().build())
                                .addProperty(
                                        "languages",
                                        JsonArraySchema.builder()
                                                .items(JsonStringSchema.builder().build())
                                                .build())
                                .required("name", "capital", "languages")
                                .build())
                        .build())
                .build())
        .strictJsonSchema(true)
        .build();
```

### 护栏
护栏是一种限制模型行为的方式，以防止其生成有害或不需要的内容。你可以在 `MistralAiChatModel` 构建器或 `MistralAiStreamingChatModel` 构建器中可选地设置 `safePrompt` 参数。

同步示例：

```java
ChatModel model = MistralAiChatModel.builder()
                .apiKey(System.getenv("MISTRAL_AI_API_KEY"))
                .safePrompt(true)
                .build();

String userMessage = "What is the best French cheese?";
String response = model.chat(userMessage);
```

流式示例：

```java
StreamingChatModel streamingModel = MistralAiStreamingChatModel.builder()
                .apiKey(System.getenv("MISTRAL_AI_API_KEY"))
                .safePrompt(true)
                .build();

String userMessage = "What is the best French cheese?";

CompletableFuture<ChatResponse> futureResponse = new CompletableFuture<>();

streamingModel.chat(userMessage, new StreamingChatResponseHandler() {
    
    @Override
    public void onPartialResponse(String partialResponse) {
        System.out.print(partialResponse);
    }

    @Override
    public void onCompleteResponse(ChatResponse completeResponse) {
        futureResponse.complete(completeResponse);
    }

    @Override
    public void onError(Throwable error) {
        futureResponse.completeExceptionally(error);
    }
});

futureResponse.join();
```
启用安全提示词会在你的消息前添加以下 `@SystemMessage`：

```plaintext
Always assist with care, respect, and truth. Respond with utmost utility yet securely. Avoid harmful, unethical, prejudiced, or negative content. Ensure replies promote fairness and positivity.
```

### 逐请求参数

Mistral 特有的选项（`safePrompt`、`randomSeed`、`sendThinking` 和 `returnThinking`）也可以通过 `MistralAiChatRequestParameters` 按请求设置，
从而覆盖在模型构建器上配置的值的值。
这样，单个共享的模型实例就能在每次调用之间改变这些选项——例如，
为一个请求启用 `safePrompt` 而为另一个请求禁用，或为可复现的补全设置 `randomSeed`，而无需
构建第二个模型：

```java
ChatModel model = MistralAiChatModel.builder()
        .apiKey(System.getenv("MISTRAL_AI_API_KEY"))
        .modelName("mistral-small-latest")
        .build();

MistralAiChatRequestParameters parameters = MistralAiChatRequestParameters.builder()
        .safePrompt(true)
        .randomSeed(42)
        .build();

ChatRequest chatRequest = ChatRequest.builder()
        .messages(UserMessage.from("What is the best French cheese?"))
        .parameters(parameters)
        .build();

ChatResponse chatResponse = model.chat(chatRequest);
```

## 思考 / 推理

`MistralAiChatModel` 和 `MistralAiStreamingChatModel` 都支持
使用 [Magistral 推理模型](https://docs.mistral.ai/capabilities/reasoning/) 进行推理。

通过以下参数配置：
- `returnThinking`：启用后，模型产生的推理文本将从 API 响应中解析
  并存储在 `AiMessage.thinking()` 中。对于流式，`StreamingChatResponseHandler.onPartialThinking()`
  和 `TokenStream.onPartialThinking()` 回调也将被调用。
  默认禁用。
- `sendThinking`：启用后，来自先前响应（存储在 `AiMessage.thinking()` 中）的推理文本
  将包含在后续发送给 LLM 的请求中。
  默认禁用。

以下是配置推理的示例：
```java
ChatModel model = MistralAiChatModel.builder()
        .apiKey(System.getenv("MISTRAL_AI_API_KEY"))
        .modelName(MistralAiChatModelName.MAGISTRAL_MEDIUM_LATEST)
        .returnThinking(true)
        .sendThinking(true)
        .build();
```

## 内容审核

它是一个分类器模型，可用于检测文本中的有害内容。

内容审核示例：

```java
ModerationModel model = new MistralAiModerationModel.Builder()
    .apiKey(System.getenv("MISTRAL_AI_API_KEY"))
    .modelName(MistralAiModerationModelName.MISTRAL_MODERATION_LATEST)
    .logRequests(true)
    .logResponses(false)
    .build();
// I want to check if the text contains harmful content
Moderation moderation = model.moderate("I want to kill them.").content();
```

## 代码补全
中间补全（Fill-in-the-Middle，FIM）模型允许你生成代码补全。用户可以使用 `prompt` 定义代码的起始点，并使用可选的 `suffix` 和可选的 `stop` 定义代码的结束点。

### FIM 同步
就像聊天补全一样，FIM 端点也正常工作。你可以通过添加以下代码来测试它。

```java
import dev.langchain4j.model.mistralai.MistralAiFimModel;
import dev.langchain4j.model.output.Response;

public class HelloWorld {
    public static void main(String[] args) {
        MistralAiFimModel codestral = MistralAiFimModel.builder()
                .apiKey(System.getenv("MISTRAL_AI_API_KEY"))
                .modelName(MistralAiFimModelName.CODESTRAL_LATEST)
                .stop(List.of("}")) // must stop at the first occurrence of "}"
                .build();
        
        // I want to generate a code completion for a simple hello world program using MistralAI of LangChain4j framework.
        String codePrompt = """
                  public static void main(String[] args) {
                      // Create a function to multiply two numbers
                """;
        String suffix = """
                    System.out.println(result);
                  }
                """;

        // Asking to Codestral model to complete the code with given prompt and suffix
        Response<String> response = codestral.generate(prompt, suffix);
        
        System.out.println(
                String.format(
                        "%s%s%s",
                        prompt, // print code prompt (prefix)
                        response.content(), // print code filled-in-the-middle
                        suffix)); // print code suffix
    }
}
```
运行该程序将打印以下输出

```console
public static void main(String[] args) {
      // Create a function to multiply two numbers
      int result = multiply(5, 3);
      System.out.println(result);
  }
```

### FIM 流式

创建一个类并添加以下代码。

```java
import dev.langchain4j.model.StreamingResponseHandler;
import dev.langchain4j.model.language.StreamingLanguageModel;
import dev.langchain4j.model.mistralai.MistralAiStreamingFimModel;
import dev.langchain4j.model.output.Response;

import java.util.concurrent.CompletableFuture;

public class HelloWorld {
    public static void main(String[] args) {
        StreamingLanguageModel codestralStream = MistralAiStreamingFimModel.builder()
                .apiKey(ApiKeys.MISTRALAI_API_KEY)
                .modelName(MistralAiFimModelName.CODESTRAL_LATEST)
                .build();

        // I want to generate a code completion for a simple hello world program.
        String prompt = "public static void main(String[] args) {";

        CompletableFuture<Response<String>> futureResponse = new CompletableFuture<>();
        codestral.generate(prompt, new StreamingResponseHandler() {
            @Override
            public void onNext(String token) {
                System.out.print(token);
            }

            @Override
            public void onComplete(Response<String> response) {
                futureResponse.complete(response);
            }

            @Override
            public void onError(Throwable error) {
                futureResponse.completeExceptionally(error);
            }
        });

        futureResponse.join();
    }
}
```
当 LLM 生成文本时，你会通过 onNext 方法接收到每一段文本（token）。

可以看到，下面的输出是实时流式传输的。

```console
public static void main(String[] args) {

        int[] arr = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};
        int sum = 0;

        for (int i = 0; i < arr.length; i++) {
            sum += arr[i];
        }

        System.out.println("Sum of all elements in the array: " + sum);
    }
}
``` 

## 访问原始 HTTP 响应和 Server-Sent Events (SSE)

使用 `MistralAiChatModel` 时，你可以访问原始 HTTP 响应：
```java
SuccessfulHttpResponse rawHttpResponse = ((MistralAiChatResponseMetadata) chatResponse.metadata()).rawHttpResponse();
System.out.println(rawHttpResponse.body());
System.out.println(rawHttpResponse.headers());
System.out.println(rawHttpResponse.statusCode());
```

使用 `MistralAiStreamingChatModel` 时，你可以访问原始 HTTP 响应（见上文）和原始 Server-Sent Events：
```java
List<ServerSentEvent> rawServerSentEvents = ((MistralAiChatResponseMetadata) chatResponse.metadata()).rawServerSentEvents();
System.out.println(rawServerSentEvents.get(0).data());
System.out.println(rawServerSentEvents.get(0).event());
```

## 批处理

`MistralAiBatchChatModel` 实现了核心的 `BatchChatModel` 接口，通过 [Mistral Batch API](https://docs.mistral.ai/capabilities/batch/)
以标准每 token 价格 50% 的费用异步处理大量聊天请求。
批处理中的所有请求都针对批处理模型上配置的单一模型运行。

提交一个批次，轮询直到其达到终止状态，然后读取每个请求的结果（结果保留提交顺序）：
```java
MistralAiBatchChatModel batchModel = MistralAiBatchChatModel.builder()
        .apiKey(System.getenv("MISTRAL_AI_API_KEY"))
        .modelName("mistral-small-latest")
        .build();

BatchResponse<ChatResponse> submitted = batchModel.submit(new BatchRequest<>(List.of(
        ChatRequest.builder().messages(UserMessage.from("What is the capital of France?")).build(),
        ChatRequest.builder().messages(UserMessage.from("What is the capital of Germany?")).build())));

String batchId = submitted.batchId();

// Poll until the batch reaches a terminal state (SUCCEEDED, FAILED, CANCELLED, EXPIRED).
BatchResponse<ChatResponse> batch = batchModel.retrieve(batchId);
while (!batch.state().isTerminal()) {
    Thread.sleep(Duration.ofSeconds(30).toMillis());
    batch = batchModel.retrieve(batchId);
}

for (BatchItemResult<ChatResponse> result : batch.results()) {
    if (result.isSuccess()) {
        System.out.println(result.response().aiMessage().text());
    } else {
        System.out.println("Failed: " + result.error().message());
    }
}
```

正在运行的批次可以被取消，并且可以分页列出已有的批次：
```java
batchModel.cancel(batchId);

BatchPage<ChatResponse> page = batchModel.list(new BatchPagination(20, null));
```

## 示例
- [Mistral AI 示例](https://github.com/langchain4j/langchain4j-examples/tree/main/mistral-ai-examples/src/main/java)