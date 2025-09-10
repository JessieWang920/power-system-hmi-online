

# 電力系統專案_HMI

## 專案介紹

期望開發者在現場可快速建置電力圖，並透過該系統拉取圖案設定綁定點位等，最後可在介面上呈現使用者所需的監控介面。  
收取MQTT 資料，並將資料寫入 SQL Server 資料庫中，並透過 vue 前端呈現使用者所需的監控介面。

後端將從 node-red 更改為python 開發

<br>

## 專案架構
node-red程式部分，為前一位 RD 開發出

- 前端：vue2 + uibuilder
- 後端：Python + MQTT + MS SQL Server + WebSocket

<br>

## 開發環境
- Python 3.12.10

### requirements.txt
```

```



<br>

### Folder Structure

```text
power-system-hmi/ 
├─ README.md
├─ .gitignore
├─ docker-compose.yml       ← 一鍵啟動 DB、MQTT、後端、前端
├─ docs/
├─ backend/                 
│  ├─ requirements.txt
│  ├─ venv/
│  ├─ tests/
│  │    └─ __init__.py
│  ├─ datas/                # 儲存運行中的資料
│  │   └─ logs/ 
│  ├─ config/
│  │   ├─ .env
│  │   └─ .env.example
│  └─ app/
│      ├─ __init__.py
│      ├─ main.py   
│      ├─ core/              # 共用工具 & 基礎庫                        
│      │   ├── __init__.py     
│      │   ├── config.py     # 讀 .env / yaml  
│      │   ├── db.py         # 資料庫操作
│      │   ├── security.py   # ip 驗證  
│      │   └── logger.py
│      │
│      └─ features/             ← 依功能放入
│          ├─ partition/
│          │   ├─ __init__.py
│          │   ├─ model.py      ← 定義資料庫 ORM 表，DB 的欄位結構格式
│          │   ├─ schema.py     ← 定義 API 用的 Pydantic 物件，定義 API 接收/輸出欄位
│          │   ├─ crud.py       ← 資料庫的操作邏輯，封裝 SQL 操作
│          │   └─ router.py     ← 放 FastAPI 路由設定，並依需要引入 schema 與 crud 
│          │
│          └─ shapes_name/
│              ├─ __init__.py
│              ├─ model.py      ← 定義資料庫 ORM 表，DB 的欄位結構格式
│              ├─ schema.py     ← 定義 API 用的 Pydantic 物件，定義 API 接收/輸出欄位
│              ├─ crud.py       ← 資料庫的操作邏輯，封裝 SQL 操作
│              └─ router.py     ← 放 FastAPI 路由設定，並依需要引入 schema 與 crud 
│
└─ frontend/               ← Vue / React / Svelte … 皆可
   ├─ src/
   ├─ public/
   ├─ package.json
   ├─ vite.config.ts
   └─ Dockerfile
```


<br>

## Quick Start

```bash
git clone https://github.com/JessieWang920/power-system-hmi.git

cd backend

pip install virtualenv

virtualenv venv

venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env

# run
uvicorn app.main:app --reload --port 8000
# Swagger UI: http://localhost:8000/docs
```
<br>  

---


```
cd backend
python -m uvicorn app.main:app --reload --port 8000
```