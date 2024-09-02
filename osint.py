import time


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup


WEBDRIVER_PATH = "./chromedriver_win64/chromedriver.exe"


class OSINT:
    def __init__(self) -> None:
        chrome_options = Options()

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(
            service=ChromeService(WEBDRIVER_PATH),
            options=chrome_options,
        )
        
    def kill_webdriver(self) -> None:
        self.driver.quit()

    def _check_gov_transparency_portal(self, cpf: str) -> tuple[bool, str]:
        PAGE_LOAD_TIME = 2

        url = f"https://portaldatransparencia.gov.br/pessoa-fisica/busca/lista?termo={cpf}&pagina=1&tamanhoPagina=10"

        self.driver.get(url)
        time.sleep(PAGE_LOAD_TIME)

        html = self.driver.page_source
        html_parser = BeautifulSoup(html, "lxml")

        result_count = html_parser.find("strong", attrs={"id": "countResultados"})

        if result_count:
            result_name = html_parser.find("h3", class_="titulo-3")
            name = ""

            if result_name:
                name = result_name.text.title()

            return (result_count.text != "0", name)

        return (False, "")

    def check_cpf(self, cpf: str) -> list[tuple[str, str]]:
        found_on = []

        result_gov_transparency_portal = self._check_gov_transparency_portal(cpf)

        if result_gov_transparency_portal[0]:
            found_on.append(
                ("gov_transparency_portal", result_gov_transparency_portal[1])
            )

        return found_on


if __name__ == "__main__":
    osint = OSINT()
    results = osint.check_cpf("011.006.521-24")

    print(results)
