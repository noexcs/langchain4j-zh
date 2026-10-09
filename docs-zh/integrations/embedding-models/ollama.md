# Ollama

https://ollama.com/

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-ollama</artifactId>
    <version>1.22.0</version>
</dependency>
```

## API

- `OllamaEmbeddingModel`

## 用法

```java
EmbeddingModel embeddingModel = OllamaEmbeddingModel.builder()
    .baseUrl("http://localhost:11434")
    .modelName("all-minilm")
    .build();

Response<Embedding> response = embeddingModel.embed("Hello, world!");
Embedding embedding = response.content();
```

## 请求/响应 API 与可观测性

`OllamaEmbeddingModel` 除了便捷方法外，还支持 `embed(EmbeddingRequest)`。Ollama 的嵌入 API 仅支持文本，因此设置了输入类型或提供了图像输入的请求会立即失败，并抛出 `UnsupportedFeatureException`。Token 用量（`prompt_eval_count`）会体现在响应元数据中。

Ollama 的可选输出参数 `dimensions` 取决于模型（只有部分模型支持缩小输出尺寸），因此需要通过构建器的 `.dimensions(...)` 进行配置，而不是作为每次调用的参数。

附加[监听器](../../tutorials/observability.md#rag-可观测性embeddingmodelembeddingstore-和-contentretriever)以观察请求、响应和错误：

```java
EmbeddingModel embeddingModel = OllamaEmbeddingModel.builder()
    .baseUrl("http://localhost:11434")
    .modelName("all-minilm")
    .listeners(List.of(myEmbeddingModelListener))
    .build();
```

## 示例

- [OllamaEmbeddingModelIT](https://github.com/langchain4j/langchain4j/blob/main/langchain4j-ollama/src/test/java/dev/langchain4j/model/ollama/OllamaEmbeddingModelIT.java)
