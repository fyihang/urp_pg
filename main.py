import requests
from bs4 import BeautifulSoup



class URPClient:
    def __init__(self, account, password):
        self.account = account
        self.password = password
        self.session = requests.session()
        
        
            #登录
    def login(self):
        import ddddocr
        import random
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
            "Referer": "http://192.168.16.207:9001/loginAction.do",
            "Origin": "http://192.168.16.207:9001",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        ocr = ddddocr.DdddOcr(show_ad=False)
        random_param = random.random()
        captcha_url = f"http://192.168.16.207:9001/validateCodeAction.do?random={random_param}"
        captcha_code = ocr.classification(self.session.get(captcha_url).content)
        data = {
            "zjh1": "",
            "tips": "",
            "lx": "",
            "evalue": "",
            "eflag": "",
            "fs": "",
            "dzslh": "",
            "zjh": self.account,
            "mm": self.password,
            "v_yzm": captcha_code
        }
        result = self.session.post("http://192.168.16.207:9001/loginAction.do", data=data, headers=header).text
        if '学分制综合教务' in result:
            print('登录成功')
            return True
        elif '您的密码不正确，请您重新输入！' in result:
            print('学号或者密码不正确，请您重新输入！')
            return False
        elif '你输入的验证码错误，请您重新输入！' in result:
            print('验证码识别错误，请重新运行！')
            return False


    # 获取评估列表并自动评估
    def get_and_evaluate_courses(self):
        evaluation_list_url = f"http://192.168.16.207:9001/jxpgXsAction.do?oper=listWj&yzxh={self.account}"
        headers = {
            'Host': '192.168.16.207:9001',
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '235',
            'Origin': 'http://192.168.16.207:9001',
            'Connection': 'keep-alive',
            'Referer': f'http://192.168.16.207:9001/jxpgXsAction.do?oper=listWj&yzxh={self.account}',
            'Upgrade-Insecure-Requests': '1',
            'Priority': 'u=4',
        }
        params = {
            'oper': 'listWj',
            'yzxh': self.account,
        }
        response_html = self.session.get(evaluation_list_url, params=params, headers=headers).text
        soup = BeautifulSoup(response_html, 'html.parser')
        # 找所有没评价的课程
        unevaluated_courses = []
        for tr in soup.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) >= 4 and tds[3].get_text(strip=True) == '否':
                # 找到未评教的课程
                img_tag = tr.find('img')
                if img_tag and 'name' in img_tag.attrs:
                    name_field = img_tag['name']
                    parts = name_field.split('#@')
                    if len(parts) >= 6:
                        questionnaire_id = parts[0]  # 问卷编码
                        evaluatee_id = parts[1]      # 被评人
                        evaluation_content = parts[5] # 评估内容
                        teacher_name = parts[2]
                        course_name = parts[4]
                        print(f"未评课程：{course_name}，教师：{teacher_name}")
                        entry = {
                            'questionnaire_id': questionnaire_id,
                            'evaluatee_id': evaluatee_id,
                            'evaluation_content': evaluation_content
                        }
                        unevaluated_courses.append(entry)
                        self.submit_evaluation(questionnaire_id, evaluatee_id, evaluation_content)
        if not unevaluated_courses:
            print('没有未评估的课程。')

    def submit_evaluation(self, questionnaire_id, evaluatee_id, evaluation_content):
        url = 'http://192.168.16.207:9001/jxpgXsAction.do'
        headers1 = {
            'Host': '192.168.16.207:9001',
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '235',
            'Origin': 'http://192.168.16.207:9001',
            'Connection': 'keep-alive',
            'Referer': f'http://192.168.16.207:9001/jxpgXsAction.do?oper=listWj&yzxh={self.account}',
            'Upgrade-Insecure-Requests': '1',
            'Priority': 'u=4',
        }
        data = {
            "wjbm": questionnaire_id,
            "bpr": evaluatee_id,
            "pgnr": evaluation_content,
            "oper": "wjShow"
        }
        self.session.post(url, data=data, headers=headers1)
        submit_url = 'http://192.168.16.207:9001/jxpgXsAction.do?oper=wjpg'
        headers2 = {
            'Host': '192.168.16.207:9001',
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'http://192.168.16.207:9001',
            'Connection': 'keep-alive',
            'Referer': 'http://192.168.16.207:9001/jxpgXsAction.do',
            'Upgrade-Insecure-Requests': '1',
            'Priority': 'u=4'
        }
        evaluation_data = {
            'wjbm': questionnaire_id,
            'bpr': evaluatee_id,
            'pgnr': evaluation_content,
            'xumanyzg': 'zg',
            'wjbz': '',
            '0000000005': '20_1',
            '0000000007': '0_0',
            '0000000008': '0_0',
            '0000000011': '0_0',
            '0000000012': '0_0',
            '0000000013': '0_0',
            '0000000018': '5_0.9',
            '0000000019': '0_0',
            '0000000014': '0_0',
            '0000000006': '20_1',
            '0000000002': '5_1',
            '0000000003': '10_1',
            '0000000017': '10_1',
            '0000000020': '20_1',
            '0000000015': '5_1',
            '0000000016': '5_0.7',
            'zgpj': ''
        }
        result = self.session.post(submit_url, data=evaluation_data, headers=headers2).text
        if "评估成功" in result:
            print('评估成功')
        else:
            print('评估失败')



if __name__ == '__main__':
    # 下方填学号
    account = ''
    # 下方填密码
    password = ''

    client = URPClient(account, password)
    if client.login():
        client.get_and_evaluate_courses()