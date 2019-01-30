from __future__ import unicode_literals
from main import *
from payloadextras import *
from startmetasploit import *
from generatepayload import *
from preparepayload import *
from stager import *
from help import *
import glob

GetIP = InterfaceSelecta()


def returnIP():
    return GetIP.ChooseInterface()['addr']

def returnINTER():
    return str(GetIP.ChooseInterface()['interface'])

def doInterfaceSelect():
    GetIP.ChooseInterface(set=True)
    return "clear"

def menuRaise():
    if killAllClients():
        raise KeyboardInterrupt

def noColourLen(colourString):
    return len(re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]').sub('', colourString))

def noColourCenter(colourString):
    len = (t.width / 2) - (noColourLen(colourString) /2 )
    if len % 2 > 0:
        len -= 1
    return (' ' * len) + colourString

def cleanUpPayloads():
    payloadsRemoved = 0
    for i in glob.glob(payloaddir() + "/*.exe"):
        os.remove(i)
        payloadsRemoved += 1
    print t.bold_green + "[*] %s Payloads removed...."% payloadsRemoved + t.normal
    return "clear"

def getAndRunPSMenu():
    if len(clientMenuOptions) > 2:
        psMenu = MenuOptions(psMenuOptions(), menuName="PS Menu")
        psMenu.runmenu()
    else:
        print t.bold_red + "[!] Clients are needed to access this menu" + t.normal
    return False

def getAndRunClientMenu():
    if len(clientMenuOptions) > 2:
        clientMenu = MenuOptions(clientMenuOptions, menuName="Client Menu")
        clientMenu.runmenu()
    else:
        print t.bold_red + "[!] Clients are needed to access this menu" + t.normal
    return False

def getAndRunMainMenu():
    mainMenu = MenuOptions(mainMenuOptions(), menuName="Main Menu")
    mainMenu.runmenu()
    return False

def returnText(colour, text):
    print colour + text + t.normal

def mainMenuOptions():
    return OrderedDict([
    ('1', {'payloadchoice': SHELLCODE.windows_rev_shell, 'payload': 'Windows_Reverse_Shell', 'extrawork': reversePayloadGeneration, 'availablemodules': None, 'params': None}),
    ('2', {'payloadchoice': SHELLCODE.windows_met_rev_shell, 'payload': 'Windows_Meterpreter_Reverse_Shell', 'extrawork': reversePayloadGeneration, 'availablemodules': METASPLOIT_Functions['reverse'], 'params': None}),
    ('3', {'payloadchoice': SHELLCODE.windows_met_bind_shell, 'payload': 'Windows_Meterpreter_Bind_Shell', 'extrawork': bindPayloadGeneration, 'availablemodules': METASPLOIT_Functions['bind'], 'params': None}),
    ('4', {'payloadchoice': SHELLCODE.windows_met_rev_https_shell, 'payload': 'Windows_Meterpreter_Reverse_HTTPS', 'extrawork': httpsPayloadGeneration, 'availablemodules': METASPLOIT_Functions['https'], 'params': None}),
    ('5', {'payloadchoice': SHELLCODE.windows_met_rev_shell_dns, 'payload': 'Windows_Meterpreter_Reverse_Dns', 'extrawork': dnsPayloadGeneration, 'availablemodules': METASPLOIT_Functions['dns'], 'params': None}),
    ('ps', {'payloadchoice': None, 'payload': 'PowerShell Menu', 'extrawork': getAndRunPSMenu, 'params': None}),
    ('stager', {'payloadchoice': None, 'payload': 'Powershell Stager', 'extrawork': printListener, 'params': None}),
    ('clients', {'payloadchoice': None, 'payload': 'Stager Connected Clients', 'extrawork': getAndRunClientMenu, 'params': None, 'spacer': True}),
    ('cleanup', {'payloadchoice': None, 'payload': 'Clean Up Payload Directory', 'extrawork': cleanUpPayloads, 'params': None, 'availablemodules': {len(glob.glob(payloaddir() + "/*.exe")): ''}}),
    ('interface', {'payloadchoice': None, 'payload': 'Set Default Network Interface', 'extrawork': doInterfaceSelect, 'params': None, 'availablemodules': {returnINTER(): ''}}),
    ('?', {'payloadchoice': None, 'payload': 'Print Detailed Help', 'extrawork': winpayloads_help, 'params': None}),
    ('back', {'payloadchoice': None, 'payload': 'Main Menu', 'extrawork': getAndRunMainMenu, 'params': None}),
    ('exit', {'payloadchoice': None, 'payload': 'Exit', 'extrawork': menuRaise, 'params': None}),
])

