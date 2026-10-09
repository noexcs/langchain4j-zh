# OpenAI 兼容语言模型

许多服务和工具都暴露了 OpenAI 兼容的 API。使用它们与 LangChain4j 集成的通用方法是：

1.  **确定基础 URL：** 找到该服务的 API 端点。这通常以 `/v1` 结尾。
2.  **获取 API 密钥：** 如果服务需要身份验证，请获取一个 API 密钥。如果服务是本地服务且不需要密钥，请将一个占位符作为 `apiKey` 参数。
3.  **指定模型名称：** 确定该服务要使用的正确模型名称。这通常是必需的。
4.  **配置 `OpenAiChatModel` 或 `OpenAiStreamingChatModel`：**

    ```java
    ChatModel model = OpenAiChatModel.builder()
            .baseUrl("YOUR_API_BASE_URL") // e.g., "http://localhost:8000/v1"
            .apiKey("YOUR_API_KEY_OR_PLACEHOLDER") // e.g., "sk-yourkey" or "none"
            .modelName("MODEL_NAME_AS_PER_PROVIDER_DOCS") // e.g., "gpt-3.5-turbo" or custom name
            // Add other configurations like temperature, timeout, etc. as needed
            .logRequests(true)
            .logResponses(true)
            .build();
    ```

### 针对特定 OpenAI 兼容 API 的配置

一些 OpenAI 兼容 API 在流式响应中可能有不同的行为，特别是对于工具调用。LangChain4j 提供了配置选项来处理这些差异：

#### `accumulateToolCallId`（用于 `OpenAiStreamingChatModel`）

控制流式响应中工具调用 ID 的处理方式。默认值为 `true`。

- **启用（`true`）**：工具调用 ID 在流式块之间累积（标准 OpenAI 行为）
    - 示例：块 1 发送 "abc"，块 2 发送 "def" → 最终 ID："abcdef"
- **禁用（`false`）**：每个块的工具调用 ID 会替换前一个
    - 示例：块 1 发送 "abc"，块 2 发送 "abc" → 最终 ID："abc"
    - 对于像 DeepSeek 或 Qwen 这样在每个块中都发送完整工具调用 ID 的 API，请使用此选项

```java
StreamingChatModel model = OpenAiStreamingChatModel.builder()
        .baseUrl("https://api.deepseek.com/v1") // or other provider
        .apiKey("YOUR_API_KEY")
        .modelName("deepseek-chat")
        .accumulateToolCallId(false) // Set to false for DeepSeek, Qwen, etc.
        .build();
    ```
下面我们为流行的 OpenAI 兼容 API 提供了具体示例，包括 OrcaRouter、Tuning Engines、Groq、Docker Model Runner、GPT4All、Ollama 和 LM Studio。

