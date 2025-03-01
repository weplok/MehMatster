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


#бакалавр три функции получение коммерцион мест бюджет мест и проход баллы
def bachalor_applicant_count_free_places(direction):
    url = "https://sfedu.ru/www/stat_pages22.show?p=ABT/N8206"
    page = requests.get(url=url)

    soup = BeautifulSoup(page.text, "html.parser")
    mim_dir_row = soup.find('tr', class_='row2')
    mim_dir_quantity = mim_dir_row.find('td', class_='column3 style10 n').text

    pmi_dir_row = soup.find('tr', class_='row3')
    pmi_dir_quantity = pmi_dir_row.find('td', class_='column3 style10 n').text

    fiit_dir_row = soup.find('tr', class_='row4')
    fiit_dir_quantity = fiit_dir_row.find('td', class_='column3 style10 n').text

    math_teach_dir_row = soup.find('tr', class_='row90')
    math_teach_dir_quantity = math_teach_dir_row.find('td', class_='column3 style12 n').text


    free_places = {
        'прикладная математика и информатика': pmi_dir_quantity,
        'фундаментальная информатика и информационные технологии': fiit_dir_quantity,
        "математика и механика": mim_dir_quantity,
        'педагогическое образование: математика': math_teach_dir_quantity,
    }

    return free_places[direction.lower()]



def bachalor_applicant_count_paid_places(direction):
    url = "https://sfedu.ru/www/stat_pages22.show?p=ABT/N8206"
    page = requests.get(url=url)

    soup = BeautifulSoup(page.text, "html.parser")
    mim_dir_row = soup.find('tr', class_='row2')
    mim_dir_quantity = mim_dir_row.find('td', class_='column7 style10 n').text

    pmi_dir_row = soup.find('tr', class_='row3')
    pmi_dir_quantity = pmi_dir_row.find('td', class_='column7 style10 n').text

    fiit_dir_row = soup.find('tr', class_='row4')
    fiit_dir_quantity = fiit_dir_row.find('td', class_='column7 style10 n').text

    math_teach_dir_row = soup.find('tr', class_='row90')
    math_teach_dir_quantity = math_teach_dir_row.find('td', class_='column7 style10 n').text



    paid_places = {
        'прикладная математика и информатика': pmi_dir_quantity,
        'фундаментальная информатика и информационные технологии': fiit_dir_quantity,
        "математика и механика": mim_dir_quantity,
        'педагогическое образование: математика': math_teach_dir_quantity,
    }

    return paid_places[direction.lower()]



def replace_br(el):
    if el.name == 'br':
        return '\n'
    else:
        return el.text

def bachalor_applicant_pass_balls(direction):
    url = "https://sfedu.ru/www/stat_pages22.show?p=ABT/N8206"
    page = requests.get(url=url)

    soup = BeautifulSoup(page.text, "html.parser")
    mim_dir_row = soup.find('tr', class_='row2')
    mim_dir_balls = mim_dir_row.find('td', class_='column8 style20 s')
    mim_dir_balls = ''.join(map(replace_br, mim_dir_balls))

    pmi_dir_row = soup.find('tr', class_='row3')
    pmi_dir_balls = pmi_dir_row.find('td', class_='column8 style20 s')
    pmi_dir_balls = ''.join(map(replace_br, pmi_dir_balls))

    fiit_dir_row = soup.find('tr', class_='row4')
    fiit_dir_balls = fiit_dir_row.find('td', class_='column8 style20 s')
    fiit_dir_balls = ''.join(map(replace_br, fiit_dir_balls))

    math_teach_dir_row = soup.find('tr', class_='row90')
    math_teach_dir_balls = math_teach_dir_row.find('td', class_='column8 style20 s')
    math_teach_dir_balls = ''.join(map(replace_br, math_teach_dir_balls))

    pass_balls = {
        'прикладная математика и информатика': pmi_dir_balls,
        'фундаментальная информатика и информационные технологии': fiit_dir_balls,
        "математика и механика": mim_dir_balls,
        'педагогическое образование: математика': math_teach_dir_balls,
    }

    return pass_balls[direction.lower()]




#магистратура три функции получение коммерцион мест бюджет мест и проход баллы
def master_applicant_count_free_places(direction):
    url = "https://sfedu.ru/www/stat_pages22.show?p=ABT/N8207/P"
    page = requests.get(url=url)

    soup = BeautifulSoup(page.text, "html.parser")
    fiit_dir_row = soup.find('tr', class_='row2')
    fiit_dir_quantity = fiit_dir_row.find('td', class_='column3 style9 n').text

    cm_dir_row = soup.find('tr', class_='row3')
    cm_dir_quantity = cm_dir_row.find('td', class_='column3 style9 n').text

    msd_dir_row = soup.find('tr', class_='row4')
    msd_dir_quantity = msd_dir_row.find('td', class_='column3 style9 n').text

    ii_dir_row = soup.find('tr', class_='row5')
    ii_dir_quantity = ii_dir_row.find('td', class_='column3 style9 n').text

    mitou_dir_row = soup.find('tr', class_='row6')
    mitou_dir_quantity = mitou_dir_row.find('td', class_='column3 style9 n').text

    rmp_dir_row = soup.find('tr', class_='row9')
    rmp_dir_quantity = rmp_dir_row.find('td', class_='column3 style9 n').text

    irpi_dir_row = soup.find('tr', class_='row10')
    irpi_dir_quantity = irpi_dir_row.find('td', class_='column3 style9 n').text

    mio_dir_row = soup.find('tr', class_='row124')
    mio_dir_quantity = mio_dir_row.find('td', class_='column3 style14 n').text



    free_places = {
        'фундаментальная математика, механика и математическое моделирование': fiit_dir_quantity,
        'computational modeling in technology and finance': cm_dir_quantity,
        "modern software development": msd_dir_quantity,
        "разработка мобильных приложений и компьютерных игр": rmp_dir_quantity,
        'искусственный интеллект: математические модели и прикладные решения': ii_dir_quantity,
        'модели и информационные технологии организационного управления': mitou_dir_quantity,
        'информатика, робототехника и прикладные исследования в области информационных технологий': irpi_dir_quantity,
        'математика и информатика в образовании': mio_dir_quantity

    }

    return free_places[direction.lower()]


