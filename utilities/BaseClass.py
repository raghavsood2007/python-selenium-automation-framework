from pathlib import Path

import pytest, logging, inspect, os, pyodbc, openpyxl, time, re
from dateutil import parser
from datetime import date, datetime, timedelta
from selenium.common import NoSuchElementException, TimeoutException, ElementNotVisibleException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains, Keys


@pytest.mark.usefixtures('setupDriver','testLevelSetup')
class BaseClass:
    @classmethod
    def set_driver(cls, driver): cls.driver=driver

    @classmethod
    def set_logger(cls, logger): cls.logger = logger

    @classmethod
    def set_ssLinks(cls, ssLinks): cls.ss_links = ssLinks

    @classmethod
    def set_testdata(cls, testdata): cls.testdata = testdata

    @classmethod
    def set_session(cls, session): cls.session = session

    debug_mode = os.environ.get('debug_mode')

    @staticmethod
    def fetchTestData(data_file, data_sheet, test_name, test_class=None):
        current_file = Path(__file__)
        base_path = current_file.parent.parent
        book_path = str(base_path / f'{os.environ.get("data_file_name")}')
        # print(book_path)
        sheet_name = data_sheet
        test_data_dict = {}

        # Load Workbook
        try:
            book = openpyxl.load_workbook(book_path, data_only=True)
        except FileNotFoundError:
            print('Error loading workbook')
            return None

        try:
            sheet = book[sheet_name]
        except KeyError:
            print(f'Error: The sheet {sheet_name} does not exist in the workbbok')
            return None

        if book and sheet:
            try:
                for i in range(1,sheet.max_row+1):
                    if sheet.cell(i,1).value==test_name:
                        for j in range(2,sheet.max_column+1):
                            cell_value = sheet.cell(i,j).value

                            if cell_value==True or cell_value==False:
                                test_data_dict[str(sheet.cell(1,j).value)] = cell_value
                            else:
                                cell_value = str(sheet.cell(i,j).value).replace(' 00:00:00','').strip()
                                if ',' in cell_value:
                                    cell_value = cell_value.replace('\n','').strip().split(',')
                                    cell_value = [entry.strip() for entry in cell_value]
                                    test_data_dict[str(sheet.cell(1, j).value)] = cell_value
                                else:
                                    test_data_dict[str(sheet.cell(1, j).value)] = cell_value
                return test_data_dict
            except Exception as e:
                raise(e)

    def logWithScreenshot(self, step_desc, status='Pass'):
        screenshot_name = f'screenshot_{datetime.now().strftime("%d%m%Y_%H%M%S_%f")}.png'
        screenshot_testcase_path = os.path.join(os.environ.get('report_directory'), self.logger.name)
        if not os.path.exists(screenshot_testcase_path):
            os.makedirs(screenshot_testcase_path)
        screenshot_path = os.path.join(screenshot_testcase_path, screenshot_name)
        self.driver.save_screenshot(screenshot_path)
        self.ss_links.append((screenshot_path, step_desc, status))
        if status=='Pass' or status:
            self.logger.info(step_desc)
        else:
            self.logger.error(step_desc)

    def findElement(self, locator, log=True, debug=debug_mode):
        try:
            return self.driver.find_element(*locator)
        except Exception as e:
            if debug == 'True': raise Exception(e)
            if log: self.logWithScreenshot(f'Element with locator {locator} not found.', status='Fail')
            return None



    def findElements(self, locator, log=True, debug=debug_mode):
        try:
            ele = self.driver.find_elements(*locator)
            if len(ele)==0: return None
            else: return(ele)
        except Exception as e:
            if debug == 'True': raise Exception(e)
            if log: self.logWithScreenshot(f'Element with locator {locator} not found.', status='Fail')
            return None


    def relativeFindElement(self, relative_to, locator, delay=0, multiple=False, log=True, debug=debug_mode):
        try:
            time.sleep(delay)
            if multiple: return relative_to.find_elements(*locator)
            else: return relative_to.find_element(*locator)
        except Exception as e:
            if debug == 'True': raise Exception(e)
            if log: self.logWithScreenshot(f'Element with locator {locator} relative to {relative_to} not found.', status='Fail')
            return None


    def findByExplicitWait(self, locator, condition='visible', timeout=10, frequency=1, log=True, debug=debug_mode):
        try:
            wait = WebDriverWait(driver=self.driver, timeout=timeout, poll_frequency=frequency, ignored_exceptions=[NoSuchElementException,ElementNotVisibleException])
            if condition=='visible':
                element = wait.until(EC.visibility_of_element_located(locator))
            elif condition == 'clickable':
                element = wait.until(EC.element_to_be_clickable(locator))
            elif condition=='present':
                element = wait.until(EC.presence_of_element_located(locator))
            elif condition == 'multiple_visible':
                element = wait.until(EC.presence_of_all_elements_located(locator))
            else:
                raise ValueError(f'Condition not supported: {condition}')
            return element
        except Exception as e:
            if debug == 'True': raise Exception(e)
            if log: self.logWithScreenshot(f'Element with locator {locator} not found.', status='Fail')
            return None

    def findElementByAccessibleName(self, tag, expected_name, timeout=10, log=True, debug=debug_mode):
        try:
            elements = self.findByExplicitWait((By.TAG_NAME, f'{tag}'), condition='multiple_visible', timeout=timeout)
            if len(elements)>0:
                for ele in elements:
                    if ele.accessible_name==expected_name:
                        return ele
                else: return None
            else: return None
        except Exception as e:
            if debug == 'True': raise Exception(e)
            if log: self.logWithScreenshot(f'Element with accessible name {expected_name} not found.', status='Fail')
            return None


    def scrollToElement(self, element):
        self.driver.execute_script(f'arguments[0].scrollIntoView(true)', element)


    def interactWithElement(self, element, action='click', param=None, desc='', scroll=False, delay=0, take_ss=True, extra_param=True, log=True, debug=debug_mode):

        if element:
            tag = element.tag_name
            action_chain = ActionChains(self.driver)
            if scroll: self.scrollToElement(element)
            try:
                if action=='click':
                    element.click()
                elif action=='click_via_js':
                    self.driver.execute_script("arguments[0].click();", element)

                elif action == 'send_keys':
                    if extra_param: element.click()
                    element.send_keys(param)
                    self.driver.execute_script(f"arguments[0].blur();",element)
                elif action == 'send_keys_with_delay':
                    if extra_param: element.click()
                    for char in param:
                        element.send_keys(char); time.sleep(0.05)
                elif action == 'clear_text':
                    element.clear()

                elif action == 'get_text':
                    return element.text.strip()
                elif action == 'get_text_via_js':
                    self.driver.execute_script(f"arguments[0].innerText;", element).strip()

                elif action == 'checkbox':
                    if param=='deselect' or param=='disable' or param=='uncheck':
                        if element.is_selected(): element.click()
                    else:
                        if not element.is_selected(): element.click()

                elif action == 'get_attribute':
                    return element.get_attribute(param)

                elif action=='hover':
                    action_chain.move_to_element(element).perform()
                elif action=='hover_via_js':
                    hover_script = """
                    var element = arguments[0];
                    var event = new MouseEvent('mouseover',{
                    bubbles: true,
                    cancelable: true,
                    view: window
                    });
                    element.dispatchEvent(event);
                    """
                    self.driver.execute_script(hover_script, element)

                elif action=='open_link_in_new_tab':
                    self.driver.execute_script("window.open(arguments[0], '_blank', 'width=800,height=600')", element.get_attribute('href'))

                elif action=='select_by_visible_text':
                    Select(element).select_by_visible_text(param)
                elif action=='select_ignore_case':
                    for opt in Select(element).options:
                        if opt.text.strip().lower()==param.strip().lower(): opt.click(); break
                elif action=='select_by_index':
                    Select(element).select_by_index(param)

                elif action=='right_click':
                    action_chain.context_click(element).perform()

                time.sleep(delay)
                if take_ss:
                    self.logWithScreenshot(f'Performed action: {action} on element with Desc:{desc}, Param:{param}, Tag:{tag}')
                else:
                    self.logger.info(f'Performed action: {action} on element with Desc:{desc}, Param:{param}, Tag:{tag}')
                return True
            except Exception as e:
                if debug == 'True': raise Exception(e)
                if take_ss: self.logWithScreenshot(f' Error performing {action} on element {desc} with tag type {tag}.', status='Fail')
                return None

        else:
            if take_ss: self.logWithScreenshot(f'Element with desc {desc} for action {action} passed to interactWithElement method not found.',
                                           status='Fail')
            return None



    def switchToWindow(self, *titles, by=None, param=None, action=None, delay=0, log=False, debug=debug_mode):
        window_found=False
        try:
            windows = self.driver.window_handles
            if by=='index':
                self.driver.switch_to.window(windows[param])
                if action=='close': self.driver.close()
                else: self.driver.maximize_window()
                time.sleep(delay)
                window_found = True
            else:
                for win in windows:
                    self.driver.switch_to.window(win)
                    for title in titles:
                        if (title in self.driver.title) or re.search(title, self.driver.title):
                            self.driver.maximize_window()
                            if action=='close': self.driver.close()
                            time.sleep(delay)
                            window_found = True
                            break
                    if window_found: break
            if not window_found: self.logWithScreenshot(f'Window with title {titles} not found.', status='Fail')

        except Exception as e:
            if debug == 'True': raise Exception(e)
            if log: self.logWithScreenshot(f' Error running switchToWindow function with param {titles}.',
                                               status='Fail')
            return None



    def setPageZoom(self, zoom_percentage):
        self.driver.execute_script(f"document.body.style.zoom='{zoom_percentage}%'")

    def highlightElement(self, element, duration=1):
        self.scrollToElement(element)
        original_style = element.get_attribute('style')
        self.driver.execute_script("arguments[0].setAttribute('style',arguments[1]);", element, "background-color: yellow;")
        time.sleep(duration)
        self.driver.execute_script("arguments[0].setAttribute('style',arguments[1]);", element, original_style)


    def terminateTest(self, condition, desc):
        if condition:
            pytest.fail()
            self.logWithScreenshot(step_desc=desc, status='Fail')

    def getData(self, key, case=None):
        try:
            data = self.testdata[key]
            if data=='None': return None
            if case==None:
                return data
            else:
                if type(data)==str:
                    if case=='upper': return data.upper()
                    else: return data.lower()
                if type(data)==list:
                    if case == 'upper': return [val.upper() for val in data]
                    else: return [val.lower() for val in data]
        except Exception as e:
            error_log = f'Error: Test data with key {key} not found. Check self.testdata variable for the test case.'
            self.logger.error(error_log); print(error_log)
            return None









