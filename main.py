#   Do not Copy (Keep learning : ) )
#   github@shdeb
#   shanyudeb@gmail.com
#   Author : Shashwat Debnath
#   all rights reserved by author



import sqlite3
from UI.cricket import Ui_MainWindow
from UI.newteamDlg import Ui_NEWTeamDialog
from UI.evaluateDlg import Ui_EVALUATETeamDialog
from PyQt5 import QtWidgets,QtCore,QtGui


class MainControl(QtWidgets.QMainWindow):
    def __init__(self, parent = None):
        print(type(self))
        QtWidgets.QMainWindow.__init__(self, parent)
        self.mainUi= Ui_MainWindow()
        self.mainUi.setupUi(self)
        self.mainUi.BAT.setEnabled(False)
        self.mainUi.BOW.setEnabled(False)
        self.mainUi.AR.setEnabled(False)
        self.mainUi.WK.setEnabled(False)
        
        # self.mainUi.menuOPEN_Team
        self.mainUi.actionOPEN_Team.triggered.connect(self.openTeamAct)
        self.mainUi.actionNEW_Team.triggered.connect(self.newTeamAct)
        self.mainUi.actionSAVE_Team.triggered.connect(self.saveTeamAct)
        self.mainUi.actionEVALUATE_Team.triggered.connect(self.evalTeamAct)
        self.mainUi.BAT.clicked.connect(self.batClickedAct)
        self.mainUi.BOW.clicked.connect(self.bowClickedAct)
        self.mainUi.AR.clicked.connect(self.arClickedAct)
        self.mainUi.WK.clicked.connect(self.wkClickedAct)
        self.mainUi.selection_list.itemDoubleClicked.connect(self.wrapperSelectPlayer)
        self.mainUi.result_list.itemDoubleClicked.connect(self.deselectPlayer)

        self._translate = QtCore.QCoreApplication.translate

    def closeEvent(self,event):
        print("Close event\nclosing db...")
        dbCur.close()
        dbConn.close()
        print("db closed")
        event.accept()
            
    def openTeamAct(self):
        print("openTeamAct")
        # msg, ok = QtWidgets.QInputDialog.getText(self, "Open Team", "Enter Team Name to Open")
        # print(str(type(ok))+str(type(msg))+msg)
        # if not ok: 
        #     return
        comboxItms=["Select"]
        dbCur.execute("Select distinct name from teams")
        for each in dbCur.fetchall():
            comboxItms.append(each[0])
        msg,ok=QtWidgets.QInputDialog.getItem(self, "Open Team", "* Select Team to open : ",comboxItms)
        if not ok: 
            return
        self.baseSetup(setopen=True)
        self.playersSetup()

        dbCur.execute("select players,value from teams where name==?",(msg,))
        qry1=dbCur.fetchall()
        if(len(qry1)==0):
            QtWidgets.QMessageBox.information(self, "DB warning", "'"+msg+"' Team not found in DataBase")
            self.baseSetup(radio=False)
            return

        i=0
        loadPlayers=[]
        for each in qry1:
            i+=1
            dbCur.execute("select CTG from stats WHERE player==?",(each[0],))
            qry2=dbCur.fetchall()
            if len(qry2)==0:
                print("player not found in stats \n getting...")
                self.getStats(each[0])
            loadPlayers.append(each[0])


        self.mainUi.teamNameVal.setText(self._translate(str(self), msg))


        self.players["__WK_lock__"]=False
        self.totalSelected=0
        self.setupPoints()
        for each in loadPlayers:
            self.curPlayer=each;
            ret=self.selectPlayer(True)
            if(ret==-1):
                QtWidgets.QMessageBox.information(self, "Cricket Team Rule Violation", "'"+msg+"' Team is Invalid")
                self.baseSetup(radio=False)
                return

    def getStats(self,playerName,setPlayerDic=True):
        QtWidgets.QMessageBox.information(self, "DB warning", "Player '"+each[0]+"' not in DataBase\nPlease enter data..");
        ctg,ok=QtWidgets.QInputDialog.getItem(self, "Enter '"+each[0]+"' data", "* Select Category : ",["Select","BAT","BWL","AR","WK"],0)
        if not ok: 
            self.baseSetup(radio=False)
            return
        value,ok=QtWidgets.QInputDialog.getInt(self, "Enter '"+each[0]+"' data", "* Enter player value:",value=20, min=0,max=250)
        if not ok: 
            self.baseSetup(radio=False)
            return
        matches,ok=QtWidgets.QInputDialog.getInt(self, "Enter '"+each[0]+"' data", "Enter player NO. of Maches:",min=0,value=20)
        runs,ok=QtWidgets.QInputDialog.getInt(self, "Enter '"+each[0]+"' data", "Enter player Runs:",min=0,value=67)
        l00s,ok=QtWidgets.QInputDialog.getInt(self, "Enter '"+each[0]+"' data", "Enter player NO. of 100s:",value=0,min=0)
        S0s,ok=QtWidgets.QInputDialog.getInt(self, "Enter '"+each[0]+"' data", "Enter player NO. of 50s:",value=1,min=0)

        dbCur.execute("insert into stats(player,ctg,value,matches,runs,100s,50s) values (?, ?, ?, ?, ?, ?, ?)",(playerName,ctg,value,matches,runs,l00s,S0s))

        if setPlayerDic:
            self.players[playerName]=[ctg,True,value]



    def newTeamAct(self):
        print("new team")
        #self.msg, self.ok = QtWidgets.QInputDialog.getText(self, "New Team", "Enter New Team Name")
        self.NEWTeamDialog = newTeamControl(self)
        self.NEWTeamDialog.show()


    def saveTeamAct(self):
        n=self.mainUi.result_list.count()
        if not n>0: return
        teamsSave=[]
        teamName=self.mainUi.teamNameVal.text()
        dbCur.execute("select distinct name from teams")
        if (teamName,) in dbCur.fetchall():
            QtWidgets.QMessageBox.warning(self, "DB warning", "Team with name '"+teamName+"' already exists in DataBase !\nCreate team with differnt name.")
            return

        for i in range(n):
            curPlayer=self.mainUi.result_list.item(i).text()[4:]
            dbCur.execute("insert into teams(name,players,value) values(?, ?, ?)",(teamName,curPlayer,self.players[curPlayer][2]))

        dbConn.commit()
        QtWidgets.QMessageBox.information(self, "DB Info", "'"+teamName+"' Saved successfuly.")


    def evalTeamAct(self):
        print("evaluate team")
        self.evalDialog = evalControl(self)
        self.evalDialog.show()

    def batClickedAct(self):
        print("BAT clicked"+str(type(dbCur)))

        self.mainUi.selection_list.clear()
        for i in self.players.keys():
            if i!="__WK_lock__" :
                if self.players[i][1] and self.players[i][0]=="BAT":
                    self.mainUi.selection_list.addItem(" "*4+i)



    def bowClickedAct(self):
        print("BOW clicked")
        self.mainUi.selection_list.clear()
        for i in self.players.keys():
            if i!="__WK_lock__" :
                if self.players[i][1] and self.players[i][0]=="BWL":
                    self.mainUi.selection_list.addItem(" "*4+i)


    def arClickedAct(self):
        print("AR clicked")
        self.mainUi.selection_list.clear()
        for i in self.players.keys():
            if i!="__WK_lock__" :
                if self.players[i][1] and self.players[i][0]=="AR":
                    self.mainUi.selection_list.addItem(" "*4+i)


    def wkClickedAct(self):
        print("WK clicked")
        self.mainUi.selection_list.clear()
        for i in self.players.keys():
            if i!="__WK_lock__" :
                if self.players[i][1] and self.players[i][0]=="WK":
                    self.mainUi.selection_list.addItem(" "*4+i)

    def setupPoints(self):
        print("setupPoints")
        dbCur.execute("select value from stats")
        sum=0
        for i in dbCur.fetchall():
            sum+=i[0]
        self.mainUi.pointsAvailableVal.setText(self._translate(str(self), " : "+str(sum)))
        self.mainUi.pointsUsedVal.setText(self._translate(str(self), " : "+str(0)))


    def updatePoints(self,do=">",val=0):
        if do==">":
            self.updateAPoints("sub",val)
            self.updateUPoints("add",val)

        elif do=="<":
            self.updateAPoints("add",val)
            self.updateUPoints("sub",val)


    def updateUPoints(self,do,val):
        curPointsUsd=int(self.mainUi.pointsUsedVal.text()[3:])
        valU=val

        if do=="sub":
            valU=curPointsUsd-val

        elif do=="add":
            valU=curPointsUsd+val

        self.mainUi.pointsUsedVal.setText(self._translate(str(self), " : "+str(valU)))


    def updateAPoints(self,do,val):
        curPointsAvl=int(self.mainUi.pointsAvailableVal.text()[3:])
        valA=val

        if do=="sub":
            valA=curPointsAvl-val

        elif do=="add":
            valA=curPointsAvl+val

        self.mainUi.pointsAvailableVal.setText(self._translate(str(self), " : "+str(valA)))


    def wrapperSelectPlayer(self):
        self.selectPlayer(False)
        return

    def selectPlayer(self,opn=False):

        curPlayer=self.curPlayer;

        print(curPlayer+"..|.."+self.curPlayer)

        if not opn:
            print("not onp..opn="+str(opn))
            if not self.mainUi.selection_list.selectedItems(): 
                return
            for item in self.mainUi.selection_list.selectedItems():
                selectedPlayerItem=item
            curPlayer=selectedPlayerItem.text()[4:]

        print(".."+curPlayer)

        if self.totalSelected>=11:
            QtWidgets.QMessageBox.information(self, "Cricket Team Rule Violation", "Cannot select more than 11 Players in 1 Team")
            return -1

        if self.players[curPlayer][0]=="BAT":
            print("BAT selected")
            if self.totalSelected>=10 and not self.players["__WK_lock__"]:
                QtWidgets.QMessageBox.information(self, "Cricket Team Rule Violation", "Team should have one Wicket Keeper")
                return -1
            self.mainUi.batVal.setText(self._translate(str(self), " : "+str(int(self.mainUi.batVal.text()[3:])+1)))

        elif self.players[curPlayer][0]=="BWL":
            print("BOW selected")
            if self.totalSelected>=10 and not self.players["__WK_lock__"]:
                QtWidgets.QMessageBox.information(self, "Cricket Team Rule Violation", "Team should have one Wicket Keeper")
                return -1
            self.mainUi.bowVal.setText(self._translate(str(self), " : "+str(int(self.mainUi.bowVal.text()[3:])+1)))

        elif self.players[curPlayer][0]=="AR":
            print("AR selected")
            if self.totalSelected>=10 and not self.players["__WK_lock__"]:
                QtWidgets.QMessageBox.information(self, "Cricket Team Rule Violation", "Team should have one Wicket Keeper")
                return -1
            self.mainUi.arVal.setText(self._translate(str(self), " : "+str(int(self.mainUi.arVal.text()[3:])+1)))

        elif self.players[curPlayer][0]=="WK":
            print("WK selected")
            if self.players["__WK_lock__"]:
                QtWidgets.QMessageBox.information(self, "Multiple WK", "Cannot select more than one Wicket Keeper")
                return -1
            self.mainUi.wkVal.setText(self._translate(str(self), " : "+str(int(self.mainUi.wkVal.text()[3:])+1)))    
            self.players["__WK_lock__"]=True

        self.totalSelected+=1;

        if not opn:
            self.mainUi.selection_list.takeItem(self.mainUi.selection_list.row(selectedPlayerItem))
            self.mainUi.result_list.addItem(selectedPlayerItem.text())
        elif opn:
            self.mainUi.result_list.addItem(" "*4+curPlayer)

        self.players[curPlayer][1]=False
        self.updatePoints(val=self.players[curPlayer][2])

    def deselectPlayer(self):
        if not self.mainUi.result_list.selectedItems(): return
        for item in self.mainUi.result_list.selectedItems():
            selectedPlayerItem=item
        self.mainUi.result_list.takeItem(self.mainUi.result_list.row(selectedPlayerItem))

        curPlayer=selectedPlayerItem.text()[4:]

        if self.players[curPlayer][0]=="BAT":
            print("BAT DEselected")
            self.mainUi.batVal.setText(self._translate(str(self), " : "+str(int(self.mainUi.batVal.text()[3:])-1)))
        elif self.players[curPlayer][0]=="BWL":
            print("BOW DEselected")
            self.mainUi.bowVal.setText(self._translate(str(self), " : "+str(int(self.mainUi.bowVal.text()[3:])-1)))
        elif self.players[curPlayer][0]=="AR":
            print("AR DEselected")
            self.mainUi.arVal.setText(self._translate(str(self), " : "+str(int(self.mainUi.arVal.text()[3:])-1)))
        elif self.players[curPlayer][0]=="WK":
            print("WK DEselected")
            self.mainUi.wkVal.setText(self._translate(str(self), " : "+str(int(self.mainUi.wkVal.text()[3:])-1)))   
            self.players["__WK_lock__"]=False 

        self.totalSelected-=1;

        self.players[curPlayer][1]=True
        self.updatePoints(do="<",val=self.players[curPlayer][2])

    def baseSetup(self,radio=True,setopen=False):
        self.mainUi.BAT.setEnabled(radio)
        self.mainUi.BOW.setEnabled(radio)
        self.mainUi.AR.setEnabled(radio)
        self.mainUi.WK.setEnabled(radio)

        self.mainUi.batVal.setText(self._translate(str(self), " : "+str(0)))
        self.mainUi.bowVal.setText(self._translate(str(self), " : "+str(0)))
        self.mainUi.arVal.setText(self._translate(str(self), " : "+str(0)))
        self.mainUi.wkVal.setText(self._translate(str(self), " : "+str(0)))

        self.setupPoints()
        self.mainUi.result_list.clear()
        self.mainUi.selection_list.clear()
        self.curPlayer=''

    def playersSetup(self):
        dbCur.execute("select player,CTG,value from stats")
        self.players={}
        self.totalSelected=0
        for each in dbCur.fetchall():
            self.players[each[0]]=[each[1],True,each[2]]
        self.players["__WK_lock__"]=False


        
