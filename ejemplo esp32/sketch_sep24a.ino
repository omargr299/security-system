#define led 2
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(led, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available()>0) 
  {
    char option = Serial.read();
    if (option == '1')
    {
      digitalWrite(led, HIGH);

    }
    else{
      digitalWrite(led, LOW);

    }
  }
}
