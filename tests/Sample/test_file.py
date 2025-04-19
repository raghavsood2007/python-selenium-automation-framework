from selenium.webdriver import Keys

from utilities.BaseClass import BaseClass
from pageObjects.LoginPage import LoginPage

# Page Variables
loginPage = LoginPage()

class TestClassSample(BaseClass):
    def test_func1(self):
        print(self.testdata)
        self.driver.get('https://www.saucedemo.com/')
        self.setPageZoom(80)
        self.logWithScreenshot('Opened Secret Sauce website to test automation script')

        username = self.getData('username')
        password = self.getData('password')
        loginPage.login(username, password)


    def test_func2(self):
        print(self.testdata)
        self.driver.get('https://google.com/')
        self.setPageZoom(120)
        self.logWithScreenshot('Opened Google')
