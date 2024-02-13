import os
import time
import pytest

from bs4 import BeautifulSoup

from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from pages import HomePage, ContactsPage, TenzorPage, DownloadPage




# настроим chrome
# 1. Путь сохранения - папка с тестом
# 2. Убираем все всплывающие окна
@pytest.fixture
def driver():
    project_path = os.path.dirname(os.path.abspath(__file__))
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": project_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    options.add_argument("--disable-notifications")
    return webdriver.Chrome(options=options)


def get_contact_page(driver):
    driver.maximize_window()
    home_page = HomePage(driver)
    home_page.open()
    time.sleep(2)
    home_page.click()


# Первый сценарий:

# Открывается раздел контакты
def test_home_page_successful(driver):
    home_page = HomePage(driver)
    get_contact_page(driver)
    home_page.click()
    if home_page.is_next_page_open():
        print("Перешло на https://sbis.ru/contacts/")
    assert home_page.is_next_page_open()

# Проверить, что есть блок "Сила в людях"
def test_contacts_page_successful(driver):
    result = ""
    home_page = HomePage(driver)
    home_page.open()
    home_page.click()
    contacts_page = ContactsPage(driver)
    contacts_page.click()

    time.sleep(2)
    print(driver.current_url)

    all_tabs = driver.window_handles

    new_tab = all_tabs[-1]
    driver.switch_to.window(new_tab)


    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # параграф с текстом "Сила в людях"
    paragraphs = soup.find_all('p', class_='tensor_ru-Index__card-title tensor_ru-pb-16')

    for paragraph in paragraphs:
        if "Сила в людях" in paragraph.text:
            result = "содержит текст 'Сила в людях'"
            break
        else:
            result = "не содержит текст 'Сила в людях'"

    time.sleep(2)
    assert result == "содержит текст 'Сила в людях'"


def get_tenzor_about_page(driver):
    home_page = HomePage(driver)
    driver.maximize_window()
    home_page.open()
    home_page.click()
    contacts_page = ContactsPage(driver)
    contacts_page.click()
    all_tabs = driver.window_handles

    new_tab = all_tabs[-1]
    driver.switch_to.window(new_tab)


# Убедиться что открывается https://tensor.ru/about
def test_tenzor_page_successful_redirect(driver):
    tenzor_page = TenzorPage(driver)
    get_tenzor_about_page(driver)
    time.sleep(5)
    tenzor_page.click()

    assert tenzor_page.is_redirect_url()

# Находим раздел Работаем и проверяем, что у всех фотографии
# хронологии одинаковые высота (height) и ширина (width)
def test_tenzor_page_imgs_sizes(driver):
    get_tenzor_about_page(driver)
    tenzor_page = TenzorPage(driver)
    time.sleep(5)
    tenzor_page.click()
    about_soup = BeautifulSoup(driver.page_source, 'html.parser')
    all_imgs = about_soup.find_all('a', img_='tensor_ru-About__block3-image new_lazy loaded')[:5]

    width = 0
    height = 0

    dimensions_equal = True
    previous_width = None
    previous_height = None

    for img in all_imgs:
        width = int(img.get('width', 0))
        height = int(img.get('height', 0))

        if previous_width is not None and previous_height is not None:
            if width != previous_width or height != previous_height:
                dimensions_equal = False
                break

        previous_width = width
        previous_height = height

    assert dimensions_equal

# Второй сценарий:

# Проверяем, что определился наш регион и есть список партнеров
def test_is_region_and_is_partners(driver):
    get_contact_page(driver)
    contact_page = ContactsPage(driver)

    assert contact_page.is_region_my_region and contact_page.is_partners

# Проверяем, что изменился регион и список партнеров на Камчатский край
def test_new_region_and_new_partners(driver):
    get_contact_page(driver)
    contact_page = ContactsPage(driver)
    contact_page.click_to_change_region()
    contact_page.click_to_kamchatskiy()
    time.sleep(5)
    assert contact_page.is_region_kamchatskiy() and contact_page.is_partners_kamchatskiy()


# Третий сценарий (необязательный)
def test_tenzor_plugin_size(driver):
    driver.maximize_window()
    home_page = HomePage(driver)
    home_page.open()
    # Element <a href="/download" class="sbisru-Footer__link">...</a> is not clickable at point (1057, 910). Other element would
    # receive the click: <div class="sbis_ru-container">...</div>
    # home_page.exec_script()
    # переходим по ссылке
    home_page.click_on_local_versions()
    # *в данной версии сайта нет Скачать СБИС, есть Скачать локальные версии

    download_page = DownloadPage(driver)
    download_page.click()
    # поставить свое время загрузки файла
    time.sleep(60)

    file_name = "sbis-setup-eo-inst.exe"
    project_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(project_path, file_name)
    file_size = os.path.getsize(file_path) / (1024 * 1024)
    expected_size = 3.58
    if os.path.exists(file_path):
        print("файл загружен")
    else:
        print("файл не загружен")

    assert os.path.exists(file_path) and abs(file_size - expected_size) < 0.1
