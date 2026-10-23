from playwright.sync_api import Page


def test_sber_title(page: Page):
    # 1. Открываем главную страницу
    page.goto("https://sberbankins.ru")
    assert "Страхование" in page.title()

    # 2. Ловим новую вкладку в момент клика
    # Мы говорим роботу: "Внимание, сейчас при клике откроется новое окно, поймай его!"
    with page.context.expect_page() as new_page_info:
        page.get_by_role("link", name="Киберриски Каско").click()

    # 3. Переключаем управление роботом на новую вкладку
    new_page = new_page_info.value

    # 4. Ждем, пока новая вкладка полностью загрузится
    new_page.wait_for_load_state()

    # 5. Печатаем URL новой вкладки в консоль для проверки
    print("\nURL новой вкладки:", new_page.url)

    # 6. Делаем проверку уже ВНУТРИ НОВОЙ ВКЛАДКИ
    assert "kasko" in new_page.url
#i am writing this for a commit