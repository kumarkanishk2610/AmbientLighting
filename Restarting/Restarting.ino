#define red 11
#define green 10
#define blue 9

int currentColor[3] = {0, 0, 0};  // Current color values
int targetColor[3] = {0, 0, 0};   // Target color values
int fadingStep = 5;               // Fading step value for smooth transitions
unsigned long lastRestartTime = 0; // Variable to store the time of the last restart

void setup() {
  Serial.begin(19200);  // Set the baud rate to match the Python code
  pinMode(red, OUTPUT);
  pinMode(green, OUTPUT);
  pinMode(blue, OUTPUT);
}

void loop() {
  // Restart Arduino every 30 seconds
  if (millis() - lastRestartTime >= 30000) {
    restartArduino();
  }
  
  if (Serial.available() > 0) {
    String colorData = Serial.readStringUntil('\n');
    colorData.trim();  // Remove leading/trailing whitespace
    
    int i = 0;
    char* part = strtok((char*)colorData.c_str(), ",");
    while (part != NULL && i < 3) {
      targetColor[i] = atoi(part);
      part = strtok(NULL, ",");
      i++;
    }
    
    // Gradually transition each color channel to the target value
    while (!reachedTargetColor()) {
      for (int i = 0; i < 3; i++) {
        if (currentColor[i] < targetColor[i]) {
          currentColor[i] += fadingStep;
          if (currentColor[i] > targetColor[i]) {
            currentColor[i] = targetColor[i];
          }
        } else if (currentColor[i] > targetColor[i]) {
          currentColor[i] -= fadingStep;
          if (currentColor[i] < targetColor[i]) {
            currentColor[i] = targetColor[i];
          }
        }
      }
      
      analogWrite(red, currentColor[0]);
      analogWrite(green, currentColor[1]);
      analogWrite(blue, currentColor[2]);
      delay(2);  // Adjust the delay for the transition speed
    }
  }
}

bool reachedTargetColor() {
  for (int i = 0; i < 3; i++) {
    if (currentColor[i] != targetColor[i]) {
      return false;
    }
  }
  return true;
}

void restartArduino() {
  rtTime = millis(); // Update last restart time
  delay(100); // Delay to ensure Serial communication completes
  asm volatile ("  jmp 0"); // Restart Arduino
}
