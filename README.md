# evon-gui

* 前言：

  這個GUI介面是一個整合平台，包含：Arduino感測數據即時擷取、數據即時視覺化呈現(電壓line plot及即時頻率)、數據儲存至SQL資料庫、以及後續之資料庫讀取功能。
是自學Python之早期，從零開始設計與實現出的專案
https://drive.google.com/file/d/1d9gAYcyEb2PYeNsidIf4bXMx22luTeil/view?usp=share_link


* 規格

  支援兩個Arduino開發版，1~16個感測器


* 專案設計：

  1. 使用物件導向程式設計(object-oriented programming)：擴充很容易
  2. 使用Model-View-Controller(MVC)設計模式：維護上很容易
  3. 使用多線程(mulitple threading)：可以即時進行與處理許多工作


* 程式架構

  分成底層與上層模組，底層模組包含
  1. arduino_to_sql_3: 進行Arduino感測數據擷取、儲存至資料庫。
  2. data: 數據校正計算與傅立葉頻譜與相位提取。
  3. read_sql: 歷史資料庫讀取，以及條件過濾。
  4. frames: GUI介面之各個Frame物件設計與功能。
  5. func: 相關使用函數。

  上層模組為gui，負責功能調用與控制。


* 調用接口為 app.py


