# GraalVM Polyglot/Truffle

!!! danger
   ⚠️ 安全警告：高风险代码执行

   该模块通过 GraalVM 执行任意 Python/JavaScript 代码，本质上具有危险性。

   ❗ 请勿在生产环境中使用！

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-code-execution-engine-graalvm-polyglot</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## API

- `GraalVmJavaScriptExecutionEngine`
- `GraalVmJavaScriptExecutionTool`
- `GraalVmPythonExecutionEngine`
- `GraalVmPythonExecutionTool`


## 返回值

`execute(String code)` 返回一个字符串，其中同时包含代码打印到
stdout 和 stderr 的内容，以及代码求得的值。

只求值的代码返回该值：

```java
engine.execute("40 + 2");
// 42
```

只打印的代码返回打印的内容，前面带有 `Output:` 前缀：

```java
engine.execute("print('hello')");
// Output:
// hello
```

两者都做的代码返回打印的输出，后跟该值：

```java
engine.execute("print('hello')\n42");
// Output:
// hello
// Result:
// 42
```

既不打印也不求值的代码返回空字符串：

```java
engine.execute("x = 1");
// (empty string)
```

如果代码失败，会抛出 `PolyglotException`，
代码在失败前打印的任何内容都会丢失。


## 示例

- [GraalVmJavaScriptExecutionEngineTest](https://github.com/langchain4j/langchain4j/blob/main/code-execution-engines/langchain4j-code-execution-engine-graalvm-polyglot/src/test/java/dev/langchain4j/code/graalvm/GraalVmJavaScriptExecutionEngineTest.java)
- [GraalVmJavaScriptExecutionToolIT](https://github.com/langchain4j/langchain4j/blob/main/code-execution-engines/langchain4j-code-execution-engine-graalvm-polyglot/src/test/java/dev/langchain4j/agent/tool/graalvm/GraalVmJavaScriptExecutionToolIT.java)
- [GraalVmPythonExecutionEngineTest](https://github.com/langchain4j/langchain4j/blob/main/code-execution-engines/langchain4j-code-execution-engine-graalvm-polyglot/src/test/java/dev/langchain4j/code/graalvm/GraalVmPythonExecutionEngineTest.java)
- [GraalVmPythonExecutionToolIT](https://github.com/langchain4j/langchain4j/blob/main/code-execution-engines/langchain4j-code-execution-engine-graalvm-polyglot/src/test/java/dev/langchain4j/agent/tool/graalvm/GraalVmPythonExecutionToolIT.java)
