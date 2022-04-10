import PySimpleGUI as sg
from PySimpleGUIQt import SystemTray as SystemTrayQt
from os.path import exists, dirname, realpath
from os import remove, system
import pandas as pd
import cryptocode
from getpass import getuser
import datetime
from time import sleep
import multiprocessing
from win10toast import ToastNotifier

sg.theme("Dark Black")
closeAll = 0
key = "29032022"
dataPath = dirname(realpath("TimeOut.exe")) + "\\data"
todayDate = datetime.date.today()
todayDateInt = int(todayDate.strftime("%Y%m%d"))
remainTime = -1
notify = ToastNotifier()


def checkIfDataExists():
    if exists("data") == False:
        password = firstTime()

        global todayDate

        if password != None:
            password = cryptocode.encrypt(password, key)
            dayLimit = cryptocode.encrypt("unlimited", key)
            todayDateEncrypt = cryptocode.encrypt(str(todayDate), key)
            isOnOff = cryptocode.encrypt("off", key)
            isTurnAutoOnOff = cryptocode.encrypt("off", key)
            counter = cryptocode.encrypt("off", key)
            toWrite = [
                [
                    password,
                    todayDateEncrypt,
                    "expires",
                    isOnOff,
                    isTurnAutoOnOff,
                    counter,
                    dayLimit,
                    dayLimit,
                    dayLimit,
                    dayLimit,
                    dayLimit,
                    dayLimit,
                    dayLimit,
                ]
            ]
            df = pd.DataFrame(
                toWrite,
                columns=[
                    "password",
                    "date",
                    "expires",
                    "isOn",
                    "isTurnAutoOn",
                    "counter",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ],
            )

            global dataPath

            with open(dataPath, "w") as data:
                dfString = df.to_string(index=False)
                data.write(dfString)
            data.close()

            notify.show_toast(
                "TimeOut",
                "You have successfully created an access password. The application is now located in the tray on the Taskbar",
                icon_path="icon.ico",
                duration=15,
                threaded=True,
            )
            settingsWindow()
        else:
            return False
    else:
        return True


def firstTime():
    layoutFirstTime = [
        [sg.Text("It looks like you are running TimeOut for the first time")],
        [sg.Text("Create a password to access the application")],
        [sg.InputText(password_char="•")],
        [sg.Text("Repeat password")],
        [sg.InputText(password_char="•")],
        [sg.Button("Save")],
    ]

    layoutCenter = [
        [sg.VPush()],
        [sg.Push(), sg.Column(layoutFirstTime, element_justification="c"), sg.Push()],
        [sg.VPush()],
    ]

    firstTimeWindow = sg.Window("TimeOut", layoutCenter, icon=r"icon.ico")

    while True:
        event, values = firstTimeWindow.read()

        if event == "Save":
            if values[0] == values[1]:
                break
            else:
                sg.popup(
                    "Passwords are not the same", auto_close=True, auto_close_duration=2
                )

        if event == sg.WIN_CLOSED:
            break

    firstTimeWindow.close()
    return values[0]


def readData(label):
    global dataPath

    with open(dataPath, "r") as data:
        df = pd.read_fwf(data)
    data.close()

    returnData = str(cryptocode.decrypt(df.iloc[0][label], key))
    return returnData


def writeData(label, toWrite):
    global dataPath

    with open(dataPath, "r") as data:
        df = pd.read_fwf(data)
    data.close()

    toWrite = str(toWrite)
    df.loc[0, label] = cryptocode.encrypt(toWrite, key)

    with open("data", "w") as data:
        dfString = df.to_string(index=False)
        data.write(dfString)
    data.close()


def turnAutoStart(turn):
    userName = getuser()
    batPath = r"C:\Users\{}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup".format(
        userName
    )
    batFilePath = r"C:\Users\{}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\TimeOutStart.bat".format(
        userName
    )

    if turn == "on":
        if exists(batFilePath) == False:
            appPath = dirname(realpath("TimeOut.exe"))
            TimeOutPath = appPath + "\\TimeOut.exe"

            with open(batPath + "\\" + "TimeOutStart.bat", "w+") as batStartFile:
                batStartFile.write(
                    r'start "" /d "{}" "{}"'.format(appPath, TimeOutPath)
                )
            batStartFile.close()

            writeData("isTurnAutoOn", "on")

            notify.show_toast(
                "TimeOut",
                "Application AutoStart enabled",
                icon_path="icon.ico",
                duration=2,
                threaded=True,
            )
            return "on"

    elif turn == "off":
        if exists(batFilePath) == True:
            remove(batFilePath)
            notify.show_toast(
                "TimeOut",
                "Application AutoStart disabled",
                icon_path="icon.ico",
                duration=2,
                threaded=True,
            )

            writeData("isTurnAutoOn", "off")
            return "off"


