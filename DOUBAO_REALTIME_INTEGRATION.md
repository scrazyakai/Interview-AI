# 豆包实时语音接入说明

这份文档说明当前项目是怎么把豆包实时语音 API 接进来的，包括：

- 前端怎么采集麦克风并和后端建立 WebSocket
- 后端怎么转发到豆包实时语音服务
- 豆包二进制协议在项目里是怎么封装的
- 需要怎么配置环境变量
- 怎么启动、怎么排查

## 1. 目标

当前 `interview` 页面实现的是一条实时链路：

`浏览器麦克风 -> 前端 WebSocket -> FastAPI WebSocket -> 豆包实时语音 WebSocket -> 豆包返回文本和音频 -> 页面播放`

项目里同时保留了两种调用方式：

- `POST /api/interview/chat`
  用于单次文本请求，发一句话，拿一句完整回复。
- `WS /api/interview/ws`
  用于实时语音对话，浏览器持续发音频，后端持续转发并接收豆包返回。

## 2. 关键文件

后端：

- `app/main.py`
- `app/api/interview.py`
- `app/services/interview_service.py`
- `app/config/interview_config.py`
- `app/schemas/interview.py`

前端：

- `frontend/src/views/InterviewMockView.vue`
- `frontend/src/utils/auth.ts`

依赖：

- `pyproject.toml`

## 3. 后端实现

### 3.1 入口

后端在 `app/api/interview.py` 里暴露了两个接口：

#### `POST /api/interview/chat`

这个接口接收：

```json
{
  "message": "你好"
}
```

后端会：

1. 建立到豆包实时语音服务的 WebSocket 连接
2. 发送 `StartConnection`
3. 发送 `StartSession`
4. 发送文本事件 `501`
5. 聚合豆包返回的文本分片和音频分片
6. 返回文本、音频和会话 ID

这是“单次调用”模式。

#### `WS /api/interview/ws`

这是实时语音入口。

前端打开这个 WebSocket 后，后端会：

1. `accept()` 浏览器 WebSocket
2. 作为客户端再去连接豆包实时语音 WebSocket
3. 建立豆包会话
4. 启动两个协程并行转发：
   - 浏览器 -> 豆包
   - 豆包 -> 浏览器

### 3.2 豆包协议封装

核心逻辑在 `app/services/interview_service.py`。

这里没有直接调用普通 HTTP 接口，而是按豆包示例里的实时语音二进制协议手工封装。

主要函数：

#### `_generate_header()`

生成豆包协议头。

#### `_build_event_request()`

构造带事件号的请求包，例如：

- `1`：开始连接
- `100`：开始会话
- `102`：结束会话
- `300`：Hello
- `501`：文本消息

#### `_build_audio_request()`

构造实时音频包：

- 事件号：`200`
- 消息类型：`CLIENT_AUDIO_ONLY_REQUEST`
- 序列化：`NO_SERIALIZATION`
- 音频内容：gzip 压缩后的原始 PCM bytes

#### `_parse_response()`

解析豆包返回的二进制响应，拆出：

- `message_type`
- `event`
- `session_id`
- `payload_msg`

### 3.3 文本模式 `chat()`

`InterviewService.chat()` 的流程：

1. 生成 `session_id`
2. 从环境变量构造豆包连接参数
3. 构造 `input_mod="text"` 的 `StartSession` payload
4. 建立 WebSocket
5. 发 `1` 和 `100`
6. 发 `501` 文本请求
7. 循环读取返回：
   - `event=550`：文本分片，拼接到 `reply`
   - `SERVER_ACK` 音频分片：拼接到音频 buffer
8. 收尾关闭会话
9. 返回：

```json
{
  "reply": "...",
  "session_id": "...",
  "audio_base64": "...",
  "audio_format": "pcm",
  "audio_sample_rate": 24000
}
```

### 3.4 实时模式 `bridge_websocket()`

`InterviewService.bridge_websocket()` 是实时语音的桥接层。

它做的事就是把两条 WebSocket 串起来：

