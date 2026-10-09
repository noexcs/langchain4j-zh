# Cohere

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-cohere</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## API

- `CohereEmbeddingModel`

## 功能

- **多模态**（`embed-v4.0`）：将文本和图像嵌入到共享的向量空间；交错的文本 + 图像会融合为单个嵌入。请在 `EmbeddingRequest` 中以 `ImageContent`（URL 或 base64）提供图像输入。
- **每次调用的参数**：`input_type` —— 对查询和文档采用不同的嵌入方式（`EmbeddingInputType.QUERY` / `DOCUMENT`，映射到 Cohere 的 `search_query` / `search_document`）。
- **监听器**：通过 `CohereEmbeddingModel.builder().listeners(...)` 配置。

有关请求/响应 API 和多模态用法，请参阅[嵌入模型](../../tutorials/rag.md#嵌入模型embedding-model)。

## 示例

- [CohereEmbeddingModelIT](https://github.com/langchain4j/langchain4j/blob/main/langchain4j-cohere/src/test/java/dev/langchain4j/model/cohere/CohereEmbeddingModelIT.java)
