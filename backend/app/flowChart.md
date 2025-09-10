```
⚡ 電力系統開發前該畫哪些 Flow？（含圖例說明）
✅ 建議畫這 4 種圖（+ Bonus）

圖類型	說明	工具建議
1️⃣ 系統架構圖	畫出所有模組 & 資料來源，例如 MQTT、資料庫、前端	draw.io / Mermaid
2️⃣ 資料流程圖 (DFD)	資料怎麼流進來、怎麼處理、去哪裡	draw.io / Mermaid
3️⃣ 狀態流程圖	DI/AI/DO 狀態變化、邏輯運算流程（AND/OR/XOR）	Mermaid / Whimsical
4️⃣ UI Flow（頁面邏輯）	按鈕點擊後做什麼、跳窗、CRUD 操作	Figma / draw.io
🔥 Bonus：模組責任圖	哪個檔案負責什麼邏輯、API 區塊	Notion / Markdown / Mermaid
```

## 1️⃣ 系統架構圖
``` text
📌 這張圖清楚表達：

各個電力裝置如何進到系統

API 串接資料庫與前端的角色

雙向溝通端點
```

```mermaid
graph TD
    subgraph Field Devices
        DI[DI 設備]
        AI[AI 設備]
        DO[DO 設備]
    end

    subgraph Communication
        MQTT[MQTT Broker]
    end

    subgraph Backend
        API[FastAPI Backend]
        DB[MS SQL 資料庫]
    end

    subgraph Frontend
        Vue[Vue 畫面]
    end

    DI --> MQTT
    AI --> MQTT
    DO --> MQTT
    MQTT --> API
    API --> DB
    API --> Vue
    Vue --> API

```
## 2️⃣ 資料流程圖 (DFD)
``` text
你可以用這種方式標記：

資料來源

傳輸方式

存放與呈現的流程
```

```mermaid
flowchart TD
    Sensor[DI/AI 訊號] -->|MQTT| Gateway
    Gateway -->|接收後存入| Backend[FastAPI]
    Backend -->|INSERT| SQL[資料庫]
    Backend -->|WebSocket/REST| Frontend
    Frontend -->|顯示| User[使用者畫面]
```
## 3️⃣ DI/AI 狀態邏輯流程圖
``` text
這張圖可以用來表示：

DI/AI 狀態變化的邏輯流程

邏輯運算流程（AND/OR/XOR）

例如：

DI = 1 且 AI > 閥值 → 警告

DI = 0 且 AI < 閥值 → 正常

DI = 1 且 AI > 高閥值 → 異常
``` 

```mermaid
stateDiagram-v2
    [*] --> 正常
    正常 --> 警告: AI > 閥值
    警告 --> 異常: DI = 1 且 AI > 高閥值
    異常 --> 正常: DI = 0 且 AI < 閥值

```
## 4️⃣ UI Flow + 操作流程
``` text
畫出「使用者操作流程」，你才知道：

要設哪些 API

哪些元件之間要互動
```

```mermaid
graph TD
    A[主畫面] --> B[點擊元件]
    B --> C[彈出跳窗設定]
    C --> D[選擇 Tag]
    D --> E[綁定完成]
    A --> F[點擊模擬執行]
    F --> G[依據 Tag 狀態變色]

```

## 🔥 Bonus：模組責任圖
``` text
它是用來標示：

每個程式模組（.py）負責什麼邏輯

誰是「資料處理」、誰是「資料庫層」、誰是「API 出口」

有助於模組化、分工、避免邏輯混雜
```

``` text
模組名稱 | 負責什麼
mqtt_client.py | 建立 MQTT 連線、訂閱主題
mqtt_handler.py | 收到 MQTT 資料後進一步處理
data_cleaner.py | 清洗資料、轉換格式
db_writer.py | 寫入資料庫邏輯
models.py | SQLAlchemy 資料模型
sql_utils.py | 資料庫查詢工具函式
api/router.py | FastAPI API 出口
service_logic.py | 接收 API 請求、處理邏輯、呼叫資料層
websocket.py | 推送即時資料到前端
```


```mermaid  
graph TB

subgraph MQTT 接收邏輯
    mqtt_client[mqtt_client.py] --> mqtt_handler[mqtt_handler.py]
    mqtt_handler --> data_cleaner[data_cleaner.py]
end

subgraph 資料層
    data_cleaner --> db_writer[db_writer.py]
    db_writer --> models[models.py]
    db_writer --> sql[sql_utils.py]
end

subgraph API 層
    api_router[api/router.py] --> logic_service[service_logic.py]
    logic_service --> sql
    logic_service --> models
end

subgraph 前端互動
    api_router --> websocket[websocket.py]
end

websocket --> mqtt_client

```