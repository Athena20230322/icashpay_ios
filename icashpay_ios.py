import time
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
    "appium:deviceName": "iPhone 15 Pro"
}

options = AppiumOptions().load_capabilities(caps)
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
# 定義兩個等待時間：一個標準等待，一個快速偵測（用於彈窗）
wait = WebDriverWait(driver, 8)
short_wait = WebDriverWait(driver, 2)

features_to_test = ["支付工具", "儲值", "轉帳", "乘車碼", "生活服務", "繳費稅", "我的"]

def check_and_close_popup():
    """檢測並關閉『下次再說』彈窗"""
    try:
        # 根據截圖，使用 Accessibility ID 定位「下次再說」
        popup_btn = short_wait.until(EC.element_to_be_clickable(
            (AppiumBy.ACCESSIBILITY_ID, "下次再說")))
        popup_btn.click()
        print("(已關閉升級彈窗)", end=" ")
        return True
    except:
        # 如果沒出現彈窗，就直接跳過
        return False

def run_loop_test():
    print(f"--- 開始執行 {len(features_to_test)} 項功能自動巡檢 ---")
    success_count = 0
    fail_list = []

    for feature in features_to_test:
        print(f"正在測試: [{feature}] ...", end=" ", flush=True)
        try:
            # 1. 點擊主功能按鈕
            btn = wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, feature)))
            btn.click()
            time.sleep(1)

            # 2. 核心修正：點擊後立即檢查是否有「下次再說」彈窗
            check_and_close_popup()

            # 3. 執行返回動作回到首頁
            # 某些頁面可能需要點擊內建返回鍵，若 back() 無效可改用 Accessibility ID 定位返回鈕
            time.sleep(1)
            driver.back()

            print("✅ 成功")
            success_count += 1

        except Exception as e:
            print(f"❌ 失敗")
            fail_list.append(feature)
            # 失敗後嘗試重置 App 到首頁狀態，避免卡在錯誤頁面
            driver.execute_script('mobile: activateApp', {'bundleId': 'tw.com.icash.i.icashpay.sit'})

    print("\n" + "=" * 30)
    print(f"巡檢完成！ 通過: {success_count}/{len(features_to_test)}")
    if fail_list: print(f"失敗清單: {fail_list}")
    print("=" * 30)

try:
    run_loop_test()
finally:
    driver.quit()