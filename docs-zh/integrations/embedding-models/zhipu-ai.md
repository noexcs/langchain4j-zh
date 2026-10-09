# Zhipu AI

[ZhiPu AI](https://www.zhipuai.cn/) 是一个提供模型服务的平台，包括文本生成、文本嵌入、
图像生成等。有关更多详细信息，请参阅 [ZhiPu AI Open Platform](https://open.bigmodel.cn/)。
LangChain4j 通过使用 [HTTP 端点](https://bigmodel.cn/dev/api/normal-model/glm-4) 与 ZhiPu AI 集成。我们正在
考虑将其从 HTTP 端点迁移到官方 SDK，并感谢任何帮助！

## Maven 依赖

你可以在纯 Java 或 Spring Boot 应用程序中通过 LangChain4j 使用 ZhiPu AI。

### 纯 Java

!!! note
   自 `1.0.0-alpha1` 起，`langchain4j-zhipu-ai` 已迁移到 `langchain4j-community`，并更名为
   `langchain4j-community-zhipu-ai`

`1.0.0-alpha1` 之前：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-zhipu-ai</artifactId>
    <version>${previous version here}</version>
</dependency>
```

`1.0.0-alpha1` 及之后：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-zhipu-ai</artifactId>
    <version>${latest version here}</version>
</dependency>
```

或者，你可以使用 BOM 来一致地管理依赖：

```xml

<dependencyManagement>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-community-bom</artifactId>
        <version>${latest version here}</version>
        <type>pom</type>
        <scope>import</scope>
    </dependency>
</dependencyManagement>
```

## API

- `ZhipuAiEmbeddingModel`


## 示例

- [ZhipuAiEmbeddingModelIT](https://github.com/langchain4j/langchain4j-community/blob/main/models/langchain4j-community-zhipu-ai/src/test/java/dev/langchain4j/community/model/zhipu/ZhipuAiEmbeddingModelIT.java)
