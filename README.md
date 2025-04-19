# python-selenium-automation-framework

# Framework details
This framework is based on the Page Object Model and uses pytest and a modified version of the pytest-html hook to display the test results including execution details and attached screenshot for each step. Test data is fetched from an excel workbook to simplify usage.

# Installation
To install in local open Git bash and clone the repo using

1. git clone https://github.com/raghavsood2007/python-selenium-automation-framework.git
2. create a virtual env locally.
3. Install the dependencies using 'requirements.txt'.

# Usage
## Setup run file
1. Open run.py
2. Specify the test file(s) to be run. If all the files in a folder are to be run just provide the path w.r.t root directory
2. Specify data excel to run the tests as in point 1.
3. Similarly specify the browser and reports directory
4. Debug mode helps to debug the script by raising an exception if it occurs during runtime. If set to 'False', an error is logged in the report and log file and execution continues.
5. Session variable is meant to run the script in a new or existing session.

#### To Run tests in new session
set `new_session = 'True'` or set `headless = 'True'`
#### To Run tests in exisiting session (for Edge)
a) Open command prompt. 
b) cd to the folder where browser executable is located (e.g. `cd C:\Program Files (x86)\Microsoft\Edge\Application`)
c) Then use command `msedge.exe --remote-debugging-port=8000 --user-data-dir=C:\Users\dumps disable extensions`
d) Set the same port number as above in run.py.


## Setup data workbook
1. Ensure that all the test files to be run have a associated sheet in the data workbook e.g. if test file to be run is named 'test_new' then workbook should have a sheet with the name 'test_new'.
2. List down the name of the tests in the test file under 'TestCaseRef' column in workbook.
3. To run a test case, mark its respective 'Run' column as TRUE.
4. Enter the respective number of iterations to be run for each test case. Default is 1.
5. Enter all the respective test data fields required in row 1 and their respective values for each test case.


## Setup test file
1. Define a class for the tests which inherits from BaseClass.
2. driver, testdata and all the required methoods are available in the BaseClass.
3. Define the steps for each test case taking a cue from the existing files.





