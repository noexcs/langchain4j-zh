# OVHcloud AI Endpoints

- [OVHcloud AI Endpoints 文档](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/)
- [OVHcloud AI Endpoints API 参考](https://www.ovhcloud.com/en/public-cloud/ai-endpoints/catalog/)

## 项目设置

OVHcloud AI Endpoints 模型与 OpenAI API 兼容，因此你可以使用与 OpenAI 模型相同的代码，只需更改基础 URL 和 API 密钥。

### Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai</artifactId>
    <version>1.13.0</version>
</dependency>
```

### API 密钥设置
将你的 OVHcloud AI API 密钥添加到项目中。

```java
public static final String OVHAI_AI_API_KEY = System.getenv("OVHAI_AI_API_KEY");
```
别忘了将你的 API 密钥设置为环境变量。
```shell
export OVHAI_AI_API_KEY=your-api-key #For Unix OS based
SET OVHAI_AI_API_KEY=your-api-key #For Windows OS
```
有关如何获取 OVHcloud AI API 密钥的更多详细信息，请参见[此处](https://help.ovhcloud.com/csm/en-public-cloud-ai-endpoints-getting-started?id=kb_article_view&sysparm_article=KB0065403)

## 嵌入
OVHcloud AI Embeddings 模型允许你对句子进行嵌入，在应用中用它很简单。我们提供了一个简单示例，帮助你开始使用 OVHcloud AI Embeddings 模型集成。

创建一个类并添加以下代码。

```java
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.ovhai.OvhAiEmbeddingModel;
import dev.langchain4j.store.embedding.EmbeddingMatch;
import dev.langchain4j.store.embedding.EmbeddingStore;
import dev.langchain4j.store.embedding.inmemory.InMemoryEmbeddingStore;

import java.util.List;

public class OvhAiEmbeddingSimpleExample {

    public static void main(String[] args) {
        EmbeddingModel model = OpenAiEmbeddingModel.builder()
                .baseUrl("https://oai.endpoints.kepler.ai.cloud.ovh.net/v1")
                .apiKey(System.getenv("OVHAI_AI_API_KEY"))
                .modelName("Qwen3-Embedding-8B")
                .logRequests(true)
                .logResponses(false) // embeddings are huge in logs
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

当然，你可以将 OVHCloud Embeddings 与 RAG（检索增强生成）技术结合使用。

在 [RAG](../../tutorials/rag.md) 中，你将学习如何使用 LangChain4j 运用 RAG 技术进行摄入、检索和高级检索。

许多参数在幕后设置，例如超时、模型类型和模型参数。
在[设置模型参数](../../tutorials/model-parameters.md)中，你将学习如何显式设置这些参数。

### 更多示例
如果你想查看更多示例，可以在 [langchain4j-examples](https://github.com/langchain4j/langchain4j-examples) 项目中找到。