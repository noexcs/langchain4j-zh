# Kotlin 支持

!!! warning
    **对 Kotlin 用户的破坏性变更。** `ChatModel` 现在声明了一个 Java 成员
    `chatAsync(ChatRequest): CompletableFuture<ChatResponse>`。在 Kotlin 中，同签名的成员优先于扩展，
    因此之前解析到 `suspend` 扩展（返回 `ChatResponse`）的单参数裸调用，现在会解析到该成员（返回
    `CompletableFuture<ChatResponse>`）：

    ```kotlin
    // Before - resolved to the suspend extension, returned ChatResponse:
    val response: ChatResponse = model.chatAsync(request)

    // After - the bare single-arg call resolves to the Java member (a CompletableFuture):
    val future: CompletableFuture<ChatResponse> = model.chatAsync(request)

    // Migration - await the future...
    val response: ChatResponse = model.chatAsync(request).await()
    // ...or supply a coroutineContext, which still selects the suspend extension:
    val response: ChatResponse = model.chatAsync(request, Dispatchers.IO)
    ```

[Kotlin](https://kotlinlang.org) 是一种面向 JVM（及其他平台）的静态类型语言，能够编写简洁优雅的代码，并与 Java 库无缝[互操作](https://kotlinlang.org/docs/reference/java-interop.html)。
LangChain4j 利用 Kotlin [扩展](https://kotlinlang.org/docs/extensions.html)和[类型安全构建器](https://kotlinlang.org/docs/type-safe-builders.html)为 Java API 增加 Kotlin 特有的便捷功能。这使得用户能够为现有 Java 类添加专为 Kotlin 定制的额外功能。
    
## 快速开始

将 `langchain4j-kotlin` 模块添加到项目依赖中：
```xml
 <dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-kotlin</artifactId>
    <version>[LATEST_VERSION]</version>
</dependency>
```

如果你想使用数据类，请确保 classpath 中有 [Jackson module kotlin](https://github.com/FasterXML/jackson-module-kotlin)。如果使用 Maven，请添加一个运行时依赖：

```xml
 <dependency>
    <groupId>com.fasterxml.jackson.module</groupId>
    <artifactId>jackson-module-kotlin</artifactId>
    <version>[LATEST_VERSION]</version>
    <scope>runtime</scope>
</dependency>
```

## ChatModel 扩展

以下 Kotlin 代码演示了如何使用[协程和 suspend 函数](https://kotlinlang.org/docs/coroutines-basics.html)以及[类型安全构建器](https://kotlinlang.org/docs/type-safe-builders.html)与 LangChain4j 中的 [`ChatModel`](https://docs.langchain4j.dev/tutorials/chat-and-language-models) 进行交互。

```kotlin
val model = OpenAiChatModel.builder()
    .apiKey("YOUR_API_KEY")
    // more configuration parameters here ...
    .build()

CoroutineScope(Dispatchers.IO).launch {
    val response = model.chat {
        messages += systemMessage("You are a helpful assistant")
        messages += userMessage("Hello!")
        parameters {
            temperature = 0.7
        }
    }
    println(response.aiMessage().text())
}
```

交互过程通过 Kotlin 的**协程**异步完成：
- `CoroutineScope(Dispatchers.IO).launch`：在[IO 调度器](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-dispatchers/-i-o.html)上执行该过程，针对网络或文件 I/O 等阻塞任务进行了优化。通过避免阻塞调用线程来确保响应性。
- `model.chat` 是一个 suspend 函数，使用构建器代码块来组织聊天请求。这种方式减少了样板代码，使代码更易读、更易维护。

对于高级场景，为支持自定义 `ChatRequestParameters`，类型安全构建器函数接受自定义构建器：
```kotlin
fun <B : DefaultChatRequestParameters.Builder<*>> parameters(
    builder: B = DefaultChatRequestParameters.builder() as B,
    configurer: ChatRequestParametersBuilder<B>.() -> Unit
)
```
用法示例：
```kotlin
 model.chat {
    messages += systemMessage("You are a helpful assistant")
    messages += userMessage("Hello!")
    parameters(OpenAiChatRequestParameters.builder()) {
        temperature = 0.7 // DefaultChatRequestParameters.Builder property
        builder.seed(42) // OpenAiChatRequestParameters.Builder property
    }
}
```

## 流式用例

`StreamingChatModel` 扩展为那些需要在 AI 模型生成响应时对其进行增量处理的用例提供了功能。对于需要实时反馈的应用（例如聊天界面、实时编辑器或逐 token 流式交互的系统）尤其有用。
使用 Kotlin 协程，`chatFlow` 扩展函数将语言模型的流式响应转换为结构化且可取消的 `Flow` 序列，从而实现便于协程、非阻塞的实现。


以下是如何使用 `chatFlow` 实现完整交互的方法：
```kotlin
val flow = model.chatFlow { // similar to non-streaming scenario
    messages += userMessage("Can you explain how streaming works?")
    parameters { // ChatRequestParameters
        temperature = 0.7
        maxOutputTokens = 42
    }
}

runBlocking { // must run in a coroutine context 
    flow.collect { reply ->
        when (reply) {
            is StreamingChatModelReply.PartialResponse -> {
                print(reply.partialResponse) // Stream output as it arrives
            }
            is StreamingChatModelReply.CompleteResponse -> {
                println("\nComplete: ${reply.response.aiMessage().text()}")
            }
            is StreamingChatModelReply.Error -> {
                println("Error occurred: ${reply.cause.message}")
            }
        }
    }
}
```

可以参考[这个测试](https://github.com/langchain4j/langchain4j/blob/main/langchain4j-kotlin/src/test/kotlin/dev/langchain4j/kotlin/model/chat/StreamingChatModelExtensionsKtTest.kt)作为示例。

## 编译器兼容性

在 Kotlin 中定义工具时，请通过将 [`javaParameters`](https://kotlinlang.org/docs/gradle-compiler-options.html#attributes-specific-to-jvm) 设置为 `true`，确保 Kotlin 编译配置保留了方法参数的元数据以支持 Java 反射。此设置对于在工具规范中保持正确的参数名是必需的。

使用 Gradle 时，可以通过以下配置实现：
```kotlin
kotlin {
    compilerOptions {
        javaParameters = true
    }
}
```
