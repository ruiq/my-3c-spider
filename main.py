import requests
from bs4 import BeautifulSoup as bs4
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///data.db', echo=True)
Database= sessionmaker(bind=engine)
Base = declarative_base()


class SPO(Base):
    __tablename__ = 'SPO'
    id = Column('id', Integer, primary_key=True)
    S = Column('S', String)
    P = Column('P', String)
    O = Column('O', String)


class Subject(Base):
    __tablename__ = 'Subject'
    id = Column('id', Integer, primary_key=True)
    Subject = Column('S', String)


class Property(Base):
    __tablename__ = 'Property'
    id = Column('id', Integer, primary_key=True)
    Property = Column('S', String)
    Category = Column('P', String)


refPropertyName = "引用"
brandPropertyName = "品牌"
typePropertyName = "类型"
categoryPropertyName = "分类"
model_typePropertyValue = "型号"
param_typePropertyValue = "参数"

detail_url = "http://detail.zol.com.cn/1170/1169534/param.shtml"



def save_spo(s,p,o):
    db = Database()
    has_record = db.query(SPO).filter(SPO.S == s,SPO.P == p,SPO.O == o).first()
    if not has_record:
        print({"s":s,"p":p,"o":o})
        spo = SPO(S=s,P=p,O=o)
        db.add(spo)
        db.commit()


def get_soup_object_from_url(url):
    try:
        r = requests.get(url=url)
        soup = bs4(r.text, features="html.parser")
        return soup
    except:
        print("请求失败：" + url)
        return


def handle_detail_html(url):
    soup = get_soup_object_from_url(url)
    print("loading : "+url)
    if soup == None:
        return
    subjectObject = soup.find(class_='product-model__name')
    if subjectObject is None:
        return
    subject = subjectObject.text.replace('参数', '')
    if subject is None:
        return

    save_spo(subject,refPropertyName,url)
    save_spo(subject,typePropertyName,model_typePropertyValue)
    a_link = soup.find(class_='breadcrumb').find(class_='breadcrumb__manu')
    if a_link:
        texts = a_link['href'].strip('/').split('/')
        if len(texts) == 2:
            subject_cate = texts[0]
            subject_brand = texts[1]
            save_spo(subject, categoryPropertyName,subject_cate)
            save_spo(subject,brandPropertyName,subject_brand)

    tables = soup.findAll('table')
    for table in tables:
        trs = table.findAll('tr')
        for index in range(1,len(trs)):
            tr = trs[index]
            cate = trs[0].find('td').text
            th = tr.find('th')
            td = tr.find('td')
            if th and td:
                p = th.find('span').text
                o = td.find('span').text
                if cate:
                    save_spo(p,categoryPropertyName,cate)
                save_spo(p,typePropertyName,param_typePropertyValue)
                save_spo(subject,p,o)


def get_category_list():
    base_url = 'http://detail.zol.com.cn'
    url = 'http://detail.zol.com.cn/category/626.html'
    soup = get_soup_object_from_url(url)
    sidebar_2 = soup.find("div",class_='inner')
    if sidebar_2 is None:
        return []
    a_list = sidebar_2.findAll("a")
    a_list.pop()
    a_urls = []
    for a in a_list:
        a_urls.append(base_url + a['href'])
    return a_urls

def get_detal_url(category_url):
    print("category : " + category_url)
    base_url = 'http://detail.zol.com.cn'
    soup = get_soup_object_from_url(category_url)
    page_desc = soup.find('span', class_='small-page-active').text
    maxPage = int(page_desc.split('/')[1])
    detail_url_list = []
    for page in range(1,maxPage):
        page_url = category_url + (str(page) + ".html")
        detail_soup = get_soup_object_from_url(page_url)
        # print(detail_soup)
        pic_mode_box = detail_soup.find('div',class_='pic-mode-box')
        product_a_list = pic_mode_box.findAll('a',class_='comment-num')
        for aIndex in range(0,len(product_a_list)):
            a = product_a_list[aIndex]
            hrefs = a['href'].split('/')
            hrefs.pop()
            url = base_url + ('/'.join(hrefs)) + "/param.shtml"
            # param.shtml
            detail_url_list.append(url)
            # print(url)
    print(category_url)
    print("detail url count : %d",len(detail_url_list))
    return detail_url_list


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    # handle_detail_html('http://detail.zol.com.cn/1170/1169534/param.shtml')

    category_list = ["http://detail.zol.com.cn/memory/","http://detail.zol.com.cn/hard_drives/","http://detail.zol.com.cn/case/","http://detail.zol.com.cn/power/","http://detail.zol.com.cn/cooling_product/","http://detail.zol.com.cn/solid_state_drive/","http://detail.zol.com.cn/dvdrw/"]
    for cate in category_list:
        detail_urls = get_detal_url(cate)
        for detail_url in detail_urls:
            handle_detail_html(detail_url)

