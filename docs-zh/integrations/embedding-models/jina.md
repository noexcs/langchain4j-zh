# Jina

https://jina.ai/

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-jina</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## API

- `JinaEmbeddingModel`

## 功能

- **多模态**（`jina-clip-v2`、`jina-embeddings-v4` —— 根据模型名称自动检测）：可嵌入文本和图像。Jina 对每个输入项只嵌入一种模态（**不会**融合交错的文本 + 图像）；请在 `EmbeddingRequest` 的每个输入中传入单个 `TextContent` 或单个 `ImageContent`（URL 或 base64）。
- **输入类型**（`jina-embeddings-v3`、`jina-embeddings-v4`、`jina-embeddings-v5` —— 根据模型名称自动检测）：对搜索查询的嵌入方式与其匹配所针对的文档不同，这通常会提高检索质量。可以在每次调用时通过 `EmbeddingRequest` 设置 `EmbeddingInputType.QUERY` 或 `DOCUMENT`，也可以通过 `EmbeddingStoreContentRetriever.embeddingInputType(...)` 设置。不支持该功能的模型（例如 `jina-clip-v2`）会拒绝该参数，而不是静默忽略。
- **监听器**：通过 `JinaEmbeddingModel.builder().listeners(...)` 配置。

有关请求/响应 API 和多模态用法，请参阅[嵌入模型](../../tutorials/rag.md#嵌入模型embedding-model)。

## 示例

- [JinaEmbeddingModelIT](https://github.com/langchain4j/langchain4j/blob/main/langchain4j-jina/src/test/java/dev/langchain4j/model/jina/JinaEmbeddingModelIT.java)
