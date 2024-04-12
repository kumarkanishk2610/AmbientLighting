#define red 9
#define green 10
#define blue 11

void setup() {
  Serial.begin(115200);  // Set the baud rate to match the Python code
  pinMode(red, OUTPUT);
  pinMode(green, OUTPUT);
  pinMode(blue, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    String colorData = Serial.readStringUntil('\n');
    colorData.trim();  // Remove leading/trailing whitespace
    
    int values[3];  // To store R, G, B values
    int i = 0;
    char* part = strtok((char*)colorData.c_str(), ",");
    while (part != NULL && i < 3) {
      values[i] = atoi(part);
      part = strtok(NULL, ",");
      i++;
    }
    
    analogWrite(red, values[0]);
    analogWrite(green, values[1]);
    analogWrite(blue, values[2]);
  }
}