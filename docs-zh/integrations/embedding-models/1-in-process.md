# 进程内 (ONNX)

LangChain4j 提供了一些流行的本地嵌入模型，已打包为 Maven 依赖。
它们由 [ONNX runtime](https://onnxruntime.ai/docs/get-started/with-java.html) 驱动，
并在同一个 Java 进程中运行。

每个模型都提供 2 种版本：原版和量化版（Maven 构件名带有 `-q` 后缀，类名带有 `Quantized`）。

例如：
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-embeddings-all-minilm-l6-v2</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```
```java
EmbeddingModel embeddingModel = new AllMiniLmL6V2EmbeddingModel();
Response<Embedding> response = embeddingModel.embed("test");
Embedding embedding = response.content();
```

或者量化版：
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-embeddings-all-minilm-l6-v2-q</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```
```java
EmbeddingModel embeddingModel = new AllMiniLmL6V2QuantizedEmbeddingModel();
Response<Embedding> response = embeddingModel.embed("test");
Embedding embedding = response.content();
```

所有嵌入模型的完整列表可[在此](https://github.com/langchain4j/langchain4j/tree/main/embeddings)找到。


## 并行化

默认情况下，嵌入过程会使用所有可用的 CPU 核心进行并行处理，
因此每个 `TextSegment` 都在单独的线程中进行嵌入。

并行化通过使用 `Executor` 实现。
默认情况下，进程内嵌入模型使用缓存线程池，
线程数等于可用处理器数量。
线程缓存时间为 1 秒。

创建模型时，你可以提供 `Executor` 的自定义实例：
```java
Executor = ...;
EmbeddingModel embeddingModel = new AllMiniLmL6V2QuantizedEmbeddingModel(executor);
```

尚不支持使用 GPU 进行嵌入。

## 自定义模型

许多模型（例如来自 [Hugging Face](https://huggingface.co/) 的模型）都可以使用，
只要它们是 ONNX 格式即可。

有关如何将模型转换为 ONNX 格式的信息，可[在此](https://huggingface.co/docs/optimum/exporters/onnx/usage_guides/export_a_model)找到。

许多已经转换为 ONNX 格式的模型可在[此处](https://huggingface.co/Xenova)找到。

使用自定义嵌入模型的示例：
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-embeddings</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```
```java
String pathToModel = "/home/langchain4j/model.onnx";
String pathToTokenizer = "/home/langchain4j/tokenizer.json";
PoolingMode poolingMode = PoolingMode.MEAN;
EmbeddingModel embeddingModel = new OnnxEmbeddingModel(pathToModel, pathToTokenizer, poolingMode);

Response<Embedding> response = embeddingModel.embed("test");
Embedding embedding = response.content();
```

## 示例

- [InProcessEmbeddingModelExamples](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/embedding/model/InProcessEmbeddingModelExamples.java)
