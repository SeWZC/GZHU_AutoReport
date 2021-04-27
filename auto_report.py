import requests
from lxml import etree
import json
import random
import time

from formdata_init import formdata_init

# 登录用到的一些URL
casurl = 'https://cas.gzhu.edu.cn/cas_server/login'
xnyqsb_int_url = 'http://yqtb.gzhu.edu.cn/infoplus/interface/start'
xnyqsburl = 'http://yqtb.gzhu.edu.cn/infoplus/form/XNYQSB/start'
renderurl = 'http://yqtb.gzhu.edu.cn/infoplus/interface/listNextStepsUsers'
render_int_url = 'http://yqtb.gzhu.edu.cn/infoplus/interface/render'
capurl = 'https://cas.gzhu.edu.cn/cas_server/captcha.jsp'


# 请求头，装成浏览器
requestheaders = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36'}



def get_captcha_code(session: requests.Session) -> str:
    ''' 获取验证码 '''
    code_image_bytes = session.get(capurl).content
    ##################################################
    '''
    你的验证码识别程序
    '''
    ##################################################
    return '0000'


def print_err(err: str) -> None:
    print(f'\033[1;31;40m{err}\033[0m')


def login(session: requests.Session, username: str, password: str) -> bool:
    ''' 进行登录操作，登录成功返回True，否则返回False '''
    print(f"--登录：用户名{{{username if username else 'null'}}}--")
    result_login = session.get(casurl)
    if not is_result_ok(result_login):
        return False
    login_html = etree.HTML(result_login.text)
    login_data = dict(zip(login_html.xpath("//div[@id='login']//input[@type!='reset']/@name"),
                          login_html.xpath("//div[@id='login']//input[@type!='reset']/@value")))
    login_data['username'] = username
    login_data['password'] = password
    login_data['captcha'] = get_captcha_code(session)
    result_main = session.post(casurl, login_data)
    if not is_result_ok(result_main):
        print_err(f'无法正确访问网页：{casurl}')
        return False
    error_div = etree.HTML(result_main.text).xpath("//div[@id='msg']/text()")
    if len(error_div) > 0:
        print_err(error_div[0])
        print_err(f'没有登录成功')
        return False
    main_html = etree.HTML(result_main.text)
    return True


