
import requests
import json
from colorama import Fore, Back, Style
from colorama import init
import random
from random import choice
import time
import threading

#initiates colourama (the module that makes the text coloured)
init()


#prints the title and calls the starting functions
def Start():
    print(Fore.CYAN + " ██████  ██████   ██████  ██    ██ ██████           ██  ██████  ██ ███    ██ ███████ ██████  ")
    print("██       ██   ██ ██    ██ ██    ██ ██   ██          ██ ██    ██ ██ ████   ██ ██      ██   ██")
    print("██   ███ ██████  ██    ██ ██    ██ ██████           ██ ██    ██ ██ ██ ██  ██ █████   ██████  ")
    print("██    ██ ██   ██ ██    ██ ██    ██ ██          ██   ██ ██    ██ ██ ██  ██ ██ ██      ██   ██ ")
    print(" ██████  ██   ██  ██████   ██████  ██           █████   ██████  ██ ██   ████ ███████ ██   ██ ")
    print(Fore.WHITE + "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")
    Config()



#gets the funcaptcha token
def GetToken(GroupUrl, proxy):
    InitSolver = requests.get(f"https://2captcha.com/in.php?key={ApiKey}&method=funcaptcha&publickey={PublicKey}&surl=https://roblox-api.arkoselabs.com&pageurl={GroupUrl}", proxies=proxy).text
    Resp = InitSolver.split("|")
    if Resp[0] != "OK":
        print(Fore.RED + f"[Error With Solver {InitSolver}]")
        raise SolverFail
    print(Fore.CYAN + "Solver Started: " + Fore.YELLOW + InitSolver)
    CaptchaId = Resp[1]
    CaptchaSolved = False
    while CaptchaSolved == False:
        time.sleep(5)
        CheckIfSolved = requests.get(f"https://2captcha.com/res.php?key={ApiKey}&action=get&id={CaptchaId}", proxies=proxy).text
        print(Fore.CYAN + "2Captcha Response: " + Fore.YELLOW + CheckIfSolved)
        if CheckIfSolved == "ERROR_CAPTCHA_UNSOLVABLE":
            print("[Captcha Unsolvable, Retrying...]")
            GetToken(GroupUrl, proxy)
        if 'CAPCHA_NOT_READY' in CheckIfSolved: 
            continue
        print(Fore.CYAN + "2Captcha: " + Fore.GREEN + "Captcha Solved")
        CaptchaSolved = True
    return CheckIfSolved.partition("|")[2]
        

#joins the group 
def JoinGroup(proxy, Cookie, GroupId, FuncaptchaToken, xcsrf):
    try:
        JoinHeaders = {"X-CSRF-TOKEN": xcsrf, "Cookie": F".ROBLOSECURITY={Cookie}"}
        JoinJson = {"captchaToken": FuncaptchaToken, "captchaProvider": "PROVIDER_ARKOSE_LABS"}
        JoinGroup = requests.post(url=f"https://groups.roblox.com/v1/groups/{GroupId}/users", headers=JoinHeaders, data=JoinJson, proxies=proxy)
        return JoinGroup
        
    except Exception as Error:
        print(Fore.RED + "[Error: " + str(Error + "]"))

#gets the amount of groups the account should have 
def AccountGroups(Cookie, proxy):
    try:
        GroupCount = 0
        UserID = requests.get(url="https://users.roblox.com/v1/users/authenticated", headers = {"Cookie": F".ROBLOSECURITY={Cookie}"}, proxies=proxy).json()["id"]
        GroupRoles = requests.get(url=f"https://groups.roblox.com/v2/users/{UserID}/groups/roles", proxies=proxy).json()["data"]
        for _ in GroupRoles:
            GroupCount += 1
        return GroupCount
    except Exception as Error:
        print(Fore.RED + "[Error: " + str(Error + "]"))

#gets the group url for 2captcha
def FuncGroupUrl(GroupId):
    try:
        GroupRequest = requests.get(f"https://roblox.com/groups/{GroupId}")
        GroupUrl = GroupRequest.url
        return GroupUrl
    except Exception as Error:
        print(Fore.RED + "[Error: " + str(Error + "]"))

#gets the xcsrf token needed for post request (joining the group)
def xcsrf_token(Cookie, proxy):
    try:
        headers = {"Cookie": F".ROBLOSECURITY={Cookie}"}
        XCSRF = requests.post("https://auth.roblox.com/v2/login", headers=headers, proxies=proxy).headers["x-csrf-token"]
        return XCSRF
    except Exception as Error:
        print(Fore.RED + "[Error: " + str(Error + "]"))

