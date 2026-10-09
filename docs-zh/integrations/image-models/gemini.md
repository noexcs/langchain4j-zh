# Google AI Gemini 图像生成

Gemini 可以使用专门的图像模型以对话方式生成和编辑图像，即 **Nano Banana**（Gemini 2.5 Flash Image）和 **Nano Banana Pro**（Gemini 3 Pro Image Preview）。

## 目录

- [概述](#概述)
- [可用模型](#可用模型)
- [GoogleAiGeminiImageModel](#googleaigeminiimagemodel)
    - [基本用法](#基本用法)
    - [配置](#配置)
- [图像生成](#图像生成)
    - [文本生成图像](#文本生成图像)
    - [宽高比](#宽高比)
    - [图像尺寸](#图像尺寸)
- [图像编辑](#图像编辑)
    - [添加和移除元素](#添加和移除元素)
    - [风格迁移](#风格迁移)
    - [图像修补](#图像修补)
- [批量图像生成](#批量图像生成)
- [限制](#限制)
- [资源](#资源)

## 概述

Gemini 的原生图像生成能力允许你：

- **文本生成图像**：从文本描述生成高质量图像
- **图像编辑**：在现有图像中添加、移除或修改元素
- **风格迁移**：将艺术风格应用到图像
- **迭代细化**：在多个对话轮次中以对话方式细化图像
- **高保真文本渲染**：生成带有清晰、位置得当的文本的图像

所有生成的图像都包含 [SynthID 水印](https://ai.google.dev/responsible/docs/safeguards/synthid)。

## 可用模型

| 模型 | 描述 | 最大分辨率 | 最大输入图像数 |
|-------|-------------|----------------|------------------|
| `gemini-2.5-flash-image` | 快速、高效的图像生成（Nano Banana） | 1024px | 3 |
| `gemini-3-pro-image-preview` | 高级功能、思考模式、Google Search 接地（Nano Banana Pro） | 4K | 14 |

## GoogleAiGeminiImageModel

### 基本用法

```java
ImageModel imageModel = GoogleAiGeminiImageModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash-image")
    .build();

Response<Image> response = imageModel.generate(
    "A nano banana dish in a fancy restaurant with a Gemini theme"
);

// Save the generated image
Image image = response.content();
byte[] imageBytes = Base64.getDecoder().decode(image.base64Data());
Files.write(Paths.get("nano-banana.png"), imageBytes);
```

### 配置

```java
ImageModel imageModel = GoogleAiGeminiImageModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-3-pro-image-preview")
    .aspectRatio("16:9")              // Output aspect ratio
    .imageSize("2K")                   // Resolution (Gemini 3 Pro only)
    .timeout(Duration.ofSeconds(120))
    .maxRetries(3)
    .logRequestsAndResponses(true)
    .safetySettings(...)               // Content safety settings
    .build();
```

## 图像生成

### 文本生成图像

根据描述性文本提示词生成图像：

```java
ImageModel imageModel = GoogleAiGeminiImageModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash-image")
    .build();

// Photorealistic style
Response<Image> photo = imageModel.generate("""
    A photorealistic close-up portrait of an elderly Japanese ceramicist
    with deep wrinkles and a warm smile, inspecting a tea bowl.
    Soft golden hour light, 85mm portrait lens, shallow depth of field.
    """);

// Stylized illustration
Response<Image> sticker = imageModel.generate("""
    A kawaii-style sticker of a happy red panda wearing a bamboo hat,
    munching on a leaf. Bold outlines, cel-shading, vibrant colors,
    white background.
    """);

// Logo design
Response<Image> logo = imageModel.generate("""
    A modern, minimalist logo for 'The Daily Grind' coffee shop.
    Clean, bold sans-serif font. Black and white. Circular design
    with a clever coffee bean element.
    """);
```

### 宽高比

两种模型支持的宽高比：

| 宽高比 | 使用场景 |
|--------------|----------|
| `1:1` | 正方形，社交媒体帖子 |
| `2:3`, `3:2` | 竖版/横版照片 |
| `3:4`, `4:3` | 标准照片 |
| `4:5`, `5:4` | Instagram 帖子 |
| `9:16`, `16:9` | Stories、YouTube 缩略图 |
| `21:9` | 电影感、超宽屏 |

```java
ImageModel imageModel = GoogleAiGeminiImageModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash-image")
    .aspectRatio("16:9")  // Widescreen format
    .build();
```

### 图像尺寸

**Gemini 3 Pro Image Preview** 支持更高分辨率：

| 尺寸 | 描述 |
|------|-------------|
| `1K` | 默认分辨率 |
| `2K` | 更高分辨率 |
| `4K` | 最大分辨率 |

```java
ImageModel imageModel = GoogleAiGeminiImageModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-3-pro-image-preview")
    .aspectRatio("1:1")
    .imageSize("4K")  // High resolution output
    .build();
```

## 图像编辑

### 添加和移除元素

通过将现有图像与文本提示词一起提供来编辑它们：

```java
ImageModel imageModel = GoogleAiGeminiImageModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash-image")
    .build();

// Load the source image
Image sourceImage = Image.builder()
    .base64Data(Base64.getEncoder().encodeToString(
        Files.readAllBytes(Paths.get("cat.png"))))
    .mimeType("image/png")
    .build();

Response<Image> edited = imageModel.edit(
    sourceImage,
    "Add a small wizard hat on the cat's head. " +
    "Make it look natural with matching lighting."
);
```

### 风格迁移

将图像转换为不同的艺术风格：

```java
Image cityPhoto = // ... load your image

Response<Image> stylized = imageModel.edit(
    cityPhoto,
    "Transform this city street into Vincent van Gogh's 'Starry Night' style. " +
    "Preserve the composition but render with swirling brushstrokes " +
    "and a dramatic palette of deep blues and bright yellows."
);
```

### 图像修补

修改特定元素，同时保留其余部分：

```java
Image livingRoom = // ... load your image

Response<Image> edited = imageModel.edit(
    livingRoom,
    "Change only the blue sofa to a vintage brown leather chesterfield. " +
    "Keep everything else exactly the same."
);
```

## 批量图像生成

如需大规模生成多张图像并降低成本 50%：

```java
GoogleAiGeminiBatchImageModel batchModel = GoogleAiGeminiBatchImageModel.builder()
    .apiKey(System.getenv("GOOGLE_AI_GEMINI_API_KEY"))
    .modelName("gemini-2.5-flash-image")
    .build();

List<String> prompts = List.of(
    "A nano banana dish in a Gemini-themed restaurant",
    "A kawaii sticker of a banana wearing a chef hat",
    "A photorealistic banana split dessert",
    "A minimalist logo for 'Nano Banana Co.'"
);

// Submit batch
BatchResponse<Response<Image>> response = batchModel.submit(GeminiBatchRequest.from(
    prompts, "image-batch"));
String batchId = response.batchId();

// Poll for completion
while (!response.state().isTerminal()) {
    Thread.sleep(10000);
    response = batchModel.retrieve(batchId);
}

// Process results
if (response.state() == BatchState.SUCCEEDED) {
    for (Response<Image> imageResponse : response.responses()) {
        Image image = imageResponse.content();
        byte[] imageBytes = Base64.getDecoder().decode(image.base64Data());
        // Save or process each image
    }
}

// Clean up
batchModel.deleteBatchJob(batchId);
```

`responses()` 和 `errors()` 是扁平的便捷视图（永不为 `null`，没有可报告内容时为空），它们不告诉你哪个提示词生成了哪张图像。要将每个结果映射回其提示词，请使用 `results()`：它按请求各返回一个 `BatchItemResult`，**与提交的提示词顺序相同**，每个都是 `BatchItemResult.Success`（带 `response()`）或 `BatchItemResult.Failure`（带 `error()`）：

```java
List<BatchItemResult<Response<Image>>> results = response.results();
for (int i = 0; i < results.size(); i++) {
    BatchItemResult<Response<Image>> item = results.get(i);
    if (item.isSuccess()) {
        Image image = item.response().content();
        // Save or process the image generated for prompts.get(i)
    } else {
        BatchError error = item.error();
        System.err.println("Prompt #" + i + " failed: " + error.code() + " - " + error.message());
    }
}
```

## 限制

- **语言**：英文（EN）效果最佳，支持的语言包括 ar-EG、de-DE、es-MX、fr-FR、hi-IN、id-ID、it-IT、ja-JP、ko-KR、pt-BR、ru-RU、vi-VN、zh-CN
- **输入**：图像生成不支持音频和视频输入
- **输出数量**：模型不一定始终生成所请求的确切图像数量
- **输入图像**：
    - `gemini-2.5-flash-image`：最多 3 张输入图像
    - `gemini-3-pro-image-preview`：最多 14 张输入图像（包括用于保持一致性的 5 张人物图像）
- **URL 图像**：编辑不支持基于 URL 的图像；请使用 base64 编码的图像
- **水印**：所有生成的图像都包含 SynthID 水印

## 资源

- [Gemini 图像生成文档](https://ai.google.dev/gemini-api/docs/image-generation)
- [Gemini API 模型](https://ai.google.dev/gemini-api/docs/models/gemini)
- [批量 API 文档](https://ai.google.dev/gemini-api/docs/batch-api)
- [图像生成示例手册](https://colab.research.google.com/github/google-gemini/cookbook/blob/main/quickstarts/Get_Started_Nano_Banana.ipynb)
