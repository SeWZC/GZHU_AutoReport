import numpy as np
import requests
from PIL import Image
import io

capurl = 'https://cas.gzhu.edu.cn/cas_server/captcha.jsp'

captest = [((0, 0), 5), ((0, 8), 7), ((2, 3), 1), ((3, 3), 4),
           ((4, 2), 8), ((0, 6), 6), ((4, 5), 3), ((0, 1), 2), ((0, 2), 9)]

def get_captcha_code(session: requests.Session) -> str:
    '''
    获取验证码
    不推荐使用，识别率低，仅供测试使用
    判断验证码方式极为简单，不存在健壮性，也不可能用于其他地方
    '''
    image = Image.open(io.BytesIO(session.get(capurl).content))
    imgarr = np.array(image)
    imgarr = imgarr[:, :, 0]//3 + imgarr[:, :, 1]//3 + imgarr[:, :, 2]//3
    num_arrays = [imgarr[12:25, 13*i:(13*i+9)] for i in range(1, 5)]
    num = [0, 0, 0, 0]
    for i in range(4):
        for j in captest:
            if num_arrays[i][j[0][0]][j[0][1]] < 160:
                num[i] = j[1]
                break
    return ''.join(list(map(str, num)))
