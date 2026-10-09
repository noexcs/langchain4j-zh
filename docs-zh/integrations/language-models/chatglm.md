# ChatGLM

https://github.com/THUDM/ChatGLM-6B

ChatGLM 是由清华大学发布的一个开源双语对话语言模型。

对于 ChatGLM2、ChatGLM3 和 GLM4，它们的 API 与 OpenAI 兼容。你可以参考 `langchain4j-zhipu-ai` 或使用 `langchain4j-open-ai`。

## Maven 依赖
!!! note
   自 `1.0.0-alpha1` 起，`langchain4j-chatglm` 已迁移到 `langchain4j-community`，并更名为 `langchain4j-community-chatglm`。

`1.0.0-alpha1` 之前：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-chatglm</artifactId>
    <version>${previous version here}</version>
</dependency>
```

`1.0.0-alpha1` 及之后：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-chatglm</artifactId>
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

你可以使用以下代码实例化 `ChatGlmChatModel`：

```java
ChatModel model = ChatGlmChatModel.builder()
        .baseUrl(System.getenv("CHATGLM_BASE_URL"))
        .logRequests(true)
        .logResponses(true)
        .build();
```

现在你可以像普通的 `ChatModel` 一样使用它。

!!! note
   `ChatGlmChatModel` 不支持函数调用和结构化输出。见 [index](index.md)

## 示例

- [ChatGlmChatModelIT](https://github.com/langchain4j/langchain4j-community/blob/main/models/langchain4j-community-chatglm/src/test/java/dev/langchain4j/community/model/chatglm/ChatGlmChatModelIT.java)
