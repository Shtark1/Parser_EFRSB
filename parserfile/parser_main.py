import os
import requests

from parserfile.function.parsers import web_parsing, html_parse, web_debtor_inn
from parserfile.function.workingfile import create_file, read_file
from bot.cfg.database import Database


db = Database("../bot/cfg/database.db")


def start_parser(file_id, file_name, chat_id, token_bot):
    try:
        list_fio = read_file(file_name)
        list_info = []
        list_info_2 = []
        os.remove(file_name)
        print(file_name)
        all_page_url_ay = web_parsing(list_fio)
        for idx, page_url_ay in enumerate(all_page_url_ay):
            if page_url_ay[0] != "Ошибка":
                # inn_ay, cro_ay_text, cro_ay_url, all_debtor_name, all_debtor_url = html_parse(page_url_ay)
                inn_ay, cro_ay_text, cro_ay_url, all_debtor = html_parse(page_url_ay)
                url_ay = page_url_ay[0]
                if all_debtor:
                    inn_debtor = web_debtor_inn(all_debtor)
                else:
                    inn_debtor = ["Нет"]
                try:
                    # list_info += [[list_fio[idx], url_ay, inn_ay, f"{cro_ay_text}\n\n{cro_ay_url}", all_debtor_name, "\n\n".join(all_debtor_url), "\n\n".join(inn_debtor)]]
                    print(inn_debtor)
                    for idx_s, inn_d in enumerate(inn_debtor):
                        if inn_d != "Нет":
                            list_info_2 += [[list_fio[idx], url_ay, inn_ay, f"{cro_ay_text}\n\n{cro_ay_url}", inn_d[1], inn_d[0], inn_d[2]]]
                        else:
                            list_info_2 += [[list_fio[idx], url_ay, inn_ay, f"{cro_ay_text}\n\n{cro_ay_url}", "Нет должников"]]

                except Exception as ex:
                    ...
        # print(list_info_2)
        create_file(list_info_2, file_name)

        with open(file_name, 'rb') as f:
            files = {'document': f}
            requests.post('https://api.telegram.org/bot{}/sendDocument'.format(token_bot), data={'chat_id': chat_id, 'caption': 'Результат парсинга'}, files=files)

        os.remove(file_name)
        db.done_file(file_id)
    except Exception as ex:
        print(ex)
        db.done_file(file_id)


if __name__ == '__main__':
    while True:
        files_names = db.get_all_file()
        for file_info in files_names:
            if file_info[2] == 0:
                file_id = file_info[0]
                file_name = f"excel/{file_info[1]}.xlsx"
                start_parser(file_id, file_name, file_info[1], db.get_all_config()[1])
