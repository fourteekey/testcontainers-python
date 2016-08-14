from testcontainers_python.webdriver_container import WebDriverContainer
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import pytest


@pytest.fixture
def driver(request):
    container = WebDriverContainer().start()

    def fin():
        print ("teardown container")
        container.stop()

    request.addfinalizer(fin)
    return container.get_driver()


class TestDocker(object):
    @pytest.mark.parametrize("browser", [
        DesiredCapabilities.CHROME,
        DesiredCapabilities.FIREFOX,
    ])
    def test_selenium(self, browser):
        with WebDriverContainer(browser) as firefox:
            driver = firefox.get_driver()
            driver.get("http://google.com")
            driver.find_element_by_name("q").send_keys("Hello")

    def test_fixture(self, driver):
        driver.get("http://google.com")
        driver.find_element_by_name("q").send_keys("Hello")

    def test_fixture_2(self, driver):
        driver.get("http://google.com")
        driver.find_element_by_name("q").send_keys("Hello")