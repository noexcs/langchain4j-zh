# 使用 Jackson 3

LangChain4j 在很多地方都会读写 JSON：与 LLM 提供商交换的请求和响应、AI 服务解析的结构化输出、你持久化的聊天记忆，等等。默认情况下，它使用 [Jackson 2](https://github.com/FasterXML/jackson) 来完成这些工作。关于 LangChain4j 如何使用 JSON 以及如何插入你自己的 mapper，请参阅 [JSON](json.md)。

如果你的应用使用的是 Jackson 3，你可以让 LangChain4j 改为使用它。

## 启用方式

添加一个依赖：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-jackson3</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

仅此而已，适用于所有模块（包括 `langchain4j-agentic`）。LangChain4j 通过 `ServiceLoader` 发现该模块，并让其 JSON 处理走 Jackson 3。无需任何配置，也没有需要调用的 API；移除该依赖后，一切恢复为 Jackson 2。

该功能由两个构件共同提供，上面的 `langchain4j-jackson3` 会同时引入这两个构件，因此除非你有特殊理由，否则应添加的就是它：

| 构件 | 覆盖范围 | 依赖 |
|---|---|---|
| `langchain4j-core-jackson3` | `langchain4j-core` 中的所有内容：提供商请求与响应、结构化输出、聊天记忆序列化、智能体状态 | `langchain4j-core` |
| `langchain4j-jackson3` | 上述内容，外加 `InMemoryEmbeddingStore` 持久化（位于 `langchain4j` 模块中） | `langchain4j-core-jackson3` 和 `langchain4j` |

只有当你的应用使用 `langchain4j-core` 和某个不带 `langchain4j` 模块的提供商时，才单独添加 `langchain4j-core-jackson3` - 例如直接构建模型的框架集成。将它与 `langchain4j-jackson3` 一起添加没有必要，但无害。

## 保持相同的行为

更换 JSON 库很容易无意间改变行为，因此该模块极力避免这种情况。Jackson 3 更改了若干默认值，其中几乎所有会影响 LangChain4j 读写内容的项都被恢复为 Jackson 2 的行为。少数有意保留的差异列在[有意保留的差异](#有意保留的差异)一节。

| 设置 | Jackson 3 默认值 | 本模块的处理 |
|---|---|---|
| `ALLOW_FINAL_FIELDS_AS_MUTATORS` | 禁用 | 启用 |
| `USE_GETTERS_AS_SETTERS` | 禁用 | 启用 |
| `SORT_PROPERTIES_ALPHABETICALLY` | 启用 | 禁用 |
| `FAIL_ON_TRAILING_TOKENS` | 启用 | 禁用 |
| `FAIL_ON_NULL_FOR_PRIMITIVES` | 启用 | 禁用 |
| `READ_ENUMS_USING_TO_STRING` | 启用 | 禁用：枚举通过 `name()` 读取 |
| `WRITE_ENUMS_USING_TO_STRING` | 启用 | 禁用：枚举通过 `name()` 写入 |
| `DETECT_PARAMETER_NAMES` | 启用 | 禁用，但结构化输出和工具参数除外（见下文） |
| `FAIL_ON_UNKNOWN_PROPERTIES` | 禁用 | 启用：目标类型中不存在的字段会导致结构化输出、工具参数、聊天记忆、智能体状态和已存储的向量存储失败；提供商响应仍会忽略未知字段 |
| `FAIL_ON_EMPTY_BEANS` | 禁用 | 启用：没有任何可写入内容的对象（例如字段为 private 且没有 getter 的对象）将报错，而不是以 `{}` 形式发送 |

其中第一项最为关键：没有它，final 集合字段将保持为空而不是被填充，而且不会有任何提示。

`DETECT_PARAMETER_NAMES` 只在代码使用 `-parameters` 编译时才有意义，Spring Boot 和 Quarkus 项目通常都是如此。对于结构化输出和工具参数，会使用构造器参数名——这与 Jackson 2 编解码器在 classpath 上存在 `jackson-module-parameter-names` 时的行为一致，而 Spring Boot 和 Quarkus 的 classpath 上恰好都有它：因此只有带参构造器的类（例如 Lombok 的 `@AllArgsConstructor` 类）也能被读取。聊天记忆、智能体状态和其他编解码器与 Jackson 2 一样，不使用参数名。

无论编译器设置如何，都可以显式指定构造器，方法是为其添加注解：

- 使用 `@JsonCreator(mode = JsonCreator.Mode.DELEGATING)` 通过单参数构造器读取 `"abc"` 这类纯值；
- 使用 `@JsonCreator`，并为每个参数添加 `@JsonProperty("name")`，通过带参构造器读取对象。

两种方式在两个版本的 Jackson 下都有效。

## 有意保留的差异

少数差异是有意保留的，因为恢复它们所带来的代价大于收益：

- **日期和时间以 ISO-8601 字符串形式写入。** `java.util.Date` 和 `Calendar` 会被写为 `"1970-01-01T00:00:00.000Z"`，而不是 epoch 毫秒。在 classpath 上存在 `jackson-datatype-jsr310` 时（Spring Boot 和 Quarkus 应用即是如此），Jackson 2 同样将 `Instant`、`OffsetDateTime` 和 `Duration` 写为数字；本模块则将它们写为 ISO-8601 字符串，LLM 对这种格式的理解可靠得多。对于 `Date`、`Instant` 和 `Duration`，数字形式的输入仍然可以被读取。
- **`java.time.Month` 写为从 1 开始的数字**（1 月为 `1`）。在存在 `jackson-datatype-jsr310` 时，Jackson 2 写为 `"JANUARY"`，并把数字读为从 0 开始的序号，因此 `1` 表示 `FEBRUARY`。两个版本都能读取名称形式。
- **枚举的 `""` 被读为 `null`**，与缺失值相同。这也适用于必填枚举：与缺失字段一样，`""` 会得到 `null` 而不是报错。Jackson 2 则会失败，但提供商确实会发送它 - 正是 OpenAI 兼容服务器对工具调用返回 `"type": ""` 这一情况发现了该问题 - 而且 LLM 也可能对可选枚举回答 `""`。对于对象、map 或列表，`""` 仍然会失败，与 Jackson 2 行为一致。
- **`private` 的单参数构造器不会被用于读取纯值。** Jackson 2 会使用它；在 Jackson 3 下，需要为其添加 `@JsonCreator(mode = JsonCreator.Mode.DELEGATING)` 注解。
- **对于结构化输出和工具参数，当类同时有无参构造器和带参构造器时，在代码以 `-parameters` 编译的情况下，会通过带参构造器创建实例。** Jackson 2 会先使用无参构造器，然后再设置字段。只有当该构造器除了赋值字段外还做其他事情时，这一差异才会产生影响。
- **类似 `xValue` 且 getter 为 `getXValue()` 的字段会被写为 `"xValue"`。** Jackson 2 会从 getter 推导出 `"xvalue"`：对结构化输出、工具结果和智能体状态，它会同时写入 `"xValue"` 和 `"xvalue"`；对提供商请求则只写入 `"xvalue"`。由 Jackson 2 以这种重复键写出的智能体状态，将无法被本模块读取。

**失败会带有 LangChain4j 类型。**
默认情况下，JSON 失败表现为包装了 Jackson 2 自身异常的 `RuntimeException` - 这意味着处理该失败的代码必须了解 Jackson 2。使用本模块后，JSON 读写失败会改为抛出 `JsonReadException` 或 `JsonWriteException`，二者都是 `LangChain4jException`，库自身的异常被保留为 cause。

这是有意的演进而非不一致：带类型的异常是 LangChain4j 在下一个大版本中的方向，在那之前 Jackson 2 的编解码器保持原样，以确保现有代码继续可用。如果你按 Jackson 类型捕获 JSON 失败，那么添加本模块时唯一需要重新审视的就是这一点：

```java
- } catch (JsonParseException e) {
+ } catch (JsonReadException e) {
```

捕获 `RuntimeException` 则两者皆可。

有两个地方会在没有 `catch` 块参与的情况下触及应用代码，因此在切换之前值得检查一下：

**工具参数错误处理程序。** 当模型生成的工具参数不是有效的 JSON 时，LangChain4j 会把失败交给你通过 `AiServices.toolArgumentsErrorHandler(...)` 注册的处理程序。在 Jackson 2 下该失败是 Jackson 自身的 `JsonParseException`；使用本模块后则是 `JsonReadException`。按类型分支的处理程序将不再匹配，而且不会有任何警告，因为处理程序仍会被调用，只是走上了另一个分支：

```java
AiServices.builder(Assistant.class)
    .toolArgumentsErrorHandler((error, context) -> {
-       if (error instanceof JsonParseException) {
+       if (error instanceof JsonReadException) {
            return ToolErrorHandlerResult.text("Please return valid JSON.");
        }
        throw error;
    })
```

如果你希望处理程序在两种环境下都能工作，可以按消息或按 `RuntimeException` 匹配。

**`OutputParsingException` 的 cause。** 当结构化输出无法解析时，LangChain4j 在两种情况下都会抛出 `OutputParsingException` - 该类型不变。变化的是它下面的异常，从 Jackson 2 的 `JsonProcessingException` 变为 Jackson 3 的 `StreamReadException`。检查 `getRootCause()` 的代码需要做同样的调整。

**已存储的数据仍然可读。** 由 Jackson 2 写出的聊天记忆和 `InMemoryEmbeddingStore` 文件可以被 Jackson 3 正确读取，而 Jackson 3 写出的内容与 Jackson 2 写出的完全一致（逐字节相同）。这一点有测试保障，因此会持续成立。

## 移除 Jackson 2

仅添加该模块本身不会移除 Jackson 2 - 它仍然作为普通的传递依赖存在，两者可以无限期共存。如果你希望把它移除，通常可以做到，因为本模块存在后，LangChain4j 不再加载任何 Jackson 2 类。

它能否真正被移除，取决于你使用了哪些模块：

| 模块 | 是否可以排除 Jackson 2？ |
|---|---|
| `langchain4j-core`、`langchain4j` | 可以 — 它们内置了 Jackson 2 编解码器，但那些只是回退方案，只要本模块在 classpath 上就永远不会被加载 |
| 提供商模块 — OpenAI、Anthropic、Mistral、Ollama、Gemini 及其他 | 可以 |
| 向量存储、网页搜索、代码执行 | 可以 |
| `langchain4j-agentic` | 可以 |
| `langchain4j-guardrails` | 不可以 - `JsonExtractorOutputGuardrail` 有意使用纯 Jackson 2 的 `ObjectMapper` 进行解析，以保证护栏保持原有的严格程度 |
| `langchain4j-mcp` | 不可以 — 其公共 API 中出现了 Jackson 的 `JsonNode`，因此该模块在所有路径上都会加载 Jackson 2 |
| `langchain4j-vespa` | 不可以 — 其 HTTP 客户端使用的是 Retrofit 自带的 Jackson 2 转换器 |
| 任何使用厂商 SDK 的 — AWS、Azure、Google | 不可以 — SDK 本身就依赖 Jackson 2 |

Maven 的 exclusions 只作用于其所声明的那个依赖，因此要写在你声明的**每一个** LangChain4j 依赖上，而不只是第一个：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j</artifactId>
    <version>1.22.0</version>
    <exclusions>
        <exclusion>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-databind</artifactId>
        </exclusion>
        <exclusion>
            <groupId>com.fasterxml.jackson.core</groupId>
            <artifactId>jackson-core</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<!-- and the same on langchain4j-open-ai, and on any other LangChain4j module you use -->
```

**不要**排除 `com.fasterxml.jackson.core:jackson-annotations`。它虽然保留 2.x 的坐标，但两个版本共享：Jackson 3 依赖它并读取其中的注解。

这一配置不只是"被认为可行"，它在每个 pull request 上都会被构建并运行：`integration-tests/integration-tests-jackson3` 就是按完全相同的方式组装的应用 - core、主模块、一个提供商、智能体以及本模块，整个依赖图中都排除了 Jackson 2 - 它的测试覆盖 AI 服务的结构化输出、工具调用、聊天记忆持久化、向量存储持久化和智能体状态持久化。如果其中任何一项开始需要 Jackson 2，这些测试就会因找不到类而失败。

如果你使用了 MCP、Vespa 或云 SDK，Jackson 2 会保留。但该 opt-in 仍然为 LangChain4j 自身序列化的所有内容提供了单一的 Jackson 3 代码路径。

## 如果你在编写提供商或 DTO

如果你要贡献线上（wire）类型，有两点需要了解。

**命名字规则应放在编解码器上，而不是类型上。** `@JsonNaming` 位于 Jackson 2 的 `databind` 包中，因此 Jackson 3 完全看不到它 — 字段名会悄无声息地变成 camelCase。改为在编解码器上设置命名规则：

```java
ProviderJson.codec(ProviderJsonSpec.builder()
        .propertyNaming(ProviderJsonSpec.PropertyNaming.SNAKE_CASE)
        .build());
```

如果单个字段需要不同的名称，`@JsonProperty("...")` 在两个版本下都有效，因为它来自两个版本共享的 `jackson-annotations` 构件。

**基于 builder 的 DTO 需要在其 builder 上提供 `@JsonCreator` 和字段可见性。** `@JsonDeserialize(builder = ...)` 也是 `databind` 注解，因此在 Jackson 3 下，DTO 改为通过接收 builder 的构造器上的 `@JsonCreator` 来构建。Jackson 3 通过写入 builder 的 private 字段来填充它，因此 builder 还需要 `@JsonAutoDetect(fieldVisibility = JsonAutoDetect.Visibility.ANY)`。缺少它时，响应能解析且不报错，但字段保持为 `null`。三处缺一不可。

**builder 方法是否会被执行取决于其上的注解。** 这是需要牢记的一点，因为它是静默的，而且规则并非你猜到的那样。Jackson 2 通过调用 builder 的 setter 再调用 `build()` 来填充。Jackson 3 只在 setter 带有属性标记时才调用它，否则直接写入字段，并且根本不会调用 `build()`：

| builder setter 上的注解 | Jackson 2 | Jackson 3 |
|---|---|---|
| `@JsonSetter("odd-name")`、`@JsonProperty`、单独的 `@JsonSetter` | 被调用 | 被调用 |
| 单独的 `@JsonAlias` | 被调用 | **不被调用** - 别名被忽略 |
| 无注解 | 被调用 | **不被调用** - 字段被直接写入 |
| `build()` | 被调用 | **绝不被调用** |

因此两个编解码器在同一个类型内可能逐属性地分道扬镳，这就是为什么值得用一条规则而非时刻保持警惕：

**把类型所保证的内容放在两条路径都会经过的地方。** 默认值应放在 builder 的字段上，而不是 `build()` 中。防御性拷贝或任何规范化逻辑应放在构造器中，而不是 setter 中。别名需要在 builder 的*字段*上以及 setter 上都标注 `@JsonAlias`。

以上每一条都曾在此出过问题：一个在 `build()` 中设置默认值的类型导致 mistral-ai 的所有工具调用丢失；只标注在 setter 上的 `@JsonAlias` 导致 vLLM、OpenRouter 和 Groq 的推理内容丢失；未加注解 setter 中的 `unmodifiableList(...)` 导致同一个响应在一个编解码器下返回可变列表，而在另一个下则不可变。它们都没有抛出任何异常。

支持该 opt-in 的模块会声明一个 `jackson3` Maven profile，它把 `langchain4j-jackson3` 放到该模块的测试 classpath 上，使其现有测试针对 Jackson 3 运行。CI 会在每个 pull request 上运行所有这些模块，你也可以用同样的方式运行单个模块：

```bash
mvn test -Pjackson3 -pl langchain4j-your-module
```

在相信结果之前，请确认该模块的 `pom.xml` 确实声明了这个 profile：Maven 会忽略所选模块未声明的 profile，因此上面的命令会在全部针对 Jackson 2 运行的情况下报告成功。添加 profile 是迁移模块工作的一部分。

该 profile 放到测试 classpath 上的是 `langchain4j-core-jackson3` 而不是 `langchain4j-jackson3`，因为后者依赖 `langchain4j` 模块，对于 `langchain4j` 模块本身所依赖的那些模块来说会造成循环依赖。需要完整构件的 `InMemoryEmbeddingStore` 持久化部分，由 `langchain4j-jackson3` 自身的测试以及 `integration-tests/integration-tests-jackson3` 覆盖。

`langchain4j-open-ai` 还包含 `OpenAiBuilderCreatorParityTest`，它把每个通过 builder 构建的基于 builder 的 DTO 与从 `{}` 解析出的同一 DTO 进行对比。这正是上面缺失 `build()` 调用所产生的差异，因此该测试一次性覆盖整个 OpenAI 线上模型，而不是逐字段检查。当基于 builder 的 DTO 缺少 `@JsonCreator` 或其 builder 缺少 `@JsonAutoDetect` 时，同一测试也会失败。

## 如果你接入自己的 JSON

使用 Jackson 3 并不需要了解本节 — 添加依赖即可。本节面向那些向 LangChain4j 提供自己配置好的 JSON mapper、而不是让它自行选择的框架，`langchain4j-jackson3` 自身就是这样做的。

LangChain4j 没有单一的 JSON 入口。它在下面每个位置都通过 `ServiceLoader` 请求编解码器，因此每个位置可以分别应答：

| 服务接口 | 决定 LangChain4j 如何读写 |
|---|---|
| `dev.langchain4j.spi.json.JsonCodecFactory` | 通用 JSON — AI 服务的结构化输出、模型的工具参数 |
| `dev.langchain4j.spi.json.ProviderJsonCodecFactory` | 与 LLM 提供商交换的请求和响应 |
| `dev.langchain4j.spi.json.StateJsonCodecFactory` | 类型无法事先确定、因此携带类型名称的状态 — 智能体状态 |
| `dev.langchain4j.spi.data.message.ChatMessageJsonCodecFactory` | 你持久化的聊天记忆 |
| `dev.langchain4j.spi.agent.tool.ToolSpecificationJsonCodecFactory` | `ToolSpecification.toJson()` 和 `ToolSpecification.fromJson(String)` |
| `dev.langchain4j.spi.prompt.structured.StructuredPromptFactory` | `@StructuredPrompt` 模板 |
| `dev.langchain4j.spi.store.embedding.inmemory.InMemoryEmbeddingStoreJsonCodecFactory` | `InMemoryEmbeddingStore.serializeToJson()` |

最后一个位于 `langchain4j` 中，其余位于 `langchain4j-core` 中。它们都是 `@Internal`，在这里意味着它们是给集成（而非应用）使用的，并且可能在小版本之间发生变化。

**框架自身的实现优先。** 如果已有某物提供了其中之一 - Quarkus 提供了四个 - 添加本模块不会将其取代。Jackson 3 的工厂声明的优先级低于其他任何实现，因此它们只应用于没有其他实现认领的服务。这一过程是静默的：不会记录警告，因为优先级决定了使用哪个实现。这意味着在这类框架上，opt-in 在设计上就是部分的：提供商流量和智能体状态切换到 Jackson 3，而框架自己负责的服务仍使用其自身的编解码器。如果你希望整个应用都运行在 Jackson 3 上，请移除框架的注册。

**要么全部实现，要么清楚自己漏掉了哪个。** 每个服务独立解析，没有注册实现的服务会回退到 Jackson 2。只应答一部分而不是另一部分不算错误，也不产生警告 — 它产生的应用是：例如聊天记忆由你的 mapper 写入，而智能体状态由另一个库写入。如果你有意省略某一个，得到的就是回退行为。

如果你已经集成了旧版本，其中两个值得再审视一下：`ProviderJsonCodecFactory` 和 `StateJsonCodecFactory` 是新增的，因此不了解它们的现有集成会继续工作，同时悄无声息地对提供商流量和智能体状态使用 Jackson 2。
