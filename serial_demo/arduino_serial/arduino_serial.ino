#define FASTLED_ALLOW_INTERRUPTS 0
#include <FastLED.h>
#include <Streaming.h>
#include "font8x8_basic.h"

// ---USED FOR LEDS---
// pins for wemos d1 mini
// #define DATA 2  // D4
// pins for ESP32
#define DATA 16  // IO16


#define WIDTH (32*2)
#define HEIGHT 8
#define NUM_LEDS (WIDTH*HEIGHT)

int getIndex(int, int);

CRGB leds[NUM_LEDS];


// ---USED FOR TIMING---
int fps = 50;
int tickDuration = 1000/fps;
long lastTickTime = 0;

// ---USED FOR TEXT---
boolean expectingNewMessage = false;
int messageWidth = 0;
String message = "";
long startTime = 0;
int scrollSpeed = 30;
int scroll = WIDTH;



// -------------------------
void setup() {
	// Serial.begin(115200);
	Serial.begin(230400);


	FastLED.addLeds<WS2812B, DATA, GRB>(leds, 0, NUM_LEDS);
	FastLED.setMaxPowerInVoltsAndMilliamps(5, 500);
	FastLED.setCorrection( TypicalLEDStrip );
	FastLED.setBrightness(64);
	FastLED.clear();
	FastLED.show();
}


void loop() {
	// READ IN NEW MESSAGES FROM SERIAL
	if(Serial.available() > 0) {
		leds[ getIndex(63, 0) ] = CRGB(128, 0, 0);
		FastLED.show();
		message = Serial.readStringUntil('\n');
		leds[ getIndex(63, 0) ] = CRGB(128, 128, 0);
		FastLED.show();
		int love_length = message.length();
		messageWidth = 0;
		startTime = millis();
		scroll = WIDTH;
		expectingNewMessage = false;
	}



	// DISPLAY TEXT
	long currentTime = millis();
	if(!expectingNewMessage && currentTime >= lastTickTime+tickDuration) {
		lastTickTime = currentTime;

		if(message.length() > 0) {
			FastLED.clear();

			if(messageWidth == 0) {
				leds[ getIndex(63, 0) ] = CRGB(0, 128, 0);
				FastLED.show();
			}


			// int scroll = WIDTH;
			if (messageWidth > 0) {
				// number between 0 and -WIDTH
				scroll--;
				if(scroll < -messageWidth) {
					scroll = WIDTH;

          if(message.length() >= 1 && message[message.length()-2] != ' ') {
            Serial.println("A");
            leds[ getIndex(63, 0) ] = CRGB(128, 0, 128);
            FastLED.show();
            expectingNewMessage = true;
            return;
          }
				}
			}

			int x = scroll;
			unsigned int charIndex = 0;
			byte bitMask = 0x01;

			while ( !(charIndex == message.length() && bitMask == (1 << 7)) ) {
				char c = message.charAt(charIndex);
				boolean emptyColumn = true;
				for (int y = 7; y >= 0; y--) {
					byte f = font[c][7 - y];
					if (f & bitMask) {
						if (x >= 0 && x < WIDTH) {
							// leds[ getIndex(x, y) ] = CRGB(255, 0, 0);


							// byte minimum = 0x20; // start of readable characters
							// byte minimum = 0x38; //8
							// byte minimum = 0x61; //a
							// byte maximum = 0x7A; //z
							// byte maximum = 0x78; //something...
							// byte maximum = 0x7F; // end of all readable characters

							// byte hue = 255 * (c - minimum) / (maximum - minimum);
							// leds[ getIndex(x, y) ] = CHSV(hue, 255, 255);
							byte hue = 255 * charIndex/message.length();
							leds[ getIndex(x, y) ] = CHSV(hue, 255, 255);
						}
						emptyColumn = false;
					}
				}
				if (bitMask == (1 << 7)) {
					if (c == ' ') {
						x += 3;
					}
					bitMask = 0x01;
					charIndex++;
					x++;
					if (charIndex == message.length()) {
						break;
					}
				}
				else {
					bitMask = bitMask << 1;
					if (!emptyColumn) {
						x++;
					}
				}

				//don't bother drawing the rest of the string if we already know its width
				if (x == WIDTH && messageWidth > 0) {
					break;
				}
			}

			if (messageWidth == 0) {
				messageWidth = x - scroll;
				leds[ getIndex(63, 0) ] = CRGB(0, 128, 128);
			}

			FastLED.show();
		}
	}


}
// -------------------------


// ---HELPER FUNCTIONS---
int getIndex(int x, int y) {
	int index = (WIDTH - 1 - x) * 8;
	if (x % 2 == 0) {
		index += 7 - y;
	}
	else {
		index += y;
	}

	if (index < 0 || index > NUM_LEDS - 1) {
		index = 1; //for debugging
	}

	return index;
}