#deals with the aspects of joining the group
def Main(GroupUrl, proxy, Cookie, GroupId, JoinedCount, GroupRange, LocalGroups):

    FuncaptchaToken = GetToken(GroupUrl, proxy)
    xcsrf = xcsrf_token(Cookie, proxy)
    Join = JoinGroup(proxy, Cookie, GroupId, FuncaptchaToken, xcsrf)
    if str(Join.json()) == "{}":
        print(Fore.GREEN + f"[Successfully Joined Group: {GroupUrl}]")
        JoinedCount += 1
        if ClaimGroups:
            ClaimGroup = requests.post(f"https://groups.roblox.com/v1/groups/{GroupId}/claim-ownership", headers={"X-CSRF-TOKEN": xcsrf, "Cookie": F".ROBLOSECURITY={Cookie}"}, proxies=proxy)
            print(Fore.CYAN + "Roblox Claim API Response: " + Fore.YELLOW + ClaimGroup.text)
            if str(ClaimGroup.json()) == "{}":
                print(Fore.GREEN + "[Successfully Claimed Group]")
    else:
        print(Fore.CYAN + "Roblox Response: " + Fore.RED + Join.text)
    if JoinedCount < GroupRange:
        GroupId = random.choice(LocalGroups)
        GroupUrl = FuncGroupUrl(GroupId)
        #stack overflow waiting to happen, was a bit lazy
        Main(GroupUrl, proxy, Cookie, GroupId, JoinedCount, GroupRange, LocalGroups)



    

#starts the threads
def InitThreads():
    for Cookie in Cookies:
        LocalGroups = Groups
        Cookie = Cookie.strip()
        proxy = random.choice(Proxies)
        proxy = {"https": f"https://{proxy}", "http": f"https://{proxy}"}
        GroupRange = 100 - AccountGroups(Cookie, proxy)
        JoinedCount = 0
        for _ in range(0, Threads):
            proxy = random.choice(Proxies)
            proxy = {"https": f"https://{proxy}", "http": f"https://{proxy}"}
            time.sleep(0.1)
            GroupId = random.choice(LocalGroups)
            GroupUrl = FuncGroupUrl(GroupId)
            Thread = threading.Thread(target=Main, args=(GroupUrl, proxy, Cookie, GroupId, JoinedCount, GroupRange, LocalGroups)).start()
            LocalGroups.remove(GroupId)
            print(Fore.GREEN + "[Thread Started]")
        #thread.join() does not work so at the moment it does all accounts at once


#setting globals and parsing the config for the required values
def Config():
    try:
        global JoiningGroups
        JoiningGroups = True
        global Proxies 
        ProxyFile = open("Proxys.txt")
        Proxies = ProxyFile.read().splitlines()
        global Groups
        GroupFile = open("Groups.txt", "r")
        Groups = GroupFile.read().splitlines()
        global Cookies
        Cookies = list()
        OpenCookies = open("Cookies.txt", "r")
        for Cookie in OpenCookies:
            Cookies.append(Cookie)
        OpenConfig = open("Config.json","r")
        try:
            LoadConfig = json.load(OpenConfig)
        except Exception as ConfigLoadError:
            print(Fore.RED + "Config Failed to Load: " + str(ConfigLoadError))
            return
        try:
            global ApiKey
            global PublicKey
            global Threads
            global ClaimGroups
            Threads = int(LoadConfig["Threads"])
            ApiKey = str(LoadConfig["ApiKey"])
            PublicKey = str(LoadConfig["PublicKey"])
            ClaimGroups = bool(LoadConfig["ClaimGroups"])
        except Exception as ParseConfigError:
            print(Fore.RED + "[Failed to Parse Config: " + str(ParseConfigError) + "]")
            return
        time.sleep(0.5)
        print(Fore.GREEN + "[Made By Squeakalus#5879]")
        #waits 0.5 seconds between each print for a nicer loading effect rather than all at once
        time.sleep(0.5)
        print(Fore.GREEN + "[Config Loaded Successfully]")
        time.sleep(0.5)
        print("[Starting Program]" + "\n")
        threading.Thread(target=InitThreads).start()
        
    except Exception as Error:
        print(Fore.RED + "[Error: "+ str(Error) + "]")
Start()

