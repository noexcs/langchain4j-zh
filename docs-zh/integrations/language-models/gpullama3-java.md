# GPULlama3.java

!!! note
   `langchain4j-gpu-llama3` 已弃用。GPULlama3.java 的继任者是 [jitLLM](jitllm.md)：
   请改用 `langchain4j-jitllm`。

[GPULlama3.java](https://github.com/beehive-lab/GPULlama3.java)

GPULlama3.java 基于 [TornadoVM](https://github.com/beehive-lab/TornadoVM) 构建，利用 GPU 和异构计算，直接从 Java 更快地进行 LLM 推理。
目前，GPULlama3.java 支持通过 PTX 和 OPENCL 后端在 NVIDIA、AMD GPU 和 Apple Silicon 上进行推理。

----
## 项目设置

要在项目中安装 langchain4j，请添加以下依赖：

对于 Maven 项目的 `pom.xml`

```xml

<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j</artifactId>
    <version>1.22.0</version>
</dependency>

<dependency>
<groupId>dev.langchain4j</groupId>
<artifactId>langchain4j-gpu-llama3</artifactId>
<version>1.22.0-beta32</version>
</dependency>

```

对于 Gradle 项目的 `build.gradle`

```groovy
implementation 'dev.langchain4j:langchain4j:1.22.0'
implementation 'dev.langchain4j:langchain4j-gpu-llama3:1.22.0-beta32'
```
---
## 模型兼容性

目前，GPULlama3.java 支持 GGUF 格式下 FP16、Q8 和 Q4 格式的以下模型：
注意，对于 Q8 和 Q4 模型，模型在加载时会反量化为 FP16。
我们在 [HuggingFace](https://huggingface.co/beehive-lab/collections) 仓库中维护了一个经过测试的模型集合。

* Llama3
* Mistral
* Qwen2.5
* Qwen3.0
* Phi-3
* DeepSeek-R1-Distill-Qwen-1.5B-GGUF
----
## 聊天补全
聊天模型允许你使用在对话数据上微调过的模型生成类似人类的响应。

### 同步
创建一个类并添加以下代码。

```java
prompt = "What is the capital of France?";
ChatRequest request = ChatRequest.builder().messages(
    UserMessage.from(prompt),
    SystemMessage.from("reply with extensive sarcasm"))
    .build();

Path modelPath = Paths.get("beehive-llama-3.2-1b-instruct-fp16.gguf");

GPULlama3ChatModel model = GPULlama3ChatModel.builder()
        .modelPath(modelPath)
        .onGPU(Boolean.TRUE) //if false, runs on CPU though a lightweight implementation of llama3.java
        .build();
ChatResponse response = model.chat(request);
System.out.println("\n" + response.aiMessage().text());
```

### 流式

创建一个类并添加以下代码。

```java
public static void main(String[] args) {
    CompletableFuture<ChatResponse> futureResponse = new CompletableFuture<>();

    String prompt;

    if (args.length > 0) {
        prompt = args[0];
        System.out.println("User Prompt: " + prompt);
    } else {
        prompt = "What is the capital of France?";
        System.out.println("Example Prompt: " + prompt);
    }

    ChatRequest request = ChatRequest.builder().messages(
                    UserMessage.from(prompt),
                    SystemMessage.from("reply with extensive sarcasm"))
            .build();

    Path modelPath = Paths.get("beehive-llama-3.2-1b-instruct-fp16.gguf");


    GPULlama3StreamingChatModel model = GPULlama3StreamingChatModel.builder()
            .onGPU(Boolean.TRUE) // if false, runs on CPU though a lightweight implementation of llama3.java
            .modelPath(modelPath)
            .build();

    model.chat(request, new StreamingChatResponseHandler() {

        @Override
        public void onPartialResponse(String partialResponse) {
            System.out.print(partialResponse);
        }

        @Override
        public void onCompleteResponse(ChatResponse completeResponse) {
            futureResponse.complete(completeResponse);
            model.printLastMetrics();
        }

        @Override
        public void onError(Throwable error) {
            futureResponse.completeExceptionally(error);
        }
    });

    futureResponse.join();
}
```

## 如何运行：

运行该示例前需要配置 TornadoVM
详细说明可参阅**[设置与配置](https://github.com/beehive-lab/GPULlama3.java?tab=readme-ov-file#prerequisites)**
#### **步骤 1 — 获取 Tornado JVM 标志**

运行以下命令（你需要先安装 Tornado）：

```bash
tornado --printJavaFlags
```

输出示例：

```bash
/home/mikepapadim/.sdkman/candidates/java/current/bin/java -server \
 -XX:+UnlockExperimentalVMOptions -XX:+EnableJVMCI \
-XX:-UseCompressedClassPointers --enable-preview \
-Djava.library.path=/home/mikepapadim/java-ai-demos/GPULlama3.java/external/tornadovm/bin/sdk/lib \
--module-path .:/home/mikepapadim/java-ai-demos/GPULlama3.java/external/tornadovm/bin/sdk/share/java/tornado \
-Dtornado.load.api.implementation=uk.ac.manchester.tornado.runtime.tasks.TornadoTaskGraph \
-Dtornado.load.runtime.implementation=uk.ac.manchester.tornado.runtime.TornadoCoreRuntime \
-Dtornado.load.tornado.implementation=uk.ac.manchester.tornado.runtime.common.Tornado \
-Dtornado.load.annotation.implementation=uk.ac.manchester.tornado.annotation.ASMClassVisitor \
-Dtornado.load.annotation.parallel=uk.ac.manchester.tornado.api.annotations.Parallel \
--upgrade-module-path /home/mikepapadim/java-ai-demos/GPULlama3.java/external/tornadovm/bin/sdk/share/java/graalJars \
-XX:+UseParallelGC \
@/home/mikepapadim/java-ai-demos/GPULlama3.java/external/tornadovm/bin/sdk/etc/exportLists/common-exports \
@/home/mikepapadim/java-ai-demos/GPULlama3.java/external/tornadovm/bin/sdk/etc/exportLists/opencl-exports \
--add-modules ALL-SYSTEM,tornado.runtime,tornado.annotation,tornado.drivers.common,tornado.drivers.opencl
```

#### **步骤 2 — 构建 Maven classpath**

在项目根目录运行：

```bash
mvn dependency:build-classpath -Dmdep.outputFile=cp.txt
```

#### **步骤 3 — 构建 Maven classpath**

```bash
mvn clean package
```

你的主 JAR 文件位于：
```bash
target/gpullama3.java-example-1.22.0-beta32.jar
```

#### **步骤 4 — 直接用 Java 运行程序**
现在你可以使用所有 JVM 和 Tornado 标志运行该示例：

```bash
JAVA_BIN=/home/mikepapadim/.sdkman/candidates/java/current/bin/java
CP="target/gpullama3.java-example-1.22.0-beta32.jar:$(cat cp.txt)"

$JAVA_BIN \
  -server \
  -XX:+UnlockExperimentalVMOptions \
  -XX:+EnableJVMCI \
  --enable-preview \
  -Djava.library.path=/home/mikepapadim/java-ai-demos/GPULlama3.java/external/tornadovm/bin/sdk/lib \
  --module-path .:/home/mikepapadim/java-ai-demos/GPULlama3.java/external/tornadovm/bin/sdk/share/java/tornado \
  -Dtornado.load.api.implementation=uk.ac.manchester.tornado.runtime.tasks.TornadoTaskGraph \
  -Dtornado.load.runtime.implementation=uk.ac.manchester.tornado.runtime.TornadoCoreRuntime \
  -Dtornado.load.tornado.implementation=uk.ac.manchester.tornado.runtime.common.Tornado \
  -Dtornado.load.annotation.implementation=uk.ac.manchester.tornado.annotation.ASMClassVisitor \
  -Dtornado.load.annotation.parallel=uk.ac.manchester.tornado.api.annotations.Parallel \
  --upgrade-module-path /home/mikepapadim/java-ai-demos/GPULlama3.java/external/tornadovm/bin/sdk/share/java/graalJars \
  -XX:+UseParallelGC \
  @/home/mikepapadim/java-ai-demos/GPULlama3.java/external/tornadovm/bin/sdk/etc/exportLists/common-exports \
  @/home/mikepapadim/java-ai-demos/GPULlama3.java/external/tornadovm/bin/sdk/etc/exportLists/opencl-exports \
  --add-modules ALL-SYSTEM,tornado.runtime,tornado.annotation,tornado.drivers.common,tornado.drivers.opencl \
  -Xms6g -Xmx6g \
  -Dtornado.device.memory=6GB \
  -cp "$CP" \
  GPULlama3ChatModelExamples
```

## 预期输出：

```bash
WARNING: Using incubator modules: jdk.incubator.vector
Example Prompt: What is the capital of France?
SLF4J(W): No SLF4J providers were found.
SLF4J(W): Defaulting to no-operation (NOP) logger implementation
SLF4J(W): See https://www.slf4j.org/codes.html#noProviders for further details.
Wow, I'm so glad you asked. I've been waiting for someone to finally ask me this question. It's not like I have better things to do, like take a nap or something. So, yes, the capital of France is... (dramatic pause) ...Paris!

achieved tok/s: 48.86. Tokens: 87, seconds: 1.78
```

## 备注：

* GPU 利用率可以使用 `nvidia-smi` 监控 NVIDIA GPU，或使用 'nvtop' 或适用于 AMD/Apple Silicon 的相应工具。
