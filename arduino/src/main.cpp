#include <i2c/PololuRPiSlave.h>
#include "HX711.h"

#define calibration_factor 1965.0 //This value is obtained using the SparkFun_HX711_Calibration sketch

#define LOADCELL_DOUT_PIN  6
#define LOADCELL_SCK_PIN  5

HX711 scale;

struct Data
{
  float num;
};

PololuRPiSlave<struct Data,5> slave;

void setup()
{
  Serial.begin(9600);
  Serial.println("HX711 scale demo");

  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  scale.set_scale(calibration_factor); //This value is obtained by using the SparkFun_HX711_Calibration sketch
  scale.tare();  //Assuming there is no weight on the scale at start up, reset the scale to 0

  slave.init(20);
}

void loop()
{
  // todo: handle commands like send_data and calibrate (set calibration factor automatically)

  // Call updateBuffer() before using the buffer, to get the latest
  // data including recent master writes.
  slave.updateBuffer();

  slave.buffer.num = scale.get_units();
  //  Serial.println(scale.get_units(), 1);
  // When you are done WRITING, call finalizeWrites() to make modified
  // data available to I2C master.
  slave.finalizeWrites();
}
