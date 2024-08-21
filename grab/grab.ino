bool isTouchTable = false;

void setup() {
    Serial.begin(9600);
    pinMode(2, OUTPUT); //slot1 R
    pinMode(3, OUTPUT); //G
    pinMode(4, OUTPUT); //B

    pinMode(5, OUTPUT); //slot2
    pinMode(6, OUTPUT);
    pinMode(7, OUTPUT);

    pinMode(8, OUTPUT); //slot3
    pinMode(9, OUTPUT);
    pinMode(10, OUTPUT);

    pinMode(A1, INPUT); //slot1
    pinMode(A2, INPUT); //slot2
    pinMode(A3, INPUT); //slot3

    pinMode(11,INPUT);
}
void loop() {
    if (Serial.available()) {
        String str = Serial.readStringUntil('\n');// 讀取傳入的字串直到"\n"結尾

        if (str == "getType") { //detect cube type
            String resultMsg = "";
            int distance1 = 60 - map(analogRead(A1),0,1024,0,60); //slot1
            int distance2 = 60 - map(analogRead(A2),0,1024,0,60); //slot2
            int distance3 = 60 - map(analogRead(A3),0,1024,0,60); //slot3

            if(distance1 <= 14){ //small
                digitalWrite(2,1);
                resultMsg += "SMALL ";
            }else if(distance1 <=  35){ //mid
                digitalWrite(3,1);
                resultMsg += "MID ";
            }else{ //large
                digitalWrite(4,1);
                resultMsg += "LARGE ";
            }

            if(distance2 <= 14){ //small
                digitalWrite(5,1);
                resultMsg += "SMALL ";
            }else if(distance2 <= 35){ //mid
                digitalWrite(6,1);
                resultMsg += "MID ";
            }else{ //large
                digitalWrite(7,1);
                resultMsg += "LARGE ";
            }

            if(distance3 <= 14){ //small
                digitalWrite(8,1);
                resultMsg += "SMALL ";
            }else if(distance3 <= 35){ //mid
                digitalWrite(9,1);
                resultMsg += "MID ";
            }else{ //large
                digitalWrite(10,1);
                resultMsg += "LARGE ";
            }

             Serial.println(resultMsg); 
            // Serial.print(distance1);//for test
            // Serial.print(" ");
            // Serial.print(distance2);
            // Serial.print(" ");
            // Serial.println(distance3);
            
        } else if (str == "clear") { //clear LED
            for(int i=2;i<=10;i++){
                digitalWrite(i,0);
            }

        } else if (str == "blink") { //LED show color white, trigger when stage finish
            for(int i=0;i<3;i++){
                for(int j=2;j<=10;j++){
                  digitalWrite(j,1);
                }

                delay(150);

                for(int j=2;j<=10;j++){
                    digitalWrite(j,0);
                }

                delay(100);
            }
        }
    }
  
}
