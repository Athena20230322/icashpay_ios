import time
import base64
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

options = AppiumOptions().load_capabilities(caps)
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
wait = WebDriverWait(driver, 10)


def run_barcode_refresh_test():
    print("\n--- 開始執行付款碼抓取與更新測試 (5次循環版) ---")

    try:
        # Step 1: 進入密碼輸入頁面
        wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "image main pay"))).click()
        print("  ✅ Step1: 點擊底部付款按鈕")

        # Step 2: 輸入安全密碼
        wait.until(EC.presence_of_element_located((AppiumBy.IOS_PREDICATE, "label == '2'")))
        for key in ["2", "4", "6", "7", "9", "0"]:
            driver.find_element(by=AppiumBy.IOS_PREDICATE, value=f"label == '{key}'").click()
            time.sleep(0.2)
        print("  ✅ Step2: 密碼輸入完成，進入付款碼頁面")

        # 開啟檔案準備記錄條碼
        with open("barcode_history.txt", "w", encoding="utf-8") as f:
            f.write("icash Pay 條碼更新紀錄\n" + "=" * 30 + "\n")

            # --- 核心循環：重複執行 5 次 ---
            for i in range(1, 6):
                print(f"  正在執行第 {i} 次條碼抓取...", end=" ", flush=True)

                # Step 3: 抓取 IC 開頭的條碼文字
                # 每次循環都重新定位元件，避免元件失效錯誤
                try:
                    barcode_el = wait.until(EC.presence_of_element_located(
                        (AppiumBy.IOS_PREDICATE, "type == 'XCUIElementTypeStaticText' AND label BEGINSWITH 'IC'")))
                    barcode_text = barcode_el.get_attribute("label")

                    # 存入 txt 檔
                    f.write(f"第 {i} 次抓取: {barcode_text} (時間: {time.strftime('%H:%M:%S')})\n")
                    print(f"✅ 成功: {barcode_text}")
                except Exception as e:
                    print(f"❌ 抓取失敗: {e}")
                    continue

                # Step 4: 點擊重新整理按鈕 (最後一次抓完不需點擊)
                if i < 5:
                    try:
                        refresh_btn = wait.until(EC.element_to_be_clickable(
                            (AppiumBy.ACCESSIBILITY_ID, "image_refresh_v3")))
                        refresh_btn.click()
                        print(f"     ➔ 已點擊重新整理，等待更新...")
                        # 💡 必須給予足夠時間讓條碼刷新，否則會抓到舊的
                        time.sleep(3)
                    except Exception as e:
                        print(f"     ❌ 無法點擊重新整理: {e}")
                        break

        print("\n--- 🏁 5次循環測試完成，請檢查 barcode_history.txt ---")

    except Exception as e:
        print(f"❌ 流程發生嚴重錯誤: {e}")
        driver.get_screenshot_as_file(f"error_barcode_loop.png")


try:
    run_barcode_refresh_test()
finally:
    driver.quit()