from login_page import LoginPage

def test_login_success(driver, credentials):
    dashboard = (
        LoginPage(driver)
        .open()
        .login(credentials["email"], credentials["password"])
    )
    assert dashboard.is_loaded()

def test_login_error(driver, credentials):
    login_page = (
        LoginPage(driver)
        .open()
        .login(credentials["email"], credentials["password"] + "_wrong")
    )
    # Проверяем, что текст ошибки содержит нужную фразу
    error_text = login_page.get_error()
    assert "Invalid Credentials" in error_text