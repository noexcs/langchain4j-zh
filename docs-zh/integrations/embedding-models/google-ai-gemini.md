# Google AI Gemini 嵌入

https://ai.google.dev/gemini-api/docs/embeddings

## 目录

- [Maven 依赖](#maven-依赖)
- [API 密钥](#api-密钥)
- [可用模型](#可用模型)
- [GoogleAiEmbeddingModel](#googleaiembeddingmodel)
    - [基本用法](#基本用法)
    - [嵌入多段文本](#嵌入多段文本)
    - [配置嵌入模型](#配置嵌入模型)
    - [任务类型](#任务类型)
    - [使用元数据指定文档标题](#使用元数据指定文档标题)
    - [输出维度](#输出维度)
    - [批量处理](#批量处理)
- [批量嵌入处理](#批量嵌入处理)
    - [批量嵌入处理](#批量嵌入处理)
    - [创建批量嵌入任务](#创建批量嵌入任务)
    - [处理批量响应](#处理批量响应)
    - [轮询结果](#轮询结果)
    - [管理批量任务](#管理批量任务)
    - [基于文件的批量处理](#基于文件的批量处理)

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-google-ai-gemini</artifactId>
    <version>1.22.0</version>
</dependency>
```

## API 密钥

可以在此免费获取 API 密钥：https://ai.google.dev/gemini-api/docs/api-key。

## 可用模型

请在文档中查看[可用模型列表](https://ai.google.dev/gemini-api/docs/embeddings#model-versions)。

* `gemini-embedding-001`
    * 输入 token 上限：2,048
    * 输出维度大小：灵活，支持：128 - 3072，推荐：768、1536、3072

## GoogleAiEmbeddingModel

`GoogleAiEmbeddingModel` 允许你使用 Google AI Gemini 的嵌入模型从文本生成嵌入。

### 基本用法

```java
EmbeddingModel embeddingModel = GoogleAiEmbeddingModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-embedding-001")
    .build();

Response<Embedding> response = embeddingModel.embed("Hello, world!");
Embedding embedding = response.content();
```

### 嵌入多段文本

```java
List<TextSegment> segments = List.of(
    TextSegment.from("First document"),
    TextSegment.from("Second document"),
    TextSegment.from("Third document")
);

Response<List<Embedding>> response = embeddingModel.embedAll(segments);
List<Embedding> embeddings = response.content();
```

### 配置嵌入模型

```java
EmbeddingModel embeddingModel = GoogleAiEmbeddingModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-embedding-001")
    .taskType(GoogleAiEmbeddingModel.TaskType.RETRIEVAL_DOCUMENT)
    .outputDimensionality(768)
    .titleMetadataKey("title")
    .maxRetries(3)
    .timeout(Duration.ofSeconds(30))
    .logRequestsAndResponses(true)
    .build();
```

### 任务类型

`taskType` 参数可为特定用例优化嵌入：

- `RETRIEVAL_QUERY`：用于搜索查询
- `RETRIEVAL_DOCUMENT`：用于待检索的文档（文档索引的默认值）
- `SEMANTIC_SIMILARITY`：用于度量文本相似度
- `CLASSIFICATION`：用于文本分类任务
- `CLUSTERING`：用于对相似文本进行聚类
- `QUESTION_ANSWERING`：用于问答系统
- `FACT_VERIFICATION`：用于事实核查应用

### 使用元数据指定文档标题

使用 `TaskType.RETRIEVAL_DOCUMENT` 时，你可以通过元数据提供文档标题：

```java
EmbeddingModel embeddingModel = GoogleAiEmbeddingModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-embedding-001")
    .taskType(GoogleAiEmbeddingModel.TaskType.RETRIEVAL_DOCUMENT)
    .titleMetadataKey("title") // defaults to "title"
    .build();

TextSegment segment = TextSegment.from(
    "This is the document content",
    Metadata.from("title", "My Document Title")
);

Response<Embedding> response = embeddingModel.embed(segment);
```

### 输出维度

你可以指定输出维度来减小嵌入的大小：

```java
EmbeddingModel embeddingModel = GoogleAiEmbeddingModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-embedding-001")
    .outputDimensionality(256) // Reduce from default 768 dimensions
    .build();
```

### 批量处理

模型在嵌入多个分段时会自动进行批量处理，每个批次最多 100 个分段以获得最佳性能。

**注意：**这不是折扣批量 API，而是用于处理多个嵌入的便捷方法。

## 批量嵌入处理

`GoogleAiGeminiBatchEmbeddingModel` 提供了一个接口，用于以较低成本（标准定价的 50%）异步处理大量嵌入请求。它非常适合非紧急的大规模嵌入任务，完成时限（SLO）为 24 小时。

### 创建批量嵌入任务

**内联方式创建批量任务：**

```java
GoogleAiGeminiBatchEmbeddingModel batchModel = GoogleAiGeminiBatchEmbeddingModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-embedding-001")
    .taskType(GoogleAiEmbeddingModel.TaskType.RETRIEVAL_DOCUMENT)
    .outputDimensionality(768)
    .build();

// Create batch of text segments
List<TextSegment> segments = List.of(
    TextSegment.from("First document to embed"),
    TextSegment.from("Second document to embed"),
    TextSegment.from("Third document to embed")
);

// Submit the batch (generic API)
BatchResponse<Response<Embedding>> response = batchModel.submit(new BatchRequest<>(segments));

// Or, to set a Gemini-specific display name and priority, use GeminiBatchRequest:
BatchResponse<Response<Embedding>> response = batchModel.submit(GeminiBatchRequest.from(
    segments,
    "Document Embeddings Batch", // display name
    0L                           // priority (optional, defaults to 0)
));
```

**基于文件的方式创建批量任务：**

对于更大的批量任务，你可以从上传的文件创建批次：

```java
// First, upload a file with batch requests
GeminiFiles filesApi = GeminiFiles.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .build();

GeminiFile uploadedFile = filesApi.uploadFile(
    Paths.get("batch_embeddings.jsonl"),
    "Batch Embedding Requests"
);

// Wait for file to be active
while (uploadedFile.isProcessing()) {
    Thread.sleep(1000);
    uploadedFile = filesApi.getMetadata(uploadedFile.name());
}

// Create batch from file
BatchResponse<Response<Embedding>> response = batchModel.submit("My Embedding Batch Job", uploadedFile);
```

### 处理批量响应

`BatchResponse` 暴露当前的 `state()`，以及按请求划分的 `results()` 和 `responses()` / `errors()` 便捷视图。
请基于 `state()` 分支（使用 `state().isTerminal()` 判断批量任务是否仍在进行中）：

```java
BatchResponse<Response<Embedding>> response = batchModel.submit(new BatchRequest<>(segments));

if (!response.state().isTerminal()) {
    System.out.println("Batch is " + response.state());
    System.out.println("Batch ID: " + response.batchId());
} else if (response.state() == BatchState.SUCCEEDED) {
    System.out.println("Batch completed successfully!");
    for (Response<Embedding> embeddingResponse : response.responses()) {
        Embedding embedding = embeddingResponse.content();
        System.out.println("Embedding dimensions: " + embedding.dimension());
    }
} else {
    System.err.println("Batch " + response.state() + ": " + response.errors());
}
```

`responses()` 和 `errors()` 是便捷视图，永远不会为 `null`（没有内容可报告时为空）。

### 将结果与请求对应起来

`responses()` 和 `errors()` 是扁平视图，丢失了哪个输入产生了哪个结果的对应关系。
当你需要把每个结果映射回其来源分段时，请改用 `results()`：它按请求各返回一个 `BatchItemResult`，
**顺序与提交的分段相同**，因此第 i 个结果对应第 i 个分段。每个结果要么是 `BatchItemResult.Success`
（携带 `response()`），要么是 `BatchItemResult.Failure`（携带 `error()`）：

```java
List<BatchItemResult<Response<Embedding>>> results = response.results();
for (int i = 0; i < results.size(); i++) {
    BatchItemResult<Response<Embedding>> item = results.get(i);
    if (item.isSuccess()) {
        System.out.println("Segment #" + i + " -> " + item.response().content().dimension() + " dimensions");
    } else {
        BatchError error = item.error();
        System.err.println("Segment #" + i + " failed: " + error.code() + " - " + error.message());
    }
}
```

### 轮询结果

由于批量处理是异步的，你需要轮询获取结果：

```java
BatchResponse<Response<Embedding>> result = batchModel.submit(new BatchRequest<>(segments));
String batchId = result.batchId();

while (!result.state().isTerminal()) {
    Thread.sleep(5000); // Wait 5 seconds between polls
    result = batchModel.retrieve(batchId);
}

// Process final result
if (result.state() == BatchState.SUCCEEDED) {
    List<Response<Embedding>> embeddings = result.responses();
    System.out.println("Generated " + embeddings.size() + " embeddings");
} else {
    System.err.println("Batch did not succeed: " + result.state());
}
```

### 管理批量任务

**取消批量任务：**

```java
String batchId = // ... obtained from submit(...)

try {
    batchModel.cancel(batchId);
    System.out.println("Batch cancelled successfully");
} catch (HttpException e) {
    System.err.println("Failed to cancel batch: " + e.getMessage());
}
```

**删除批量任务：**

```java
batchModel.deleteBatchJob(batchId);
System.out.println("Batch deleted successfully");
```

**列出批量任务：**

```java
// List first page of batch jobs
BatchPage<Response<Embedding>> page = batchModel.list(new BatchPagination(10, null));

for (BatchResponse<Response<Embedding>> batch : page.batches()) {
    System.out.println("Batch: " + batch);
}

// Get next page if available
if (page.nextPageToken() != null) {
    BatchPage<Response<Embedding>> nextPage = batchModel.list(new BatchPagination(10, page.nextPageToken()));
}
```

### 基于文件的批量处理

对于进阶用例，你可以将批量请求写入 JSONL 文件并上传：

```java
// Create a JSONL file with batch requests
Path batchFile = Files.createTempFile("batch", ".jsonl");

try (JsonLinesWriter writer = new StreamingJsonLinesWriter(batchFile)) {
    List<BatchFileRequest<TextSegment>> fileRequests = List.of(
        new BatchFileRequest<>("segment-1", TextSegment.from("First document")),
        new BatchFileRequest<>("segment-2", TextSegment.from("Second document")),
        new BatchFileRequest<>("segment-3", TextSegment.from("Third document"))
    );
    
    batchModel.writeBatchToFile(writer, fileRequests);
}

// Upload the file
GeminiFiles filesApi = GeminiFiles.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .build();

GeminiFile uploadedFile = filesApi.uploadFile(batchFile, "Batch Embedding Requests");

// Create batch from file
BatchResponse<Response<Embedding>> response = batchModel.submit("File-Based Embedding Batch", uploadedFile);
```

### 在批量嵌入中使用元数据

使用 `TaskType.RETRIEVAL_DOCUMENT` 时，你可以通过元数据包含文档标题：

```java
GoogleAiGeminiBatchEmbeddingModel batchModel = GoogleAiGeminiBatchEmbeddingModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-embedding-001")
    .taskType(GoogleAiEmbeddingModel.TaskType.RETRIEVAL_DOCUMENT)
    .titleMetadataKey("title")
    .build();

List<TextSegment> segments = List.of(
    TextSegment.from(
        "Content of first document",
        Metadata.from("title", "First Document Title")
    ),
    TextSegment.from(
        "Content of second document",
        Metadata.from("title", "Second Document Title")
    )
);

BatchResponse<Response<Embedding>> response = batchModel.submit(GeminiBatchRequest.from(
    segments, "Documents with Titles"));
```

### 配置

`GoogleAiGeminiBatchEmbeddingModel` 支持 `GoogleAiEmbeddingModel` 相同的配置选项：

```java
GoogleAiGeminiBatchEmbeddingModel batchModel = GoogleAiGeminiBatchEmbeddingModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-embedding-001")
    .taskType(GoogleAiEmbeddingModel.TaskType.RETRIEVAL_DOCUMENT)
    .outputDimensionality(768)
    .titleMetadataKey("title")
    .maxRetries(3)
    .timeout(Duration.ofSeconds(30))
    .logRequestsAndResponses(true)
    .build();
```

### 重要限制

- **大小限制**：内联 API 支持总请求大小为 20 MB 或以下
- **批量大小**：每个批次最多 100 个分段以获得最佳性能
- **成本**：与实时请求相比，批量处理可降低成本 50%
- **完成时限**：24 小时 SLO，但实际完成往往快得多
- **适用场景**：最适合文档索引或语义搜索的大规模嵌入生成

### 示例：完整工作流

```java
GoogleAiGeminiBatchEmbeddingModel batchModel = GoogleAiGeminiBatchEmbeddingModel.builder()
    .apiKey(System.getenv("GEMINI_AI_KEY"))
    .modelName("gemini-embedding-001")
    .taskType(GoogleAiEmbeddingModel.TaskType.RETRIEVAL_DOCUMENT)
    .outputDimensionality(768)
    .build();

// Prepare batch of text segments
List<TextSegment> segments = new ArrayList<>();
for (int i = 0; i < 500; i++) {
    segments.add(TextSegment.from(
        "Document content #" + i,
        Metadata.from("title", "Document " + i)
    ));
}

// Submit batch
BatchResponse<Response<Embedding>> result = batchModel.submit(GeminiBatchRequest.from(
    segments, "Large Document Collection", 0L));
String batchId = result.batchId();

// Poll for completion
int attempts = 0;
int maxAttempts = 720; // 1 hour with 5-second intervals
while (!result.state().isTerminal()) {
    if (attempts++ >= maxAttempts) {
        throw new RuntimeException("Batch processing timeout");
    }
    Thread.sleep(5000);
    result = batchModel.retrieve(batchId);
    System.out.println("Status: " + result.state());
}

// Process results
if (result.state() == BatchState.SUCCEEDED) {
    List<Response<Embedding>> embeddings = result.responses();
    System.out.println("Generated " + embeddings.size() + " embeddings");

    // Store embeddings in your vector database
    for (int i = 0; i < embeddings.size(); i++) {
        Embedding embedding = embeddings.get(i).content();
        System.out.println("Embedding " + i + " has " + embedding.dimension() + " dimensions");
        // vectorStore.add(embedding, segments.get(i));
    }
} else {
    System.err.println("Batch did not succeed: " + result.state());
}
```

## 请求/响应 API 与能力

除了上面展示的 builder 级别的 `taskType(...)` 之外，`GoogleAiEmbeddingModel` 还支持带每次调用参数的请求/响应 API：

- **每次调用参数**：`input_type`（`EmbeddingInputType.QUERY` / `DOCUMENT`）让你以不同方式嵌入查询和文档，
  而无需配置两个模型实例。对于 `gemini-embedding-001`，它通过 Gemini 的 `RETRIEVAL_QUERY` / `RETRIEVAL_DOCUMENT`
  任务类型生效。Gemini Embedding 2 不接受任务类型参数，因此会改以提示词指令的形式应用（查询为
  `task: search result | query: ...`，文档为 `title: none | text: ...`）—— 这是自动完成的。
- **多模态**（`gemini-embedding-2-preview`，Gemini Embedding 2）：原生支持将交错的文本 + 图像
  嵌入为单个嵌入。较早的模型（如 `gemini-embedding-001`）仅支持文本。图像必须以 base64 形式提供（`ImageContent`）。
- **监听器**：通过 `GoogleAiEmbeddingModel.builder().listeners(...)` 配置。

关于请求/响应 API 和多模态用法，参见[嵌入模型](../../tutorials/rag.md#嵌入模型embedding-model)。

## 了解更多

如果你想进一步了解 Google AI Gemini 的嵌入模型，请查看[文档](https://ai.google.dev/gemini-api/docs/embeddings)。
