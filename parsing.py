import requests
from bs4 import BeautifulSoup


# парсим события для студента
def student_get_news():
    headers = {
        "user": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    url = "https://sfedu.ru/"
    page = requests.get(url=url, headers=headers)

    soup = BeautifulSoup(page.text, "html.parser")
    all_student_news = soup.findAll('div', class_='index-news-list__wrapper')
    # print(all_student_news)
    title = soup.find('div', class_='h3')
    link_class = soup.find('li', class_='index-news-list__more')
    link = link_class.findAll('a')[0]['href']
    filter_student_news = []
    for data in all_student_news:
        if data.find('li') is not None:
            # print(data.text)
            filter_student_news.append(data.text)
    # filter_student_news.append(link)
    filter_student_news = ''.join(filter_student_news)
    filter_student_news = filter_student_news.split('\n')
    res_student_news = []
    for new in filter_student_news:
        if new != '' and new != 'Больше новостей':
             res_student_news.append('👀 ->' + new + '\n\n')

    print(res_student_news)
    return ''.join(res_student_news)+'Чтобы узнать больше новостей, нажимай на Пресс-Центр ЮФУ 👆'


def student_get_news_mehmat():
    headers = {
        "user": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    url = "https://mmcs.sfedu.ru/"
    page = requests.get(url=url, headers=headers)

    soup = BeautifulSoup(page.text, "html.parser")
    news_cards = soup.findAll('div', class_='news_item_f')
    # print(news_cards)
    filter_news_cards = []
    for data in news_cards:
        # print(data)
        # print('------------')
        data_title = data.find('h2', class_='article_title')
        data_date = data.find('div', class_='newsitem_tools')
        data_main_info = data.find('div', class_='newsitem_text')
        if data_title is not None and data_date is not None and data_main_info is not None:
            filter_news_cards.append('📝' + (''.join(data_title.text.split('\n'))) + '\n' + '🕑' + ''.join(data_date.text.split('\n'))
                                     + '\n' + ''.join(data_main_info.text.split('\n')) + '\n\n\n')
    return "".join(filter_news_cards)


# функция возвращает количество бюджетных мест исходя из запроса пользователя
def applicant_count_free_places(direction):
    url = "https://sfedu.ru/www/stat_pages22.show?p=ABT/N8206"
    page = requests.get(url=url)

    soup = BeautifulSoup(page.text, "html.parser")
    mim_dir_row = soup.find('tr', class_='row2')
    mim_dir_quantity = mim_dir_row.find('td', class_='column3 style10 n').text

    pmi_dir_row = soup.find('tr', class_='row3')
    pmi_dir_quantity = pmi_dir_row.find('td', class_='column3 style10 n').text

    fiit_dir_row = soup.find('tr', class_='row4')
    fiit_dir_quantity = fiit_dir_row.find('td', class_='column3 style10 n').text

    moais_dir_row = soup.find('tr', class_='row7')
    moais_dir_quantity = moais_dir_row.find('td', class_='column3 style10 n').text

    pi_dir_row = soup.find('tr', class_='row19')
    pi_dir_quantity = pi_dir_row.find('td', class_='column3 style10 n').text

    ivt_dir_row = soup.find('tr', class_='row28')
    ivt_dir_quantity = ivt_dir_row.find('td', class_='column3 style10 n').text

    free_places = {
        'прикладная математика и информатика': pmi_dir_quantity,
        'фундаментальная информатика и информационные технологии': fiit_dir_quantity,
        'информатика и вычислительная техника': ivt_dir_quantity,
        "математика и механика": mim_dir_quantity,
        'математическое обеспечение и администрирование информационных систем': moais_dir_quantity,
        'прикладная информатика': pi_dir_quantity
    }

    return free_places[direction.lower()]



# функция возвращает количество платных мест исходя из запроса пользователя
def applicant_count_paid_places(direction):
    url = "https://sfedu.ru/www/stat_pages22.show?p=ABT/N8206"
    page = requests.get(url=url)

    soup = BeautifulSoup(page.text, "html.parser")
    mim_dir_row = soup.find('tr', class_='row2')
    mim_dir_quantity = mim_dir_row.find('td', class_='column7 style10 n').text

    pmi_dir_row = soup.find('tr', class_='row3')
    pmi_dir_quantity = pmi_dir_row.find('td', class_='column7 style10 n').text

    fiit_dir_row = soup.find('tr', class_='row4')
    fiit_dir_quantity = fiit_dir_row.find('td', class_='column7 style10 n').text

    moais_dir_row = soup.find('tr', class_='row7')
    moais_dir_quantity = moais_dir_row.find('td', class_='column7 style10 n').text

    pi_dir_row = soup.find('tr', class_='row19')
    pi_dir_quantity = pi_dir_row.find('td', class_='column7 style10 n').text

    ivt_dir_row = soup.find('tr', class_='row28')
    ivt_dir_quantity = ivt_dir_row.find('td', class_='column7 style10 n').text

    free_places = {
        'прикладная математика и информатика': pmi_dir_quantity,
        'фундаментальная информатика и информационные технологии': fiit_dir_quantity,
        'информатика и вычислительная техника': ivt_dir_quantity,
        "математика и механика": mim_dir_quantity,
        'математическое обеспечение и администрирование информационных систем': moais_dir_quantity,
        'прикладная информатика': pi_dir_quantity
    }

    return free_places[direction.lower()]









