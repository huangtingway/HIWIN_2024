import HIWIN_Python
import time
import serial
import os
import ctypes
import gui

#基本參數
IP = "192.168.0.2"
speedRate= 100 #速度比例
putSpeedRate = 20 #放料速度比例
accRatio = 25 #加速度比例
getAccRatio = 12 #取料加速度比例
emptyAccRatio = 50 #空轉加速度比例
WORK_TABLE_HEIGHT= -20 #桌面絕對高度
EXTEND_TABLE_HEIGHT= -250 #延伸檯面絕對高度
GET_CUBE_STEP = 65 #取料步伐
GRAB_UNIT_OFFSET = 80 #夾爪單位偏移
LARGE_CUBE_SIZE = 70 #大方塊尺寸
MID_CUBE_SIZE = 55 #中方塊尺寸
SMALL_CUBE_SIZE = 30 #小方塊尺寸
SLOT_IO_INDEX = [9,10,11] #IO
START_BUTTON_IO_INDEX = 9 #按鈕IO
COM_PORT = 'COM7'
BAUD_RATES = 9600

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
READY_POS = [0.0   ,470.0  ,140.0  ,180.0  ,0.0  ,90.0] #預備位置
READY_AXIS = [0,-17,1.492,0,-73.6,0]

#分揀座標
GET_CUBE_READY_POS = [-550.0 ,-80.0  ,130.0                     ,180.0  ,0.0  ,90.0] #取料預備位置
GET_CUBE_POS =       [-550.0 ,-250.0 ,EXTEND_TABLE_HEIGHT + 90 ,180.0  ,0.0  ,90.0] #來料位置
PLACE_READY_POS =    [-343.0 ,254.0  ,WORK_TABLE_HEIGHT + 160  ,180.0  ,0.0  ,90.0] #分揀預備位置
SORT_LARGE_ORG_POS = [-343.0 ,254.0  ,WORK_TABLE_HEIGHT + 160  ,180.0  ,0.0  ,180.0] #分揀位置原點(大)
SORT_MID_ORG_POS =   [-102.0  ,349.0  ,WORK_TABLE_HEIGHT + 160  ,180.0  ,0.0  ,180.0] #分揀位置原點(中)
SORT_SMALL_ORG_POS = [109.0  ,316.0  ,WORK_TABLE_HEIGHT + 160  ,180.0  ,0.0 , 180.0] #分揀位置原點(小)

SORT_LARGE_POS = SORT_LARGE_ORG_POS.copy()
SORT_MID_POS = SORT_MID_ORG_POS.copy()
SORT_SMALL_POS = SORT_SMALL_ORG_POS.copy()

#裝疊座標
STACK_ORG_POS = [[360.0   ,205.0  ,WORK_TABLE_HEIGHT + 160,180.0  ,0.0  ,270.0],
                [360.0   ,320.0  ,WORK_TABLE_HEIGHT + 160,180.0  ,0.0  ,270.0],
                [360.0   ,440.0  ,WORK_TABLE_HEIGHT + 160,180.0  ,0.0  ,270.0],
                [-17.0   ,290.0  ,WORK_TABLE_HEIGHT + 160,180.0  ,0.0  ,270.0]] 

STACK_POS = [[360.0   ,205.0  ,WORK_TABLE_HEIGHT + 90,180.0  ,0.0  ,270.0],
            [360.0   ,320.0  ,WORK_TABLE_HEIGHT + 90,180.0  ,0.0  ,270.0],
            [360.0   ,440.0  ,WORK_TABLE_HEIGHT + 90,180.0  ,0.0  ,270.0],
            [-17.0   ,290.0  ,WORK_TABLE_HEIGHT + 90,180.0  ,0.0  ,270.0]] 

isSubmitOrder = False
stackOrder = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]] #[large,mid,small]

def init():
    s=HIWIN_Python.connect_robot(IP,1) #連線
    HIWIN_Python.clear_alarm(s)
    time.sleep(0.2)

    HIWIN_Python.set_connection_level(s,1)
    HIWIN_Python.set_operation_mode(s,1) #0自動,1手動
    HIWIN_Python.set_motor_state(s,1) #啟動馬達
    time.sleep(0.2)

    #設定速度
    HIWIN_Python.set_acc_dec_ratio(s,accRatio) #設定加減速比例
    # HIWIN_Python.set_lin_speed_edited(s,650)#設定直線運動速度- int set_lin_speed(HROBOT robot, double value),value=mm/s
    # HIWIN_Python.set_ptp_speed(s,speedRate)#設定直線運動速度- int set_lin_speed(HROBOT robot, double value),value=mm/s

    #設定移動%
    HIWIN_Python.set_override_ratio(s,speedRate) #設定整體速度 int set_override_ratio(HROBOT robot, double value)#整體速度比例:1-100(%)
    time.sleep(0.2)

    move_abs(s ,  'PTP' , HOME_POS)
    return s

