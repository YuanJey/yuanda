import argparse
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def check(src):
    """通过网络请求验证MAC地址"""
    url = 'https://test-1312265679.cos.ap-chengdu.myqcloud.com/config_check.json'
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            json_data = response.json()
            checks_list = json_data.get('checks', [])
            if src in checks_list:
                return 1
        print('网络请求失败或未找到匹配的机器信息')
        return 0
    except requests.RequestException as e:
        print('请求错误:', e)
        return 0

# 固定页面链接
m_100 = 'https://sc.yuanda.biz/pg/234.html'
m_200 = 'https://sc.yuanda.biz/pg/235.html'
m_500 = 'https://sc.yuanda.biz/pg/237.html'
m_1000 = 'https://sc.yuanda.biz/pg/240.html'
m_2000 = 'https://sc.yuanda.biz/pg/241.html'

# global f_100,f_200,f_500,f_1000,f_2000
def buy(url, number):
    try:
        driver.get(url)
        buy_button = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.cart-buy > a.buy-btn'))
        )
        # 使用JavaScript点击
        driver.execute_script("arguments[0].click();", buy_button)

        # 找“找人代付”并点击
        pay_button = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.ID, 'alipay'))
        )
        driver.execute_script("arguments[0].click();", pay_button)

        # 点击结算按钮
        submit_btn = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.ID, 'jiesuan'))
        )
        # 使用JavaScript点击
        driver.execute_script("arguments[0].click();", submit_btn)

        success_message = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, 'zhengwen'))
        )
        message_text = success_message.text
        print("成功信息：", message_text)

        print(number,"面额购买成功+1")
    except Exception as e:
        print(f"操作失败：{e}","金额:",number)
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
        time.sleep(5)  # 等待5秒
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
        veriimg = driver.find_element(By.ID, 'veriimg')
        file_path = './' + account + '/veriimg.png'
        #确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        veriimg.screenshot(file_path)
        captcha_code = get_code_from_path(file_path, "4f7fe23e7cd68680a6b320982be0a1c9")
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
            time.sleep(3)  # 等待页面加载
            current_url = driver.current_url
            if current_url == 'https://sc.yuanda.biz/jingdian/user/uscenter.html':
                print('登录成功！')
                break
            else:
                print('登录失败，重新识别验证码...')
        else:
            print('验证码识别失败，重试...')
        time.sleep(1)  # 做适当延时，避免请求过快

def logout():
    try:
        # 点击退出登录按钮
        logout_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@href="/jingdian/User/loginOut.html"]'))
        )
        # 直接点击
        logout_link.click()
        print("已成功退出登录。")
    except Exception as e:
        print(f"退出登录失败：{e}")

def start(num100,num200,num500,num1000,num2000):
    for i in range(num100):
        buy(m_100, 100)
    for i in range(num200):
        buy(m_200, 200)
    for i in range(num500):
        buy(m_500, 500)
    for i in range(num1000):
        buy(m_1000, 1000)
    for i in range(num2000):
        buy(m_2000, 2000)

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
def get_key():
    with open('key.txt', 'r', encoding='utf-8') as file:
        key=''
        for line in file:
            line = line.strip()
            if not line:
                continue  # 跳过空行
            key = line

    return key

def create_driver():
    # options = Options()
    # timestamp = str(int(time.time() * 1000))  # 毫秒时间戳
    # profile_dir = os.path.join("./", timestamp)
    # options.add_argument(f'--user-data-dir={profile_dir}')
    # return webdriver.Chrome(options=options)
    return webdriver.Chrome()
driver=create_driver()

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

#获取余额 <span class="corg">0.00 元</span>
def get_balance():
    """获取账户余额"""
    url = 'https://sc.yuanda.biz/jingdian/User/usCenter.html'
    driver.get(url)
    # 等待元素出现（最多等待10秒）
    wait = WebDriverWait(driver, 10)
    balance_element = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, 'corg'))
    )
    # 获取余额文本 '0.00 元'
    balance_text = balance_element.text
    print(f"余额：{balance_text}")
    balance_text = balance_text.replace('元', '').strip()
    balance_text=balance_text.replace(',', '')
    balance_text = float(balance_text)
    return balance_text


import os
import time
from datetime import datetime


# 模拟 init 函数：检查并创建当日的 _err.txt 文件
def init_err_file():
    date=datetime.now()-timedelta(days=1)
    current_date = date.strftime("%Y-%m-%d")
    filename = f"{current_date}_balance.txt"

    if not os.path.exists(filename):
        try:
            with open(filename, 'w') as f:
                pass  # 创建空文件
        except Exception as e:
            print(f"创建文件失败: {e}")


# 保存账号与余额到文件
def save_balance_to_file(k: str, v: str):
    init_err_file()
    date = datetime.now() - timedelta(days=1)
    current_date = date.strftime("%Y-%m-%d")
    filename = f"{current_date}_balance.txt"

    try:
        with open(filename, 'a') as f:  # a 表示追加模式
            f.write(f"{k}\t{v}\n")
    except Exception as e:
        print(f"写入文件失败: {e}")


if __name__ == '__main__':
    phone=get_key()
    print("授权的手机号: ",phone)
    result = check(phone)
    if result:
        print("手机号验证通过，即将开始执行。")
        print(os.getcwd())
        parser = argparse.ArgumentParser(description='账户信息')
        parser.add_argument('account', type=str, help='账户')
        parser.add_argument('password', type=str, help='密码')
        parser.add_argument('--num100', type=int, default=0, help='100元数量')
        parser.add_argument('--num200', type=int, default=0, help='200元数量')
        parser.add_argument('--num500', type=int, default=0, help='500元数量')
        parser.add_argument('--num1000', type=int, default=0, help='1000元数量')
        parser.add_argument('--num2000', type=int, default=0, help='2000元数量')
        args = parser.parse_args()
        num100 = args.num100
        num200 = args.num200
        num500 = args.num500
        num1000 = args.num1000
        num2000 = args.num2000
        account = args.account
        password = args.password
        # account = "nuoshou776"
        # password = "Yuan970901"
        print("账号信息: ",account,password)
        login(account, password)
        cookie=get_cookie()
        download_file(cookie, account)
        balance=get_balance()
        save_balance_to_file(account, str(balance))
        while True:
            balance = get_balance()
            if balance >=30000.00:
                print("余额大于等于30000元，即将开始执行。")
                break
            else:
                print("余额小于30000元，等待充值...")
                time.sleep(10)
        start(num100,num200,num500,num1000,num2000)
        balance = get_balance()
        print("执行完成，当前余额：",account, balance)
    else:
        print("手机号验证未通过或无权限。")