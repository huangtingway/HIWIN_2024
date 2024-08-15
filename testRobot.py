import HIWIN_Python
import time
import serial

speedRate=80
WORK_TABLE_HEIGHT= -20 #桌面絕對高度
EXTEND_TABLE_HEIGHT= -260 #延伸檯面絕對高度
START_BUTTON_IO_INDEX = 9
SLOT_IO_INDEX = [9,10,11] #IO

COM_PORT = 'COM7'
BAUD_RATES = 9600
IP = "192.168.0.2"

HOME_POS = [0.0   ,368.0  ,293.5  ,180.0  ,0.0  ,90.0] #原點位置
READY_POS = [0.0   ,470.0  ,180.0  ,180.0  ,0.0  ,90.0] #預備位置

#分揀參數
GET_CUBE_STEP = 65 #取料步伐
GET_CUBE_YOFFSET = 80 #取料Y軸偏移

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

STACK_POS = [[360.0   ,205.0  ,WORK_TABLE_HEIGHT + 90,180.0  ,0.0  ,270.0],
            [360.0   ,320.0  ,WORK_TABLE_HEIGHT + 90,180.0  ,0.0  ,270.0],
            [360.0   ,440.0  ,WORK_TABLE_HEIGHT + 90,180.0  ,0.0  ,270.0],
            [-17.0   ,290.0  ,WORK_TABLE_HEIGHT + 90,180.0  ,0.0  ,270.0]] 

TEST_POS1 = [-343.0 ,254.0  ,WORK_TABLE_HEIGHT + 80  ,180.0  ,0.0  ,180.0] #測試位置(右上)
TEST_POS2 = [-343.0 ,583.0  ,WORK_TABLE_HEIGHT + 50  ,180.0  ,0.0  ,180.0] #測試位置(右下)
TEST_POS3 = [310.0  ,617.0  ,WORK_TABLE_HEIGHT + 50  ,180.0  ,0.0  ,270.0] #測試位置(左下)
TEST_POS4 = [360.0  ,205.0  ,WORK_TABLE_HEIGHT + 80  ,180.0  ,0.0  ,270.0] #測試位置(左上)

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

    print(f"  Move rel ({position[0]},{position[1]},{position[2]})")

def move_axis(s ,  mode , position):
    if (mode == 'PTP'):
        HIWIN_Python.ptp_axis_edited(s,1,*position)
        while HIWIN_Python.get_motion_state(s) != 1:
            time.sleep(0.1)
        time.sleep(0.1)

    print(f"  Move rel ({position[0]},{position[1]},{position[2]})")

def init():
    s=HIWIN_Python.connect_robot(IP,1) #連線
    HIWIN_Python.clear_alarm(s)
    time.sleep(0.2)

    HIWIN_Python.set_connection_level(s,1)
    HIWIN_Python.set_operation_mode(s,0) #0自動,1手動
    HIWIN_Python.set_motor_state(s,1) #啟動馬達
    time.sleep(0.2)

    #設定速度
    HIWIN_Python.set_acc_dec_ratio(s,100)
    HIWIN_Python.set_lin_speed_edited(s,650)#設定直線運動速度- int set_lin_speed(HROBOT robot, double value),value=mm/s
    HIWIN_Python.set_ptp_speed(s,speedRate)#設定直線運動速度- int set_lin_speed(HROBOT robot, double value),value=mm/s

    #設定移動%
    HIWIN_Python.set_override_ratio(s,speedRate) #設定整體速度 int set_override_ratio(HROBOT robot, double value)#整體速度比例:1-100(%)
    time.sleep(0.2)

    move_abs(s ,  'PTP' , HOME_POS)
    return s

def testMove():
    input('按任意鍵開始移動測試')
    move_rel(s ,  'PTP' , (0,0,50,0,0,0))
    move_rel(s ,  'PTP' , (0,0,-50,0,0,0))
    move_rel(s ,  'PTP' , (0,50,0,0,0,0))
    move_rel(s ,  'PTP' , (0,-50,0,0,0,0))
    move_rel(s ,  'PTP' , (50,0,0,0,0,0))
    move_rel(s ,  'PTP' , (-50,0,0,0,0,0))
    print('V 移動測試完成\n')

def testIO():
    input('按任意鍵開始IO測試')
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[0], True) #開啟電磁閥
    time.sleep(0.5)
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[1], True) #開啟電磁閥
    time.sleep(0.5)
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[2], True) #開啟電磁閥
    time.sleep(0.8)

    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[0], False) #關閉電磁閥
    time.sleep(0.5)
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[1], False) #關閉電磁閥
    time.sleep(0.5)
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[2], False) #關閉電磁閥

    print('按下開始按鈕')

    while HIWIN_Python.get_digital_input(s,START_BUTTON_IO_INDEX) == 0: #等待按鈕
        time.sleep(0.1)
    
    print('V IO測試完成\n')

