# Google Cloud Vertex AI Ranking API

- [Google Cloud Vertex AI Ranking 文档](https://cloud.google.com/generative-ai-app-builder/docs/ranking)
- [Google Cloud Vertex AI Ranking API 说明](https://cloud.google.com/generative-ai-app-builder/docs/reference/rest/v1/projects.locations.rankingConfigs/rank)


### 简介

Google Cloud Vertex AI Ranking API 是一款强大的工具，它通过优化检索文档与给定查询的相关性来提升搜索结果。
与传统搜索方法不同，它利用先进的机器学习算法来理解查询和文档双方的语义上下文，从而提供更精确、更相关的结果。
通过分析查询与每篇文档之间的语义关系，该 API 可以根据计算出的相关度分数对候选文档重新排序，确保最相关的结果
出现在搜索结果页面顶部。

### Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-vertex-ai</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

### 使用方法

要配置模型，你必须指定：
* Google Cloud 项目 ID， 
* 项目编号， 
* 位置（例如 `us-central1`、`europe-west1`）， 
* 以及你想使用的模型。

> 注意：你可以在 Google Cloud 控制台中找到项目编号，也可以通过运行 `gcloud projects describe your-project-id` 来获取。

借助 `score(text, query)` 和 `score(segment, query)` 方法，
你可以将单个字符串或 `TextSegment` 针对查询进行评分。

你也可以使用 `scoreAll(segments, query)` 方法，
将多个字符串或 `TextSegment` 针对查询进行评分：

```java
VertexAiScoringModel scoringModel = VertexAiScoringModel.builder()
    .projectId(System.getenv("GCP_PROJECT_ID"))
    .projectNumber(System.getenv("GCP_PROJECT_NUM"))
    .projectLocation(System.getenv("GCP_LOCATION"))
    .model("semantic-ranker-512")
    .build();

Response<List<Double>> score = scoringModel.scoreAll(Stream.of(
        "The sky appears blue due to a phenomenon called Rayleigh scattering. " +
            "Sunlight is comprised of all the colors of the rainbow. Blue light has shorter " +
            "wavelengths than other colors, and is thus scattered more easily.",

        "A canvas stretched across the day,\n" +
            "Where sunlight learns to dance and play.\n" +
            "Blue, a hue of scattered light,\n" +
            "A gentle whisper, soft and bright."
        ).map(TextSegment::from).collect(Collectors.toList()),
    "Why is the sky blue?");

// [0.8199999928474426, 0.4300000071525574]
```

如果你传入带有特定 `title` 键的 `TextSegment`，Ranker 模型可以在计算中考虑这一元数据。
要指定自定义的标题键，可以使用 `titleMetadataKey()` builder 方法。

你可以将评分模型与 `AiServices` 及其 `contentAgregator()` 方法一起使用，
该方法接受一个可以指定评分模型的 `ContentAggregator` 类：

```java
VertexAiScoringModel scoringModel = VertexAiScoringModel.builder()
    .projectId(System.getenv("GCP_PROJECT_ID"))
    .projectNumber(System.getenv("GCP_PROJECT_NUM"))
    .projectLocation(System.getenv("GCP_LOCATION"))
    .model("semantic-ranker-512")
    .build();

ContentAggregator contentAggregator = ReRankingContentAggregator.builder()
    .scoringModel(scoringModel)
    ... 
    .build();

RetrievalAugmentor retrievalAugmentor = DefaultRetrievalAugmentor.builder()
    ...
    .contentAggregator(contentAggregator)
    .build();

return AiServices.builder(Assistant.class)
    .chatModel(...)
    .retrievalAugmentor(retrievalAugmentor)
    .build();
```