def countRemainTime():
    global todayDateInt

    readedDate = datetime.datetime.strptime(readData("date"), "%Y-%m-%d")
    readedDate = int(readedDate.strftime("%Y%m%d"))
    dayName = todayDate.strftime("%A")
    dayLimit = readData(dayName)

    try:
        remainTime = int(readData("expires"))
    except:
        remainTime = readData("expires")

    if todayDateInt > readedDate:
        writeData("expires", dayLimit)
        writeData("date", todayDate)

    while True:
        if readData("isOn") == "on":
            if remainTime == 0:
                notify.show_toast(
                    "TimeOut",
                    "Your time for today is up, you have 1 minute to log in to the application, otherwise you will be logged out",
                    icon_path="icon.ico",
                    duration=20,
                    threaded=True,
                )
                sleep(60)
                if readData("counter") == "on":
                    notify.show_toast(
                        "TimeOut",
                        "Time's up, logging out...",
                        icon_path="icon.ico",
                        duration=5,
                        threaded=True,
                    )
                    sleep(5)
                    system('cmd /c "shutdown -l"')

            else:
                while True:
                    if readData("counter") == "on":
                        try:
                            remainTime = int(readData("expires"))
                        except:
                            print("")
                        if remainTime == 10 and readData("counter") == "on":
                            notify.show_toast(
                                "TimeOut",
                                "There are 10 minutes of time left, better save your work",
                                icon_path="icon.ico",
                                duration=10,
                                threaded=True,
                            )
                        elif remainTime == 0:
                            notify.show_toast(
                                "TimeOut",
                                "Time's up, logging out...",
                                icon_path="icon.ico",
                                duration=5,
                                threaded=True,
                            )
                            sleep(5)
                            system('cmd /c "shutdown -l"')
                            break
                        elif remainTime == "unlimited":
                            break

                        sleep(60)
                        remainTime -= 1
                        writeData("expires", remainTime)
                        continue
                    sleep(60)
        sleep(60)


def settingsWindow():
    if readData("isTurnAutoOn") == "on":
        turnAutoButton = sg.Button(
            "Enable/Disable Application AutoStart",
            key="turnAuto",
            button_color=("white", "green"),
            size=(30, 1),
        )
    else:
        turnAutoButton = sg.Button(
            "Enable/Disable Application AutoStart",
            key="turnAuto",
            button_color=("white", "red"),
            size=(30, 1),
        )

    if readData("isOn") == "on":
        turnOnButton = sg.Button(
            "Enable/disable daily limits",
            key="turnOn",
            button_color=("white", "green"),
            size=(30, 1),
        )
    else:
        turnOnButton = sg.Button(
            "Enable/disable daily limits",
            key="turnOn",
            button_color=("white", "red"),
            size=(30, 1),
        )

    layoutSettings = [
        [sg.Text("Application settings")],
        [
            sg.Text(
                "NOTE! Today's time will be reset when the daily limit is enabled/disabled"
            )
        ],
        [sg.Text("")],
        [sg.Button("Change the time limits", size=(30, 1))],
        [sg.Button("Change password", size=(30, 1))],
        [turnAutoButton],
        [turnOnButton],
        [sg.Button("Close the entire application", size=(30, 1))],
        [sg.Button("Close this window", size=(30, 1))],
        [sg.Text("")],
        [sg.Text("Time is stopped")],
        [sg.Text("Szymon Kowalczyk          GitHub: Morlom")],
    ]

    layoutCenter = [
        [sg.VPush()],
        [sg.Push(), sg.Column(layoutSettings, element_justification="c"), sg.Push()],
        [sg.VPush()],
    ]

    settingsWindow = sg.Window(
        "TimeOut", layoutCenter, modal=True, element_padding=(2, 2), icon=r"icon.ico"
    )

    global closeAll

    if readData("isOn") == "on":
        writeData("counter", "off")

    while True:
        event, values = settingsWindow.read()

        if event == "Change password":
            passChangeWindow()

        elif event == "Change the time limits":
            dayLimitWindow()

        elif event == "turnAuto":
            if turnAutoStart("on") == "on":
                settingsWindow["turnAuto"].update(button_color=("white", "green"))
            elif turnAutoStart("off") == "off":
                settingsWindow["turnAuto"].update(button_color=("white", "red"))

        elif event == "turnOn":
            if readData("isOn") == "off":
                writeData("isOn", "on")
                writeData("counter", "on")
                dayName = todayDate.strftime("%A")
                dayLimit = readData(dayName)
                writeData("expires", dayLimit)
                settingsWindow["turnOn"].update(button_color=("white", "green"))
                notify.show_toast(
                    "TimeOut",
                    "Daily limits are enabled",
                    icon_path="icon.ico",
                    duration=2,
                    threaded=True,
                )
            elif readData("isOn") == "on":
                writeData("isOn", "off")
                writeData("counter", "off")
                settingsWindow["turnOn"].update(button_color=("white", "red"))
                notify.show_toast(
                    "TimeOut",
                    "Daily limits have been disabled",
                    icon_path="icon.ico",
                    duration=2,
                    threaded=True,
                )

        elif event == "Close the entire application":
            if readData("isOn") == "on":
                writeData("counter", "on")
            closeAll = 1
            break

        if event == sg.WIN_CLOSED or event == "Close this window":
            break

    settingsWindow.close()


