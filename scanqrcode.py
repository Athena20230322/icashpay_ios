import time
from appium import webdriver
from appium.options.common import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ===========================
# 1. 連線設定與 Driver 初始化
# ===========================
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

wait = WebDriverWait(driver, 20)
short_wait = WebDriverWait(driver, 5)


# ===========================
# 2. 功能函式定義
# ===========================

def handle_security_password():
    """檢測並輸入安全密碼 246790"""
    try:
        short_wait.until(EC.presence_of_element_located(
            (AppiumBy.IOS_PREDICATE, "label CONTAINS '安全密碼'")))
        print("🔒 偵測到密碼鎖，正在輸入 246790...", end=" ")
        time.sleep(1)
        for digit in ["2", "4", "6", "7", "9", "0"]:
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, digit).click()
            time.sleep(0.3)
        print("✅", end=" ")
        time.sleep(2)
        return True
    except:
        return False


def run_positive_scan_test(iteration):
    """執行單次正掃付款流程"""
    try:
        print(f"\n>>> 開始執行第 {iteration} 次測試循環 <<<")

        # Step 1: 點擊 payment scan
        wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "payment scan"))).click()
        print(f"Step 1: Payment Scan ✅", end=" ")

        # Step 2: 點擊 icon photo
        wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "icon photo"))).click()
        print(f"Step 2: Icon Photo ✅", end=" ")

        # Step 3: 座標點擊第一張照片
        time.sleep(2)
        size = driver.get_window_size()
        driver.execute_script('mobile: tap', {'x': size['width'] * 0.2, 'y': size['height'] * 0.2})
        print(f"Step 3: Tap Photo ✅", end=" ")

        # Step 4: 付款資訊頁輸入金額
        wait.until(EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "付款資訊")))
        try:
            wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "TWD"))).click()
            time.sleep(1.5)
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "1").click()
        except:
            driver.execute_script('mobile: tap', {'x': size['width'] * 0.5, 'y': size['height'] * 0.35})
            time.sleep(1.5)
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, "1").click()
        print(f"Step 4: Input Amount ✅", end=" ")

        # Step 5 ~ 7: 下一步、密碼、完成
        wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "下一步"))).click()
        print(f"Step 5: Next ✅", end=" ")

        handle_security_password()

        wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "完成"))).click()
        print(f"Step 7: Finish ✅", end=" ")

        # Step 8: 回首頁
        time.sleep(4)
        home_success = False
        for _ in range(3):
            try:
                home_btn = short_wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "image main home")))
                home_btn.click()
                home_success = True
                print(f"Step 8: Back Home ✅")
                break
            except:
                time.sleep(1)

        if not home_success:
            # 座標備案
            driver.execute_script('mobile: tap', {'x': size['width'] * 0.45, 'y': size['height'] * 0.94})
            print(f"Step 8: Back Home (Coord) ✅")

        return True

    except Exception as e:
        print(f"\n❌ 第 {iteration} 次測試中斷: {e}")
        # 發生錯誤時重啟 App 確保下一次循環能正常開始
        driver.execute_script('mobile: activateApp', {'bundleId': 'tw.com.icash.i.icashpay.sit'})
        time.sleep(3)
        return False


# ===========================
# 3. 主程式進入點 (執行 5 次)
# ===========================
if __name__ == "__main__":
    success_count = 0
    total_iterations = 5

    print(f"--- 開始正掃付款 5 次循環自動測試 ---")

    for i in range(1, total_iterations + 1):
        if run_positive_scan_test(i):
            success_count += 1
        # 每次循環間休息 2 秒
        time.sleep(2)

    print("\n" + "=" * 30)
    print(f"測試完成！成功次數: {success_count}/{total_iterations}")
    print("=" * 30)

    if 'driver' in locals():
        driver.quit()