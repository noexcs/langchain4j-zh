# Jlama
[Jlama 项目](https://github.com/tjake/Jlama)

## 项目设置

要在项目中安装 langchain4j，请添加以下依赖：

对于 Maven 项目的 `pom.xml`

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j</artifactId>
    <version>1.22.0</version>
</dependency>

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-jlama</artifactId>
    <version>1.22.0-beta32</version>
</dependency>

<dependency>
    <groupId>com.github.tjake</groupId>
    <artifactId>jlama-native</artifactId>
    <!-- for faster inference. supports linux-x86_64, macos-x86_64/aarch_64, windows-x86_64 
       Use https://github.com/trustin/os-maven-plugin to detect os and arch -->
    <classifier>${os.detected.name}-${os.detected.arch}</classifier>
    <version>${jlama.version}</version> <!-- Version from langchain4j-jlama pom -->
</dependency>

```

对于 Gradle 项目的 `build.gradle`

```groovy
implementation 'dev.langchain4j:langchain4j:1.22.0'
implementation 'dev.langchain4j:langchain4j-jlama:1.22.0-beta32'
```

Jlama 使用了 Java 21 预览特性。你可以通过以下方式全局启用这些特性：

`export JDK_JAVA_OPTIONS="--add-modules jdk.incubator.vector --enable-preview"`

或者通过配置 maven compiler 和 failsafe 插件来启用预览特性。


### 模型选择
你可以使用 [HuggingFace](https://huggingface.co/models?library=safetensors&sort=trending) 上的大多数 safetensor 模型，并使用 `owner/model-name` 格式指定它们。
Jlama 在 http://huggingface.co/tjake 下维护了一份预量化的热门模型列表

支持使用以下架构的模型：
- Gemma 模型
- Llama 模型
- Mistral 模型
- Mixtral 模型
- GPT-2 模型
- BERT 模型

## 聊天补全
聊天模型允许你使用在对话数据上微调过的模型生成类人的回复。

### 同步
创建一个类并添加以下代码。

```java
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.jlama.JlamaChatModel;

public class HelloWorld {
    public static void main(String[] args) {
        ChatModel model = JlamaChatModel.builder()
                .modelName("tjake/TinyLlama-1.1B-Chat-v1.0-Jlama-Q4")
                .build();

        String response = model.chat("Say 'Hello World'");
        System.out.println(response);
    }
}
```
运行程序将生成如下输出的变体

```plaintext
Hello World! How can I assist you today?
```

### 流式
创建一个类并添加以下代码。

```java
import dev.langchain4j.data.message.AiMessage;
import dev.langchain4j.model.chat.response.StreamingChatResponseHandler;
import dev.langchain4j.model.jlama.JlamaStreamingChatModel;
import dev.langchain4j.model.output.Response;

import java.util.concurrent.CompletableFuture;

public class HelloWorld {
    public static void main(String[] args) {
        StreamingChatModel model = JlamaStreamingChatModel.builder()
                .modelName("tjake/TinyLlama-1.1B-Chat-v1.0-Jlama-Q4")
                .build();

        CompletableFuture<ChatResponse> futureResponse = new CompletableFuture<>();         
        model.chat("Tell me a joke about Java", new StreamingChatResponseHandler() {

            @Override
            public void onPartialResponse(String partialResponse) {
                System.out.print(partialResponse);
            }

            @Override
            public void onCompleteResponse(ChatResponse completeResponse) {
                futureResponse.complete(completeResponse);
            }

            @Override
            public void onError(Throwable error) {
                futureResponse.completeExceptionally(error);
            }    
        });

        futureResponse.join();
    }
}
```
每当 LLM 生成文本块（token）时，你都会在 `onPartialResponse` 方法中接收到它。

可以看到，下面的输出是实时流式传输的。

```plaintext
"Why do Java developers wear glasses? Because they can't C#"
```

当然，你可以将 Jlama 聊天补全与其他功能（如[设置模型参数](../../tutorials/model-parameters.md)和[聊天记忆](../../tutorials/chat-memory.md)）结合使用，以获得更准确的回复。

在[聊天记忆](../../tutorials/chat-memory.md)中，你将学习如何传递聊天历史，使 LLM 知道之前说过的内容。如果不传递聊天历史（如本简单示例所示），LLM 将不知道之前说过的内容，因此无法正确回答第二个问题（'我刚才问了什么？'）。

许多参数在幕后被设置，例如超时、模型类型和模型参数。
在[设置模型参数](../../tutorials/model-parameters.md)中，你将学习如何显式地设置这些参数。


Jlama 有一些你可以设置的特殊模型参数

 - `modelCachePath` 参数，允许你指定一个目录路径，模型下载后会缓存在该目录中。默认为 `~/.jlama`。
 - `workingDirectory` 参数，允许你为给定模型实例在磁盘上保留持久化的 ChatMemory。这比使用 Chat Memory 更快。
 - `quantizeModelAtRuntime` 参数，将在运行时对模型进行量化。当前的量化始终是 Q4。你也可以使用 jlama 项目的工具预先量化模型（更多信息请参见 [Jlama 项目](https://github.com/tjake/jlama)）。

### 函数调用
Jlama 支持对支持函数调用的模型使用该功能（Mistral、Llama-3.1 等）。
参见 [Jlama 示例](https://github.com/langchain4j/langchain4j-examples/tree/main/jlama-examples)

### JSON 模式
Jlama 暂不支持 JSON 模式。但你总是可以礼貌地要求模型返回 JSON。

## 示例

- [Jlama 示例](https://github.com/langchain4j/langchain4j-examples/tree/main/jlama-examples)
