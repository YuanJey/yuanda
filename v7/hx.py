import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import requests
from selenium import webdriver


def read_file(file_path):
    account_password_map = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue  # 跳过空行
            parts = line.split()
            if len(parts) >= 2:
                jd_account = parts[0]
                jd_password = parts[1]
                account_password_map[jd_account] = jd_password
    return account_password_map

def verification(jd_account, jd_password,cookie):
    # 目标URL
    url = 'https://hx.yuanda.biz/Home/Card/writeOffCard'

    # 自定义请求头，包含 Cookie 和 Content-Type
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    # 要发送的数据（表单格式）
    data = {
        'cardkey': jd_account,
        'cardpwd': jd_password,
        'cardid': '351',
        'priceid': '2846',
        'typeid': '109',
    }
    # 发送POST请求
    response = requests.post(url, headers=headers,cookies=cookie, data=data)
    # 打印响应状态码和内容
    if response.status_code == 200:
        resp=response.json()
        status = resp.get('status')
        info = resp.get('info')
        if status!=1:
            print("核销失败 ",info,jd_account,jd_password)
        if status==1:
            print("核销成功",info)
    else:
        print("请求失败",jd_account,jd_password)
def get_all_txt():
    current_date = datetime.now()
    # 计算前一天的日期
    previous_day = current_date - timedelta(days=1)
    # 格式化输出为字符串（格式为YYYY-MM-DD）
    file_path = previous_day.strftime("%Y-%m-%d")
    if not os.path.exists(file_path) or not os.path.isdir(file_path):
        print(f"路径 {file_path} 不存在或不是文件夹")
        return []

    txt_files = [os.path.join(file_path, f) for f in os.listdir(file_path) if f.endswith('.txt')]
    return txt_files

def get_cookie():
    """获取cookie"""
    cookies = driver.get_cookies()
    cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
    return cookie_dict
driver=webdriver.Chrome()
# if __name__ == '__main__':
#     driver.get("https://hx.yuanda.biz")
#     input("请在浏览器中完成登陆操作后，按Enter继续...")
#     # parser = argparse.ArgumentParser(description='读取账户密码文件')
#     # parser.add_argument('file_path', type=str, help='账户密码文件路径')
#     # args = parser.parse_args()
#     # file_path = os.path.abspath(args.file_path)
#     # accounts_info = get_account_password_map(file_path)
#
#     accounts_info = get_account_password_map("accounts.txt")
#     for account, password in accounts_info.items():
#         jd_map=read_file(account)
#         with ThreadPoolExecutor(max_workers=5) as executor:
#             for jd_account, jd_password in jd_map.items():
#                 executor.submit(verification(jd_account, jd_password, get_cookie()))


if __name__ == '__main__':
    driver.get("https://hx.yuanda.biz")
    input("请在浏览器中完成登陆操作后，按Enter继续...")
    cookie = get_cookie()  # 统一获取一次 Cookie（确保登录状态有效）
    orders = get_all_txt()
    while True:
        with ThreadPoolExecutor(max_workers=5) as executor:  # 线程池统一管理
            for order in orders:
                jd_map = read_file(order)
                for jd_account, jd_password in jd_map.items():
                    executor.submit(verification, jd_account, jd_password, cookie)
        cont = input("是否继续（1:再次核销，其他任意键，退出）：")
        if cont == '1':
            continue
        else:
            print("退出程序")
            break

