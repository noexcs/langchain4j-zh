# Infinispan

Infinispan 是一个开源（Apache 2 许可）的内存键值数据库和缓存，几乎可以存储任何类型的数据，从纯文本
到结构化对象，专为高性能、可扩展性和低延迟数据访问而设计。
它支持嵌入式和客户端-服务器两种模式，应用程序既可以将其用作本地缓存，
也可以将其用作远程服务器数据库。

Infinispan 使用 Java 构建，提供持久化、事务、
查询（包括全文检索和向量搜索）、集群以及基于 Protobuf 的数据索引等功能——使其适用于
从简单缓存到微服务和 AI 应用中复杂实时数据处理的多种场景。

更多信息见 https://infinispan.org/

从 Infinispan Server 15.2 及以上版本开始，支持元数据过滤。

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-infinispan</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```


## API

- `InfinispanEmbeddingStore`


## 示例

- [InfinispanEmbeddingStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/infinispan-example/src/main/java/InfinispanEmbeddingStoreExample.java)
