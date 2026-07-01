from Operator import *
from config import load_config
import send


def input_password(prompt):
    try:
        import msvcrt
    except ImportError:
        from getpass import getpass
        return getpass(prompt)

    print(prompt, end="", flush=True)
    password = []
    while True:
        char = msvcrt.getwch()
        if char in ("\r", "\n"):
            print()
            return "".join(password)
        if char == "\x03":
            raise KeyboardInterrupt
        if char == "\b":
            if password:
                password.pop()
                print("\b \b", end="", flush=True)
            continue
        if char in ("\x00", "\xe0"):
            msvcrt.getwch()
            continue
        if not char.isprintable():
            continue

        password.append(char)
        print("*", end="", flush=True)


def query_available_classrooms(jwxt):
    weeks = input("请输入周次(如18):").strip()
    weekday = input("请输入星期(1-7):").strip()
    keyword = input("请输入关键字(可空，默认东区6):").strip() or "东区6"
    sections = input("请输入节次(可空，如10-13或10,11,12,13):").strip()
    period = ""
    if sections == "":
        period = input("请选择时段(可空，1上午/2下午/3晚上):").strip()

    try:
        result = jwxt.get_available_classrooms(
            weeks=weeks,
            weekday=weekday,
            keyword=keyword,
            sections=sections,
            period=period
        )
    except ValueError as error:
        print("查询参数错误：" + str(error))
        return

    classrooms = result.get("items", [])
    if not classrooms:
        print("未查询到空教室")
        return

    print("查询结果：")
    for classroom in classrooms:
        name = classroom.get("cdmc", "")
        can_borrow = classroom.get("sfkjy", "")
        seats = classroom.get("zws", "")
        classroom_type = classroom.get("cdlbmc", "")
        print(f"{name}\t可借用:{can_borrow}\t座位:{seats}\t类型:{classroom_type}")


def check_classroom_list_empty(jwxt):
    keywords = input("请输入教室关键字列表(逗号分隔，如东区6栋401,东区6栋402):").strip()
    weeks = input("请输入周次(如18):").strip()
    weekday = input("请输入星期(1-7):").strip()
    sections = input("请输入节次(可空，如10-13或10,11,12,13):").strip()
    period = ""
    if sections == "":
        period = input("请选择时段(可空，1上午/2下午/3晚上):").strip()

    try:
        not_empty_classrooms = jwxt.get_not_empty_classrooms(
            keywords=keywords,
            weeks=weeks,
            weekday=weekday,
            sections=sections,
            period=period
        )
    except ValueError as error:
        print("查询参数错误：" + str(error))
        return

    if not not_empty_classrooms:
        print("全部为空")
        return

    print("以下教室没空：")
    for classroom in not_empty_classrooms:
        keyword = classroom.get("query_keyword", "")
        name = classroom.get("cdmc", "")
        can_borrow = classroom.get("sfkjy", "")
        seats = classroom.get("zws", "")
        classroom_type = classroom.get("cdlbmc", "")
        print(f"{keyword}\t{name}\t可借用:{can_borrow}\t座位:{seats}\t类型:{classroom_type}")


def main():  # 程序初始页
    login_status = False
    jwxt = Operator()
    print("欢迎使用教务系统操作程序，请勿用于非法操作！")
    """
    读取配置
    
    """
    config = load_config()  # 寻找配置是否存在
    userName = config.get("JWXT_USERNAME")
    password = config.get("JWXT_PASSWORD")
    cookies = config.get("JWXT_COOKIES")
    if cookies:
        print("===正在尝试使用cookies登录===")
        if jwxt.cookies_login(cookies):  # 尝试使用cookie登录
            print("登录成功！")
            jwxt.cookies = cookies
            jwxt.student_id = userName
            login_status = True
        else:
            print("===尝试使用上次的账号登录===")
    if not login_status and userName and password:
        login = jwxt.login(userName, password)
        if login:
            print("登录成功")
            login_status = True
        else:
            print("登录失败")
    if not login_status:  # 还未登录成功
        while True:
            userName = input("请输入您的学号:")
            password = input_password("请输入您的密码:")
            login = jwxt.login(userName, password)
            if login:
                login_status = True
                break

    while True:
        print("请选择以下命令进行您的操作：")
        print("1.查询成绩\t2.退出登录\t3.查询空教室\t4.检查教室列表是否为空\t")
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
            query_available_classrooms(jwxt)
        elif select == "4":
            check_classroom_list_empty(jwxt)


if __name__ == '__main__':
    main()