def testPos():
    input('按任鍵開始座標測試')
    HIWIN_Python.set_override_ratio(s,40)
    move_abs(s ,  'PTP' , TEST_POS1)
    HIWIN_Python.set_override_ratio(s,speedRate)
    input('按任意鍵繼續')
    
    move_abs(s ,  'PTP' , TEST_POS2)
    input('按任意鍵繼續')
    move_rel(s ,  'PTP' , (0,0,0,0,0,90))
    move_abs(s ,  'PTP' , TEST_POS3)
    input('按任意鍵繼續')
    move_abs(s ,  'PTP' , TEST_POS4)
    input('按任意鍵繼續')
    move_rel(s ,  'PTP' , (0,0,0,0,0,-90))
    move_abs(s ,  'PTP' , SORT_LARGE_POS)
    input('按任意鍵繼續')
    move_abs(s ,  'PTP' , SORT_MID_POS)
    input('按任意鍵繼續')
    move_abs(s ,  'PTP' , SORT_SMALL_POS)
    input('按任意鍵繼續')
    move_abs(s ,  'PTP' , STACK_POS[0])
    input('按任意鍵繼續')
    move_abs(s ,  'PTP' , STACK_POS[1])
    input('按任意鍵繼續')
    move_abs(s ,  'PTP' , STACK_POS[2])
    input('按任意鍵繼續')
    move_abs(s ,  'PTP' , STACK_POS[3])
    input('按任意鍵繼續')
    move_rel(s ,  'PTP' , (0,0,0,0,0,-90))
    move_rel(s ,  'PTP' , (0,0,0,0,0,-90))
    #move_axis(s ,  'PTP' , (0,-17,1.492,0,-73.6,0))
    
    move_abs(s ,  'PTP' , GET_CUBE_READY_POS) #延伸檯面
    input('按任意鍵繼續')
    HIWIN_Python.set_override_ratio(s,35)
    move_abs(s ,  'PTP' , GET_CUBE_POS)
    HIWIN_Python.set_override_ratio(s,speedRate)
    input('按任意鍵繼續')
    move_rel(s ,  'PTP' , (0,GET_CUBE_YOFFSET,0,0,0,0))
    input('按任意鍵繼續')
    move_rel(s ,  'PTP' , (0,GET_CUBE_YOFFSET,0,0,0,0))
    input('按任意鍵繼續')
    move_rel(s ,  'PTP' , (0,GET_CUBE_YOFFSET,0,0,0,0))
    input('按任意鍵繼續')

    print('V 座標測試結束\n')

def testGrab():
    global grab
    input('按任鍵開始夾爪測試')
    move_abs(s ,  'PTP' , GET_CUBE_READY_POS)
    move_abs(s ,  'PTP' , GET_CUBE_POS)

    while True:
        grab.write(b'clear\n')
        HIWIN_Python.set_override_ratio(s,10)
        move_rel(s ,  'PTP' , (0,0,GET_CUBE_STEP*-1,0,0,0))
        HIWIN_Python.set_override_ratio(s,speedRate)
        grab.write(b'getType\n')
        time.sleep(0.1)
        data_raw = grab.readline()  # 讀取一行
        data = data_raw.decode()   # 用預設的UTF-8解碼
        print(data)
        move_rel(s ,  'PTP' , (0,0,GET_CUBE_STEP,0,0,0))

        command = input('按任鍵繼續, 按Q離開：')
        if command == 'Q' or command == 'q':
            break
    
    grab.write(b'clear\n')
    grab.write(b'blink\n')
    time.sleep(1)
    print('V 夾爪測試完成\n')

def testGetPut():
    input('按任鍵開始取料測試')
    move_abs(s ,  'PTP' , GET_CUBE_POS)
    
    HIWIN_Python.set_override_ratio(s,20)
    move_rel(s ,  'PTP' , (0,0,GET_CUBE_STEP*-1,0,0,0))
    HIWIN_Python.set_override_ratio(s,speedRate)
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[0], True) # Open slot IO 1#啟動電磁閥
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[1], True) # Open slot IO 2
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[2], True) # Open slot IO 3
    time.sleep(0.3)
    move_rel(s ,  'PTP' , (0,0,GET_CUBE_STEP,0,0,0))

    move_abs(s ,  'PTP' , GET_CUBE_READY_POS)
    move_abs(s ,  'PTP' , PLACE_READY_POS)
    move_rel(s ,  'PTP' , (0,0,0,0,0,90))

    placeOffset = 105
    HIWIN_Python.set_override_ratio(s,15)
    move_rel(s ,  'PTP' , (0,0,-placeOffset,0,0,0))
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[0], False) 
    HIWIN_Python.set_override_ratio(s,speedRate)
    move_rel(s ,  'PTP' , (0,0,placeOffset,0,0,0))
    
    placeOffset = 120
    HIWIN_Python.set_override_ratio(s,15)
    move_rel(s ,  'PTP' , (0,0,-placeOffset,0,0,0))
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[1], False) 
    HIWIN_Python.set_override_ratio(s,speedRate)
    move_rel(s ,  'PTP' , (0,0,placeOffset,0,0,0))
    
    placeOffset = 140
    HIWIN_Python.set_override_ratio(s,15)
    move_rel(s ,  'PTP' , (0,0,-placeOffset,0,0,0))
    HIWIN_Python.set_digital_output(s, SLOT_IO_INDEX[2], False) 
    HIWIN_Python.set_override_ratio(s,speedRate)
    move_rel(s ,  'PTP' , (0,0,placeOffset,0,0,0))
    
    move_rel(s ,  'PTP' , (0,0,0,0,0,-90))
    HIWIN_Python.set_override_ratio(s,speedRate)
    print('V 取料測試完成\n')
    
if __name__=='__main__':
    global grab
    grab = serial.Serial(COM_PORT, BAUD_RATES) #夾爪通訊
    s = init()
    time.sleep(2)
    input('預備執行任務，請按任意鍵繼續')
    move_abs(s ,  'PTP' , READY_POS)

    #testMove()
    #testIO()
    testPos()
    testGrab()
    testGetPut()
    
    move_abs(s ,  'PTP' , HOME_POS)
    grab.close()
    HIWIN_Python.disconnect(s)