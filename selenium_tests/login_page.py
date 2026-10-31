from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from base_page import BasePage
from dashboard_page import DashboardPage

class LoginPage(BasePage):
    URL = "https://phptravels.net/login"

    EMAIL = (By.ID, "email")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.XPATH, "//button[contains(., 'Sign In to your account')]")
    ERROR = (By.XPATH, "//*[contains(text(), 'Invalid Credentials')]")

    def open(self):
        self.driver.get(self.URL)
        self._handle_popup()
        return self

    def _handle_popup(self):
        modal = (By.ID, "demoWarningModal")
        try:
            self.find_visible(modal)
            btn = self.find_clickable((By.XPATH, "//div[@id='demoWarningModal']//button[contains(., 'I Understand')]"))
            btn.click()
            self.wait_for_invisibility(modal)
        except TimeoutException:
            pass

    def login(self, email, password):
        self.find_visible(self.EMAIL).clear()
        self.find_visible(self.EMAIL).send_keys(email)
        self.find_visible(self.PASSWORD).clear()
        self.find_visible(self.PASSWORD).send_keys(password)
        self.find_clickable(self.SUBMIT).click()

        # Ждем 5 секунд: либо появится ошибка, либо нас перекинет на другую страницу
        try:
            # Если ошибка появилась, возвращаем текущую страницу (LoginPage)
            self.wait.until(lambda d: "Invalid Credentials" in d.page_source or "dashboard" in d.current_url)
            if "Invalid Credentials" in self.driver.page_source:
                return self
        except TimeoutException:
            pass

        # Если ошибки нет, значит логин успешен
        return DashboardPage(self.driver)

    def get_error(self):
        return self.find_visible(self.ERROR).text