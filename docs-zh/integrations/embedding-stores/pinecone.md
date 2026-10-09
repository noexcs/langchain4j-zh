# Pinecone

https://www.pinecone.io/

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-pinecone</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## 已知问题

- https://github.com/langchain4j/langchain4j/issues/1948
Pinecone 将所有数字存储为[浮点值](https://docs.pinecone.io/guides/data/filter-with-metadata#supported-metadata-types)，
这意味着存储在 `Metadata` 中的 `Integer` 和 `Long` 值（例如 1746714878034235396）
可能会损坏，并以不正确的数字返回！
一种可能的解决方法：在将整数值/双精度值存入 `Metadata` 之前，先将其转换为 `String`。
请注意，在这种情况下元数据过滤可能无法正常工作！

## API

- `PineconeEmbeddingStore`


## 示例

- [PineconeEmbeddingStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/pinecone-example/src/main/java/PineconeEmbeddingStoreExample.java)
