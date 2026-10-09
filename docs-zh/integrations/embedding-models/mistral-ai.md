# Mistral AI
[MistralAI 文档](https://docs.mistral.ai/)

### 项目设置

要将 langchain4j 安装到你的项目中，请添加以下依赖：

对于 Maven 项目 `pom.xml`

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j</artifactId>
    <version>1.22.0</version>
</dependency>

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-mistral-ai</artifactId>
    <version>1.22.0</version>
</dependency>
```

对于 Gradle 项目 `build.gradle`

```groovy
implementation 'dev.langchain4j:langchain4j:1.22.0'
implementation 'dev.langchain4j:langchain4j-mistral-ai:1.22.0'
```
#### API 密钥设置
将你的 MistralAI API 密钥添加到项目中，你可以创建一个类 ```ApiKeys.java```，代码如下

```java
public class ApiKeys {
    public static final String MISTRALAI_API_KEY = System.getenv("MISTRAL_AI_API_KEY");
}
```
别忘了将你的 API 密钥设置为环境变量。
```shell
export MISTRAL_AI_API_KEY=your-api-key #For Unix OS based
SET MISTRAL_AI_API_KEY=your-api-key #For Windows OS
```
有关如何获取 MistralAI API 密钥的更多详细信息，请参见[此处](https://docs.mistral.ai/#api-access)

## 嵌入
MistralAI Embeddings 模型允许你对句子进行嵌入，在应用中用它很简单。我们提供了一个简单示例，帮助你开始使用 MistralAI Embeddings 模型集成。

创建一个类并添加以下代码。

```java
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.mistralai.MistralAiEmbeddingModel;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingMatch;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;

import java.util.List;

public class HelloWorld {
    public static void main(String[] args) {
        EmbeddingModel embeddingModel = MistralAiEmbeddingModel.builder()
                .apiKey(System.getenv("MISTRAL_AI_API_KEY"))
                .modelName("mistral-embed")
                .build();

        // For simplicity, this example uses an in-memory store, but you can choose any external compatible store for production environments.
        EmbeddingStore<TextSegment> embeddingStore = new InMemoryEmbeddingStore<>();

        TextSegment segment1 = TextSegment.from("I like football.");
        Embedding embedding1 = embeddingModel.embed(segment1).content();
        embeddingStore.add(embedding1, segment1);
        
        TextSegment segment2 = TextSegment.from("The weather is good today.");
        Embedding embedding2 = embeddingModel.embed(segment2).content();
        embeddingStore.add(embedding2, segment2);
        
        String userQuery = "What is your favourite sport?";
        Embedding queryEmbedding = embeddingModel.embed(userQuery).content();
        EmbeddingSearchRequest searchRequest = EmbeddingSearchRequest.builder()
                .queryEmbedding(queryEmbedding)
                .maxResults(1)
                .build();
        EmbeddingSearchResult<TextSegment> searchResult = embeddingStore.search(searchRequest);
        EmbeddingMatch<TextSegment> embeddingMatch = searchResult.matches().get(0);

        System.out.println("Question: " + userQuery); // What is your favourite sport?
        System.out.println("Response: " + embeddingMatch.embedded().text()); // I like football.
    }
}
```
在此示例中，我们将添加 2 个文本段，但 LangChain4j 提供内置支持，可从多种来源加载文档：
文件系统、URL、Amazon S3、Azure Blob Storage、GitHub、Tencent COS。
此外，LangChain4j 支持解析多种文档类型：
text、pdf、doc、xls、ppt。

输出类似于以下内容：

```plaintext
Question: What is your favourite sport?
Response: I like football.
```

当然，你可以将 MistralAI Embeddings 与 RAG（检索增强生成）技术结合使用。

在 [RAG](../../tutorials/rag.md) 中，你将学习如何使用 LangChain4j 运用 RAG 技术进行摄入、检索和高级检索。

许多参数在幕后设置，例如超时、模型类型和模型参数。
在[设置模型参数](../../tutorials/model-parameters.md)中，你将学习如何显式设置这些参数。

### 更多示例
如果你想查看更多示例，可以在 [langchain4j-examples](https://github.com/langchain4j/langchain4j-examples) 项目中找到。