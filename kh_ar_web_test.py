import time
from selenium.webdriver import Chrome, ie, Firefox
from selenium.common.exceptions import NoSuchElementException
from PIL import Image
from io import BytesIO
from online_verify import YDMHttp


dirver_list = ['Chrome', 'Firefox', 'ie']

kh_username = 'admin'
kh_password = '123456ar??'
ydmh_username = 'wrydeveloper'
ydmh_password = 'wry19950107'
ydmh_appid = '9793'
ydmh_appkey = 'd9f03ea2f792e551420f4b672565a478'
filename = 'verify.png'
codetype = 1004
timeout = 60

class KH_AR_TEST:
    
    def __init__(self, login_url, browser):
        self._login_url = login_url
        self._dirver = self._dirver_setup(browser)
        
    def _dirver_setup(self, browser):
        if browser in dirver_list:
            return eval(browser)()
        else:
            return Chrome()
    
    def _clean_test(self):
        self._dirver.close()
        
    def kh_login(self):
        self._dirver.get(self._login_url)
        self._dirver.find_element_by_name('username').send_keys(kh_username)
        self._dirver.find_element_by_name('password').send_keys(kh_password)
        verfy_code_element = self._dirver.find_elements_by_class_name('captcha')[0]
        yundama = YDMHttp(ydmh_username, ydmh_password, ydmh_appid, ydmh_appkey)
        verify_code = self._verfy_code_recognizing(verfy_code_element, yundama)
        self._verification_code_right(verfy_code_element, yundama, verify_code, True)
        
        while self._dirver.current_url == self._login_url:
            time.sleep(1)
        
        print(self._dirver.current_url)
    
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
    
        
if __name__ == '__main__':
    url = 'https://flower-ar.poy.cn/admin/login/index.html'
    test = KH_AR_TEST(url, 'Chrome')
    test.kh_login()
