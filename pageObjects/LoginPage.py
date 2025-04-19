from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from utilities.BaseClass import BaseClass

class LoginPage(BaseClass):

    usernameInputVar = (By.XPATH, '//input[@id="user-name"]')
    passwordInputVar = (By.XPATH, '//input[@id="password"]')
    loginButtonVar = (By.XPATH, '//input[@id="login-button"]')

    def usernameInput(self):
        return self.findByExplicitWait(locator=self.usernameInputVar, condition='visible')
    def passwordInput(self):
        return self.findByExplicitWait(locator=self.passwordInputVar, condition='visible')
    def loginButton(self):
        return self.findElement(locator=self.loginButtonVar)

    def login(self, username, password):
        self.interactWithElement(element=self.usernameInput(),
                                 action='send_keys',
                                 param=username,
                                 desc='Enter username')
        self.interactWithElement(element=self.passwordInput(),
                                 action='send_keys',
                                 param=password,
                                 desc='Enter password')
        self.interactWithElement(element=self.loginButton(),
                                 action='click',
                                 desc='Login button')