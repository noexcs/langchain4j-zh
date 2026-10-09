# Elasticsearch

https://www.elastic.co/


## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-elasticsearch</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## 概述

`langchain4j-elasticsearch` 模块提供与 Elasticsearch 的集成，使其可作为向量存储和内容检索器使用。

它包含两个主要类：

- [`ElasticsearchEmbeddingStore`](#elasticsearchembeddingstore)：`EmbeddingStore` 接口的一个实现，使用 Elasticsearch 来存储和检索嵌入。
- [`ElasticsearchContentRetriever`](#elasticsearchcontentretriever)：`ContentRetriever` 接口的一个实现，使用 Elasticsearch 基于向量相似度搜索来检索相关文档。

两个类都需要一个 [Elasticsearch Client](https://www.elastic.co/docs/reference/elasticsearch/clients/java) 来连接到 Elasticsearch 服务器。

```java
String apiKey = "VnVhQ2ZHY0JDZGJrU...";
ElasticsearchClient client = ElasticsearchClient.of(ec -> ec
        .host("https://localhost:9200")
        .apiKey(apiKey));
```

**说明：**

> 有关如何创建 ElasticsearchClient 实例，请参阅 [Elasticsearch 文档](https://www.elastic.co/docs/reference/elasticsearch/clients/java/setup/connecting)。

## ElasticsearchEmbeddingStore

要创建 `ElasticsearchEmbeddingStore` 实例，你需要提供一个 `ElasticsearchClient`：

```java
ElasticsearchEmbeddingStore store = ElasticsearchEmbeddingStore.builder()
    .client(client)
    .build();
```

它提供以下选项：

* `indexName`：要使用的 Elasticsearch 索引名称。默认为 `default`。
* `configuration`：要使用的 `ElasticsearchConfiguration`。默认为 `ElasticsearchConfigurationKnn`。
* `refresh`：按 ID 写入或删除的文档何时对搜索可见。默认为 `Refresh.False`。

上面的代码等价于：

```java
ElasticsearchEmbeddingStore store = ElasticsearchEmbeddingStore.builder()
    .client(client)
    .configuration(ElasticsearchConfigurationKnn.builder().build())
    .indexName("default")
    .build();
```

### 刷新策略

写入请求返回后，Elasticsearch 并不会立即让该文档可被搜索。默认情况下，文档会在下一次周期性索引刷新时（除非索引另有配置，否则为每秒一次）对搜索可见。在此之前，文档已被安全存储，并且可以通过 ID 获取，但不会出现在搜索结果中。

当你添加文档后随即执行搜索这些文档的操作时，这一点就很重要。`refresh` 选项让你可以改为等待文档对搜索可见：

```java
import co.elastic.clients.elasticsearch._types.Refresh;

ElasticsearchEmbeddingStore store = ElasticsearchEmbeddingStore.builder()
    .client(client)
    .refresh(Refresh.WaitFor)
    .build();
```

这三个取值分别是：

* `Refresh.False`（默认）：文档存储后立即返回，刷新交由 Elasticsearch 处理。这是最快的选项。
* `Refresh.WaitFor`：文档对搜索可见后才返回。它不会强制额外刷新，因此在你需要可见性时通常是合适的选择。注意，如果索引已关闭自动刷新（`index.refresh_interval: -1`），该调用会一直等待，直到其他操作触发刷新。
* `Refresh.True`：立即强制刷新。这可以在不等待的情况下获得可见性，但每次请求都创建新段会降低索引吞吐量，因此在写入密集的索引上应避免使用。

该选项适用于 `add`、`addAll` 和 `removeAll(Collection<String> ids)`。它不会改变搜索行为，也不会让你免受他人并发写入的影响。`ElasticsearchContentRetriever.builder()` 上也有同样的选项。

带过滤器的删除（`removeAll(Filter)`）是一种按查询删除（delete-by-query）操作，因此它同样只匹配已对搜索可见的文档：稍早添加的嵌入可能不会因此被删除。如果你在添加嵌入后立即通过过滤器将其删除，请配置 `Refresh.WaitFor`，以便删除执行之前写入即可被搜索到。

详见 [Elasticsearch refresh 参数文档](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/refresh-parameter)。

### 存储无嵌入的文档

除常规的 `add(Embedding, TextSegment)` 方法外，该向量存储还可以对纯文本建立索引，而无需为其计算嵌入：

```java
store.add("Printer troubleshooting guide");                    // generates an id
store.add("my-id", "Printer troubleshooting guide");           // with your own id
store.addAllText(List.of("First guide", "Second guide"));      // several at once
```

由于这些文档没有向量，向量搜索永远不会返回它们，无论是使用 [`ElasticsearchConfigurationKnn`](#elasticsearchconfigurationknn) 还是 [`ElasticsearchConfigurationScript`](#elasticsearchconfigurationscript)。全文搜索仍然可以找到它们，因此单个索引可以同时存放带嵌入的文档和纯文本文档，并且你可以使用 [`ElasticsearchConfigurationFullText`](#elasticsearchconfigurationfulltext) 或 [`ElasticsearchConfigurationHybrid`](#elasticsearchconfigurationhybrid) 以两种方式搜索它。

## ElasticsearchContentRetriever

内容检索器需要一个嵌入模型：

```java
EmbeddingModel embeddingModel = new AllMiniLmL6V2QuantizedEmbeddingModel();
```

要创建 `ElasticsearchContentRetriever` 实例，你需要提供 `ElasticsearchClient` 和 `EmbeddingModel`：

```java
ElasticsearchContentRetriever contentRetriever = ElasticsearchContentRetriever.builder()
    .client(client)
    .embeddingModel(embeddingModel)
    .build();
```

它提供以下选项：

* `configuration`：要使用的 `ElasticsearchConfiguration`（参见[下文](#elasticsearchconfiguration)）。默认为 `ElasticsearchConfigurationKnn`。
* `indexName`：要使用的 Elasticsearch 索引名称。默认为 `default`。索引不存在时会自动创建。
* `maxResults`：要检索的最大结果数。默认为 `3`。
* `minScore`：检索结果的最低分数阈值。默认为 `0.0`。
* `filter`：检索期间要应用的 `Filter`（如果有的话）。默认为 `null`。

上面的代码等价于：

```java
ElasticsearchContentRetriever contentRetriever = ElasticsearchContentRetriever.builder()
    .client(client)
    .embeddingModel(embeddingModel)
    .configuration(ElasticsearchConfigurationKnn.builder().build())
    .indexName("default")
    .maxResults(3)
    .minScore(0.0)
    .filter(null)
    .build();
```

## ElasticsearchConfiguration

`ElasticsearchConfiguration` 定义了向量存储或内容检索器如何与 Elasticsearch 服务器交互。你可以通过实现 `ElasticsearchConfiguration` 接口来创建自己的配置，也可以使用提供的实现之一：

- [`ElasticsearchConfigurationKnn`](#elasticsearchconfigurationknn)：使用近似 [kNN 查询](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-knn-query.html)（默认）。
- [`ElasticsearchConfigurationScript`](#elasticsearchconfigurationscript)：使用 [scriptScore 查询](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-script-score-query.html)。注意，此实现使用的是余弦相似度。
- [`ElasticsearchConfigurationFullText`](#elasticsearchconfigurationfulltext)：使用[全文搜索](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-match-query)（仅用于内容检索器）。
- [`ElasticsearchConfigurationHybrid`](#elasticsearchconfigurationhybrid)：使用[混合搜索](https://www.elastic.co/search-labs/tutorials/search-tutorial/vector-search/hybrid-search)（仅用于内容检索器，需要付费许可证）。它将 kNN 向量查询与全文查询相结合。

要创建配置实例，你可以使用每个实现所提供的构建器。例如：

```java
ElasticsearchConfiguration configuration = ElasticsearchConfigurationKnn.builder().build();
```

### ElasticsearchConfigurationKnn

`ElasticsearchConfigurationKnn` 使用近似 kNN 查询来执行向量相似度搜索。

它是 [`ElasticsearchEmbeddingStore`](#elasticsearchembeddingstore) 和 [`ElasticsearchContentRetriever`](#elasticsearchcontentretriever) 所使用的默认配置。

要创建实例，你可以使用构建器：

```java
ElasticsearchConfiguration configuration = ElasticsearchConfigurationKnn.builder().build();
```

它提供以下选项：

* `numCandidates`：搜索期间要考虑的候选邻居数量。默认为 `null`，即使用 Elasticsearch 的默认值。
* `includeVectorResponse`：是否在搜索响应中包含向量字段。默认为 `false`。

> **说明：**
> 从 Elasticsearch 服务器 9.2 版本开始，响应默认不包含向量字段。如果你想在响应中包含向量字段（不推荐），请在构建器中设置 `includeVectorResponse`：
>
> ```java
> ElasticsearchConfigurationKnn configuration = ElasticsearchConfigurationKnn.builder()
>     .includeVectorResponse(true)
>     .build();
> ```

### ElasticsearchConfigurationScript

`ElasticsearchConfigurationScript` 使用 scriptScore 查询来执行向量相似度搜索。注意，此实现使用的是余弦相似度。

它同时可用于 [`ElasticsearchEmbeddingStore`](#elasticsearchembeddingstore) 和 [`ElasticsearchContentRetriever`](#elasticsearchcontentretriever)。

要创建实例，你可以使用构建器：

```java
ElasticsearchConfiguration configuration = ElasticsearchConfigurationScript.builder().build();
```

它提供以下选项：

* `includeVectorResponse`：是否在搜索响应中包含向量字段。默认为 `false`。

> **说明：**
> 从 Elasticsearch 服务器 9.2 版本开始，响应默认不包含向量字段。如果你想在响应中包含向量字段（不推荐），请在构建器中设置 `includeVectorResponse`：
>
> ```java
> ElasticsearchConfiguration configuration = ElasticsearchConfigurationScript.builder()
>     .includeVectorResponse(true)
>     .build();
> ```

### ElasticsearchConfigurationFullText

`ElasticsearchConfigurationFullText` 使用全文搜索来检索相关文档。

它仅可用于 [`ElasticsearchContentRetriever`](#elasticsearchcontentretriever)。

要创建实例，你可以使用构建器：

```java
ElasticsearchConfiguration configuration = ElasticsearchConfigurationFullText.builder().build();
```

### ElasticsearchConfigurationHybrid

`ElasticsearchConfigurationHybrid` 使用混合搜索将 kNN 向量查询与全文查询相结合。注意，混合搜索需要 Elasticsearch 企业版许可证或试用版。

它仅可用于 [`ElasticsearchContentRetriever`](#elasticsearchcontentretriever)。

要创建实例，你可以使用构建器：

```java
ElasticsearchConfiguration configuration = ElasticsearchConfigurationHybrid.builder().build();
```

它提供以下选项：

* `numCandidates`：搜索期间要考虑的候选邻居数量。默认为 `null`，即使用 Elasticsearch 的默认值。
* `includeVectorResponse`：是否在搜索响应中包含向量字段。默认为 `false`。

> **说明：**
> 从 Elasticsearch 服务器 9.2 版本开始，响应默认不包含向量字段。如果你想在响应中包含向量字段（不推荐），请在构建器中设置 `includeVectorResponse`：
>
> ```java
> ElasticsearchConfiguration configuration = ElasticsearchConfigurationHybrid.builder()
>     .includeVectorResponse(true)
>     .build();
> ```

### 创建自定义配置

你可以通过实现 `ElasticsearchConfiguration` 接口来创建自己的 Elasticsearch 配置。例如：

```java
public class MyElasticsearchConfiguration implements ElasticsearchConfiguration {
    @Override
    SearchResponse<Document> vectorSearch(
            ElasticsearchClient client,
            String indexName,
            EmbeddingSearchRequest embeddingSearchRequest) {
        // Your optional custom vector search implementation here
    }

    @Override
    SearchResponse<Document> fullTextSearch(
            ElasticsearchClient client,
            String indexName,
            FullTextSearchRequest request) {
        // Your optional custom full text search implementation here
    }

    @Override
    SearchResponse<Document> hybridSearch(
            ElasticsearchClient client,
            String indexName,
            EmbeddingSearchRequest embeddingSearchRequest,
            String textQuery) {
        // Your optional custom hybrid search implementation here
    }
}
```

请注意，你只需实现与你的用例相关的方法：

* `vectorSearch`：用于向量相似度搜索（`ElasticsearchEmbeddingStore` 和 `ElasticsearchContentRetriever` 均使用）。
* `fullTextSearch`：用于全文搜索（仅 `ElasticsearchContentRetriever` 使用）。
* `hybridSearch`：用于混合搜索（仅 `ElasticsearchContentRetriever` 使用）。

`FullTextSearchRequest` 携带要搜索的 `textQuery`，以及 `ElasticsearchContentRetriever` 上配置的 `maxResults`、`minScore` 和 `filter`。你的实现负责应用这些参数，否则可能会返回不符合过滤条件的文档。

> **说明：**
> 还有一个已弃用的 `fullTextSearch(ElasticsearchClient client, String indexName, String textQuery)` 方法。仅实现了该方法的配置仍可继续工作，但检索器的 `maxResults`、`minScore` 和 `filter` 将被忽略，并且会记录一条警告。请改为实现接收 `FullTextSearchRequest` 参数的方法。

## 示例

- [ElasticsearchEmbeddingStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/elasticsearch-example/src/main/java/ElasticsearchEmbeddingStoreExample.java)
- [ElasticsearchEmbeddingStoreWithScriptExample](https://github.com/langchain4j/langchain4j-examples/blob/main/elasticsearch-example/src/main/java/ElasticsearchEmbeddingStoreWithScriptExample.java)
