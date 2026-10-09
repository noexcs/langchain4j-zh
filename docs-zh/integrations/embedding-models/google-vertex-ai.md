# Google Vertex AI

## 快速上手

开始之前，请按照[Vertex AI Gemini 集成教程](../language-models/google-vertex-ai-gemini.md)中 `Get started` 部分所述的步骤，创建一个
Google Cloud Platform 账户，并建立一个可访问 Vertex AI API 的新项目。

## 添加依赖

将以下依赖添加到项目的 `pom.xml` 中：

```xml
<dependency>
  <groupId>dev.langchain4j</groupId>
  <artifactId>langchain4j-vertex-ai</artifactId>
  <version>1.22.0-beta32</version>
</dependency>
```

或者项目的 `build.gradle`：

```groovy
implementation 'dev.langchain4j:langchain4j-vertex-ai:1.22.0-beta32'
```

### 尝试一个示例代码：

[使用 Vertex AI 嵌入模型的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/embedding/model/VertexAiEmbeddingModelExample.java)

`PROJECT_ID` 字段表示你创建新的 Google Cloud 项目时设置的变量。

```java
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.output.Response;
import dev.langchain4j.model.vertexai.VertexAiEmbeddingModel;

public class VertexAiEmbeddingModelExample {
    
    private static final String PROJECT_ID = "YOUR-PROJECT-ID";
    private static final String MODEL_NAME = "textembedding-gecko@latest";

    public static void main(String[] args) {

        EmbeddingModel embeddingModel = VertexAiEmbeddingModel.builder()
                .project(PROJECT_ID)
                .location("us-central1")
                .endpoint("us-central1-aiplatform.googleapis.com:443")
                .publisher("google")
                .modelName(MODEL_NAME)
                .build();

        Response<Embedding> response = embeddingModel.embed("Hello, how are you?");
        
        Embedding embedding = response.content();

        int dimension = embedding.dimension(); // 768
        float[] vector = embedding.vector(); // [-0.06050122, -0.046411075, ...

        System.out.println(dimension);
        System.out.println(embedding.vectorAsList());
    }
}
```

### 可用的嵌入模型

|英文模型|多语言模型|
|---|---|
|`textembedding-gecko@001`|`textembedding-gecko-multilingual@001`|
|`textembedding-gecko@003`|`text-multilingual-embedding-002`|
|`text-embedding-004`|   |

[多语言模型支持的语言列表](https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings#language_coverage_for_textembedding-gecko-multilingual_models)

以 `@latest` 结尾的模型名称引用该模型的最新版本。

默认情况下，大多数嵌入模型输出 768 维的向量嵌入（接受可配置较低维度的 "Matryoshka" 模型除外）。
该 API 最多接受每个待嵌入片段 2,048 个输入 token。
你可以发送最多 250 个文本片段。
当你要求同时嵌入超过 250 个片段时，`VertexAiEmbeddingModel` 类会自动且透明地将请求拆分为多个批次。
嵌入 API 限制每次调用总计 20,000 token（跨所有片段）。达到该限制时，`VertexAiEmbeddingModel` 会再次对请求进行分批，以避免触及该限制。

### 配置嵌入模型

```java
EmbeddingModel embeddingModel = VertexAiEmbeddingModel.builder()
    .project(PROJECT_ID)
    .location("us-central1")
    .endpoint("us-central1-aiplatform.googleapis.com:443") // optional
    .publisher("google")
    .modelName(MODEL_NAME)
    .maxRetries(2)             // 2 by default
    .maxSegmentsPerBatch(250)  // up to 250 segments per batch
    .maxTokensPerBatch(2048)   // up to 2048 tokens per segment
    .taskType()                // see below for the different task types
    .titleMetadataKey()        // for the RETRIEVAL_DOCUMENT task, you can specify a title  
                               // for the text segment to identify its document origin
    .autoTruncate(false)       // false by default: truncates segments longer than 2,048 input tokens
    .outputDimensionality(512) // for models that support different output vector dimensions
    .credentials(credentials)  // custom Google Cloud credentials    
    .build();
```

## 嵌入任务类型

嵌入模型可用于不同的使用场景。
为了获得更好的嵌入值，你可以从以下任务中指定一个 _task_：

* `RETRIEVAL_QUERY`
* `RETRIEVAL_DOCUMENT`
* `SEMANTIC_SIMILARITY`
* `CLASSIFICATION`
* `CLUSTERING`
* `QUESTION_ANSWERING`
* `FACT_VERIFICATION`
* `CODE_RETRIEVAL_QUERY`

参见[受支持的模型列表](https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/task-types)。

### 参考

[关于 Vertex AI 嵌入模型的 Google Codelab](https://codelabs.developers.google.com/codelabs/genai-chat-java-palm-langchain4j)

[可用的稳定版嵌入模型](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings#model_versions)

[最新版嵌入模型版本](https://cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versioning#palm-latest-models)