def stopWindow():
    global remainTime

    layoutStop = [
        [sg.Text("Time stopped")],
        [sg.Text("")],
        [sg.Button("Unlock", size=(10, 1))],
        [sg.Text("")],
        [sg.Text("Remaining time: " + readData("expires") + " min")],
    ]

    layoutCenter = [
        [sg.VPush()],
        [sg.Push(), sg.Column(layoutStop, element_justification="c"), sg.Push()],
        [sg.VPush()],
    ]

    stopWindow = sg.Window(
        "STOP",
        layoutCenter,
        modal=True,
        finalize=True,
        no_titlebar=True,
        keep_on_top=True,
        element_padding=(2, 2),
    )
    stopWindow.Maximize()

    while True:
        stopWindow.BringToFront()

        event, values = stopWindow.read()

        if event == "Unlock":
            writeData("counter", "on")
            break

    stopWindow.close()


def loginWindow():
    global remainTime

    layoutLogin = [
        [sg.Text("Enter password")],
        [sg.InputText(password_char="•", size=(52, 1))],
        [
            sg.Button("Log in", size=(14, 1)),
            sg.Button("Stop time", size=(14, 1)),
            sg.Button("Close this window", size=(14, 1)),
        ],
        [sg.Text("Today's remaining time: " + readData("expires") + " min", key="txt")],
    ]

    layoutCenter = [
        [sg.VPush()],
        [sg.Push(), sg.Column(layoutLogin, element_justification="c"), sg.Push()],
        [sg.VPush()],
    ]

    loginWindow = sg.Window(
        "TimeOut", layoutCenter, modal=True, element_padding=(2, 2), icon=r"icon.ico"
    )

    global closeAll
    closeLogin = 0

    while True:
        event, values = loginWindow.read(timeout=10000)

        if event == "Log in":
            password = readData("password")
            if str(values[0]) == password:
                settingsWindow()
            else:
                sg.popup("Incorrect password", auto_close=True, auto_close_duration=2)
        elif event == "Stop time":
            if readData("isOn") == "on" and readData("expires") != "unlimited":
                writeData("counter", "off")
                closeLogin = 1
                break

        if event == "Close this window" or event == sg.WIN_CLOSED:
            break
        elif closeAll == 1:
            break

        loginWindow["txt"].update(
            "Today's remaining time: " + readData("expires") + " min"
        )

    loginWindow.close()
    if closeLogin == 1:
        stopWindow()


def passChangeWindow():
    layoutPassChange = [
        [sg.Text("Changing your password")],
        [sg.Text("Enter old password")],
        [sg.InputText(password_char="•", size=(35, 1))],
        [sg.Text("Enter a new password")],
        [sg.InputText(password_char="•", size=(35, 1))],
        [sg.Text("Repeat new password")],
        [sg.InputText(password_char="•", size=(35, 1))],
        [sg.Text("")],
        [sg.Button("Save", size=(20, 1))],
    ]

    layoutCenter = [
        [sg.VPush()],
        [sg.Push(), sg.Column(layoutPassChange, element_justification="c"), sg.Push()],
        [sg.VPush()],
    ]

    passChangeWindow = sg.Window(
        "TimeOut", layoutCenter, modal=True, element_padding=(2, 2), icon=r"icon.ico"
    )

    while True:
        event, values = passChangeWindow.read()

        if event == "Save":
            if values[0] != "":
                password = readData("password")
                if str(values[0]) == password:
                    if values[1] == values[2]:
                        writeData("password", values[1])
                        notify.show_toast(
                            "TimeOut",
                            "Password successfully changed",
                            icon_path="icon.ico",
                            duration=5,
                            threaded=True,
                        )
                        break
                    else:
                        sg.popup(
                            "New passwords are not the same",
                            auto_close=True,
                            auto_close_duration=2,
                        )
                else:
                    sg.popup(
                        "The old password is not correct",
                        auto_close=True,
                        auto_close_duration=2,
                    )
            else:
                break

        if event == sg.WIN_CLOSED:
            break

    passChangeWindow.close()


