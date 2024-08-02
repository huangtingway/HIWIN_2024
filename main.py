import HIWIN_Python
import time
import serial
import os
import ctypes
import gui

#基本參數
IP = "192.168.0.2"
speedRate= 80 #速度比例
#groundZ=-193.5 #桌面絕對高度
GET_CUBE_STEP = 80 #取料步伐
#PUT_CUBE_STEP = 80 #分揀放料步伐
GRAB_UNIT_OFFSET = 80 #夾爪單位偏移
LARGE_CUBE_SIZE = 70 #大方塊尺寸
MID_CUBE_SIZE = 55 #中方塊尺寸
SMALL_CUBE_SIZE = 30 #小方塊尺寸
SLOT_IO_INDEX = [9,10,11] #IO
START_BUTTON_IO_INDEX = 9 #按鈕IO

#分揀參數
GET_CUBE_YOFFSET = 80 #取料Y軸偏移

PUT_CUBE_SMALL_XOFFSET = 60 #放料小X軸偏移
PUT_CUBE_MID_XOFFSET = 72.5 #放料中X軸偏移
PUT_CUBE_LARGE_XOFFSET = 80 #放料大X軸偏移

PUT_CUBE_SMALL_YOFFSET = 80 #放料小Y軸偏移
PUT_CUBE_MID_YOFFSET = 80 #放料中Y軸偏移
PUT_CUBE_LARGE_YOFFSET = 80 #放料大Y軸偏移

largePosCounter = [0,0] #(x,y)
midPosCounter = [0,0]
smallPosCounter = [0,0]

HOME_POS = [0.0   ,368.0  ,293.5  ,180.0  ,0.0  ,90.0] #原點位置
READY_POS = [0.0   ,470.0  ,130.0  ,180.0  ,0.0  ,90.0] #預備位置

#分揀座標
GET_CUBE_READY_POS = [-520.0   ,-60.0  ,60.0  ,180.0  ,0.0  ,90.0] #取料預備位置
GET_CUBE_POS = [-520.0   ,-200.0  ,-130.0  ,180.0  ,0.0  ,90.0] #來料位置
PLACE_READY_POS = [-320.0   ,414.0  ,130.0  ,180.0  ,0.0  ,180.0] #分揀預備位置
SORT_LARGE_POS = [-283.0   ,314.0  ,130.0  ,180.0  ,0.0  ,180.0] #分揀位置(大)
SORT_MID_POS = [-42.0   ,374.0  ,130.0  ,180.0  ,0.0  ,180.0] #分揀位置(中)
SORT_SMALL_POS = [134.0   ,351.0  ,130.0  ,180.0  ,0.0 , 180.0] #分揀位置(小)

#裝疊座標
STACK_POS = [[297.0   ,193.0  ,120.0  ,-180.0  ,0.0  ,90.0], #裝疊位置
             [297.0   ,273.0  ,120.0  ,-180.0  ,0.0  ,90.0],
             [297.0   ,353.0  ,120.0  ,-180.0  ,0.0  ,90.0],
             [297.0   ,433.0  ,120.0  ,-180.0  ,0.0  ,90.0]] 


isSubmitOrder = False
stackOrder = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]] #[large,mid,small]

COM_PORT = 'COM6'
BAUD_RATES = 9600

def init():
    s=HIWIN_Python.connect_robot(IP,1) #連線
    HIWIN_Python.clear_alarm(s)
    time.sleep(0.3)

    HIWIN_Python.set_connection_level(s,1)
    HIWIN_Python.set_operation_mode(s,0) #0自動,1手動
    HIWIN_Python.set_motor_state(s,1) #啟動馬達
    time.sleep(0.3)

    #設定速度
    HIWIN_Python.set_acc_dec_ratio(s,100)
    HIWIN_Python.set_lin_speed_edited(s,650)#設定直線運動速度- int set_lin_speed(HROBOT robot, double value),value=mm/s
    HIWIN_Python.set_ptp_speed(s,speedRate)#設定直線運動速度- int set_lin_speed(HROBOT robot, double value),value=mm/s

    #設定移動%
    HIWIN_Python.set_override_ratio(s,speedRate) #設定整體速度 int set_override_ratio(HROBOT robot, double value)#整體速度比例:1-100(%)
    time.sleep(0.3)

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

    print(f"  Move abs ({position[0]},{position[1]},{position[2]})")

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
    
    print(f"  Move rel ({position[0]},{position[1]},{position[2]})")

def getCubeType():
    return
    global grab
    grab.write(b'getType\n')
    time.sleep(0.2)

    data_raw = grab.readline()  # 讀取一行
    data = data_raw.decode()   # 用預設的UTF-8解碼
    data = data.split(' ')
    print('夾爪辨識：', data)
    return data

