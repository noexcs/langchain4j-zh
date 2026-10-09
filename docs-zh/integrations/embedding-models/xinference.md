# Xinference

- https://inference.readthedocs.io/


## Maven 依赖

`1.0.0-alpha1` 及更高版本：

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-xinference</artifactId>
    <version>${latest version here}</version>
</dependency>
```

或者，你可以使用 BOM 来统一管理依赖：

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

## 接口

- `XinferenceEmbeddingModel`


## 示例

- [XinferenceEmbeddingModelIT](https://github.com/langchain4j/langchain4j-community/blob/main/models/langchain4j-community-xinference/src/test/java/dev/langchain4j/community/model/xinference/XinferenceEmbeddingModelIT.java)
