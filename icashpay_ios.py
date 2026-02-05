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
    "appium:deviceName": "iPhone 15 Pro"
}

options = AppiumOptions().load_capabilities(caps)
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

wait = WebDriverWait(driver, 8)
short_wait = WebDriverWait(driver, 3)


# ===========================
# 2. 功能函式定義
# ===========================

def check_and_close_popup():
    """檢測並關閉彈窗"""
    try:
        popup_btn = short_wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "下次再說")))
        popup_btn.click()
        print("(已關閉彈窗)", end=" ")
    except:
        pass


def handle_security_password():
    """自動輸入 6 位數安全密碼"""
    try:
        short_wait.until(EC.presence_of_element_located(
            (AppiumBy.XPATH, '//XCUIElementTypeStaticText[contains(@name, "安全密碼")]')))
        print("🔒 輸入密碼...", end=" ")
        time.sleep(1)
        for digit in "246790":
            driver.find_element(AppiumBy.ACCESSIBILITY_ID, digit).click()
            time.sleep(0.3)
        time.sleep(2)
        return True
    except:
        return False


def swipe_vertical(direction="down"):
    """垂直滑動"""
    size = driver.get_window_size()
    start_x = size['width'] * 0.5
    if direction == "down":
        start_y, end_y = size['height'] * 0.7, size['height'] * 0.3
    else:
        start_y, end_y = size['height'] * 0.3, size['height'] * 0.7

    driver.execute_script("mobile: dragFromToForDuration", {
        "duration": 0.5, "fromX": start_x, "fromY": start_y, "toX": start_x, "toY": end_y
    })
    time.sleep(1)


def swipe_horizontal(to_right=True):
    """橫向滑動"""
    size = driver.get_window_size()
    fixed_y = size['height'] * 0.28
    if to_right:
        start_x, end_x = size['width'] * 0.85, size['width'] * 0.15
    else:
        start_x, end_x = size['width'] * 0.15, size['width'] * 0.85

    driver.execute_script("mobile: dragFromToForDuration", {
        "duration": 0.6, "fromX": start_x, "fromY": fixed_y, "toX": end_x, "toY": fixed_y
    })
    time.sleep(1)


def run_tax_sub_tests():
    """繳費稅子功能測試"""
    tax_items = ["綜所稅", "停車費", "水費", "電費", "電信費", "瓦斯費", "健保費"]
    print("\n    >>> [繳費稅] 子巡檢", end=" ")
    time.sleep(3)
    for _ in range(3): swipe_horizontal(to_right=False)

    for item in tax_items:
        try:
            print(f"[{item}]", end=" ", flush=True)
            found_btn = None
            for _ in range(2):
                try:
                    found_btn = short_wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, item)))
                    break
                except:
                    swipe_horizontal(to_right=True)

            found_btn.click()
            time.sleep(1.5)
            handle_security_password()

            back_id = "icn close" if item in ["綜所稅", "健保費"] else "icp ic left nav white arrow"
            wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, back_id))).click()
            time.sleep(1)
        except:
            print(f"(X)", end=" ")
            driver.back()


def run_loop_test():
    features_to_test = ["支付工具", "儲值", "轉帳", "乘車碼", "生活服務", "繳費稅", "我的"]
    success_count = 0
    for feature in features_to_test:
        print(f"測試: [{feature}]", end=" ", flush=True)
        try:
            wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, feature))).click()
            time.sleep(1.5)
            handle_security_password()
            check_and_close_popup()

            if feature == "繳費稅":
                run_tax_sub_tests()
                driver.back()
            elif feature == "乘車碼":
                try:
                    wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "Close"))).click()
                except:
                    driver.back()
            elif feature == "我的":
                print("\n    >>> [我的] 子巡檢", end=" ")
                for _ in range(2): swipe_vertical(direction="up")  # 回到頁面頂端

                # 按照截圖規劃的子項目順序
                my_sub_items = [
                    "個人資訊", "交易限額", "設定", "會員卡", "使用教學",
                    "版本與登入紀錄", "常見問題", "服務條款", "聯絡我們"
                ]

                for item in my_sub_items:
                    print(f"[{item}]", end=" ", flush=True)
                    try:
                        target = None
                        for _ in range(3):
                            try:
                                target = short_wait.until(
                                    EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, item)))
                                if target.location['y'] > driver.get_window_size()['height'] * 0.85:
                                    raise Exception("too low")
                                break
                            except:
                                swipe_vertical(direction="down")

                        if not target: raise Exception("Not Found")

                        target.click()
                        time.sleep(2)
                        handle_security_password()

                        # 統一使用 icp ic left nav white arrow 進行返回
                        try:
                            back_btn = wait.until(
                                EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "icp ic left nav white arrow")))
                            back_btn.click()
                        except:
                            driver.back()

                        time.sleep(1.5)
                    except:
                        print(f"❌", end=" ")
                        # 嘗試恢復 App 狀態
                        driver.execute_script('mobile: activateApp', {'bundleId': 'tw.com.icash.i.icashpay.sit'})
                        time.sleep(2)

                print("\n    <<< [我的] 結束", end=" ")
            else:
                time.sleep(1)
                driver.back()

            print("✅")
            success_count += 1
        except Exception:
            print("❌")
            driver.execute_script('mobile: activateApp', {'bundleId': 'tw.com.icash.i.icashpay.sit'})

    print(f"\n巡檢完成！ 通過: {success_count}/{len(features_to_test)}")

    # ===========================
    # 4. 回到首頁
    # ===========================
    try:
        print("正在點擊底部 [首頁] 按鈕...", end=" ")
        # 使用截圖提供的 Accessibility ID: image main home
        home_btn = wait.until(EC.element_to_be_clickable((AppiumBy.ACCESSIBILITY_ID, "image main home")))
        home_btn.click()
        print("✅ 已回到首頁")
    except Exception as e:
        print(f"無法回首頁: {e}")


# ===========================
# 3. 主程式進入點
# ===========================
try:
    run_loop_test()
finally:
    if 'driver' in locals():
        driver.quit()