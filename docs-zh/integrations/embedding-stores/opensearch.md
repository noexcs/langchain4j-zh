# OpenSearch

https://opensearch.org/


## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-opensearch</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```


## API

`OpenSearchEmbeddingStore` 使用带评分脚本实现的精确 k-NN 进行相似度搜索。
更多详情请参见 [OpenSearch k-NN 文档](https://opensearch.org/docs/latest/search-plugins/knn/knn-score-script/)。

### 功能

- **元数据过滤**：支持使用 `Filter` API 按元数据过滤搜索结果
- **删除操作**：
  - 按 ID 删除嵌入
  - 按元数据过滤器删除嵌入
  - 删除所有嵌入（删除索引）
- **AWS 支持**：原生支持 Amazon OpenSearch Service 和 Amazon OpenSearch Serverless

### 基本用法

要为本地或网络可达的 OpenSearch 创建 `OpenSearchEmbeddingStore` 实例：

```java
OpenSearchEmbeddingStore store = OpenSearchEmbeddingStore.builder()
        .serverUrl("http://localhost:9200")
        .indexName("my-embeddings")
        .build();
```

使用认证：

```java
OpenSearchEmbeddingStore store = OpenSearchEmbeddingStore.builder()
        .serverUrl("https://my-opensearch.example.com:9200")
        .userName("admin")
        .password("admin")
        .indexName("my-embeddings")
        .build();
```

### AWS OpenSearch

对于 Amazon OpenSearch Service 或 OpenSearch Serverless：

```java
AwsSdk2TransportOptions options = AwsSdk2TransportOptions.builder()
        .setCredentials(DefaultCredentialsProvider.create())
        .build();

OpenSearchEmbeddingStore store = OpenSearchEmbeddingStore.builder()
        .serverUrl("https://search-domain.us-east-1.es.amazonaws.com")
        .serviceName("es") // or "aoss" for Serverless
        .region("us-east-1")
        .options(options)
        .indexName("my-embeddings")
        .build();
```

### 元数据过滤

按元数据过滤搜索结果：

```java
Filter filter = metadataKey("category").isEqualTo("documentation");

EmbeddingSearchRequest searchRequest = EmbeddingSearchRequest.builder()
        .queryEmbedding(queryEmbedding)
        .filter(filter)
        .maxResults(10)
        .build();

EmbeddingSearchResult<TextSegment> result = store.search(searchRequest);
```

支持的过滤操作：
- 比较：`isEqualTo`、`isNotEqualTo`、`isGreaterThan`、`isGreaterThanOrEqualTo`、`isLessThan`、`isLessThanOrEqualTo`
- 集合：`isIn`、`isNotIn`
- 逻辑：`and`、`or`、`not`

### 删除操作

按 ID 删除嵌入：
```java
store.removeAll(List.of("id1", "id2", "id3"));
```

按元数据过滤器删除嵌入：
```java
Filter filter = metadataKey("status").isEqualTo("archived");
store.removeAll(filter);
```

删除所有嵌入（删除索引）：
```java
store.removeAll();
```


## 示例

- [OpenSearchEmbeddingStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/opensearch-example/src/main/java/OpenSearchEmbeddingStoreExample.java)