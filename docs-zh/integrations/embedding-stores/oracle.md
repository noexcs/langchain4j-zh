# Oracle
Oracle 向量存储与 Oracle Database 的 [AI Vector Search 特性](https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/overview-ai-vector-search.html) 集成。

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-oracle</artifactId>
    <version>1.22.0-beta32</version>

</dependency>
```

## API

- `OracleEmbeddingStore`
- `OracleChatMemoryStore`


## 示例

- [OracleEmbeddingStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/oracle-example/src/main/java/OracleEmbeddingStoreExample.java)

## 用法

可以通过配置构建器来创建该存储的实例。构建器
要求提供一个 DataSource 和一个嵌入表。两个向量之间的距离
使用[余弦相似度](https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/cosine-similarity.html)计算，
它衡量的是两个向量之间夹角的余弦值。

建议配置一个连接池式的 DataSource，例如
Universal Connection Pool 或 Hikari。连接池可以避免反复
创建新数据库连接带来的延迟。

如果数据库中已存在嵌入表，请提供表名。

```java
EmbeddingStore embeddingStore = OracleEmbeddingStore.builder()
   .dataSource(myDataSource)
   .embeddingTable("my_embedding_table")
   .build();
```

如果表尚不存在，可以通过向构建器传入 CreateOption 来创建它。

```java
EmbeddingStore embeddingStore = OracleEmbeddingStore.builder()
   .dataSource(myDataSource)
   .embeddingTable("my_embedding_table", CreateOption.CREATE_IF_NOT_EXISTS)
   .build();
```

默认情况下，嵌入表将包含以下列：

| 名称 | 类型 | 描述 |
| ---- | ---- | ----------- |
| id | VARCHAR(36) | 主键。用于存储嵌入存储生成时产生的 UUID 字符串 |
| embedding | VECTOR(*, FLOAT32) | 存储嵌入 |
| text | CLOB | 存储文本片段 |
| metadata | JSON | 存储元数据 |

如果你现有表的列与预定义的列名不匹配，
或者想使用不同的列名，可以使用 EmbeddingTable
构建器来配置你的嵌入表。

```java
OracleEmbeddingStore embeddingStore =
OracleEmbeddingStore.builder()
    .dataSource(myDataSource)
    .embeddingTable(EmbeddingTable.builder()
            .createOption(CREATE_OR_REPLACE) // use NONE if the table already exists
            .name("my_embedding_table")
            .idColumn("id_column_name")
            .embeddingColumn("embedding_column_name")
            .textColumn("text_column_name")
            .metadataColumn("metadata_column_name")
            .build())
    .build();
```

构建器允许你通过提供 Index 类的实例，在
EmbeddingTable 的嵌入列和元数据列上创建索引。有两个构建器
可以创建 Index 类的实例：IVFIndexBuilder 和 JSONIndexBuilder。

*IVFIndexBuilder* 允许你在 EmbeddingTable 的嵌入列上配置 **IVF（Inverted File Flat）** 索引。

```java
OracleEmbeddingStore embeddingStore =
    OracleEmbeddingStore.builder()
        .dataSource(myDataSource)
        .embeddingTable(EmbeddingTable.builder()
            .createOption(CreateOption.CREATE_OR_REPLACE) // use NONE if the table already exists
            .name("my_embedding_table")
            .idColumn("id_column_name")
            .embeddingColumn("embedding_column_name")
            .textColumn("text_column_name")
            .metadataColumn("metadata_column_name")
            .build())
        .index(Index.ivfIndexBuilder().createOption(CreateOption.CREATE_OR_REPLACE).build())
        .build();
```

*JSONIndexBuilder* 允许你在 EmbeddingTable 元数据列的键上配置**基于函数的索引**。

```java
OracleEmbeddingStore.builder()
    .dataSource(myDataSource)
    .embeddingTable(EmbeddingTable.builder()
        .createOption(CreateOption.CREATE_OR_REPLACE) // use NONE if the table already exists
        .name("my_embedding_table")
        .idColumn("id_column_name")
        .embeddingColumn("embedding_column_name")
        .textColumn("text_column_name")
        .metadataColumn("metadata_column_name")
        .build())
    .index(Index.jsonIndexBuilder()
        .createOption(CreateOption.CREATE_OR_REPLACE)
        .key("name", String.class, JSONIndexBuilder.Order.ASC)
        .key("year", Integer.class, JSONIndexBuilder.Order.DESC)
        .build())
    .build();
```

有关 Oracle AI Vector Search 的更多信息，请参见[文档](https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/overview-ai-vector-search.html)。

## 聊天记忆

`OracleChatMemoryStore` 可用于在 Oracle Database 中持久化聊天记忆。

创建一张表：

```sql
CREATE TABLE chat_memory (
    memory_id VARCHAR2(255) PRIMARY KEY,
    content CLOB NOT NULL
);
```

在聊天记忆中使用它：

```java
ChatMemoryStore store = OracleChatMemoryStore.builder()
   .dataSource(myDataSource)
   .tableName("chat_memory")
   .build();

ChatMemory chatMemory = MessageWindowChatMemory.builder()
   .id("conversation-1")
   .maxMessages(10)
   .chatMemoryStore(store)
   .build();
```

`OracleChatMemoryStore` 为每个 memory id 存储一行，所有消息以 JSON 形式序列化在 `content` 列中。