def clock(session: requests.Session):
    ''' 进入打卡系统进行打卡 '''

    # 访问健康打卡加载页面，以获取Token
    result_xnqysb = session.get(xnyqsburl)
    if not is_result_ok(result_xnqysb):
        print_err(f'在访问{xnyqsburl}时发生错误，状态码为{result_xnqysb.status_code}')
        return False
    xnyqsb = etree.HTML(result_xnqysb.text)
    csrfToken = xnyqsb.xpath('//meta[@itemscope]/@content')[0]

    # 因为打卡是需要流水号的，需要获取流水号
    result_clock_form = session.post(xnyqsb_int_url, data={
                                     'idc': 'XNYQSB', 'release': '', 'csrfToken': csrfToken, 'lang': 'zh'})
    if not is_result_ok(result_clock_form):
        print_err(
            f'在访问{xnyqsb_int_url}时发生错误，状态码为{result_clock_form.status_code}')
        return False
    clock_form_url = result_clock_form.json()['entities'][0]
    print(f'打卡网址:{clock_form_url}')
    stepId = clock_form_url.split('/')[-2]

    # 通过接口获取默认值（若从未打卡则将打卡失败）
    render_int_data = {'stepId': stepId, 'instanceId': '', 'admin': 'false', 'rand': str(
        random.random()*999), 'width': '1051', 'lang': 'zh', 'csrfToken': csrfToken}
    session.headers['Referer'] = clock_form_url
    renderpost = session.post(render_int_url, render_int_data)
    if not is_result_ok(renderpost):
        print_err(f'在访问{render_int_url}时发生错误，状态码为{renderpost.status_code}')
        return False
    render_json = renderpost.json()

    # 处理需要打卡
    tags = render_json['entities'][0]['app']['tags']
    instanceName = render_json['entities'][0]['step']['instanceName']
    data = render_json['entities'][0]['data']
    formdata = str(formdata_init(
        data, clock_form_url, tags, instanceName))
    boundFields = 'fieldSTQKzdjgmc,fieldSTQKjtcyglkssj,fieldCXXXsftjhb,fieldzgzjzdzjtdz,fieldJCDDqmsjtdd,fieldSHENGYC,fieldYQJLksjcsj,fieldSTQKjtcyzd,fieldJBXXjgsjtdz,fieldSTQKbrstzk,fieldSTQKfrtw,fieldSTQKjtcyqt,fieldCXXXjtfslc,fieldJBXXlxfs,fieldSTQKpcsj,fieldJKHDDzt,fieldYQJLsfjcqtbl,fieldYQJLzhycjcsj,fieldSTQKfl,fieldSTQKhxkn,fieldJBXXbz,fieldCXXXsfylk,fieldFLid,fieldjgs,fieldSTQKglfs,fieldCXXXsfjcgyshqzbl,fieldSTQKjtcyfx,fieldCXXXszsqsfyyshqzbl,fieldJCDDshi,fieldSTQKrytsqkqsm,fieldJCDDs,fieldSTQKjtcyfs,fieldSTQKjtcyzljgmc,fieldSQSJ,fieldzgzjzdzs,fieldzgzjzdzq,fieldJBXXnj,fieldSTQKjtcyzdkssj,fieldSTQKfx,fieldSTQKfs,fieldYQJLjcdry,fieldCXXXjtfsdb,fieldCXXXcxzt,fieldYQJLjcddshi,fieldCXXXjtjtzz,fieldCXXXsftjhbs,fieldHQRQ,fieldSTQKjtcyqtms,fieldCXXXksjcsj,fieldSTQKzdkssj,fieldSTQKjtcyzysj,fieldjgshi,fieldSTQKjtcyxm,fieldJBXXsheng,fieldJBXXdrsfwc,fieldqjymsjtqk,fieldJBXXdw,fieldCXXXjcdr,fieldCXXXsftjhbjtdz,fieldJCDDq,fieldSTQKjtcyclfs,fieldSTQKxm,fieldCXXXjtgjbc,fieldSTQKjtcygldd,fieldzgzjzdzshi,fieldSTQKjtcyzdjgmcc,fieldSTQKzd,fieldSTQKqt,fieldCXXXlksj,fieldSTQKjtcyfrsj,fieldCXXXjtfsqtms,fieldSTQKjtcyzdmc,fieldCXXXjtfsfj,fieldJBXXfdy,fieldJBXXxm,fieldSTQKzljgmc,fieldCXXXzhycjcsj,fieldCXXXsftjhbq,fieldSTQKqtms,fieldYCFDY,fieldJBXXxb,fieldSTQKglkssj,fieldCXXXjtfspc,fieldSTQKbrstzk1,fieldYCBJ,fieldCXXXssh,fieldSTQKzysj,fieldJBXXgh,fieldCNS,fieldCXXXfxxq,fieldSTQKclfs,fieldSTQKqtqksm,fieldCXXXqjymsxgqk,fieldYCBZ,fieldJBXXxnjzbgdz,fieldSTQKjtcyfl,fieldSTQKjtcyzdjgmc,fieldCXXXddsj,fieldSTQKfrsj,fieldSTQKgldd,fieldCXXXfxcfsj,fieldJBXXbj,fieldSTQKks,fieldJBXXcsny,fieldCXXXjtzzq,fieldJBXXJG,fieldCXXXdqszd,fieldCXXXjtzzs,fieldJBXXshi,fieldSTQKjtcyfrtw,fieldSTQKjtcystzk1,fieldCXXXjcdqk,fieldSTQKzdmc,fieldSTQKjtcyks,fieldSTQKjtcystzk,fieldCXXXjtfshc,fieldCXXXcqwdq,fieldSTQKjtcypcsj,fieldJBXXqu,fieldJBXXjgshi,fieldYQJLjcddq,fieldYQJLjcdryjkqk,fieldYQJLjcdds,fieldSTQKjtcyhxkn,fieldCXXXjtzz,fieldJBXXjgq,fieldCXXXjtfsqt,fieldJBXXjgs,fieldSTQKzdjgmcc,fieldJBXXqjtxxqk,fieldDQSJ,fieldSTQKjtcyglfs'
    postdata = {'stepId': stepId, 'actionId': 1, 'formData': formdata, 'timestamp': str(int(time.time())), 'rand': str(
        random.random()*999), 'csrfToken': csrfToken, 'lang': 'zh', 'boundFields': boundFields, 'nextUsers': '{}'}

    r = session.post(
        'http://yqtb.gzhu.edu.cn/infoplus/interface/doAction', postdata)
    if not is_result_ok(r):
        print("打卡最终阶段出现错误")
        return False
    return True


def is_result_ok(result: requests.Response):
    '''如果返回不是200，说明有错误'''
    if result.status_code != 200:
        print(result.text)
        return False
    return True


def sleeptime() -> float:
    '''
    睡眠时间
    为避免每次打卡时间都在同一个时间，加入随机时间模拟
    可能并没有什么用
    '''
    # return random.random()*120
    return 0


def runclock(username: str, password: str):
    session = requests.Session()
    session.headers = requestheaders
    print('================================')
    print(f'{time.asctime(time.localtime(time.time()))}启动打卡')

    time.sleep(sleeptime())

    print(f'{time.asctime(time.localtime(time.time()))}准备打卡')
    if login(session, username, password) and clock(session):
        print(f'{time.asctime(time.localtime(time.time()))}完成打卡')
    else:
        print_err(f'{time.asctime(time.localtime(time.time()))}打卡失败')
    print('================================')


defusername = ""
defpassword = ""

def main():
    isreaddef = False
    try:
        with open("config.json") as f:
            logins = json.load(f)['login']
    except:
        print_err('================================')
        print_err("读取配置文件出错，使用默认登录账户")
        print_err('================================')
        isreaddef = True

    if (isreaddef):
        runclock(defusername, defpassword)
    else:
        for user in logins:
            try:
                username = user['username']
                password = user['password']
            except:
                print("读取某个登录用户失败")
                continue
            runclock(username, password)


if __name__ == '__main__':
    main()