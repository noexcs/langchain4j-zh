# OpenAI Official SDK

!!! note
    这是 `OpenAI Official SDK` 集成的文档，它使用[官方 OpenAI Java SDK](https://github.com/openai/openai-java)。

    LangChain4j 提供了 3 种不同的 OpenAI 图像生成集成，这是第 2 种：

    - [OpenAI](../language-models/open-ai.md) 使用 OpenAI REST API 的自定义 Java 实现，与 Quarkus 配合效果最佳（因为它使用 Quarkus REST 客户端），与 Spring 也配合良好（因为它使用 Spring 的 RestClient）。
    - [OpenAI Official SDK](../language-models/open-ai-official.md) 使用官方 OpenAI Java SDK。
    - [Azure OpenAI](../language-models/azure-open-ai.md) 使用 Microsoft 的 Azure SDK，如果你使用的是 Microsoft Java 技术栈（包括高级 Azure 认证机制），则效果最佳。

## 此集成的用例

此集成使用 [OpenAI Java SDK GitHub 仓库](https://github.com/openai/openai-java)，将适用于所有可由以下提供的 OpenAI 模型：

- OpenAI
- Microsoft Foundry

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

要使用 OpenAI 模型，你通常需要端点 URL、API 密钥和模型名称。这取决于模型的托管位置，此集成通过一些自动配置来简化这一过程：

### 通用配置

```java
import com.openai.models.images.ImageModel;
import dev.langchain4j.model.image.ImageModel;
import dev.langchain4j.model.openaiofficial.OpenAiOfficialImageModel;

import static com.openai.models.images.ImageModel.GPT_IMAGE_1_MINI;

// ....

ImageModel model = OpenAiOfficialImageModel.builder()
        .baseUrl(System.getenv("OPENAI_BASE_URL"))
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName(GPT_IMAGE_1_MINI)
        .build();
```

### Microsoft Foundry 和 GitHub Models 的特定配置

与配置 [OpenAI Official Chat Model](../language-models/open-ai-official.md) 类似，你可以使用 `isAzure()` 和 `isGitHubModels()` 方法为 Microsoft Foundry 和 GitHub Models 配置 `OpenAiOfficialImageModel`。

#### Microsoft Foundry

```java
ImageModel model = OpenAiOfficialImageModel.builder()
        .baseUrl(System.getenv("AZURE_OPENAI_ENDPOINT"))
        .apiKey(System.getenv("AZURE_OPENAI_KEY"))
        .modelName(GPT_IMAGE_1_MINI)
        .isAzure(true) // Not necessary if the base URL ends with `openai.azure.com`
        .build();
```

你还可以使用"无密码"认证，如 [OpenAI Official Chat Model](../language-models/open-ai-official.md) 文档中所述。

#### GitHub Models

```java
ImageModel model = OpenAiOfficialImageModel.builder()
        .modelName(GPT_IMAGE_1_MINI)
        .isGitHubModels(true)
        .build();
```

## 使用模型

模型配置完成后，你可以用它来生成图像：

```java
String imageUrl = imageModel
        .generate("A coffee mug in Paris, France")
        .content()
        .base64Data();
```