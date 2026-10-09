# 技能

!!! note
    Skills API 是实验性的。API 和行为在未来版本中可能仍会变化。

技能（Skills）是一种为 LLM 配备可复用、自包含行为说明的机制。
一个技能捆绑了名称、简短描述和一段说明正文（即其 _内容_），
以及可选的资源（例如参考资料、素材、模板等）。
LLM 会按需加载技能，从而保持初始上下文较小，仅在真正需要时
才拉入详细说明。

!!! note
    技能的设计遵循 [Agent Skills 规范](https://agentskills.io)。

## 创建技能

### 从文件系统

通常，每个技能都位于自己的目录中，其中包含一个 `SKILL.md` 文件。
该文件必须以 YAML front matter 块开头，声明技能的 `name` 和 `description`。
front matter 下方的所有内容都会成为技能的内容——即 LLM
激活该技能时提供给它的说明。

```
skills/
├── docx/
│   ├── SKILL.md
│   └── references/
│       └── tracked-changes.md   ← loaded as a resource
└── data-analysis/
    └── SKILL.md
```

`SKILL.md` 示例：

```markdown
---
name: docx
description: Edit and review Word documents using tracked changes
---

When the user asks you to edit a Word document:

1. Always use tracked changes so edits can be reviewed.
   ...
```

技能目录中的任何文件（`SKILL.md` 本身和 `scripts/`
子目录下的文件除外）都会自动加载为 `SkillResource`，LLM 可按需读取。

使用 `langchain4j-skills` 模块中的 `FileSystemSkillLoader` 从文件系统加载技能：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-skills</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

```java
// Load all skills found in immediate subdirectories:
List<FileSystemSkill> skills = FileSystemSkillLoader.loadSkills(Path.of("skills/"));

// Or load a single skill by its directory:
FileSystemSkill skill = FileSystemSkillLoader.loadSkill(Path.of("skills/docx"));
```

### 从类路径

`ClassPathSkillLoader` 的工作方式与 `FileSystemSkillLoader` 类似，但技能目录
从类路径解析，而不是从文件系统。当技能打包在你的
JAR 内或位于 `src/main/resources` 下时，这非常有用：

```
src/main/resources/
└── skills/
    ├── docx/
    │   ├── SKILL.md
    │   └── references/
    │       └── tracked-changes.md
    └── data-analysis/
        └── SKILL.md
```

```java
// Load all skills from a classpath directory:
List<FileSystemSkill> skills = ClassPathSkillLoader.loadSkills("skills");

// Or load a single skill:
FileSystemSkill skill = ClassPathSkillLoader.loadSkill("skills/docx");
```

默认情况下，`ClassPathSkillLoader` 使用线程上下文类加载器。
如有需要，你可以传入自定义的 `ClassLoader`：

```java
FileSystemSkill skill = ClassPathSkillLoader.loadSkill("skills/docx", myClassLoader);
```

与 `FileSystemSkillLoader` 相同，相同的 `SKILL.md` 格式、资源加载规则和
`scripts/` 排除规则同样适用。

### 以编程方式

技能不一定基于文件系统。
你可以使用构建器 API 从任意来源创建技能——数据库、远程 API 或运行时生成：

```java
Skill skill = Skill.builder()
        .name("incident-response")
        .description("Step-by-step runbook for diagnosing and resolving production incidents")
        .content("""
                When a production alert fires:
                1. Call `fetchRecentLogs(serviceName)` to retrieve the last 5 minutes of logs.
                2. Call `checkServiceHealth(serviceName)` to get current health metrics.
                3. Based on the findings, call `createIncidentTicket(summary, severity)`.
                4. If severity is CRITICAL, also call `pageOnCall(incidentId)`.
                """)
        .build();
```

你还可以通过编程方式附加资源：

```java
SkillResource reference = SkillResource.builder()
        .relativePath("references/tone-guide.md")
        .content("Use warm, concise language. Avoid jargon.")
        .build();

Skill skill = Skill.builder()
        .name("customer-support")
        .description("Handles customer support inquiries")
        .content("Follow the tone guide in references/tone-guide.md ...")
        .resources(List.of(reference))
        .build();
```

## 模式

根据你需要多少控制权和信任度，技能可以以两种不同的模式
与 AI 服务集成。

### 工具模式（推荐）

**类：** `Skills`（来自 `langchain4j-skills` 模块）

这对应于 [Agent Skills 规范](https://agentskills.io/integrate-skills) 中描述的
**基于工具的智能体**集成方式。

在此模式下，LLM 通过激活技能来获取分步说明，然后通过调用你显式注册的
[工具](tools.md) 来执行这些说明。
**LLM 在推理期间无法访问文件系统**——所有技能内容和
资源都会提前加载到内存中（例如通过 `FileSystemSkillLoader`），并且 `activate_skill`
和 `read_skill_resource` 工具返回的是这些预加载的内容，而不是从磁盘读取。
由于只能调用你预定义的工具，**不存在任意代码执行的风险**。

#### 注册的工具

| 工具                  | 注册时机                                                                               |
|-----------------------|----------------------------------------------------------------------------------------|
| `activate_skill`      | 始终注册。LLM 调用它以将技能的完整说明加载到上下文中。              |
| `read_skill_resource` | 当至少一个技能带有资源时注册。LLM 调用它以读取单个参考文件。 |
| 技能作用域工具    | 技能激活之后。                                                                 |

#### 工作原理

1. 系统消息列出可用技能（名称和描述），以便 LLM 进行选择。
2. 用户提出一个需要特定技能的问题。
3. LLM 调用 `activate_skill("my-skill")` 以获取其说明。
4. LLM 按照这些说明完成任务，过程中可选择读取资源文件。

#### 技能示例

技能描述的是_策略_——精确的调用顺序、必需的参数、错误处理步骤
以及完整的示例——而实际的执行保留在类型安全、经过测试的 Java 代码中：

```markdown
---
name: process-order
description: Processes a customer order end-to-end
---

To process an order:

1. Call `validateOrder(orderId)` to check the order is valid.
2. Call `reserveInventory(orderId)` to reserve the required stock.
3. Only if reservation succeeds, call `chargePayment(orderId)`.
4. Finally, call `sendConfirmationEmail(orderId)`.

If any step fails, call `rollbackOrder(orderId)` before reporting the error.
```

#### 接入配置

将你常规的工具一起，将 `Skills` 的 `ToolProvider` 传入你的 AI 服务构建器。
使用 `formatAvailableSkills()` 将技能目录注入系统消息，以便
LLM 知道它可以激活哪些技能：

```java
Skills skills = Skills.from(FileSystemSkillLoader.loadSkills(Path.of("skills/")));

MyAiService service = AiServices.builder(MyAiService.class)
        .chatModel(chatModel)
        .tools(new OrderTools()) // your tools
        .toolProvider(skills.toolProvider()) // or .toolProviders(myToolProvider, skills.toolProvider()) if you already have a tool provider configured
        .systemMessage("You have access to the following skills:\n" + skills.formatAvailableSkills()
                + "\nWhen the user's request relates to one of these skills, activate it first using the `activate_skill` tool before proceeding.")
        .build();
```

`formatAvailableSkills()` 返回一个 XML 格式的块，列出每个技能的名称和描述：

```xml

<available_skills>
    <skill>
        <name>process-order</name>
        <description>Processes a customer order end-to-end</description>
    </skill>
    <skill>
        <name>data-analysis</name>
        <description>Analyse tabular data and produce charts</description>
    </skill>
</available_skills>
```

#### 自定义

每个工具的名称、描述和参数元数据都可以通过
构建器上对应的配置类进行覆盖：

```java
Skills skills = Skills.builder()
        .skills(mySkills)
        .activateSkillToolConfig(ActivateSkillToolConfig.builder()
                .name(...)                    // tool name (default: "activate_skill")
                .description(...)             // tool description
                .parameterName(...)           // parameter name (default: "skill_name")
                .parameterDescription(...)    // parameter description
                .throwToolArgumentsExceptions(...) // throw ToolArgumentsException instead of ToolExecutionException (default: false)
                .build())
        .readResourceToolConfig(ReadResourceToolConfig.builder()
                .name(...)                              // tool name (default: "read_skill_resource")
                .description(...)                       // tool description
                .skillNameParameterName(...)             // skill_name parameter name (default: "skill_name")
                .skillNameParameterDescription(...)      // skill_name parameter description
                .relativePathParameterName(...)          // relative_path parameter name (default: "relative_path")
                .relativePathParameterDescription(...)   // static description (takes precedence over provider)
                .relativePathParameterDescriptionProvider(...) // dynamic description based on available resources
                .throwToolArgumentsExceptions(...)       // throw ToolArgumentsException instead of ToolExecutionException (default: false)
                .build())
        .build();
```

#### 技能作用域工具

你可以将工具直接附加到技能上。这些工具**只有在技能通过 `activate_skill` 工具
激活之后才会暴露给 LLM**。
这能让 LLM 的工具列表保持精简且聚焦，并确保技能专属工具只
在相关时才出现。

##### 使用 `@Tool` 注解方法

附加工具最简单的方式是传入带有 `@Tool` 注解方法的对象：

```java
class OrderTools {

    @Tool("Validates a customer order by ID")
    String validateOrder(String orderId) {
        // validation logic
        return "valid";
    }

    @Tool("Charges payment for a customer order")
    String chargePayment(String orderId) {
        // payment logic
        return "charged";
    }
}

Skill skill = Skill.builder()
        .name("process-order")
        .description("Processes a customer order end-to-end")
        .content("""
                To process an order:
                1. Call `validateOrder(orderId)` to check the order is valid.
                2. Call `chargePayment(orderId)`.
                """)
        .tools(new OrderTools())
        .build();
```

你还可以通过 `toBuilder()` 将工具附加到已经构建好的技能上——例如，
为从文件系统加载的技能添加工具：

```java
FileSystemSkill skill = FileSystemSkillLoader.loadSkill(Path.of("skills/process-order"));

Skill skillWithTools = skill.toBuilder()
        .tools(new OrderTools())
        .build();
```

##### 使用工具提供器

你还可以将 `ToolProvider` 附加到技能——例如，仅在技能激活之后
暴露来自 MCP 服务器的工具：

```java
ToolProvider mcpToolProvider = McpToolProvider.builder()
        .mcpClients(mcpClient)
        .toolFilter((tool, mcpClient) -> tool.name().startsWith("inventory_"))
        .build();

Skill skill = Skill.builder()
        .name("inventory-management")
        .description("Manages warehouse inventory")
        .content("""
                Use inventory tools to check stock levels and update quantities.
                """)
        .toolProviders(mcpToolProvider)
        .build();
```

##### 使用 `Map<ToolSpecification, ToolExecutor>`

为了完全控制工具规范和执行逻辑，你可以直接传入一个 map：

```java
ToolSpecification validateOrder = ToolSpecification.builder()
        .name("validateOrder")
        .description("Validates a customer order by ID")
        .addParameter("orderId", JsonSchemaProperty.STRING, JsonSchemaProperty.description("The order ID"))
        .build();

ToolExecutor validateOrderExecutor = (request, memoryId) -> {
    String orderId = parseOrderId(request.arguments());
    return validate(orderId);
};

Skill skill = Skill.builder()
        .name("process-order")
        .description("Processes a customer order end-to-end")
        .content("""
                To process an order:
                1. Call `validateOrder(orderId)` to check the order is valid.
                """)
        .tools(Map.of(validateOrder, validateOrderExecutor))
        .build();
```

三种方式可以组合使用——`@Tool` 方法、`ToolProvider` 和 `Map` 条目
会合并为单一的技能作用域工具集合：

```java
Skill skill = Skill.builder()
        .name("process-order")
        .description("Processes a customer order end-to-end")
        .content("...")
        .tools(new OrderTools())
        .tools(Map.of(validateOrder, validateOrderExecutor))
        .toolProviders(mcpToolProvider)
        .build();
```

##### 接入配置

```java
Skills skills = Skills.from(skill);

MyAiService service = AiServices.builder(MyAiService.class)
        .chatModel(chatModel)
        .chatMemory(MessageWindowChatMemory.withMaxMessages(100))
        .toolProvider(skills.toolProvider())
        .systemMessage("You have access to the following skills:\n" + skills.formatAvailableSkills()
                + "\nWhen the user's request relates to one of these skills, activate it first.")
        .build();
```

##### 技能作用域工具的工作原理

1. 在技能激活之前，LLM 只能看到 `activate_skill`（以及 `read_skill_resource`）工具。
   技能作用域工具不包含在工具列表中。
2. 当 LLM 调用 `activate_skill("process-order")` 时，该激活记录在 `ToolExecutionResultMessage` 中。
3. 在下一次 LLM 调用之前（在同一次 AI 服务调用内），AI 服务会针对当前消息
   重新评估动态工具提供器。技能作用域工具（例如 `validateOrder`）随即
   变为可见，LLM 可以在同一次 AI 服务调用中立即调用它们。
   技能作用域工具在下一次 AI 服务调用中仍对 LLM 可见，只有当
   技能被取消激活时它们才会变得不可见。

##### 与工具搜索配合使用技能

技能可以与 [工具搜索](tools.md#工具搜索) 配合使用。当两者都配置时，
它们各自独立工作：

- **技能作用域工具永远不可被搜索。** 它们不会出现在可搜索的工具池中，
  也无法通过 `tool_search_tool` 找到。只有当 LLM 激活
  相应技能后，它们才会变得可见。
- **常规工具仍可被搜索。** 通过 AI 服务上的 `.tools(...)` 注册的工具
  （不是注册在技能上的工具）继续可被搜索，无论是否有技能被激活。
- **`activate_skill` 始终可见。** 它被标记为 `ALWAYS_VISIBLE`，因此即使启用了工具搜索，LLM 也
  始终可以调用它。

```java
Skills skills = Skills.from(mySkills);

MyAiService service = AiServices.builder(MyAiService.class)
        .chatModel(chatModel)
        .chatMemory(MessageWindowChatMemory.withMaxMessages(100))
        .tools(new MySearchableTools()) // these are searchable
        .toolProvider(skills.toolProvider()) // skill-scoped tools are NOT searchable
        .toolSearchStrategy(new SimpleToolSearchStrategy())
        .systemMessage("You have access to the following skills:\n" + skills.formatAvailableSkills()
                + "\nWhen the user's request relates to one of these skills, activate it first.")
        .build();
```

### Shell 模式（实验性）

**类：** `ShellSkills`（来自 `langchain4j-experimental-skills-shell` 模块）

这对应于 [Agent Skills 规范](https://agentskills.io/integrate-skills) 中描述的
**基于文件系统的智能体**集成方式。

!!! warning
    **Shell 执行本质上是不安全的。**
    命令直接在宿主进程环境中运行，**没有任何沙箱、容器化
    或权限限制**。行为异常或遭受提示注入的 LLM 可以在运行你应用程序的机器上
    执行任意命令。
    请仅在你完全信任输入并接受相关风险的受控环境中使用它。

在此模式下，LLM 被赋予单一的 `run_shell_command` 工具，并使用 shell 命令
直接从文件系统读取技能说明。没有 `activate_skill` 或
`read_skill_resource` 工具——LLM 像人类开发者一样导航技能文件。

#### 注册的工具

| 工具                | 注册时机                                                                                   |
|---------------------|-----------------------------------------------------------------------------------------------|
| `run_shell_command` | 始终注册。LLM 运行 shell 命令以读取 `SKILL.md` 文件、资源文件并执行脚本。 |

#### 工作原理

1. 系统消息列出可用技能及其绝对文件系统路径。
2. 用户提出一个需要特定技能的问题。
3. LLM 运行 `cat /path/to/skills/docx/SKILL.md` 以读取说明。
4. LLM 通过运行更多 shell 命令来遵循这些说明。

#### 依赖

Shell 执行位于一个独立的实验性构件中——请将其添加到你的构建中：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-experimental-skills-shell</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

#### 接入配置

所有技能必须基于文件系统（通过 `FileSystemSkillLoader` 加载）。
使用 `ShellSkills` 而不是 `Skills`：

```java
ShellSkills skills = ShellSkills.from(FileSystemSkillLoader.loadSkills(Path.of("skills/")));

MyAiService service = AiServices.builder(MyAiService.class)
        .chatModel(chatModel)
        .toolProvider(skills.toolProvider()) // or .toolProviders(myToolProvider, skills.toolProvider()) if you already have a tool provider configured
        .systemMessage("You have access to the following skills:\n" + skills.formatAvailableSkills()
                + "\nWhen the user's request relates to one of these skills, read its SKILL.md before proceeding.")
        .build();
```

`formatAvailableSkills()` 包含一个 `<location>` 字段，以便 LLM 知道
每个 `SKILL.md` 的确切位置：

```xml

<available_skills>
    <skill>
        <name>docx</name>
        <description>Edit and review Word documents using tracked changes</description>
        <location>/path/to/skills/docx/SKILL.md</location>
    </skill>
    <skill>
        <name>data-analysis</name>
        <description>Analyse tabular data and produce charts</description>
        <location>/path/to/skills/data-analysis/SKILL.md</location>
    </skill>
</available_skills>
```

#### 何时使用 Shell 模式

此模式最适合**实验和原型开发**，或者当你想使用社区发布的
第三方技能（例如来自 [agentskills.io](https://agentskills.io) 生态系统的技能）而无需先将其移植到 Java 时。
它可以让你快速搭建一个可用的工作流，然后随着方案的成熟，将各个动作
逐步迁移为工具。

#### 自定义

使用 `RunShellCommandToolConfig` 来调整工作目录、输出限制
和参数名称：

```java
ShellSkills skills = ShellSkills.builder()
        .skills(mySkills)
        .runShellCommandToolConfig(RunShellCommandToolConfig.builder()
                .name(...)                              // tool name (default: "run_shell_command")
                .description(...)                       // tool description (default: includes OS name)
                .commandParameterName(...)              // command parameter name (default: "command")
                .commandParameterDescription(...)       // command parameter description
                .timeoutSecondsParameterName(...)       // timeout parameter name (default: "timeout_seconds")
                .timeoutSecondsParameterDescription(...) // timeout parameter description
                .workingDirectory(...)                  // working directory for commands (default: JVM's user.dir)
                .maxStdOutChars(...)                    // max stdout chars in result (default: 10_000)
                .maxStdErrChars(...)                    // max stderr chars in result (default: 10_000)
                .executorService(...)                   // ExecutorService for reading stdout/stderr streams
                .throwToolArgumentsExceptions(...)      // throw ToolArgumentsException instead of ToolExecutionException (default: false)
                .build())
        .build();
```