#絕對移動
def move_abs(s ,  mode , position):
    if (mode == 'PTP'):
        HIWIN_Python.ptp_pos_edited(s,1,*position)
        while HIWIN_Python.get_motion_state(s) != 1:
            time.sleep(0.05)
        time.sleep(0.01)

    if (mode == 'LIN'):
        HIWIN_Python.lin_pos_edited(s,0,0.0,*position)
        while HIWIN_Python.get_motion_state(s) != 1:
            time.sleep(0.05)
        time.sleep(0.01)

    print(f"  Move abs ({position[0]},{position[1]},{position[2]})")

#絕對移動
def move_abs_offset(s ,  mode , position, x_offset, y_offset):
    position[0] += x_offset
    position[1] += y_offset

    if (mode == 'PTP'):
        HIWIN_Python.ptp_pos_edited(s,1,*position)
        while HIWIN_Python.get_motion_state(s) != 1:
            time.sleep(0.05)
        time.sleep(0.01)

    if (mode == 'LIN'):
        HIWIN_Python.lin_pos_edited(s,0,0.0,*position)
        while HIWIN_Python.get_motion_state(s) != 1:
            time.sleep(0.05)
        time.sleep(0.01)

    print(f"  Move abs with offset ({position[0]},{position[1]},{position[2]})")

#相對移動
def move_rel(s ,  mode , position):
    if (mode == 'PTP'):
        HIWIN_Python.ptp_rel_pos_edited(s,1,*position)
        while HIWIN_Python.get_motion_state(s) != 1:
            time.sleep(0.05)
        time.sleep(0.01)

    if (mode == 'LIN'):
        array = (ctypes.c_double * len(position))(*position)
        HIWIN_Python.lin_rel_pos(s,0,0,array)
        while HIWIN_Python.get_motion_state(s) != 1:
            time.sleep(0.05)
        time.sleep(0.01)
    
    print(f"  Move rel ({position[0]},{position[1]},{position[2]})")

#移動軸
def move_axis(s ,  mode , position):
    if (mode == 'PTP'):
        HIWIN_Python.ptp_axis_edited(s,1,*position)
        while HIWIN_Python.get_motion_state(s) != 1:
            time.sleep(0.01)
        time.sleep(0.01)

    print(f"  Move axis ({position[0]},{position[1]},{position[2]})")

def getCubeType():
    global grab
    grab.write(b'getType\n')
    time.sleep(0.05)

    data_raw = grab.readline()  # 讀取一行
    data = data_raw.decode()   # 用預設的UTF-8解碼
    data = data.split(' ')
    res = [data[2],data[1],data[0]]
    print('夾爪辨識：', res)
    return res

def getSourceCube():
    HIWIN_Python.set_override_ratio(s,putSpeedRate) #設定取料速度
    time.sleep(0.05)
    move_rel(s,'PTP',(0,0,-GET_CUBE_STEP,0,0,0)) #放下夾爪
    HIWIN_Python.set_override_ratio(s,speedRate) #恢復速度

    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[0], True) # Open slot IO 1#啟動電磁閥
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[1], True) # Open slot IO 2
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[2], True) # Open slot IO 3
    cubeType = getCubeType() #取得方塊類型

    HIWIN_Python.set_acc_dec_ratio(s,getAccRatio) #設定取料加速度
    time.sleep(0.3)
    move_rel(s,'PTP',(0,0,GET_CUBE_STEP + 70,0,0,0)) #抬起夾爪
    HIWIN_Python.set_acc_dec_ratio(s,accRatio) #恢復加速度
    time.sleep(0.1)
    return cubeType

def getSortedCube(cubeType, orgSlotNumber, requireStackCube, slotCubeType): #for stack
    moveOffset = 0
    getCubes = 0

    if cubeType == 'LARGE':
        moveOffset = 105

    elif cubeType == 'MID':
        moveOffset = 120

    elif cubeType == 'SMALL':
        moveOffset = 145

    HIWIN_Python.set_override_ratio(s,putSpeedRate) #設定取料速度
    time.sleep(0.05)
    move_rel(s,'PTP',(0,0,-moveOffset,0,0,0)) #放下夾爪
    HIWIN_Python.set_override_ratio(s,speedRate) #恢復速度

    for i in range(orgSlotNumber, -1, -1): #開啟電磁閥
        if requireStackCube > 0 and checkGetPosValid(cubeType, orgSlotNumber, i) == True:
            getCubes += 1
            requireStackCube -= 1
            slotCubeType[i] = cubeType
            HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[i], True) 
        else:
            break

    HIWIN_Python.set_acc_dec_ratio(s,getAccRatio) #設定取料加速度
    time.sleep(0.3)
    move_rel(s,'PTP',(0,0,moveOffset,0,0,0)) #抬起夾爪
    HIWIN_Python.set_acc_dec_ratio(s,accRatio) #恢復加速度
    time.sleep(0.1)
    return getCubes