def dayLimitWindow():
    layoutDayLimit = [
        [sg.Text("Enter the daily limits in minutes")],
        [sg.Text('Enter "0" to block computer use for the current day')],
        [sg.Text('Enter "-" if you want to disable the limit on a given day')],
        [sg.Text("A blank field does not change the limit on a given day")],
        [sg.Text("")],
        [
            sg.Text("Monday  ", size=(11, 1), justification="right"),
            sg.InputText(size=(6, 1)),
            sg.Text(
                "  currently: " + readData("Monday") + " min",
                size=(19, 1),
                justification="left",
            ),
        ],
        [
            sg.Text("Tuesday  ", size=(11, 1), justification="right"),
            sg.InputText(size=(6, 1)),
            sg.Text(
                "  currently: " + readData("Tuesday") + " min",
                size=(19, 1),
                justification="left",
            ),
        ],
        [
            sg.Text("Wednesday  ", size=(11, 1), justification="right"),
            sg.InputText(size=(6, 1)),
            sg.Text(
                "  currently: " + readData("Wednesday") + " min",
                size=(19, 1),
                justification="left",
            ),
        ],
        [
            sg.Text("Thursday  ", size=(11, 1), justification="right"),
            sg.InputText(size=(6, 1)),
            sg.Text(
                "  currently: " + readData("Thursday") + " min",
                size=(19, 1),
                justification="left",
            ),
        ],
        [
            sg.Text("Friday  ", size=(11, 1), justification="right"),
            sg.InputText(size=(6, 1)),
            sg.Text(
                "  currently: " + readData("Friday") + " min",
                size=(19, 1),
                justification="left",
            ),
        ],
        [
            sg.Text("Saturday  ", size=(11, 1), justification="right"),
            sg.InputText(size=(6, 1)),
            sg.Text(
                "  currently: " + readData("Saturday") + " min",
                size=(19, 1),
                justification="left",
            ),
        ],
        [
            sg.Text("Sunday  ", size=(11, 1), justification="right"),
            sg.InputText(size=(6, 1)),
            sg.Text(
                "  currently: " + readData("Sunday") + " min",
                size=(19, 1),
                justification="left",
            ),
        ],
        [sg.Text("")],
        [sg.Button("Save", size=(30, 1))],
    ]

    layoutCenter = [
        [sg.VPush()],
        [sg.Push(), sg.Column(layoutDayLimit, element_justification="c"), sg.Push()],
        [sg.VPush()],
    ]

    dayLimitWindow = sg.Window(
        "TimeOut", layoutCenter, modal=True, element_padding=(2, 2), icon=r"icon.ico"
    )

    i = 0
    toWrite = 0
    write = 0
    saved = 0

    while True:
        event, values = dayLimitWindow.read()

        if event == "Save":
            while i <= 6:
                try:
                    values[i] = int(values[i])
                except:
                    print("")

                if isinstance(values[i], int) == True:
                    toWrite = values[i]
                    write = 1
                elif values[i] == "-":
                    toWrite = "unlimited"
                    write = 1
                else:
                    write = 0

                if write == 1:
                    saved = 1
                    match i:
                        case 0:
                            writeData("Monday", toWrite)
                        case 1:
                            writeData("Tuesday", toWrite)
                        case 2:
                            writeData("Wednesday", toWrite)
                        case 3:
                            writeData("Thursday", toWrite)
                        case 4:
                            writeData("Friday", toWrite)
                        case 5:
                            writeData("Saturday", toWrite)
                        case 6:
                            writeData("Sunday", toWrite)
                i += 1
            if saved == 1:
                notify.show_toast(
                    "TimeOut",
                    "Successfully saved daily limits",
                    icon_path="icon.ico",
                    duration=2,
                    threaded=True,
                )
            break

        if event == sg.WIN_CLOSED:
            break

    dayLimitWindow.close()


def systemTrayIcon():
    global closeAll
    global startCounting

    if checkIfDataExists() == False:
        closeAll = 1

    startCounting.start()

    menu_def = ["BLANK", ["&Open", "---", "Stop time"]]
    tray = SystemTrayQt(menu=menu_def, filename=r"icon.ico")

    while True:
        if closeAll == 1:
            break

        event = tray.read()

        if event == "Open":
            loginWindow()
        elif event == "Stop time":
            if readData("isOn") == "on" and readData("expires") != "unlimited":
                writeData("counter", "off")
                stopWindow()
    startCounting.terminate()
    startApp.terminate()


startCounting = multiprocessing.Process(target=countRemainTime)
startApp = multiprocessing.Process(target=systemTrayIcon)


def main():
    startApp.start()
    startApp.join()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
