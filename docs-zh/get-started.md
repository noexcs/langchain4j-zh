# 入门指南

!!! note
    如果你正在使用 Quarkus，请参见[Quarkus 集成](tutorials/quarkus-integration.md)。

    如果你正在使用 Spring Boot，请参见[Spring Boot 集成](tutorials/spring-boot-integration.md)。

    如果你正在使用 Helidon，请参见[Helidon 集成](tutorials/helidon-integration.md)

LangChain4j 提供了与许多 [LLM 提供商](integrations/language-models/index.md)、
[嵌入/向量存储](integrations/embedding-stores/index.md) 等的集成。
每个集成都有自己的 Maven 依赖。

最低支持的 JDK 版本为 17。

作为示例，我们导入 OpenAI 依赖：

- 对于 Maven，在 `pom.xml` 中：
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai</artifactId>
    <version>1.22.0</version>
</dependency>
```

如果你希望使用高层 [AI 服务](tutorials/ai-services.md) API，还需要添加
以下依赖：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j</artifactId>
    <version>1.22.0</version>
</dependency>
```

- 对于 Gradle，在 `build.gradle` 中：
```groovy
implementation 'dev.langchain4j:langchain4j-open-ai:1.22.0'
implementation 'dev.langchain4j:langchain4j:1.22.0'
```

<details>
<summary>物料清单（BOM）</summary>

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>dev.langchain4j</groupId>
            <artifactId>langchain4j-bom</artifactId>
            <version>1.22.0</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

!!! note
    请注意，`langchain4j-bom` 始终包含所有 LangChain4j 模块的最新版本。

!!! note
    请注意，虽然 `langchain4j-bom` 的版本为 `1.22.0`，
    但许多模块的版本仍为 `1.22.0-beta32`，
    因此这些模块未来可能存在一些破坏性变更。
</details>

<details>
<summary>SNAPSHOT 依赖（最新功能）</summary>

如果你想在其正式发布前测试最新功能，
可以使用最新的 `SNAPSHOT` 依赖：
```xml
<repositories>
  <repository>
    <name>Central Portal Snapshots</name>
    <id>central-portal-snapshots</id>
    <url>https://central.sonatype.com/repository/maven-snapshots/</url>
    <releases>
      <enabled>false</enabled>
    </releases>
    <snapshots>
      <enabled>true</enabled>
    </snapshots>
  </repository>
</repositories>

<dependencies>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j</artifactId>
        <version>1.22.0-SNAPSHOT</version>
    </dependency>
</dependencies>
```
</details>

然后，导入你的 OpenAI API 密钥。
建议将 API 密钥存储在环境变量中，以降低公开暴露的风险。
```java
String apiKey = System.getenv("OPENAI_API_KEY");
```

设置好密钥后，让我们创建一个 `OpenAiChatModel` 实例：
```java
OpenAiChatModel model = OpenAiChatModel.builder()
    .apiKey(apiKey)
    .modelName("gpt-4o-mini")
    .build();
```
现在，是时候聊天了！
```java
String answer = model.chat("Say 'Hello World'");
System.out.println(answer); // Hello World
```