# Discord 機器人

## 概述

本機器人提供一個簡單的經濟系統與任務型簽到機制，同時也提供了商品系統可以讓成員進行商品購買，或是讓成員自行上架商品進行販售。

> 由於這機器人是提供給一個情慾系 Discord 群做使用，所以有些指令敘述會比較特別；若有調整需要可以進行 Fork 並自行替換。

## 環境建置

1. 安裝 [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Clone 此專案
3. `cp .env.example > .env` 並進行專案所需資料設定
4. 在此專案資料夾根目錄底下使用 `docker compose up` 建立環境

> ***求助***
>
> 你會在 python 中使用 Migration 嗎？  
> 這個專案需要你的幫助！
>
> 目前此專案無法透過 Migration 自動建立資料庫環境與寫入初始資料。  
> 所以我們需要你的協助！
>
> 請提供 Pull Request 協助完善這部分的開發！

## 功能詳解

每個指令都會標注「可見度」，  
這代表當你使用該指令時，跳出的互動訊息是否可以被其他人所看見。

某些指令被設定為「大家都可以看見」是為了讓大家可以知道你發生了什麼事情，  
例如「簽到」的領取任務，就是全成員可見。  

這是為了讓成員們能將這樣的結果當作話題閒聊用，刺激活躍度。  
若有客製化需求仍然可以 Fork 並自行調整。

> 注意，私人訊息有時效限制，當時效到期或是重整畫面，訊息都會消失。

### /personal 個人資料模組

- `/personal 個人資料`
    > 可見度：自己

    - 查看當前自己的錢包餘額
    - 查看當前自己的連續簽到紀錄
- `/personal 富翁榜`
    > 可見度：自己

    - 查看 Discord 群內前十名帳戶餘額最高的成員
- `/personal 簽到榜`
    > 可見度：自己

    - 查看 Discord 群內前十名連續簽到紀錄最高的成員

### /check-in 簽到模組

每天 00:00:00 (UTC+8, 台灣時區) 會檢查是否有人最後簽到日期不等於昨天，  
若有則進行連勝紀錄清空。

- `/check-in 簽到`
    > 可見度：公開

    - 隨機從題庫中取得一則題目並分配給成員
- `/check-in 任務`
    > 可見度：自己

    - 成員可以查看自己身上的任務

- `/check-in 任務回報`
    > 可見度：自己

    - 成員完成任務後，可以進行任務回報，並發放獎勵金給成員

    > 本機器人並沒有針對任務是否確實被玩家完成進行客製化開發，  
    > 若有這類需要，請試著 Fork 並進行客製化開發。

### /shop 商店模組

- `/shop 查看商品`
    > 可見度：自己

    - 以分頁的方式瀏覽商品
    - 可以指定特定成員，只查看他上架的商品

- `/shop 購買商品`
    > 可見度：自己

    - 輸入從 `/shop 查看商品` 中看到的商品編號來進行商品購買。
    - 輸入後，會先檢視該商品的資料，如果確定要買再按下按鈕即可。
    
    > 購買後，上架方會收到一則 Direct Message 紀錄購買記錄，  
    > 由於這指令的可見度是「自己」的關係，  
    > 代表除了上架方和你之外，不會有人知道你買了什麼。

    > 購買後不會立刻將錢轉給上架者，  
    > 購買者必須進行「兌換」才代表使用，這時上架者才會收到錢。  

- [ ] `/shop 商品上架`
    > 可見度：自己

    - TODO

- [ ] `/shop 商品下架`
    > 可見度：自己
    
    - TODO


### /inventory 背包模組

- `/inventory 查看背包`
    > 可見度：自己

    - 以分頁的方式查看目前尚未使用的商品

- `/inventory 兌換商品`
    > 可見度：自己

    - 以下拉選單的方式，選擇目前有購買的商品並進行兌換

### /bank 銀行模組

- `/bank 轉帳`
    > 可見度：自己

    - 指定要轉帳的成員與金額，將你帳上的金額轉帳給對方。

    > 轉帳後，雙方都會收到一則 Direct Message 紀錄轉帳資料


### /manager 管理員模組

- [ ] `/manager 金錢發放`

- [ ] `/manager 金錢扣除`

- [ ] `/manager 上架任務`