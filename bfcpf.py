import json
import itertools
import requests

DIGITS = "0123456789"

CPF_LENGTH_WITHOUT_PONCTUATION = 11
CPF_LENGTH_WITH_PONCTUATION = 14


class BFCPF:
    def is_character_valid(self, character: str) -> str:
        if character in DIGITS:
            return character

        if character == "X":
            return character

        return ""

    def sanitize_cpf(self, cpf: str) -> str:
        assert len(cpf) == CPF_LENGTH_WITH_PONCTUATION

        return "".join(filter(self.is_character_valid, cpf))

    def desanitize_cpf(self, cpf: str) -> str:
        assert len(cpf) == CPF_LENGTH_WITHOUT_PONCTUATION

        desanitized_cpf = f"{cpf[0:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"

        return desanitized_cpf

    def calculate_verification_digit(self, partial_cpf: str):
        weights = range(2, 10 + 1)[::-1]

        sum_ = sum(int(partial_cpf[i]) * weights[i] for i in range(len(weights)))
        resto = sum_ % 11

        if resto == 0 or resto == 1:
            return "0"

        return str(11 - resto)

    def is_cpf_valid(self, cpf: str) -> bool:
        if len(cpf) != 11:
            return False

        if cpf == cpf[0] * 11:
            return False

        digito1 = self.calculate_verification_digit(cpf[:9])

        if digito1 != cpf[9]:
            return False

        digito2 = self.calculate_verification_digit(cpf[1:10])

        if digito2 != cpf[10]:
            return False

        return True

    def find_missing_digits_indexes(self, partial_cpf: str) -> list[int]:
        missing_digits_indexes = []

        for i, character in enumerate(partial_cpf):
            if character == "X":
                missing_digits_indexes.append(i)

        return missing_digits_indexes
    
    def request_gov_api(self, valid_cpf: str) -> requests.Response:
        termo = valid_cpf
        pagina = 1
        tamanho_pagina = 10
        t = "5asIvv4b4YB453bWielC"
        token_captcha = "03AFcWeA66ZQaEZIugWYAuzKTlTVSKn6dYG9_l-N04V-iYm7jarvFFAb1ylZOUL-10fA-PSaB78fxtzearj-WjdgyseTgiJaNtPDbds4wGtFRnhPYCLHMPqigmGuIgNfceU4zsjy0fUO-w9S82nLTPeq217nVNfPicxSuKXe8SyX2hD1V3xd_AwJWAtjzZyBvS8ixlp_vzNYYFY3US-XV75UA9SoKRZ1fw_Dn09lIRPi6bs0lsC4OG9s2FThBQPBVRiKtH87SXR5Mx2xNBlfCPSpVdvS9W2r79xjXFfgPufufXwSaOo9zw1uePut9E1flMlHQ7xFKrvz1sdyjkWp3II7zSYQQY9GDcIp1H4OK86ptOF4TfF6X0wvEdvrjdShSGFUt3k0AbRvPq_ULhZIQgK1I7cRcggtZsFt5R3bkWwit4IptAKYNXyiU-m2V8JzB-GLVF1AUToJJ_bQkNE86bJEgk4yst4r0G4DN-zPfzsX5wdXaBI9MNBW-nEY5H4ZbmMlqDj1moLw9dOOLv8KBRx0jLMfA66oSShmxFVZR9oM2Pi19gX3JxXJ44AEMMRj1gS8MERqQqShdVW4iOwGCkspvq_Z1gFWvVJaEWjtOoYfGfKJCJo2jewbBPKTSWl-3rznY05f3cukPBIYRzjJMXLRMWY7j0wU-KudU4Wbv_OJNhzBIXvcfgpenyUs-Te6n7ZkPkxKXHb1WoqLmHVSxFSGI8K62hA9HxfGCWweL2pAMwSjCA9yYU7oIN8BZvQGh3SWnMx1O1lPekOuVCCHkaSudQPrkD2I7dcOFNBF-HjiuX_a3HUzLl0hUTUGs4QguUafqH6IQfngHOBNqzdTwJ0z_X9F1awLA64Ns9X10_-0Nbml3GuDgcxAmIwAQR4uug9gTi6n6yFHZ5tsBzM33ESgbnnv8MX9M3KA"
        
        url = f"https://portaldatransparencia.gov.br/pessoa-fisica/busca/resultado?termo={termo}&pagina={pagina}&tamanhoPagina={tamanho_pagina}&t={t}&tokenRecaptcha={token_captcha}"
        
        response = requests.get(url)
        
        return response
    
    def cpf_exists_on_gov_api(self, valid_cpf: str) -> bool:
        response = self.request_gov_api(valid_cpf)
        
        print(response)

    def brute_force(self, sanitized_cpf: str) -> str:
        valid_cpfs = []

        missing_digits_indexes = self.find_missing_digits_indexes(sanitized_cpf)
        total_missing_digits = len(missing_digits_indexes)

        possibilities = itertools.product(DIGITS, repeat=total_missing_digits)

        for possibility in possibilities:
            sanitized_cpf_list = list(sanitized_cpf)

            for i, missing_digit_index in enumerate(missing_digits_indexes):
                sanitized_cpf_list[missing_digit_index] = possibility[i]

            cpf = "".join(sanitized_cpf_list)

            if self.is_cpf_valid(cpf):
                valid_cpfs.append(cpf)

        # Implement request on GOV API
        
        for valid_cpf in valid_cpfs:
            cpf_exists_on_gov_api = self.cpf_exists_on_gov_api(valid_cpf)
            exit(1)

    def run(self, partial_cpf: str):
        sanitized_cpf = self.sanitize_cpf(partial_cpf)

        self.brute_force(sanitized_cpf)
