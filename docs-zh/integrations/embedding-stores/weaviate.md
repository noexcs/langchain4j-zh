# Weaviate

https://weaviate.io/

## Maven 依赖

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-weaviate</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## API

- `WeaviateEmbeddingStore`

## 用法

| 参数 | 描述 | 必填/可选 |
|:---:|---|---|
| `apiKey` | 你的 Weaviate API 密钥。本地部署不需要。 | 可选 |
| `scheme` | 集群 URL 的协议方案，例如 "https"。可在你的 Weaviate 集群的 Details 中找到。 | 必填 |
| `host` | 集群 URL 的主机名，例如 "langchain4j-4jw7ufd9.weaviate.network"。可在你的 Weaviate 集群的 Details 中找到。 | 必填 |
| `port` | 端口，例如 8080。 | 可选 |
| `objectClass` | 要存储的对象类，例如 "MyGreatClass"。必须以大写字母开头。 | 可选（默认：`Default`） |
| `avoidDups` | 如果为 `true`（默认值），则 `WeaviateEmbeddingStore` 会基于提供的文本片段生成哈希 ID，避免数据库中产生重复条目。如果为 false，则会生成随机 ID。 | 可选（默认：`true`） |
| `consistencyLevel` | 一致性级别：`ONE`、`QUORUM`（默认）或 `ALL`。更多详情请参见[此处](https://weaviate.io/developers/weaviate/concepts/replication-architecture/consistency#tunable-write-consistency)。 | 可选（默认：`QUORUM`） |
| `useGrpcForInserts` | 仅批量插入时使用 GRPC 代替 HTTP。搜索仍需要配置 HTTP。 | 可选 |
| `securedGrpc` | GRPC 连接是加密的。 | 可选 |
| `grpcPort` | 端口，例如 50051。 | 可选 |
| `textFieldName` | 包含 `TextSegment` 文本的字段名。 | 可选（默认：`text`） |
| `metadataFieldName` | 存储 `Metadata` 条目的字段名。如果设置为空字符串（`""`），`Metadata` 条目将存储在根对象中。使用根对象时，建议使用 `metadataKeys`。 | 可选（默认：`_metadata`） |
| `metadataKeys` | 需要持久化的元数据键。 | 可选 |

## Weaviate 1.39 及更高版本

从 1.39 版本开始，Weaviate 在自动创建集合时，会将对象的嵌入存储在*命名向量*
（名为 `default`）中。旧版本的 Weaviate
使用的是单个匿名向量。

`1.22.0-beta32` 及更早版本的 `langchain4j-weaviate` 只读取单个匿名向量。
当使用这些版本配合 Weaviate 1.39 或更高版本创建的集合时，
每个搜索结果的 `EmbeddingMatch.embedding()` 都是空的。分数、ID、
`TextSegment` 及其 `Metadata` 仍能正确返回，因此只有当你的应用
使用匹配的嵌入时，这才会产生影响。

这在 `1.22.0-beta32` 中已修复，该版本读取两种布局：早期版本
存储的嵌入同样会返回，无需做任何更改。

使用 `1.22.0-beta32` 及更早版本时，请在首次使用
`WeaviateEmbeddingStore` 之前自行创建集合，并将其配置为不使用命名向量：

```java
WeaviateClient client = new WeaviateClient(new Config("https", "my-cluster.weaviate.network"));

client.schema().classCreator()
        .withClass(WeaviateClass.builder()
                .className("MyGreatClass")
                .vectorizer("none")
                .build())
        .run();
```

也可以通过一个普通的 HTTP 请求完成：

```shell
curl -X POST https://my-cluster.weaviate.network/v1/schema \
  -H 'Content-Type: application/json' \
  -d '{"class": "MyGreatClass", "vectorizer": "none"}'
```

由 Weaviate 1.38 或更早版本创建的集合不受影响。

## 示例

- [WeaviateEmbeddingStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/weaviate-example/src/main/java/WeaviateEmbeddingStoreExample.java)