def checkGetPosValid(cubeType, orginSlotNumber, targetSlotNumber):
    getAmount = orginSlotNumber - targetSlotNumber + 1
    vaildGetAmount = 0

    if cubeType == 'LARGE':
        vaildGetAmount = largePosCounter[1] + 1
    elif cubeType == 'MID':
        vaildGetAmount = midPosCounter[1] + 1
    elif cubeType == 'SMALL':
        vaildGetAmount = smallPosCounter[1] + 1

    if getAmount > vaildGetAmount:
        return False
    
    return True

def placeSourceCube(cubeType, slotNumber):
    moveOffset = 0
    placeCubes = 0

    if cubeType[slotNumber] == 'LARGE':
       moveOffset = 105
    elif cubeType[slotNumber] == 'MID':
       moveOffset = 120
    elif cubeType[slotNumber] == 'SMALL':
        moveOffset = 140

    HIWIN_Python.set_override_ratio(s,putSpeedRate) #設定放料速度
    time.sleep(0.05)
    move_rel(s,'PTP',(0,0,-moveOffset,0,0,0)) #放下夾爪
    HIWIN_Python.set_override_ratio(s,speedRate) #恢復速度

    for i in range(slotNumber, 3): #關閉電磁閥
        if cubeType[i] == cubeType[slotNumber] and checkPutPosValid(cubeType[slotNumber], slotNumber, i) == True:
            placeCubes += 1
            HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[i], False) 
        else:
            break
    
    HIWIN_Python.set_acc_dec_ratio(s,getAccRatio) #設定取料加速度
    time.sleep(0.1)
    move_rel(s,'PTP',(0,0,moveOffset,0,0,0)) #抬起夾爪
    HIWIN_Python.set_acc_dec_ratio(s,accRatio) #恢復加速度
    time.sleep(0.1)
    return placeCubes

def checkPutPosValid(cubeType, orginSlotNumber, targetSlotNumber):
    placeAmount = targetSlotNumber - orginSlotNumber + 1
    vaildPlaceAmount = 0

    if cubeType == 'LARGE':
        vaildPlaceAmount = 3 - largePosCounter[1] 
    elif cubeType == 'MID':
        vaildPlaceAmount = 3 - midPosCounter[1]
    elif cubeType == 'SMALL':
        vaildPlaceAmount = 3 - smallPosCounter[1]

    if placeAmount > vaildPlaceAmount:
        return False
    
    return True

def placeSortedCube(cubeType, slotNumber): #for stack
    downOffset = 0
    upOffset = 0

    if cubeType == 'LARGE':
        downOffset = 30
        upOffset = downOffset + LARGE_CUBE_SIZE
    elif cubeType == 'MID':
        downOffset = 45
        upOffset = downOffset + MID_CUBE_SIZE
    elif cubeType == 'SMALL':
        downOffset = 70
        upOffset = downOffset + SMALL_CUBE_SIZE

    HIWIN_Python.set_override_ratio(s,putSpeedRate) #設定放料速度
    time.sleep(0.05)
    move_rel(s,'PTP',(0,0,-downOffset,0,0,0)) #放下夾爪
    HIWIN_Python.set_override_ratio(s,speedRate) #恢復速度
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[slotNumber], False) #關閉電磁閥
    HIWIN_Python.set_acc_dec_ratio(s,getAccRatio) #設定取料加速度
    time.sleep(0.1)
    move_rel(s,'PTP',(0,0,upOffset,0,0,0)) #抬起夾爪
    HIWIN_Python.set_acc_dec_ratio(s,accRatio) #恢復加速度
    time.sleep(0.1)