class newTeamControl(QtWidgets.QDialog):
    def __init__(self, parent = None):
        print(type(self))
        print("newTeamControl")
        QtWidgets.QDialog.__init__(self, parent)
        self.newTeamdlgUi=Ui_NEWTeamDialog()
        self.newTeamdlgUi.setupUi(self)
        self.teamNameTxt=""

        self.newTeamdlgUi.buttonBox.accepted.connect(self.getText)
        self.newTeamdlgUi.buttonBox.rejected.connect(self.reject)

    def getText(self):
        print("getText")
        
        self.teamNameTxt=self.newTeamdlgUi.lineEdit.text()
        if(len(self.teamNameTxt)==0):
            QtWidgets.QMessageBox.warning(self, "Warning", "Team name cannot be empty !")
            self.reject()
        else:
            MainApp.mainUi.teamNameVal.setText(MainApp._translate(str(self), self.teamNameTxt))

        print(self.teamNameTxt)
        MainApp.baseSetup()
        MainApp.playersSetup()
        self.accept()
        return


class evalControl(QtWidgets.QDialog):
    def __init__(self, parent = None):
        import re
        print(type(self))
        print("evalControl")
        QtWidgets.QDialog.__init__(self, parent)
        self.evaldlgUi=Ui_EVALUATETeamDialog()
        self.evaldlgUi.setupUi(self)

        self.evaldlgUi.comboBox.addItem("Select Team")
        self.evaldlgUi.comboBox_2.addItem("Select Maches")
        self.evaldlgUi.pushButton.clicked.connect(self.evaluate)
        # self.evaldlgUi.listWidget.sc


        dbCur.execute("Select distinct name from teams")
        for each in dbCur.fetchall():
            self.evaldlgUi.comboBox.addItem(each[0])
            

        dbCur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        for each in dbCur.fetchall():
            if re.search(".*match.*", each[0], re.I):
                self.evaldlgUi.comboBox_2.addItem(each[0])


    def evaluate(self):
        self.evaldlgUi.listWidget.clear()
        self.evaldlgUi.listWidget_2.clear()

        print("evaluating...")
        curTeam=self.evaldlgUi.comboBox.currentText()
        if(curTeam=="Select Team"):
            QtWidgets.QMessageBox.information(self, "Warning", "Select a team !")
            return
        curMatch=self.evaldlgUi.comboBox_2.currentText()
        if(curMatch=="Select Maches"):
            QtWidgets.QMessageBox.information(self, "Warning", "Select a Match !")
            return
        

        dbCur.execute("select players from teams where name==?",(curTeam,))
        teamPoint=0

        for each in dbCur.fetchall():
            self.evaldlgUi.listWidget.addItem(" "*4+each[0])
            dbCur.execute("select scored,faced,fours,sixes,bowed,given,wkts,catches,stumping,RO from "+curMatch+" where player=='"+each[0]+"'")
            plyrpoint=self.evalPoints(dbCur.fetchall())
            self.evaldlgUi.listWidget_2.addItem(" "+str(plyrpoint))
            teamPoint+=plyrpoint


        self.evaldlgUi.pointsVal.setText(MainApp._translate(str(self), str(teamPoint)))



    def evalPoints(self,plyrmachRec):
        scored,faced,fours,sixes,bowed,given,wkts,catches,stumping,RO=plyrmachRec[0]

        plyrPoint=0
        if scored>0:
            srate=scored/faced
            if srate>0.8: plyrPoint+=2
            if srate>1: plyrPoint+=4
        if bowed>0:
            eco=given/(bowed/6)
            if eco>3.5 and eco<=4.5: plyrPoint+=4
            elif eco>2 and eco<=3.5: plyrPoint+=7
            elif eco<=2 : plyrPoint+=10

        plyrPoint+=((scored//2)+(scored//50)*5+(scored//100)*10+wkts*10+(wkts//3)*5+(wkts//5)*10+catches*10+stumping*10+RO*10)

        return plyrPoint




if __name__ == "__main__":
    dbConn=sqlite3.connect("cricket1.db")
    dbCur=dbConn.cursor()
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainApp = MainControl()
    MainApp.show()
    sys.exit(app.exec_())
        
    


