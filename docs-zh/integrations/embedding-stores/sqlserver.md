# SQL Server

SQL Server 嵌入存储与 SQL Server 2025 中引入的[向量搜索和向量索引](https://learn.microsoft.com/en-us/sql/sql-server/ai/vectors?view=sql-server-ver17)集成。

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-sqlserver</artifactId>
    <version>${latest version here}</version>
</dependency>
```

## API

- `SQLServerEmbeddingStore`

## 使用方法

此存储的实例可以通过配置构建器来创建。构建器
要求提供 DataSource 和嵌入表。

建议配置一个池化连接的 DataSource，例如
Universal Connection Pool 或 Hikari。连接池可以避免
重复创建新数据库连接带来的延迟。

### 嵌入存储配置示例

如果你的数据库中已存在嵌入表，请提供表配置：

```java
EmbeddingStore<TextSegment> embeddingStore = SQLServerEmbeddingStore.dataSourceBuilder()
   .dataSource(myDataSource)
   .embeddingTable(EmbeddingTable.builder()
           .name("my_embedding_table")
           .dimension(384) // Must specify dimension
           .build())
   .build();
```

如果表尚不存在，可以通过设置创建选项来创建它：

```java
EmbeddingStore<TextSegment> embeddingStore = SQLServerEmbeddingStore.dataSourceBuilder()
   .dataSource(myDataSource)
   .embeddingTable(EmbeddingTable.builder()
           .name("my_embedding_table")
           .createOption(CreateOption.CREATE)
           .dimension(384) 
           .build())
   .build();
```

如果表已存在，上述选项将会失败。在这种情况下，可以使用 CREATE_IF_NOT_EXISTS 选项：

```java
EmbeddingStore<TextSegment> embeddingStore = SQLServerEmbeddingStore.dataSourceBuilder()
   .dataSource(myDataSource)
   .embeddingTable(EmbeddingTable.builder()
           .name("my_embedding_table")
           .createOption(CreateOption.CREATE_IF_NOT_EXISTS)
           .dimension(384) 
           .build())
   .build();
```

最后，如果你想重新创建表，可以使用 CREATE_OR_REPLACE 选项：

```java
EmbeddingStore<TextSegment> embeddingStore = SQLServerEmbeddingStore.dataSourceBuilder()
   .dataSource(myDataSource)
   .embeddingTable(EmbeddingTable.builder()
           .name("my_embedding_table")
           .createOption(CreateOption.CREATE_OR_REPLACE)
           .dimension(384) 
           .build())
   .build();
```

如果现有表的列与预定义的列名不匹配，
或者你想使用不同的列名，可以自定义表配置：

```java
SQLServerEmbeddingStore embeddingStore =
SQLServerEmbeddingStore.dataSourceBuilder()
    .dataSource(myDataSource)
    .embeddingTable(EmbeddingTable.builder()
            .createOption(CreateOption.CREATE_OR_REPLACE)
            .name("my_embedding_table")
            .idColumn("id_column_name")
            .embeddingColumn("embedding_column_name")
            .textColumn("text_column_name")
            .metadataColumn("metadata_column_name")
            .dimension(1024)
            .build())
    .build();
```

你还可以在不提供 DataSource 的情况下直接配置 SQL Server 连接：

```java
SQLServerEmbeddingStore embeddingStore =
SQLServerEmbeddingStore.connectionBuilder()
    .host("localhost")
    .port(1433)
    .database("MyDatabase")
    .userName("myuser")
    .password("mypassword")
    .embeddingTable(EmbeddingTable.builder()
            .name("embeddings")
            .createOption(CreateOption.CREATE_OR_REPLACE)
            .dimension(384)
            .build())
    .build();
```

### 嵌入表架构

默认情况下，嵌入表将具有以下列：

| 名称 | 类型              | 描述 |
| ---- |-------------------| ----------- |
| id | NVARCHAR(36)      | 主键。用于存储嵌入存储时生成的 UUID 字符串 |
| embedding | VECTOR(dimension) | 使用 SQL Server 2025 原生向量类型存储嵌入 |
| text | NVARCHAR(MAX)     | 存储文本片段 |
| metadata | JSON              | 使用 SQL Server 2025 原生 JSON 数据类型存储元数据 |


## 半精度（float16）支持

### 动机

SQL Server 中的标准 `float32` 向量最多**1998 维**。这意味着生成超过 1998 维向量的嵌入模型（例如 OpenAI 的 `text-embedding-3-large`，最高可达 3072 维）无法使用默认向量类型进行存储。

为了克服这一限制，SQL Server 支持半精度（`float16`）向量，允许存储更高维度的向量。更多详情，请参阅 [Microsoft 关于半精度向量的文档](https://learn.microsoft.com/en-us/sql/t-sql/data-types/vector-data-type-half-precision-float?view=sql-server-ver17) 和 [JDBC 驱动文档](https://learn.microsoft.com/en-us/sql/connect/jdbc/use-vector-data-type?view=sql-server-ver17#use-vector-float16-data-type)。

### 要求

- 必须**在 SQL Server 数据库中启用预览功能（Preview features）**，才能使用半精度向量。
- JDBC 驱动属性 `vectorTypeSupport` 必须设置为 `v2`。

### 配置

`EmbeddingTable` 上的 `halfPrecision` 参数控制是否使用半精度向量：

- `HalfPrecisionConfiguration.OFF`（**默认**）：强制使用 `float32` 向量。注意，如果维度大于 1998，表创建将会失败。
- `HalfPrecisionConfiguration.ON`：强制使用 `float16` 向量。
- `HalfPrecisionConfiguration.AUTO`：默认使用 `float32`，但如果配置的维度大于 1998，则自动切换到 `float16`。

```java
EmbeddingStore<TextSegment> embeddingStore = SQLServerEmbeddingStore.dataSourceBuilder()
   .dataSource(myDataSource)
   .embeddingTable(EmbeddingTable.builder()
           .name("my_large_embedding_table")
           .dimension(3072)
           .halfPrecision(HalfPrecisionConfiguration.ON)
           .build())
   .build();
```

### 限制

- 半精度向量支持目前仅适用于 **Azure SQL 数据库**。
- 与 `float32` 向量相比，使用半精度向量可能导致**精度损失**。

## 重要说明

### 数值类型
所有数值都以 JSON 字符串的形式写入元数据字段，以避免 `Long.MAX_VALUE` 这类数字的溢出问题。

### 向量存储与相似度
SQL Server 2025+ 支持原生 VECTOR 数据类型，此模块使用 [VECTOR_DISTANCE](https://learn.microsoft.com/en-us/sql/t-sql/functions/vector-distance-transact-sql?view=sql-server-ver17) 相似度函数。
此模块支持 `VECTOR_DISTANCE` 函数的以下度量：

- **COSINE**：余弦相似度（默认）
- **EUCLIDEAN**：欧氏距离。欧氏度量需要进行一些额外计算才能从距离得到分数。

### JSON 元数据支持

SQL Server 2025 提供原生 JSON 数据类型支持和 JSON 索引功能。此模块
使用原生 JSON 数据类型存储元数据，并支持创建 JSON 索引，
以便使用 [JSON_VALUE](https://learn.microsoft.com/es-es/sql/t-sql/functions/json-value-transact-sql?view=sql-server-ver17) 函数优化元数据过滤。

你可以为特定的元数据键配置 JSON 索引的创建，并可选地指定键的顺序：

```java
EmbeddingTable embeddingTable = EmbeddingTable.builder()
    .name("test_table")
    .createOption(CreateOption.CREATE_OR_REPLACE)
    .dimension(4)
    .build();

SQLServerEmbeddingStore embeddingStore =
    SQLServerEmbeddingStore.dataSourceBuilder()
        .dataSource(myDataSource)
        .embeddingTable(embeddingTable)
        .addIndex(Index.jsonIndexBuilder()
            .createOption(CreateOption.CREATE_OR_REPLACE)
            .key("author", String.class, JSONIndexBuilder.Order.ASC)
            .key("year", Integer.class)
            .build()
        )
        .build();
```

- 使用 `Index.jsonIndexBuilder()` 创建的索引不支持 `CreateOption.CREATE_IF_NOT_EXISTS` 选项。

## 限制

- 向量索引性能取决于数据大小和分布
- 不支持在向量列上创建 DiskANN 索引
- 数据库排序规则应设置为区分大小写的排序规则，以实现元数据的区分大小写字符串比较
- 不支持 DOT 距离度量
