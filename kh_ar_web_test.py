import time
import sys
import getopt
from selenium.webdriver import Chrome, ie, Firefox
from selenium.webdriver.chrome.options import Options as Chrome_Options
from selenium.webdriver.firefox.options import Options as Firefox_Options
from selenium.webdriver.ie.options import Options as ie__Options

from selenium.common.exceptions import NoSuchElementException
from PIL import Image
from io import BytesIO
from online_verify import YDMHttp


dirver_list = ['Chrome', 'Firefox', 'ie']

# kh_username = 'admin'
# kh_password = '123456ar??'
# ydmh_username = 'wrydeveloper'
# ydmh_password = 'wry19950107'
# ydmh_appid = '9793'
# ydmh_appkey = 'd9f03ea2f792e551420f4b672565a478'
browser = ''
kh_username = ''
kh_password = ''
ydmh_username = ''
ydmh_password = ''
ydmh_appid = ''
ydmh_appkey = ''
filename = 'verify.png'
codetype = 1004
timeout = 60

class KH_AR_TEST:
    
    def __init__(self, login_url, browser, kh_username, kh_password, ydmh_username, ydmh_password, ydmh_appid, ydmh_appkey):
        self._login_url = login_url
        options = eval(browser + '_Options')()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        self._dirver = self._dirver_setup(browser, options)
        self._kh_username = kh_username
        self._kh_password = kh_password
        self._ydmh_username = ydmh_username
        self._ydmh_password = ydmh_password
        self._ydmh_appid = ydmh_appid
        self._ydmh_appkey = ydmh_appkey
        
    def _dirver_setup(self, browser, options):
        if browser in dirver_list:
            param = {str.lower(browser) + '_options': options}
            return eval(browser)(**param)
        else:
            return Chrome(chrome_options=options)
    
    def _clean_test(self):
        self._dirver.close()
        
    def kh_login(self):
        try:
            self._dirver.get(self._login_url)
            self._dirver.find_element_by_name('username').send_keys(self._kh_username)
            self._dirver.find_element_by_name('password').send_keys(self._kh_password)
            verfy_code_element = self._dirver.find_elements_by_class_name('captcha')[0]
            yundama = YDMHttp(self._ydmh_username, self._ydmh_password, self._ydmh_appid, self._ydmh_appkey)
            verify_code = self._verfy_code_recognizing(verfy_code_element, yundama)
            self._verification_code_right(verfy_code_element, yundama, verify_code, True)
            
            times = 0
            while self._dirver.current_url == self._login_url and times <= 10:
                time.sleep(1)
                times += 1
            
            if times > 10 and self._dirver.current_url == self._login_url:
                print('登录超过10s没有正常跳转, 登录失败!')
                sys.exit()
            print('登录成功')
            print(self._dirver.current_url)
        except Exception as e:
            print(e)
    
    def _verification_code_right(self, verfy_code_element, yundama, verify_code, last_verify_result=True):
        self._dirver.find_element_by_name('verify').clear()
        if last_verify_result == False:
            if verify_code == '':
                verfy_code_element.click()
            verify_code = self._verfy_code_recognizing(verfy_code_element, yundama)
        
        self._dirver.find_element_by_name('verify').send_keys(verify_code)
        self._dirver.find_elements_by_class_name('layui-btn')[0].click()
        try:
            time.sleep(0.2)
            msg_element = self._dirver.find_element(by='class name', value='layui-layer-content')
        except NoSuchElementException:
            print('无异常')
        else:
            msg = msg_element.get_attribute("innerHTML")
            if msg == '验证码不正确':
                time.sleep(2)
                self._verification_code_right(verfy_code_element, yundama, verify_code, False)
            elif msg == '用户名或密码错误':
                raise Exception(msg)
    
    def _verfy_code_recognizing(self, verfy_code_element, yundama):
        # 截图
        code_image = verfy_code_element.location
        image = self._dirver.get_screenshot_as_png()
        img = Image.open(BytesIO(image))
        code_png = img.crop((code_image['x'], code_image['y'], code_image['x'] + verfy_code_element.size['width'],
                             code_image['y'] + verfy_code_element.size['height']))
        code_png.save('verify.png')
        # 识别
        balance = yundama.balance()
        print(balance)
        if int(balance) > 10:
            cid, result = yundama.decode(filename, codetype, timeout)
        else:
            result = ''
            print('没钱了')
        return result
    
    
def main(argv):
    try:
        opts, _ = getopt.getopt(argv, "", ["browser=", "kh_username=", "kh_password=", "ydmh_username=", "ydmh_password=", "ydmh_appid=", "ydmh_appkey="])
        for opt, arg in opts:
            if opt in ("--browser"):
                if arg in dirver_list:
                    browser = arg
                    continue
                else:
                    print('No support type of browser')
                    sys.exit()
            
            if opt in ("--kh_username"):
                kh_username = arg
                continue
            
            if opt in ('--kh_password'):
                kh_password = arg
                continue
            
            if opt in ('--ydmh_username'):
                ydmh_username = arg
                continue
            
            if opt in ('--ydmh_password'):
                ydmh_password = arg
                continue
            
            if opt in ('--ydmh_appid'):
                ydmh_appid = arg
                continue
            
            if opt in ('--ydmh_appkey'):
                ydmh_appkey = arg
                continue
    except getopt.GetoptError:
        print('Error: kh_ar_web_test.py --browser=<browser-type> --kh_username=<kehai ar username> --kh_password=<kehai ar password> --ydmh_username=<ydmh username> --ydmh_password=<ydmh password>  --ydmh_appid=<ydmh appid>  --ydmh_appkey=<ydmh appkey>')

    url = 'https://flower-ar.poy.cn/admin/login/index.html'
    test = KH_AR_TEST(url, browser, kh_username, kh_password, ydmh_username, ydmh_password, ydmh_appid, ydmh_appkey)
    test.kh_login()
    
if __name__ == '__main__':
    main(sys.argv[1:])