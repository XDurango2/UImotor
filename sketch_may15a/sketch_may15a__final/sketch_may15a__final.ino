#define pinAEncoder 2
#define pinBEncoder 3

long pulsoPorRevolucion=97.0;
long intervalo =100;

long tiempoAct = 0;
long tiempoAnt = 0;
long rpm = 0;
long pulsoAct = 0;
long pulsoAnt=0;
long tiempo = 0;

#define entradaPWM 11
#define puenteHEntrada1 9
#define puenteHEntrada2 10

float speedRPM;//==600.00;
float speedPWM=0;       

float kP=0.3; //0.3
float kI=0.2;   //0.2
float kD=0.1;  //0.1

float P;
float I;
float D;
float PID;
float error;
float a_error;
float dt_error;
float last_error;

void setup() {
  
 pinMode(pinAEncoder,INPUT);
 pinMode(pinBEncoder,INPUT);
 
 pinMode(entradaPWM,OUTPUT);
 pinMode(puenteHEntrada1,OUTPUT);
 pinMode(puenteHEntrada2,OUTPUT);
 
 Serial.begin(9600);
 
 attachInterrupt(1,interrupcion,RISING);
  
 digitalWrite(puenteHEntrada1,LOW);
 digitalWrite(puenteHEntrada2,HIGH);
  
}

void loop() {

unsigned long tiempoAct = millis();

if((tiempoAct-tiempoAnt)>=intervalo){

  rpm = abs(((float)(pulsoAct - pulsoAnt)/pulsoPorRevolucion)*(60000.0/intervalo));
  
  if(rpm>1){
      tiempo=tiempo+intervalo;
    }else{
      tiempo=0;
    }
  
  pulsoAnt=pulsoAct;
  tiempoAnt=tiempoAct;
  
  error=speedRPM-rpm;
  P=error*kP;
  a_error=a_error+error,
  I=a_error*kI;
  dt_error=(error-last_error);
  D=dt_error*kD;
  last_error=error,
  PID=P+I+D;
  speedPWM=PID;
  
 speedPWM=constrain(speedPWM,0,255);
 
 analogWrite(entradaPWM,speedPWM);
 
 Serial.println(String(rpm));
  }

}

void interrupcion(){
  pulsoAct++;
  }
void serialEvent() {
if (Serial.available()) {
  String comando = Serial.readStringUntil('\n');
  comando.trim();

  if (comando.startsWith("RPM:")) {
    speedRPM=0;
    delay(100);
    speedRPM = comando.substring(4).toFloat();
  } else if (comando.startsWith("Kp:")) {
    kP = comando.substring(3).toFloat();
  } else if (comando.startsWith("Kd:")) {
    kD = comando.substring(3).toFloat();
  } else if (comando.startsWith("Ki:")) {
    kI = comando.substring(3).toFloat();
  }

  
}
}
