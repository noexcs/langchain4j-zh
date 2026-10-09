# Hazelcast

[Hazelcast](https://hazelcast.com/) 是一个分布式内存数据网格和计算平台。
LangChain4j 通过两个模块与 Hazelcast 集成，拆分的方式使开源路径
不依赖任何企业版/许可要求：

- **`langchain4j-community-hazelcast`**（开源）— 提供 `HazelcastChatMemoryStore`，
  一个由 Hazelcast `IMap` 支持的 `ChatMemoryStore`。针对开源的 Community Edition
  运行，无需许可证。
- **`langchain4j-community-hazelcast-enterprise`**（需要 Hazelcast Enterprise）— 提供
  `HazelcastEmbeddingStore`（通过 `VectorCollection` 进行向量搜索）和
  `HazelcastCPMapChatMemoryStore`（一个强一致的、由 CP Subsystem 支持的聊天记忆存储）。
  此模块重新导出了 `langchain4j-community-hazelcast`，因此企业版使用者也可以从单个依赖中获得
  基于 `IMap` 的存储。

## Maven 依赖

### 开源（聊天记忆存储）

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-hazelcast</artifactId>
    <version>${latest version here}</version>
</dependency>
```

Hazelcast 依赖为 `provided`，因此请添加你所运行的版本。默认为开源的 Community Edition：

```xml
<dependency>
    <groupId>com.hazelcast</groupId>
    <artifactId>hazelcast</artifactId>
    <version>5.7.0</version>
</dependency>
```

### Hazelcast Enterprise（嵌入存储 + CP 聊天记忆）

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-community-hazelcast-enterprise</artifactId>
    <version>${latest version here}</version>
</dependency>
```

或者使用 BOM 来统一管理版本：

```xml
<dependencyManagement>
    <dependencies>
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

!!! note
   `HazelcastEmbeddingStore` 和 `HazelcastCPMapChatMemoryStore` 需要 **Hazelcast Enterprise**。
   `com.hazelcast:hazelcast-enterprise` 不在 Maven Central 上——它由
   `langchain4j-community-hazelcast-enterprise` 传递引入，但你必须添加 Hazelcast release 仓库和一个
   有效的 Enterprise 许可证密钥：

   ```xml
   <repositories>
       <repository>
           <id>hazelcast-release</id>
           <name>Hazelcast Release Repository</name>
           <url>https://repository.hazelcast.com/release/</url>
       </repository>
   </repositories>
   ```

   通过 `config.setLicenseKey(...)` 或 `HZ_LICENSEKEY` 环境变量提供许可证密钥。
   `HazelcastCPMapChatMemoryStore` 还要求启用 CP Subsystem；否则它会快速失败
   （fail fast）。

## 聊天记忆存储

`HazelcastChatMemoryStore`（开源）将每个聊天记忆作为 `ChatMessage` 的 JSON 序列化列表
存储在 Hazelcast `IMap` 中。你提供的 `HazelcastInstance` 可以是嵌入式成员，
也可以是瘦客户端——构建器不区分二者。

```java
// Embedded member
HazelcastInstance hz = Hazelcast.newHazelcastInstance(new Config());

ChatMemoryStore store = HazelcastChatMemoryStore.builder()
        .hazelcastInstance(hz)
        .name("chatMemory") // optional, defaults to "chatMemory"
        .build();
```

```java
// Client connecting to an external cluster
ClientConfig clientConfig = new ClientConfig();
clientConfig.getNetworkConfig().addAddress("hazelcast-host:5701");
HazelcastInstance hzClient = HazelcastClient.newHazelcastClient(clientConfig);

ChatMemoryStore store = HazelcastChatMemoryStore.builder()
        .hazelcastInstance(hzClient)
        .build();
```

你也可以直接使用
`HazelcastChatMemoryStore.create(IMap<String, String>)` 包装一个预先配置好的 `IMap`。

### 强一致变体（Enterprise）

`HazelcastCPMapChatMemoryStore`（Enterprise）是由 [CP Subsystem](https://docs.hazelcast.com/hazelcast/latest/cp-subsystem/cp-subsystem)
中 `CPMap` 支持的替代方案。它是**线性一致**（linearizable）
的（强一致、由 Raft 支持），避免了当同一个 `memoryId`
被并发更新时出现丢失更新的情况。实例上必须启用 CP Subsystem。

```java
Config config = new Config();
config.getCPSubsystemConfig().setCPMemberCount(3); // CP Subsystem must be enabled
HazelcastInstance hz = Hazelcast.newHazelcastInstance(config);

ChatMemoryStore store = HazelcastCPMapChatMemoryStore.builder()
        .hazelcastInstance(hz)
        .name("chatMemory")
        .build();
```

与 `IMap` 存储相比的取舍：`CPMap` **不是分区化**的（它必须能放进每个 CP
成员的 RAM 中，默认总共 100 MB），并且**没有 TTL/驱逐**。它适合许多小规模对话；
对于非常大的用户群体中无上限的历史记录，请优先选择基于 `IMap` 的存储。

## 嵌入存储

`HazelcastEmbeddingStore`（Enterprise）由 Hazelcast `VectorCollection` 支持。向量索引
的维度必须与所使用的嵌入模型匹配；度量默认为 `COSINE`。

```java
HazelcastInstance hz = Hazelcast.newHazelcastInstance(new Config());

EmbeddingStore<TextSegment> store = HazelcastEmbeddingStore.builder()
        .hazelcastInstance(hz)
        .collectionName("embeddings")   // optional, defaults to "embeddings"
        .dimension(384)                 // required, must match the embedding model
        .metric(Metric.COSINE)          // optional, defaults to COSINE
        .build();
```

你也可以用
`HazelcastEmbeddingStore.create(VectorCollection<String, TextSegmentDocument>)` 包装一个预先配置好的 `VectorCollection`。`search(...)`
返回的相关性分数是 Hazelcast 已经归一化的 COSINE 分数，直接用于结果。

### 限制

- **不支持** `removeAll(Filter)` —— `VectorCollection` 没有服务器端谓词删除；
  它会抛出 `UnsupportedFeatureException`。按 id 删除、`removeAll(Collection<String>)` 和
  `removeAll()` 是支持的。
- 搜索期间的元数据过滤**不**在服务器端执行。如果 `EmbeddingSearchRequest`
  携带过滤器，它会在**检索之后的客户端侧**应用（会记录一条警告日志），这可能导致
  返回的匹配结果少于 `maxResults`。

## API

- `HazelcastChatMemoryStore` — 基于 `IMap`（AP），开源
- `HazelcastCPMapChatMemoryStore` — 基于 `CPMap`（CP，线性一致），Enterprise
- `HazelcastEmbeddingStore` — 基于 `VectorCollection` 的向量存储，Enterprise

## 示例

- [HazelcastChatMemoryStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/hazelcast-example/src/main/java/HazelcastChatMemoryStoreExample.java)
- [HazelcastCPMapChatMemoryStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/hazelcast-example/src/main/java/HazelcastCPMapChatMemoryStoreExample.java)
- [HazelcastEmbeddingStoreExample](https://github.com/langchain4j/langchain4j-examples/blob/main/hazelcast-example/src/main/java/HazelcastEmbeddingStoreExample.java)
