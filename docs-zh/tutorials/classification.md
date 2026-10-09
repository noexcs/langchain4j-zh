# 分类

## **概述**
本文档介绍了一个使用 **LangChain4j** 在 Java 中实现的分类系统。分类对于将文本归类到预定义标签（例如**情感分析、意图检测**和**实体识别**）这一任务来说至关重要。

本示例演示了如何使用 LangChain4j 的 AI 驱动服务进行**情感分类**。

---

LangChain4j 支持三种常见的文本分类方法：

- 当标签依赖于细致的自然语言推理时，通过 **AI 服务** 使用 LLM。
- 当每个类别都有标注好的示例，并且希望按语义相似度进行分类时，通过 `TextClassifier` 和 `EmbeddingModelTextClassifier` 使用**嵌入**。
- 当你希望在没有训练数据的情况下获得带有各标签概率的答案时，通过[决策服务](decision-services.md)使用**决策模型**。专用决策模型通常比聊天模型更快、成本更低。

## **情感分类服务**
情感分类系统将输入文本归类为以下**情感类别**之一：
- **POSITIVE**
- **NEUTRAL**
- **NEGATIVE**

### **实现**
```java
import dev.langchain4j.model.chat.ChatModel;
import dev.langchain4j.model.openai.OpenAiChatModel;
import dev.langchain4j.service.AiServices;
import dev.langchain4j.service.UserMessage;

public class SentimentClassification {

    // Initialize the chat model using OpenAI
    static ChatModel chatModel = OpenAiChatModel.withApiKey("YOUR_OPENAI_API_KEY");

    // Define the Sentiment enum
    enum Sentiment {
        POSITIVE, NEUTRAL, NEGATIVE
    }

    // Define the AI-powered Sentiment Analyzer interface
    interface SentimentAnalyzer {

        @UserMessage("Analyze sentiment of {{it}}")
        Sentiment analyzeSentimentOf(String text);

        @UserMessage("Does {{it}} have a positive sentiment?")
        boolean isPositive(String text);
    }

    public static void main(String[] args) {

        // Create an AI-powered Sentiment Analyzer instance
        SentimentAnalyzer sentimentAnalyzer = AiServices.create(SentimentAnalyzer.class, chatModel);

        // Example Sentiment Analysis
        Sentiment sentiment = sentimentAnalyzer.analyzeSentimentOf("I love this product!");
        System.out.println(sentiment); // Expected Output: POSITIVE

        boolean positive = sentimentAnalyzer.isPositive("This is a terrible experience.");
        System.out.println(positive); // Expected Output: false
    }
}
```

---

## **组件说明**

### **1. 聊天模型初始化**
```java
static ChatModel chatModel = OpenAiChatModel.withApiKey("YOUR_OPENAI_API_KEY");
```
- 初始化 **OpenAI 聊天模型**以处理自然语言文本。
- 将 `"YOUR_OPENAI_API_KEY"` 替换为真实的 OpenAI API 密钥。

### **2. 定义情感类别**
```java
enum Sentiment {
    POSITIVE, NEUTRAL, NEGATIVE
}
```
- `Sentiment` 枚举表示可能的情感分类。

### **3. 创建 AI 驱动的情感分析器**
```java
interface SentimentAnalyzer {
    
    @UserMessage("Analyze sentiment of {{it}}")
    Sentiment analyzeSentimentOf(String text);

    @UserMessage("Does {{it}} have a positive sentiment?")
    boolean isPositive(String text);
}
```
- 该接口定义了两个 AI 驱动的方法：
    - `analyzeSentimentOf(String text)`：将给定文本分类为 **POSITIVE、NEUTRAL** 或 **NEGATIVE**。
    - `isPositive(String text)`：如果文本具有积极情感则返回 `true`，否则返回 `false`。

### **4. 创建 AI 服务实例**
```java
SentimentAnalyzer sentimentAnalyzer = AiServices.create(SentimentAnalyzer.class, chatModel);
```
- `AiServices.create()` 使用 AI 模型动态实现 `SentimentAnalyzer` 接口。

### **5. 运行情感分析**
```java
Sentiment sentiment = sentimentAnalyzer.analyzeSentimentOf("I love this product!");
System.out.println(sentiment); // Output: POSITIVE

boolean positive = sentimentAnalyzer.isPositive("This is a terrible experience.");
System.out.println(positive); // Output: false
```
- AI 模型将给定文本分类到预定义的情感类别之一。
- `isPositive()` 方法返回布尔结果。

---

## **基于嵌入的分类**

`EmbeddingModelTextClassifier` 通过对输入进行嵌入，并将其与每个标签的嵌入示例进行比较来对文本进行分类。当你能够为每个类别提供有代表性的示例，并且不需要为每次分类请求调用 LLM 时，这种方法会很有用。

```java
import dev.langchain4j.classification.EmbeddingModelTextClassifier;
import dev.langchain4j.classification.TextClassifier;
import dev.langchain4j.model.embedding.EmbeddingModel;
import dev.langchain4j.model.embedding.onnx.allminilml6v2q.AllMiniLmL6V2QuantizedEmbeddingModel;

import java.util.List;
import java.util.Map;

public class EmbeddingBasedSentimentClassification {

    enum Sentiment {
        POSITIVE, NEUTRAL, NEGATIVE
    }

    public static void main(String[] args) {

        Map<Sentiment, List<String>> examples = Map.of(
                Sentiment.POSITIVE, List.of("This is great!", "I love this product."),
                Sentiment.NEUTRAL, List.of("It is okay.", "This works as expected."),
                Sentiment.NEGATIVE, List.of("This is terrible.", "I am disappointed."));

        EmbeddingModel embeddingModel = new AllMiniLmL6V2QuantizedEmbeddingModel();

        TextClassifier<Sentiment> classifier = new EmbeddingModelTextClassifier<>(embeddingModel, examples);

        List<Sentiment> sentiments = classifier.classify("Awesome experience!");
        System.out.println(sentiments); // [POSITIVE]
    }
}
```

当你需要每个返回标签的相似度分数时，还可以使用 `classifyWithScores(...)`。根据 `maxResults`、`minScore` 和 `meanToMaxScoreRatio` 的设置，分类器可以返回零个、一个或多个标签。

---

## **用例**
该情感分类服务可用于各种应用场景，包括：

✅ **客户反馈分析**：将客户评论分类为积极、中性或消极。  
✅ **社交媒体监控**：分析社交媒体评论中的情感趋势。  
✅ **聊天机器人回复**：理解用户情感，以提供更好的回复。


## 示例

- [使用 LLM 进行分类的示例](https://github.com/langchain4j/langchain4j-examples/blob/5c5fc14613101a84fe32b39200e30701fec45194/other-examples/src/main/java/OtherServiceExamples.java#L27)
- [使用嵌入进行分类的示例](https://github.com/langchain4j/langchain4j-examples/blob/main/other-examples/src/main/java/embedding/classification/EmbeddingModelTextClassifierExample.java)