print(master_applicant_count_free_places('математика и информатика в образовании'))


def master_applicant_count_paid_places(direction):
    url = "https://sfedu.ru/www/stat_pages22.show?p=ABT/N8207/P"
    page = requests.get(url=url)

    soup = BeautifulSoup(page.text, "html.parser")
    fiit_dir_row = soup.find('tr', class_='row2')
    fiit_dir_quantity = fiit_dir_row.find('td', class_='column5 style11 n').text

    cm_dir_row = soup.find('tr', class_='row3')
    cm_dir_quantity = cm_dir_row.find('td', class_='column5 style11 n').text

    msd_dir_row = soup.find('tr', class_='row4')
    msd_dir_quantity = msd_dir_row.find('td', class_='column5 style11 n').text

    ii_dir_row = soup.find('tr', class_='row5')
    ii_dir_quantity = ii_dir_row.find('td', class_='column5 style11 n').text

    mitou_dir_row = soup.find('tr', class_='row6')
    mitou_dir_quantity = mitou_dir_row.find('td', class_='column5 style11 n').text

    rmp_dir_row = soup.find('tr', class_='row9')
    rmp_dir_quantity = rmp_dir_row.find('td', class_='column5 style11 n').text

    irpi_dir_row = soup.find('tr', class_='row10')
    irpi_dir_quantity = irpi_dir_row.find('td', class_='column5 style11 n').text

    mio_dir_row = soup.find('tr', class_='row124')
    mio_dir_quantity = mio_dir_row.find('td', class_='column5 style11 n').text



    paid_places = {
        'фундаментальная математика, механика и математическое моделирование': fiit_dir_quantity,
        'computational modeling in technology and finance': cm_dir_quantity,
        "modern software development": msd_dir_quantity,
        "разработка мобильных приложений и компьютерных игр": rmp_dir_quantity,
        'искусственный интеллект: математические модели и прикладные решения': ii_dir_quantity,
        'модели и информационные технологии организационного управления': mitou_dir_quantity,
        'информатика, робототехника и прикладные исследования в области информационных технологий': irpi_dir_quantity,
        'математика и информатика в образовании': mio_dir_quantity

    }

    return paid_places[direction.lower()]



def master_applicant_pass_balls(direction):
    url = "https://sfedu.ru/www/stat_pages22.show?p=ABT/N8207/P"
    page = requests.get(url=url)

    soup = BeautifulSoup(page.text, "html.parser")

    fiit_dir_row = soup.find('tr', class_='row2')
    fiit_dir_balls = fiit_dir_row.find('td', class_='column6 style8 s').text

    cm_dir_row = soup.find('tr', class_='row3')
    cm_dir_balls = cm_dir_row.find('td', class_='column6 style8 s').text

    msd_dir_row = soup.find('tr', class_='row4')
    msd_dir_balls = msd_dir_row.find('td', class_='column6 style8 s').text

    mitou_dir_row = soup.find('tr', class_='row6')
    mitou_dir_balls = mitou_dir_row.find('td', class_='column6 style8 s').text

    rmp_dir_row = soup.find('tr', class_='row9')
    rmp_dir_balls = rmp_dir_row.find('td', class_='column6 style8 s').text

    ii_dir_row = soup.find('tr', class_='row5')
    ii_dir_balls = ii_dir_row.find('td', class_='column6 style8 s').text

    irpi_dir_row = soup.find('tr', class_='row10')
    irpi_dir_balls = irpi_dir_row.find('td', class_='column6 style8 s').text

    mio_dir_row = soup.find('tr', class_='row124')
    mio_dir_balls = mio_dir_row.find('td', class_='column6 style8 s').text


    pass_balls = {
        'фундаментальная математика, механика и математическое моделирование': fiit_dir_balls,
        'computational modeling in technology and finance': cm_dir_balls,
        "modern software development": msd_dir_balls,
        "разработка мобильных приложений и компьютерных игр": rmp_dir_balls,
        'искусственный интеллект: математические модели и прикладные решения': ii_dir_balls,
        'модели и информационные технологии организационного управления': mitou_dir_balls,
        'информатика, робототехника и прикладные исследования в области информационных технологий': irpi_dir_balls,
        'математика и информатика в образовании': mio_dir_balls

    }

    return pass_balls[direction.lower()]























