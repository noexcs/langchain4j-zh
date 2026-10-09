# Google AlloyDB for PostgreSQL

[AlloyDB](https://cloud.google.com/alloydb) 是一个全托管的关系数据库服务，提供高性能、无缝集成和出色的可扩展性。AlloyDB 与 PostgreSQL 100% 兼容。扩展你的数据库应用，利用 AlloyDB 的 Langchain 集成来构建 AI 驱动的体验。

此模块实现了由 AlloyDB for PostgreSQL 数据库支持的 `EmbeddingStore`。

### Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artificatId>langchain4j-community-alloydb-pg</artificatId>
    <version>${latest version here}</version>
</dependency>
```

## AlloyDBEmbeddingStore 用法

使用向量存储来存储文本嵌入数据并执行向量搜索。可以通过配置提供的 `Builder` 创建 `AlloyDBEmbeddingStore` 实例，它需要以下内容：

- `AlloyDBEngine` 实例
- 表名
- 架构名（可选，默认："public"）
- 内容列（可选，默认："content"）
- 嵌入列（可选，默认："embedding"）
- id 列（可选，默认："langchain_id"）
- 元数据列名（可选）
- 附加元数据 json 列（可选，默认："langchain_metadata"）
- 忽略的元数据列名（可选）
- 距离策略（可选，默认：DistanceStrategy.COSINE_DISTANCE）
- 查询选项（可选）

用法示例：
```java
import dev.langchain4j.data.document.Metadata;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.onnx.allminilml6v2.AllMiniLmL6V2EmbeddingModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingMatch;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingSearchResult;
import dev.langchain4j.engine.EmbeddingStoreConfig;
import dev.langchain4j.engine.AlloyDBEngine;
import dev.langchain4j.engine.MetadataColumn;
import dev.langchain4j.store.embedding.alloydb.AlloyDBEmbeddingStore;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

AlloyDBEngine engine = new AlloyDBEngine.Builder()
    .projectId("")
    .region("")
    .cluster("")
    .instance("")
    .database("")
    .build();

AlloyDBEmbeddingStore store = new AlloyDBEmbeddingStore.Builder(engine, TABLE_NAME)
    .build();

List<String> testTexts = Arrays.asList("cat", "dog", "car", "truck");
List<Embedding> embeddings = new ArrayList<>();
List<TextSegment> textSegments = new ArrayList<>();
EmbeddingModel embeddingModel = new AllMiniLmL6V2EmbeddingModel();

for (String text : testTexts) {
    Map<String, Object> metaMap = new HashMap<>();
    metaMap.put("my_metadata", "string");
    Metadata metadata = new Metadata(metaMap);
    textSegments.add(new TextSegment(text, metadata));
    embeddings.add(MyEmbeddingModel.embed(text).content());
}
List<String> ids = store.addAll(embeddings, textSegments);
// search for "cat"
EmbeddingSearchRequest request = EmbeddingSearchRequest.builder()
        .queryEmbedding(embeddings.get(0))
        .maxResults(10)
        .minScore(0.9)
        .build();
List<EmbeddingMatch<TextSegment>> result = store.search(request).matches();
// remove "cat"
store.removeAll(singletonList(result.get(0).embeddingId()));
```