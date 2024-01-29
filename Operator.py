class Operator:
    import time
    import requests
    from bs4 import BeautifulSoup
    import re

    cookies = None
    student_id = None
    t = str(round(time.time() * 1000))  # 13位时间戳
    session = requests.session()  # 创建一个session

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/120.0.0.0 '
                      'Safari/537.36 Edg/120.0.0.0',
        'cookies': cookies
    }

    def get_publicKey(self):  # 获取公钥
        url = "https://jwxt.gxnzd.com.cn/jwglxt/xtgl/login_getPublicKey.html?time=" + self.t + "&_=" + str(int(self.t) + 79)
        response = self.session.get(url=url, headers=self.headers).json()
        return response["modulus"], response["exponent"]

    def get_enPassword(self, password):  # 返回加密过的密码
        publickey = self.get_publicKey()
        modulus = publickey[0]
        exponent = publickey[1]
        import execjs
        with open('enPassword.js', mode='r', encoding='utf-8') as js:
            js = js.read()
        js = execjs.compile(js)
        enPassword = js.call('PWD', modulus, exponent, password)
        return enPassword

    def get_csrftoken(self):  # 获取csrftoken
        url = "https://jwxt.gxnzd.com.cn/jwglxt/xtgl/login_slogin.html"
        response = self.session.get("https://jwxt.gxnzd.com.cn/jwglxt/xtgl/login_slogin.html").text
        soup = self.BeautifulSoup(response, "lxml")
        return soup.find("input", attrs={"id": "csrftoken"})["value"]

    def login(self, userName, password):  # 登录主程序

        url = "https://jwxt.gxnzd.com.cn/jwglxt/xtgl/login_slogin.html?time=" + self.t
        enPassword = self.get_enPassword(password)
        data = {
            "csrftoken": self.get_csrftoken(),
            "language": "zh_CN",
            "yhm": userName,
            "mm": enPassword,
            "mm": enPassword
        }
        response = self.session.post(url=url, data=data, headers=self.headers).text

        if "退出" in response:
            print("登录成功！")
            student_id = userName

            # 获取cookies
            JSESSIONID = self.re.search(r'(JSESSIONID=[^ ]+)', str(self.session.cookies)).group(1)
            route = self.re.search(r'(route=[^ ]+)', str(self.session.cookies)).group(1)
            cookies = JSESSIONID + "; " + route
            # 保存登录信息
            with open("config.ini", "w", encoding="utf-8") as f:
                f.write("userName:" + userName + "\n")
                f.write("password:" + password + "\n")
                f.write("cookies:" + cookies + "\n")
            return True
        else:
            print("登录失败，请检查！")
            return False

    def cookies_login(self, cookie):  # 使用cookie登录
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 '
                          'Safari/537.36 Edg/120.0.0.0',
            "Cookie": cookie
        }
        url = "https://jwxt.gxnzd.com.cn/jwglxt/xtgl/index_initMenu.html?jsdm=xs&_t=" + self.t
        response = self.requests.get(url=url, headers=headers)
        if "退出" in response.text:
            # print("登录成功")
            return True
        else:
            print("登录失败")
            return False

    def logout(self):
        url = "https://jwxt.gxnzd.com.cn/jwglxt/logout?t=" + str(int(self.time.time() * 1000)) + "&login_type="
        response = self.session.get(url=url, headers=self.headers)
        print("退出成功！")

    """

    以下为教务系统操作类


    """

    def get_score(self):  # 查询成绩

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 '
                          'Safari/537.36 Edg/120.0.0.0',
            "Cookie": self.cookies
        }

        scores = {}  # 建立一个存放成绩的空字典
        url = "https://jwxt.gxnzd.com.cn/jwglxt/cjcx/cjcx_cxXsgrcj.html?doType=query&gnmkdm=N305005&su=" + str(
            self.student_id)
        data = {
            "xnm": "",
            "xqm": "",
            "_search": "false",
            "nd": "t",
            "queryModel.showCount": "15",
            "queryModel.currentPage": "1",
            "queryModel.sortName": "",
            "queryModel.sortOrder": "asc",
            "time": "0"
        }
        if self.cookies is None:  # 不使用cookies登录
            response = self.session.post(url=url, data=data, headers=headers).json()
        else:
            response = self.requests.post(url=url, data=data, headers=headers).json()

        # return response.json()
        # 处理成绩
        for item in response["items"]:
            scores[item["kcmc"]] = float(item["cj"])

        return scores


