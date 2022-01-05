import json


class Languages:
    @staticmethod
    def get_message(name, lang, *args):
        if lang == "en":
            try:
                with open("resources/english.json", "r") as rfile:
                    data = json.load(rfile)
                    mes_list = dict(data)
            except FileNotFoundError:
                raise FileNotFoundError("Error with en")

        if lang == "ru":
            try:
                with open("resources/russian.json", "r", encoding='utf-8') as rfile:
                    data = json.load(rfile)
                    mes_list = dict(data)
            except FileNotFoundError:
                raise FileNotFoundError("Error with ru")

        if lang == "uk":
            try:
                with open("resources/ukrainian.json", "r", encoding='utf-8') as rfile:
                    data = json.load(rfile)
                    mes_list = dict(data)
            except FileNotFoundError:
                raise FileNotFoundError("Error with uk")

        if isinstance(mes_list[name], list):
            return mes_list[name]

        if mes_list[name].find('%') != -1:
            a1 = mes_list[name].split('%')
            a2 = a1[0] + args[0] + a1[1]
            return a2

        return mes_list[name]
