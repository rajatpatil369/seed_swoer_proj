const int trigPin = 8;    // common trig pin
const int echoPinA = 9;   // hc-sr04 a
const int echoPinB = 10;  // hc-sr04 b
const int echoPinC = 11;  // hc-sr04 c
const int echoPinD = 12;  // hc-sr04 d

const int clockPin = 6;
const int latchPin = 5;
const int dataPin = 4;

void setup() {
  pinMode(trigPin, OUTPUT);   // hc-sr04, a to d
  pinMode(echoPinA, INPUT);
  pinMode(echoPinB, INPUT);
  pinMode(echoPinC, INPUT);
  pinMode(echoPinD, INPUT); 
  pinMode(clockPin, OUTPUT);  // 74hc595
  pinMode(latchPin, OUTPUT);
  pinMode(dataPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  long disA, disB, disC, disD;
  disA = dist(echoPinA, trigPin);
  disB = dist(echoPinB, trigPin);
  disC = dist(echoPinC, trigPin);
  disD = dist(echoPinD, trigPin);
  Serial.print("disA="); Serial.print(disA);
  Serial.print(", disB="); Serial.print(disB);
  Serial.print(", disC="); Serial.print(disC);
  Serial.print(", disD="); Serial.print(disD);
}


long dist(int echoPin, int trigPin) {
  long duration, distance;
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, LOW);
  duration = pulseIn(echoPin, HIGH);  // Reads the echoPin, returns the sound wave travel time in microseconds
  distance = duration * 0.034 / 2;
  return distance;
}
