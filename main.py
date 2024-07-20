import HIWIN_Python
import time
import serial
import os
import ctypes
import gui

speedRate=20
groundZ=-193.5 #桌面絕對高度
GET_CUBE_STEP = 50 #取料步伐
PUT_CUBE_STEP = 50 #分揀放料步伐
GET_CUBE_YOFFSET = 50 #取料Y軸偏移
PUT_CUBE_SMALL_XOFFSET = 50 #放料小X軸偏移
PUT_CUBE_MID_XOFFSET = 50 #放料中X軸偏移
PUT_CUBE_LARGE_XOFFSET = 50 #放料大X軸偏移
GRAB_UNIT_OFFSET = 90 #夾爪單位偏移
LARGE_CUBE_SIZE = 70 #大方塊尺寸
MID_CUBE_SIZE = 50 #中方塊尺寸
SMALL_CUBE_SIZE = 30 #小方塊尺寸

HOME_POS = [0.0   ,368.0  ,293.5  ,-180.0  ,0.0  ,90.0] #原點位置
READY_POS = [0.0   ,420.0  ,345.0  ,-180.0  ,0.0  ,95.0] #預備位置
PLACE_READY_POS = [0.0   ,420.0  ,345.0  ,-180.0  ,0.0  ,95.0] #分揀預備位置
GET_CUBE_POS = [0.0   ,420.0  ,345.0  ,-180.0  ,0.0  ,95.0] #來料位置
SORT_LARGE_POS = [0.0   ,420.0  ,345.0  ,-180.0  ,0.0  ,95.0] #分揀位置(大)
SORT_MID_POS = [0.0   ,420.0  ,345.0  ,-180.0  ,0.0  ,95.0] #分揀位置(中)
SORT_SMALL_POS = [0.0   ,420.0  ,345.0  ,-180.0  ,0.0  ,95.0] #分揀位置(小)
GET_LARGE_POS = [0.0   ,420.0  ,345.0  ,-180.0  ,0.0  ,95.0] #取料位置(大)
GET_MID_POS = [0.0   ,420.0  ,345.0  ,-180.0  ,0.0  ,95.0] #取料位置(中)
GET_SMALL_POS = [0.0   ,420.0  ,345.0  ,-180.0  ,0.0  ,95.0] #取料位置(小)
STACK_POS = [[0.0   ,420.0  ,345.0  ,-180.0  ,0.0  ,95.0], #裝疊位置
             [0.0   ,420.0  ,345.0  ,-180.0  ,0.0  ,95.0],
             [0.0   ,420.0  ,345.0  ,-180.0  ,0.0  ,95.0],
             [0.0   ,420.0  ,345.0  ,-180.0  ,0.0  ,95.0]] 


isSubmitOrder = False
stackOrder = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]] #[large,mid,small]

COM_PORT = 'COM6'
BAUD_RATES = 9600

def init():
    s=HIWIN_Python.connect_robot("127.0.0.1",1) #連線
    HIWIN_Python.clear_alarm(s)
    time.sleep(0.5)

    HIWIN_Python.set_connection_level(s,1)
    HIWIN_Python.set_operation_mode(s,0) #0自動,1手動

    #設定速度
    HIWIN_Python.set_lin_speed_edited(s,50) #設定直線運動速度 int set_lin_speed(HROBOT robot, double value),value=mm/s
    HIWIN_Python.set_ptp_speed(s,speedRate) #設定直線運動速度 int set_lin_speed(HROBOT robot, double value),value=mm/s
    #設定移動%
    HIWIN_Python.set_override_ratio(s,speedRate) #設定整體速度 int set_override_ratio(HROBOT robot, double value)#整體速度比例:1-100(%)
    move_abs(s ,  'PTP' , HOME_POS)
    return s

#絕對移動
def move_abs(s ,  mode , position):
    if (mode == 'PTP'):
        HIWIN_Python.ptp_pos_edited(s,1,*position)
        while HIWIN_Python.get_motion_state(s) != 1:
            time.sleep(0.1)
        time.sleep(0.1)

    if (mode == 'LIN'):
        HIWIN_Python.lin_pos_edited(s,0,0.0,*position)
        while HIWIN_Python.get_motion_state(s) != 1:
            time.sleep(0.1)
        time.sleep(0.1)

    print(f"Move abs ({position[0]},{position[1]},{position[2]})")

#相對移動
def move_rel(s ,  mode , position):
    if (mode == 'PTP'):
        HIWIN_Python.ptp_rel_pos_edited(s,1,*position)
        while HIWIN_Python.get_motion_state(s) != 1:
            time.sleep(0.1)
        time.sleep(0.1)

    if (mode == 'LIN'):
        array = (ctypes.c_double * len(position))(*position)
        HIWIN_Python.lin_rel_pos(s,0,0,array)
        while HIWIN_Python.get_motion_state(s) != 1:
            time.sleep(0.1)
        time.sleep(0.1)
    
    print(f"Move rel ({position[0]},{position[1]},{position[2]})")

def getCubeType():
    pass

def getSourceCube():
    move_rel(s,'PTP',(0,0,GET_CUBE_STEP*-1,0,0,0)) #放下夾爪
    cubeType = getCubeType() #取得方塊類型
    #(啟動電磁閥)
    move_rel(s,'PTP',(0,0,GET_CUBE_STEP,0,0,0)) #抬起夾爪
    return cubeType

