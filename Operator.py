from config import save_config


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
    period_sections = {
        "1": "1-5",
        "上午": "1-5",
        "morning": "1-5",
        "2": "6-10",
        "下午": "6-10",
        "afternoon": "6-10",
        "3": "10-13",
        "晚上": "10-13",
        "evening": "10-13",
        "night": "10-13"
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
            self.student_id = userName

            # 获取cookies
            JSESSIONID = self.re.search(r'(JSESSIONID=[^ ]+)', str(self.session.cookies)).group(1)
            route = self.re.search(r'(route=[^ ]+)', str(self.session.cookies)).group(1)
            cookies = JSESSIONID + "; " + route
            self.cookies = cookies
            # 保存登录信息
            save_config(userName, password, cookies)
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

    def _to_bitmask(self, values, field_name):
        if isinstance(values, int):
            values = [values]
        elif isinstance(values, str):
            values = self._parse_number_selection(values, field_name)
        else:
            values = list(values)

        if not values:
            raise ValueError(field_name + "不能为空")

        bitmask = 0
        for value in values:
            value = int(value)
            if value < 1:
                raise ValueError(field_name + "必须大于等于1")
            bitmask |= 1 << (value - 1)
        return str(bitmask)

    def _parse_number_selection(self, value, field_name):
        values = []
        for item in value.split(","):
            item = item.strip()
            if not item:
                continue
            if "-" in item:
                start, end = item.split("-", 1)
                start = int(start.strip())
                end = int(end.strip())
                if start > end:
                    raise ValueError(field_name + "范围开始值不能大于结束值")
                values.extend(range(start, end + 1))
            else:
                values.append(int(item))
        return values

    def _resolve_sections(self, sections, period):
        if not (sections is None or isinstance(sections, str) and sections.strip() == ""):
            return sections
        if period is None or str(period).strip() == "":
            raise ValueError("节次不能为空，或传入上午/下午/晚上")

        period_key = str(period).strip().lower()
        if period_key not in self.period_sections:
            raise ValueError("时段只能是上午、下午、晚上，或1、2、3")
        return self.period_sections[period_key]

    def _parse_keywords(self, keywords):
        if isinstance(keywords, str):
            keywords = keywords.replace("，", ",").split(",")
        return [keyword.strip() for keyword in keywords if str(keyword).strip()]

    def get_available_classrooms(
            self,
            weeks,
            weekday,
            sections=None,
            period=None,
            xnm="2025",
            xqm="12",
            xqh_id="A9E6F05E39905B29E0552EA72D56AB7C",
            lh="",
            cdlb_id="",
            cdejlb_id="",
            qszws="",
            jszws="",
            keyword="东区6",
            cdmc=None,
            jyfs="0",
            cdjylx="",
            sfbhkc="",
            show_count=15,
            current_page=1,
            sort_name="cdbh ",
            sort_order="asc"
    ):  # 查询可借用场地列表
        """
        weeks和sections支持传入单个数字、数字列表、逗号分隔字符串或范围字符串。
        例如：18、[10, 11, 12, 13]、"10,11,12,13"、"10-13"。
        period可传上午/下午/晚上，只有sections为空时才会使用。
        keyword为场地名称关键字，兼容cdmc参数；传入cdmc时优先使用cdmc。
        """
        weekday = int(weekday)
        if weekday < 1 or weekday > 7:
            raise ValueError("星期必须在1到7之间")
        sections = self._resolve_sections(sections, period)
        if cdmc is not None:
            keyword = cdmc

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 '
                          'Safari/537.36 Edg/120.0.0.0',
            "Cookie": self.cookies
        }
        url = "https://jwxt.gxnzd.com.cn/jwglxt/cdjy/cdjy_cxKxcdlb.html?doType=query&gnmkdm=N2155"
        data = {
            "xqh_id": xqh_id,
            "xnm": str(xnm),
            "xqm": str(xqm),
            "cdlb_id": cdlb_id,
            "cdejlb_id": cdejlb_id,
            "qszws": str(qszws),
            "jszws": str(jszws),
            "cdmc": keyword,
            "lh": lh,
            "jyfs": jyfs,
            "cdjylx": cdjylx,
            "sfbhkc": sfbhkc,
            "zcd": self._to_bitmask(weeks, "周次"),
            "xqj": str(weekday),
            "jcd": self._to_bitmask(sections, "节次"),
            "_search": "false",
            "nd": str(int(self.time.time() * 1000)),
            "queryModel.showCount": str(show_count),
            "queryModel.currentPage": str(current_page),
            "queryModel.sortName": sort_name,
            "queryModel.sortOrder": sort_order,
            "time": "3"
        }
        if self.cookies is None:  # 不使用cookies登录
            response = self.session.post(url=url, data=data, headers=headers).json()
        else:
            response = self.requests.post(url=url, data=data, headers=headers).json()
        return response

    def get_not_empty_classrooms(
            self,
            keywords,
            weeks,
            weekday,
            sections=None,
            period=None,
            **kwargs
    ):  # 查询教室列表是否为空
        """
        keywords支持列表或逗号分隔字符串。
        返回空列表代表传入的教室关键字全部为空；否则返回没空的教室列表。
        """
        keywords = self._parse_keywords(keywords)
        if not keywords:
            raise ValueError("关键字列表不能为空")

        not_empty_classrooms = []
        added_keys = set()
        for keyword in keywords:
            result = self.get_available_classrooms(
                weeks=weeks,
                weekday=weekday,
                sections=sections,
                period=period,
                keyword=keyword,
                **kwargs
            )
            for classroom in result.get("items", []):
                classroom_key = classroom.get("cd_id") or classroom.get("cdmc")
                if classroom_key in added_keys:
                    continue
                classroom = classroom.copy()
                classroom["query_keyword"] = keyword
                not_empty_classrooms.append(classroom)
                added_keys.add(classroom_key)
        return not_empty_classrooms

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


