import pytest, os
from datetime import datetime

test_file = 'tests/Sample'
data_file = 'data/data_test.xlsx'
browser = 'Edge'
save_reports_to_dir = 'reports and ss'
debug_mode = 'True'
new_session = 'True'
port = '9223'
headless = 'False'













def get_output_directory():
    base_dir = os.path.join(os.getcwd(), save_reports_to_dir)
    if not os.path.exists(base_dir):
        os. makedirs (base_dir)
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S_%f")
    # timestamp = datetime.now().strftime("%d%m%Y_%I%M%p_%f")
    os.environ['run_details'] = timestamp
    output_dir = os.path.join(base_dir, f'Run_{timestamp}')
    os. makedirs(output_dir)
    return output_dir


report_dir = get_output_directory()
os. environ['report_directory'] = report_dir
os. environ['data_file_name'] = data_file
os. environ ['browser'] = browser.lower()
os. environ['debug_mode'] = debug_mode
os. environ['session'] = new_session
os. environ['port'] = port
os. environ['headless'] = 'headless'
report_file = os. path. join(report_dir, f'report - Run_{str(os.environ.get("run_details"))} .html')

def main():
    pytest_args = [test_file, '-s', '--html='+report_file, '--self-contained-html',]
    pytest.main(pytest_args)

if __name__=='__main__':
    main()