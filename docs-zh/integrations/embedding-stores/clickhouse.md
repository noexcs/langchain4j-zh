# ClickHouse

[ClickHouse](https://clickhouse.com/) 是用于实时应用和分析的最快且资源效率最高的开源
数据库，它完全支持 SQL，并提供丰富的函数来帮助用户编写分析查询。最近添加的
数据结构和距离搜索函数（如 cosineDistance）以及
[近似最近邻搜索索引](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/annindexes)
使 ClickHouse 能够作为高性能、可扩展的向量数据库，使用 SQL 来存储和搜索向量。

## Maven 依赖

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-clickhouse</artifactId>
    <version>${latest version here}</version>
</dependency>
```

## API

LangChain4j 使用 `client-v2` 作为 ClickHouse 客户端。要创建 `ClickHouseEmbeddingStore` 实例，你需要提供 `ClickHouseSettings`：

```java
// Mapping metadata key to ClickHouse data type.
Map<String, ClickHouseDataType> metadataTypeMap = new HashMap<>();

ClickHouseSettings settings = ClickHouseSettings.builder()
    .url("http://localhost:8123")
    .table("langchain4j_table")
    .username(System.getenv("USERNAME"))
    .password(System.getenv("PASSWORD"))
    .dimension(embeddingModel.dimension())
    .metadataTypeMap(metadataTypeMap)
    .build();
```

然后你可以创建向量存储：

```java
ClickHouseEmbeddingStore embeddingStore = ClickHouseEmbeddingStore.builder()
    .settings(settings)
    .build();
```

## 示例

- [ClickHouseEmbeddingStoreIT](https://github.com/langchain4j/langchain4j-community/blob/main/langchain4j-community-clickhouse/src/test/java/dev/langchain4j/community/store/embedding/clickhouse/ClickHouseEmbeddingStoreIT.java)
