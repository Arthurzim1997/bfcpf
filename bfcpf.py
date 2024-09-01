import argparse
import itertools
import textwrap
import threading


DIGITS = "0123456789"

CPF_LENGTH_WITHOUT_PONCTUATION = 11
CPF_LENGTH_WITH_PONCTUATION = 14


def print_line():
    print("-" * 40)


class BFCPF:
    def __init__(self, args) -> None:
        self.args = args
        self.output = ""

        self.possibilities = self.discover_possibilities()
        self.threads = self.create_threads()

        self.valid_cpfs = []

    def create_threads(self) -> list[threading.Thread]:
        threads = []

        missing_digits_indexes = self.find_missing_digits_indexes(self.args.cpf)

        total_missing_digits = len(missing_digits_indexes)
        total_possibilities = len(DIGITS) ** total_missing_digits

        possibilities_per_thread = total_possibilities // self.args.threads

        if total_possibilities % self.args.threads != 0:
            self.args.threads += 1

        start_index = 0
        end_index = possibilities_per_thread - 1

        thread = threading.Thread(
            target=self.discover_valid_cpfs_of_thread, args=(start_index, end_index)
        )
        threads.append(thread)

        for _ in range(self.args.threads - 1):
            start_index += possibilities_per_thread
            end_index += possibilities_per_thread

            if end_index >= total_possibilities:
                end_index = total_possibilities - 1

            thread = threading.Thread(
                target=self.discover_valid_cpfs_of_thread, args=(start_index, end_index)
            )
            threads.append(thread)

        return threads

    def start_threads(self) -> None:
        for thread in self.threads:
            thread.start()

    def join_threads(self) -> None:
        for thread in self.threads:
            thread.join()

    def save_output_to_file(self) -> None:
        output_file_path = f"{self.args.cpf}.txt"

        with open(output_file_path, "w") as output_file:
            output_file.write(self.output)

    def print_output(self) -> None:
        print(self.output)

    def main_menu(self):
        with open("./interface/main_menu.txt", "r") as main_menu_file:
            print(main_menu_file.read())

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

    def discover_possibilities(self) -> itertools.product:
        sanitized_cpf = self.sanitize_cpf(self.args.cpf)

        missing_digits_indexes = self.find_missing_digits_indexes(sanitized_cpf)
        total_missing_digits = len(missing_digits_indexes)

        possibilities = itertools.product(DIGITS, repeat=total_missing_digits)
        possibilities = list(possibilities)

        return possibilities

    def discover_valid_cpfs_of_thread(self, start_index: int, end_index: int):
        sanitized_cpf = self.sanitize_cpf(self.args.cpf)

        missing_digits_indexes = self.find_missing_digits_indexes(sanitized_cpf)

        for i in range(start_index, end_index + 1):
            possibility = self.possibilities[i]

            sanitized_cpf_list = list(sanitized_cpf)

            for i, missing_digit_index in enumerate(missing_digits_indexes):
                sanitized_cpf_list[missing_digit_index] = possibility[i]

            cpf = "".join(sanitized_cpf_list)

            if self.is_cpf_valid(cpf):
                cpf = self.desanitize_cpf(cpf)

                self.valid_cpfs.append(cpf)

    def brute_force(self) -> str:
        self.start_threads()
        self.join_threads()

        self.output += "Valid CPFs found:\n\n"
        self.output += "\n".join(self.valid_cpfs)

    def run(self):
        self.main_menu()
        print_line()

        self.brute_force()

        if self.args.file == "yes":
            self.save_output_to_file()

        else:
            self.print_output()


def main():
    epilog = ""

    with open("./interface/epilog.txt", "r") as epilog_file:
        epilog = epilog_file.read()

    parser = argparse.ArgumentParser(
        description="CPF Brute Forcer by Gustavo Naldoni & André Zappa",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(epilog),
    )

    parser.add_argument("-c", "--cpf", required=True, help="partial CPF to attack")
    parser.add_argument(
        "-f", "--file", required=False, default="no", help="output as a file (yes/no)"
    )
    parser.add_argument(
        "-t",
        "--threads",
        required=False,
        default=10,
        type=int,
        help="number of threads",
    )

    args = parser.parse_args()

    bfcpf = BFCPF(args)
    bfcpf.run()


if __name__ == "__main__":
    main()
