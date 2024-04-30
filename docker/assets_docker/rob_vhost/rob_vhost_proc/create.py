from __future__ import print_function, unicode_literals
from PyInquirer import prompt
from ipaddress import IPv4Address
import re
import os
import stat
from rich.console import Console
import subprocess
from jinja2 import Environment, FileSystemLoader
#import pwd
#import grp
import sys
import pprint


class Create:
    
    noSudo = False

    converted = ""    
    data = {}
    dataVH = {}
    jnEnvloader = None

    local_base_path = ''
    simulation = False

    modelsDir = '/etc/rob_vhost/templates'
    modelsDirDocker = '/etc/rob_vhost/templates_docker'
    baseWWWPath = "/var/www"
    logsPath = '/var/log/apache2'
    configPath = '/etc/apache2'
    ftpPassFile = '/etc/vsftpd/password'
    ftpUsersDir = '/etc/vsftpd/users'
    
    opensslCommand = '/usr/bin/openssl'
    apacheHostingUserId = 0
    apacheHostingGroupId = 0
    logUserId = 0
    logGroupId = 3
    apacheConfUserId = 0
    apacheConfGroupId = 0
    ftpConfUserId = 0
    ftpConfGroupId = 0

    servicesPath = ''
    hostingsPath = ''

    
    def __init__(self, data_conf, local_base_path):
        self.local_base_path = local_base_path
        self.apacheHostingUserId = data_conf["apache_hosting_usr_id"]
        self.apacheHostingGroupId = data_conf["apache_hosting_group_id"]
        self.logUserId = data_conf["log_usr_id"]
        self.logGroupId = data_conf["log_group_id"]
        self.apacheConfUserId = data_conf["log_usr_id"]
        self.apacheConfGroupId = data_conf["log_group_id"]
        self.ftpConfUserId = data_conf["ftp_usr_id"]
        self.ftpConfGroupId = data_conf["ftp_usr_id"]
        if data_conf["docker"] == True:
            self.modelsDir = self.modelsDirDocker
        self.console_rich = Console()
        if data_conf['simulation'] == True:
            self.simulation = True
            if data_conf["docker"] == True:
                self.modelsDir = '{}/src/local/rob_vhost/templates_docker'.format(local_base_path)
            else:
                self.modelsDir = '{}/src/local/rob_vhost/templates'.format(local_base_path)
            self.baseWWWPath = '{}/src/local/www'.format(local_base_path)
            self.logsPath = '{}/src/local/log/apache2'.format(local_base_path)
            self.configPath = '{}/src/local/apache2'.format(local_base_path)
            self.ftpPassFile = '{}/src/local/vsftpd/password'.format(local_base_path)
            self.ftpUsersDir = '{}/src/local/vsftpd/users'.format(local_base_path)

        self.servicesPath = '/'.join([self.baseWWWPath, 'services'])
        self.hostingsPath = '/'.join([self.baseWWWPath, 'hostings'])


    def confirm(self, value):
        question_local = [
            {
                'type': 'expand',
                'name': 'confirm_value',
                'message': 'Confirm {}'.format(value),
                'default': 'y',
                'choices': [
                    {
                        'key': 'y',
                        'name': 'Yes',
                        'value': 'yes'
                    },
                    {
                        'key': 'n',
                        'name': 'No',
                        'value': 'no'
                    },
                    {
                        'key': 'q',
                        'name': 'Quit',
                        'value': 'quit'
                    },
                ]
            }
        ]
        answer_local = prompt(question_local)
        return answer_local['confirm_value']           

    
    def question(self, varName, message, validation):
        defaultValue  = ''
        if varName in self.data:
            defaultValue = self.data[varName]

        question_local = [
            {
                'type': 'input',
                'name': 'tmp_name',
                'message': 'Enter {}:'.format(message),
                'default': defaultValue,
                'validate' : lambda value: validation(value),
            }
        ]
        while True:
            answer_local = prompt(question_local)
            confirm_answer = self.confirm('Confirm {} ->{}<- :'.format(message, answer_local['tmp_name']))
            if confirm_answer == 'yes':
                self.data[varName] = self.converted
                break  
            if confirm_answer == 'quit':
                quit()

        return answer_local['tmp_name']     

    
    def checkASCII(self, data):
        retVal = True
        self.converted = data.encode('ascii', 'ignore').decode('ascii')
        if len(self.converted) != len(data):
            retVal = "invalid char only ascii admitted"
        return retVal

    
    def checkSPACE(self, data):
        return True
        retVal = True
        noSpaces = data.replace(" ", "").replace("\t", "").replace("\n", "").replace("\r")
        if len(noSpaces) != len(data):
            retVal = "SPACE or TAB \n \r not admitted"
        return retVal


    def checkIPV4(self, address):
        retVal = True
        try:
            IPv4Address(address)
        except:
            retVal = "Invalid ip address"
        return retVal

    
    def validateVhCode(self, value):
        retVal = self.checkASCII(value)
        if retVal is True:
            retVal = self.checkSPACE(self.converted)
            if retVal is True:
                if re.match('^[0-9]+$', self.converted) is None:
                    retVal = 'Invalid char only numbers admitted'
            if retVal is True:
                if len(self.converted) != 3:
                    retVal = 'Length = 3'
        return retVal


    def validateVhHostname(self, value):
        retVal = self.checkASCII(value)
        if retVal is True:
            retVal = self.checkSPACE(self.converted)
            if retVal is True:
                if re.match('^[-+_a-zA-Z0-9\.]+$', self.converted) is None:
                    retVal = 'Invalid char only -+_a-zA-Z0-9. admitted'
        return retVal


    def validateVhIp(self, value):
        retVal = self.checkASCII(value)
        if retVal is True:
            retVal = self.checkSPACE(self.converted)
            if retVal is True:
                if self.converted != '*':
                    retVal = self.checkIPV4(self.converted)
                    if retVal is False:
                        retVal = "Insert valid IP or * for named virtualhosting"
        return retVal


    def validateVhFtpLogin(self, value):
        retVal = self.checkASCII(value)
        if retVal is True:
            retVal = self.checkSPACE(self.converted)
            if retVal is True:
                if re.match('^[a-zA-Z0-9\.]+$', self.converted) is None:
                    retVal = 'Invalid char only a-zA-Z0-9. admitted'
            if retVal is True:
                if len(self.converted) < 8:
                    retVal = 'Min length = 8'
        return retVal

    
    def validateVhFtpPassword(self, value):
        retVal = self.checkASCII(value)
        if retVal is True:
            retVal = self.checkSPACE(self.converted)
            if re.match('^[\(\)\[\]\@\#\!-+_a-zA-Z0-9\.]+$', self.converted) is None:
                retVal = 'Invalid char only ()[]@#!><-+_a-zA-Z0-9. admitted'
            if retVal is True:
                if len(self.converted) < 8:
                    retVal = 'Min length = 8'
        return retVal


    def reqVhCode(self):
        question_local = [
            {
                'type': 'input',
                'name': 'vh_code',
                'message': 'Enter vh code',
                'validate' : lambda value: self.validateVhCode(value)
            }
        ]
        answer_local = prompt(question_local)
        self.confirm('Virtual host code {}'.format(answer_local['vh_code']))
        pprint(answer_local)     
    
    
    def printValues(self):
        console_rich = self.console_rich
        console_rich.print(
            'Virtualhosting data:', style='bold bright_white')
        console_rich.print(
            'Code ->[bold bright_white]{}[/bold bright_white]<-'.format(self.data['vh_code']))
        console_rich.print(
            'Hostname ->[bold bright_white]{}[/bold bright_white]<-'.format(self.data['vh_hostname']))
        console_rich.print(
            'IP ->[bold bright_white]{}[/bold bright_white]<-'.format(self.data['vh_ip']))
        console_rich.print(
            'FTP login ->[bold bright_white]{}[/bold bright_white]<-'.format(self.data['vh_ftp_login']))
        console_rich.print(
            'FTP password ->[bold bright_white]{}[/bold bright_white]<-'.format(
                self.data['vh_ftp_password']))

    
    def genVHInfo(self):
        name = "{}-{}".format(self.data['vh_code'], self.data['vh_hostname'])
        self.dataVH = {
            'hostingDir': '/'.join([self.hostingsPath, name]),
            'hostingIndex': '/'.join([self.hostingsPath, name, 'index.html']),
            'configFile': '/'.join([self.configPath, 'sites-available', "{}.conf".format(name)]),
            'configLink': '/'.join([self.configPath, 'sites-enabled', "{}.conf".format(name)]),
            'logDir': '/'.join([self.logsPath, name]),
            'logFileError': '/'.join([self.logsPath, name, 'error.log']),
            'logFileAccess': '/'.join([self.logsPath, name, 'access.log']),
            'indexFile': '/'.join([self.hostingsPath, name, 'index.html']),
            'ftpUserFile': '/'.join([self.ftpUsersDir, self.data['vh_ftp_login']]),
        }
        for value in self.dataVH:
            self.data[value] = self.dataVH[value]


    # check non existence
    def checkVH(self):
        retVal = True
        self.genVHInfo()
        # print(self.dataVH)
        for value in self.dataVH:
            if os.path.exists(self.dataVH[value]):
                print("Found -> {}".format(self.dataVH[value]))
                retVal = False
        return retVal

    
    def makeVH(self):
        retVal = True
        try:
            if self.checkVH() == False:
                raise RuntimeError('Invalid check')

            apacheHostingUserUID = self.apacheHostingUserId 
            apacheHostingGroupGID = self.apacheHostingGroupId
            logUserUID = self.logUserId
            logGroupGID = self.logGroupId
            apacheConfUserUID = self.apacheConfUserId
            apacheConfGroupGID = self.apacheConfGroupId
            ftpConfUserUID = self.ftpConfUserId
            ftpConfGroupGID = self.ftpConfUserId
            
            # Start creation
            self.jnEnvloader = Environment(loader=FileSystemLoader(self.modelsDir))
            cfgTemplate = self.jnEnvloader.get_template('configmodel.jinja') 
            cfgData = cfgTemplate.render(self.data)
            indexTemplate = self.jnEnvloader.get_template('indexmodel.jinja') 
            indexData = indexTemplate.render(self.data)
            ftpUserTemplate = self.jnEnvloader.get_template('userftpmodel.jinja') 
            ftpUserData = ftpUserTemplate.render(self.data)

            print('creo le directory')
            os.mkdir(self.dataVH['hostingDir'])
            if self.simulation == False:
                os.chown(self.dataVH['hostingDir'], apacheHostingUserUID, apacheHostingGroupGID)
            
            os.mkdir(self.dataVH['logDir'])
            if self.simulation == False:
                os.chown(self.dataVH['logDir'], logUserUID, logGroupGID)

            print('scrivo i file vuoti')
            mode = 0o777 | stat.S_IRUSR
            os.mknod(self.dataVH['logFileError'], mode)
            if self.simulation == False:
                os.chown(self.dataVH['logFileError'], logUserUID, logGroupGID)
                os.chmod(
                    self.dataVH['logFileError'],
                    stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
                )

            os.mknod(self.dataVH['logFileAccess'], mode)
            if self.simulation == False:
                os.chown(self.dataVH['logFileAccess'], logUserUID, logGroupGID)
                os.chmod(
                    self.dataVH['logFileAccess'],
                    stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
                )

            print('scrivo i file dai template')
            with open(self.dataVH['configFile'], 'w') as f:
                f.write(cfgData)
                f.close()
                if self.simulation == False:
                    os.chown(self.dataVH['configFile'], apacheConfUserUID, apacheConfGroupGID)
                    os.chmod(
                        self.dataVH['configFile'],
                        stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
                    )

            with open(self.dataVH['indexFile'], 'w') as f:
                f.write(indexData)
                f.close()
                if self.simulation == False:
                    os.chown(self.dataVH['indexFile'], apacheHostingUserUID, apacheHostingGroupGID)
                    os.chmod(
                        self.dataVH['indexFile'],
                        stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
                    )
                
            with open(self.dataVH['ftpUserFile'], 'w') as f:
                f.write(ftpUserData)
                f.close()
                if self.simulation == False:
                    os.chown(self.dataVH['ftpUserFile'], ftpConfUserUID, ftpConfGroupGID)
                    os.chmod(
                        self.dataVH['ftpUserFile'],
                        stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
                    )

            print('creo utente ftp')
            result = subprocess.run([
                    self.opensslCommand, 
                    'passwd', 
                    '-1', 
                    self.data['vh_ftp_password']
                ],
                stdout=subprocess.PIPE
            )
            passValue = result.stdout.decode('utf-8')
            with open(self.ftpPassFile, 'a') as f:
                f.write("\n{}:{}".format(self.data['vh_ftp_login'], passValue))
                f.close()
                if self.simulation == False:
                    os.chown(self.ftpPassFile, ftpConfUserUID, ftpConfGroupGID)
                    os.chmod(
                        self.ftpPassFile,
                        stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
                    )

        except Exception as e:
            print(e)
            retVal = False

        return retVal


    def checkSudo(self):
        retVal = True
        #try:
        #    if self.noSudo == False:
        #        mode = 0o777 | stat.S_IRUSR
        #        os.mknod('/root/xxassmemeienWWW', mode)
        #        os.remove('/root/xxassmemeienWWW')
        #    
        #except Exception:
        #    print("You need to be root or sudo user !")
        #    retVal = False
        
        return retVal


    def run(self):
        print("START")
        if self.checkSudo():
            doVH = False
            while True:
                self.question('vh_code', 'virtualhosting code', self.validateVhCode)
                self.question('vh_hostname', 'virtualhosting hostname', self.validateVhHostname)
                self.question('vh_ip', 'virtualhosting ip or *', self.validateVhIp)
                self.question('vh_ftp_login', 'virtualhosting ftp login', self.validateVhFtpLogin)
                self.question('vh_ftp_password', 'virtualhosting ftp password', self.validateVhFtpPassword)
                self.printValues()
                if self.checkVH():
                    confirm_answer = self.confirm("All values")
                    if confirm_answer == 'yes':
                        doVH = True
                        break
                else:
                    print("Already exists !")
            if doVH == True:
                print('Virtualhosting build begin')
                print(self.makeVH())
                print('Virtualhosting build end')
                print('RICORDARSI DI ESEGUIRE a2ensite O DI FARE IL LINK IN docker')
        print("END")
        sys.exit(0)