def changeLargePos(offset):
    global largePosCounter

    if (largePosCounter[0] == 3 and offset == 1) or (largePosCounter[0] == -1 and offset == -1):
        print("Error: large cube overflow")
        os._exit(0)

    largePosCounter[1] += offset

    if largePosCounter[1] >= 3:
        largePosCounter[1] = 0
        largePosCounter[0] += 1

    if largePosCounter[1] < 0:
        largePosCounter[1] = 2
        largePosCounter[0] -= 1

    SORT_LARGE_POS[1] = SORT_LARGE_ORG_POS[1] + largePosCounter[1]*PUT_CUBE_LARGE_YOFFSET
    SORT_LARGE_POS[0] = SORT_LARGE_ORG_POS[0] + largePosCounter[0]*PUT_CUBE_LARGE_XOFFSET
    print(f"largePosCounter:{largePosCounter}")

def changeMidPos(offset):
    global midPosCounter

    if (midPosCounter[0] == 3 and offset == 1) or (midPosCounter[0] == -1 and offset == -1):
        print("Error: mid cube overflow")
        os._exit(0)

    midPosCounter[1] += offset

    if midPosCounter[1] >= 3:
        midPosCounter[1] = 0
        midPosCounter[0] += 1

    if midPosCounter[1] < 0:
        midPosCounter[1] = 2
        midPosCounter[0] -= 1

    SORT_MID_POS[1] = SORT_MID_ORG_POS[1] + midPosCounter[1]*PUT_CUBE_MID_YOFFSET
    SORT_MID_POS[0] = SORT_MID_ORG_POS[0] + midPosCounter[0]*PUT_CUBE_MID_XOFFSET
    print(f"midPosCounter:{midPosCounter}")

def changeSmallPos(offset):
    global smallPosCounter

    if (smallPosCounter[0] == 3 and offset == 1) or (smallPosCounter[0] == -1 and offset == -1):
        print("Error: small cube overflow")
        os._exit(0)

    smallPosCounter[1] += offset

    if smallPosCounter[1] >= 3:
        smallPosCounter[1] = 0
        smallPosCounter[0] += 1

    if smallPosCounter[1] < 0:
        smallPosCounter[1] = 2
        smallPosCounter[0] -= 1

    SORT_SMALL_POS[1] = SORT_SMALL_ORG_POS[1] + smallPosCounter[1]*PUT_CUBE_SMALL_YOFFSET
    SORT_SMALL_POS[0] = SORT_SMALL_ORG_POS[0] + smallPosCounter[0]*PUT_CUBE_SMALL_XOFFSET
    print(f"smallPosCounter:{smallPosCounter}")

def checkOrderVaild(order, orderNum):
    if sum(order) == 0 :
        print("Error: order is 0")
        return False
    
    if sum(order) > 3:
        print("Error: order overflow")
        return False
    
    return True