def getSortedCube(cubeType, totalneed): #for stack
    grabSlot = [False,False,False] #夾爪是否有方塊

    if totalneed == 0: return grabSlot

    if cubeType == 'LARGE':
        move_abs(s,'PTP',GET_LARGE_POS)
        GET_LARGE_POS[0] += GRAB_UNIT_OFFSET*3 #下一個取料位置

    elif cubeType[j] == 'MID':
        move_abs(s,'PTP',GET_MID_POS)
        GET_MID_POS[0] += GRAB_UNIT_OFFSET*3 #下一個取料位置

    elif cubeType[j] == 'SMALL':
        move_abs(s,'PTP',GET_SMALL_POS)
        GET_SMALL_POS[0] += GRAB_UNIT_OFFSET*3 #下一個取料位置

    move_rel(s,'PTP',(0,0,-60,0,0,0)) #放下夾爪

    if totalneed == 1:
        grabSlot = [True,False,False]
        #(啟動電磁閥)
    elif totalneed == 2:
        grabSlot = [True,True,False]
        #(啟動電磁閥)
    else:
        grabSlot = [True,True,True]
        #(啟動電磁閥)
    
    move_rel(s,'PTP',(0,0,60,0,0,0)) #抬起夾爪
    
    return grabSlot

def placeSourceCube(cubeType):
    moveOffset = 0

    if cubeType == 'LARGE':
       moveOffset = 80
    elif cubeType[j] == 'MID':
       moveOffset = 60
    elif cubeType[j] == 'SMALL':
        moveOffset = 40

    move_rel(s,'PTP',(0,0,-moveOffset,0,0,0)) #放下夾爪
    #(關閉電磁閥)
    move_rel(s,'PTP',(0,0,moveOffset,0,0,0)) #抬起夾爪

def placeSortedCube(cubeType, slotNumber): #for stack
    move_rel(s,'PTP',(GRAB_UNIT_OFFSET*(slotNumber-1),0,0,0,0,0)) #夾爪偏移
    moveOffset = 0

    if cubeType == 'LARGE':
       moveOffset = 60
    elif cubeType[j] == 'MID':
        moveOffset = 40
    elif cubeType[j] == 'SMALL':
        moveOffset = 20

    move_rel(s,'PTP',(0,0,-moveOffset,0,0,0)) #放下夾爪
    #(關閉電磁閥)
    move_rel(s,'PTP',(0,0,moveOffset,0,0,0)) #抬起夾爪


#MAIN=========================================================================================================
if __name__=='__main__':
    #grab = serial.Serial(COM_PORT, BAUD_RATES) #夾爪通訊
    time.sleep(2)
    s = init()

    input('預備執行任務，請按任意鍵繼續')
    move_abs(s ,  'PTP' , READY_POS)
    input('開始執行任務，請按任意鍵繼續')

    #分揀-----------------------------------------------------------------------------------------------
    for i in range(4):
        move_abs(s,'PTP',GET_CUBE_POS) #移動至取料位置
        cubeType = getSourceCube()
        cubeType = ['LARGE','MID','SMALL']
        move_abs(s,'PTP',PLACE_READY_POS) #移動至分揀位置

        for j in range(3): #分揀
            if cubeType[j] == 'LARGE':
                move_abs(s,'PTP',SORT_LARGE_POS)
                move_rel(s,'PTP',(GRAB_UNIT_OFFSET*(j-1),0,0,0,0,0)) #夾爪偏移
                placeSourceCube('LARGE')
                SORT_LARGE_POS[0] += PUT_CUBE_LARGE_XOFFSET #下一個放料位置

            elif cubeType[j] == 'MID':
                move_abs(s,'PTP',SORT_MID_POS)
                move_rel(s,'PTP',(GRAB_UNIT_OFFSET*(j-1),0,0,0,0,0)) #夾爪偏移
                placeSourceCube('MID')
                SORT_MID_POS[0] += PUT_CUBE_MID_XOFFSET #下一個放料位置

            elif cubeType[j] == 'SMALL':
                move_abs(s,'PTP',SORT_SMALL_POS)
                move_rel(s,'PTP',(GRAB_UNIT_OFFSET*(j-1),0,0,0,0,0)) #夾爪偏移
                placeSourceCube('SMALL')
                SORT_SMALL_POS[0] += PUT_CUBE_SMALL_XOFFSET #下一個放料位置

        GET_CUBE_POS[1] += GET_CUBE_YOFFSET #下一個取料位置
    
    move_abs(s,'PTP',READY_POS) #回到預備位置
    gui.show_form()

    while gui.isSubmitOrder != True:
        time.sleep(0.1)

    #裝疊-----------------------------------------------------------------------------------------------
    stackOrder = gui.stackOrder
    totalNeedCube = [0,0,0] #總共需要的方塊數[large,mid,small]
    print(stackOrder)

    for i in range(4):
        for j in range(3):
            totalNeedCube[j] += stackOrder[i][j]
    
    print(totalNeedCube)

    grabSlot = [False,False,False] #夾爪是否有方塊
    
    for i in range(4):
        if stackOrder[i][0] == 0: continue

        while stackOrder[i][0] > 0:
            if all(not slot for slot in grabSlot): #夾爪沒有方塊
                grabSlot = getSortedCube('LARGE',totalNeedCube[0])

            move_abs(s,'PTP',STACK_POS[i])
            
            if grabSlot[0]: #夾爪有方塊
                placeSortedCube('LARGE',0)
                grabSlot[0] = False
            
            elif grabSlot[1]:
                placeSortedCube('LARGE',1)
                grabSlot[1] = False

            elif grabSlot[2]:
                placeSortedCube('LARGE',2)
                grabSlot[2] = False

            stackOrder[i][0] -= 1
            totalNeedCube[0] -= 1
            STACK_POS[i][2] += LARGE_CUBE_SIZE #下一個放料位置
            
    
    move_abs(s,'PTP',HOME_POS)#回原點位置
    HIWIN_Python.disconnect(s)#斷開連接