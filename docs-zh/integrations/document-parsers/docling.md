# Docling

[Docling](https://docling.ai) 是一个 IBM Research 文档处理引擎，可以从各种文档格式（包括 PDF、DOCX、PPTX 等）中提取文本和结构。它提供 OCR、表格提取和布局分析等高级功能。

此集成通过 REST API 与正在运行的 [docling-serve](https://github.com/docling-project/docling-serve) 实例通信，并基于 [官方 Docling Java 库](https://docling-project.github.io/docling-java/current/) 构建。


## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-document-parser-docling</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

此模块依赖于 `docling-serve-api`（接口），并将 `docling-serve-client`（参考 HTTP 客户端）作为可选的运行时依赖包含在内。

**如果你没有使用 Spring Boot 或 Quarkus**（它们可能会提供自己的 `DoclingServeApi` 实现），你还必须显式添加参考客户端：

```xml
<dependency>
    <groupId>ai.docling</groupId>
    <artifactId>docling-serve-client</artifactId>
    <version>0.6.4</version>
</dependency>
```

像 [Quarkus](https://quarkus.io) 或 [Spring Boot](https://spring.io/projects/spring-boot) 这样的框架提供了它们自己的 Docling 集成。有关如何接入这些特定实现，请参阅 [Docling Java 文档](https://docling-project.github.io/docling-java/dev/docling-serve/serve-client/#when-to-use-this-module)。


## 使用

启动一个 `docling-serve` 实例（参见 [docling-serve 文档](https://github.com/docling-project/docling-serve)），然后构建一个 `DoclingServeApi` 客户端并将其传递给解析器：

```java
DoclingServeApi api = DoclingServeApi.builder()
        .baseUrl("http://localhost:5001")
        .build();

DoclingDocumentParser parser = DoclingDocumentParser.builder()
        .doclingClient(api)
        .build();

Document document = parser.parse(inputStream);
String text = document.text();
```

要从文件、目录、URL 或类路径加载文档——并
自动填充 `file_name`、`absolute_directory_path` 和 `url` 等标准
元数据——请将 `langchain4j` 模块中的加载器
与解析器一起使用：

```java
Document fromFile = FileSystemDocumentLoader.loadDocument(Path.of("/tmp/report.pdf"), parser);
Document fromUrl = UrlDocumentLoader.load("https://example.com/report.pdf", parser);
```

### 选择 Docling 操作

Docling 执行的操作——转换、分层切分或混合
切分——由提供给构建器的 [`DocumentRequest`](https://docling-project.github.io/docling-java/dev/docling-serve/serve-api/#requests-convertdocumentrequest)
模板控制。模板包含文档来源之外的一切：
解析器会为每次调用将正在解析的文档来源注入
模板的一个新副本中，并将其路由到匹配的 Docling
端点。如果没有提供模板，则使用普通的 `ConvertDocumentRequest`。

要自定义转换，请提供一个携带你的
`ConvertDocumentOptions` 的 `ConvertDocumentRequest`：

```java
ConvertDocumentOptions options = ConvertDocumentOptions.builder()
        // configure options here
        .build();

DoclingDocumentParser parser = DoclingDocumentParser.builder()
        .doclingClient(api)
        .documentRequest(ConvertDocumentRequest.builder()
                .options(options)
                .build())
        .build();
```

> 已弃用的 `Builder.options(ConvertDocumentOptions)` 快捷方式仍然
> 可用，它只是委托给 `documentRequest(...)`，但建议传递一个
> `ConvertDocumentRequest`，这样你还可以选择 Docling 操作。

要将文档进行切分而不是转换，请提供一个
`HierarchicalChunkDocumentRequest` 或 `HybridChunkDocumentRequest`：

```java
DoclingDocumentParser parser = DoclingDocumentParser.builder()
        .doclingClient(api)
        .documentRequest(HybridChunkDocumentRequest.builder().build())
        .build();
```

模板所携带的任何文档来源都会被忽略——解析器会注入
正在解析的文档来源。模板必须描述一个 body 内
操作：`BatchConvertDocumentRequest`，或者携带非 body 内
目标（例如 `ZipTarget` 或 `PresignedUrlTarget`）的请求，会导致 `build()`
失败。

### 自定义文本提取

默认情况下，解析器从转换响应中提取 markdown 内容，
并连接切分响应中的切分文本（以换行符分隔）。你可以通过两个构建器方法自定义
文本的提取方式，每个方法接收具体的
响应类型——无需强制类型转换：

- `documentTextExtractor(Function<InBodyConvertDocumentResponse, String>)` — 用于
  转换请求。可以访问各种
  格式（markdown、HTML、文本、doctags、JSON）的转换文档、转换错误、处理
  时间和状态信息。
- `chunkTextExtractor(Function<ChunkDocumentResponse, String>)` — 用于切分
  请求。可以访问切分块及其元数据。

如果你需要控制整个生成的 `Document`——例如附加
额外的 `Metadata`（如从结构化响应派生的来源信息）——请改用
返回 `Document` 的变体：

- `documentExtractor(Function<InBodyConvertDocumentResponse, Document>)`
- `chunkExtractor(Function<ChunkDocumentResponse, Document>)`

对于每种响应类型，你**要么**设置文本提取器**要么**设置
`Document` 提取器——一对中的两个变体互斥，同时
配置两者（`documentTextExtractor` + `documentExtractor`，或
`chunkTextExtractor` + `chunkExtractor`）会使 `build()` 抛出
`IllegalArgumentException`。

```java
DoclingDocumentParser parser = DoclingDocumentParser.builder()
        .doclingClient(api)
        .documentRequest(ConvertDocumentRequest.builder()
                .options(ConvertDocumentOptions.builder().toFormat(OutputFormat.JSON).build())
                .build())
        .documentExtractor(response -> {
            DoclingDocument doc = response.getDocument().getJsonContent();
            String fullText = buildFullText(doc);
            return Document.from(fullText, buildProvenanceMetadata(doc, fullText));
        })
        .build();
```

解析器始终会在你的提取器返回的内容之上添加 `document_size_bytes` 元数据条目。

例如，要提取 HTML 内容而不是 markdown：

```java
DoclingDocumentParser parser = DoclingDocumentParser.builder()
        .doclingClient(api)
        .documentTextExtractor(response -> response.getDocument().getHtmlContent())
        .build();
```

或者提取纯文本：

```java
DoclingDocumentParser parser = DoclingDocumentParser.builder()
        .doclingClient(api)
        .documentTextExtractor(response -> response.getDocument().getTextContent())
        .build();
```

以及自定义切分块的连接方式：

```java
DoclingDocumentParser parser = DoclingDocumentParser.builder()
        .doclingClient(api)
        .documentRequest(HybridChunkDocumentRequest.builder().build())
        .chunkTextExtractor(response -> response.getChunks().stream()
                .map(Chunk::getText)
                .collect(Collectors.joining("\n\n")))
        .build();
```

### 异步 / 响应式解析

`DoclingDocumentParser.parse(InputStream)` 通过阻塞底层的异步调用来满足同步的
`DocumentParser` 契约。对于
响应式或非阻塞管道，请使用 `parseAsync(InputStream)`，它返回一个
`CompletionStage<Document>`：

```java
CompletionStage<Document> stage = parser.parseAsync(inputStream);
```

`parseAsync` 将读取输入流和准备请求的工作卸载到
后台线程（通过 `CompletableFuture.supplyAsync`，即公共
`ForkJoinPool`），因此它在返回时不会阻塞调用线程。解析出的
`Document`——或任何失败（`null`/空流、请求构建错误，或
来自 Docling 调用的错误）——都会通过返回的 stage 传递：它会
以异常方式完成而不是抛出异常，因此响应式调用方不需要
外围的 `try/catch`。

这可以直接用于响应式类型，例如 Mutiny：

```java
Uni.createFrom().completionStage(() -> parser.parseAsync(inputStream));
```

> **线程说明。** `parseAsync` 只控制流在哪里被读取；
> Docling 网络调用本身运行在 Docling 客户端拥有的线程上。
> 参考 `docling-serve-client` 在公共
> `ForkJoinPool` 上执行其 HTTP 和任务轮询，并且不暴露执行器来更改这一点。如果你需要控制
> 阻塞网络工作运行的位置（例如专用池或虚拟
> 线程），请提供一个自定义的
> [`DoclingRequestExecutor`](#自定义-docling-的调用方式)，在你自己的执行器上调用
> 客户端。

### 自定义 Docling 的调用方式

默认情况下，解析器调用 Docling 的异步转换/切分端点，
与请求类型相匹配。这些端点本身就会提交任务、轮询
完成状态并获取结果——全部在公共 `ForkJoinPool` 上进行，因此
仅仅为了获得该任务/队列行为并不需要自定义执行器。当你想要
提供 `DoclingRequestExecutor` 时：

- 在 Docling 调用周围添加**重试或退避**；
- 在**你自己的执行器**（专用池或虚拟
  线程）上运行阻塞调用，而不是公共 `ForkJoinPool`；或者
- 执行**完全自定义的编排**（例如使用自定义轮询频率自行
  驱动任务/队列端点）。

要在失败时重试一次转换：

```java
DoclingDocumentParser parser = DoclingDocumentParser.builder()
        .doclingClient(api)
        .requestExecutor((client, request) -> {
            ConvertDocumentRequest convertRequest = (ConvertDocumentRequest) request;
            return client.convertSourceAsync(convertRequest)
                    .exceptionallyCompose(error -> client.convertSourceAsync(convertRequest));
        })
        .build();
```

要在你自己的执行器上运行阻塞工作（此处为虚拟线程）——这使用
*同步* 的 `convertSource`，使网络调用在提供的池上
运行，而不是公共 `ForkJoinPool` 上：

```java
Executor executor = Executors.newVirtualThreadPerTaskExecutor();

DoclingDocumentParser parser = DoclingDocumentParser.builder()
        .doclingClient(api)
        .requestExecutor((client, request) -> CompletableFuture.supplyAsync(
                () -> client.convertSource((ConvertDocumentRequest) request), executor))
        .build();
```

当提供了自定义执行器时，解析器不再限制请求
类型或目标（执行器拥有这些语义），因此诸如
`BatchConvertDocumentRequest` 或非 body 内目标之类的操作变得可用。

## API

- `DoclingDocumentParser`
- `DoclingRequestExecutor`


## 示例

- [DoclingDocumentParserTest](https://github.com/langchain4j/langchain4j/blob/main/document-parsers/langchain4j-document-parser-docling/src/test/java/dev/langchain4j/data/document/parser/docling/DoclingDocumentParserTest.java)
- [DoclingDocumentParserIT](https://github.com/langchain4j/langchain4j/blob/main/document-parsers/langchain4j-document-parser-docling/src/test/java/dev/langchain4j/data/document/parser/docling/DoclingDocumentParserIT.java)
