import argparse
import os
import time
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import requests
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait


chrome_options = Options()
# chrome_options.add_argument("--headless")  # 启用无头模式
# chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速（某些系统需要）
# chrome_options.add_argument("--no-sandbox")  # 提升权限兼容性
# chrome_options.add_argument("--window-size=1920,1080")  # 设置窗口大小（可选）

# 初始化 WebDriver 并应用配置
driver = webdriver.Chrome(options=chrome_options)
# driver=webdriver.Chrome()


def get_code_from_path(image_path, api_key):
    # 读取本地图片内容（二进制）
    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
    except FileNotFoundError:
        print("图片文件未找到")
        return None

    # 上传到2Captcha
    files = {'file': ('captcha.png', image_bytes)}
    data = {
        'key': api_key,
        'method': 'post',
        'json': 1
    }
    response = requests.post(
        'https://2captcha.com/in.php',
        data=data,
        files=files
    )
    upload_result = response.json()

    if upload_result['status'] != 1:
        print('上传验证码失败:', upload_result['request'])
        return None

    captcha_id = upload_result['request']
    print('上传成功，任务ID:', captcha_id)

    # 轮询等待验证码识别结果
    fetch_url = f'https://2captcha.com/res.php?key={api_key}&action=get&id={captcha_id}&json=1'
    for i in range(20):  # 最多轮询20次
        time.sleep(3)  # 等待5秒
        res_response = requests.get(fetch_url)
        res_json = res_response.json()
        if res_json['status'] == 1:
            print('识别结果:', res_json['request'])
            return res_json['request']
        elif res_json['request'] == 'CAPCHA_NOT_READY':
            print('验证码还在识别中，等待中...')
        else:
            print('识别失败:', res_json['request'])
            return None
    print('超时未获得识别结果')
    return None
def login(account, password):
    driver.get('https://sc.yuanda.biz/')
    # 点击登录
    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//div//ul//li//a[text()="登录"]'))
    )
    login_btn.click()
    account_input = driver.find_element(By.ID, 'account')
    # 输入账号（例如：testuser）
    account_input.send_keys(account)
    # 找到密码输入框
    password_input = driver.find_element(By.ID, 'password')
    # 输入密码（例如：mypassword123）
    password_input.send_keys(password)
    # 定位按钮
    # login_button = driver.find_element(By.ID, 'loginbtn')
    # # 点击按钮
    # login_button.click()
    # input("登陆完成后，按Enter继续...")
    while True:
        # 获取验证码图片
        veriimg=WebDriverWait(driver,10).until(
            EC.presence_of_element_located((By.ID, 'veriimg'))
        )
        # veriimg = driver.find_element(By.ID, 'veriimg')
        veriimg.screenshot('veriimg.png')
        captcha_code = get_code_from_path("./veriimg.png", "4f7fe23e7cd68680a6b320982be0a1c9")
        if captcha_code:
            print('识别到验证码:', captcha_code)
            # 输入验证码
            veri_input = driver.find_element(By.ID, 'veri')
            veri_input.clear()
            veri_input.send_keys(captcha_code)

            # 定位按钮
            login_button = driver.find_element(By.ID, 'loginbtn')
            # 点击按钮
            login_button.click()
            time.sleep(5)  # 等待页面加载
            current_url = driver.current_url
            if current_url == 'https://sc.yuanda.biz/jingdian/user/uscenter.html':
                print('登录成功！')
                return
        else:
            print('验证码识别失败，重试...')
        time.sleep(1)  # 做适当延时，避免请求过快

def check(src):
    """通过网络请求验证MAC地址"""
    url = 'https://test-1312265679.cos.ap-chengdu.myqcloud.com/config.json'
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            json_data = response.json()
            checks_list = json_data.get('checks', [])
            if src in checks_list:
                return 1
        print('网络请求失败或未找到匹配的MAC')
        return 0
    except requests.RequestException as e:
        print('请求错误:', e)
        return 0
def get_account_password_map(file_path):
    account_password_map = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue  # 跳过空行
            parts = line.split()
            if len(parts) >= 2:
                account = parts[0]
                password = parts[1]
                account_password_map[account] = password

    return account_password_map
def get_cookie():
    """获取cookie"""
    cookies = driver.get_cookies()
    cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
    return cookie_dict
def download_file(cookie,name):
    """下载文件"""
    current_date = datetime.now()
    # 计算前一天的日期
    previous_day = current_date - timedelta(days=1)
    # 格式化输出为字符串（格式为YYYY-MM-DD）
    previous_day_str = previous_day.strftime("%Y-%m-%d")
    directory = Path(previous_day_str)
    # 创建目录（包括所有必要的父目录）
    directory.mkdir(parents=True, exist_ok=True)
    save_path=previous_day_str+"/"+name+".txt"
    url = f"https://sc.yuanda.biz/jingdian/index/export.html?start={previous_day_str}&end="
    # https://sc.yuanda.biz/jingdian/index/export.html?start=2025-06-02&end=
    try:
        response = requests.get(url, cookies=cookie,timeout=10)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
            print(f"文件已下载到: {save_path}")
        else:
            print(f"下载失败，状态码: {response.status_code}")
    except requests.RequestException as e:
        print(f"下载错误: {e}")

def logout():
    try:
        driver.get('https://sc.yuanda.biz/jingdian/User/loginOut.html')
        print("已成功退出登录。")
    except Exception as e:
        print(f"退出登录失败：{e}")
if __name__ == '__main__':
    # 获取MAC地址，并转为字符串
    mac_address = uuid.getnode()
    mac_str = str(mac_address)
    print("检测MAC：", mac_str)
    result = check(mac_str)
    if result:
        print("验证通过，即将开始执行。")
        # parser = argparse.ArgumentParser(description='读取账户密码文件')
        # parser.add_argument('file_path', type=str, help='账户密码文件路径')
        # args = parser.parse_args()
        # file_path = os.path.abspath(args.file_path)
        accounts_info = get_account_password_map("./accounts.txt")
        for account, password in accounts_info.items():
            login(account, password)
            cookie = get_cookie()
            download_file(cookie, account)
            logout()
    else:
        print("MAC验证未通过或无权限。")
