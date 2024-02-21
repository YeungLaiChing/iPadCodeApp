#Simple assignment
from selenium.webdriver import Chrome
driver = Chrome()
#Or use the context manager
from selenium.webdriver import Chrome
with Chrome() as driver:
    #your code inside this indent
    url ='https://www.google.com'
    driver.get(url)
    
    datas = driver.find_elements('div')
    for data in datas:
        print(data.text)
