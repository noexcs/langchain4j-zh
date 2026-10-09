# 构建 Java MCP stdio 服务器

LangChain4j 提供了一个 MCP **客户端**（`langchain4j-mcp`），用于连接 MCP 服务器。
如果你想构建一个基于 Java 的 MCP **stdio 服务器**（由 MCP 客户端启动的本地子进程），
请使用社区模块：`langchain4j-community-mcp-server`。

本指南展示了通过 stdio 以 MCP（JSON-RPC）方式暴露现有带 `@Tool` 注解方法的最小配置。

## 添加依赖

添加 BOM（推荐）：

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>dev.langchain4j</groupId>
            <artifactId>langchain4j-bom</artifactId>
            <version>${latest version here}</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
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

然后添加社区 MCP 服务器依赖：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-mcp-server</artifactId>
</dependency>
```

## 实现工具

使用 `@Tool` 暴露你的功能：

```java
import dev.langchain4j.agent.tool.P;
import dev.langchain4j.agent.tool.Tool;

class Calculator {

    @Tool
    long add(@P("a") long a, @P("b") long b) {
        return a + b;
    }
}
```

## 启动 stdio 服务器

```java
import dev.langchain4j.community.mcp.server.McpServer;
import dev.langchain4j.community.mcp.server.transport.StdioMcpServerTransport;
import dev.langchain4j.mcp.protocol.McpImplementation;
import java.util.List;

public class McpServerMain {

    public static void main(String[] args) throws Exception {
        McpImplementation serverInfo = new McpImplementation();
        serverInfo.setName("my-java-mcp-server");
        serverInfo.setVersion("1.0.0");

        McpServer server = new McpServer(List.of(new Calculator()), serverInfo);
        new StdioMcpServerTransport(System.in, System.out, server);

        // Keep the process alive while stdio is open
        Thread.currentThread().join();
    }
}
```

!!! caution
   `StdioMcpServerTransport` 会将 JSON-RPC 协议写入 `System.out`。
   请确保你的日志已配置为写入 `System.err`（否则你会破坏协议流，导致客户端断开连接）。

## 打包为可运行的 JAR

MCP 客户端（如 Claude Desktop）通常期望启动一个本地服务器进程。
将你的服务器打包为可运行（fat）JAR 是一种常见做法，但任何可运行的进程都可以。

## 配置 MCP 客户端

### Claude Desktop

在 `claude_desktop_config.json` 中添加一个服务器条目：

```json
{
  "mcpServers": {
    "my-java-tool": {
      "command": "java",
      "args": ["-jar", "/absolute/path/to/my-java-mcp-server.jar"]
    }
  }
}
```

使用绝对路径；在 Windows 上，请转义反斜杠。
