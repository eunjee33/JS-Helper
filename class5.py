import subprocess
import os
from colorama import Fore, Style, init
import argparse

init(autoreset=True)


class DataLeaker:
    def __init__(self, secretFinder_path="lib/secretFinder.py", personal_info_file="personals.txt", credential_file="creds.txt", key_file="keys.txt",function_file="funcs.txt"):
        self.secretFinder_path = secretFinder_path
        self.personal_info_file = personal_info_file
        self.credential_file = credential_file
        self.key_file = key_file
        self.function_file = function_file

        self.keywords = {
            "personal_info": ["personal_RRN", "personal_phone_num", "personal_email", "personal_name", "personal_account_num", "personal_card_num", "personal_address", "personal_address2"],
            "credential": ["authorization_basic", "authorization_bearer", "authorization_api", "possible_Creds"],
            "key": ["google_api", "firebase", "google_captcah", "google_oauth", "amazon_aws_access_key_id", "amazon_mws_auth_token", "facebook_access_token", "mailgun_api_key", "twilio_api_key",
                    "twilio_account_sid", "twilio_app_sid", "paypal_braintree_access_token", "square_oauth_secret", "square_access_token", "stripe_standard_api", "stripe_restricted_api",
                    "github_access_token", "rsa_private_key", "ssh_dsa_private_key", "ssh_dc_private_key", "pgp_private_block", "json_web_token", "slack_token", "SSH_privKey", "Herok_api_key"],
            "function": ['fileDownload', 'fileUpload', 'inputEscape', 'encrypt']
        }


    """전체 프로세스 실행"""
    def run(self, js_file):
        print(f"{Fore.BLUE}[*] Start Leak Data from {js_file}")
        output = self.execute_secretFinder(js_file)
        personal_infos, credentials, keys, functions = self.parse_output(output)
        
        self.save_to_txt(personal_infos, output_file=self.personal_info_file)
        self.save_to_txt(credentials, output_file=self.credential_file)
        self.save_to_txt(keys, output_file=self.key_file)
        self.save_to_txt(functions, output_file=self.function_file)


    """secretFinder tool 실행"""
    def execute_secretFinder(self, js_file):
        try:
            command = ["python", self.secretFinder_path, "-i", js_file, "-o", "cli"]
            output = subprocess.run(command, capture_output=True, text=True, check=True)
            return output
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[!] Error executing secretFinder.py: {e}")
        except Exception as e:
            print(f"{Fore.RED}[!] Unexpected error: {e}")


    def parse_output(self, output):
        personal_infos, credentials, keys, functions = [], [], [], []
        for line in output.stdout.splitlines():
            data_type = self.categorize_data(line)

            if data_type == "personal_info":
                personal_infos.append(line)
                print(f" - Find {data_type} :\t {Fore.CYAN}{line}{Style.RESET_ALL}")
            elif data_type == "credential":
                credentials.append(line)
                print(f" - Find {data_type} :\t {Fore.CYAN}{line}{Style.RESET_ALL}")
            elif data_type == "key":
                keys.append(line)
                print(f" - Find {data_type} :\t\t {Fore.CYAN}{line}{Style.RESET_ALL}")
            elif data_type == "function":
                functions.append(line)
                print(f" - Find {data_type} :\t {Fore.CYAN}{line}{Style.RESET_ALL}")
        
        return personal_infos, credentials, keys, functions


    def categorize_data(self, line):     
        for data_type, keywords in self.keywords.items():
            if any(keyword in line.lower() for keyword in keywords):
                return data_type


    """결과를 file(.txt)로 저장"""
    def save_to_txt(self, results, output_file="test.txt"):
        try:
            with open(output_file, "a") as f:
                for result in results:
                    f.write(result + "\n")
            print(f"{Fore.GREEN}[*] Successfully appended to {output_file}")

        except Exception as e:
            print(f"{Fore.RED}[!] Unexpected error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Leak Sensitive Information from Javascript file")
    parser.add_argument("-f", "--file", help="js_file")
    args = parser.parse_args()

    if not args.file:
        print(f"{Fore.YELLOW}Usage: python script.py -f <file>")
        
    else:
        data_leaker = DataLeaker()
        js_file = args.file
        data_leaker.run(js_file)
