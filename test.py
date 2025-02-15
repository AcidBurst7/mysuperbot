# import requests

# params = {
#     'sl': 'ru',
#     'tl': 'en',
#     'text': 'Hello, World!',
#     'op': 'translate'
# }
# headers = {
#     'cache-control': 'max-age=0',
#     'upgrade-insecure-requests': '1',
#     'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
#     'sec-fetch-user': '?1',
#     # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#     'x-compress': 'null',
#     'sec-fetch-site': 'none',
#     'sec-fetch-mode': 'navigate',
#     'accept-encoding': 'deflate, br',
#     'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
# }
# url = 'https://translate.google.ru'
# textToTranslate = 'Привет'
# response = requests.get(url='http://translate.google.ru/translate_a/t?client=x&text={textToTranslate}&hl=en&sl=en&tl=ru', headers=headers)
# print(response._content)


# Создание пространства исходов для подбрасывания монеты
sample_space = {'Heads', 'Tails'}

# Вычисление вероятности выпадения орла
probability_heads = 1 / len(sample_space)
print(f'Probability of choosing is {probability_heads}')

# Определение условий событий
def is_heads_or_tails(outcome):
    return outcome in sample_space

def is_neither(outcome):
    return not is_heads_or_tails(outcome)

# Определение дополнительных условий событий
def is_heads(outcome):
    return outcome == 'Heads'

def is_tails(outcome):
    return outcome == 'Tails'

# Определение функции выявления события
def get_matching_event(event_condition, sample_space):
    return set([outcome for outcome in sample_space if event_condition(outcome)])
