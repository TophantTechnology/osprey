"""

PoC filename must be in format like `id_name.py`,
for example, vb_2017_0001_Dedecms_sql_injection.py

POC_NAME must be the same with the class name

"""
import utils


POC_NAME = 'BasePoc'


class BasePoc:
    poc_info = {
        'poc': {
            'Id': None,  # poc编号，命名规范为vb_2014_0001_*.py
            'vbid': None,  # vulbox id
            'Name': None,  # poc名称
            'Author': None,  # poc作者
            'Create_date': None,  # poc创建时间：如'2014-11-19'
        },

        # to be edited by you
        'vul': {
            'Product': None,  # 漏洞所在产品名称
            'Version': None,  # 产品的版本号
            'Type': None,  # 漏洞类型
            'Severity': None,  # Bug severity
            'Description': None,  # 漏洞介绍
            'DisclosureDate': None,  # poc公布时间：如'2014-11-19'
        }
    }

    # 用于开始检测前的初始化（target， mode， verbose）
    # 和检测结束后的结果保存（Error,Success,Ret）
    # 额外的输出信息以dict形式保存在Ret中
    # to be updated by verify or exploits
    scan_info = {
        'Target': '',  # 目标网站域名
        'TaskId': '',
        'Mode': 'verify',  # verify或exploit， 默认值为verify
        'Verbose': False,  # 是否打印详细信息，默认值为False
        'Error': '',  # 记录poc失败信息
        'Success': False,  # 是否执行成功，默认值为False表示poc执行不成功，若成功请更新该值为True
        'Ret': utils.tree()  # 记录额外的poc相关信息
    }
    # 用于测试脚本需要数据的存储
    #
    test_case = {
        'Need_fb': False,  # 是否需要上层数据或者测试数据不宜构建, False不进行测试
        'Vuln': [],        # 可通过此PoC进行验证的测试目标
        'Not_vuln': []     # 不能通过此PoC进行验证的测试目标
    }

    def __init__(self):
        pass

    def verify(self, first=False, *args, **kwargs):
        pass

    def exploit(self, first=False, *args, **kwargs):
        pass

    def run(self, first=False, fb=None, **kwargs):
        self.target = self.scan_info['Target']
        self.mode = self.scan_info['Mode']
        self.verbose = self.scan_info['Verbose']
        self.fb = fb

        if self.mode == 'verify':
            self.verify(first=first, **kwargs)
        elif self.mode == 'exploit':
            self.exploit(first=first, **kwargs)

    # call it to test POC
    def run_test(self):
        pass
