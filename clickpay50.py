import time
from datetime import datetime
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. 連線設定
caps = {
    "platformName": "iOS",
    "appium:automationName": "XCUITest",
    "appium:bundleId": "tw.com.icash.i.icashpay.sit",
    "appium:noReset": True,
    "appium:deviceName": "iPhone 15 Pro",
    "appium:connectHardwareKeyboard": False
}

driver = webdriver.Remote("http://127.0.0.1:4723", options=AppiumOptions().load_capabilities(caps))
wait = WebDriverWait(driver, 10)


def get_barcode_text():
    """抓取 IC 開頭的條碼"""
    try:
        el = wait.until(EC.presence_of_element_located(
            (AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeStaticText' AND label BEGINSWITH 'IC'")))
        return el.get_attribute("label")
    except:
        return None


def click_refresh_by_name():
    """使用 name == 'image_refresh_v3' 定位並計算座標點擊"""
    try:
        # 使用 presence_of_element_located 找到不可見的按鈕
        target_el = wait.until(EC.presence_of_element_located(
            (AppiumBy.IOS_PREDICATE, "name == 'image_refresh_v3'")))

        # 獲取該元件的實際座標與大小
        rect = target_el.rect
        click_x = rect['x'] + (rect['width'] / 2)
        click_y = rect['y'] + (rect['height'] / 2)

        print(f"  ➔ 定位到按鈕，執行座標點擊: ({click_x}, {click_y})")

        # 使用 mobile: tap 進行物理點擊
        driver.execute_script('mobile: tap', {'x': click_x, 'y': click_y})
        return True
    except Exception as e:
        print(f"  ❌ 定位刷新按鈕失敗: {e}")
        return False


try:
    print("--- 開始執行 5 次循環 (含 txt 存檔) ---")

    # Step 1: 點擊付款按鈕
    wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "image main pay"))).click()

    # Step 2: 輸入密碼
    wait.until(EC.presence_of_element_located((AppiumBy.IOS_PREDICATE, "label == '2'")))
    for key in ["2", "4", "6", "7", "9", "0"]:
        driver.find_element(by=AppiumBy.IOS_PREDICATE, value=f"label == '{key}'").click()
        time.sleep(0.2)
    print("✅ 已進入條碼頁面")

    # --- 開啟檔案準備寫入 ---
    # 使用 'w' 模式，每次執行都會覆蓋舊檔案；若要保留舊紀錄可改用 'a' (append)
    with open("barcode_history.txt", "w", encoding="utf-8") as log_file:

        # 寫入檔頭資訊
        start_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file.write(f"--- icash Pay 條碼更新紀錄 ({start_time_str}) ---\n")
        log_file.write(f"{'次數':<10}{'時間':<12}{'條碼內容'}\n")
        log_file.write("-" * 40 + "\n")

        # 初始化：先抓取第一次的條碼
        last_barcode = get_barcode_text()
        print(f"\n[初始條碼] {last_barcode}")
        log_file.write(f"{'初始':<10}{datetime.now().strftime('%H:%M:%S'):<12}{last_barcode}\n")

        # --- 核心循環：執行 5 次更新測試 ---
        for i in range(1, 6):
            print(f"\n--- 第 {i} 次更新測試 ---")

            # A. 執行刷新動作
            if click_refresh_by_name():

                # B. 驗證更新：持續檢查直到條碼改變
                print("  等待條碼更新中...", end=" ", flush=True)
                new_barcode = None
                start_check_time = time.time()

                # 給予最多 10 秒等待時間
                while time.time() - start_check_time < 10:
                    current_temp = get_barcode_text()
                    if current_temp and current_temp != last_barcode:
                        new_barcode = current_temp
                        break
                    time.sleep(1)

                    # C. 輸出結果並寫入檔案
                if new_barcode:
                    current_time = datetime.now().strftime('%H:%M:%S')
                    print(f"\n  ✅ 條碼已更新! 新條碼: {new_barcode}")

                    # 寫入 txt
                    log_file.write(f"第 {i} 次   {current_time}    {new_barcode}\n")
                    # 確保立即寫入磁碟 (Optional)
                    log_file.flush()

                    last_barcode = new_barcode
                else:
                    print("\n  ⚠️ 超時：條碼內容未變動")
                    log_file.write(f"第 {i} 次   FAILED      條碼未更新\n")

            # 休息一下再進行下一輪
            time.sleep(2)

    print("\n--- 🏁 測試結束，結果已存入 barcode_history.txt ---")

except Exception as e:
    print(f"\n❌ 發生錯誤: {e}")

finally:
    driver.quit()