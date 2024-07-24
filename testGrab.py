import serial
import time
COM_PORT = 'COM6'
BAUD_RATES = 9600

def getCubeType():
    grab.write(b'getType\n')
    time.sleep(0.5)

    data_raw = grab.readline()  # 讀取一行
    data = data_raw.decode()   # 用預設的UTF-8解碼
    print('接收到的原始資料：', data_raw)
    print('接收到的資料：', data)

#main=========================================================================================================
grab = serial.Serial(COM_PORT, BAUD_RATES) #夾爪通訊
time.sleep(2)

for i in range(3):
    getCubeType()
    time.sleep(3)
    grab.write(b'clear\n')
    time.sleep(3)

grab.write(b'blink\n')
grab.close()