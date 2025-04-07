
# Discord Bot

一個基於 [discord.py](https://discordpy.readthedocs.io/en/stable/) 開發的 Discord 機器人，提供每日簽到、互動任務、虛擬經濟與用戶商店功能。

支援：
- Slash 指令（`/` 開頭的指令）
- 使用者互動（選單、按鈕）
- 多層級模組化架構
- Docker 部署

## 📜 授權 License

本專案以 [AGPL v3](https://www.gnu.org/licenses/agpl-3.0.html) 授權條款釋出，並依據原始授權條款第七條附加以下限制：

> ❗ **禁止任何商業用途**，包含但不限於營利性服務、SaaS 架設、公司內部部署。  
> 若您欲將此專案用於商業場景，請來信聯繫取得授權：**temporarylambda@gmail.com**

詳細條款請見 [`LICENSE`](./LICENSE)。



---

## 🛠️ 專案結構總覽

```bash
src/
├── Cogs/              # 指令邏輯（CheckIn, Shop, Personal 等）
├── Services/          # 商業邏輯處理（UserService, TopicService 等）
├── Repositories/      # 資料存取層
├── Views/             # UI 與互動元件（下拉選單、按鈕）
├── Enums/Exceptions/  # 基礎型別與例外處理
├── main.py            # 機器人啟動點
```

---

## 🧰 如果你尚未安裝 Docker

本專案透過 Docker 簡化部署流程，若你的電腦尚未安裝 Docker，請依照下方步驟操作。

### 🔽 安裝 Docker Desktop

1. 前往官方網站下載安裝程式：

   👉 [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

2. 選擇符合你作業系統的版本（Windows / macOS / Linux）

3. 安裝過程中請確保下列選項已勾選：
   - 啟用 WSL 2（Windows 用戶建議）
   - 使用 Containerd / Kubernetes（非必選，視需求）

4. 安裝完成後，請重啟電腦（依照提示操作）

5. 啟動 Docker Desktop，並確認系統右下角 / 上方選單圖示中 Docker 已成功啟動

### 🧪 驗證是否成功安裝

打開終端機（Terminal / PowerShell / CMD）執行以下指令：

```bash
docker -v
```

若顯示版本號（例如 `Docker version 24.x.x`），即表示安裝成功。

---

### 🛠️ Linux 使用者補充

請依照你的發行版執行官方教學（包含權限組設定與 systemd 啟動）：

👉 [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)

> 如果你使用 Ubuntu / Debian，可使用 `apt install docker.io` 或 `docker-ce` 版本，並將目前使用者加入 `docker` 群組以避免每次都要 sudo。

---

完成上述安裝後，即可繼續參閱 [🐳 使用 Docker 部署](#-使用-docker-部署) 章節，開始建立與啟動本專案！


## 🐳 使用 Docker 部署

### 1. 複製專案

```bash
git clone https://github.com/temporarylambda/discord-bot.git
cd discord-bot
```

### 2. 建立 `.env` 檔案

```bash
cp .env.example .env
```

請依照需求修改 `.env` 內容，至少需填入 `DISCORD_TOKEN`（Bot Token）與資料庫相關設定。

### 3. 建立並啟動容器

```bash
docker-compose up --build
```

> 📦 這會自動建立：
> - Python + discord.py 的機器人環境


### ✅ 預設指令

```bash
# 啟動服務（背景模式）
docker-compose up -d

# 停止服務
docker-compose down

# 查看 log
docker-compose logs -f

# 重新啟動（例如更新指令）
docker-compose restart
```

---

## ⚙️ 資料庫遷移

### 啟動時自動遷移

已經於 `docker-compose.yml` 中整併相關指令，當 `bot` 被啟動時，會自動觸發一次資料庫遷移。

```bash
alembic upgrade head
```

### 開發時新增新的資料庫異動紀錄

如果開發新功能而需要異動資料庫，請透過 alembic 進行操作：

```
alembic revision -m "{異動說明}"
```

這會建立一個新的 migration 檔案，完成開發後即可透過遷移指令進行部署

```bash
alembic upgrade head
```

或是部署後透過降版指令還原

```bash
alembic downgrade -1
```

> 如果要一次降不只一個版本，可以嘗試 -2 或 -3，代表降兩個、三個版本


或透過 `history` 指令來查看詳細資訊 

```bash
alembic history --verbose
```

---

## 💬 Slash 指令一覽

**🔐 權限總表**

> - 擁有懲罰身份組的使用者將無法使用大多數指令  
> - 所有互動元件都有基本錯誤保護與防重複提交設計  
> - 預留日後支援「管理員」等身分組權限控管  

| 權限類型 | 說明 |
|----------|------|
| 無限制 | 所有人皆可使用 |
| `不可封鎖` | 經 `RoleService.checkIsNotBanned()` 驗證，不允許被封鎖者使用 |
| `僅限管理員` | 經 `RoleService.checkIsManager()` 驗證，僅限特定角色使用 |

---

## 📦 `/inventory` 模組 – 背包功能

| 指令 | 參數 | 說明 | 權限限制 |
|------|------|------|----------|
| `/inventory 查看背包` | 無 | 顯示使用者尚未兌換的商品清單（支援分頁） | 一般使用者 |
| `/inventory 兌換商品` | `merchandise_id: int` | 兌換指定商品，可觸發任務刷新或通知上架者 | 一般使用者（不可封鎖） |

---

## 🏦 `/bank` 模組 – 金錢功能

| 指令 | 參數 | 說明 | 權限限制 |
|------|------|------|----------|
| `/bank 轉帳` | `member: discord.Member`<br>`amount: int` | 將金錢轉給他人，需額外扣除固定手續費 | 一般使用者（不可封鎖） |

---

## 🛒 `/shop` 模組 – 商品販售系統

| 指令 | 參數 | 說明 | 權限限制 |
|------|------|------|----------|
| `/shop 查看商品` | `member: Optional[discord.Member]` | 檢視所有或特定上架者的商品列表（支援分頁） | 一般使用者（不可封鎖） |
| `/shop 購買商品` | `merchandise_id: int`<br>`quantity: int = 1` | 檢視商品資訊並透過互動按鈕完成購買 | 一般使用者（不可封鎖） |
| `/shop 商品上架` | Modal：名稱、價格、描述 | 透過 Modal 表單上架商品 | 一般使用者（不可封鎖） |
| `/shop 商品下架` | `merchandise_id: int` | 將自己上架的商品下架（需確認） | 一般使用者（不可封鎖） |

---

## 🗓️ `/checkin` 模組 – 每日任務系統

| 指令 | 參數 | 說明 | 權限限制 |
|------|------|------|----------|
| `/checkin 簽到` | 無 | 領取每日任務題目 | 一般使用者（不可封鎖） |
| `/checkin 任務` | 無 | 查看當前進行中的任務清單 | 一般使用者（不可封鎖） |
| `/checkin 任務回報` | 無 | 回報已完成的任務並領取獎勵（互動選單） | 一般使用者（不可封鎖） |

---

## 👤 `/personal` 模組 – 個人資訊與排行榜

| 指令 | 參數 | 說明 | 權限限制 |
|------|------|------|----------|
| `/personal 個人資料` | 無 | 查詢個人資訊（餘額、簽到連勝等） | 一般使用者 |
| `/personal 富翁榜` | 無 | 查看伺服器內前十名資產最多使用者 | 一般使用者（不可封鎖） |
| `/personal 簽到榜` | 無 | 查看伺服器內前十名連續簽到王 | 一般使用者（不可封鎖） |

---

## 🛠️ `/manager` 模組 – 管理控制台

| 指令 | 參數 | 說明 | 權限限制 |
|------|------|------|----------|
| `/manager 金錢發放` | `user: discord.Member`<br>`amount: int`<br>`note: Optional[str]` | 管理員發錢給任意用戶 | 僅限管理員（不可封鎖） |
| `/manager 金錢扣除` | `user: discord.Member`<br>`amount: int`<br>`note: Optional[str]` | 管理員扣除任意用戶金錢，可扣至負數 | 僅限管理員（不可封鎖） |
| `/manager 上架任務` | Modal：內容、獎勵、備註 | 透過表單新增一則任務題目 | 僅限管理員（不可封鎖） |
| `/manager 任務清單` | 無 | 查看所有任務（支援分頁） | 僅限管理員（不可封鎖） |
| `/manager 下架任務` | `topic_id: int` | 將指定任務下架（需確認） | 僅限管理員（不可封鎖） |
| `/manager 強制下架商品` | `merchandise_id: int` | 強制下架任意商品（任務刷新卷除外） | 僅限管理員（不可封鎖） |


---

有任何建議、Bug 回報或想一起開發，歡迎開 PR 或 issue 🙌


