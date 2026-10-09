# Amazon S3 Vectors

Amazon S3 Vectors 向量存储与 [Amazon S3 Vectors](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors.html) 集成，这是 Amazon S3 中内置的专用向量存储功能，专为大规模存储和查询向量嵌入而设计。

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-s3-vectors</artifactId>
    <version>${latest version here}</version>
</dependency>
```

## API

- `S3VectorsEmbeddingStore`

## 功能

- 存储带元数据的嵌入
- 使用余弦距离或欧氏距离进行向量相似度搜索
- 按元数据字段过滤搜索结果
- 首次插入嵌入时自动创建索引
- 支持标准 AWS 凭据提供程序

## 用法

### 基本配置

```java
S3VectorsEmbeddingStore embeddingStore = S3VectorsEmbeddingStore.builder()
    .vectorBucketName("my-vector-bucket")       // S3 Vectors bucket name (required)
    .indexName("my-index")                       // Index name within the bucket (required)
    .region("us-west-2")                         // AWS region (default: us-east-1)
    .distanceMetric(DistanceMetric.COSINE)       // Distance metric (default: COSINE)
    .createIndexIfNotExists(true)                // Auto-create index (default: true)
    .timeout(Duration.ofSeconds(60))             // API call timeout (default: 30 seconds)
    .credentialsProvider(myCredentialsProvider)  // Custom AWS credentials
    .build();
```

### 使用现有的 S3VectorsClient

如果你已经有一个配置好的 S3VectorsClient，可以直接将其传递给构建器：

```java
S3VectorsClient customClient = S3VectorsClient.builder()
    .region(Region.US_WEST_2)
    .credentialsProvider(myCredentialsProvider)
    .build();

S3VectorsEmbeddingStore embeddingStore = S3VectorsEmbeddingStore.builder()
    .s3VectorsClient(customClient)
    .vectorBucketName("my-vector-bucket")
    .indexName("my-index")
    .build();
```

## 距离度量

S3 Vectors 向量存储支持两种距离度量。距离值会自动转换为 [0, 1] 范围内的相关性得分，其中 1 表示最相关的匹配。

### 余弦距离（默认）

**适用于：** 文本嵌入、语义相似度搜索

- 测量向量之间夹角的余弦值
- 转换为相关性得分：`score = (1 - distance + 1) / 2`
- 结果与向量模长无关

```java
.distanceMetric(DistanceMetric.COSINE)  // Default, recommended for text embeddings
```

### 欧氏距离

**适用于：** 方向和模长都重要的场景

- 测量向量之间的直线距离
- 取值范围：[0, ∞)
- 转换为相关性得分：`score = 1 / (1 + distance)`

```java
.distanceMetric(DistanceMetric.EUCLIDEAN)
```

## 过滤

S3 Vectors 向量存储支持按元数据字段过滤搜索结果。

### 支持的过滤操作

- `isEqualTo`：相等比较
- `isNotEqualTo`：不相等比较
- `isGreaterThan`：大于比较
- `isGreaterThanOrEqualTo`：大于或等于比较
- `isLessThan`：小于比较
- `isLessThanOrEqualTo`：小于或等于比较
- `isIn`：IN 操作符（多个值）
- `isNotIn`：NOT IN 操作符
- `And`：逻辑与
- `Or`：逻辑或
- `Not`：逻辑非

## 实现细节

### 凭据

默认情况下，该存储使用 `DefaultCredentialsProvider`，遵循标准的 AWS 凭据解析链（环境变量、系统属性、凭据文件、EC2 实例配置文件等）。你可以通过构建器提供自定义的 `AwsCredentialsProvider`。

### 索引创建

当 `createIndexIfNotExists` 设置为 `true`（默认值）时，索引会在首次插入嵌入时自动创建。索引的维度和距离度量基于添加的第一个嵌入和配置的距离度量来设置。

### 资源清理

`S3VectorsEmbeddingStore` 实现了 `AutoCloseable`。当你完成对该存储的使用后，调用 `close()` 以释放底层 S3VectorsClient 资源，或使用 try-with-resources。

## 限制

- **最大结果数**：S3 Vectors 将每次查询的搜索结果限制为 100 条（topK 范围：1-100）
- **按过滤条件删除**：不支持 `removeAll(Filter)`；请改用 `removeAll(Collection<String> ids)`
- **删除全部**：`removeAll()` 将删除整个索引

## 示例

- [S3VectorsEmbeddingStoreIT](https://github.com/langchain4j/langchain4j-community/blob/main/embedding-stores/langchain4j-community-s3-vectors/src/test/java/dev/langchain4j/community/store/embedding/s3/S3VectorsEmbeddingStoreIT.java)