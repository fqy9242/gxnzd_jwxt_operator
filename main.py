import os
from Operator import *
import send


def main():  # 程序初始页
    login_status = False
    jwxt = Operator()
    print("欢迎使用教务系统操作程序，请勿用于非法操作！")
    """
    读取配置
    
    """
    if os.path.exists("config.ini"):  # 寻找配置是否存在
        with open("config.ini", "r", encoding="utf-8") as f:
            if f.readline() != "":
                f.seek(0)
                date = f.read().splitlines()
                userName = date[0].strip("userName:")
                password = date[1].strip("password:")
                cookies = date[2].strip("cookies:")
                print("===正在尝试使用cookies登录===")
                if jwxt.cookies_login(cookies):  # 尝试使用cookie登录
                    print("登录成功！")
                    jwxt.cookies = cookies
                    login_status = True
                else:
                    print("===尝试使用上次的账号登录===")
                    login = jwxt.login(userName, password)
                    if login:
                        print("登录成功")
                        login_status = True
                    else:
                        print("登录失败")
    if not login_status:  # 还未登录成功
        while True:
            userName = input("请输入您的学号:")
            password = input("请输入您的密码:")
            login = jwxt.login(userName, password)
            if login:
                login_status = True
                break

    while True:
        print("请选择以下命令进行您的操作：")
        print("1.查询成绩\t2.退出登录\t")
        select = input("请输入:")
        if select == "1":
            scores = jwxt.get_score()
            print(scores)
            sent_str = ""
            average_score = sum(scores.values()) / len(scores)
            for course in scores:
                sent_str += f"{course}:{scores[course]}\n"
            sent_str += f"最低分:{min(scores.values())}\n最高分:{max(scores.values())}\n平均分:{sum(scores.values())/ len(scores)}"
            send.sendmsg("oHMtq63KaBZw3zASYwdcUNt1VZGI", sent_str)

        elif select == "2":
            jwxt.logout()
            login_status = False
        elif select == "3":
            pass


if __name__ == '__main__':
    main()