def psMenuOptions():
    return OrderedDict([
    ('1', {'payloadchoice': None, 'payload': 'Screen_Watch', 'extrawork': returnText , 'params': (t.bold_red, 'Module is borked...')}),
    ('2', {'payloadchoice': SHELLCODE.windows_ps_ask_creds_tcp, 'payload': 'Asks_Creds', 'extrawork': reversePowerShellAskCredsGeneration, 'params': None}),
    ('3', {'payloadchoice': SHELLCODE.windows_invoke_mimikatz, 'payload': 'Invoke_Mimikatz', 'extrawork': reversePowerShellInvokeMimikatzGeneration, 'params': None}),
    ('4', {'payloadchoice': SHELLCODE.windows_uac_bypass, 'payload': 'UAC_Bypass', 'extrawork': UACBypassGeneration, 'params': None}),
    ('clients', {'payloadchoice': None, 'payload': 'Connected Interpreter Clients', 'extrawork': getAndRunClientMenu, 'params': None}),
    ('back', {'payloadchoice': None, 'payload': 'Main Menu', 'extrawork': getAndRunMainMenu, 'params': None}),
])

clientMenuOptions = OrderedDict([
    ('back', {'payloadchoice': None, 'payload': 'Main Menu', 'extrawork': getAndRunMainMenu, 'params': None}),
    ('r', {'payloadchoice': None, 'payload': 'Refresh', 'extrawork': getAndRunClientMenu, 'params': None}),
])

class promptComplete(prompt_toolkit.completion.Completer):
    def __init__(self, choices):
        super(promptComplete, self).__init__()
        self.choices = choices

    def get_completions(self, document, complete_event):
        return [prompt_toolkit.completion.Completion(x, start_position=-document.cursor_position) for x in self.choices if x.startswith(document.text)]


class MenuOptions(object):
    def __init__(self, choices, menuName):
        self.choices = choices
        self.menuName = menuName
        self.style = prompt_toolkit.styles.style_from_dict({
            prompt_toolkit.token.Token:  '#FFCC66'
        })

    def _choose(self, n):
        if self.choices.has_key(n):
            return (True, self.choices[n]['payloadchoice'], self.choices[n]['payload'], self.choices[n]['extrawork'], self.choices[n]['params'])
        else:
            if not n == "":
                print t.bold_red + '[*] Wrong Selection' + t.normal
            return (False, None, None, None, None)

    def runmenu(self):
        self.printMenues(True)
        while True:
            user_choice = prompt_toolkit.prompt('%s > '%(self.menuName),style=self.style, patch_stdout=True, completer=promptComplete(self.choices)).rstrip(' ')
            success, payloadchoice, payload, extrawork, params = self._choose(user_choice)

            if not success:
                continue
            if extrawork:
                if payloadchoice:
                    result = extrawork(payloadchoice,payload)
                elif params:
                    result = extrawork(*params)
                else:
                    result = extrawork()
                if result == "noclear":
                    self.printMenues(False)
                if result == "clear":
                    if self.menuName == 'Main Menu':
                        getAndRunMainMenu()
                    elif self.menuName == 'PowerShell Menu':
                        getAndRunPSMenu()
                    elif self.menuName == 'Stager Connected Clients':
                        self.printMenues(True)
                if result == "pass":
                    pass

    def printMenues(self,toClear):
        Splash(toClear)
        if t.width % 2 > 0:
            adjust = 0
        else:
            adjust = -1
        print t.bold_black + '=' * (t.width / 2 - (len(self.menuName) / 2)) + t.yellow + self.menuName + t.bold_black + '=' * (t.width / 2 - ((len(self.menuName) / 2)- adjust)) + t.normal
        maxlen = 0
        arr = []
        for i in self.choices.iterkeys():
            menuPrintString = t.bold_yellow + str(i) + ': ' + t.normal + str(self.choices[i]['payload']).replace('_',' ')
            if 'availablemodules' in self.choices[i].keys() and self.choices[i]['availablemodules']:
                menuPrintString += t.bold_green + ' ' + str(self.choices[i]['availablemodules'].keys()).replace('\'','').replace('normal, ','') + t.normal
            if 'spacer' in self.choices[i]:
                menuPrintString += '\n'

            nocolourlen = noColourLen(menuPrintString)
            if nocolourlen > maxlen:
                maxlen = nocolourlen
            arr.append(menuPrintString)

        for i in arr:
            spacing = (t.width / 2) - (maxlen / 2)
            if spacing % 2 > 0:
                spacing -= 1
            if len(i) % 2 > 0:
                adjust = 0
            else:
                adjust = 1
            print (' '* spacing) + i + (' ' * (spacing - adjust))
        print t.bold_black + '='*t.width + t.normal

def Splash(toClear):
    if toClear:
        print t.clear
    print t.bold_red
    print noColourCenter("_       ___       ____              __                __")
    print noColourCenter("   | |     / (_)___  / __ \____ ___  __/ /___  ____ _____/ /____")
    print noColourCenter("   | | /| / / / __ \/ /_/ / __ `/ / / / / __ \/ __ `/ __  / ___/")
    print noColourCenter(" | |/ |/ / / / / / ____/ /_/ / /_/ / / /_/ / /_/ / /_/ (__  )")
    print noColourCenter(" |__/|__/_/_/ /_/_/    \__,_/\__, /_/\____/\__,_/\__,_/____/")
    print noColourCenter("                        /____/NCCGroup - CharlieDean" + t.normal)
