# 进程内（ONNX）

LangChain4j 提供本地评分（重排）模型，
由 [ONNX runtime](https://onnxruntime.ai/docs/get-started/with-java.html) 提供支持，运行在同一个 Java 进程中。

许多模型（例如来自 [Hugging Face](https://huggingface.co/) 的模型）都可以使用，
只要它们处于 ONNX 格式即可。

关于如何将模型转换为 ONNX 格式的信息见[这里](https://huggingface.co/docs/optimum/exporters/onnx/usage_guides/export_a_model)。

许多已转换为 ONNX 格式的模型可在[这里](https://huggingface.co/Xenova)获取。

### 用法

默认情况下，评分（重排）模型使用 CPU。
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-onnx-scoring</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```
```java
String pathToModel = "/home/langchain4j/model.onnx";
String pathToTokenizer = "/home/langchain4j/tokenizer.json";
OnnxScoringModel scoringModel = new OnnxScoringModel(pathToModel, pathToTokenizer);

Response<Double> response = scoringModel.score("query", "passage");
Double score = response.content();
```

`OnnxScoringModel` 实现了 `AutoCloseable`；不再需要时请关闭它以释放其原生资源。

如果你想使用 GPU，`onnxruntime_gpu` 版本见
[这里](https://onnxruntime.ai/docs/execution-providers/CUDA-ExecutionProvider.html)。
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-onnx-scoring</artifactId>
    <version>1.22.0-beta32</version>
    <exclusions>
        <exclusion>
            <groupId>com.microsoft.onnxruntime</groupId>
            <artifactId>onnxruntime</artifactId>
        </exclusion>
    </exclusions>
</dependency>

<!-- 1.22.0 support CUDA 12.x -->
<dependency>
    <groupId>com.microsoft.onnxruntime</groupId>
    <artifactId>onnxruntime_gpu</artifactId>
    <version>1.22.0</version>
</dependency>
```

```java
String pathToModel = "/home/langchain4j/model.onnx";
String pathToTokenizer = "/home/langchain4j/tokenizer.json";

OrtSession.SessionOptions options = new OrtSession.SessionOptions();
options.addCUDA(0);
OnnxScoringModel scoringModel = new OnnxScoringModel(pathToModel, options, pathToTokenizer);

Response<Double> response = scoringModel.score("query", "passage");
Double score = response.content();
```
