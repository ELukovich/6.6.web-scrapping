import json

import requests

from bs4 import BeautifulSoup

from fake_headers import Headers

import unicodedata


# генертруем заголовки, чтобы "прикинуться" человеком
headers_gen = Headers(os="win", browser="chrome")
main_hh = requests.get('https://spb.hh.ru/search/vacancy?area=1&area=2&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&text=python',
                       headers=headers_gen.generate())


main_hh_html = main_hh.text
main_soup = BeautifulSoup(main_hh_html, 'lxml')

# залезаем на странички, вытаскиваем теги и информацию
vacancy_list = main_soup.find('div', id='a11y-main-content')
vacancy_tegs = vacancy_list.find_all('div', class_='vacancy-serp-item__layout')

parsed_data = []
for vacancy_teg in vacancy_tegs:
    vacancy_link_teg = vacancy_teg.find('a')
    salary_teg = vacancy_teg.find('span', class_='bloko-header-section-2')
    name_company_teg = vacancy_teg.find('div', class_='vacancy-serp-item__meta-info-company')
    city_teg = vacancy_teg.find(attrs={'data-qa': 'vacancy-serp__vacancy-address'})
    name_vacancy = vacancy_teg.find("a", class_="serp-item__title").text

    vacancy_link = vacancy_link_teg['href']
    name_company = unicodedata.normalize('NFKD', name_company_teg.text)
    city = city_teg.text

    vacancy_des_html = requests.get(vacancy_link, headers=headers_gen.generate()).text
    vacancy_des_soup = BeautifulSoup(vacancy_des_html, 'lxml')
    desctiption_teg = vacancy_des_soup.find('div', class_='g-user-content')
    desctiption = desctiption_teg.text
    salary_teg = vacancy_des_soup.find('span', class_='bloko-header-section-2 bloko-header-section-2_lite')
    salary = unicodedata.normalize('NFKD', salary_teg.text)

# проверка на 'Django' and 'Flask'
    if 'Django' and 'Flask' in desctiption:
# добавляем
        parsed_data.append(
            {
                "vacancy": name_vacancy,
                "salary": salary,
                "name_company": name_company,
                "city": city,
                "link": vacancy_link,
            }
        )

print(parsed_data)

# записываем в файл
with open('vacancies.json', 'w', encoding='utf-8') as file:
    json.dump(parsed_data, file, ensure_ascii=False, indent=4)
