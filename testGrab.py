import serial
import time
COM_PORT = 'COM6'
BAUD_RATES = 9600

def getCubeType():
    global grab
    grab.write(b'getType\n')
    time.sleep(0.2)

    data_raw = grab.readline()  # 讀取一行
    data = data_raw.decode()   # 用預設的UTF-8解碼
    data = data.split(' ')
    print('夾爪辨識：', data)
    return data

#main=========================================================================================================
if __name__=='__main__':
    global grab
    grab = serial.Serial(COM_PORT, BAUD_RATES) #夾爪通訊
    time.sleep(2)
    grab.write(b'blink\n')
    time.sleep(2)

    for i in range(3):
        getCubeType()
        time.sleep(3)
        grab.write(b'clear\n')
        time.sleep(3)

    grab.write(b'blink\n')
    time.sleep(2)
    grab.close()