const int trigPin = 8;    // common trig pin
const int echoPinA = 9;   // hc-sr04 a
const int echoPinB = 10;  // hc-sr04 b

const int serDataPin = 6; // level lights
const int latchPin = 5;
const int clockPin = 4;

const int buzzerPin = 3;

const int lowerLimit = 2;
const int upperLimit = 29;

int calcDis(int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH);  // reads the echoPin, returns the sound wave travel time in microseconds
  int distance = (int) ((duration * 0.034) / 2);
  return distance;
}

void setup() {
  pinMode(trigPin, OUTPUT);   // hc-sr04, a to d
  pinMode(echoPinA, INPUT);
  pinMode(echoPinB, INPUT);
  pinMode(buzzerPin, OUTPUT);  
  pinMode(serDataPin, OUTPUT);  // 74hc595
  pinMode(latchPin, OUTPUT);
  pinMode(clockPin, OUTPUT);
  Serial.begin(115200);
  Serial.println("setup done!");
}
int i = 0;
void loop() {
  int disA = calcDis(echoPinA);
  delay(100);
  int disB = calcDis(echoPinB);
  delay(100);
  int dis[] = {disA, disB};
  digitalWrite(latchPin, LOW);
  for (int i = 0; i < 2; ++i) {
    int level = map(dis[i], lowerLimit, upperLimit, 7, 0);
    byte serData = 0x00;
    if (dis[i] >= lowerLimit && dis[i] <= upperLimit) {
      for (int j = 0; j < 8; ++j) {
        if (j < level) {
          bitSet(serData, j);
        }
      }
    } else {
      serData = 0b01000001;
    }
    if (dis[i] <= (upperLimit + 3) && dis[i] >= (upperLimit - 3)) {
      digitalWrite(buzzerPin, !digitalRead(buzzerPin));
    } else {
      digitalWrite(buzzerPin, LOW);
    }
    Serial.println(digitalRead(buzzerPin));
    Serial.print("dis"); Serial.print((char) ('A'+i)); Serial.print('='); Serial.print(dis[i]);
    Serial.print(", level="); Serial.print(level);
    Serial.print(", serData="); Serial.println(serData, BIN);
    shiftOut(serDataPin, clockPin, LSBFIRST, serData);
    delay(200);
  }
  digitalWrite(latchPin, HIGH);
  Serial.println("");
}
