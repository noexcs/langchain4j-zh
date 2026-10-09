# MongoDB Atlas

[MongoDB Atlas](https://www.mongodb.com/docs/atlas/) 是一个全托管的
云数据库，可在 AWS、Azure 和 GCP 上使用。它支持对 MongoDB
文档数据原生进行向量搜索和全文搜索（BM25 算法）。

[Atlas 向量搜索](https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-overview/)
功能允许你将嵌入存储在 MongoDB 文档中，创建
向量搜索索引，并使用一种名为 Hierarchical Navigable Small Worlds 的近似
最近邻算法执行 KNN 搜索。
LangChain4j 的 MongoDB 集成内部使用
[`$vectorSearch`](https://www.mongodb.com/docs/atlas/atlas-vector-search/vector-search-stage/#mongodb-pipeline-pipe.-vectorSearch)
聚合阶段实现了 Atlas 向量搜索。

你可以使用 LangChain4j 搭配 Atlas 向量搜索对你的数据执行语义
搜索，并构建一个简单的 RAG 实现。要查看执行这些任务的
完整教程，请参阅 MongoDB Atlas 文档中的
[开始使用 LangChain4j 集成](https://www.mongodb.com/docs/atlas/atlas-vector-search/ai-integrations/langchain4j/)
教程。

## 前提条件

要使用 Atlas 向量搜索，你必须拥有一个正在运行以下 MongoDB Server 版本
的部署：

-   6.0.11 或更高版本
-   7.0.2 或更高版本

MongoDB 提供永久免费的集群。请参阅
[开始使用 Atlas](https://www.mongodb.com/docs/atlas/getting-started/) 教程，了解更多关于
设置账户并连接部署的信息。

此外，你还需要一个拥有额度的 LLM 服务的 API 密钥，该服务
提供嵌入模型，例如提供免费额度的
[Voyage AI](https://www.voyageai.com/)。对于 RAG
应用，你还必须拥有一个提供聊天模型
功能的服务的 API 密钥，例如 [OpenAI](https://openai.com/api/) 或来自
[HuggingFace](https://huggingface.co/) 的模型。

## 环境和安装

1. 在你首选的 IDE 中创建一个新的 Java 应用。
2. 向应用添加以下依赖，以安装
   LangChain4j 和 MongoDB Java Sync Driver：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-mongodb-atlas</artifactId>
</dependency>
<dependency>
    <groupId>org.mongodb</groupId>
    <artifactId>mongodb-driver-sync</artifactId>
    <version>5.4.0</version>
</dependency>
```

你还必须安装嵌入模型的依赖，例如
Voyage AI：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-voyage-ai</artifactId>
</dependency>
```

我们还建议添加 LangChain4j BOM：

```xml
<dependencyManagement>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-bom</artifactId>
        <version>1.22.0-beta32</version>
        <type>pom</type>
    </dependency>
</dependencyManagement>
```

## 将 MongoDB Atlas 用作嵌入存储

1. 实例化一个[嵌入模型](https://docs.langchain4j.dev/category/embedding-models)。
2. 将 MongoDB Atlas 实例化为嵌入存储。

在构建 `MongoDbEmbeddingStore`
实例时，向 `createIndex()` 方法传入 `true`，
可以启用自动索引创建。

```java
import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import dev.langchain4j.data.document.Metadata;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.voyageai.VoyageAiEmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingMatch;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingSearchResult;
import dev.langchain4j.store.embedding.filter.comparison.*;
import dev.langchain4j.store.embedding.mongodb.IndexMapping;
import dev.langchain4j.store.embedding.mongodb.MongoDbEmbeddingStore;
import org.bson.Document;

import java.io.*;
import java.util.*;

String embeddingApiKey = System.getenv("VOYAGE_AI_KEY");
String uri = System.getenv("MONGODB_URI");

EmbeddingModel embeddingModel = VoyageAiEmbeddingModel.builder()
        .apiKey(embeddingApiKey)
        .modelName("voyage-3")
        .build();

MongoClient mongoClient = MongoClients.create(uri);

System.out.println("Instantiating the embedding store...");

// Set to false if the vector index already exists
Boolean createIndex = true;

IndexMapping indexMapping = IndexMapping.builder()
        .dimension(embeddingModel.dimension())
        .metadataFieldNames(new HashSet<>())
        .build();

MongoDbEmbeddingStore embeddingStore = MongoDbEmbeddingStore.builder()
        .databaseName("search")
        .collectionName("langchaintest")
        .createIndex(createIndex)
        .indexName("vector_index")
        .indexMapping(indexMapping)
        .fromClient(mongoClient)
        .build();
```

## 将数据存储到 MongoDB

这段代码演示了如何将文档持久化到
嵌入存储。`embed()` 方法会为文档中 `text`
字段的值生成嵌入。

```java
ArrayList<Document> docs = new ArrayList<>();

docs.add(new Document()
        .append("text", "Penguins are flightless seabirds that live almost exclusively below the equator. Some island-dwellers can be found in warmer climates.")
        .append("metadata", new Metadata(Map.of("website", "Science Direct"))));

docs.add(new Document()
        .append("text", "Emperor penguins are amazing birds. They not only survive the Antarctic winter, but they breed during the worst weather conditions on earth.")
        .append("metadata", new Metadata(Map.of("website", "Our Earth"))));

docs.add(...);

System.out.println("Persisting document embeddings...");

for (Document doc : docs) {
    TextSegment segment = TextSegment.from(
            doc.getString("text"),
            doc.get("metadata", Metadata.class)
    );
    Embedding embedding = embeddingModel.embed(segment).content();
    embeddingStore.add(embedding, segment);
}
```

## 执行语义/相似度搜索

这段代码演示了如何创建一个搜索请求，将你的
查询转换为向量，并返回语义相似的文档。
返回的 `EmbeddingMatch` 实例包含文档内容
以及描述每个结果与查询匹配程度的分数。

```java
String query = "Where do penguins live?";
Embedding queryEmbedding = embeddingModel.embed(query).content();

EmbeddingSearchRequest searchRequest = EmbeddingSearchRequest.builder()
        .queryEmbedding(queryEmbedding)
        .maxResults(3)
        .build();

System.out.println("Performing the query...");

EmbeddingSearchResult<TextSegment> searchResult = embeddingStore.search(searchRequest);
List<EmbeddingMatch<TextSegment>> matches = searchResult.matches();

for (EmbeddingMatch<TextSegment> embeddingMatch : matches) {
    System.out.println("Response: " + embeddingMatch.embedded().text());
    System.out.println("Author: " + embeddingMatch.embedded().metadata().getString("author"));
    System.out.println("Score: " + embeddingMatch.score());
}
```

### 元数据过滤

你可以在构建 `EmbeddingSearchRequest` 时，
使用 `filter()` 方法实现元数据过滤。`filter()` 方法接受一个
继承自
[Filter](https://docs.langchain4j.dev/apidocs/dev/langchain4j/store/embedding/filter/Filter.html) 的参数。

这段代码实现了元数据过滤，仅针对
`website` 值为所列值之一的文档。

```java
EmbeddingSearchRequest searchRequest = EmbeddingSearchRequest.builder()
        .queryEmbedding(queryEmbedding)
        .filter(new IsIn("website", List.of("Our Earth", "Natural Habitats")))
        .maxResults(3)
        .build();
```

## RAG

要查看使用 MongoDB Atlas 作为向量存储
实现 RAG 的说明，请参阅 Atlas 文档中 LangChain4j 教程的
[使用你的数据回答问题](https://www.mongodb.com/docs/atlas/atlas-vector-search/ai-integrations/langchain4j/#use-your-data-to-answer-questions)
部分。

## API 文档

-   [MongoDB Atlas 嵌入存储集成](https://docs.langchain4j.dev/apidocs/dev/langchain4j/store/embedding/mongodb/package-summary.html)

-   [MongoDB Java Sync Driver](https://mongodb.github.io/mongo-java-driver/5.4/apidocs/mongodb-driver-sync/index.html)

## 相关链接

-   [开始使用 LangChain4j 集成](https://www.mongodb.com/docs/atlas/atlas-vector-search/ai-integrations/langchain4j/)
-   [如何使用 LangChain4j 构建 RAG 应用](https://dev.to/mongodb/how-to-make-a-rag-application-with-langchain4j-1mad)
