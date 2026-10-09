# Oracle Coherence

https://coherence.community/

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-coherence</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

`langchain4j-coherence` 模块将 Coherence 作为 provided 依赖，因为它适用于各种 Coherence 版本。
开发者应包含相关的 Coherence 依赖，无论是社区版（Community Edition）还是商业版。
Coherence CE 的 groupId 为 `com.oracle.coherence.ce`，商业版的 groupId 为 `com.oracle.coherence`。

例如，要使用社区版（CE），将 Coherence BOM 添加到依赖管理部分，然后将 Coherence 添加为依赖。
之后，可以按需向项目中添加其他 Coherence 模块。

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>com.oracle.coherence.ce</groupId>
            <artifactId>coherence-bom</artifactId>
            <version>24.09</version>
            <type>pom</type>
            <scope>import</scope>
        </dependency>
    </dependencies>
</dependencyManagement>

<dependencies>
    <dependency>
        <groupId>dev.langchain4j</groupId>
        <artifactId>langchain4j-coherence</artifactId>
        <version>1.22.0-beta32</version>
    </dependency>
    <dependency>
        <groupId>com.oracle.coherence.ce</groupId>
        <artifactId>coherence</artifactId>
    </dependency>
</dependencies>
```

## API

- `CoherenceEmbeddingStore`
- `CoherenceChatMemoryStore`

## 示例

- [CoherenceEmbeddingStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/oracle-coherence-example/src/main/java/CoherenceEmbeddingStoreExample.java)