- 下游：浏览器
- 上游：豆包实时语音服务

#### 浏览器 -> 后端 -> 豆包

浏览器发两类消息：

- 二进制消息：麦克风 PCM 音频
- 文本 JSON：
  - `{"type":"text","content":"..."}`：手动文字提问
  - `{"type":"stop"}`：结束会话

后端收到后：

- 音频二进制 -> 组装成豆包 `event=200` 音频包
- 文本 -> 组装成豆包 `event=501`
- `stop` -> 结束转发循环

#### 豆包 -> 后端 -> 浏览器

后端把豆包的返回继续转给前端：

- `event=352` + 音频 ACK -> 直接 `send_bytes()` 给浏览器
- `event=550` + `content` -> 发 JSON：

```json
{
  "type": "assistant_text",
  "text": "..."
}
```

- `event=359` -> 发：

```json
{
  "type": "assistant_done"
}
```

- `event=450` -> 发：

```json
{
  "type": "user_speaking"
}
```

- `event=459` -> 发：

```json
{
  "type": "user_done"
}
```

### 3.5 后端配置读取

配置在 `app/config/interview_config.py` 里。

后端通过两个函数组装配置：

#### `build_realtime_ws_config()`

负责生成豆包 WebSocket 地址和请求头。

读取这些环境变量：

- `VOLC_REALTIME_APP_ID`
- `VOLC_REALTIME_ACCESS_KEY`
- `VOLC_REALTIME_URL`
- `VOLC_REALTIME_RESOURCE_ID`
- `VOLC_REALTIME_APP_KEY`

#### `build_start_session_payload(input_mod)`

负责生成 `StartSession` 的 JSON 参数。

读取这些环境变量：

- `VOLC_REALTIME_SPEAKER`
- `VOLC_REALTIME_OUTPUT_FORMAT`
- `VOLC_REALTIME_OUTPUT_SAMPLE_RATE`
- `VOLC_REALTIME_END_SMOOTH_WINDOW_MS`
- `VOLC_REALTIME_RECV_TIMEOUT`
- `VOLC_REALTIME_BOT_NAME`
- `VOLC_REALTIME_SYSTEM_ROLE`
- `VOLC_REALTIME_SPEAKING_STYLE`

`input_mod="text"` 用于单次文本接口。  
`input_mod="audio"` 用于实时语音接口。

## 4. 前端实现

前端逻辑在 `frontend/src/views/InterviewMockView.vue`。

### 4.1 页面职责

页面负责四件事：

1. 打开浏览器麦克风
2. 建立到后端 `/api/interview/ws` 的 WebSocket
3. 把麦克风数据转换成后端可接受的 PCM 二进制流
4. 播放豆包返回的 PCM 音频，并渲染文本

### 4.2 前端 WebSocket 地址

在 `frontend/src/utils/auth.ts` 里定义了：

- `API_BASE_URL`
- `getInterviewWebSocketUrl()`

它会把：

`http://127.0.0.1:8000/api`

转成：

`ws://127.0.0.1:8000/api/interview/ws`

### 4.3 打开麦克风后的流程

点击“开启麦克风”后，前端会：

1. 调用 `navigator.mediaDevices.getUserMedia({ audio: true })`
2. 创建输入 `AudioContext({ sampleRate: 16000 })`
3. 创建 `ScriptProcessorNode`
4. 持续拿到单声道浮点音频
5. 把浮点采样转成 `Int16 PCM`
6. 累积到固定 `3200` 字节一帧
7. 通过浏览器 WebSocket 发给后端

这一步的目标是尽量贴近豆包示例的输入格式：

- 单声道
- 16k
- PCM int16
- 固定小块持续发送

### 4.4 接收豆包返回

前端收到两类返回：

#### JSON 文本事件

例如：

- `ready`
- `assistant_text`
- `assistant_done`
- `user_speaking`
- `user_done`
- `error`

这些会更新聊天气泡和状态标签。

#### 二进制音频

