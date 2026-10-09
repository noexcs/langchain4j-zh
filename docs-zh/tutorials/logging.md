# 日志

LangChain4j 使用 [SLF4J](https://www.slf4j.org/) 进行日志记录，
允许你接入任何你喜欢的日志后端，
例如 [Logback](https://logback.qos.ch/) 或 [Log4j](https://logging.apache.org/log4j/2.x/index.html)。

## 纯 Java

在创建模型实例时设置 `.logRequests(true)` 和 `.logResponses(true)`，
即可启用对发往 LLM 的每个请求和响应的日志记录：
```java
OpenAiChatModel.builder()
    ...
    .logRequests(true)
    .logResponses(true)
    .build();
```

请确保你的依赖中包含一个 SLF4J 日志后端，例如 Logback：
```xml
<dependency>
    <groupId>ch.qos.logback</groupId>
    <artifactId>logback-classic</artifactId>
    <version>1.5.8</version>
</dependency>
```

## Quarkus

当使用 [Quarkus 集成](quarkus-integration.md) 时，
日志在 `application.properties` 文件中配置：

```properties
...
quarkus.langchain4j.openai.chat-model.log-requests = true
quarkus.langchain4j.openai.chat-model.log-responses = true
quarkus.log.console.enable = true
quarkus.log.file.enable = false
```

这些属性也可以在 Quarkus Dev UI 中设置和修改，
在开发模式（`mvn quarkus:dev`）下运行应用时。
此时 Dev UI 可通过 `http://localhost:8080/q/dev-ui` 访问。

## Spring Boot

当使用 [Spring Boot 集成](spring-boot-integration.md) 时，
日志在 `application.properties` 文件中配置：

```properties
...
langchain4j.open-ai.chat-model.log-requests = true
langchain4j.open-ai.chat-model.log-responses = true
logging.level.dev.langchain4j = DEBUG
```
