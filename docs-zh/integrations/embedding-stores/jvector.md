# JVector

https://github.com/jbellis/jvector

JVector 是一个纯 Java 嵌入式向量搜索引擎，使用基于图的索引提供高性能的近似最近邻（ANN）搜索。它融合了 DiskANN 和 HNSW 两大算法族，提供可配置精度/性能权衡的快速相似度搜索。

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-jvector</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

注意：这是一个社区集成模块。你可能需要在项目配置中添加 langchain4j-community 仓库。

## API

- `JVectorEmbeddingStore`

## 特性

- **纯 Java 实现**：无需原生依赖，Java 能运行的地方就能运行
- **基于图的索引**：使用 HNSW 层次结构和 Vamana 算法实现高性能 ANN 搜索
- **默认内存模式**：搜索速度快，支持可选磁盘持久化
- **可配置性能**：通过 `maxDegree` 和 `beamWidth` 等参数调整精度/速度权衡
- **多种相似度函数**：支持 DOT_PRODUCT（默认）、COSINE 和 EUCLIDEAN 距离度量
- **线程安全**：无阻塞并发控制允许安全的并发访问
- **磁盘持久化**：索引的可选保存/加载功能
- **动态更新**：索引创建后可以添加和删除嵌入

## 基本用法

### 内存存储

创建一个简单的内存向量存储：

```java
EmbeddingStore<TextSegment> store = JVectorEmbeddingStore.builder()
    .dimension(384)                    // Must match your embedding model's dimension
    .build();
```

### 持久化存储

创建一个带磁盘持久化的向量存储：

```java
EmbeddingStore<TextSegment> store = JVectorEmbeddingStore.builder()
    .dimension(384)
    .persistencePath("/path/to/index") // Base path for index files
    .build();

// Add embeddings...
store.add(embedding, textSegment);

// Save to disk
((JVectorEmbeddingStore) store).save();
```

当你使用 `persistencePath` 创建存储时，如果该位置已存在文件，索引将自动从磁盘加载。

## 配置选项

JVector 提供多个构建器选项来调整性能：

```java
EmbeddingStore<TextSegment> store = JVectorEmbeddingStore.builder()
    .dimension(384)                    // Required: embedding dimension
    .maxDegree(16)                     // Graph connectivity (default: 16)
    .beamWidth(100)                    // Index construction quality (default: 100)
    .neighborOverflow(1.2f)            // Overflow during construction (default: 1.2)
    .alpha(1.2f)                       // Diversity parameter (default: 1.2)
    .similarityFunction(VectorSimilarityFunction.DOT_PRODUCT) // Default
    .persistencePath("/path/to/index") // Optional: enable persistence
    .build();
```

### 参数指南

- **dimension**：必须与嵌入模型的输出维度匹配（必填）
- **maxDegree**：控制每个节点的图连接数。更高的值可提高召回率，但占用更多内存。推荐值：16（默认）
- **beamWidth**：控制索引构建质量。更高的值能构建更好的索引，但耗时更长。推荐值：100（默认）
- **neighborOverflow**：内存索引推荐 1.2（默认），磁盘索引推荐 1.5
- **alpha**：控制边距离与多样性的权衡。高维向量推荐 1.2（默认），低维（2D/3D）向量推荐 2.0
- **similarityFunction**：
  - `DOT_PRODUCT` - 对归一化向量最快（默认）
  - `COSINE` - 用于余弦相似度
  - `EUCLIDEAN` - 用于欧氏距离

## 持久化

JVector 支持从磁盘保存和加载索引：

```java
// Create store with persistence enabled
JVectorEmbeddingStore store = JVectorEmbeddingStore.builder()
    .dimension(384)
    .persistencePath("/path/to/index")
    .build();

// Add embeddings
store.add(embeddings, textSegments);

// Save to disk (creates .graph and .metadata files)
store.save();

// Later: Load automatically when creating with same path
JVectorEmbeddingStore loadedStore = JVectorEmbeddingStore.builder()
    .dimension(384)
    .persistencePath("/path/to/index")
    .build();
// All previous embeddings and index structure are restored
```

持久化会创建两个文件：
- `{path}.graph` - 包含向量的图索引结构
- `{path}.metadata` - 嵌入 ID、文本片段和元数据

## 当前限制

- **不支持元数据过滤**：JVector 不支持在搜索操作期间按元数据过滤搜索结果。所有过滤都必须在搜索后进行。
- **修改后需重建索引**：添加或删除嵌入会使索引失效，索引会在下一次搜索时重建。为获得最佳性能，请在可能时批量添加。
- **维度必须匹配**：所有嵌入必须与创建存储时指定的维度相同。

## 性能特征

JVector 针对以下方面进行了优化：
- **快速相似度搜索**：搜索为对数时间复杂度
- **线性可扩展性**：索引构建随 CPU 核心数线性扩展
- **内存效率**：仅内存索引，支持可选磁盘持久化
- **高召回率**：基于图的方法在适当调优后通常能达到 >98% 的召回率

理想的使用场景：
- 需要向量搜索且无外部依赖的嵌入式应用
- 开发和测试环境
- 希望完全掌控索引的生产部署
- 需要磁盘持久化但又不想使用独立数据库的应用

## 示例

- 示例代码可在 [JVector 源代码仓库](https://github.com/jbellis/jvector/tree/main/jvector-examples)中找到
- 有关 LangChain4j 特定的集成示例，请查看 [langchain4j-community-jvector 模块](https://github.com/langchain4j/langchain4j-community/tree/main/embedding-stores/langchain4j-community-jvector/src/test/java)中的测试文件
