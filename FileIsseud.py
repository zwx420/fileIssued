#!/usr/bin/python
# --*-- coding:utf-8 --*--

import settings
import os
import paramiko
import datetime


class Core(object):
    def file_path(self):
        """
        :return: 文件绝对路径
        """
        route_list = []  # 定义一个集合，接收输入的绝对路径的文件
        print "添加绝对路径的文件，结束添加输入'Q'"
        print "windows下请把'\\'替换为‘/’"
        while True:  # 循环输入
            values = raw_input(">>>").strip()
            if values == "Q":
                # print route_list
                return route_list
            elif os.path.exists(values):  # 判断输入的绝对路径的文件名是否存在
                route_list.append(values)  # 把输入的文件存入集合
            else:
                print "file does not exist!!!"

    def host_group(self):
        """
        :return: 所选主机组信息
        """
        print "序号", format("主机组名", "^24"), format("主机数量", "^18")  # 格式化输出主机组列表的列名
        for index, key in enumerate(settings.msg_dic):  # 遍历主机组配置文件的主机组
            print index + 1, format(key, "^26"), format(len(settings.msg_dic[key]), "^10")  # 格式化输出主机组信息
        while True:
            choose_host_list = raw_input("选择主机组>>>:").strip()  # 选择主机组
            host_dic = settings.msg_dic.get(choose_host_list)  # 得到所选的主机组中的所有主机信息，并存入host_dic
            if host_dic:
                # print host_dic
                return host_dic
            else:
                print "The host group does not exist!!!"

    def ssh_issued(self):
        """
        :param host_dic: 主机信息
        :param route_list: 主机信息
        :return:
        通过主机组信息和文件列表，下发文件到指定的目录，
            1，在这里对组机组的配置信息错误捕捉，并给予提示
            2，对在组中的所有主机的指定目录进行校验，捕捉错误信息，并给与提示
            3，对传入目录有无写入权限错误捕捉，并给予提示
        """
        host_dic = self.host_group()
        route_list = self.file_path()

        remote_dir = raw_input("传入路径>>>:").strip()  # 指定下发对象主机的存储目录，并去掉输入内容首尾多余字符
        for key in host_dic:  # 开始遍历指定主机组对象主机
            try:
                # global hostname  # 设置hostname变量为全局变量
                hostname = host_dic[key]["IP"]  # 获取对象主机IP
                username = host_dic[key]["username"]  # 获取对象主机用户
                port = host_dic[key]["port"]  # 获取ssh端口
                password = host_dic[key]["password"]  # 获得登录密码
                # key_path="/root/.ssh/id_rsa"#本地私钥路径
                # key=paramiko.RSAKey.from_private_key_file(key_path)#获得登录私钥
                ssh = paramiko.SSHClient()  # 获取连接ssh方法
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 允许连接不在know_hosts中的主机
                con = paramiko.Transport(hostname, port)  # 获取ip和端口
                con.connect(username=username, password=password)  # 登录目标主机
                sftp = paramiko.SFTPClient.from_transport(con)  # 获得SFTP连接

                path = con.open_sftp_client()
                try:
                    path.stat(remote_dir)  # 判断输入的传入目录是否正确
                    try:
                        print "*" * 30, hostname, "*" * 30
                        print '开始上传文件......%s' % datetime.datetime.now()  # 文件下发前打印时间
                        for f in route_list:
                            print f  # 打印遍历的当前文件名
                            list = f.split("/")  # 把route_list集合中的元素以/为分隔符拆分并存入list集合
                            sftp.put(f, remote_dir + "/" + list[-1])  # 下发文件，list[-1]是获取list集合的最后一个元素，也就是文件名
                        print '传输完成...... %s' % datetime.datetime.now()  # 文件下发完成后打印时间
                        print "*" * 76
                    except IOError:
                        print "ERROR: Directory does not have permissions!!!"
                except IOError:
                    print "ERROR: %s directory does not exist!!!" % hostname
                con.close()  # 下发完成，关闭sftp连接
            except Exception:
                print "ERROR: %s Host information configuration error!!!" % hostname
