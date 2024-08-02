import HIWIN_Python
import time
import serial

speedRate=50

HOME_POS = [0.0   ,368.0  ,293.5  ,-180.0  ,0.0  ,90.0] #原點位置
READY_POS = [0.0   ,470.0  ,120.0  ,-180.0  ,0.0  ,90.0] #預備位置
GET_CUBE_READY_POS = [-520.0   ,-40.0  ,60.0  ,-180.0  ,0.0  ,90.0] #取料預備位置
tableHeight = 60.0

SLOT1_IO_INDEX = 9 #IO1
SLOT2_IO_INDEX = 10 #IO2
SLOT3_IO_INDEX = 11 #IO3

COM_PORT = 'COM6'
BAUD_RATES = 9600

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

def init():
    s=HIWIN_Python.connect_robot("192.168.0.2",1) #連線
    HIWIN_Python.clear_alarm(s)
    time.sleep(0.5)

    HIWIN_Python.set_connection_level(s,1)
    HIWIN_Python.set_operation_mode(s,0) #0自動,1手動

    #設定速度
    HIWIN_Python.set_lin_speed_edited(s,50) #設定直線運動速度 int set_lin_speed(HROBOT robot, double value),value=mm/s
    HIWIN_Python.set_ptp_speed(s,speedRate) #設定直線運動速度 int set_lin_speed(HROBOT robot, double value),value=mm/s
    HIWIN_Python.set_motor_state(s,1) #啟動馬達
    time.sleep(0.2)

    #設定移動%
    HIWIN_Python.set_override_ratio(s,speedRate) #設定整體速度 int set_override_ratio(HROBOT robot, double value)#整體速度比例:1-100(%)
    move_abs(s ,  'PTP' , HOME_POS)
    return s

if __name__=='__main__':
    global grab
    grab = serial.Serial(COM_PORT, BAUD_RATES) #夾爪通訊
    s = init()
    time.sleep(2)
    input('預備執行任務，請按任意鍵繼續')
    move_abs(s ,  'PTP' , READY_POS)

    #電磁閥控制
    HIWIN_Python.set_digital_output(s, SLOT1_IO_INDEX, True) #開啟電磁閥
    time.sleep(1)
    HIWIN_Python.set_digital_output(s, SLOT2_IO_INDEX, True) #開啟電磁閥
    time.sleep(1)
    HIWIN_Python.set_digital_output(s, SLOT3_IO_INDEX, True) #開啟電磁閥
    time.sleep(2)

    HIWIN_Python.set_digital_output(s, SLOT1_IO_INDEX, False) #關閉電磁閥
    time.sleep(1)
    HIWIN_Python.set_digital_output(s, SLOT2_IO_INDEX, False) #關閉電磁閥
    time.sleep(1)
    HIWIN_Python.set_digital_output(s, SLOT3_IO_INDEX, False) #關閉電磁閥

    move_abs(s ,  'PTP' , GET_CUBE_READY_POS)
    HIWIN_Python.set_override_ratio(s,10)

    while True :
        grab.write(b'testHeight\n') 
        time.sleep(0.1)
        data_raw = grab.readline()  # 讀取一行
        data = data_raw.decode()   # 用預設的UTF-8解碼

        if data == 'stop':
            break
        
        move_rel(s ,  'PTP' , (0,0,-1,0,0,0))
        tableHeight -= 1

    HIWIN_Python.set_override_ratio(s,80)
    move_abs(s ,  'PTP' , HOME_POS)
    HIWIN_Python.disconnect(s)