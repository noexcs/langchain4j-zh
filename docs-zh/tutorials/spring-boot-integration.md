# Spring Boot 集成

LangChain4j 为以下内容提供 [Spring Boot starters](https://github.com/langchain4j/langchain4j-spring)：
- 主流集成
- 声明式 [AI 服务](ai-services.md)


## Spring Boot Starters

Spring Boot starters 通过属性帮助你创建和配置
[语言模型](../integrations/language-models/index.md)、
[嵌入模型](../integrations/embedding-models/index.md)、
[向量存储](../integrations/embedding-stores/index.md)，
以及其他核心 LangChain4j 组件。

要使用 [Spring Boot starters](https://github.com/langchain4j/langchain4j-spring) 之一，
请引入对应的依赖。

Spring Boot starter 依赖的命名约定为：
- `langchain4j-{integration-name}-spring-boot4-starter` 用于 **Spring Boot 4**
- `langchain4j-{integration-name}-spring-boot-starter` 用于 **Spring Boot 3**

以 OpenAI（`langchain4j-open-ai`）为例：

**Spring Boot 4：**
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-spring-boot4-starter</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

**Spring Boot 3：**
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai-spring-boot-starter</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

然后，你可以在 `application.properties` 文件中按如下方式配置模型参数：
```
langchain4j.open-ai.chat-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.chat-model.model-name=gpt-4o
langchain4j.open-ai.chat-model.log-requests=true
langchain4j.open-ai.chat-model.log-responses=true
...
```

在这种情况下，会自动创建 `OpenAiChatModel` 的一个实例（它是 `ChatModel` 的实现），
你可以在需要的地方自动装配它：
```java
@RestController
public class ChatController {

    ChatModel chatModel;

    public ChatController(ChatModel chatModel) {
        this.chatModel = chatModel;
    }

    @GetMapping("/chat")
    public String model(@RequestParam(value = "message", defaultValue = "Hello") String message) {
        return chatModel.chat(message);
    }
}
```

如果你需要 `StreamingChatModel` 的实例，
请使用 `streaming-chat-model` 属性而不是 `chat-model` 属性：
```
langchain4j.open-ai.streaming-chat-model.api-key=${OPENAI_API_KEY}
...
```


## 声明式 AI 服务的 Spring Boot starter

LangChain4j 提供了一个 Spring Boot starter，用于自动配置
[AI 服务](ai-services.md)、[RAG](rag.md)、[工具](tools.md) 等。

假设你已经引入了某个集成 starter（见上文），
请引入 `langchain4j-spring-boot4-starter`（Spring Boot 4）或 `langchain4j-spring-boot-starter`（Spring Boot 3）：

**Spring Boot 4：**
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-spring-boot4-starter</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

**Spring Boot 3：**
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-spring-boot-starter</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

现在你可以定义 AI 服务接口，并用 `@AiService` 对其进行注解：
```java
@AiService
interface Assistant {

    @SystemMessage("You are a polite assistant")
    String chat(String userMessage);
}
```

可以把它想象成一个标准的 Spring Boot `@Service`，只是多了 AI 能力。

应用启动时，LangChain4j starter 会扫描 classpath，
找到所有带 `@AiService` 注解的接口。
对于找到的每个 AI 服务，它会使用应用上下文中可用的所有 LangChain4j 组件创建该接口的一个实现，
并将其注册为 bean，
这样你就可以在需要的地方自动装配它：
```java
@RestController
class AssistantController {

    @Autowired
    Assistant assistant;

    @GetMapping("/chat")
    public String chat(String message) {
        return assistant.chat(message);
    }
}
```

### 组件自动装配
如果以下组件存在于应用上下文中，它们将被自动装配到 AI 服务中：
- `ChatModel`
- `StreamingChatModel`
- `ChatMemory`
- `ChatMemoryProvider`
- `ContentRetriever`
- `RetrievalAugmentor`
- `ToolProvider`
- `ToolExecutionErrorHandler` 和 `ToolArgumentsErrorHandler`（参见[错误处理](tools.md#错误处理)）
- 任何 `@Component` 或 `@Service` 类中所有带 `@Tool` 注解的方法
示例：
```java
@Component
public class BookingTools {

    private final BookingService bookingService;

    public BookingTools(BookingService bookingService) {
        this.bookingService = bookingService;
    }

    @Tool
    public Booking getBookingDetails(String bookingNumber, String customerName, String customerSurname) {
        return bookingService.getBookingDetails(bookingNumber, customerName, customerSurname);
    }

    @Tool
    public void cancelBooking(String bookingNumber, String customerName, String customerSurname) {
        bookingService.cancelBooking(bookingNumber, customerName, customerSurname);
    }
}
```

!!! note
    如果应用上下文中存在多个同类型的组件，应用将启动失败。
    在这种情况下，请使用显式装配模式（下文有说明）。

### 显式组件装配

如果你有多个 AI 服务，并希望为每个服务装配不同的 LangChain4j 组件，
可以使用显式装配模式（`@AiService(wiringMode = EXPLICIT)`）来指定使用哪些组件。

假设我们配置了两个 `ChatModel`：
```properties
# OpenAI
langchain4j.open-ai.chat-model.api-key=${OPENAI_API_KEY}
langchain4j.open-ai.chat-model.model-name=gpt-4o-mini

# Ollama
langchain4j.ollama.chat-model.base-url=http://localhost:11434
langchain4j.ollama.chat-model.model-name=llama3.1
```

```java
@AiService(wiringMode = EXPLICIT, chatModel = "openAiChatModel")
interface OpenAiAssistant {

    @SystemMessage("You are a polite assistant")
    String chat(String userMessage);
}

@AiService(wiringMode = EXPLICIT, chatModel = "ollamaChatModel")
interface OllamaAssistant {

    @SystemMessage("You are a polite assistant")
    String chat(String userMessage);
}
```

!!! note
    在这种情况下，你必须显式指定**所有**组件。

#### 通过配置选择组件

除了硬编码 bean 名称，你还可以使用属性占位符，
这样装配到 AI 服务中的组件就可以通过配置来更改（例如按环境或 profile）：
```properties
my-app.assistant.chat-model-bean=ollamaChatModel
my-app.assistant.tool-beans=weatherTools,calendarTools
```

```java
@AiService(
        wiringMode = EXPLICIT,
        chatModel = "${my-app.assistant.chat-model-bean:openAiChatModel}",
        tools = "${my-app.assistant.tool-beans}"
)
interface Assistant {

    String chat(String userMessage);
}
```

有几点需要注意：
- 占位符必须解析为一个 **bean 名称**（例如 `ollamaChatModel`），而不是 LLM 模型的名称（例如 `llama3.1`）。
模型名称配置在 `ChatModel` bean 本身之上（例如 `langchain4j.ollama.chat-model.model-name`）。
- 可以在冒号后指定默认值：`${my-app.assistant.chat-model-bean:openAiChatModel}`。
- 如果占位符无法解析且没有默认值，应用将启动失败。
- 如果占位符解析为空值，该属性将视为未设置。
- 对于 `tools`，占位符可以解析为多个以逗号分隔的 bean 名称。

更多详情可参见[此处](https://github.com/langchain4j/langchain4j-spring/blob/main/langchain4j-spring-boot-starter/src/main/java/dev/langchain4j/service/spring/AiService.java)
（Spring Boot 4 变体使用相同的 API）。

### 监听 AI 服务注册事件

当你以声明式方式完成 AI 服务开发后，可以通过实现 `ApplicationListener<AiServiceRegisteredEvent>` 接口来监听
`AiServiceRegisteredEvent`。
当 AI 服务在 Spring 上下文中注册时，该事件会被触发，
使你可以在运行时获取所有已注册 AI 服务及其工具的信息。
示例如下：
```java
@Component
class AiServiceRegisteredEventListener implements ApplicationListener<AiServiceRegisteredEvent> {


    @Override
    public void onApplicationEvent(AiServiceRegisteredEvent event) {
        Class<?> aiServiceClass = event.aiServiceClass();
        List<ToolSpecification> toolSpecifications = event.toolSpecifications();
        for (int i = 0; i < toolSpecifications.size(); i++) {
            System.out.printf("[%s]: [Tool-%s]: %s%n", aiServiceClass.getSimpleName(), i + 1, toolSpecifications.get(i));
        }
    }
}
```

## Flux

在流式场景下，你可以将 `Flux<String>` 用作 AI 服务的返回类型：
```java
@AiService
interface Assistant {

    @SystemMessage("You are a polite assistant")
    Flux<String> chat(String userMessage);
}
```
为此，请引入 `langchain4j-reactor` 模块。
更多详情见[此处](ai-services.md#flux)。

该模块还为[非阻塞模式](non-blocking.md)提供了 `Mono<T>` 和 `Flux<AiServiceStreamingEvent>`，
starter 还可以通过 `langchain4j.executor.use-spring-task-executor=true` 将 LangChain4j 卸载的工作
路由到 Spring 自身的任务执行器，使链路追踪、MDC 和安全上下文跟随异步调用。


## 可观测性

要为 `ChatModel` 或 `StreamingChatModel`
bean 启用可观测性，你需要声明一个或多个 `ChatModelListener` bean：

```java
@Configuration
class MyConfiguration {
    
    @Bean
    ChatModelListener chatModelListener() {
        return new ChatModelListener() {

            private static final Logger log = LoggerFactory.getLogger(ChatModelListener.class);

            @Override
            public void onRequest(ChatModelRequestContext requestContext) {
                log.info("onRequest(): {}", requestContext.chatRequest());
            }

            @Override
            public void onResponse(ChatModelResponseContext responseContext) {
                log.info("onResponse(): {}", responseContext.chatResponse());
            }

            @Override
            public void onError(ChatModelErrorContext errorContext) {
                log.info("onError(): {}", errorContext.error().getMessage());
            }
        };
    }
}
```

应用上下文中的每个 `ChatModelListener` bean 都会被自动
注入到我们任一 Spring Boot starter 创建的所有 `ChatModel` 和 `StreamingChatModel` bean 中。

### Micrometer 指标
在你的项目中添加 `langchain4j-micrometer-metrics` 依赖：

Maven：
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-micrometer-metrics</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```
Gradle：
```gradle
implementation 'dev.langchain4j:langchain4j-micrometer-metrics:1.22.0-beta32'
```

#### Micrometer Actuator 配置
你的项目中还应具备必要的 Actuator 依赖。
例如，如果你在使用 Spring Boot，可以在 `pom.xml` 中添加以下依赖：

Maven：
```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```
Gradle：
```gradle
implementation 'org.springframework.boot:spring-boot-starter-actuator'
```

在属性中启用 `/metrics` Actuator 端点。

application.properties：
```properties
management.endpoints.web.exposure.include=metrics
```
application.yaml：
```yaml
management:
  endpoints:
    web:
      exposure:
        include: metrics
```

#### 配置 `MicrometerMetricsChatModelListener` bean

在 Spring Boot 应用中，你可以将监听器定义为 bean，并注入 `MeterRegistry`：

```java
import dev.langchain4j.micrometer.metrics.listeners.MicrometerMetricsChatModelListener;
import io.micrometer.core.instrument.MeterRegistry;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class MetricsConfig {

    @Bean
    public MicrometerMetricsChatModelListener listener(MeterRegistry meterRegistry) {
        return new MicrometerMetricsChatModelListener(meterRegistry);
    }
}
```

#### 查看指标

你可以通过访问应用的 `/actuator/metrics` 端点来查看指标。

例如，如果你的应用运行在 `localhost:8080` 上，
可以访问 http://localhost:8080/actuator/metrics 来查看指标。

##### Token 用量指标

在以下地址查看 token 用量指标：
```
http://localhost:8080/actuator/metrics/gen_ai.client.token.usage
```

##### 按 Token 类型过滤

`gen_ai.token.type` 标签指示 token 用于输入还是输出：

| Token 类型 | 端点 |
|------------|----------|
| 输入 token | `/actuator/metrics/gen_ai.client.token.usage?tag=gen_ai.token.type:input` |
| 输出 token | `/actuator/metrics/gen_ai.client.token.usage?tag=gen_ai.token.type:output` |

> **注意**：`gen_ai.client.token.usage` 指标是一个直方图（DistributionSummary）。不带任何标签的端点显示的是跨所有 token 类型、模型和提供商的聚合统计（count、total、max）。

### Micrometer Observation API

该实现使用 [Micrometer Observation API](https://docs.micrometer.io/micrometer/reference/observation.html) 来实现 `ChatModelListener`，通过添加以下依赖即可透明地生成指标和追踪：

Maven：
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-observation</artifactId>
</dependency>
```
Gradle：
```gradle
implementation 'dev.langchain4j:langchain4j-observation'
```

你需要按如下方式实例化 Observation 监听器……

#### 配置 ObservationChatModelListener bean

```java
@Configuration
public class ObservationConfig {

    @Bean
    public ObservationChatModelListener listener(ObservationRegistry observationRegistry, MeterRegistry meterRegistry) {
        return new ObservationChatModelListener(observationRegistry, meterRegistry);
    }
}
```

该依赖需要[上文所述的 SpringBoot Actuator 配置](spring-boot-integration.md#micrometer-actuator-配置)。

对于 SpringBoot 应用额外的可观测性需求，请参照：
[Building Your First Observed Application](https://spring.io/blog/2022/10/12/observability-with-spring-boot-3#building-your-first-observed-application)

关于 `langchain4j-observation` 库的更多详情，请查看[可观测性文档](observability.md#micrometer-observation-api)。


## 测试

- [客户支持智能体集成测试的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/customer-support-agent-example/src/test/java/dev/langchain4j/example/CustomerSupportAgentIT.java)

## 支持的版本

LangChain4j Spring Boot 集成要求 Java 17，同时支持：
- **Spring Boot 4**（4.0+）—— 使用带 `-spring-boot4-starter` 后缀的 starter
- **Spring Boot 3**（3.5+）—— 使用带 `-spring-boot-starter` 后缀的 starter，与 [Spring Boot OSS 支持策略](https://spring.io/projects/spring-boot#support) 保持一致

两个系列的 starter 一同发布并共享相同的版本号。请选择与你项目中 Spring Boot 版本匹配的那一组 starter。

## 示例
- [底层 Spring Boot 示例](https://github.com/langchain4j/langchain4j-examples/blob/main/spring-boot-example/src/main/java/dev/langchain4j/example/lowlevel/ChatModelController.java)，使用 [ChatModel API](chat-and-language-models.md)
- [高层 Spring Boot 示例](https://github.com/langchain4j/langchain4j-examples/blob/main/spring-boot-example/src/main/java/dev/langchain4j/example/aiservice/AssistantController.java)，使用 [AI 服务](ai-services.md)
- [使用 Spring Boot 的客户支持智能体示例](https://github.com/langchain4j/langchain4j-examples/blob/main/customer-support-agent-example/src/main/java/dev/langchain4j/example/CustomerSupportAgentApplication.java)
