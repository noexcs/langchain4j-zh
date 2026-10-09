# watsonx.ai

- [watsonx.ai API Reference](https://cloud.ibm.com/apidocs/watsonx-ai)
- [watsonx.ai Java SDK](https://github.com/IBM/watsonx-ai-java-sdk)
- [watsonx.ai Java SDK 文档](https://ibm.github.io/watsonx-ai-java-sdk/services/model-gateway/image-generation)

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-watsonx</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## Model Gateway

图像生成仅通过 IBM watsonx.ai **Model Gateway** 提供，它暴露了一个与 OpenAI 兼容的 images 端点，并将请求路由到其中注册的提供商所托管的模型。没有基础模型（foundation model）的对应物，因此 `WatsonxGatewayImageModel` 是此集成中唯一的图像模型。

> **注意：** 网关必须由管理员在使用前进行配置。你传入的每个 `modelName` 都必须是网关中已注册的 id。

## WatsonxGatewayImageModel

`WatsonxGatewayImageModel` 实现了 LangChain4j 的 `ImageModel` 接口。要创建实例，请指定：

- `baseUrl(...)` – IBM Cloud 端点 URL（`String`、`URI` 或 `CloudRegion`）
- `apiKey(...)` – IBM Cloud IAM API 密钥（或通过 `.authenticator(...)` 传入完整的 `Authenticator`）
- `modelName(...)` – 在网关中注册的图像模型 id，采用 OpenAI 风格写法

不需要 `projectId` 或 `spaceId`，网关会自行解析模型。

```java
import com.ibm.watsonx.ai.CloudRegion;
import dev.langchain4j.data.image.Image;
import dev.langchain4j.model.image.ImageModel;
import dev.langchain4j.model.watsonx.WatsonxGatewayImageModel;

ImageModel imageModel = WatsonxGatewayImageModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .modelName("gpt-image-1")
    .build();

Image image = imageModel.generate("A futuristic city at sunset").content();
```

### 生成多张图像

```java
Response<List<Image>> response = imageModel.generate("A futuristic city at sunset", 3);

for (Image image : response.content()) {
    System.out.println(image.base64Data());
}
```

每个请求接受的图像数量取决于模型，因此一个模型允许的值可能被另一个模型拒绝。

### 保存生成的图像

根据模型和所请求的响应格式，图像以链接或 Base64 数据的形式返回。

```java
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Base64;

Image image = imageModel.generate("A futuristic city at sunset").content();

if (image.base64Data() != null) {
    Files.write(Path.of("image.png"), Base64.getDecoder().decode(image.base64Data()));
} else {
    System.out.println(image.url());
}
```

当模型报告其生成的图像的格式时，`mimeType()` 会携带该格式，例如 `image/png`。

## 参数

每个参数都可以在构建器上设置一次，并应用于所有请求。

| 构建器方法 | 描述 |
|---|---|
| `background(...)` | 生成图像的背景，`TRANSPARENT`、`OPAQUE` 或 `AUTO`。透明需要支持它的输出格式，即 `PNG` 或 `WEBP` |
| `moderation(...)` | 对生成图像的过滤严格程度，`LOW` 或 `AUTO` |
| `outputCompression(...)` | 0 到 100 的压缩级别，仅 `JPEG` 和 `WEBP` 格式接受 |
| `outputFormat(...)` | 生成图像的文件格式，`PNG`、`JPEG`、`WEBP` 或 `AUTO` |
| `quality(...)` | 生成图像的质量，`AUTO`、`HIGH`、`MEDIUM`、`LOW`、`HD` 或 `STANDARD` |
| `responseFormat(...)` | 图像的返回方式，`URL` 表示链接，`B64_JSON` 表示 Base64 数据 |
| `size(...)` | 生成图像的尺寸，例如 `SIZE_1024X1024` |
| `style(...)` | 生成图像的视觉风格，`VIVID` 或 `NATURAL` |
| `user(...)` | 最终用户的标识符，用于滥用监控 |

它们各自还有一个接受 `String` 的重载，适用于枚举尚未覆盖的值。

```java
import com.ibm.watsonx.ai.gateway.image.ModelGatewayImageParameters.OutputFormat;
import com.ibm.watsonx.ai.gateway.image.ModelGatewayImageParameters.Quality;
import com.ibm.watsonx.ai.gateway.image.ModelGatewayImageParameters.Size;

ImageModel imageModel = WatsonxGatewayImageModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .modelName("gpt-image-1")
    .size(Size.SIZE_1024X1024)
    .quality(Quality.LOW)
    .outputFormat(OutputFormat.PNG)
    .build();
```

### 按请求参数

相同的值也可以通过 `ModelGatewayImageParameters` 按请求传入。给定的参数会替换构建器上设置的参数，而不是与它们合并。

```java
import com.ibm.watsonx.ai.gateway.image.ModelGatewayImageParameters;

WatsonxGatewayImageModel imageModel = WatsonxGatewayImageModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key")
    .modelName("gpt-image-1")
    .build();

ModelGatewayImageParameters parameters = ModelGatewayImageParameters.builder()
    .size(Size.SIZE_1024X1024)
    .quality(Quality.HIGH)
    .n(2)
    .build();

Response<List<Image>> response = imageModel.generate("A futuristic city at sunset", parameters);
```

`n` 和 `partialImages` 仅在这里可用，构建器上没有。图像数量已经通过 `generate(prompt, n)` 成为 LangChain4j 图像请求 API 的一部分，而 `partialImages` 不起作用，因为该端点不会流式返回结果。

## 特定模型的行为

网关会将请求转发到模型的提供商，因此并非每个参数都能被每个模型遵循。

| 模型 | 行为 |
|---|---|
| `gpt-image-1` | 始终以 Base64 数据作答，忽略 `responseFormat`。它是唯一报告 token 用量的模型 |
| `dall-e-3` | 遵循 `responseFormat`，并且是唯一返回改写后的提示词的模型，可通过 `image.revisedPrompt()` 读取 |
| `dall-e-2` | 遵循 `responseFormat`，不支持 `quality` 或 `style` |

当某个参数未设置时，应用的默认值为：`responseFormat` 为 `url`、`outputFormat` 为 `jpeg`、`size` 为 `1024x1024`、`quality` 为 `auto`，且仅一张图像。

## Token 用量

只有计算提示词 token 的模型才会报告 token 用量，因此 `response.tokenUsage()` 可能为 `null`。

```java
Response<Image> response = imageModel.generate("A futuristic city at sunset");

if (response.tokenUsage() != null) {
    System.out.println(response.tokenUsage().totalTokenCount());
}
```

## 不支持的操作

该端点仅能从提示词生成图像，因此 `ImageModel` 接口的编辑方法没有对应实现。调用 `edit(Image, String)` 或 `edit(Image, Image, String)` 会抛出 `IllegalArgumentException`。

## 身份验证

Watsonx.ai 支持通过 `Authenticator` 接口进行身份验证。

这允许你根据部署环境使用不同的身份验证机制：

- **IBMCloudAuthenticator** – 使用 API 密钥对 **IBM Cloud** 进行身份验证。这是最简单的方法，在提供 `apiKey(...)` 构建器方法时使用。
- **CP4DAuthenticator** – 对 **Cloud Pak for Data** 部署进行身份验证。
- **自定义身份验证器** – 可以使用 `Authenticator` 接口的任何实现。

`WatsonxGatewayImageModel` 和其他服务构建器接受通过 `.apiKey(...)` 的快捷方式，或通过 `.authenticator(...)` 的完整 `Authenticator` 实例。

### 示例

```java
WatsonxGatewayImageModel.builder()
    .baseUrl(CloudRegion.FRANKFURT)
    .apiKey("your-api-key") // Simple IBM Cloud authentication
    .modelName("gpt-image-1")
    .build();

WatsonxGatewayImageModel.builder()
    .baseUrl("https://my-instance-url")
    .authenticator( // For Cloud Pak for Data deployments
        CP4DAuthenticator.builder()
            .baseUrl("https://my-instance-url")
            .username("username")
            .apiKey("api-key")
            .build()
    )
    .modelName("gpt-image-1")
    .build();
```
