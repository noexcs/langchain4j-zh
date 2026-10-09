# jitLLM

[jitLLM](https://github.com/beehive-lab/jitllm) 在 JVM 内运行 GGUF 格式的 LLM。它通过 [TornadoVM](https://github.com/beehive-lab/TornadoVM) 在 GPU 上运行这些模型，TornadoVM 会针对 CUDA、OpenCL 或 Metal 对模型的 kernel 进行 JIT 编译；也可以运行在 CPU 上。无需单独的推理服务器。

## 项目配置

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-jitllm</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

```groovy
implementation 'dev.langchain4j:langchain4j-jitllm:1.22.0-beta32'
```

## 要求

* JDK 21 或更高版本。在 JDK 21 上，参见[在 JDK 21 上运行](#在-jdk-21-上运行)。
* 一个 GGUF 格式的模型（FP16、Q8_0 或 Q4_0）。支持的模型系列包括 Llama 3、Mistral、Qwen 2.5、Qwen 3、Phi-3、IBM Granite 3.3 / 4.0、Gemma 4 和 DeepSeek-R1-Distill。已测试的模型汇总在 [Hugging Face](https://huggingface.co/beehive-lab/collections)。
* JVM 选项 `--add-modules jdk.incubator.vector`。
* 要在 GPU 上运行：需要匹配你的 JDK 系列（`jdk21` 或 `jdk22plus`）以及你的 GPU 后端的 [TornadoVM SDK](https://www.tornadovm.org/downloads)，例如通过 SDKMAN! 安装（`sdk install tornadovm`）。JVM 必须通过 TornadoVM 的 `tornado` 启动器并带有 `-Duse.tornadovm=true` 启动。
* 要在普通 JVM（不使用 TornadoVM 启动器）中运行于 CPU：将 `io.github.beehive-lab:tornado-api:7.0.1-jdk22plus`（JDK 21 上使用 `7.0.1-jdk21`）作为 `runtime` 依赖。通过 TornadoVM 运行时不要包含它，因为 TornadoVM 已经提供了它。

仅支持 JVM 模式；不支持 GraalVM 原生镜像。

### 在 JDK 21 上运行

jitLLM 以两种构建版本发布：`langchain4j-jitllm` 所依赖的 `jdk22plus`，以及 `jdk21`。在 JDK 21 上，用后者替换前者，并使用 `--enable-preview` 启动 JVM，因为 `jdk21` 构建使用了 Foreign Function & Memory API，而该 API 在 JDK 21 中是预览特性：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-jitllm</artifactId>
    <version>1.22.0-beta32</version>
    <exclusions>
        <exclusion>
            <groupId>io.github.beehive-lab</groupId>
            <artifactId>jitllm</artifactId>
        </exclusion>
    </exclusions>
</dependency>

<dependency>
    <groupId>io.github.beehive-lab</groupId>
    <artifactId>jitllm</artifactId>
    <version>1.0.2-jdk21</version>
</dependency>
```

## 聊天

```java
try (JitLLMChatModel model = JitLLMChatModel.builder()
        .modelPath(Path.of("Qwen3-0.6B-Q8_0.gguf"))
        .build()) {

    String answer = model.chat("What is the capital of Germany?");
}
```

模型在构建时加载，并保留其内存（包括 GPU 内存），直到调用 `close()`。构建一次并重复使用它。

## 流式

```java
try (JitLLMStreamingChatModel model = JitLLMStreamingChatModel.builder()
        .modelPath(Path.of("Qwen3-0.6B-Q8_0.gguf"))
        .build()) {

    model.chat("Tell me a story", new StreamingChatResponseHandler() {

        @Override
        public void onPartialResponse(String partialResponse) {
            System.out.print(partialResponse);
        }

        @Override
        public void onCompleteResponse(ChatResponse completeResponse) {
            System.out.println();
        }

        @Override
        public void onError(Throwable error) {
            error.printStackTrace();
        }
    });
}
```

`chat(...)` 在响应完成后返回：模型在调用线程中运行，处理器也在该线程上被调用。为避免阻塞，请从另一个线程（例如虚拟线程）调用它。可以通过 `onPartialResponse(PartialResponse, PartialResponseContext)` 中可获取的 `StreamingHandle` 来停止流式处理。

## 在 GPU 上运行

```bash
tornado --jvm="-Duse.tornadovm=true --add-modules jdk.incubator.vector -Dtornado.device.memory=8GB" \
  -cp "target/my-app.jar:target/dependency/*" com.example.Main
```

可以使用 `mvn dependency:copy-dependencies` 填充 `target/dependency`。以这种方式启动 JVM 时，模型将在 GPU 上运行，使用 TornadoVM SDK 提供的后端。`onGPU(false)` 强制使用 CPU；如果 JVM 不是通过 TornadoVM 启动的，`onGPU(true)` 会在构建时失败。

## 配置

| 构建器方法 | 默认值 | 说明 |
|---|---|---|
| `modelPath` | 必填 | GGUF 文件的路径。 |
| `contextLength` | 4096 | 整个对话（包括响应）的最大 token 数。其内存会在加载时预留。 |
| `onGPU` | 使用 `-Duse.tornadovm=true` 启动时为 `true` | 在 GPU 或 CPU 上运行。 |
| `temperature` | 0.1 | 采样温度。 |
| `topP` | 0.95 | 核采样概率。 |
| `maxTokens` | 512 | 每个响应生成的最大 token 数（包括思考过程）。 |
| `stopSequences` | | 用于结束响应的序列。它们作用于回答，而不作用于思考过程。 |
| `seed` | 每个请求随机 | 采样的种子，用于生成可复现的响应。 |
| `think` | 模型默认值 | 推理模型是否在回答前进行思考。`false` 让它们直接回答。 |
| `returnThinking` | `false` | 通过 `AiMessage.thinking()` 返回推理模型的思考过程，并将其流式输出到 `onPartialThinking`。 |
| `defaultRequestParameters` | | 默认的 `ChatRequestParameters`；上述值优先。 |
| `listeners` | | 会在请求、响应和错误发生时收到通知的[监听器](../../tutorials/observability.md)。 |

`temperature`、`topP`、`maxOutputTokens` 和 `stopSequences` 也可以在 `ChatRequestParameters` 中按请求进行设置。

一个模型实例可以被多个线程使用，但它一次只生成一个响应：并发请求会相互等待。

## 功能

* 流式，支持取消。
* 工具，支持同步和流式，包括在一个响应中进行多次工具调用。使用工具时，流式响应会在完成后一次性交付。
* 推理模型的思考过程（`<think>` 和 `</think>` 之间的文本）：可以通过 `think` 开启或关闭，设置 `returnThinking(true)` 时会被返回。
* `ChatResponse` 中的 token 用量和结束原因。
* 不支持：JSON 响应格式、`ToolChoice.REQUIRED`、图像，以及 `modelName`、`topK`、`frequencyPenalty` 和 `presencePenalty` 参数。

## 从 GPULlama3.java 迁移

jitLLM 是 [GPULlama3.java](gpullama3-java.md) 的继任者，`langchain4j-jitllm` 取代了已弃用的 `langchain4j-gpu-llama3` 模块：

* 用 `JitLLMChatModel` 替换 `GPULlama3ChatModel`，用 `JitLLMStreamingChatModel` 替换 `GPULlama3StreamingChatModel`。
* `maxTokens` 现在只限制生成的 token 数。上下文窗口通过 `contextLength` 设置。
* 使用 `close()` 释放内存，而不是 `freeTornadoVMGPUResources()`。模型被垃圾回收时不会有自动清理。
* 思考过程仅在设置了 `returnThinking(true)` 时返回，并且不带 `<think>` 标签。
* `printLastMetrics()` 由 `ChatResponse.tokenUsage()` 取代。
* 当未设置 `onGPU` 时，模型仅在 JVM 使用 `-Duse.tornadovm=true` 启动时运行在 GPU 上。
