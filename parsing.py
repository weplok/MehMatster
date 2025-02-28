
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
    title = soup.find('div', class_='h3')
    # link_class = soup.find('li', class_='index-news-list__more')
    # # link = link_class.findAll('a')['href']
    # link = link_class.findAll('a')[0]['href']
    # link_title = link_class.findAll('a')[0].text
    #
    # title = all_student_news.find('div', class_='h3')
    filter_student_news = []
    for data in all_student_news:
        if data.find('li') is not None:
            filter_student_news.append(data.text)
    # filter_student_news.append(link)

    return ''.join(filter_student_news)


def teacher_info(teacher_name):
    headers = {
        "user": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    url = "https://sfedu.ru/www/stat_pages22.show?p=ELs/sotr/D&x=ELS/2000000000000"
    page = requests.get(url=url, headers=headers)

    soup = BeautifulSoup(page.text, "html.parser")
    all_student_workers = soup.findAll('div', class_='content_wrapper')
    filter_workers = []
    for data in all_student_workers:
        if data.find('tr') is not None:
            filter_workers.append(data.text)

    if teacher_name not in filter_workers:
        return 'Такого сотрудника нет'
    else:
        url = "https://sfedu.ru/www/stat_pages22.show?p=ELs/sotr/D&x=ELS/2000000000000"
        page = requests.get(url=url)

        soup = BeautifulSoup(page.text, "html.parser")
        all_student_workers = soup.findAll('div', class_='content_wrapper')
        filter_workers = []
        for data in all_student_workers:
            if data.find('tr') is not None:
                filter_workers.append(data.text)


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









