# Redis

https://redis.io/


## Maven 依赖

你可以在纯 Java 或 Spring Boot 应用程序中将 Redis 与 LangChain4j 一起使用。

### 纯 Java

!!! note
   自 `1.0.0-beta1` 起，`langchain4j-redis` 已迁移到 `langchain4j-community` 并更名为
   `langchain4j-community-redis`。

`1.0.0-beta1` 之前：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-redis</artifactId>
    <version>${previous version here}</version>
</dependency>
```

`1.0.0-beta1` 及之后版本：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-redis</artifactId>
    <version>${latest version here}</version>
</dependency>
```

### Spring Boot

!!! note
   自 `1.0.0-beta1` 起，`langchain4j-redis-spring-boot-starter` 已迁移到 `langchain4j-community` 并更名为
   `langchain4j-community-redis-spring-boot-starter`。

`1.0.0-beta1` 之前：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-redis-spring-boot-starter</artifactId>
    <version>${previous version here}</version>
</dependency>
```

`1.0.0-beta1` 及之后版本：

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-redis-spring-boot-starter</artifactId>
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

- `RedisEmbeddingStore`


## 示例

- [RedisEmbeddingStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/redis-example/src/main/java/RedisEmbeddingStoreExample.java)