#MAIN=========================================================================================================
if __name__=='__main__':
    s = init() 
    global grab
    grab = serial.Serial(COM_PORT, BAUD_RATES) #夾爪通訊
    gui.show_form()

    while gui.isSubmitOrder != True: #等待輸入訂單
        time.sleep(0.05)

    while HIWIN_Python.get_digital_input(s,START_BUTTON_IO_INDEX) == 0: #等待按鈕
        time.sleep(0.05)

    grab.write(b'blink\n')
    time.sleep(0.2)

    #分揀-----------------------------------------------------------------------------------------------
    for i in range(4):
        print(f"-----------------------------\nget source cube {i}")
        HIWIN_Python.set_acc_dec_ratio(s,emptyAccRatio) #設定空轉速度
        time.sleep(0.05)
        move_abs(s,'PTP',GET_CUBE_READY_POS) #移動至取料預備位置
        move_abs(s,'PTP',GET_CUBE_POS) #移動至取料位置
        cubeType = getSourceCube()
        move_abs(s,'PTP',GET_CUBE_READY_POS) #移動至取料預備位置
        move_abs(s,'PTP',PLACE_READY_POS) #移動至分揀位置
        move_rel(s,'PTP',(0,0,0,0,0,90)) #轉90度
        
        placeCubes = 0 #放料數量

        for j in range(3): #分揀
            if placeCubes > 1: 
                placeCubes -= 1
                continue

            if cubeType[j] == 'LARGE':
                print(f"\nsort \'large\' cube slot:{j}")
                move_abs_offset(s,'PTP', SORT_LARGE_POS.copy(), 0, GRAB_UNIT_OFFSET*(1-j)) #移動至分揀位置
                placeCubes = placeSourceCube(cubeType,j)
                changeLargePos(placeCubes)

            elif cubeType[j] == 'MID':
                print(f"\nsort \'mid\' cube slot:{j}")
                move_abs_offset(s,'PTP',SORT_MID_POS.copy(), 0, GRAB_UNIT_OFFSET*(1-j)) #移動至分揀位置
                placeCubes = placeSourceCube(cubeType,j)
                changeMidPos(placeCubes)

            elif cubeType[j] == 'SMALL':
                print(f"\nsort \'small\' cube slot:{j}")
                move_abs_offset(s,'PTP',SORT_SMALL_POS.copy(), 0, GRAB_UNIT_OFFSET*(1-j)) #移動至分揀位置
                placeCubes = placeSourceCube(cubeType,j)
                changeSmallPos(placeCubes)

        GET_CUBE_POS[1] += GET_CUBE_YOFFSET #下一個取料位置
        move_rel(s,'PTP',(0,0,0,0,0,-90))
        grab.write(b'clear\n') #清除夾爪

    print(f"-----------------------------\nfinish sorting\n")
    HIWIN_Python.set_acc_dec_ratio(s,emptyAccRatio) #設定空轉速度
    time.sleep(0.05)
    move_abs(s,'PTP',HOME_POS) #回到預備位置
    changeLargePos(-1) #reset largePosCounter
    changeMidPos(-1) #reset midPosCounter
    changeSmallPos(-1) #reset smallPosCounter
    grab.write(b'blink\n') #夾爪閃爍
    time.sleep(0.2)

    #裝疊-----------------------------------------------------------------------------------------------
    stackOrder = gui.stackOrder
    
    for i in range(4): #iterate through 4 orders
        print(f"-----------------------------\nstart stackOrder {i}:{stackOrder[i]}")
        if(checkOrderVaild(stackOrder[i], i) == False): continue
        slotCubeType = ["NULL","NULL","NULL"]

        while sum(stackOrder[i]) > 0:
            getCubes = 0
            # 取得方塊
            for j in range(2, -1, -1):  # iterate through 3 slots
                if getCubes > 1:
                    getCubes -= 1
                    continue

                if stackOrder[i][0] > 0:
                    move_abs_offset(s, 'PTP', SORT_LARGE_POS.copy(), 0, GRAB_UNIT_OFFSET*(1-j)) #移動至分揀位置
                    getCubes = getSortedCube('LARGE', j, stackOrder[i][0], slotCubeType) #取得方塊
                    stackOrder[i][0] -= getCubes 
                    changeLargePos(-getCubes)
                    
                elif stackOrder[i][1] > 0:
                    move_abs_offset(s, 'PTP', SORT_MID_POS.copy(),0, GRAB_UNIT_OFFSET*(1-j)) #移動至分揀位置
                    getCubes = getSortedCube('MID', j, stackOrder[i][1], slotCubeType) #取得方塊
                    stackOrder[i][1] -= getCubes
                    changeMidPos(-getCubes) #更新位置

                elif stackOrder[i][2] > 0:
                    move_abs_offset(s, 'PTP', SORT_SMALL_POS.copy(),0, GRAB_UNIT_OFFSET*(1-j)) #移動至分揀位置
                    getCubes = getSortedCube('SMALL', j, stackOrder[i][2], slotCubeType) #取得方塊
                    stackOrder[i][2] -= getCubes
                    changeSmallPos(-getCubes) #更新位置

            move_rel(s,'PTP',(0,0,0,0,0,90))
            move_abs(s, 'PTP', STACK_ORG_POS[i]) #移動至裝疊位置

            # 放置方塊
            for j in range(2, -1, -1):
                move_abs_offset(s,'PTP',STACK_POS[i].copy(), GRAB_UNIT_OFFSET*(j-1), 0) #移動至裝疊位置

                if slotCubeType[j] == 'LARGE':
                    placeSortedCube('LARGE', j)
                    STACK_POS[i][2] += LARGE_CUBE_SIZE #更新高度
                    
                elif slotCubeType[j] == 'MID':
                    placeSortedCube('MID', j)
                    STACK_POS[i][2] += MID_CUBE_SIZE #更新高度

                elif slotCubeType[j] == 'SMALL':
                    placeSortedCube('SMALL', j)
                    STACK_POS[i][2] += SMALL_CUBE_SIZE #更新高度

            HIWIN_Python.set_acc_dec_ratio(s,emptyAccRatio) #設定空轉速度
            time.sleep(0.05)
            move_rel(s,'PTP',(0,0,0,0,0,-90))
            slotCubeType = ["NULL","NULL","NULL"] #reset slotCubeType
    
    print(f"-----------------------------\nfinish stacking\n")
   
    HIWIN_Python.set_acc_dec_ratio(s,emptyAccRatio) #設定空轉速度
    time.sleep(0.05)
    move_abs(s,'PTP',HOME_POS)#回原點位置 
    HIWIN_Python.disconnect(s)#斷開連接

    grab.write(b'blink\n') #夾爪閃爍
    time.sleep(2)
    grab.close()