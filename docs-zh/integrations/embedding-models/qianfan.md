# Qianfan

[百度智能云千帆大模型](https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application)
![image](https://github.com/langchain4j/langchain4j/assets/95265298/600f8006-4484-4a75-829c-c8c16a3130c2)

## Maven 依赖

你可以在纯 Java 或 Spring Boot 应用程序中通过 LangChain4j 使用 DashScope。

### 纯 Java

!!! note
   自 `1.0.0-alpha1` 起，`langchain4j-qianfan` 已迁移到 `langchain4j-community`，并更名为 `langchain4j-community-qianfan`。

`1.0.0-alpha1` 之前：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-qianfan</artifactId>
    <version>${previous version here}</version>
</dependency>
```

`1.0.0-alpha1` 及之后：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-qianfan</artifactId>
    <version>${latest version here}</version>
</dependency>
```

### Spring Boot

!!! note
   自 `1.0.0-alpha1` 起，`langchain4j-qianfan-spring-boot-starter` 已迁移到 `langchain4j-community`，并更名为
   `langchain4j-community-qianfan-spring-boot-starter`。

`1.0.0-alpha1` 之前：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-qianfan-spring-boot-starter</artifactId>
    <version>${previous version here}</version>
</dependency>
```

`1.0.0-alpha1` 及之后：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-qianfan-spring-boot-starter</artifactId>
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

- `QianfanEmbeddingModel`


## 示例

- [QianfanEmbeddingModelIT](https://github.com/langchain4j/langchain4j-community/blob/main/models/langchain4j-community-qianfan/src/test/java/dev/langchain4j/community/model/qianfan/QianfanEmbeddingModelIT.java)
