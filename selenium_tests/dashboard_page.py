from base_page import BasePage

class DashboardPage(BasePage):
    def is_loaded(self):
        # Ждем, пока URL изменится на dashboard (или пока не пропадет login)
        try:
            self.wait.until(lambda driver: "dashboard" in driver.current_url)
            return True
        except Exception:
            return False