### 目录：
- [使用 OpenAI 兼容语言模型的前提条件](#使用-openai-兼容语言模型的前提条件)
- [OrcaRouter](#orcarouter)
- [Tuning Engines](#tuning-engines)
- [Groq](#groq)
- [Docker Model Runner](#docker-model-runner)
- [GPT4All](#gpt4all)
- [Ollama](#ollama)
- [LM Studio](#lm-studio)

## 使用 OpenAI 兼容语言模型的前提条件

LangChain4j 的 OpenAI 模块可以与各种 OpenAI 兼容 API 一起使用，包括本地和基于云的解决方案。对于下面的每个模型，我们演示如何创建一个 `ChatModel`，然后你可以用它与模型进行对话，就像在[标准 OpenAI 示例](https://github.com/langchain4j/langchain4j-examples/blob/main/open-ai-examples/src/main/java/OpenAiChatModelExamples.java)中一样。

首先，确保你的 `pom.xml` 或 Gradle 构建文件中有 OpenAI 模块：

### 纯 Java
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai</artifactId>
    <version>1.22.0</version>
</dependency>
```

### Spring Boot
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-spring-boot4-starter</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

!!! note
    此 starter 需要 **Spring Boot 4**。在 **Spring Boot 3** 上，请改用 `langchain4j-open-ai-spring-boot-starter`。
    详情参见 [Spring Boot 集成](../../tutorials/spring-boot-integration.md#支持的版本)。

## OrcaRouter

**部署方式：** SaaS（需要密钥）

**描述：** [OrcaRouter](https://www.orcarouter.ai) 是一个为模型和智能体而构建的 OpenAI 兼容 AI 网关。与 OpenRouter 类似，它跨众多模型暴露了 provider/model 命名空间——但它还在同一端点背后结合了自适应路由、自动回退、零标记推理、可观测性、护栏以及智能体工具治理。将 OrcaRouter 作为一等提供商加入，意味着本项目的用户可以直接使用该技术栈，而无需将 OrcaRouter 视为匿名的自定义基础 URL。它还在同一端点上为 AI 智能体运行网关级零信任安全——基于默认拒绝原则审查每个提示词/响应并治理每个工具调用，无需更改应用程序代码。

**设置：**
要使用 OrcaRouter，你需要从 [OrcaRouter](https://www.orcarouter.ai) 获取一个 API 密钥（密钥以 `sk-orca-` 开头）。

配置 LangChain4j 的 `OpenAiChatModel` 或 `OpenAiStreamingChatModel`：
```java
ChatModel model = OpenAiChatModel.builder()
        .baseUrl("https://api.orcarouter.ai/v1")
        .apiKey(System.getenv("ORCAROUTER_API_KEY")) // Your actual key, e.g. "sk-orca-..."
        .modelName("deepseek/deepseek-v4-flash-0731") // Or any other model offered by OrcaRouter
        .build();
```
你可以在 [OrcaRouter 模型页面](https://www.orcarouter.ai) 找到可用的模型名称。

## Tuning Engines

**部署方式：** SaaS（需要密钥）

**描述：** [Tuning Engines](https://www.tuningengines.com/) 暴露了一个 OpenAI 兼容端点，可以置于你的模型提供商之前。LangChain4j 保留应用程序和智能体逻辑，而该端点可以集中管理路由、策略控制、审计日志、链路追踪、审批和成本可见性。

```java
ChatModel model = OpenAiChatModel.builder()
        .baseUrl("https://api.tuningengines.com/v1")
        .apiKey(System.getenv("TUNING_ENGINES_API_KEY"))
        .modelName("gpt-4o-mini")
        .build();
```

## Groq

**部署方式：** SaaS（需要密钥）

**描述：** Groq 为 LLM 提供极快的推理。

**设置：**
要使用 Groq，你需要从 [GroqCloud](https://console.groq.com/keys) 获取一个 API 密钥。

配置 LangChain4j 的 `OpenAiChatModel` 或 `OpenAiStreamingChatModel`：
```java
ChatModel model = OpenAiChatModel.builder()
        .baseUrl("https://api.groq.com/openai/v1")
        .apiKey(System.getenv("GROQ_API_KEY")) // Or your actual key
        .modelName("llama3-8b-8192") // Or any other model offered by Groq, e.g., mixtral-8x7b-32768, llama3-70b-8192
        .temperature(0.0)
        .build();
```
你可以在 [Groq 模型页面](https://console.groq.com/docs/models) 找到可用的模型名称。

## Docker Model Runner

**部署方式：** 本地

**描述：** Docker Model Runner 允许你使用 Docker Desktop 在本地运行 LLM（底层使用 `llama.cpp`，可以使用你的 CPU）。这对于开发、测试或离线使用非常有用。支持 Mac 和 Windows。

**设置：**

1. 安装 Docker Desktop
2. 在 Docker Desktop 中启用 Docker Model Runner 功能（Settings > Experimental Features > Enable Docker Model Runner）
3. 就在其下方，勾选 "Enable host-side TCP support"。
4. 使用 Docker Model Runner CLI 拉取一个模型，例如 `docker model pull ai/qwen3` 或 [此列表](https://hub.docker.com/u/ai) 中的任何其他模型。

`ai/qwen3` 的示例（有关该模型的更多信息见[此处](https://hub.docker.com/r/ai/qwen3)）：

```java
ChatModel model = OpenAiChatModel.builder()
        .baseUrl("http://localhost:12434/engines/llama.cpp/v1")
        .modelName("ai/qwen3")
        .build();
```
一些模型支持工具调用，详见 docker 模型页面。

## GPT4All

**部署方式：** 本地

**描述：** GPT4All 提供了一个桌面应用程序，可在你的机器上本地运行开源 LLM。它还可以暴露一个 OpenAI 兼容 API。

**设置：**
1. 从 [https://gpt4all.io/](https://gpt4all.io/) 下载并安装 GPT4All。
2. 启动 GPT4All，并通过其 UI 下载所需的模型，例如 `llama-3.2-1b-instruct`。
3. 在 GPT4All 设置中启用 "Web Server" 模式（"Settings" > "Application" > under Advanced: "Enable Local API Server"）。
4. 记下 GPT4All 中显示的 IP 地址和端口（通常是 `http://localhost:4891/v1`）。
5. 配置 LangChain4j：
```java
ChatModel model = OpenAiChatModel.builder()
        .baseUrl("http://localhost:4891/v1")
        .modelName("llama-3.2-1b-instruct") // The model name might be derived from the model loaded in GPT4All UI or configurable. Check GPT4All docs.
        .build();
```

## Ollama

虽然 LangChain4j 有专门的 `langchain4j-ollama` 模块（参见 [Ollama 文档](ollama.md)），但你也可以像上面展示的那样使用 OpenAI 模块连接到 Ollama 的 OpenAI 兼容端点。

**部署方式：** 本地

**描述：** Ollama 允许你在本地运行开源大型语言模型，例如 Llama 3、Mistral 等。它提供一个 OpenAI 兼容 API 端点。

**设置：**
1. 从 [https://ollama.ai/](https://ollama.ai/) 安装 Ollama。
2. 使用命令行拉取一个模型：`ollama pull <model_name>`（例如 `ollama pull gemma3`）。
3. 确保 Ollama 正在运行。它在 `http://localhost:11434/v1/` 提供 OpenAI 兼容 API。
4. 配置 LangChain4j：
```java
ChatModel model = OpenAiChatModel.builder()
        .baseUrl("http://localhost:11434/v1/")
        .modelName("gemma3")
        .build();
```

**示例：**
*   关于 OpenAI 兼容端点的使用，请改造通用的 OpenAI 示例。
*   使用专门的 Ollama 模块：[langchain4j-examples/.../OllamaChatModelExamples.java](https://github.com/langchain4j/langchain4j-examples/blob/main/src/main/java/dev/langchain4j/model/ollama/OllamaChatModelExamples.java)


## LM Studio

**部署方式：** 本地

**描述：** LM Studio 提供了一个 UI，用于发现、下载和运行本地 LLM。它还有一个 OpenAI 兼容的本地服务器。

**设置：**
1. 从 [https://lmstudio.ai/](https://lmstudio.ai/) 下载并安装 LM Studio。
2. 通过 LM Studio UI（Search 选项卡）下载你所需的模型，例如 `smollm2-135m-instruct`。
3. 进入 "Developer" 选项卡（左侧类似 `>_` 的图标），将服务器状态切换为 "running"
4. 当服务器运行时，你可以在右上角看到地址（例如 `http://127.0.0.1:1234`）。或者，cURL 调用会给你完整的 URL。
5. LMStudio 目前不支持 HTTP2，因此我们需要强制使用 HTTP1.1。为此，我们需要添加正确的 maven 或 gradle 依赖：
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-http-client-jdk</artifactId>
    <version>1.22.0</version>
</dependency>
```
6. 配置 LangChain4j 并指定 `httpClientBuilder`
```java
import java.net.http.HttpClient;
import dev.langchain4j.http.client.jdk.JdkHttpClientBuilder;
import dev.langchain4j.http.client.jdk.JdkHttpClient;

...

HttpClient.Builder httpClientBuilder = HttpClient.newBuilder()
        .version(HttpClient.Version.HTTP_1_1) ;

JdkHttpClientBuilder jdkHttpClientBuilder = JdkHttpClient.builder()
        .httpClientBuilder(httpClientBuilder);

ChatModel model = OpenAiChatModel.builder()
        .baseUrl("http://127.0.0.1:1234/v1")
        .modelName("smollm2-135m-instruct")
        .httpClientBuilder(jdkHttpClientBuilder)
        .build();
```
