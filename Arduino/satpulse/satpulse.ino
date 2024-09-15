
#include <arduinoFFT.h>
const double samplingFrequency = 50;
const uint16_t samples = 128;
const byte period PROGMEM = 20;
int sensorPin = 0;
double alpha = 0.75;

double change = 0.0;
int max_elem = 0;
int max_index = 0;
double vReal[samples];
double vReal_prev[samples] = {0};
double vImag[samples];
bool first = true;
int cnt = 0;

void setup()
{
Serial.begin(115200);
delay(1500);

}
//function to copy arrays
void deepCopyArray(double source[], double destination[], byte size) {
  for (int i = 0; i < size; i++) {
    destination[i] = source[i];
  }
}
void loop()
{
  cnt = cnt +1;
  static double oldValue = 0;
  static double oldChange = 0;
  int rawValue = analogRead(sensorPin);
  //calculating sensor read value, and applying a filter
  double value = alpha * oldValue + (1 - alpha) * rawValue;
  
  float avg = 0.0;
  if (first){
    first = false;
    vReal_prev[127] = 0;
  }
  //circular Buffer implementation using 2 arrays
  for (int i = samples-2; i>-1; i--) {
			vReal[i] = vReal_prev[i+1];
  }
  vReal[127]=value;
  deepCopyArray(vReal, vReal_prev, samples);
  Serial.print("\n");
  //begin DFT only after we get 128 points
  if(cnt>128){
  //Compuote DFT, and update input arrays
  double vImag[samples]= {0};
  ArduinoFFT<double> FFT = ArduinoFFT<double>(vReal, vImag, samples, samplingFrequency);  
  FFT.compute(FFTDirection::Forward); /* Compute FFT */
  FFT.complexToMagnitude(); 
  Serial.print("\n");

  max_elem = 0;
  max_index = 0;
  //Start from 2% and end at 98% to neglect the 0th, 1st, and sample-1 frequencies 
  for (int i = ceil(0.02*samples); i<floor(0.98*samples); i++){
  //finding the max amplitude
  if (vReal[i]>max_elem){
    max_elem = vReal[i];
    max_index = i;
  }
}  
//using the fact that DFT output is symmetrical
if(max_index>samples/2){
    max_index = samples-max_index;
  }
//There are 50 points outputted every second, 60 seconds in a minunte, that is why we multiply by 50*60=3000 
Serial.print(3000*max_index/samples);
  }
oldValue = value;
//delay every iteration
delay(period);

}
