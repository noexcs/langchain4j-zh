# Qianfan

[百度智能云千帆大模型](https://console.bce.baidu.com/qianfan/ais/console/applicationConsole/application)
![image](https://github.com/langchain4j/langchain4j/assets/95265298/600f8006-4484-4a75-829c-c8c16a3130c2)


## Maven 依赖

你可以在纯 Java 或 Spring Boot 应用程序中结合 LangChain4j 使用 DashScope。

### 纯 Java

!!! note
    自 `1.0.0-alpha1` 起，`langchain4j-qianfan` 已迁移至 `langchain4j-community` 并重命名为 `langchain4j-community-qianfan`。

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
    自 `1.0.0-alpha1` 起，`langchain4j-qianfan-spring-boot-starter` 已迁移至 `langchain4j-community` 并重命名为
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

## QianfanChatModel

[千帆所有模型及付费状态](https://console.bce.baidu.com/qianfan/ais/console/onlineService)
```java
QianfanChatModel model = QianfanChatModel.builder()
        .apiKey("apiKey")
        .secretKey("secretKey")
        .modelName("Yi-34B-Chat") // 一个免费的模型名称 
        .build();

String answer = model.chat("雷军");

System.out.println(answer);
```
### 自定义

```java
QianfanChatModel model = QianfanChatModel.builder()
    .baseUrl(...)
    .apiKey(...)
    .secretKey(...)
    .temperature(...)
    .maxRetries(...)
    .topP(...)
    .modelName(...)
    .endpoint(...)
    .responseFormat(...)
    .penaltyScore(...)
    .logRequests(...)
    .logResponses()
    .build();
```

上述部分参数的说明见[此处](https://console.bce.baidu.com/tools/?u=qfdc#/api?product=QIANFAN&project=%E5%8D%83%E5%B8%86%E5%A4%A7%E6%A8%A1%E5%9E%8B%E5%B9%B3%E5%8F%B0&parent=Yi-34B-Chat&api=rpc%2F2.0%2Fai_custom%2Fv1%2Fwenxinworkshop%2Fchat%2Fyi_34b_chat&method=post)。
### 函数
**IAiService(重点)**
```java
public interface IAiService {
    /**
     * Ai Services 提供了一种更简单、更灵活的替代方案。 您可以定义自己的 API（具有一个或多个方法的 Java 接口）， 并将为其提供实现。
     * @param userMessage
     * @return String
     */
    String chat(String userMessage);
}
```
#### QianfanChatWithOnePersonMemory (带有一个人的聊天记忆)

```java

  QianfanChatModel model = QianfanChatModel.builder()
          .apiKey("apiKey")
          .secretKey("secretKey")
          .modelName("Yi-34B-Chat")
          .build();
  /* MessageWindowChatMemory
     functions as a sliding window, retaining the N most recent messages and evicting older ones that no longer fit.
     However, because each message can contain a varying number of tokens, MessageWindowChatMemory is mostly useful for fast prototyping.
     保留最新的n条消息(包括回复)
   */
  /* TokenWindowChatMemory
    which also operates as a sliding window but focuses on keeping the N most recent tokens, evicting older messages as needed. Messages are indivisible.
    If a message doesn't fit, it is evicted completely.
    MessageWindowChatMemory requires a TokenCountEstimator to count the tokens in each ChatMessage.
  */
  ChatMemory chatMemory = MessageWindowChatMemory.builder()
          .maxMessages(10)
          .build();

  IAiService assistant = AiServices.builder(IAiService.class)
          .chatModel(model) // the model
          .chatMemory(chatMemory)  // memory
          .build();
        String answer = assistant.chat("Hello,my name is xiaoyu");
        System.out.println(answer); // Hello xiaoyu!******

        String answerWithName = assistant.chat("What's my name?");
        System.out.println(answerWithName); // Your name is xiaoyu.******

        String answer1 = assistant.chat("I like playing football.");
        System.out.println(answer1); // The answer

        String answer2 = assistant.chat("I want to go eat delicious food.");
        System.out.println(answer2); // The answer

        String answerWithLike = assistant.chat("What I like to do?");
        System.out.println(answerWithLike);//Playing football.******
```

#### QianfanChatWithMorePersonMemory (带有多个人的聊天记忆)

```java
  QianfanChatModel model = QianfanChatModel.builder()
          .apiKey("apiKey")
          .secretKey("secretKey")
          .modelName("Yi-34B-Chat")
          .build();
  IAiService assistant = AiServices.builder(IAiService.class)
          .chatModel(model)         // the model
          .chatMemoryProvider(memoryId -> MessageWindowChatMemory.withMaxMessages(10)) // chatMemory
          .build();

  String answer = assistant.chat(1,"Hello, my name is xiaoyu");
  System.out.println(answer); // Hello xiaoyu!******
  String answer1 = assistant.chat(2,"Hello, my name is xiaomi");
  System.out.println(answer1); // Hello xiaomi!******

  String answerWithName1 = assistant.chat(1,"What's my name?");
  System.out.println(answerWithName1); // Your name is xiaoyu.
  String answerWithName2 = assistant.chat(2,"What's my name?");
  System.out.println(answerWithName2); // Your name is xiaomi.
```

#### QianfanChatWithPersistentMemory(持久化聊天记忆)

```xml
    <dependency>
        <groupId>org.mapdb</groupId>
        <artifactId>mapdb</artifactId>
        <version>3.1.0</version>
    </dependency>
```
```java
class PersistentChatMemoryStore implements ChatMemoryStore {
    private final DB db = DBMaker.fileDB("chat-memory.db").transactionEnable().make();
    private final Map<String, String> map = db.hashMap("messages", STRING, STRING).createOrOpen();

    @Override
    public List<ChatMessage> getMessages(Object memoryId) {
        String json = map.get((String) memoryId);
        return messagesFromJson(json);
    }

    @Override
    public void updateMessages(Object memoryId, List<ChatMessage> messages) {
        String json = messagesToJson(messages);
        map.put((String) memoryId, json);
        db.commit();
    }

    @Override
    public void deleteMessages(Object memoryId) {
        map.remove((String) memoryId);
        db.commit();
    }
}

class PersistentChatMemoryTest{
  public void test(){
    QianfanChatModel chatModel = QianfanChatModel.builder()
            .apiKey("apiKey")
            .secretKey("secretKey")
            .modelName("Yi-34B-Chat")
            .build();
    
    ChatMemory chatMemory = MessageWindowChatMemory.builder()
            .maxMessages(10)
            .chatMemoryStore(new PersistentChatMemoryStore())
            .build();
    
    IAiService assistant = AiServices.builder(IAiService.class)
            .chatModel(chatModel)
            .chatMemory(chatMemory)
            .build();
    
    String answer = assistant.chat("My name is xiaoyu");
    System.out.println(answer);
    // Run it once and then comment the top to run the bottom(运行一次后注释上面运行下面)
    // String answerWithName = assistant.chat("What is my name?");
    // System.out.println(answerWithName);
  }
}

```

#### QianfanStreamingChatModel(流式回复)
LLM 逐个 token 生成文本，因此许多 LLM 提供商提供了一种逐个 token 流式传输响应的方法，而不是等待整个文本生成完毕。这极大地改善了用户体验，因为用户不需要等待未知的时间，几乎可以立即开始阅读响应。（因此许多LLM提供者提供了一种逐个token地传输响应的方法，而不是等待生成整个文本。这极大地改善了用户体验，因为用户不需要等待未知的时间，几乎可以立即开始阅读响应。）
以下是一个通过StreamingChatResponseHandler来实现
```java
  QianfanStreamingChatModel qianfanStreamingChatModel = QianfanStreamingChatModel.builder()
          .apiKey("apiKey")
          .secretKey("secretKey")
          .modelName("Yi-34B-Chat")
          .build();

  qianfanStreamingChatModel.chat(userMessage, new StreamingChatResponseHandler() {

        @Override
        public void onPartialResponse(String partialResponse) {
            System.out.print(partialResponse);
        }
        @Override
        public void onCompleteResponse(ChatResponse completeResponse) {
            System.out.println("onCompleteResponse: " + completeResponse);
        }
        @Override
        public void onError(Throwable throwable) {
            throwable.printStackTrace();
        }
  });
```
以下是另一个通过TokenStream来实现
```java
  QianfanStreamingChatModel qianfanStreamingChatModel = QianfanStreamingChatModel.builder()
          .apiKey("apiKey")
          .secretKey("secretKey")
          .modelName("Yi-34B-Chat")
          .build();
  IAiService assistant = AiServices.create(IAiService.class, qianfanStreamingChatModel);
  
  TokenStream tokenStream = assistant.chatInTokenStream("Tell me a story.");
  tokenStream.onPartialResponse(System.out::println)
          .onError(Throwable::printStackTrace)
          .start();
```
#### QianfanRAG

程序自动将匹配的内容与用户问题组装成一个Prompt，向大语言模型提问，大语言模型返回答案

LangChain4j 有一个 "Easy RAG" 功能，让你可以尽可能简单地开始使用 RAG。你不需要学习嵌入、选择向量存储、找到合适的嵌入模型、弄清楚如何解析和切分文档等等。只需指向你的文档，LangChain4j 就会施展它的魔法。

- 引入依赖：langchain4j-easy-rag
```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-easy-rag</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```
- 使用
```java

  QianfanChatModel chatModel = QianfanChatModel.builder()
        .apiKey(API_KEY)
        .secretKey(SECRET_KEY)
        .modelName("Yi-34B-Chat")
        .build();
  // All files in a directory, txt seems to be faster
  List<Document> documents = FileSystemDocumentLoader.loadDocuments("/home/langchain4j/documentation");
  // for simplicity, we will use an in-memory one:
  InMemoryEmbeddingStore<TextSegment> embeddingStore = new InMemoryEmbeddingStore<>();
  EmbeddingStoreIngestor.ingest(documents, embeddingStore);

  IAiService assistant = AiServices.builder(IAiService.class)
          .chatModel(chatModel)
          .chatMemory(MessageWindowChatMemory.withMaxMessages(10))
          .contentRetriever(EmbeddingStoreContentRetriever.from(embeddingStore))
          .build();

  String answer = assistant.chat("The Question");
  System.out.println(answer);

```


## 示例

- [Qianfan Examples](https://github.com/langchain4j/langchain4j-community/tree/main/models/langchain4j-community-qianfan/src/test/java/dev/langchain4j/community/model/qianfan)
