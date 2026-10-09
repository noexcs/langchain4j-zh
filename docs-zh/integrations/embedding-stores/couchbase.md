# Couchbase

https://www.couchbase.com/


## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-couchbase</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## APIs

- `CouchbaseEmbeddingStore`


## 示例

- [CouchbaseEmbeddingStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/couchbase-example/src/main/java/CouchbaseEmbeddingStoreExample.java)

## Couchbase 嵌入存储
Couchbase 的 langchain4j 集成将每个嵌入存储在独立的文档中，并使用 FTS 向量索引对已存储的向量执行查询。目前，它支持存储嵌入及其元数据，以及删除嵌入。编写本教程时，尚不支持根据元数据过滤向量搜索选中的嵌入。请注意，该向量存储集成仍处于积极开发中，其自带的默认配置不推荐用于生产环境。

### 连接到 Couchbase 集群
可以使用构建器类来初始化 Couchbase 向量存储。初始化时需要以下参数：
- 集群连接字符串
- 集群用户名
- 集群密码
- 存储嵌入的 bucket 名称
- 存储嵌入的 scope 名称
- 存储嵌入的 collection 名称
- 向量存储要使用的 FTS 向量索引名称
- 要存储的向量的维度（长度）

下面的示例代码展示了如何初始化一个连接到本地运行的 Couchbase 服务器的向量存储：

```java
CouchbaseEmbeddingStore embeddingStore = CouchbaseEmbeddingStore.builder()
        .clusterUrl("localhost:8091")
        .username("Administrator")
        .password("password")
        .bucketName("langchain4j")
        .scopeName("_default")
        .collectionName("_default")
        .searchIndexName("test")
        .dimensions(512)
        .build();
```

示例源代码使用 `testcontainers` 库启动一个专用的 Couchbase 服务器：

```java
CouchbaseContainer couchbaseContainer =
        new CouchbaseContainer(DockerImageName.parse("couchbase:enterprise").asCompatibleSubstituteFor("couchbase/server"))
                .withCredentials("Administrator", "password")
                .withBucket(testBucketDefinition)
                .withStartupTimeout(Duration.ofMinutes(1));

CouchbaseEmbeddingStore embeddingStore = CouchbaseEmbeddingStore.builder()
        .clusterUrl(couchbaseContainer.getConnectionString())
        .username(couchbaseContainer.getUsername())
        .password(couchbaseContainer.getPassword())
        .bucketName(testBucketDefinition.getName())
        .scopeName("_default")
        .collectionName("_default")
        .searchIndexName("test")
        .dimensions(384)
        .build();
```

### 向量索引
该向量存储使用 FTS 向量索引来执行向量相似度查找。如果提供的向量索引名称在集群上不存在，向量存储会尝试根据提供的初始化设置，以默认配置创建一个新的索引。建议手动检查所创建索引的设置，并根据具体用例进行调整。有关向量搜索和 FTS 索引配置的更多信息，请参阅 [Couchbase 文档](https://docs.couchbase.com/server/current/vector-search/vector-search.html)。

### 嵌入文档
该集成会为所有存储的嵌入自动分配唯一的基于 `UUID` 的标识符。下面是一个嵌入文档的示例（为便于阅读，向量字段的值已截断）：

```json
{
  "id": "f4831648-07ca-4c77-a031-75acb6c1cf2f",
  "vector": [
    ...
    0.037255168,
    -0.001608681
  ],
  "text": "text",
  "metadata": {
    "some": "value"
  },
  "score": 0
}
```

这些嵌入由开发者选定的嵌入模型生成，所得的向量值因模型而异。

## 在 Couchbase 中存储嵌入
可以使用 `CouchbaseEmbeddingStore` 类的 `add` 和 `addAll` 方法，将嵌入模型生成的嵌入存储到 Couchbase 中：
```java
EmbeddingModel embeddingModel = new AllMiniLmL6V2EmbeddingModel();

TextSegment segment1 = TextSegment.from("I like football.");
Embedding embedding1 = embeddingModel.embed(segment1).content();
embeddingStore.add(embedding1, segment1);

TextSegment segment2 = TextSegment.from("The weather is good today.");
Embedding embedding2 = embeddingModel.embed(segment2).content();
embeddingStore.add(embedding2, segment2);

Thread.sleep(1000); // to be sure that embeddings were persisted
```

## 查询相关嵌入
向向量存储中添加一些嵌入后，可以使用查询向量在向量存储中查找与之相关的嵌入。这里，我们使用嵌入模型为短语 "what is your favorite sport?" 生成一个向量，然后使用该向量在数据库中查找最相关的回答：
```java
Embedding queryEmbedding = embeddingModel.embed("What is your favourite sport?").content();
EmbeddingSearchRequest searchRequest = EmbeddingSearchRequest.builder()
        .queryEmbedding(queryEmbedding)
        .maxResults(1)
        .build();
EmbeddingSearchResult<TextSegment> searchResult = embeddingStore.search(searchRequest);
EmbeddingMatch<TextSegment> embeddingMatch = searchResult.matches().get(0);
```

然后，可以将所选回答的相关性得分和文本打印到应用程序输出：
```java
System.out.println(embeddingMatch.score()); // 0.81442887
System.out.println(embeddingMatch.embedded().text()); // I like football.
```

## 删除嵌入
Couchbase 向量存储还支持根据标识符删除嵌入，例如：
```java
embeddingStore.remove(embeddingMatch.id())
```

或者，要删除所有嵌入：
```java
embeddingStore.removeAll();
```
