# 提示词重复

`langchain4j-community-prompt-repetition` 是一个可选的社区模块，为 LangChain4j 的两个集成点提供现成的提示词重复集成：

- AI 服务输入护栏
- RAG 查询转换

该模块受到论文 [Prompt Repetition Improves Non-Reasoning LLMs](https://arxiv.org/html/2512.14982v1) 的启发，该论文报告了其在一系列非推理类工作负载上的收益。在 LangChain4j 中，该模块通过框架原生组件暴露核心的重复输入转换功能，并为实际应用添加了保守的默认设置。

该模块处于实验阶段，其效果取决于工作负载。在大规模推广之前，请先在你自己的提示词、模型和任务上验证它。

## 它是什么

提示词重复按以下形式重写文本：

```text
Q -> Q\nQ
```

在 LangChain4j 中，这可以应用于两个不同的位置：

- 在非 RAG 的 AI 服务调用之前，使用 `PromptRepeatingInputGuardrail`
- 在高级 RAG 管道的检索之前，使用 `RepeatingQueryTransformer`

对于 RAG，重复应仅应用于检索查询，而不是发送给模型的最终增强提示词。

## Maven 依赖

如果你已经在使用社区模块，建议导入社区 BOM：

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>dev.langchain4j</groupId>
            <artifactId>langchain4j-community-bom</artifactId>
            <version>${latest version here}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>
```

然后添加提示词重复模块：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-prompt-repetition</artifactId>
</dependency>
```

你也可以直接声明该模块：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-prompt-repetition</artifactId>
    <version>${latest version here}</version>
</dependency>
```

## 组件

该模块提供三个主要 API：

- `PromptRepeatingInputGuardrail` 在调用模型之前重复符合条件的单文本用户输入
- `RepeatingQueryTransformer` 在高级 RAG 管道中重复检索查询
- `PromptRepetitionPolicy` 包含两个集成共用的重复规则

所有这些 API 都被标记为 `@Experimental`。

## 非 RAG 用法

对于非 RAG 的 AI 服务调用，将 `PromptRepeatingInputGuardrail` 附加到 `AiServices` 构建器上：

```java
PromptRepetitionPolicy policy = PromptRepetitionPolicy.builder()
        .mode(PromptRepetitionMode.AUTO)
        .maxChars(8_000)
        .build();

Assistant assistant = AiServices.builder(Assistant.class)
        .chatModel(chatModel)
        .inputGuardrails(new PromptRepeatingInputGuardrail(policy))
        .build();
```

如果你希望在模型调用之前重写用户输入，并且你操作的不是增强后的 RAG 提示词，这就是首选的集成点。

## RAG 用法

对于 RAG，只重复检索查询：

```java
PromptRepetitionPolicy policy = PromptRepetitionPolicy.builder()
        .mode(PromptRepetitionMode.AUTO)
        .maxChars(8_000)
        .build();

RetrievalAugmentor retrievalAugmentor = DefaultRetrievalAugmentor.builder()
        .queryTransformer(new RepeatingQueryTransformer(policy))
        .build();
```

这将转换保留在检索阶段内部，避免在检索内容已经注入之后重复最终提示词。

## 模式

`PromptRepetitionPolicy` 支持三种模式：

- `NEVER`：禁用重复
- `ALWAYS`：重复符合条件的输入
- `AUTO`：保守模式，跳过已经重复的文本、过长的输入以及看起来请求显式推理的提示词

`AUTO` 是评估时最安全的起点。

## 安全与约束

- `PromptRepeatingInputGuardrail` 只重写符合条件的单文本用户输入
- 它不打算作为多模态请求的主要集成点
- 默认情况下，当 RAG 增强已经发生时，护栏会跳过该请求
- 在 RAG 设置中，使用 `RepeatingQueryTransformer` 来重复检索查询，而不是重复最终的增强提示词
- 该模块处于实验阶段，因此 API 和行为可能在未来的版本中发生变化

## 何时使用

当你希望在 LangChain4j 中以现成的方式应用提示词重复时，请使用此模块；如果你想要的是一种通用的默认提示词策略，则不应使用它。

- 从 `PromptRepetitionMode.AUTO` 开始
- 优先用于非推理或低推理的工作负载
- 使用 A/B 测试在你自己的提示词、模型和任务上评估它
- 除非你有明确的理由放宽默认的安全约束，否则请保留它们
- 将改进视为取决于工作负载的，而不是有保证的