def getSourceCube():
    move_rel(s,'PTP',(0,0,GET_CUBE_STEP*-1,0,0,0)) #放下夾爪
    cubeType = getCubeType() #取得方塊類型
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[0], True) # Open slot IO 1#啟動電磁閥
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[1], True) # Open slot IO 2
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[2], True) # Open slot IO 3
    time.sleep(0.1)
    move_rel(s,'PTP',(0,0,GET_CUBE_STEP,0,0,0)) #抬起夾爪
    return cubeType

def getSortedCube(cubeType, grabSlotNumber): #for stack
    moveOffset = 0
    move_rel(s,'PTP',(GRAB_UNIT_OFFSET*(1-grabSlotNumber),0,0,0,0,0)) #夾爪偏移

    if cubeType == 'LARGE':
        moveOffset = 80

    elif cubeType == 'MID':
        moveOffset = 100

    elif cubeType == 'SMALL':
        moveOffset = 125

    move_rel(s,'PTP',(0,0,-moveOffset,0,0,0)) #放下夾爪
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[grabSlotNumber], True) #開啟電磁閥
    move_rel(s,'PTP',(0,0,moveOffset,0,0,0)) #抬起夾爪

def placeSourceCube(cubeType, slotNumber):
    moveOffset = 0

    if cubeType == 'LARGE':
       moveOffset = 80
    elif cubeType == 'MID':
       moveOffset = 100
    elif cubeType == 'SMALL':
        moveOffset = 125

    move_rel(s,'PTP',(0,0,-moveOffset,0,0,0)) #放下夾爪
    HIWIN_Python.set_digital_output(s, slotNumber, False) #關閉電磁閥
    time.sleep(0.1)
    move_rel(s,'PTP',(0,0,moveOffset,0,0,0)) #抬起夾爪

def placeSortedCube(cubeType, slotNumber): #for stack
    move_rel(s,'PTP',(GRAB_UNIT_OFFSET*(1-slotNumber),0,0,0,0,0)) #夾爪偏移
    moveOffset = 0

    if cubeType == 'LARGE':
       moveOffset = 60
    elif cubeType == 'MID':
        moveOffset = 40
    elif cubeType == 'SMALL':
        moveOffset = 20

    move_rel(s,'PTP',(0,0,-moveOffset,0,0,0)) #放下夾爪
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[slotNumber], False) #關閉電磁閥
    time.sleep(0.1)
    move_rel(s,'PTP',(0,0,moveOffset,0,0,0)) #抬起夾爪

def changeLargePos(offset):
    global largePosCounter
    largePosCounter[1] += offset

    if largePosCounter[1] >= 3:
        largePosCounter[1] = 0
        largePosCounter[0] += 1

    if largePosCounter[1] < 0:
        largePosCounter[1] = 2
        largePosCounter[0] -= 1

    if largePosCounter[0] == 4 or largePosCounter[0] == -1:
        print("Error: large cube overflow")
        os._exit(0)

    SORT_LARGE_POS[1] = 314.0 + largePosCounter[1]*PUT_CUBE_LARGE_YOFFSET
    SORT_LARGE_POS[0] = -360.0 + largePosCounter[0]*PUT_CUBE_LARGE_XOFFSET
    print(f"largePosCounter:{largePosCounter}")

def changeMidPos(offset):
    global midPosCounter
    midPosCounter[1] += offset

    if midPosCounter[1] >= 3:
        midPosCounter[1] = 0
        midPosCounter[0] += 1

    if midPosCounter[1] < 0:
        midPosCounter[1] = 2
        midPosCounter[0] -= 1

    if midPosCounter[0] == 4 or midPosCounter[0] == -1:
        print("Error: mid cube overflow")
        os._exit(0)

    SORT_MID_POS[1] = 374.0 + midPosCounter[1]*PUT_CUBE_MID_YOFFSET
    SORT_MID_POS[0] = -42.0 + midPosCounter[0]*PUT_CUBE_MID_XOFFSET
    print(f"midPosCounter:{midPosCounter}")

def changeSmallPos(offset):
    global smallPosCounter
    smallPosCounter[1] += offset

    if smallPosCounter[1] >= 3:
        smallPosCounter[1] = 0
        smallPosCounter[0] += 1

    if smallPosCounter[1] < 0:
        smallPosCounter[1] = 2
        smallPosCounter[0] -= 1

    if smallPosCounter[0] == 4 or smallPosCounter[0] == -1:
        print("Error: small cube overflow")
        os._exit(0)

    SORT_SMALL_POS[1] = 351.0 + smallPosCounter[1]*PUT_CUBE_SMALL_YOFFSET
    SORT_SMALL_POS[0] = 134.0 + smallPosCounter[0]*PUT_CUBE_SMALL_XOFFSET
    print(f"smallPosCounter:{smallPosCounter}")

def checkOrderVaild(order):
    if sum(order) == 0 or sum(order) > 3:
        print("Error: invalid order")
        return False
    return True

