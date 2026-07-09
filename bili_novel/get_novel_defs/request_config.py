import random

class config:
    # 获取UA
    def get_UA(self) -> list:
        UA_list = []
        with open("UA.txt", "r", encoding="utf-8") as f:
            for line in f:
                UA_list.append(line)

            return UA_list

    # 选择随机UA
    def random_choice_UA(self, UA_lst: list) -> str:
        UA = random.choice(UA_lst)

        return UA