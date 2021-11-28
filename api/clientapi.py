import json
import os
import subprocess
import sys
from base64 import b64encode
from time import sleep

import psutil
import urllib3

from util.session import Session


class ClientApi:
    dataFile = [
        "gameModes",
        "gameTypes",
        "maps",
        "seasons",
        "queues"
    ]
    baseBotId = [1, 3, 8, 12, 10, 31, 48, 36, 32]

    clientProcessName = "LeagueClientUX"
    clientHostProcessName = "LeagueClient"
    gameProcessName = "League of Legends"

    clientExecutablePath = "League of Legends\\LeagueClient.exe"
    clientPbeExecutablePath = "League of Legends (PBE)\\LeagueClient.exe"
    defaultLeaguePath = "C:\\riot\\Riot Games"
    leagueGameconfigPath = "League of Legends\\Config\\game.cfg"
    leagueKeyconfigPath = "League of Legends\\Config\\input.ini"
    leaguePersistedSettingsPath = "League of Legends\\Config\\PersistedSettings.json"
    gameApiPort = 2999

    adress = "127.0.0.1"
    getCustomUrl = "/lol-lobby/v1/custom-games"
    loginUrl = "/lol-login/v1/session"
    createLobbyUrl = "/lol-lobby/v2/lobby"
    addBotsUrl = "/lol-lobby/v1/lobby/custom/bots"
    searchUrl = "/lol-lobby/v2/lobby/matchmaking/search"
    switchTeamurl = "/lol-lobby/v1/lobby/custom/switch-teams"
    startCustomUrl = "/lol-lobby/v1/lobby/custom/start-champ-select"
    acceptUrl = "/lol-matchmaking/v1/ready-check/accept"
    pickUrl = "/lol-champ-select/v1/session/actions/"
    sessionUrl = "/lol-champ-select/v1/session"
    registerRolesUrl = "/lol-lobby/v2/lobby/members/localMember/position-preferences"
    honorURL = "/lol-honor-v2/v1/honor-player"
    getHonorDataUrl = "/lol-honor-v2/v1/ballot"
    pickableChampionsUrl = "/lol-champ-select/v1/pickable-champion-ids"
    summonerWardUrl = "/lol-champ-select/v1/session/my-selection"
    killUXUrl = "/riotclient/kill-ux"
    gameflowAvailabilityUrl = "/lol-gameflow/v1/availability"
    gameflowPhaseUrl = "/lol-gameflow/v1/gameflow-phase"
    currentSummonerUrl = "/lol-summoner/v1/current-summoner"
    gameSessionUrl = "/lol-gameflow/v1/session"
    getLootUrl = "/lol-loot/v1/player-loot"
    lootIdContextUrl = "/lol-loot/v1/player-loot/{}/context-menu"
    lootIdUrl = "/lol-loot/v1/player-loot/{}"

    lockPath = os.path.join(defaultLeaguePath, "League of Legends\\lockfile")
    pbelockPath = os.path.join(defaultLeaguePath, "League of Legends (PBE)\\lockfile")

    def __init__(self, mode="NORMAL"):
        print('-- CLIENT INIT START --')
        self.mode = mode
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.pid = self.clientOpened()

        if self.pid == -1:
            self.killClient()
            sleep(0.5)
            self.openClient()
            sleep(0.5)
            while not self.setLockFile():
                sleep(0.5)
        else:
            while not self.setLockFile():
                sleep(0.5)

        print("Waiting for Client to open")
        while not self.isApiReady():
            sleep(0.5)
        while not self.isAvailable():
            sleep(0.5)
        print('-- CLIENT INIT DONE --')

    def killClient(self):
        for process in ['LeagueClientUxRender.exe', 'LeagueClient.exe', 'LeagueClientUx.exe', 'RiotClientServices.exe']:
            try:
                # os.system("taskkill /f /im "+process)
                subprocess.Popen("taskkill /f /im " + process, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            except:
                pass
        sleep(0.1)

    def setLockFile(self):
        if self.mode == "NORMAL":
            lockPath = self.lockPath
        else:
            lockPath = self.pbelockPath
        if not os.path.isfile(lockPath):
            return False
        with open(lockPath, "r+") as fd:
            lockData = fd.read().split(':')
        self.session = Session(
            lockData[4], self.adress,
            lockData[2],
            {
                'Authorization': 'Basic ' + b64encode(bytes("riot:{}".format(lockData[3]), 'utf-8')).decode('ascii')
            }
        )
        self.pid = lockData[1]
        return True

    def isApiReady(self):
        try:
            r = self.session.request('get', '/lol-login/v1/session')
            if r.status_code != 200:
                return False
            # Login completed, now we can get data
            if r.json()['state'] == 'SUCCEEDED':
                if r.json()['summonerId'] == None:
                    return False
                self.summonerId = r.json()['summonerId']
                return True
            else:
                # print(r.json()['state'])
                return False
        except:
            return False

    def clientOpened(self):
        for proc in psutil.process_iter():
            try:
                # Get process name & pid from process object.
                processName = proc.name()
                if processName == self.clientHostProcessName + '.exe':
                    return proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return -1

    def openClient(self):
        print('-- STARTING CLIENT --')
        if self.mode == "normal":
            subprocess.call([os.path.join(self.defaultLeaguePath, self.clientExecutablePath)])
        else:
            subprocess.call([os.path.join(self.defaultLeaguePath, self.clientPbeExecutablePath)])

    def isAvailable(self):
        r = self.session.request('get', '/lol-gameflow/v1/availability')
        return r.json()['isAvailable']

    def disenchantAll(self):
        r = self.session.request("get", self.getLootUrl)
        datas = r.json()
        resId = [(data['lootId'], data['count']) for data in datas if
                 data['disenchantLootName'] == "CURRENCY_champion"]
        if not len(resId):
            return False
        for champId, count in resId:
            self.session.request("post",
                                 "/lol-loot/v1/recipes/CHAMPION_RENTAL_disenchant/craft?repeat={}".format(count),
                                 [champId]).json()
        return True
