from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import logging


logging.basicConfig(level=logging.INFO)


class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.logger = logging.getLogger(__name__)


# sbis домашняя
class HomePage(BasePage):
    CONTACTS_LINK = (By.XPATH, '//*[@id="wasaby-content"]/div/div/div[2]/div[1]/div[1]/div[1]/div[2]/ul/li[2]')
    DOWNLOAD_LOCAL_VERSIONS_LINK = (By.CSS_SELECTOR,
                                    '#container > div.sbisru-Footer.sbisru-Footer__scheme--default > '
                                    'div.sbis_ru-container > div.sbisru-Footer__container > div:nth-child(3) > ul > '
                                    'li:nth-child(8) > a')
    OVERLAPPING_ELEMENT = (By.XPATH, '//*[@id="container"]/div[2]/div[1]')

    def open(self):
        self.driver.get('https://sbis.ru/')
        self.logger.info("Переход на домашнюю страницу ")

    def exec_script(self):

        over_element = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(self.OVERLAPPING_ELEMENT))
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);", over_element)

    def click(self):
        contacts_link = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(self.CONTACTS_LINK))
        contacts_link.click()
        self.logger.info("Переход на страницу с контактами ")

    def click_on_local_versions(self):

        action_chains = ActionChains(self.driver)
        local_versions_link = (WebDriverWait(self.driver, 20).
                               until(EC.element_to_be_clickable(self.DOWNLOAD_LOCAL_VERSIONS_LINK)))
        action_chains.move_to_element(local_versions_link).perform()
        try:
            local_versions_link.click()
            self.logger.info("Переход на страницу с загрузками ")
        except ElementClickInterceptedException as e:
            self.logger.error(f'Ошибка нахождения ссылки, вероятно закрыта другим элементом: {e}')
            self.driver.execute_script("arguments[0].click()", local_versions_link)

    def is_next_page_open(self):
        return 'contacts' in self.driver.current_url


# /contacts/
class ContactsPage(BasePage):
    TENZOR_IMG = (By.XPATH,
                  '//*[@id="contacts_clients"]/div[1]/div/div/div[2]/div/a')
    CHANGE_REGION_LINK = (By.XPATH, '//*[@id="container"]/div[1]/div/div[3]/div[2]/div['
                                    '1]/div/div[2]/span/span')
    CITIES_CONTAINER = (By.XPATH, '//*[@id="contacts_list"]')
    KAMCHATSKIY_LI = (By.XPATH, '//*[@id="popup"]/div[2]/div/div/div/div/div[2]/div/ul/li[43]/span/span')
    KAMCHATSKIY_PARTNERS_DIV = (By.XPATH, '//*[@id="contacts_list"]/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/div['
                                          '2]/div/div/div[1]/div[1]')

    def click(self):
        tenzor_img = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(self.TENZOR_IMG))
        tenzor_img.click()
        self.logger.info("tenzor_img нажат")

    def is_next_page_open(self):
        return 'https://tensor.ru/' in self.driver.current_url

    def is_region_my_region(self):
        return 'sverdlovskaya-oblast' in self.driver.current_url

    def is_partners(self):
        cities_container = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.CITIES_CONTAINER))
        return cities_container.text.strip() != ""

    def click_to_change_region(self):
        change_region_link = self.driver.find_element(By.XPATH, '//*[@id="container"]/div[1]/div/div[3]/div[2]/div['
                                                                '1]/div/div[2]/span/span')
        change_region_link.click()
        self.logger.info("Регион нажат")

    def click_to_kamchatskiy(self):
        # regions_xpath = '//*[@id="popup"]/div[2]/div/div/div/div/div[2]/div/ul'
        # regions = WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, regions_xpath)))

        try:
            # region_element = self.driver.find_element(By.XPATH, '//li[contains(text(), "41 Камчатский край")]')
            region_element = WebDriverWait(self.driver, 20).until(EC.visibility_of_element_located(self.KAMCHATSKIY_LI))
            region_element.click()
        except Exception as e:
            print("Ошибка при выборе региона: ", e)

    def is_region_kamchatskiy(self):
        change_region_link = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(self.CHANGE_REGION_LINK))
        return 'kamchatskij-kraj' in self.driver.current_url and "Камчатский край" in change_region_link.text

    def is_partners_kamchatskiy(self):
        partners_container = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.KAMCHATSKIY_PARTNERS_DIV))
        return partners_container.text == "СБИС - Камчатка"

        # for region in regions:
        #     if region_name in region.text:
        #         region.click()
        #         break
        #         return True
        #     else:
        #         return False


# tenzor.ru
class TenzorPage(BasePage):
    # ABOUT_LINK = (By.XPATH,
    #               '//*[@id="container"]/div[1]/div/div[5]/div/div/div[1]/div/p[4]/a')

    def click(self):
        action_chains = ActionChains(self.driver)
        # about_link = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(self.ABOUT_LINK))
        about_link = self.driver.find_element(By.XPATH, '//*[@id="container"]/div[1]/div/div[5]/div/div/div[1]/div/p['
                                                        '4]/a')
        action_chains.move_to_element(about_link).perform()
        try:
            about_link.click()
            self.logger.info("Переход на страницу Подробнее")
        except ElementClickInterceptedException as e:
            self.logger.error(f'Ошибка нахождения ссылки на Подробнее, вероятно закрыта другим элементом: {e}')
            self.driver.execute_script("arguments[0].click()", about_link)

    def is_redirect_url(self):
        return 'about' in self.driver.current_url


# tenzor.ru/downloads
class DownloadPage(BasePage):
    # DOWNLOAD_LINK = (By.XPATH,
    #                  '//*[@id="ws-7bz5p8p990h1707840393130"]/div[1]/div[2]/div[2]/div[1]/a')

    def click(self):
        action_chains = ActionChains(self.driver)
        download_link = self.driver.find_element(By.XPATH, '/html/body/div[1]/div[2]/div[1]/div/div['
                                                           '1]/div/div/div/div[2]/div/div[1]/div/div/div[2]/div['
                                                           '1]/div[2]/div[2]/div[1]/a')

        action_chains.move_to_element(download_link).perform()
        # download_link = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located(self.DOWNLOAD_LINK))

        try:
            download_link.click()
            self.logger.info("Скачиваем файл")
        except Exception as e:
            self.logger.error(f'Ошибка нажатия на ссылку с download=True, вероятно закрыта другим элементом: {e}')
            self.driver.execute_script("arguments[0].click()", download_link)
