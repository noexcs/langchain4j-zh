# DashScope (Qwen)

[DashScope](https://dashscope.aliyun.com/) 是由 [Alibaba Cloud](https://www.alibabacloud.com/) 开发的平台。
它为模型可视化、监控和调试提供了接口，特别是在生产环境中处理 AI/ML
模型时。该平台允许用户可视化性能指标、跟踪模型行为，并
在部署周期早期识别潜在问题。

[Qwen](https://tongyi.aliyun.com/) 模型系列是由
[Alibaba Cloud](https://www.alibabacloud.com/) 开发的一系列生成式 AI 模型。Qwen 模型家族专为文本生成、
摘要、问答以及各种 NLP 任务而设计。

更多详细信息请参阅
[DashScope 文档](https://help.aliyun.com/zh/model-studio/getting-started/?spm=a2c4g.11186623.help-menu-2400256.d_0.6655453aLIyxGp)。LangChain4j 通过使用
[DashScope Java SDK](https://help.aliyun.com/zh/dashscope/java-sdk-best-practices?spm=a2c4g.11186623.0.0.272a1507Ne69ja) 与 DashScope 集成

## Maven 依赖

你可以在纯 Java 或 Spring Boot 应用程序中结合 LangChain4j 使用 DashScope。

### 纯 Java

!!! note
    自 `1.0.0-alpha1` 起，`langchain4j-dashscope` 已迁移至 `langchain4j-community` 并重命名为
    `langchain4j-community-dashscope`。

`1.0.0-alpha1` 之前：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-dashscope</artifactId>
    <version>${previous version here}</version>
</dependency>
```

`1.0.0-alpha1` 及之后：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-dashscope</artifactId>
    <version>${latest version here}</version>
</dependency>
```

### Spring Boot

!!! note
    自 `1.0.0-alpha1` 起，`langchain4j-dashscope-spring-boot-starter` 已迁移至 `langchain4j-community` 并重命名为
    `langchain4j-community-dashscope-spring-boot-starter`。

`1.0.0-alpha1` 之前：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-dashscope-spring-boot-starter</artifactId>
    <version>${previous version here}</version>
</dependency>
```

`1.0.0-alpha1` 及之后：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-dashscope-spring-boot-starter</artifactId>
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

## 可配置参数

`langchain4j-community-dashscope` 提供 4 个可用的模型：

- `QwenChatModel`
- `QwenStreamingChatModel`
- `QwenLanguageModel`
- `QwenStreamingLanguageModel`

`langchain4j-dashscope` 提供文本生成图像模型
- `WanxImageModel`

### `QwenChatModel`

初始化 `QwenChatModel` 时，它可以配置以下参数：

| Property          | Description                                                                                                                                        | Default Value                                                                                                                                    |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| baseUrl           | 要连接到的 URL。你可以使用 HTTP 或 websocket 连接到 DashScope                                                                                                                                  | [Text Inference](https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation) 和 [Multi-Modal](https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation) |
| apiKey            | API 密钥                                                                                                                                                                                   |                                                                                                                                                  |
| modelName         | 要使用的模型。                                                                                                                                                                             | qwen-plus                                                                                                                                        |
| topP              | 内核采样的概率阈值，控制模型生成文本的多样性。`top_p` 越高，生成的文本越多样，反之亦然。取值范围：(0, 1.0]。我们通常建议调整此项或 temperature，但不要同时调整两者。 |                                                                                                                                          |
| topK              | 生成过程中采样候选集的大小。                                                                                                                                                                 |                                                                                                                                                  |
| enableSearch      | 模型生成文本时是否使用互联网搜索结果作为参考。                                                                                                                                              |                                                                                                                                                  |
| seed              | 设置 seed 参数将使文本生成过程更具确定性，通常用于使结果保持一致。                                                                                                                             |                                                                                                                                                  |
| repetitionPenalty | 模型生成过程中连续序列中的重复。增加 `repetition_penalty` 会减少模型生成中的重复，1.0 表示无惩罚。取值范围：(0, +inf)                                                                       |                                                                                                                                                  |
| temperature       | 采样温度，控制模型生成文本的多样性。温度越高，生成的文本越多样，反之亦然。取值范围：[0, 2)                                                                                                     |                                                                                                                                                  |
| stops             | 通过 stop 参数，当文本即将包含指定字符串或 token_id 时，模型会自动停止生成文本。                                                                                                            |                                                                                                                                                  |
| maxTokens         | 本次请求返回的最大 token 数。                                                                                                                                                              |                                                                                                                                                  |
| listeners         | 用于监听请求、响应和错误的监听器。                                                                                                                                                         |                                                                                                                                                  |

### `QwenStreamingChatModel`

与 `QwenChatModel` 相同

### `QwenLanguageModel`

与 `QwenChatModel` 相同，除了 `listeners`。

### `QwenStreamingLanguageModel`

与 `QwenChatModel` 相同，除了 `listeners`。

## 示例

### 纯 Java

你可以使用以下代码初始化 `QwenChatModel`：

```java
ChatModel qwenModel = QwenChatModel.builder()
                    .apiKey("You API key here")
                    .modelName("qwen-max")
                    .build();
```

或者针对其他参数进行更多自定义：

```java
ChatModel qwenModel = QwenChatModel.builder()
                    .apiKey("You API key here")
                    .modelName("qwen-max")
                    .enableSearch(true)
                    .temperature(0.7)
                    .maxTokens(4096)
                    .stops(List.of("Hello"))
                    .build();
```

如何调用文生图模型：

```java
WanxImageModel wanxImageModel = WanxImageModel.builder()
                    .modelName("wanx2.1-t2i-plus") 
                    .apiKey("阿里云百炼apikey")     
                    .build();
Response<Image> response = wanxImageModel.generate("美女");
System.out.println(response.content().url());

```

### Spring Boot

引入 `langchain4j-community-dashscope-spring-boot-starter` 依赖后，你可以使用以下配置简单地注册 `QwenChatModel` bean：

```properties
langchain4j.community.dashscope.chat-model.api-key=<You API Key here>
langchain4j.community.dashscope.chat-model.model-name=qwen-max
# The properties are the same as `QwenChatModel`
# e.g.
# langchain4j.community.dashscope.chat-model.temperature=0.7
# langchain4j.community.dashscope.chat-model.max-tokens=4096
```

### 更多示例

你可以在 [LangChain4j Community](https://github.com/langchain4j/langchain4j-community/blob/main/models/langchain4j-community-dashscope/src/test/java/dev/langchain4j/community/model/dashscope) 中查看更详细的示例
