# Voyage AI

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-voyage-ai</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## API

- `VoyageAiEmbeddingModel`

## 功能特性

- **多模态**（`voyage-multimodal-3`、`voyage-multimodal-3.5` — 根据模型名称自动检测）：将
  文本和图像嵌入到共享的向量空间中；交错的文本 + 图像会融合为单个嵌入。
  在 `EmbeddingRequest` 中以 `ImageContent`（URL 或 base64）的形式提供图像输入。
- **按调用参数**：`input_type`（`EmbeddingInputType.QUERY` / `DOCUMENT`），以及 Voyage AI 自身的
  `truncation` 和 `encoding_format`（通过 `VoyageAiEmbeddingRequestParameters` 设置）。在构建器上设置的值是
  每次调用的默认值，在请求上设置的值会针对该次调用覆盖它。`truncation(false)`
  会使调用失败，而不是缩短超出模型上下文的输入。`encoding_format`
  （`"base64"`）只是请求更小的响应；你拿回的嵌入是相同的，而且只有文本
  模型接受它，因此多模态模型会拒绝它。
- **监听器**：通过 `VoyageAiEmbeddingModel.builder().listeners(...)` 配置。

请求/响应 API 和多模态用法参见[嵌入模型](../../tutorials/rag.md#嵌入模型embedding-model)。

## 示例

- [VoyageAiEmbeddingModelIT](https://github.com/langchain4j/langchain4j/blob/main/langchain4j-voyage-ai/src/test/java/dev/langchain4j/model/voyageai/VoyageAiEmbeddingModelIT.java)
- [VoyageAiEmbeddingModelExample](https://github.com/langchain4j/langchain4j-examples/blob/main/voyage-ai-examples/src/main/java/VoyageAiEmbeddingModelExample.java)
