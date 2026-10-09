# OpenAI Official SDK

!!! note
    这是 `OpenAI Official SDK` 集成的文档，它使用[官方 OpenAI Java SDK](https://github.com/openai/openai-java)。

    LangChain4j 提供了 3 种不同的 OpenAI 嵌入模型集成，这是其中的 #2：

    - [OpenAI](../language-models/open-ai.md) 使用 OpenAI REST API 的自定义 Java 实现，与 Quarkus（因为它使用 Quarkus REST 客户端）和 Spring（因为它使用 Spring 的 RestClient）搭配效果最佳。
    - [OpenAI Official SDK](../language-models/open-ai-official.md) 使用官方 OpenAI Java SDK。
    - [Azure OpenAI](../language-models/azure-open-ai.md) 使用微软的 Azure SDK，如果你在使用微软 Java 技术栈（包括高级 Azure 认证机制），搭配效果最佳。

## 此集成的使用场景

此集成使用 [OpenAI Java SDK GitHub 仓库](https://github.com/openai/openai-java)，适用于所有可由以下提供商提供的 OpenAI 模型：

- OpenAI
- Azure OpenAI
- GitHub Models

它也适用于支持 OpenAI API 的模型。

## OpenAI 文档

- [OpenAI Java SDK GitHub 仓库](https://github.com/openai/openai-java)
- [OpenAI API 文档](https://platform.openai.com/docs/introduction)
- [OpenAI API 参考](https://platform.openai.com/docs/api-reference)

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-official</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## 配置模型

要使用 OpenAI 模型，你通常需要端点 URL、API 密钥和模型名称。这取决于模型托管在哪里，此集成尝试
通过一些自动配置来简化这一过程：

### 通用配置

```java
import com.openai.models.embeddings.EmbeddingModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.openaiofficial.OpenAiOfficialEmbeddingModel;

import static com.openai.models.embeddings.EmbeddingModel.TEXT_EMBEDDING_3_SMALL;

// ....

EmbeddingModel model = OpenAiOfficialEmbeddingModel.builder()
        .baseUrl(System.getenv("AZURE_OPENAI_ENDPOINT"))
        .apiKey(System.getenv("AZURE_OPENAI_KEY"))
        .modelName(TEXT_EMBEDDING_3_SMALL)
        .build();
```

### Azure OpenAI 和 GitHub Models 的特定配置

类似于配置 [OpenAI Official Chat Model](../language-models/open-ai-official.md)，你可以使用
`isAzure()` 和 `isGitHubModels()` 方法将 `OpenAiOfficialEmbeddingModel` 配置为 Azure OpenAI 和 GitHub Models。

#### Azure OpenAI

```java
EmbeddingModel model = OpenAiOfficialEmbeddingModel.builder()
        .baseUrl(System.getenv("AZURE_OPENAI_ENDPOINT"))
        .apiKey(System.getenv("AZURE_OPENAI_KEY"))
        .modelName(TEXT_EMBEDDING_3_SMALL)
        .isAzure(true) // Not necessary if the base URL ends with `openai.azure.com`
        .build();
```

你还可以使用"无密码"认证，如 [OpenAI Official Chat Model](../language-models/open-ai-official.md) 文档中所述。

#### GitHub Models

```java
EmbeddingModel model = OpenAiOfficialEmbeddingModel.builder()
        .modelName(TEXT_EMBEDDING_3_SMALL)
        .isGitHubModels(true)
        .build();
```

## 使用模型

模型配置完成后，你可以用它来创建嵌入：

```java
Response<Embedding> response = model.embed("Please embed this sentence.");
```
