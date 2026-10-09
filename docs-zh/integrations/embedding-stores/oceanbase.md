# OceanBase

OceanBase 向量存储与 [OceanBase](https://www.oceanbase.com/) 数据库集成，提供向量相似性搜索和混合搜索能力。

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-oceanbase</artifactId>
    <version>${latest version here}</version>
</dependency>
```

注意：这是一个社区集成模块。你可能需要在项目配置中添加 langchain4j-community 仓库。

## API

- `OceanBaseEmbeddingStore`

## 要求

- OceanBase 数据库实例（4.3.5 或更高版本）
- Java >= 17

## 功能

- 带元数据（JSON 格式）存储嵌入
- 支持余弦、L2 或内积距离的向量相似性搜索
- **混合搜索**：结合向量相似性搜索和全文搜索（RRF 算法）
- 按元数据字段和表列过滤搜索结果
- 自动创建表和向量索引
- 可自定义字段名和距离度量

## 用法

### 基本示例

```java
import dev.langchain4j.data.document.Metadata;
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.embedding.onnx.allminilml6v2q.AllMiniLmL6V2QuantizedEmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingSearchRequest;
import dev.langchain4j.store.embedding.EmbeddingSearchResult;
import dev.langchain4j.store.embedding.oceanbase.OceanBaseEmbeddingStore;

// Initialize embedding model
EmbeddingModel embeddingModel = new AllMiniLmL6V2QuantizedEmbeddingModel();

// Create embedding store
OceanBaseEmbeddingStore embeddingStore = OceanBaseEmbeddingStore.builder()
    .url("jdbc:oceanbase://127.0.0.1:2881/test")
    .user("root@test")
    .password("password")
    .tableName("embeddings")
    .dimension(384)
    .build();

// Add document with metadata
String id = embeddingStore.add(
    embeddingModel.embed("Java is a programming language").content(),
    TextSegment.from("Java is a programming language", 
        Metadata.from("category", "programming").put("language", "Java"))
);

// Search
Embedding queryEmbedding = embeddingModel.embed("programming language").content();
EmbeddingSearchResult<TextSegment> results = embeddingStore.search(
    EmbeddingSearchRequest.builder()
        .queryEmbedding(queryEmbedding)
        .maxResults(10)
        .build()
);

// Process results
results.matches().forEach(match -> {
    System.out.println("Score: " + match.score());
    System.out.println("Text: " + match.embedded().text());
    System.out.println("Metadata: " + match.embedded().metadata());
});
```

### 高级配置

```java
OceanBaseEmbeddingStore embeddingStore = OceanBaseEmbeddingStore.builder()
    .url("jdbc:oceanbase://127.0.0.1:2881/test")
    .user("root@test")
    .password("password")
    .tableName("embeddings")
    .dimension(384)
    .metricType("cosine")  // Options: "cosine", "l2", "ip"
    .retrieveEmbeddingsOnSearch(true)
    .idFieldName("id_field")
    .textFieldName("text_field")
    .metadataFieldName("metadata_field")
    .vectorFieldName("vector_field")
    .build();
```

## 距离度量

OceanBase 向量存储支持三种距离度量。距离值会被自动转换为 [0, 1] 范围内的相关性得分，其中 1 表示最相关的匹配。

### 余弦距离（默认）- `"cosine"`

**最适合：** 文本嵌入、语义相似性搜索

**工作原理：**
- OceanBase 的 `cosine_distance` 返回 [0, 2] 范围内的值
  - `0` = 相同向量（方向相同）
  - `1` = 正交向量（垂直）
  - `2` = 相反向量（方向完全相反）
- 转换为相关性得分：`score = (2 - distance) / 2`
- 结果与向量的模长无关

```java
.metricType("cosine")  // Default, recommended for text embeddings
```

### L2 距离（欧几里得）- `"l2"` 或 `"euclidean"`

**最适合：** 方向和模长都重要的场景

**工作原理：**
- 测量向量之间的直线距离
- 范围：[0, ∞)
- 转换为相关性得分：`score = 1 / (1 + distance)`

```java
.metricType("l2")  // or "euclidean"
```

### 内积 - `"inner_product"` 或 `"ip"`

**最适合：** 归一化嵌入、对性能要求高的应用

**工作原理：**
- 测量向量的点积
- 对于归一化向量，范围是 [-1, 1]
- 转换为相关性得分：`score = (inner_product + 1) / 2`

```java
.metricType("inner_product")  // or "ip"
```

**参考：** [OceanBase 向量距离函数](https://www.oceanbase.com/docs/common-oceanbase-database-cn-1000000004475471)

## 过滤

OceanBase 向量存储支持按元数据字段和表列过滤搜索结果。

### 按元数据字段过滤

```java
import dev.langchain4j.store.embedding.filter.MetadataFilterBuilder;
import static dev.langchain4j.store.embedding.filter.MetadataFilterBuilder.metadataKey;

// Filter by single metadata field
Filter filter = metadataKey("category").isEqualTo("programming");

// Filter with multiple conditions
Filter filter = new And(
    metadataKey("category").isEqualTo("programming"),
    metadataKey("language").isEqualTo("Java")
);

// Filter with IN operator
Filter filter = metadataKey("language").isIn("Java", "Python", "C++");

// Search with filter
EmbeddingSearchResult<TextSegment> results = embeddingStore.search(
    EmbeddingSearchRequest.builder()
        .queryEmbedding(queryEmbedding)
        .filter(filter)
        .maxResults(10)
        .build()
);
```

### 按表列过滤

你也可以直接按表列过滤（id, text, metadata, vector）：

```java
import dev.langchain4j.store.embedding.filter.comparison.IsIn;
import dev.langchain4j.store.embedding.filter.comparison.ContainsString;
import dev.langchain4j.store.embedding.filter.comparison.IsEqualTo;

// Filter by ID field
Filter filter = new IsIn("id", List.of("id1", "id2", "id3"));

// Filter by text field (contains)
Filter textFilter = new ContainsString("text", "programming");

// Filter by exact text match
Filter exactTextFilter = new IsEqualTo("text", "Java programming");
```

**注意**：按表列过滤时，请使用 `FieldDefinition` 中定义的实际字段名。映射器会自动识别常见的别名：
- `id` → id 字段
- `text` 或 `document` → text 字段  
- `metadata` → metadata 字段
- `vector` 或 `embedding` → vector 字段

### 支持的过滤操作

- `isEqualTo`：相等比较
- `isNotEqualTo`：不相等比较
- `isGreaterThan`：大于比较
- `isGreaterThanOrEqualTo`：大于等于比较
- `isLessThan`：小于比较
- `isLessThanOrEqualTo`：小于等于比较
- `isIn`：IN 运算符（多个值）
- `isNotIn`：NOT IN 运算符
- `containsString`：LIKE 运算符（模式匹配）
- `And`：逻辑与
- `Or`：逻辑或
- `Not`：逻辑非

## 混合搜索

混合搜索结合向量相似性搜索和全文搜索，提供更好的搜索结果。启用后，它会自动在 text 字段上创建全文索引，并使用**倒数排名融合（RRF）**算法合并结果。

### 启用混合搜索

```java
OceanBaseEmbeddingStore embeddingStore = OceanBaseEmbeddingStore.builder()
    .url("jdbc:oceanbase://127.0.0.1:2881/test")
    .user("root@test")
    .password("password")
    .tableName("embeddings")
    .dimension(384)
    .enableHybridSearch(true)  // Enable hybrid search
    .build();
```

### 执行混合搜索

```java
// Perform hybrid search by providing both query embedding and query text
EmbeddingSearchResult<TextSegment> results = embeddingStore.search(
    EmbeddingSearchRequest.builder()
        .queryEmbedding(queryEmbedding)  // Vector embedding for similarity search
        .query("search text")            // Text query for fulltext search
        .maxResults(10)
        .build()
);
```

### 混合搜索如何工作

1. **向量搜索**：使用查询嵌入执行相似性搜索
2. **全文搜索**：在 text 字段上使用 `MATCH AGAINST` 执行全文搜索
3. **结果融合**：使用 RRF（倒数排名融合）算法合并结果
   - 公式：`score = Σ(1 / (k + rank))`，其中 k=60
   - 两个搜索的每个结果都会根据其排名对最终得分做出贡献
   - 结果经过归一化后按 RRF 综合得分排序

**优势：**
- 更好的召回率：可以通过语义相似性或精确关键词找到文档
- 更高的精确率：RRF 有效地平衡了两种搜索方式
- 对精确关键词匹配的处理优于单独的向量搜索

## 实现细节

### 得分计算

向量存储直接在 SQL 查询中计算相关性得分：
- **余弦**：`score = (2 - cosine_distance) / 2`
- **L2/欧几里得**：`score = 1 / (1 + distance)`
- **内积**：`score = (inner_product + 1) / 2`

得分返回在 [0, 1] 范围内，其中 1 表示最相关的匹配。

### 元数据处理

- 元数据以 JSON 格式存储在数据库中
- 大的 `Long` 值（> 2^53-1）会自动序列化为字符串以保留精度
- 过滤同时支持直接列过滤和 JSON 元数据过滤

### 表架构

默认情况下，嵌入表具有以下列：

| 名称 | 类型 | 描述 |
| ---- | ---- | ----------- |
| id | VARCHAR(36) | 主键。用于存储向量存储生成的 UUID 字符串 |
| vector | JSON | 以 JSON 数组形式存储嵌入向量 |
| text | TEXT | 存储文本片段 |
| metadata | JSON | 以 JSON 形式存储元数据 |

## 限制

- `removeAll(Filter)` 和 `removeAll()` 方法目前尚不支持。请改用 `removeAll(Collection<String> ids)`。
- 按表列过滤时，字段名不区分大小写，但必须与实际列名或已识别的别名匹配。

## 参考资料

- [OceanBase 文档](https://www.oceanbase.com/docs)
- [倒数排名融合](https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking)
- [LangChain4j 文档](https://docs.langchain4j.dev)
