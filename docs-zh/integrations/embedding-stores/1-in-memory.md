# 内存

LangChain4j 提供了一个简单的 `EmbeddingStore` 接口的内存实现：
`InMemoryEmbeddingStore`。
它适用于快速原型设计和简单用例。
它在内存中保存 `Embedding` 和相关的 `TextSegment`。
搜索也在内存中进行。
它还可以持久化，并可以从 JSON 字符串或文件中恢复。

### Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j</artifactId>
    <version>1.22.0</version>
</dependency>
```

## API

- `InMemoryEmbeddingStore`


## 持久化

`InMemoryEmbeddingStore` 可以序列化为 json 字符串或文件：
```java
InMemoryEmbeddingStore<TextSegment> embeddingStore = new InMemoryEmbeddingStore<>();
embeddingStore.addAll(embeddings, embedded);

String serializedStore = embeddingStore.serializeToJson();
InMemoryEmbeddingStore<TextSegment> deserializedStore = InMemoryEmbeddingStore.fromJson(serializedStore);

String filePath = "/home/me/store.json";
embeddingStore.serializeToFile(filePath);
InMemoryEmbeddingStore<TextSegment> deserializedStore = InMemoryEmbeddingStore.fromFile(filePath);
```

## 示例

- [InMemoryEmbeddingStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/embedding/store/InMemoryEmbeddingStoreExample.java)