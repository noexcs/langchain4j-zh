# Chroma

https://www.trychroma.com/


## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-chroma</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## API

- `ChromaEmbeddingStore`


## 示例

- [ChromaEmbeddingStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/chroma-example/src/main/java/ChromaEmbeddingStoreExample.java)

## 支持的 API 版本
Chroma 有多个 REST API 版本：
- 0.5.16 版本之前：仅支持 API V1
- 0.5.16 到 0.6.3 版本：支持 API V1 和 V2（V1 API 在 0.6.2 左右引入了一些 bug）
- 0.7.0 之后的版本：仅支持 API V2，因此在配置 `ChromaEmbeddingStore` 时
  你需要选择正确的版本：
```java
ChromaEmbeddingStore.builder()
    .apiVersion(ChromaApiVersion.V2)
    .baseUrl(...)
    .tenantName(...)
    .databaseName(...)
    .collectionName(...)
    .build();
```

## 距离度量

Chroma 集合创建时带有一个距离度量，它决定如何衡量两个嵌入之间
的距离。Chroma 支持 `cosine`、`l2`（平方欧氏距离）和 `ip`（内积），除非
请求其他度量，否则使用 `l2`。

当 `ChromaEmbeddingStore` 创建集合时，会使用 `cosine` 距离度量来创建它。
如果集合已存在，则按原样使用，无论它当初使用哪种距离度量创建：

```java
ChromaEmbeddingStore store = ChromaEmbeddingStore.builder()
    .baseUrl("http://localhost:8000")
    .collectionName("my-collection")
    .build();
```

`EmbeddingMatch.score()` 返回的相关性分数总是在 `[0, 1]` 范围内，其中 1 表示最
相关。它由集合的距离度量派生而来，因此从使用不同距离度量的集合中获得的分数
彼此不可比较。`EmbeddingSearchRequest` 的 `minScore` 也是如此，
它会与集合自身度量的分数进行比较。

对于 `ip`，只有当嵌入经过归一化时分数才是准确的，大多数嵌入模型都是这种情况。

## 当前限制

- Chroma 不能按字母数字元数据的大于和小于进行过滤，仅支持 int 和 float
- Chroma 按 *not* 过滤的行为如下：如果你按 "key" 不等于 "a" 进行过滤，
  那么实际上会返回所有 "key" != "a" 值的项，但不会返回没有 "key" 元数据的项！