前端把后端传回来的二进制按 `Float32 PCM / 24000Hz` 解码，然后放进浏览器 `AudioBuffer` 播放。

### 4.5 结束面试

点击“结束面试”后，前端会：

1. 停止麦克风采集
2. 发送 `{"type":"stop"}`
3. 主动关闭浏览器 WebSocket
4. 把页面状态恢复到空闲

## 5. 配置方式

## 5.1 必须使用 `.env`

后端运行时读的是项目根目录 `.env`，不是 `.env.example`。

`.env.example` 只是模板文件；如果只把值写在 `.env.example` 里，后端是读不到的。

## 5.2 必要配置

项目根目录 `.env` 至少要有：

```env
VOLC_REALTIME_APP_ID=你的实时语音APP_ID
VOLC_REALTIME_ACCESS_KEY=你的实时语音ACCESS_KEY
```

建议完整写成：

```env
VOLC_API_KEY=your_volc_api_key
VOLC_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
VOLC_MODEL=doubao-seed-1-8-251228

VOLC_REALTIME_APP_ID=your_realtime_app_id
VOLC_REALTIME_ACCESS_KEY=your_realtime_access_key
VOLC_REALTIME_URL=wss://openspeech.bytedance.com/api/v3/realtime/dialogue
VOLC_REALTIME_RESOURCE_ID=volc.speech.dialog
VOLC_REALTIME_APP_KEY=PlgvMymc7f3tQnJ6
VOLC_REALTIME_SPEAKER=zh_male_yunzhou_jupiter_bigtts
VOLC_REALTIME_OUTPUT_FORMAT=pcm
VOLC_REALTIME_OUTPUT_SAMPLE_RATE=24000
VOLC_REALTIME_END_SMOOTH_WINDOW_MS=1500
VOLC_REALTIME_RECV_TIMEOUT=30
VOLC_REALTIME_BOT_NAME=豆包
VOLC_REALTIME_SYSTEM_ROLE=你是一名专业的 AI 面试官，回答简洁、自然，并围绕面试场景追问。
VOLC_REALTIME_SPEAKING_STYLE=表达专业、清晰、语速适中。
```

## 5.3 `.env` 的加载位置

项目在 `app/main.py` 里通过 `load_dotenv()` 加载 `.env`。

所以：

- 改完 `.env`
- 必须重启后端

否则新变量不会生效。

## 6. 启动方式

### 6.1 后端

推荐在项目根目录启动：

```powershell
d:\Code\project-forLearn\interviwew-ai\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

### 6.2 前端

在 `frontend` 目录启动：

```powershell
npm install
npm run dev
```

默认前端会访问：

- HTTP API：`http://127.0.0.1:8000/api`
- WebSocket：`ws://127.0.0.1:8000/api/interview/ws`

## 7. 常见问题

### 7.1 打开麦克风后立刻变成“未连接”或“连接失败”

通常是后端没读到豆包配置。

检查：

1. 根目录是否真的有 `.env`
2. `.env` 是否写了：
   - `VOLC_REALTIME_APP_ID`
   - `VOLC_REALTIME_ACCESS_KEY`
3. 改完后是否重启了后端

### 7.2 能听到豆包说话，但豆包听不到用户

这通常说明：

- 豆包上游连接成功了
- 下行音频返回正常
- 但上行音频采集或转发有问题

重点检查：

1. 浏览器是否真的授权了麦克风
2. 前端是否持续发送二进制音频
3. 后端是否持续收到 `bytes`
4. 豆包是否返回 `450 / 459` 事件

### 7.3 只写了 `.env.example` 还是报缺少配置

这是正常现象。  
运行时只读 `.env`，不读 `.env.example`。

## 8. 当前实现的边界

当前版本已经能打通“浏览器 <-> 后端 <-> 豆包”的实时链路，但还不是最终工程形态。

当前还没有做的内容包括：

- WebSocket 鉴权
- 会话持久化入库
- 更完整的豆包事件分类
- 更细的打断逻辑
- 更详细的上行音频日志

这些都可以继续迭代，但不影响当前接通和使用。
