# Amazon Bedrock


## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-bedrock</artifactId>
    <version>1.22.0</version>
</dependency>
```


## AWS 凭证
要使用 Amazon Bedrock 嵌入，你需要配置 AWS 凭证。
其中一个选项是设置 `AWS_ACCESS_KEY_ID` 和 `AWS_SECRET_ACCESS_KEY` 环境变量。
更多信息可参阅[这里](https://docs.aws.amazon.com/bedrock/latest/userguide/security-iam.html)。

## Cohere 模型
- `BedrockCohereEmbeddingModel`

## Cohere 嵌入模型
支持 Bedrock Cohere 嵌入模型，可使用以下版本：

- **`cohere.embed-english-v3`**
- **`cohere.embed-multilingual-v3`**

这些模型非常适合为英文和多语言文本处理任务生成高质量的文本嵌入。

### 实现示例

下面是一个配置和使用 Bedrock 嵌入模型的示例：

```
BedrockCohereEmbeddingModel embeddingModel = BedrockCohereEmbeddingModel
        .builder()
        .region(Region.US_EAST_1)
        .model("cohere.embed-multilingual-v3")
        .inputType(BedrockCohereEmbeddingModel.InputType.SEARCH_QUERY)
        .truncation(BedrockCohereEmbeddingModel.Truncate.NONE)
        .build();
```

## API

- `BedrockTitanEmbeddingModel`
- `BedrockCohereEmbeddingModel`

## Titan 多模态嵌入

`BedrockTitanEmbeddingModel` 支持 Amazon Titan 多模态嵌入（`amazon.titan-embed-image-v1`）：它
将文本和/或单张图像嵌入到一个（融合的）嵌入中。

```java
EmbeddingModel model = BedrockTitanEmbeddingModel.builder()
    .model("amazon.titan-embed-image-v1")
    .region(Region.US_EAST_1)
    .build();

EmbeddingResponse response = model.embed(EmbeddingRequest.builder()
    .input(TextContent.from("a photo of a cat"), ImageContent.from(base64Data, "image/png"))
    .build());
```

Titan 需要 **base64** 图像数据（不支持 URL）。监听器可通过
`.listeners(...)` 配置。请求/响应 API 请参阅[嵌入模型](../../tutorials/rag.md#嵌入模型embedding-model)。

## 示例

- [BedrockEmbeddingIT](https://github.com/langchain4j/langchain4j/blob/main/langchain4j-bedrock/src/test/java/dev/langchain4j/model/bedrock/BedrockEmbeddingIT.java)
