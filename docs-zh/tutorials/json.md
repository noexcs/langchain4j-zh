# JSON 编解码器

LangChain4j 内置了一个 JSON 序列化器（默认使用 Jackson），供"工具"（tools）和"结构化输出"（structured output）功能使用。

如果你只是希望 LangChain4j 使用 Jackson 3 而不是 Jackson 2，那么无需下面提到的任何配置——添加一个依赖即可。参见[使用 Jackson 3](jackson-3.md)。

默认的序列化器适用于大多数场景。但在某些环境中，默认的 Jackson 序列化器可能会因其他依赖而产生错误，例如 Jetbrains/IntelliJ 插件的开发者就遇到过这种情况。

如果你需要提供自己的 JSON 序列化器（即 JSON 编解码器），可以按照以下步骤操作：

1. 在你的项目中创建 `dev.langchain4j.spi.json.JsonCodecFactory` 的实现

假设示例中的工厂类为：`example.MyJsonCodecFactory`

可以参考 `dev.langchain4j.internal.JacksonJsonCodec`，它是 LangChain4j 内部使用的默认编解码器，你可以在此基础上根据自己的需求进行调整。

2. 添加 SPI 提供者配置文件

在你的资源目录（例如 `src/main/resources`）中添加一个 `META-INF/services` 文件夹，并创建一个名为 `dev.langchain4j.spi.json.JsonCodecFactory` 的文件，该文件的内容必须是你工厂实现的全限定类名（FQDN），在我们的示例中应为：

```
example.MyJsonCodecFactory
```

## 注意事项

`dev.langchain4j.spi.json.JsonCodecFactory` 是 LangChain4j 的内部使用接口——仅当环境中确实需要自定义 JSON 编解码器时，才应使用这种方式。
