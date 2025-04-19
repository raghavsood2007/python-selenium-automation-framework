import json
from pytest_html import extras
from selenium.webdriver import Edge, EdgeOptions, Chrome, EdgeService
from utilities.BaseClass import BaseClass
import pytest, logging, inspect, datetime, os, pyodbc, time, traceback, tempfile, requests
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.service import Service
from pathlib import Path

accessUtility = None
driver = None
ss_links = None
logger = None
testdata = None
data = None



# # Command line options. Below function is to choose the browser to run tests
def pytest_addoption (parser):
    parser.addoption('--browser_name', action='store', default='edge')

def get_dynamic_scope():
    if os.environ.get('session')!='False': scope='function'
    else: scope='session'
    return scope



@pytest.fixture(scope=get_dynamic_scope())
def setupDriver(request):
    # # Below declaration is to pass global driver object to screenshot method
    global driver

    browser_name = os.environ.get('browser')
    if browser_name=='edge':
        options = EdgeOptions()
        options.use_chromium = True
        service = EdgeService(EdgeChromiumDriverManager().install())
        if os.environ.get('headless')=='True': options.add_argument('--headless')
        if os.environ.get('session')=='False' and os.environ.get('headless')!='True':
            port = os.environ.get('port')
            debugger_url = f'http://localhost:{port}/json'
            response = requests.get(debugger_url)
            sessions = json.loads(response.text)
            for session in sessions:
                if session.get('type')=='page':
                    correct_debugger_url = session['webSocketDebuggerUrl']
                    print(f'connecting to {correct_debugger_url}')
                    break
            options.debugger_address = f'localhost:{port}'
            driver = Edge(service=service, options=options, keep_alive=True); print('connected')
        else:
            options.add_experimental_option('excludeSwitches',['disable-sync','enable-automation'])
            args = ['--disable-features=msEdgeSidebarV2', '--no-first-run', '--disable-restore-session-state',
                    '--no-default-browser-check', '--guest']
            for arg in args: options.add_argument(arg)
            driver = Edge(service=service, options=options)

    elif browser_name=='chrome':
        driver = Chrome()

    driver.maximize_window()
    BaseClass.set_driver(driver)
    BaseClass.set_session(os.environ.get('session'))
    yield driver
    if os.environ.get('session')=='True': driver.quit()


@pytest.fixture
def testLevelSetup(request):
    global ss_links, logger, test_data, data
    ss_links = []

    logger = logging.getLogger(request.node.name)
    run_details = 'Run_'+str(os.environ.get('run_details'))
    fileHandler = logging.FileHandler(f'{os.environ.get("report_directory")}\\LogFile - {run_details}.log', mode='a')
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    fileHandler.setFormatter(formatter)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fileHandler)

    BaseClass.set_logger(logger)
    BaseClass.set_ssLinks(ss_links)
    BaseClass.set_testdata(data[request.node.name])

    yield
    logger.info(('-'*30+logger.name+f' ends here{"-"*30}\n').upper())
    print(('\n'+logger.name+' ends here\n').upper())



# Collect and modify the tests to be executed
def pytest_collection_modifyitems(config, items):
    global data
    data = {}
    for item in items:
        # print(item, item.name, data.keys(), item.name in data.keys())
        if item.name in data.keys():
            raise ValueError('Duplicate test case name found in the collected test file(s)')
        else:
            test_class = item.parent.cls.__name__ if item.parent.cls else 'None'
            data[item.name] = BaseClass.fetchTestData(data_file=os.environ.get('data_file_name'),
                                                      data_sheet=os.path.splitext(item.fspath.basename)[0],
                                                      test_class=test_class,
                                                      test_name=item.name)
    tests_to_run = []
    for key in data.keys():
        try:
            if data[key]['Run']: tests_to_run.append(key)
        except:
            pass

    selected_items = []
    for item in items:
        if item.name in tests_to_run:
            num_iterations = data[item.name].get('Iterations',1)
            if num_iterations!='None': num_iterations = int(num_iterations)
            else: num_iterations=1
            for i in range(num_iterations):
                item.add_marker(pytest.mark.parametrize('iteration',[i]))
                selected_items.append(item)

    items[:] = selected_items



@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()

    if report.when == 'call':
        links_list=[]
        for i in range(len(ss_links)):
            if ss_links[i][2]=='Pass' or ss_links[i][2]==True:
                links_list.append(f'<a href="{ss_links[i][0]}" target="_blank" style="color:green; font-size:12px; font-style:italic;">Pass: {ss_links[i][1]}</a><br>')
            else:
                report.outcome='failed'
                links_list.append(f'<a href="{ss_links[i][0]}" target="_blank" style="color:red; font-size:12px; font-style:italic;">Fail: {ss_links[i][1]}</a><br>')
            html_links = "".join(links_list)
            if hasattr(report,'extra'):
                report.extras.append(extras.html(html_links))
            else:
                report.extras = [extras.html(html_links)]





