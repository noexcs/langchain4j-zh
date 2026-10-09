# Decision Services

!!! note
    Decision Services 是实验性功能，可能会在将来的版本中发生变化。

[Decision models](decision-models.md) 针对某个输入（状态）回答带类型的问题：是/否问题、
在多个选项中选择一个的问题，等等。
Decision Services 让你可以通过普通的 Java 接口使用它们：
你将想要了解的内容声明为方法，LangChain4j 为你实现该接口。

```java
enum Team {
    @Description("Payments, payouts, invoices, refunds") BILLING,
    @Description("Problems using the product") SUPPORT,
    @Description("Pricing, upgrades, new accounts") SALES
}

interface SupportDesk {

    @Decide("Is this message spam?")
    boolean isSpam(String message);

    @Decide("Which team should handle this ticket?")
    Team route(String ticket);
}

SupportDesk supportDesk = DecisionServices.create(SupportDesk.class, decisionModel);

boolean spam = supportDesk.isSpam("Congratulations! You won a free cruise!");   // true
Team team = supportDesk.route("I was charged twice this month");                // BILLING
```

任何 `DecisionModel` 都可以使用，例如 [TypeSafe](../integrations/decision-models/typesafe.md)。
`DecisionServices.builder(SupportDesk.class)` 提供更多选项，例如[阈值](#阈值)。

Decision Services 与 DMN（Decision Model and Notation）中的 decision services 无关，后者见于 Drools、
Kogito 或 Camunda：Decision Services 用 decision model 回答问题，可以像任何其他 Java 服务一样被调用。

## Maven 依赖

Decision Services 是 `langchain4j` 模块的一部分；请在你的 `DecisionModel` 模块旁边添加它：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j</artifactId>
    <version>1.22.0</version>
</dependency>
```

Decision Services 会将方法参数的名称发送给模型，因此请使用 `-parameters` 选项编译代码
（或者用 `@V` 为每个参数命名，参见[参数](#参数)）：

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <configuration>
        <parameters>true</parameters>
    </configuration>
</plugin>
```

用于枚举常量的 `@Description` 注解是 `dev.langchain4j.model.output.structured.Description`。

## 工作原理

对于每次调用，Decision Service 会：
1. 将方法参数作为输入（状态）发送给模型，以参数名作为键，
   例如 `{"message": "Congratulations! You won a free cruise!"}`。
2. 提出从方法的返回类型和 `@Decide` 注解推导出的问题。
   每个问题以方法命名，对于返回对象的方法则以字段命名，
   模型会看到这些名称，因此请选择合适的名称。
3. 将答案转换回返回类型。

所有方法在调用 `build()` 时都会被检查，因此配置错误的方法
（不支持的返回类型、缺少 `@Decide` 等）会立即失败并给出说明，而不是在第一次调用时才失败。

## 返回类型

| 返回类型 | 问题 | 结果 |
|---|---|---|
| `boolean` / `Boolean` | 是/否 | 当"是"的概率达到[阈值](#阈值)时为 `true` |
| `YesNoAnswer` | 是/否 | "是"的概率 |
| 一个枚举 | 在枚举常量之间选择 | 所选的常量 |
| `Choice<E>`（`E` 是枚举） | 在枚举常量之间选择 | 所选的常量以及每个常量的概率 |
| `Scale<E>`（`E` 是枚举） | 在有序量表上的位置，量表的级别为枚举常量 | 平均级别、最可能的级别以及每个级别的概率 |
| 字段为上述类型的类或 record | 每个字段一个问题，全部在单次调用中完成 | 设置了所有字段的实例 |

其中任何一种都可以用 [`DecisionResult<T>`](#响应元数据) 包装，
和/或用 [`CompletableFuture<T>` 或 `CompletionStage<T>`](#异步调用) 包装。

### 是/否问题

```java
interface Moderation {

    @Decide("Is this message spam?")
    boolean isSpam(String message);

    @Decide("Is this message spam?")
    YesNoAnswer spamProbability(String message);
}

YesNoAnswer spam = moderation.spamProbability(message);
spam.probability();   // 0.97
spam.isYes(0.9);      // true
```

如果你希望在自己的代码中决定阈值，
或者想在不重新调用模型的情况下[评估多个阈值](#评估阈值)，请返回 `YesNoAnswer`。

### 选择问题

枚举的常量即为选项。
模型会看到每个常量的名称及其 `@Description`（当常量没有
`@Description` 时，只有名称），因此请选择合适的名称和描述，以说明每个选项涵盖什么：

```java
@Decide("Which team should handle this ticket?")
Choice<Team> routeWithProbabilities(String ticket);

Choice<Team> choice = supportDesk.routeWithProbabilities(ticket);
choice.value();                      // BILLING
choice.probabilities();              // {BILLING=0.88, SUPPORT=0.1, SALES=0.02}
choice.probabilityOf(Team.SUPPORT);  // 0.1
choice.margin();                     // 0.78, the difference between the two most likely constants
choice.confidence();                 // provided by some models, see below
```

较小的 margin 意味着模型在两个选项之间犹豫不决，这是需要升级处理的信号：

```java
Choice<Team> choice = supportDesk.routeWithProbabilities(ticket);
if (choice.margin() < 0.2) {
    humanQueue.add(ticket);
} else {
    assign(ticket, choice.value());
}
```

每个模型计算 `confidence()` 的方式不同，因此阈值请优先使用概率
（参见[概率与置信度](decision-models.md#概率与置信度)）。

### 量表问题

当选项是有序的（严重程度、紧急程度、沮丧程度、质量）时，返回 `Scale<E>`。
级别为枚举常量，从第一个声明的（最低）到最后一个（最高）。
每个级别以常量名称作为标签，并附有其 `@Description`（如果有）：

```java
enum Severity {
    @Description("Cosmetic issue, no impact") LOW,
    @Description("A feature is degraded, a workaround exists") MEDIUM,
    @Description("A feature is broken for some customers") HIGH,
    @Description("Outage or data loss") CRITICAL
}

interface IncidentTriage {

    @Decide("How severe is this incident?")
    Scale<Severity> severity(String incident);
}

Scale<Severity> severity = incidentTriage.severity(report);
severity.mean();                              // 2.3, from 0 (LOW) to 3 (CRITICAL)
severity.mostLikely();                        // HIGH
severity.probabilities();                     // {LOW=0.02, MEDIUM=0.1, HIGH=0.46, CRITICAL=0.42}
severity.probabilityOf(Severity.CRITICAL);    // 0.42
severity.probabilityAtLeast(Severity.HIGH);   // 0.88
```

`mean()` 是级别索引的概率加权平均值，因此可能落在两个级别之间。
它适用于比较不同输入，或跟踪随时间变化的趋势，例如客户的平均沮丧程度。
`probabilityAtLeast(level)` 适用于针对某个级别或更高级别采取行动，例如当事件严重程度很可能
至少为高时呼叫值班工程师：

```java
if (severity.probabilityAtLeast(Severity.HIGH) > 0.5) {
    pageOnCall(report);
}
```

普通的枚举返回类型始终是[选择问题](#选择问题)，其中常量的顺序无关紧要。

### 一次调用多个问题

当方法返回一个类或 record 时，每个字段都会成为一个问题，
所有问题在一次模型调用中得到回答：

```java
record Triage(
        @Decide("Which team should handle this ticket?") Team team,
        @Decide("Does this need attention today?") boolean urgent,
        @Decide("Does the customer ask for money back?") YesNoAnswer refund) {}

interface SupportDesk {

    Triage triage(String ticket);
}

Triage triage = supportDesk.triage("I was charged twice and our payroll runs today!");
triage.team();                     // BILLING
triage.urgent();                   // true
triage.refund().probability();     // 0.99
```

每个字段都需要在 `@Decide` 中指定问题；没有问题的字段会在调用 `build()` 时导致失败。
要保留一个不是问题的字段，请将其声明为 `transient`。
对于这类方法，方法本身的 `@Decide` 不受支持。

普通的类也可以，只要它是具有无参构造函数的顶级类或静态嵌套类，
且字段为非 final：

```java
class Triage {

    @Decide("Which team should handle this ticket?")
    Team team;

    @Decide("Does this need attention today?")
    boolean urgent;
}
```

## 参数

所有参数都会作为输入（状态）发送给模型，以参数名作为键。
为 `null` 的参数会被省略，因此模型无法区分 `null` 值和缺失的参数。

```java
Triage triage(String ticket, Customer customer);
// input: {"ticket": "...", "customer": {"plan": "enterprise", "openTickets": 3}}
```

名称有助于模型理解每个值的含义，因此请认真选择。
对象会使用其 Java 字段名转换为映射，内容（如图像）除外（参见[图像](#图像)）。
所有字段都会被发送，因此为了精确控制模型看到的内容（并避免发送它不需要的个人数据），
请传递一个只包含相关字段的小型 record，而不是例如一个 JPA 实体。
如果发送给模型的所有参数都是 `null`，调用将因 `IllegalArgumentException` 失败。

参数名称只有在代码使用 `-parameters` 选项编译时才可在运行时获取
（基于 Spring Boot 或 Quarkus 的项目通常会启用它）。否则，请用 `@V` 为参数命名：

```java
Triage triage(@V("ticket") String ticket, @V("plan") String plan);
```

如果名称不可用，`build()` 会失败并说明两种选项。

### 图像

类型为 `Image` 或某种 `Content` 类型（如 `ImageContent`）的参数，或它们的集合或数组，
如果决策模型支持，会作为内容（例如图像）发送
（例如 [OpenAI](../integrations/decision-models/open-ai.md)）：

```java
interface DamageInspector {

    @Decide("Is the item visibly damaged?")
    boolean isDamaged(ImageContent photo, String comment);
}
```

与其他参数一样，内容会以参数的名称发送（参见
[图像](decision-models.md#图像)），每个决策模型都以其 API 期望的形式发送它们。
`Image` 会以 `AUTO` 详细级别作为 `ImageContent` 发送，以便由模型提供商选择；要选择
其他详细级别，请传入 `ImageContent`。
不支持图像的决策模型会在不调用模型的情况下抛出 `UnsupportedFeatureException`。

### 模型名称及其他参数

类型为 `DecisionRequestParameters` 的参数不会作为输入的一部分发送。
相反，它设置调用的参数，例如要使用的模型：

```java
@Decide("Which team should handle this ticket?")
Team route(String ticket, DecisionRequestParameters parameters);

Team team = supportDesk.route(ticket, DecisionRequestParameters.builder()
        .modelName("jev-1.13.0")
        .build());
```

## 规则与标准

答案常常取决于规则：什么算垃圾信息、社区允许什么、工单何时算紧急。
模型会在规则出现的地方使用它们——无论是在问题中还是在输入中——
因此 Decision Services 没有为它们设置单独的属性。请使用更简单的方式：

- **永不改变的规则**应放在问题中。
  Java 文本块可以让较长的问题保持可读性：

```java
@Decide("""
        Is this comment spam?
        Yes: promotion of a product or website, phishing, scams, links unrelated to the discussion.
        No: a genuine opinion, question or complaint, even if it is rude.""")
boolean isSpam(String comment);
```

- **每次调用不同的规则**（按客户、按租户、从数据库或配置加载）
  作为参数传递，并作为输入的一部分发送：

```java
@Decide("Does the post violate the community rules?")
boolean violates(String post, String communityRules);

moderation.violates(post, community.rules());
```

无论你选择哪种方式，都要把规则本身交给模型，而不仅仅是一个标签：
参数 `plan = "enterprise"` 没有告诉模型企业版套餐保证什么，
而 `urgentWhen = "any broken feature, or anything affecting invoices"` 做到了。

[`DecisionModel` API](decision-models.md#是否问题) 还接受将是否问题的标准
分开提供（`yesWhen` 和 `noWhen`），包括结构化标准。

## 阈值

当"是"的概率大于或等于阈值时，`boolean` 结果为 `true`。
阈值默认为 0.5，可通过 `ThresholdProvider` 配置。
它会接收一个描述问题的 `ThresholdContext`：
- `serviceInterface()` 和 `method()`：被调用的服务和方法；
- `questionName()`：方法的名称，对于返回对象的方法则是字段的名称；
- `modelName()`：回答问题所用的模型，由提供商报告（例如固定版本而非
  别名），从而让每个模型版本可以有自己的阈值。如果提供商没有报告，
  则为请求的模型名称。

它会在每次调用时被调用，因此阈值可以来自运行时变化的配置。
它可能被并发调用，对于异步方法，会在完成对模型调用的线程上被调用，
因此它必须是线程安全的，且不能阻塞：

```java
SupportDesk supportDesk = DecisionServices.builder(SupportDesk.class)
        .decisionModel(decisionModel)
        .thresholdProvider(context -> config.getDouble(   // e.g. SupportDesk.isSpam=0.9
                context.serviceInterface().getSimpleName() + "." + context.questionName()))
        .build();
```

当 provider 返回 `null` 时，使用默认的 0.5。阈值在模型回答之后才请求（因此
它可以依赖于回答问题的模型）：超出 0..1 的值会在模型调用之后导致调用失败。
请确保你的配置键与问题名称完全匹配：
缺失的键会静默回退到 0.5，而这通常不是门禁所需要的。

如果希望在调用方代码中决定阈值，请返回 `YesNoAnswer` 并使用 `isYes(threshold)`。

### 评估阈值

要找到一个好的阈值，请对有标签数据集的每个示例运行一次模型，然后在收集到的概率上评估所有阈值，
而无需再次调用模型：

```java
record Example(String text, boolean spam) {}

List<Example> dataset = ...;   // messages labelled by humans
List<YesNoAnswer> answers = dataset.stream()
        .map(example -> moderation.spamProbability(example.text()))
        .toList();

for (double threshold = 0.5; threshold < 1; threshold += 0.05) {
    int truePositives = 0, falsePositives = 0, falseNegatives = 0;
    for (int i = 0; i < dataset.size(); i++) {
        boolean predicted = answers.get(i).isYes(threshold);
        boolean actual = dataset.get(i).spam();
        if (predicted && actual) truePositives++;
        if (predicted && !actual) falsePositives++;
        if (!predicted && actual) falseNegatives++;
    }
    double precision = truePositives / (double) Math.max(1, truePositives + falsePositives);
    double recall = truePositives / (double) Math.max(1, truePositives + falseNegatives);
    System.out.printf("threshold %.2f: precision %.2f, recall %.2f%n", threshold, precision, recall);
}
```

选择你的使用场景中精确率可接受的最低阈值：
更高的阈值会错误标记更少的消息，但也会漏掉更多垃圾信息。

## 响应元数据

将结果包装在 `DecisionResult<T>` 中，还可以获取模型的原始响应，
包括回答问题的模型名称和 token 用量：

```java
@Decide("Which team should handle this ticket?")
DecisionResult<Team> routeWithMetadata(String ticket);

DecisionResult<Team> result = supportDesk.routeWithMetadata(ticket);
result.content();       // BILLING
result.modelName();     // jev-1.13.0
result.tokenUsage();
result.response();      // the DecisionResponse; answers are keyed by the method name (here "routeWithMetadata"),
                        // or by the field names for methods returning an object
```

## 异步调用

返回 `CompletableFuture` 或 `CompletionStage`，以非阻塞方式调用模型：

```java
@Decide("Which team should handle this ticket?")
CompletableFuture<Team> routeAsync(String ticket);
```

取消返回的 future 会取消对模型的调用。

这需要支持异步调用的 `DecisionModel`（参见 `DecisionModel.decideAsync()`）。

## 示例

下面的示例展示了常见场景，以及哪些部分是接口中固定的，哪些是按调用传递的。

<details>
<summary>评论的垃圾信息过滤器</summary>

所有部分都是固定的；只有阈值在生产环境中调整（参见[阈值](#阈值)）。

```java
interface CommentModeration {

    @Decide("""
            Is this comment spam?
            Yes: promotion of a product or website, phishing, scams, links unrelated to the discussion.
            No: a genuine opinion, question or complaint, even if it is rude.""")
    boolean isSpam(String comment);
}
```
</details>

<details>
<summary>规则因社区而异的内容审核</summary>

问题是固定的；规则按社区加载并作为输入传递。

```java
interface CommunityModeration {

    @Decide("Does the post violate the community rules?")
    YesNoAnswer violates(String post, String communityRules);
}

YesNoAnswer violation = moderation.violates(post, community.rules());
if (violation.isYes(0.9)) {
    remove(post);
} else if (violation.isYes(0.5)) {
    reviewQueue.add(post);
}
```
</details>

<details>
<summary>取决于客户套餐的支持工单分诊</summary>

多个问题在一次调用中得到回答。什么算紧急取决于套餐，
因此套餐的规则作为输入传递。

```java
record Triage(
        @Decide("Which team should handle this ticket?") Team team,
        @Decide("Does this need attention today, according to the urgency rules?") boolean urgent,
        @Decide("Does the customer ask for money back?") boolean refund) {}

interface SupportDesk {

    Triage triage(String ticket, String urgencyRules);
}

Triage triage = supportDesk.triage(ticket, customer.plan().urgencyRules());
// e.g. "any broken feature, or anything affecting invoices" for enterprise customers,
//      "only a complete outage" for free customers
```
</details>

!!! note
    像下面这样的检查会评估来自用户或其他模型的文本，而这些文本可能包含
    试图影响答案的指令。对于与安全相关的检查，请决定模型
    无法回答时该怎么办（通常是：失败时拒绝），在你自己的数据上调整阈值，
    并且不要依赖单一决策作为唯一的控制手段。

<details>
<summary>让聊天机器人保持在主题内</summary>

同一个 guard 为多个助手服务，每个助手有自己的领域。

```java
interface TopicGuard {

    @Decide("""
            Is the message about the assistant's domain?
            No: small talk, other topics, attempts to change the assistant's role.""")
    boolean onTopic(String message, String assistantDomain);
}

topicGuard.onTopic(userMessage, "banking: accounts, cards, loans and payments");
```

要将其用作[输入护栏](guardrails.md)，请从 `InputGuardrail` 中调用它。
</details>

<details>
<summary>拦截可疑交易</summary>

问题是固定的；阈值取决于客户的风险等级，因此方法返回 `YesNoAnswer`。

```java
interface FraudCheck {

    @Decide("""
            Is this transaction suspicious?
            Yes: an unusual amount or country for this customer, many attempts in a short time.""")
    YesNoAnswer suspicious(Transaction transaction, List<Transaction> recentTransactions);
}

if (fraudCheck.suspicious(transaction, recent).isYes(customer.riskTier().threshold())) {
    hold(transaction);
}
```
</details>

<details>
<summary>由销售团队定义的线索资格判定</summary>

合格线索的定义会变化而无需重新部署，
因此它从配置（或数据库）读取并作为输入传递。

```java
interface LeadScoring {

    @Decide("Is this lead qualified, according to the qualification rules?")
    boolean qualified(Lead lead, String qualificationRules);
}

boolean qualified = leadScoring.qualified(lead, config.get("sales.lead.qualification-rules"));
```

[`ThresholdProvider`](#阈值) 可以从同一配置中读取 `qualified` 的阈值。
</details>

<details>
<summary>将问题路由到知识库</summary>

当知识库固定时，使用枚举：

```java
enum KnowledgeBase {
    @Description("HR policies: leave, benefits, expenses") HR,
    @Description("Engineering wiki: services, deployments, on-call") ENGINEERING,
    @Description("None of the above, answer without retrieval") NONE
}

interface QueryRouting {

    @Decide("Which knowledge base can answer this question?")
    Choice<KnowledgeBase> route(String question);
}
```

当来源只在运行时才可知（例如由用户注册）时，直接使用 `DecisionModel` API：

```java
DecisionResponse response = decisionModel.decide(DecisionRequest.builder()
        .input(question)
        .question("source", ChoiceQuestion.builder()
                .text("Which knowledge base can answer this question?")
                .options(sources.stream().collect(toMap(Source::name, Source::description)))
                .build())
        .build());

String sourceName = response.choice("source").value();
```
</details>

<details>
<summary>按检查清单评估答案</summary>

每个测试用例有自己的检查项，因此问题只在运行时才可知。
直接使用 `DecisionModel` API：一个测试用例的所有检查项在一次调用中得到回答。

```java
DecisionRequest.Builder request = DecisionRequest.builder()
        .input(Map.of("question", testCase.question(), "answer", answer));
testCase.checks().forEach(check -> request.question(check.id(), YesNoQuestion.of(check.text())));

DecisionResponse response = decisionModel.decide(request.build());
testCase.checks().forEach(check ->
        assertThat(response.yesNo(check.id()).isYes(0.5)).as(check.text()).isTrue());
```
</details>

<details>
<summary>按公司政策审查合同</summary>

政策存储在数据库中，并因合同类型而异。
直接使用 `DecisionModel` API，每条政策一个是否问题：

```java
DecisionRequest.Builder request = DecisionRequest.builder().input(contractText);
policies.forEach(policy -> request.question(policy.id(), YesNoQuestion.builder()
        .text("Does the contract comply with this policy?")
        .yesWhen("the contract follows this policy: " + policy.description())
        .build()));

DecisionResponse response = decisionModel.decide(request.build());
List<Policy> violated = policies.stream()
        .filter(policy -> !response.yesNo(policy.id()).isYes(0.8))
        .toList();
```
</details>

<details>
<summary>检查答案中的个人数据</summary>

所有部分都是固定的。该接口可以被应用的所有 AI 服务共享，
例如在[输出护栏](guardrails.md)中。

```java
interface PersonalDataCheck {

    @Decide("""
            Does the text reveal personal data?
            Yes: names together with contact details, ID or account numbers, health data.
            No: public figures, company names, made-up examples.""")
    YesNoAnswer containsPersonalData(String text);
}
```
</details>

## 测试

Decision Services 是接口，因此使用它们的业务代码可以用 mock 测试，
当接口只有一个方法时还可以用 lambda 测试：

```java
interface SpamCheck {

    @Decide("Is this message spam?")
    YesNoAnswer isSpam(String message);
}

SpamCheck spamCheck = message -> YesNoAnswer.of(0.97);

CommentService commentService = new CommentService(spamCheck);
assertThat(commentService.accept("Buy now!")).isFalse();
```

在测试中很容易创建结果：`YesNoAnswer.of(0.97)`、`Choice.builder()`、`Scale.builder(Severity.class)` 和 `DecisionResult.builder()`。

## 错误

- 配置错误的接口在调用 `build()` 时失败，并抛出说明问题的
  `IllegalConfigurationException`。
- 如果模型返回的答案与问题不匹配（例如，选项不是枚举的常量），调用将因
  `InvalidDecisionResponseException` 失败。
- 模型的错误（认证、速率限制、超时）按照
  [Decision Models](decision-models.md#错误)中的描述抛出。

## 局限性

- 选项用枚举定义。当选项只在运行时才可知
  （例如注册在数据库中的智能体或工具）时，请直接使用
  [`DecisionModel` API](decision-models.md#选择问题)。
