# 结构化输出

!!! note
    "Structured Outputs"（结构化输出）这一术语被重载使用，可能指以下两种含义：
    - LLM 以结构化格式生成输出的一般能力（本页介绍的就是这个）
    - OpenAI 的 [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) 功能，
    该功能同时适用于响应格式和工具（函数调用）。

许多 LLM 和 LLM 提供商支持以结构化格式（通常是 JSON）生成输出。
这些输出可以轻松地映射为 Java 对象，并在应用程序的其他部分中使用。

例如，假设我们有一个 `Person` 类：
```java
record Person(String name, int age, double height, boolean married) {
}
```
我们的目标是从描述一个虚构角色的非结构化文本中提取一个 `Person` 对象：
```
Eldwin Brightblade is 412 years old and serves as court wizard in the kingdom of Aelyria.
He stands 1.65 meters tall and is known for his flowing white beard.
Currently unmarried, he devotes his time to studying ancient runes.
```

目前，根据 LLM 和 LLM 提供商的不同，有三种方式可以实现这一点
（按可靠性从高到低排列）：
- [JSON Schema](structured-outputs.md#json-schema)
- [提示词 + JSON 模式](structured-outputs.md#提示词-json-模式)
- [提示词](structured-outputs.md#提示词)


## JSON Schema
一些 LLM 提供商（目前是 Amazon Bedrock、Azure OpenAI、Google AI Gemini、Mistral、Ollama 和 OpenAI）允许
为期望的输出指定 [JSON schema](https://json-schema.org/overview/what-is-jsonschema)。
你可以在[这里](../integrations/language-models/index.md)的 "JSON Schema" 列中查看所有受支持的 LLM 提供商。

当请求中指定了 JSON schema 时，LLM 将生成遵循该 schema 的输出。

!!! note
    请注意，JSON schema 是在发给 LLM 提供商 API 的请求的一个专用属性中指定的，
    无需在提示词（例如系统消息或用户消息）中包含任何自由格式的说明。

LangChain4j 在底层的 `ChatModel` API
和高层的 AI 服务 API 中都支持 JSON Schema 功能。

### 使用 JSON Schema 配合 `ChatModel`

在底层的 `ChatModel` API 中，创建 `ChatRequest` 时可以使用
与 LLM 提供商无关的 `ResponseFormat` 和 `JsonSchema` 来指定 JSON schema：
```java
ResponseFormat responseFormat = ResponseFormat.builder()
        .type(JSON) // type can be either TEXT (default) or JSON
        .jsonSchema(JsonSchema.builder()
                .name("Person") // OpenAI requires specifying the name for the schema
                .rootElement(JsonObjectSchema.builder() // see [1] below
                        .addStringProperty("name")
                        .addIntegerProperty("age")
                        .addNumberProperty("height")
                        .addBooleanProperty("married")
                        .required("name", "age", "height", "married") // see [2] below
                        .build())
                .build())
        .build();

UserMessage userMessage = UserMessage.from("""
        Eldwin Brightblade is 412 years old and serves as court wizard in the kingdom of Aelyria.
        He stands 1.65 meters tall and is known for his flowing white beard.
        Currently unmarried, he devotes his time to studying ancient runes.
        """);

ChatRequest chatRequest = ChatRequest.builder()
        .responseFormat(responseFormat)
        .messages(userMessage)
        .build();

ChatModel chatModel = OpenAiChatModel.builder()
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4o-mini")
        .logRequests(true)
        .logResponses(true)
        .build();
// OR
ChatModel chatModel = AzureOpenAiChatModel.builder()
        .endpoint(System.getenv("AZURE_OPENAI_URL"))
        .apiKey(System.getenv("AZURE_OPENAI_API_KEY"))
        .deploymentName("gpt-4o-mini")
        .logRequestsAndResponses(true)
        .build();
// OR
ChatModel chatModel = GoogleAiGeminiChatModel.builder()
        .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
        .modelName("gemini-1.5-flash")
        .logRequestsAndResponses(true)
        .build();
// OR
ChatModel chatModel = OllamaChatModel.builder()
        .baseUrl("http://localhost:11434")
        .modelName("llama3.1")
        .logRequests(true)
        .logResponses(true)
        .build();
// OR
ChatModel chatModel = MistralAiChatModel.builder()
        .apiKey(System.getenv("MISTRAL_AI_API_KEY"))
        .modelName("mistral-small-latest")
        .logRequests(true)
        .logResponses(true)
        .build();
// OR
ChatModel chatModel = WatsonxChatModel.builder()
        .baseUrl(System.getenv("WATSONX_URL"))
        .projectId(System.getenv("WATSONX_PROJECT_ID"))
        .apiKey(System.getenv("WATSONX_API_KEY"))
        .modelName("ibm/granite-4-h-small")
        .logRequests(true)
        .logResponses(true)
        .build();
// OR
ChatModel chatModel = BedrockChatModel.builder()
        .modelId("us.anthropic.claude-haiku-4-5-20251001-v1:0")
        .logRequests(true)
        .logResponses(true)
        .build();

ChatResponse chatResponse = chatModel.chat(chatRequest);

String output = chatResponse.aiMessage().text();
System.out.println(output); // {"name":"Eldwin Brightblade","age":412,"height":1.65,"married":false}

Person person = new ObjectMapper().readValue(output, Person.class);
System.out.println(person); // Person[name=Eldwin Brightblade, age=412, height=1.65, married=false]
```
说明：
- [1] - 大多数情况下，根元素必须是 `JsonObjectSchema` 类型，
不过：
  - Amazon Bedrock、Azure OpenAI、Mistral、Ollama、OpenAI 和 OpenAI Official 也允许将 `JsonRawSchema` 作为根元素
  - Gemini 还允许将 `JsonEnumSchema` 和 `JsonArraySchema` 作为根元素
- [2] - 必填属性必须显式指定；否则，它们将被视为可选的。

JSON schema 的结构使用 `JsonSchemaElement` 接口定义，
具有以下子类型：
- `JsonObjectSchema` - 用于对象类型。
- `JsonStringSchema` - 用于 `String`、`char`/`Character` 类型。
- `JsonIntegerSchema` - 用于 `int`/`Integer`、`long`/`Long`、`BigInteger` 类型。
- `JsonNumberSchema` - 用于 `float`/`Float`、`double`/`Double`、`BigDecimal` 类型。
- `JsonBooleanSchema` - 用于 `boolean`/`Boolean` 类型。
- `JsonEnumSchema` - 用于 `enum` 类型。
- `JsonArraySchema` - 用于数组和集合（例如 `List`、`Set`）。
- `JsonReferenceSchema` - 用于支持递归（例如 `Person` 有一个 `Set<Person> children` 字段）。
- `JsonAnyOfSchema` - 用于支持多态（例如 `Shape` 可以是 `Circle` 或 `Rectangle`）。
- `JsonNullSchema` - 用于支持可空类型。
- `JsonRawSchema` - 用于使用你自己完整定义的 JSON schema。

#### `JsonObjectSchema`

`JsonObjectSchema` 表示一个带有嵌套属性的对象。
它通常是 `JsonSchema` 的根元素。

有几种方法可以向 `JsonObjectSchema` 添加属性：
1. 可以使用 `properties(Map<String, JsonSchemaElement> properties)` 方法一次性添加所有属性：
```java
JsonSchemaElement citySchema = JsonStringSchema.builder()
        .description("The city for which the weather forecast should be returned")
        .build();

JsonSchemaElement temperatureUnitSchema = JsonEnumSchema.builder()
        .enumValues("CELSIUS", "FAHRENHEIT")
        .build();

Map<String, JsonSchemaElement> properties = Map.of(
        "city", citySchema,
        "temperatureUnit", temperatureUnitSchema
);

JsonSchemaElement rootElement = JsonObjectSchema.builder()
        .addProperties(properties)
        .required("city") // required properties should be specified explicitly
        .build();
```

2. 可以使用 `addProperty(String name, JsonSchemaElement jsonSchemaElement)` 方法逐个添加属性：
```java
JsonSchemaElement rootElement = JsonObjectSchema.builder()
        .addProperty("city", citySchema)
        .addProperty("temperatureUnit", temperatureUnitSchema)
        .required("city")
        .build();
```

3. 可以使用其中一个 `add{Type}Property(String name)` 或 `add{Type}Property(String name, String description)` 方法逐个添加属性：
```java
JsonSchemaElement rootElement = JsonObjectSchema.builder()
        .addStringProperty("city", "The city for which the weather forecast should be returned")
        .addEnumProperty("temperatureUnit", List.of("CELSIUS", "FAHRENHEIT"))
        .required("city")
        .build();
```

更多详细信息，请参阅
[JsonObjectSchema](https://github.com/langchain4j/langchain4j/blob/main/langchain4j-core/src/main/java/dev/langchain4j/model/chat/request/json/JsonObjectSchema.java) 的 Javadoc。

#### `JsonStringSchema`

创建 `JsonStringSchema` 的示例：
```java
JsonSchemaElement stringSchema = JsonStringSchema.builder()
        .description("The name of the person")
        .build();
```

#### `JsonIntegerSchema`

创建 `JsonIntegerSchema` 的示例：
```java
JsonSchemaElement integerSchema = JsonIntegerSchema.builder()
        .description("The age of the person")
        .build();
```

#### `JsonNumberSchema`

创建 `JsonNumberSchema` 的示例：
```java
JsonSchemaElement numberSchema = JsonNumberSchema.builder()
        .description("The height of the person")
        .build();
```

#### `JsonBooleanSchema`

创建 `JsonBooleanSchema` 的示例：
```java
JsonSchemaElement booleanSchema = JsonBooleanSchema.builder()
        .description("Is the person married?")
        .build();
```

#### `JsonEnumSchema`

创建 `JsonEnumSchema` 的示例：
```java
JsonSchemaElement enumSchema = JsonEnumSchema.builder()
        .description("Marital status of the person")
        .enumValues(List.of("SINGLE", "MARRIED", "DIVORCED"))
        .build();
```

#### `JsonArraySchema`

创建 `JsonArraySchema` 以定义字符串数组的示例：
```java
JsonSchemaElement itemSchema = JsonStringSchema.builder()
        .description("The name of the person")
        .build();

JsonSchemaElement arraySchema = JsonArraySchema.builder()
        .description("All names of the people found in the text")
        .items(itemSchema)
        .build();
```

#### `JsonReferenceSchema`

`JsonReferenceSchema` 可用于支持递归：
```java
String reference = "person"; // reference should be unique withing the schema

JsonObjectSchema jsonObjectSchema = JsonObjectSchema.builder()
        .addStringProperty("name")
        .addProperty("children", JsonArraySchema.builder()
                .items(JsonReferenceSchema.builder()
                        .reference(reference)
                        .build())
                .build())
        .required("name", "children")
        .definitions(Map.of(reference, JsonObjectSchema.builder()
                .addStringProperty("name")
                .addProperty("children", JsonArraySchema.builder()
                        .items(JsonReferenceSchema.builder()
                                .reference(reference)
                                .build())
                        .build())
                .required("name", "children")
                .build()))
        .build();
```

!!! note
    `JsonReferenceSchema` 目前仅由 Azure OpenAI、Mistral 和 OpenAI 支持。

#### `JsonAnyOfSchema`

`JsonAnyOfSchema` 可用于支持多态：
```java
JsonSchemaElement circleSchema = JsonObjectSchema.builder()
        .addNumberProperty("radius")
        .build();

JsonSchemaElement rectangleSchema = JsonObjectSchema.builder()
        .addNumberProperty("width")
        .addNumberProperty("height")
        .build();

JsonSchemaElement shapeSchema = JsonAnyOfSchema.builder()
        .anyOf(circleSchema, rectangleSchema)
        .build();

JsonSchema jsonSchema = JsonSchema.builder()
        .name("Shapes")
        .rootElement(JsonObjectSchema.builder()
                .addProperty("shapes", JsonArraySchema.builder()
                        .items(shapeSchema)
                        .build())
                .required(List.of("shapes"))
                .build())
        .build();

ResponseFormat responseFormat = ResponseFormat.builder()
        .type(ResponseFormatType.JSON)
        .jsonSchema(jsonSchema)
        .build();

UserMessage userMessage = UserMessage.from("""
        Extract information from the following text:
        1. A circle with a radius of 5
        2. A rectangle with a width of 10 and a height of 20
        """);

ChatRequest chatRequest = ChatRequest.builder()
        .messages(userMessage)
        .responseFormat(responseFormat)
        .build();

ChatResponse chatResponse = model.chat(chatRequest);

System.out.println(chatResponse.aiMessage().text()); // {"shapes":[{"radius":5},{"width":10,"height":20}]}
```

!!! note
    `JsonAnyOfSchema` 目前仅由 OpenAI、Azure OpenAI 和 Google AI Gemini 支持。

#### `JsonRawSchema`

从现有 schema 字符串创建 `JsonRawSchema` 的示例：

```java
var rawSchema = """
{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "city": {
            "type": "string"
        }
    },
    "required": ["city"],
    "additionalProperties": false
}
""";

JsonRawSchema schema = JsonRawSchema.from(rawSchema);
```

!!! note
    `JsonRawSchema` 目前仅由 Amazon Bedrock、Azure OpenAI、Mistral、Ollama、OpenAI、OpenAI Official 和 Google AI Gemini 支持。
    对于 Google AI Gemini，请参见 [Response JSON Schema](../integrations/language-models/google-ai-gemini.md#响应格式-响应-schema) 中的示例。


#### 添加描述

除 `JsonReferenceSchema` 外，所有 `JsonSchemaElement` 子类型都有一个 `description` 属性。
如果 LLM 未提供期望的输出，可以提供描述，
以便向 LLM 提供更多说明和正确输出的示例，例如：
```java
JsonSchemaElement stringSchema = JsonStringSchema.builder()
        .description("The name of the person, for example: John Doe")
        .build();
```

#### 限制

将 JSON Schema 与 `ChatModel` 一起使用时，存在一些限制：
- 它仅适用于受支持的 Amazon Bedrock、Azure OpenAI、Google AI Gemini、Mistral、Ollama 和 OpenAI 模型。
- 对于 OpenAI，它目前还不能在[流式模式](ai-services.md#流式)下工作。
对于 Google AI Gemini、Mistral 和 Ollama，可以在创建/构建模型时通过 `responseSchema(...)` 指定 JSON Schema。
- `JsonReferenceSchema` 和 `JsonAnyOfSchema` 目前仅由 Azure OpenAI、Mistral 和 OpenAI 支持。


### 使用 JSON Schema 配合 AI 服务

使用 [AI 服务](ai-services.md) 时，可以更轻松、用更少的代码实现同样的效果：
```java
interface PersonExtractor {
    
    Person extractPersonFrom(String text);
}

ChatModel chatModel = OpenAiChatModel.builder() // see [1] below
        .apiKey(System.getenv("OPENAI_API_KEY"))
        .modelName("gpt-4o-mini")
        .supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA) // see [2] below
        .strictJsonSchema(true) // see [2] below
        .logRequests(true)
        .logResponses(true)
        .build();
// OR
ChatModel chatModel = AzureOpenAiChatModel.builder() // see [1] below
        .endpoint(System.getenv("AZURE_OPENAI_URL"))
        .apiKey(System.getenv("AZURE_OPENAI_API_KEY"))
        .deploymentName("gpt-4o-mini")
        .strictJsonSchema(true)
        .supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA) // see [3] below
        .logRequestsAndResponses(true)
        .build();
// OR
ChatModel chatModel = GoogleAiGeminiChatModel.builder() // see [1] below
        .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
        .modelName("gemini-1.5-flash")
        .supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA) // see [4] below
        .logRequestsAndResponses(true)
        .build();
// OR
ChatModel chatModel = OllamaChatModel.builder() // see [1] below
        .baseUrl("http://localhost:11434")
        .modelName("llama3.1")
        .supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA) // see [5] below
        .logRequests(true)
        .logResponses(true)
        .build();
// OR
ChatModel chatModel = MistralAiChatModel.builder()
         .apiKey(System.getenv("MISTRAL_AI_API_KEY"))
         .modelName("mistral-small-latest")
         .supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA) // see [6] below
         .strictJsonSchema(true) // see [6] below
         .logRequests(true)
         .logResponses(true)
         .build();
// OR
ChatModel chatModel = WatsonxChatModel.builder()
        .baseUrl(System.getenv("WATSONX_URL"))
        .projectId(System.getenv("WATSONX_PROJECT_ID"))
        .apiKey(System.getenv("WATSONX_API_KEY"))
        .modelName("ibm/granite-4-h-small")
        .supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA) // see [7] below
        .logRequests(true)
        .logResponses(true)
        .build();
// OR
ChatModel chatModel = BedrockChatModel.builder()
        .modelId("us.anthropic.claude-haiku-4-5-20251001-v1:0")
        .supportedCapabilities(RESPONSE_FORMAT_JSON_SCHEMA) // see [8] below
        .logRequests(true)
        .logResponses(true)
        .build();

PersonExtractor personExtractor = AiServices.create(PersonExtractor.class, chatModel); // see [1] below

String text = """
        Eldwin Brightblade is 412 years old and serves as court wizard in the kingdom of Aelyria.
        He stands 1.65 meters tall and is known for his flowing white beard.
        Currently unmarried, he devotes his time to studying ancient runes.
        """;

Person person = personExtractor.extractPersonFrom(text);

System.out.println(person); // Person[name=Eldwin Brightblade, age=412, height=1.65, married=false]
```
说明：
- [1] - 在 Quarkus 或 Spring Boot 应用程序中，无需显式创建 `ChatModel` 和 AI 服务，
因为这些 bean 会自动创建。更多信息：
[Quarkus](https://docs.quarkiverse.io/quarkus-langchain4j/dev/ai-services.html)，
[Spring Boot](https://docs.langchain4j.dev/tutorials/spring-boot-integration#spring-boot-starter-for-declarative-ai-services)。
- [2] - 对于 OpenAI，这是启用 JSON Schema 功能所必需的，更多详细信息请参见[这里](../integrations/language-models/open-ai.md#response-format-的结构化输出)。
- [3] - 对于 [Azure OpenAI](../integrations/language-models/azure-open-ai.md)，这是启用 JSON Schema 功能所必需的。
- [4] - 对于 [Google AI Gemini](../integrations/language-models/google-ai-gemini.md)，这是启用 JSON Schema 功能所必需的。
- [5] - 对于 [Ollama](../integrations/language-models/ollama.md)，这是启用 JSON Schema 功能所必需的。
- [6] - 对于 [Mistral](../integrations/language-models/mistral-ai.md)，这是启用 JSON Schema 功能所必需的。
- [7] - 对于 [watsonx.ai](../integrations/language-models/watsonx.md)，这是启用 JSON Schema 功能所必需的。
- [8] - 对于 [Amazon Bedrock](../integrations/language-models/amazon-bedrock.md)，这是启用 JSON Schema 功能所必需的。

当满足以下所有条件时：
- AI 服务方法返回一个 POJO
- 所使用的 `ChatModel` [支持](https://docs.langchain4j.dev/integrations/language-models/) JSON Schema 功能
- 所使用的 `ChatModel` 已启用 JSON Schema 功能

则会根据指定的返回类型自动生成带有 `JsonSchema` 的 `ResponseFormat`。

!!! note
    配置 `ChatModel` 时，请确保显式启用 JSON Schema 功能，
    因为它默认是禁用的。

生成的 `JsonSchema` 的 `name` 是返回类型的简单名称（`getClass().getSimpleName()`），
在本例中为："Person"。

当 LLM 响应后，输出会被解析为一个对象，并从 AI 服务方法返回。

你可以在[这里](https://github.com/langchain4j/langchain4j/blob/main/langchain4j/src/test/java/dev/langchain4j/service/AiServicesWithJsonSchemaIT.java)
和[这里](https://github.com/langchain4j/langchain4j/blob/main/langchain4j/src/test/java/dev/langchain4j/service/AiServicesWithJsonSchemaWithDescriptionsIT.java)
找到许多受支持用例的示例。

#### 必填与可选

默认情况下，生成的 `JsonSchema` 中的所有字段和子字段都被视为**_可选的_**。
这是因为 LLM 倾向于产生幻觉，当它们缺乏足够信息时，
会用合成数据填充字段（例如，在缺少姓名时使用 "John Doe"）。

!!! note
    请注意，原始类型（例如 `int`、`boolean` 等）的可选字段
    如果 LLM 未为它们提供值，
    将被初始化为默认值（例如 `int` 为 `0`，`boolean` 为 `false` 等）。

!!! note
    请注意，即使在启用严格模式（`strictJsonSchema(true)`）时，
    可选的 `enum` 字段仍可能被填充幻觉值。

若要使某个字段变为必填，可以用 `@JsonProperty(required = true)` 对其进行注解：
```java
record Person(@JsonProperty(required = true) String name, String surname) {
}

interface PersonExtractor {
    
    Person extractPersonFrom(String text);
}
```

!!! note
    请注意，当与[工具](tools.md)一起使用时，
    所有字段和子字段默认都被视为**_必填的_**。

#### 添加描述

如果 LLM 未提供期望的输出，可以用 `@Description` 对类和字段进行注解，
以便向 LLM 提供更多说明和正确输出的示例，例如：
```java
@Description("a person")
record Person(@Description("person's first and last name, for example: John Doe") String name,
              @Description("person's age, for example: 42") int age,
              @Description("person's height in meters, for example: 1.78") double height,
              @Description("is person married or not, for example: false") boolean married) {
}
```

!!! note
    请注意，放置在 `enum` 值上的 `@Description` 是**_无效的_**，并且**_不会_**包含
    在生成的 JSON schema 中：
    ```java
    enum Priority {

        @Description("Critical issues such as payment gateway failures or security breaches.") // this is ignored
        CRITICAL,
        
        @Description("High-priority issues like major feature malfunctions or widespread outages.") // this is ignored
        HIGH,
        
        @Description("Low-priority issues such as minor bugs or cosmetic problems.") // this is ignored
        LOW
    }
    ```

#### 多态类型

AI 服务方法可以返回多态类型——一种其具体子类型
由 LLM 在运行时决定的基础类型。支持两种形式：

- **Sealed 接口和 sealed 类** — 无需注解；子类型通过
  `Class.getPermittedSubclasses()` 发现。
- **普通抽象类和接口** — 必须使用 Jackson 的 `@JsonSubTypes`
  显式声明其子类型。

多态返回类型适用于类型本身、集合（`List<T>`、`Set<T>`）、
嵌套在其他 POJO 内部的字段，以及子类型将基础类型作为字段包含的递归层级（例如，
`ExpressionNode` 是 sealed 基类时的 `BinaryOp(left: ExpressionNode, right: ExpressionNode)`）。

每个子类型都会添加一个判别属性（默认为 `"type"`），以便 LLM
能够说明它生成的是哪个具体类型；解析器随后会自动分发到
正确的子类型。

**Sealed 接口和类 — 无需注解：**

```java
sealed interface Animal permits Dog, Cat {}

record Dog(String name, String breed) implements Animal {}

record Cat(String name, boolean indoor) implements Animal {}

interface AnimalExtractor {

    Animal extractAnimalFrom(String text);
}
```

LLM 看到的 schema 中，`Dog` 和 `Cat` 之上有一个 `anyOf`，每个都被约束为在
`type` 属性中输出其简单类名。给定：

```
Rex is a Labrador.
```

LLM 会输出 `{"value":{"type":"Dog","name":"Rex","breed":"Labrador"}}`，它会被解析
回一个 `Dog` 实例。

!!! note
    由于许多 LLM 提供商不支持根级带有 `anyOf` 的 JSON schema，
    该 schema 会将多态选择包装在一个 `value` 属性下（对于集合则为 `values`）。
    该包装器是一个实现细节——你的 AI 服务方法仍然返回未包装的子类型。

**多态类型的集合：**

```java
interface AnimalsExtractor {

    List<Animal> extractAnimalsFrom(String text);
}
```

**另一个 POJO 内部的多态字段：**

```java
record Owner(String name, Animal pet) {}

interface OwnerExtractor {

    Owner extractOwnerFrom(String text);
}
```

**Jackson `@JsonSubTypes` / `@JsonTypeInfo`** 也受到支持，并允许将线上
名称与 Java 类名解耦：

```java
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "kind")
@JsonSubTypes({
    @JsonSubTypes.Type(value = Square.class, name = "square"),
    @JsonSubTypes.Type(value = Circle.class, name = "circle")
})
interface Shape {}

class Square implements Shape { double side; }

class Circle implements Shape { double radius; }
```

判别值的解析顺序：
1. 基础类型上的 `@JsonSubTypes.Type(name = "...")`
2. 子类型上的 `@JsonTypeName`
3. `Class.getSimpleName()`（默认值）

因此，当你不想在基类上声明时，`@JsonTypeName` 是设置线上名称的便捷方式：

```java
sealed interface Bird permits Eagle, Sparrow {}

@JsonTypeName("bird_eagle")
record Eagle(double wingspanMeters) implements Bird {}

@JsonTypeName("bird_sparrow")
record Sparrow(boolean migratory) implements Bird {}
```

LLM 看到的判别值将是 `"bird_eagle"` / `"bird_sparrow"`，而不是简单
类名（`"Eagle"`/`"Sparrow"`）。

**受支持的 `@JsonTypeInfo` 配置：**

| 属性 | 受支持的值 |
|---|---|
| `use` | `Id.NAME`、`Id.SIMPLE_NAME` |
| `include` | `As.PROPERTY`（默认）、`As.EXISTING_PROPERTY` |
| `property` | 任意显式值；为空时默认为 `"@type"` |
| `defaultImpl` | 任意具体子类 — 在 LLM 的判别值缺失或未知时使用 |
| `visible` | `true` 保留反序列化后的 bean 上的判别字段（并绕过字段冲突检查） |

其他任何配置（例如 `Id.CLASS`、`As.WRAPPER_OBJECT`）都会在 schema 生成时
被 `UnsupportedFeatureException` 拒绝。

**用于容忍幻觉的 `defaultImpl`：**

```java
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, defaultImpl = UnknownTool.class)
@JsonSubTypes({
    @JsonSubTypes.Type(value = Hammer.class, name = "hammer"),
    @JsonSubTypes.Type(value = Wrench.class, name = "wrench")
})
interface Tool {}
```

如果 LLM 输出了未知的判别值（例如 `"saw"`）或完全省略了它，解析器
会返回一个 `UnknownTool` 而不是失败，这样你的代码就可以检测并处理
幻觉。

**添加描述：**

你可以通过用 `@Description` 注解基础类型和/或子类型来引导 LLM。
基础类型的描述会附加到 `anyOf` 元素上，而每个子类型的
描述会附加到其单独的选项上：

```java
@Description("A pet that lives in your home")
sealed interface Pet permits Hamster, Parrot {}

@Description("A small caged rodent kept as a pet")
record Hamster(String name, double weightGrams) implements Pet {}

@Description("A talking bird that can mimic human speech")
record Parrot(String name, int vocabulary) implements Pet {}
```

如果省略 `@Description`，描述将回退到简单类名
（例如 `"Hamster"`），这样 LLM 对每个选项仍然有一个标签。

**递归多态类型：**

子类型将基础类型作为字段包含的多态基类也能正常工作：

```java
sealed interface ExpressionNode permits Literal, BinaryOp {}

record Literal(int value) implements ExpressionNode {}

record BinaryOp(String operator, ExpressionNode left, ExpressionNode right) implements ExpressionNode {}
```

递归多态 schema 需要一个支持 `$ref` / `$defs` 的模型
（目前是 Azure OpenAI、Mistral 和 OpenAI）。

**判别字段冲突：**

如果某个子类型声明了与判别器同名的字段（例如，一个仅 sealed 基类上的
`type` 字段），schema 生成会失败并给出清晰的错误消息。修复选项：

- 重命名该字段，或
- 使用 `@JsonTypeInfo(property = "...")` 选择不同的判别器名称，或
- 如果该字段有意作为子类型的一部分，设置 `@JsonTypeInfo(visible = true)`，或
- 当子类型上的字段是判别器的权威来源时，
  使用 `@JsonTypeInfo(include = As.EXISTING_PROPERTY)`。

#### 限制

将 JSON Schema 与 AI 服务一起使用时，存在一些限制：
- 它仅适用于受支持的 Amazon Bedrock、Azure OpenAI、Google AI Gemini、Mistral、Ollama 和 OpenAI 模型。
- 配置 `ChatModel` 时需要显式启用对 JSON Schema 的支持。
- 它不能在[流式模式](ai-services.md#流式)下工作。
- 并非所有类型都受支持。受支持类型的列表请参见[这里](structured-outputs.md#支持的类型)。
- POJO 可以包含：
  - 标量/简单类型（例如 `String`、`int`/`Integer`、`double`/`Double`、`boolean`/`Boolean` 等）
  - `enum`
  - 嵌套 POJO
  - `List<T>`、`Set<T>` 和 `T[]`，其中 `T` 是标量、`enum` 或 POJO
  - 多态类型（sealed 接口/类或带有 Jackson `@JsonSubTypes` 注解的类型）
- 递归目前仅由 Azure OpenAI、Mistral 和 OpenAI 支持。
- 多态类型需要一个在 JSON schema 中支持 `anyOf` 的 LLM。
- 当 LLM 不支持 JSON Schema 功能、该功能未启用或类型不受支持时，
  AI 服务将回退到[提示词](structured-outputs.md#提示词)。


## 提示词 + JSON 模式

更多信息即将推出。
在此期间，请阅读[这一节](ai-services.md#json-模式)
和[这篇文章](https://glaforge.dev/posts/2024/11/18/data-extraction-the-many-ways-to-get-llms-to-spit-json-content/)。


## 提示词

当使用提示词方式（这是默认选择，除非启用了 JSON schema 支持）时，
AI 服务会自动生成格式说明，并将其追加到 `UserMessage` 的末尾，
指明 LLM 应以何种格式响应。
在方法返回之前，AI 服务会将 LLM 的输出解析为期望的类型。

你可以通过[启用日志](logging.md)来观察追加的说明。

!!! note
    这种方法相当不可靠。
    如果 LLM 和 LLM 提供商支持上述方法，最好使用那些方法。


## 支持的类型

| 类型                                                       | JSON Schema | 提示词 |
|------------------------------------------------------------|-------------|-----------|
| `POJO`                                                     | ✅           | ✅         |
| `List<POJO>`、`Set<POJO>`                                  | ✅           | ❌         |
| `Enum`                                                     | ✅           | ✅         |
| `List<Enum>`、`Set<Enum>`                                  | ✅           | ✅         |
| `List<String>`、`Set<String>`                              | ✅           | ✅         |
| 多态（sealed / `@JsonSubTypes`），包括 `List`/`Set`        | ✅           | ❌         |
| `boolean`、`Boolean`                                       | ✅           | ✅         |
| `int`、`Integer`                                           | ✅           | ✅         |
| `long`、`Long`                                             | ✅           | ✅         |
| `float`、`Float`                                           | ✅           | ✅         |
| `double`、`Double`                                         | ✅           | ✅         |
| `byte`、`Byte`                                             | ✅           | ✅         |
| `short`、`Short`                                           | ✅           | ✅         |
| `BigInteger`                                               | ✅           | ✅         |
| `BigDecimal`                                               | ✅           | ✅         |
| `Date`                                                     | ❌           | ✅         |
| `LocalDate`                                                | ❌           | ✅         |
| `LocalTime`                                                | ❌           | ✅         |
| `LocalDateTime`                                            | ❌           | ✅         |
| `Map<?, ?>`                                                | ❌           | ✅         |

几个示例：
```java
record Person(String firstName, String lastName) {}

enum Sentiment {
    POSITIVE, NEGATIVE, NEUTRAL
}

interface Assistant {

    Person extractPersonFrom(String text);

    Set<Person> extractPeopleFrom(String text);

    Sentiment extractSentimentFrom(String text);

    List<Sentiment> extractSentimentsFrom(String text);

    List<String> generateOutline(String topic);

    boolean isSentimentPositive(String text);

    Integer extractNumberOfPeopleMentionedIn(String text);
}
```

## 相关教程
- [Data extraction: The many ways to get LLMs to spit JSON content](https://glaforge.dev/posts/2024/11/18/data-extraction-the-many-ways-to-get-llms-to-spit-json-content/) 作者 [Guillaume Laforge](https://glaforge.dev/about/)
