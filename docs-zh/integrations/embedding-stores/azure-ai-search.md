# Azure AI Search

https://azure.microsoft.com/en-us/products/ai-services/ai-search/


## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-azure-ai-search</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## API

- `AzureAiSearchEmbeddingStore` - 支持向量搜索
- `AzureAiSearchContentRetriever` - 支持向量、全文、混合搜索和重排


## 来自自带索引的元数据

默认情况下，`AzureAiSearchContentRetriever` 和 `AzureAiSearchEmbeddingStore` 从它们
自己写入的嵌套 `metadata` 字段中读取片段元数据。当你让它们指向一个已存在的索引
（`createOrUpdateIndex(false)`），且该索引的字段存储在文档根层时，请在任一构建器上使用
`metadataFieldNames` 列出要作为元数据暴露的顶层字段：

```java
ContentRetriever retriever = AzureAiSearchContentRetriever.builder()
        .endpoint(endpoint)
        .tokenCredential(tokenCredential)
        .indexName(indexName)
        .createOrUpdateIndex(false)
        .queryType(AzureAiSearchQueryType.FULL_TEXT)
        .metadataFieldNames(List.of("sourcepage", "weburl", "topic", "role"))
        .maxResults(4)
        .build();
```

当某个列出的字段的值是 `Metadata` 支持的类型
（`String`、`Integer`、`Long`、`Float`、`Double` 或 `UUID`）时，该字段会被复制到片段的 `Metadata` 中。
不存在的字段、`null` 字段或其他类型的字段（例如嵌入向量）会被跳过。字段必须在 Azure
索引中被标记为可检索，其值才会被返回；且当字段名与嵌套 `metadata` 中的某个键
匹配时，顶层值优先。

此选项仅配置元数据提取；索引的核心 ID、内容、向量和语义搜索字段的
现有要求保持不变。

## 示例

- [AzureAiSearchEmbeddingStoreIT](https://github.com/langchain4j/langchain4j/blob/main/langchain4j-azure-ai-search/src/test/java/dev/langchain4j/store/embedding/azure/search/AzureAiSearchEmbeddingStoreIT.java)
- [AzureAiSearchContentRetrieverIT](https://github.com/langchain4j/langchain4j/blob/main/langchain4j-azure-ai-search/src/test/java/dev/langchain4j/rag/content/retriever/azure/search/AzureAiSearchContentRetrieverIT.java)
