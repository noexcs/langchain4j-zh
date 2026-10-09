# Neo4j

[Neo4j](https://neo4j.com/) 是一个高性能的开源图数据库，专为管理相互关联的数据而设计。
Neo4j 的原生图模型非常适合对复杂且高度互联的领域进行建模，例如社交图谱、推荐系统和知识网络。
通过其在 LangChain4j 中的集成，可以在 Langchain4j 库中使用 [Neo4j Vector](https://github.com/neo4j-documentation/labs-pages/blob/publish/modules/genai-ecosystem/pages/vector-search.adoc) 功能。

## Maven 依赖
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-neo4j</artifactId>
    <version>${latest version here}</version>
</dependency>

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-neo4j-retriever</artifactId>
    <version>${latest version here}</version>
</dependency>

<!-- if we want to use the Spring Boot starter -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-neo4j-spring-boot-starter</artifactId>
    <version>${latest version here}</version>
</dependency>
```
## API

LangChain4j 为 Neo4j 集成提供了以下类：
- `Neo4jEmbeddingStore`：实现了 EmbeddingStore 接口，支持在 Neo4j 数据库中存储和查询向量嵌入。
- `Neo4jText2CypherRetriever`：实现了 ContentRetriever 接口，用于从用户问题生成并执行 Cypher 查询，从而改进从 Neo4j 数据库中的内容检索。它将自然语言问题翻译为 Cypher 查询，
  并利用通过 [apoc.meta.data](https://neo4j.com/docs/apoc/current/overview/apoc.meta/apoc.meta.data) 过程计算的 Neo4j 架构。
- `KnowledgeGraphWriter`：一个用于存储 Neo4j 节点和关系的类，其起点是来自 `LLMGraphTransformer` 的结构化数据，
  后者是一个将一份或多份非结构化文档转换为图的工具。它与数据库无关，意味着它可以将文本转换为一组节点和边，这些节点和边也可以用于 RedisGraph 等其他图数据库。
- `Neo4jEmbeddingStoreIngestor`：实现了 `ParentChildEmbeddingStoreIngestor` 接口，它执行多阶段转换流水线：转换文档、将它们切分为段落、可选地对子段落应用额外转换、生成嵌入，并将父子关系和嵌入一起存储在 Neo4j 中。
- `Neo4jChatMemoryStore`：实现了 `ChatMemoryStore` 接口，在 Neo4j 图数据库中存储和检索对话消息。它支持使用 Neo4j 节点和关系高效地查询和持久化，从而管理聊天历史。

## 使用示例

### Neo4jEmbeddingStore

以下是创建 `Neo4jEmbeddingStore` 实例的方法：

```java
Neo4jEmbeddingStore embeddingStore = Neo4jEmbeddingStore.builder().<builderParameters>.build();
```

其中 `<builderParameters>` 必须包含 `dimension` 以及 `driver` 或 `withBasicAuth` 参数，以及其他可选参数。

以下是完整的构建器列表：

| 键                 | 默认值| 描述        |
| ------------------- |-----| --------------------- |
| `driver`            | *如果未设置 `withBasicAuth` 则必填*   | [Java Driver 实例](https://neo4j.com/docs/api/java-driver/current/org.neo4j.driver/org/neo4j/driver/Driver.html) |
| `withBasicAuth`     | *如果未设置 `driver` 则必填*       | 从 `uri`、`user` 和 `password` 创建 [Java Driver 实例](https://neo4j.com/docs/api/java-driver/current/org.neo4j.driver/org/neo4j/driver/Driver.html) |
| `dimension`         | *必填*    | 向量的维度  |
| `config`            | `org.neo4j.driver.SessionConfig.forDatabase("<databaseName>")`   | [SessionConfig 实例](https://neo4j.com/docs/api/java-driver/current/org.neo4j.driver/org/neo4j/driver/SessionConfig.html)                                |
| `label`             | `"Document"`| 标签名称    |
| `embeddingProperty` | `"embedding"` | 嵌入属性名称 |
| `idProperty`        | `"id"` | ID 属性名称  |
| `metadataPrefix`    | `""`       | 元数据前缀   |
| `textProperty`      | `"text"`  | 文本属性名称 |
| `indexName`         | `"vector"` | 向量索引名称  |
| `databaseName`      | `"neo4j"`| 数据库名称  |
| `retrievalQuery`    | `"RETURN properties(node) AS metadata, node.idProperty AS idProperty, node.textProperty AS textProperty, node.embeddingProperty AS embeddingProperty, score"`  | 检索查询     |




因此，要创建 `Neo4jEmbeddingStore` 实例，你需要提供适当的设置：
```java
// ---> MINIMAL EMBEDDING <---
Neo4jEmbeddingStore minimalEmbedding = Neo4jEmbeddingStore.builder()
    .withBasicAuth(NEO4J_CONNECTION_STRING, USERNAME, ADMIN_PASSWORD)
    .dimension(384)
    .build();

// ---> CUSTOM EMBEDDING <---
Neo4jEmbeddingStore customEmbeddingStore = Neo4jEmbeddingStore.builder()
        .withBasicAuth(NEO4J_CONNECTION_STRING, USERNAME, ADMIN_PASSWORD)
        .dimension(384)
        .indexName(CUSTOM_INDEX)
        .metadataPrefix(CUSTOM_METADATA_PREF)
        .label(CUSTOM_LABEL)
        .embeddingProperty(CUSTOM_PROP)
        .idProperty(CUSTOM_ID)
        .textProperty(CUSTOM_TEXT)
        .build();
```
然后你可以通过许多不同的方式添加嵌入，并对其进行搜索：
```java
// ---> ADD MINIMAL EMBEDDING <---
Embedding embedding = embeddingModel.embed("embedText").content();
String id = minimalEmbedding.add(embedding); // output: id of the embedding

// ---> ADD MINIMAL EMBEDDING WITH ID <---
String id = randomUUID();
Embedding embedding = embeddingModel.embed("embedText").content();
minimalEmbedding.add(id, embedding);

// ---> ADD EMBEDDING WITH SEGMENT <---
TextSegment segment = TextSegment.from(randomUUID());
Embedding embedding = embeddingModel.embed(segment.text()).content();
String id = minimalEmbedding.add(embedding, segment);

// ---> ADD EMBEDDING WITH SEGMENT AND METADATA <---
TextSegment segment = TextSegment.from(randomUUID(), Metadata.from(METADATA_KEY, "test-value"));
Embedding embedding = embeddingModel.embed(segment.text()).content();
String id = minimalEmbedding.add(embedding, segment);

// ---> ADD MULTIPLE EMBEDDINGS <---
Embedding firstEmbedding = embeddingModel.embed("firstEmbedText").content();
Embedding secondEmbedding = embeddingModel.embed("secondEmbedText").content();
List<String> ids = minimalEmbedding.addAll(asList(firstEmbedding, secondEmbedding));

// ---> ADD MULTIPLE EMBEDDINGS WITH SEGMENTS <---
TextSegment firstSegment = TextSegment.from("firstText");
Embedding firstEmbedding = embeddingModel.embed(firstSegment.text()).content();
TextSegment secondSegment = TextSegment.from("secondText");
Embedding secondEmbedding = embeddingModel.embed(secondSegment.text()).content();
List<String> ids = minimalEmbedding.addAll(
        asList(firstEmbedding, secondEmbedding),
        asList(firstSegment, secondSegment)
);
```
然后你可以搜索已存储的嵌入：
```java
// ---> SEARCH EMBEDDING WITH MAX RESULTS <---
String id = minimalEmbedding.add(embedding);
final EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
        .queryEmbedding(embedding)
        .maxResults(10)
        .build();
final List<EmbeddingMatch<TextSegment>> relevant = embeddingStore.search(request).matches();

// ---> SEARCH EMBEDDING WITH MIN SCORE <---
Embedding embedding = embeddingModel.embed("embedText").content();
String id = minimalEmbedding.add(embedding);
final EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
        .queryEmbedding(embedding)
        .maxResults(10)
        .minScore(0.15)
        .build();
final List<EmbeddingMatch<TextSegment>> relevant = embeddingStore.search(request).matches();

// ---> SEARCH EMBEDDING WITH CUSTOM METADATA PREFIX <---
String metadataCompleteKey = CUSTOM_METADATA_PREF + METADATA_KEY;
TextSegment segment = TextSegment.from(randomUUID(), Metadata.from(METADATA_KEY, "test-value"));
Embedding embedding = embeddingModel.embed(segment.text()).content();
String id = customEmbeddingStore.add(embedding, segment);
final EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
        .queryEmbedding(embedding)
        .maxResults(10)
        .build();
final List<EmbeddingMatch<TextSegment>> relevant = embeddingStore.search(request).matches();

// ---> SEARCH EMBEDDING WITH CUSTOM ID PROPERTY <---
String metadataCompleteKey = CUSTOM_METADATA_PREF + METADATA_KEY;
TextSegment segment = TextSegment.from(randomUUID(), Metadata.from(METADATA_KEY, "test-value"));
Embedding embedding = embeddingModel.embed(segment.text()).content();
String id = embeddingStore.add(embedding, segment);
final EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
                .queryEmbedding(embedding)
                .maxResults(10)
                .build();
final List<EmbeddingMatch<TextSegment>> relevant = embeddingStore.search(request).matches();

// ---> SEARCH MULTIPLE EMBEDDING <---
List<String> ids = minimalEmbedding.addAll(asList(firstEmbedding, secondEmbedding));
final EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
        .queryEmbedding(firstEmbedding)
        .maxResults(10)
        .build();
final List<EmbeddingMatch<TextSegment>> relevant = embeddingStore.search(request).matches();

// ---> SEARCH MULTIPLE EMBEDDING WITH SEGMENTS <---
List<String> ids = minimalEmbedding.addAll(
        asList(firstEmbedding, secondEmbedding),
        asList(firstSegment, secondSegment)
);
final EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
        .queryEmbedding(firstEmbedding)
        .maxResults(10)
        .build();
final List<EmbeddingMatch<TextSegment>> relevant = embeddingStore.search(request).matches();
```

要通过同时利用向量索引和全文索引的混合搜索来获取嵌入：
```java
// ---> ADDS EMBEDDING AND FULLTEXT WITH ID <---
embeddingStore = Neo4jEmbeddingStore.builder()
        .withBasicAuth("<Bolt URL>", "<username>", "<password>")
        .dimension(384)
        .fullTextIndexName("movie_text")
        .fullTextQuery("Matrix")
        .autoCreateFullText(true)
        .label(LABEL_TO_SANITIZE)
        .build();

List<Embedding> embeddings =
        embeddingModel.embedAll(List.of(TextSegment.from("test"))).content();
        embeddingStore.addAll(embeddings);

final Embedding queryEmbedding = embeddingModel.embed("Matrix").content();

final EmbeddingSearchRequest embeddingSearchRequest = EmbeddingSearchRequest.builder()
        .queryEmbedding(queryEmbedding)
        .maxResults(1)
        .build();

final List<EmbeddingMatch<TextSegment>> matches =
        embeddingStore.search(embeddingSearchRequest).matches();

// ---> SEARCH EMBEDDING WITH AUTOCREATED FULLTEXT <---
final String fullTextIndexName = "movie_text";
final String label = "Movie";
final String fullTextSearch = "Matrix";
embeddingStore = Neo4jEmbeddingStore.builder()
        .withBasicAuth("<Bolt URL>", "<username>", "<password>")
        .dimension(384)
        .label(label)
        .indexName("movie_vector_idx")
        .fullTextIndexName(fullTextIndexName)
        .fullTextQuery(fullTextSearch)
        .build();
```

如果 FULLTEXT 索引无效，将抛出描述性的异常：
```java
// ---> ERROR HANDLING WITH INVALID FULLTEXT <---
Neo4jEmbeddingStore embeddingStore = Neo4jEmbeddingStore.builder()
        .withBasicAuth("<Bolt URL>", "<username>", "<password>")
        .dimension(384)
        .fullTextIndexName("full_text_with_invalid_retrieval")
        .fullTextQuery("Matrix")
        .autoCreateFullText(true)
        .fullTextRetrievalQuery("RETURN properties(invalid) AS metadata")
        .label(LABEL_TO_SANITIZE)
        .build();

List<Embedding> embeddings = embeddingModel.embedAll(List.of(TextSegment.from("test"))).content();
embeddingStore.addAll(embeddings);

final Embedding queryEmbedding = embeddingModel.embed("Matrix").content();

final EmbeddingSearchRequest embeddingSearchRequest = EmbeddingSearchRequest.builder()
        .queryEmbedding(queryEmbedding)
        .maxResults(3)
        .build();
embeddingStore.search(embeddingSearchRequest).matches();
// This search will throw a ClientException: ... Variable `invalid` not defined ...
```

要利用 `dev.langchain4j.store.embedding.filter.Filter` 类执行带元数据过滤的搜索：
```java
// ---> ADD EMBEDDING WITH ID AND RETRIEVE WITH OR WITHOUT PREFILTER <---
final List<TextSegment> segments = IntStream.range(0, 10)
                .boxed()
                .map(i -> {
                    if (i == 0) {
                        final Map<String, Object> metas =
                                Map.of("key1", "value1", "key2", 10, "key3", "3", "key4", "value4");
                        final Metadata metadata = new Metadata(metas);
                        return TextSegment.from(randomUUID(), metadata);
                    }
                    return TextSegment.from(randomUUID());
                })
                .toList();

final List<Embedding> embeddings = embeddingModel.embedAll(segments).content();
embeddingStore.addAll(embeddings, segments);

final And filter = new And(
        new And(new IsEqualTo("key1", "value1"), new IsEqualTo("key2", "10")),
        new Not(new Or(new IsIn("key3", asList("1", "2")), new IsNotEqualTo("key4", "value4"))));

TextSegment segmentToSearch = TextSegment.from(randomUUID());
Embedding embeddingToSearch =
        embeddingModel.embed(segmentToSearch.text()).content();
final EmbeddingSearchRequest requestWithFilter = EmbeddingSearchRequest.builder()
        .maxResults(5)
        .minScore(0.0)
        .filter(filter)
        .queryEmbedding(embeddingToSearch)
        .build();
final EmbeddingSearchResult<TextSegment> searchWithFilter = embeddingStore.search(requestWithFilter);
final List<EmbeddingMatch<TextSegment>> matchesWithFilter = searchWithFilter.matches();

final EmbeddingSearchRequest requestWithoutFilter = EmbeddingSearchRequest.builder()
        .maxResults(5)
        .minScore(0.0)
        .queryEmbedding(embeddingToSearch)
        .build();
final EmbeddingSearchResult<TextSegment> searchWithoutFilter = embeddingStore.search(requestWithoutFilter);
final List<EmbeddingMatch<TextSegment>> matchesWithoutFilter = searchWithoutFilter.matches();
```

要执行后续查询以读取或写入嵌入搜索检索到的数据，我们可以利用节点的 `embeddingId`。
例如：
```java
// ... Neo4jEmbeddingStore instance creation ...
// ... add embeddings.... 

final List<EmbeddingMatch<TextSegment>> results = embeddingStore.search(/*dev.langchain4j.store.embedding.EmbeddingSearchRequest instance*/)
        .matches();

// retrieve the ids to execute the follow-up
List<String> nodeIds = results.stream().map(dev.langchain4j.store.embedding.EmbeddingMatch:embeddingId).toList();

String cypher = """
        MATCH (d:Document)
        WHERE d.id IN $ids
        // -- here the follow-up query, for example
        WITH (d)-[:CONNECTED_TO]->(o:OtherLabel) 
        RETURN o.id
    """;

// run the follow-up query
Map<String, Object> params = Map.of("ids", nodeIds);
final List<Record> list = session.run(cypher, params).list();
```

#### Spring Boot Starter

要创建 **Spring Boot starter**，Neo4j starter 目前提供以下 `application.properties`：
```properties

# the builder.dimension(dimension) method
langchain4j.community.neo4j.dimension=<dimension>
# the builder.withBasicAuth(uri, username, password) method
langchain4j.community.neo4j.auth.uri=<boltURI>
langchain4j.community.neo4j.auth.user=<username>
langchain4j.community.neo4j.auth.password=<password>
# the builder.label(label) method
langchain4j.community.neo4j.label=<label>
# the builder.indexName(indexName) method
langchain4j.community.neo4j.indexName=<indexName>
# the builder.metadataPrefix(metadataPrefix) method
langchain4j.community.neo4j.metadataPrefix=<metadataPrefix>
# the builder.embeddingProperty(embeddingProperty) method
langchain4j.community.neo4j.embeddingProperty=<embeddingProperty>
# the builder.idProperty(idProperty) method
langchain4j.community.neo4j.idProperty=<idProperty>
# the builder.textProperty(textProperty) method
langchain4j.community.neo4j.textProperty=<textProperty>
# the builder.databaseName(databaseName) method
langchain4j.community.neo4j.databaseName=<databaseName>
# the builder.retrievalQuery(retrievalQuery) method
langchain4j.community.neo4j.retrievalQuery=<retrievalQuery>
# the builder.awaitIndexTimeout(awaitIndexTimeout) method
langchain4j.community.neo4j.awaitIndexTimeout=<awaitIndexTimeout>
```
配置 Starter 后，我们可以创建如下简单的 Spring Boot 项目：
```java
@SpringBootApplication
public class SpringBootExample {

    public static void main(String[] args) {
        SpringApplication.run(SpringBootExample.class, args);
    }

    @Bean
    public AllMiniLmL6V2EmbeddingModel embeddingModel() {
        return new AllMiniLmL6V2EmbeddingModel();
    }
    
}

@RestController
@RequestMapping("/api/embeddings")
public class EmbeddingController {

    private final EmbeddingStore<TextSegment> store;
    private final EmbeddingModel model;

    public EmbeddingController(EmbeddingStore<TextSegment> store, EmbeddingModel model) {
        this.store = store;
        this.model = model;
    }

    // add embeddings
    @PostMapping("/add")
    public String add(@RequestBody String text) {
        TextSegment segment = TextSegment.from(text);
        Embedding embedding = model.embed(text).content();
        return store.add(embedding, segment);
    }

    // search embeddings
    @PostMapping("/search")
    public List<String> search(@RequestBody String query) {
        Embedding queryEmbedding = model.embed(query).content();
        EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
                .queryEmbedding(queryEmbedding)
                .maxResults(5)
                .build();
        return store.search(request).matches()
                .stream()
                .map(i -> i.embedded().text()).toList();
    }
}
```
我们定义了可以轻松调用的 API，如下所示：
```shell
# to create a new embedding 
# and store it with a label "Spring Boot"
curl -X POST localhost:8083/api/embeddings/add -H "Content-Type: text/plain" -d "embeddingTest"

# to search the first 5 embeddings
curl -X POST localhost:8083/api/embeddings/search -H "Content-Type: text/plain" -d "querySearchTest"
```


### Neo4jText2CypherRetriever

以下是创建 `Neo4jText2CypherRetriever` 实例的方法：

```java
Neo4jText2CypherRetriever retriever = Neo4jText2CypherRetriever.builder().<builderParameters>.build();
````

以下是完整的构建器列表：

| 键 | 默认值     | 描述 |
| ---------- |-------------------| ---------- |
| `graph`    | *必填*        | 见下文  |
| `chatModel` | *必填*        | 用于从自然语言问题创建 Cypher 查询的 [ChatModel](https://github.com/langchain4j/langchain4j/blob/main/langchain4j-core/src/main/java/dev/langchain4j/model/chat/ChatModel.java) 实现 |
| `prompt`   | 见下方示例 | 将与 chatModel 一起使用的提示词 |
| `examples` | 空字符串      | 用于丰富并改进结果的附加示例 |
| `maxRetries` | 3                 | 如果 Cypher 查询生成失败或返回空结果，则额外重试生成                                                                                                                                           |

要连接到 Neo4j，我们需要以如下方式利用 `Neo4jGraph` 类：

```java
// Neo4j Java Driver connection instance
Driver driver = GraphDatabase.driver("<Bolt URL>", AuthTokens.basic("<username>", "<password>"));

Neo4jGraph neo4jGraph = Neo4jGraph.builder()
    .driver(driver)
    .build();
```

或者像 `Neo4jEmbeddingStore` 一样使用 `withBasicAuth`：

```java
Neo4jGraph neo4jGraph = Neo4jGraph.builder()
    .withBasicAuth("<Bolt URL>", "<username>", "<password>")
    .build();
```

然后将其传递给构建器：

```java
Neo4jGraph neo4jGraph = /* Neo4jGraph instance */;

// ChatModel instance, e.g. OpenAiChatModel
ChatModel chatModel = OpenAiChatModel.builder()
        .apiKey(OPENAI_API_KEY)
        .modelName(GPT_4_O_MINI)
        .build();

// Neo4jText2CypherRetriever instance
Neo4jText2CypherRetriever retriever = Neo4jText2CypherRetriever.builder()
        .graph(neo4jGraph)
        .chatModel(chatModel)
        .build();
```

你可以通过调整诸如 `sample`（在上下文提示词中返回多少个示例路径）和 `maxRels`（每个节点标签最多读取多少个关系）等参数，进一步自定义 `Neo4jGraph` 的行为。
这些参数是可选的（默认值分别为 `1000` 和 `100`），如果你希望使用默认行为，可以省略它们。
这些参数在更大的图中特别有用，可用于控制提示词的大小和复杂度。

此外，你可以使用 `Neo4jGraph` 返回实体架构，
即描述图结构的模式、节点属性和关系属性列表：

```java
final Neo4jGraph.StructuredSchema structuredSchema = graph.getStructuredSchema();

List<String> patterns = structuredSchema.patterns();
List<String> nodesProperties = structuredSchema.nodesProperties();
List<String> relationshipsProperties = structuredSchema.relationshipsProperties();

/*
Example outputs:
`patterns`: [(:Person)-[:WROTE]->(:Book)]
`nodesProperties`: [:Book {title: STRING}, :Person {name: STRING}]
`relationshipsProperties`: [:WROTE {year: 1986}]
*/
```

### 使用 `sample` 和 `maxRels` 的示例

```java
Neo4jGraph neo4jGraph = Neo4jGraph.builder()
    .driver(driver)
    .sample(3L) // Sample up to 3 example paths from the graph schema
    .maxRels(8L) // Explore a maximum of 8 relationships from the start node
    .build();

Neo4jText2CypherRetriever retriever = Neo4jText2CypherRetriever.builder()
    .graph(neo4jGraph)
    .chatModel(chatModel)
    .build();
```


以下是一个基本示例：
```java

// create dataset, for example:
// CREATE (book:Book {title: 'Dune'})<-[:WROTE {when: date('1999')}]-(author:Person {name: 'Frank Herbert'})");


// create a Neo4jGraph instance
Neo4jGraph neo4jGraph = Neo4jGraph.builder()
        .driver(/*<Neo4j Driver instance>*/)
        .build();

// create a Neo4jText2CypherRetriever instance
Neo4jText2CypherRetriever retriever = Neo4jText2CypherRetriever.builder()
        .graph(neo4jGraph)
        .chatModel(chatModel)
        .build();

Query query = new Query("Who is the author of the book 'Dune'?");

// retrieve result
List<Content> contents = retriever.retrieve(query);

System.out.println(contents.get(0).textSegment().text());
// example output: "Frank Herbert"
```
以上代码将使用以下提示词字符串执行一次聊天请求：
```text
Task:Generate Cypher statement to query a graph database.
Instructions
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.
Schema:

Node properties are the following:
:Book {title: STRING}
:Person {name: STRING}

Relationship properties are the following:
:WROTE {when: DATE}

The relationships are the following:
(:Person)-[:WROTE]->(:Book)

Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.
The question is: {{question}}
```
其中 `question` 是 "Who is the author of the book 'Dune'?"，
而 `schema` 由 apoc.meta.data 过程处理，以检索并字符串化当前的 Neo4j 架构。
在这种情况下是
```text
Node properties are the following:
:Book {title: STRING}
:Person {name: STRING}

Relationship properties are the following:
:WROTE {when: DATE}

The relationships are the following:
(:Person)-[:WROTE]->(:Book)
----

We can also change the default prompt if needed:
[source,java]
----
Neo4jGraph neo4jGraph = /* Neo4jGraph instance */

Neo4jText2CypherRetriever.builder()
  .neo4jGraph(neo4jGraph)
  .promptTemplate("<custom prompt>")
  .build();
```


要创建没有任何重试逻辑的检索器，将 `maxRetries` 设置为 `0`：

```java
Neo4jText2CypherRetriever retriever = Neo4jText2CypherRetriever.builder()
    .graph(graph)
    .chatModel(chatModel)
    .maxRetries(0) // disables retry logic
    .build();
```
当你希望行为确定、并且不想让检索器在 Cypher 生成失败时尝试回退查询时，此配置非常有用。通常在性能至关重要或失败处理由外部管理的场景中推荐使用此配置。


还可以使用 `fromLLM("<question>")` 方法，利用 `chatModel` 和以下提示词，基于检索到的上下文和 Cypher 查询生成自然语言答案。其中 `{{context}}` 是从 `Neo4jGraph` 检索到的架构，`{{cypher}}` 是由 text-to-Cypher 生成的 Cypher 查询，`{{question}}` 是传递给 `fromLLM()` 的参数。
```
Based on the following context and the generated Cypher,
write an answer in natural language to the provided user's question:
Context: {{context}}
Generated Cypher: {{cypher}}
Question: {{question}}
Cypher query:
````

用法示例：

```java
Neo4jText2CypherRetriever neo4jContentRetriever = Neo4jText2CypherRetriever.builder()
        .graph(graph)
        .chatModel(OPEN_AI_CHAT_MODEL)
        .build();

Query query = new Query("Who is the author of the book 'Dune'?");

String response = neo4jContentRetriever.fromLLM(query);
// example output: the author of the book 'Dune' is Frank Herbert

````



### KnowledgeGraphWriter

`KnowledgeGraphWriter` 是一个用于将结构化知识图谱数据写入 Neo4j 的工具类。它专为处理 `LLMGraphTransformer` 产生的数据而设计，后者从非结构化文档中提取节点和关系。

对于文本数据已被转换为图结构、并需要高效存储在 Neo4j 数据库中的场景（包括可选的文档来源信息），此写入器特别有用。

#### 特性

- 从 `GraphDocument` 实例中存储节点和关系到 Neo4j。
- 支持可选地存储源文档的元数据和内容。
- 为实体自动创建唯一约束。
- 允许自定义标签、关系类型、ID 和文本属性。

以下是创建 `KnowledgeGraphWriter` 实例的方法：

```java
KnowledgeGraphWriter writer = KnowledgeGraphWriter.builder().<builderParameters>.build();
```

#### 以下是完整的构建器列表：

| 构建器方法           | 描述                                                | 默认值    |
| ------------------------ | ---------------------------------------------------------- | ---------------- |
| `graph(Neo4jGraph)`      | 设置 Neo4j 图连接。（必填）                | -                |
| `label(String)`          | 设置节点的实体标签。                           | `__Entity__`     |
| `relType(String)`        | 设置实体与文档之间的关系类型。 | `HAS_ENTITY`     |
| `idProperty(String)`     | 设置用作唯一标识符的属性名称。      | `id`             |
| `textProperty(String)`   | 设置用于存储文档文本的属性名称。     | `text`           |
| `constraintName(String)` | 设置在 Neo4j 中唯一约束的名称。       | `knowledge_cons` |



```java
Neo4jGraph graph = Neo4jGraph.builder()
    .withBasicAuth("bolt://localhost:7687", "neo4j", "password")
    .build();

KnowledgeGraphWriter writer = KnowledgeGraphWriter.builder()
    .graph(graph)
    .label("Entity")
    .relType("MENTIONS")
    .idProperty("id")
    .textProperty("text")
    .build();

List<GraphDocument> graphDocuments = ... // obtained from LLMGraphTransformer
writer.addGraphDocuments(graphDocuments, true); // set to true to include document source
````


### Neo4jEmbeddingStoreIngestor

`Neo4jEmbeddingStoreIngestor` 是一个专门的摄入器类，旨在将嵌入及相关数据存储在 Neo4j 图数据库中。它为嵌入存储、查询模板和提示词提供了可配置的选项，以支持各种知识摄入和检索工作流。

以下是创建 `Neo4jEmbeddingStoreIngestor` 实例的方法：

```java
Neo4jEmbeddingStoreIngestor ingestor = Neo4jEmbeddingStoreIngestor.builder()
    .<builderParameters>
    .build();
```

其中 `<builderParameters>` 必须包含 `driver` 和 `dimension`，此外还可以进行可选的自定义。

以下是完整的构建器列表：

| 键                   | 默认值             | 描述                                                                                                                    |
| --------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `driver`              | *必填*                | [Neo4j Java Driver 实例](https://neo4j.com/docs/api/java-driver/current/org.neo4j.driver/org/neo4j/driver/Driver.html) |
| `retrievalQuery`      | 见类默认值         | 嵌入查找期间用于检索实体的 Cypher 查询                                                                 |
| `entityCreationQuery` | 见类默认值         | 用于创建带嵌入的实体的 Cypher 查询                                                                             |
| `label`               | `"Child"`                 | 在 Neo4j 中嵌入节点使用的节点标签                                                                                 |
| `indexName`           | `"child_embedding_index"` | 嵌入节点索引的名称                                                                                          |
| `dimension`           | `384`                     | 嵌入向量的维度                                                                                        |
| `systemPrompt`        | 见类默认值         | 用于 LLM 驱动任务的系统提示词                                                                                             |
| `userPrompt`          | 见类默认值         | 用于 LLM 驱动任务的用户提示词                                                                                               |


**使用必需参数的基本用法：**

```java
Neo4jEmbeddingStoreIngestor ingestor = Neo4jEmbeddingStoreIngestor.builder()
    .driver(neo4jDriver)
    .dimension(384)
    .build();
```

**自定义检索和创建查询：**

```java
Neo4jEmbeddingStoreIngestor ingestor = Neo4jEmbeddingStoreIngestor.builder()
    .driver(neo4jDriver)
    .dimension(384)
    .retrievalQuery("MATCH (doc:Document) WHERE doc.id = $id RETURN doc")
    .entityCreationQuery("CREATE (doc:Document {id: $id, embedding: $embedding})")
    .label("Document")
    .indexName("document_embedding_index")
    .build();
```

**使用自定义系统提示词和用户提示词：**

```java
Neo4jEmbeddingStoreIngestor ingestor = Neo4jEmbeddingStoreIngestor.builder()
    .driver(neo4jDriver)
    .dimension(384)
    .systemPrompt("You are an expert knowledge base ingestor.")
    .userPrompt("Please ingest the following content:")
    .build();
```


### 面向特定使用场景的 Neo4j Ingestor

以下类扩展了 `Neo4jEmbeddingStoreIngestor`，提供针对特定 [GraphRAG](https://graphrag.com/reference/graphrag) 模式的预配置摄入逻辑。每个摄入器都附带预定义的 Cypher 查询和提示词模板，同时仍允许构建器级别的自定义。
所有摄入器都继承自 `Neo4jEmbeddingStoreIngestor` 的完整构建器 API。

#### SummaryGraphIngestor


要实现[全局社区摘要检索器概念](https://graphrag.com/reference/graphrag/global-community-summary-retriever/)
此摄入器使用摘要提示词从图中提取并存储文档的简洁摘要，并将其存储为标记为 `"Summary"`（默认）的节点，链接到原始文档。

用法示例：
```java
SummaryGraphIngestor ingestor = SummaryGraphIngestor.builder()
        .driver(driver)
        .embeddingModel(embeddingModel)
        .questionModel(chatModel)
        .documentSplitter(splitter)
        .build();
````

与 `Neo4jEmbeddingStoreIngestor` 不同，它具有以下默认值：

- `query`: `"CREATE (:SummaryChunk $metadata)"`
- `systemPrompt`:
```text
You are generating concise and accurate summaries based on the information found in the text.
```

- `userPrompt`:
```text
Generate a summary of the following input:
{{input}}

Summary:
```

- `embeddingStore`:
```java
private static final String DEFAULT_RETRIEVAL = """
        MATCH (node)<-[:HAS_SUMMARY]-(parent)
        WITH parent, max(score) AS score, node // deduplicate parents
        RETURN parent.text AS text, score, properties(node) AS metadata
        ORDER BY score DESC
        LIMIT $maxResults""";

private static final String DEFAULT_PARENT_QUERY = """
        UNWIND $rows AS row
        MATCH (p:SummaryChunk {parentId: $parentId})
        CREATE (p)-[:HAS_SUMMARY]->(u:%1$s {%2$s: row.%2$s})
        SET u += row.%3$s
        WITH row, u
        CALL db.create.setNodeVectorProperty(u, $embeddingProperty, row.%4$s)
        RETURN count(*)""";

EmbeddingStore defaultEmbeddingStore = Neo4jEmbeddingStore.builder()
    .driver(driver)
    .retrievalQuery(DEFAULT_RETRIEVAL)
    .entityCreationQuery(DEFAULT_PARENT_QUERY)
    .label("Summary")
    .indexName("summary_embedding_index")
    .dimension(384)
    .build();
```

#### HypotheticalQuestionGraphIngestor

要通过生成并嵌入从内容块中推导出的假设问题来实现[假设问题检索器概念](https://graphrag.com/reference/graphrag/hypothetical-question-retriever/)。这可以提高语义搜索的准确性，尤其是对于间接或抽象的用户问题。
当查询与文档措辞不直接匹配时，它能增强检索效果。


用法示例：
```java
HypotheticalQuestionGraphIngestor ingestor = HypotheticalQuestionGraphIngestor.builder()
        .embeddingModel(embeddingModel)
        .driver(driver)
        .documentSplitter(splitter)
        .questionModel(chatModel)
        .embeddingStore(embeddingStore)
        .build();
```

与 `Neo4jEmbeddingStoreIngestor` 不同，它具有以下默认值：

- `query`: `"CREATE (:QuestionChunk $metadata)"`
- `systemPrompt`:
```text
You are generating hypothetical questions based on the information found in the text.
Make sure to provide full context in the generated questions.
```

- `userPrompt`:
```text
Use the given format to generate hypothetical questions from the following input:
{{input}}

Hypothetical questions:
```

- `embeddingStore`:
```java
private static final String DEFAULT_RETRIEVAL = """
        MATCH (node)<-[:HAS_QUESTION]-(parent)
        WITH parent, max(score) AS score, node // deduplicate parents
        RETURN parent.text AS text, score, properties(node) AS metadata
        ORDER BY score DESC
        LIMIT $maxResults""";

private static final String DEFAULT_PARENT_QUERY = """
        UNWIND $rows AS question
        MATCH (p:QuestionChunk {parentId: $parentId})
        WITH p, question
        CREATE (q:%1$s {%2$s: question.%2$s})
        SET q += question.%3$s
        MERGE (q)<-[:HAS_QUESTION]-(p)
        WITH q, question
        CALL db.create.setNodeVectorProperty(q, $embeddingProperty, question.%4$s)
        RETURN count(*)""";

EmbeddingStore defaultEmbeddingStore = Neo4jEmbeddingStore.builder()
    .driver(driver)
    .retrievalQuery(DEFAULT_RETRIEVAL_QUERY)
    .entityCreationQuery(DEFAULT_PARENT_QUERY)
    .label("Child")
    .indexName("child_embedding_index")
    .dimension(384)
    .build();
```

#### ParentChildGraphIngestor

要实现[父子检索器概念](https://graphrag.com/reference/graphrag/parent-child-retriever/)。
当语义搜索在子节点上执行而结果锚定到父文档时，它很有用。
此摄入器存储带嵌入的子块，默认使用 `:HAS_CHILD` 关系将它们链接到父节点。在引用更广泛的文档上下文的同时检索相关片段时非常理想。


```java
ParentChildGraphIngestor ingestor = ParentChildGraphIngestor.builder()
        .embeddingModel(embeddingModel)
        .driver(driver)
        .documentSplitter(parentSplitter)
        .documentChildSplitter(childSplitter)
        .build();
```

与 `Neo4jEmbeddingStoreIngestor` 不同，它具有以下默认值：

- `query`: `"CREATE (:ParentChunk $metadata)"`

- `embeddingStore`:
```java
private static final String DEFAULT_RETRIEVAL = """
        MATCH (node)<-[:HAS_CHILD]-(parent)
        WITH parent, collect(node.text) AS chunks, max(score) AS score
        RETURN parent.text + reduce(r = "", c in chunks | r + "\n\n" + c) AS text,
               score,
               properties(parent) AS metadata
        ORDER BY score DESC
        LIMIT $maxResults""";

private static final String DEFAULT_PARENT_QUERY = """
        UNWIND $rows AS row
        MATCH (p:ParentChunk {parentId: $parentId})
        CREATE (p)-[:HAS_CHILD]->(u:%1$s {%2$s: row.%2$s})
        SET u += row.%3$s
        WITH row, u
        CALL db.create.setNodeVectorProperty(u, $embeddingProperty, row.%4$s)
        RETURN count(*)""";

EmbeddingStore defaultEmbeddingStore = Neo4jEmbeddingStore.builder()
        .driver(driver)
        .retrievalQuery(DEFAULT_RETRIEVAL)
        .entityCreationQuery(DEFAULT_PARENT_QUERY)
        .label("Child")
        .indexName("child_embedding_index")
        .dimension(384)
        .build();
```





### Neo4jChatMemoryStore

`Neo4jChatMemoryStore` 是一种专门的聊天记忆实现，在 Neo4j 图数据库中存储和检索对话消息。它支持使用 Neo4j 节点和关系高效地查询和持久化，从而管理聊天历史。

以下是创建 `Neo4jChatMemoryStore` 实例的方法：

```java
Neo4jChatMemoryStore chatMemoryStore = Neo4jChatMemoryStore.builder()
    .<builderParameters>
    .build();
```

其中 `<builderParameters>` 必须包含 `driver`，以及关于标签和节点属性名称的可选属性。

以下是完整的构建器列表：

| 键                      | 默认值      | 描述                                                                                                                    |
| ------------------------ | ------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| `driver`                 | *必填*         | [Neo4j Java Driver 实例](https://neo4j.com/docs/api/java-driver/current/org.neo4j.driver/org/neo4j/driver/Driver.html) |
| `label`                  | `"ChatMessage"`    | 在 Neo4j 中聊天消息节点使用的标签                                                                                 |
| `idProperty`             | `"id"`             | 消息 ID 的属性名称                                                                                           |
| `conversationIdProperty` | `"conversationId"` | 用于标识对话的属性名称                                                                                 |
| `timestampProperty`      | `"timestamp"`      | 消息时间戳的属性名称                                                                                       |

#### 示例

**使用必需参数的基本用法：**

```java
Neo4jChatMemoryStore chatMemoryStore = Neo4jChatMemoryStore.builder()
    .driver(neo4jDriver)
    .build();
```

**自定义节点标签和属性：**

```java
Neo4jChatMemoryStore chatMemoryStore = Neo4jChatMemoryStore.builder()
    .driver(neo4jDriver)
    .label("Message")
    .idProperty("messageId")
    .conversationIdProperty("convId")
    .timestampProperty("timeSent")
    .build();
```












### 简单流程示例
以下是 `Neo4jEmbeddingStore` 和 `Neo4jText2CypherRetriever` API 的几个使用流程示例。
- `Neo4jEmbeddingStore`:
```java
private static final EmbeddingModel embeddingModel = new AllMiniLmL6V2EmbeddingModel();

public static void minimalEmbedding() {
    try (Neo4jContainer<?> neo4j = new Neo4jContainer<>("neo4j:5.26")) {
        neo4j.start();

        EmbeddingStore<TextSegment> minimalEmbedding = Neo4jEmbeddingStore.builder()
                .withBasicAuth(neo4j.getBoltUrl(), "neo4j", neo4j.getAdminPassword())
                .dimension(384)
                .build();


        TextSegment segment1 = TextSegment.from("I like football.", Metadata.from("test-key-1", "test-value-1"));
        Embedding embedding1 = embeddingModel.embed(segment1).content();

        TextSegment segment2 = TextSegment.from("The weather is good today.", Metadata.from("test-key-2", "test-value-2"));
        Embedding embedding2 = embeddingModel.embed(segment2).content();

        TextSegment segment3 = TextSegment.from("I like basketball.", Metadata.from("test-key-3", "test-value-3"));
        Embedding embedding3 = embeddingModel.embed(segment3).content();
        minimalEmbedding.addAll(
                List.of(embedding1, embedding2, embedding3),
                List.of(segment1, segment2, segment3)
        );

        Embedding queryEmbedding = embeddingModel.embed("What are your favourite sports?").content();
        final EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
                .queryEmbedding(queryEmbedding)
                .maxResults(2)
                .minScore(0.15)
                .build();
        List<EmbeddingMatch<TextSegment>> relevant = minimalEmbedding.search(request).matches();
        relevant.forEach(match -> {
            System.out.println(match.score()); // 0.8144289255142212
            System.out.println(match.embedded().text()); // I like football. || I like basketball.
        });
    }
}

public static void customEmbeddingStore() {
    try (Neo4jContainer<?> neo4j = new Neo4jContainer<>("neo4j:5.26")) {
        neo4j.start();
        
        Neo4jEmbeddingStore customEmbeddingStore = Neo4jEmbeddingStore.builder()
                .withBasicAuth(neo4j.getBoltUrl(), "neo4j", neo4j.getAdminPassword())
                .dimension(384)
                .indexName("customidx")
                .label("CustomLabel")
                .embeddingProperty("customProp")
                .idProperty("customId")
                .textProperty("customText")
                .build();
        
        TextSegment segment1 = TextSegment.from("I like football.");
        Embedding embedding1 = embeddingModel.embed(segment1).content();
        customEmbeddingStore.add(embedding1, segment1);

        TextSegment segment2 = TextSegment.from("The weather is good today.");
        Embedding embedding2 = embeddingModel.embed(segment2).content();
        customEmbeddingStore.add(embedding2, segment2);

        Embedding queryEmbedding = embeddingModel.embed("What is your favourite sport?").content();
        final EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
                .queryEmbedding(queryEmbedding)
                .maxResults(1)
                .build();
        List<EmbeddingMatch<TextSegment>> relevant = customEmbeddingStore.search(request).matches();
        EmbeddingMatch<TextSegment> embeddingMatch = relevant.get(0);

        System.out.println(embeddingMatch.score()); // 0.8144289255142212
        System.out.println(embeddingMatch.embedded().text()); // I like football.
    }
}
```
- `Neo4jText2CypherRetriever`:
```java
    private final ChatModel chatModel;

    public void Neo4jText2CypherRetriever() {
        try (
                Neo4jContainer<?> neo4jContainer = new Neo4jContainer<>("neo4j:5.16.0")
                                                        .withoutAuthentication()
                                                        .withLabsPlugins("apoc")
        ) {
            neo4jContainer.start();
            try (Driver driver = GraphDatabase.driver(neo4jContainer.getBoltUrl(), AuthTokens.none())) {
                try (Neo4jGraph graph = Neo4jGraph.builder().driver(driver).build()) {
                    try (Session session = driver.session()) {
                        session.run("CREATE (book:Book {title: 'Dune'})<-[:WROTE]-(author:Person {name: 'Frank Herbert'})");
                    }
                    graph.refreshSchema();
                    
                    Neo4jText2CypherRetriever retriever = Neo4jText2CypherRetriever.builder()
                            .graph(graph)
                            .chatModel(chatModel)
                            .build();

                    Query query = new Query("Who is the author of the book 'Dune'?");

                    List<Content> contents = retriever.retrieve(query);

                    System.out.println(contents.get(0).textSegment().text()); // "Frank Herbert"
                }
            }
        }
    }
```
[示例源码](https://github.com/langchain4j/langchain4j-examples/tree/main/neo4j-example/src/main/java)