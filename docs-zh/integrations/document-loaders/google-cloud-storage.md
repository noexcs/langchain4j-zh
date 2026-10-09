# Google Cloud Storage

一个 Google Cloud Storage (GCS) 文档加载器，允许你从存储桶中加载文档。

## Maven 依赖

```xml
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-document-loader-google-cloud-storage</artifactId>
    <version>1.22.0-beta32</version>
</dependency>
```

## API

- `GoogleCloudStorageDocumentLoader`

## 认证

认证应该为你透明处理：
* 如果你的应用程序运行在 Google Cloud Platform（Cloud Run、App Engine、Compute Engine 等）上
* 在本地机器上运行时，如果你已经通过 Google 的 `gcloud` SDK 完成认证

你只需要创建一个指定项目 ID 的加载器：

```java
GoogleCloudStorageDocumentLoader gcsLoader = GoogleCloudStorageDocumentLoader.builder()
    .project(System.getenv("GCP_PROJECT_ID"))
    .build();
```

否则，如果你下载了服务账号密钥并导出了指向它的环境变量，则可以指定 `Credentials`：

```java
GoogleCloudStorageDocumentLoader gcsLoader = GoogleCloudStorageDocumentLoader.builder()
    .project(System.getenv("GCP_PROJECT_ID"))
    .credentials(GoogleCredentials.fromStream(new FileInputStream(System.getenv("GOOGLE_APPLICATION_CREDENTIALS"))))
    .build();
```

了解更多关于[凭据](https://cloud.google.com/docs/authentication/application-default-credentials)的信息。

访问公共存储桶时，你不需要进行认证。

## 示例

### 从 GCS 存储桶加载单个文件

```java
GoogleCloudStorageDocumentLoader gcsLoader = GoogleCloudStorageDocumentLoader.builder()
    .project(System.getenv("GCP_PROJECT_ID"))
    .build();

Document document = gcsLoader.loadDocument("BUCKET_NAME", "FILE_NAME.txt", new TextDocumentParser());
```

### 从 GCS 存储桶加载所有文件

```java
GoogleCloudStorageDocumentLoader gcsLoader = GoogleCloudStorageDocumentLoader.builder()
    .project(System.getenv("GCP_PROJECT_ID"))
    .build();

List<Document> documents = gcsLoader.loadDocuments("BUCKET_NAME", new TextDocumentParser());
```

### 使用 glob 模式从 GCS 存储桶加载所有文件

```java
GoogleCloudStorageDocumentLoader gcsLoader = GoogleCloudStorageDocumentLoader.builder()
    .project(System.getenv("GCP_PROJECT_ID"))
    .build();

List<Document> documents = gcsLoader.loadDocuments("BUCKET_NAME", "*.txt", new TextDocumentParser());
```

更多代码示例，请查看集成测试类：
- [GoogleCloudStorageDocumentLoaderIT](https://github.com/langchain4j/langchain4j/blob/main/document-loaders/langchain4j-document-loader-google-cloud-storage/src/test/java/dev/langchain4j/data/document/loader/gcs/GoogleCloudStorageDocumentLoaderIT.java)