#MAIN=========================================================================================================
if __name__=='__main__':
    gui.show_form()
    global grab
    #grab = serial.Serial(COM_PORT, BAUD_RATES) #夾爪通訊

    while gui.isSubmitOrder != True:
        time.sleep(0.1)
   
    s = init()
    #grab.write(b'blink\n')
    time.sleep(1.5)

    while HIWIN_Python.get_digital_input(s,START_BUTTON_IO_INDEX) == 0: #等待按鈕
        time.sleep(0.1)

    #分揀-----------------------------------------------------------------------------------------------
    for i in range(4):
        print(f"-----------------------------\nget source cube {i}")
        move_abs(s,'PTP',GET_CUBE_READY_POS) #移動至取料預備位置
        move_abs(s,'PTP',GET_CUBE_POS) #移動至取料位置
        cubeType = getSourceCube()
        cubeType = ['LARGE','MID','SMALL'] #for test
        move_abs(s,'PTP',GET_CUBE_READY_POS) #移動至取料預備位置
        move_abs(s,'PTP',PLACE_READY_POS) #移動至分揀位置
        
        for j in range(3): #分揀
            if cubeType[j] == 'LARGE':
                print(f"\nsort \'large\' cube slot:{j}")
                move_abs(s,'PTP',SORT_LARGE_POS)
                move_rel(s,'PTP',(0,GRAB_UNIT_OFFSET*(1-j),0,0,0,0)) #夾爪偏移
                placeSourceCube('LARGE',SLOT_IO_INDEX[j])
                changeLargePos(1) #下一個放料位置

            elif cubeType[j] == 'MID':
                print(f"\nsort \'mid\' cube slot:{j}")
                move_abs(s,'PTP',SORT_MID_POS)
                move_rel(s,'PTP',(0,GRAB_UNIT_OFFSET*(1-j),0,0,0,0)) #夾爪偏移
                placeSourceCube('MID',SLOT_IO_INDEX[j])
                changeMidPos(1) #下一個放料位置

            elif cubeType[j] == 'SMALL':
                print(f"\nsort \'small\' cube slot:{j}")
                move_abs(s,'PTP',SORT_SMALL_POS)
                move_rel(s,'PTP',(0,GRAB_UNIT_OFFSET*(1-j),0,0,0,0)) #夾爪偏移
                placeSourceCube('SMALL',SLOT_IO_INDEX[j])
                changeSmallPos(1) #下一個放料位置

        GET_CUBE_POS[1] += GET_CUBE_YOFFSET #下一個取料位置
        #grab.write(b'clear\n') #清除夾爪

    print(f"-----------------------------\nfinish sorting\n")
    move_abs(s,'PTP',HOME_POS) #回到預備位置
    #grab.write(b'blink\n') #夾爪閃爍
    time.sleep(2)

    #裝疊-----------------------------------------------------------------------------------------------
    stackOrder = gui.stackOrder
    
    for i in range(4): #iterate through 4 orders
        print(f"-----------------------------\nstart stackOrder {i}:{stackOrder[i]}")
        if(checkOrderVaild(stackOrder[i]) == False): continue
        slotCubeType = ["NULL","NULL","NULL"]

        while sum(stackOrder[i]) > 0:
            # 取得方塊
            for j in range(2, -1, -1):  # iterate through 3 slots
                if stackOrder[i][0] > 0:
                    move_abs(s, 'PTP', SORT_LARGE_POS)
                    getSortedCube('LARGE', j)
                    stackOrder[i][0] -= 1
                    changeLargePos(-1)
                    slotCubeType[j] = "LARGE"

                elif stackOrder[i][1] > 0:
                    move_abs(s, 'PTP', SORT_MID_POS)
                    getSortedCube('MID', j)
                    stackOrder[i][1] -= 1
                    changeMidPos(-1)
                    slotCubeType[j] = "MID"

                elif stackOrder[i][2] > 0:
                    move_abs(s, 'PTP', SORT_SMALL_POS)
                    getSortedCube('SMALL', j)
                    stackOrder[i][2] -= 1
                    changeSmallPos(-1)

            # 放置方塊
            for j in range(3):
                move_abs(s, 'PTP', STACK_POS[i])

                if slotCubeType[j] == 'LARGE':
                    placeSortedCube('LARGE', j)
                    STACK_POS[i][2] += LARGE_CUBE_SIZE
                elif slotCubeType[j] == 'MID':
                    placeSortedCube('MID', j)
                    STACK_POS[i][2] += MID_CUBE_SIZE
                elif slotCubeType[j] == 'SMALL':
                    placeSortedCube('SMALL', j)
                    STACK_POS[i][2] += SMALL_CUBE_SIZE
    
    print(f"-----------------------------\nfinish stacking\n")
   
    move_abs(s,'PTP',HOME_POS)#回原點位置 
    #grab.write(b'blink\n') #夾爪閃爍
    time.sleep(2)
    #grab.close()
    HIWIN_Python.disconnect(s)#斷開連接