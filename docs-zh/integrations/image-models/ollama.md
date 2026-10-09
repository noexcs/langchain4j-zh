# Ollama 图像生成

!!! warning
    Ollama 图像生成为实验性功能。Ollama API 和 LangChain4j 集成可能会在未来版本中变化。

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-ollama</artifactId>
    <version>${latest version here}</version>
</dependency>
```

## API

- `OllamaImageModel`

`OllamaImageModel` 实现了 `ImageModel`，并支持通过 Ollama 的标准 `/api/generate` 端点进行文本到图像的生成。不支持图像编辑和从同一提示词生成多张图像。

这需要支持实验性图像生成功能的 Ollama 版本和模型。
普通的文本模型返回的是文本而非图像，并会以 `OllamaImageGenerationException` 失败。

## 用法

```java
ImageModel imageModel = OllamaImageModel.builder()
        .baseUrl("http://localhost:11434")
        .modelName("x/z-image-turbo")
        .width(1024)
        .height(768)
        .steps(20)
        .seed(42)
        .build();

Response<Image> response = imageModel.generate("a sunset over mountains");
Image image = response.content();
byte[] imageBytes = Base64.getDecoder().decode(image.base64Data());
Files.write(Path.of("ollama-image.png"), imageBytes);
```

## 参数

| 参数                | 描述                                                                                     | 类型                    |
|---------------------|---------------------------------------------------------------------------------------------|-------------------------|
| `httpClientBuilder` | 参见[可定制 HTTP 客户端](https://docs.langchain4j.dev/tutorials/customizable-http-client) | `HttpClientBuilder`     |
| `baseUrl`           | Ollama 服务器的基础 URL。                                                              | `String`                |
| `modelName`         | 要使用的 Ollama 服务器上的图像生成模型。                                    | `String`                |
| `width`             | 生成图像的宽度（像素）。使用 `0` 或留空以使用 Ollama/模型的默认值。设置时必须介于 0 和 4096 之间。 | `Integer`               |
| `height`            | 生成图像的高度（像素）。使用 `0` 或留空以使用 Ollama/模型的默认值。设置时必须介于 0 和 4096 之间。 | `Integer`               |
| `steps`             | 扩散步数。使用 `0` 或留空以使用 Ollama/模型的默认值。不得为负数。 | `Integer`               |
| `seed`              | 通过 Ollama `options.seed` 发送的随机种子。                                              | `Integer`               |
| `timeout`           | API 调用完成的最大允许时间。                                       | `Duration`              |
| `customHeaders`     | 自定义 HTTP 头。                                                                        | `Map<String, String>`   |
| `logRequests`       | 是否记录请求。                                                                    | `Boolean`               |
| `logResponses`      | 是否记录响应。                                                                   | `Boolean`               |
| `maxRetries`        | API 调用失败时的最大重试次数。                                   | `Integer`               |

目前 `OllamaImageModel` 没有 Spring Boot starter 配置。

生成的图像以 Base64 编码的 PNG 数据返回。URL 输出、token 用量以及 Ollama
流式进度字段（如 `completed` 和 `total`）未暴露。