from micropython import const
from machine import Pin, Timer, PWM
from esp32_gpio_lcd import GpioLcd
from time import sleep_ms, ticks_ms, ticks_diff
from rotary_irq_esp import RotaryIRQ
from math import pi

LCD_D7 = const(27)
LCD_D6 = const(26)
LCD_D5 = const(25)
LCD_D4 = const(33)
LCD_RS = const(32)
LCD_EN = const(23)

WHEEL_PERI = const(1.11715) # meter, diameter: 14" dispatcher wheel
MPS_TO_KMPH = const(3.6) # ((1000m / (60sec*60min)) ** -1

HALL = const(4)
HALL_DEBOUNCE = const(50) # ms, tractor speed should not exceed: 3.6*(1.11715/0.05) ~ 81kmph

ROT_DT = const(18)
ROT_CLK = const(19)

MOT = const(22)

DELAY = const(100)

lcd = GpioLcd(
    d7_pin=Pin(LCD_D7),
    d6_pin=Pin(LCD_D6),
    d5_pin=Pin(LCD_D5),
    d4_pin=Pin(LCD_D4),
    rs_pin=Pin(LCD_RS),
    enable_pin=Pin(LCD_EN),
)

start_time = 0
speed = 0
def record_speed(pin):
    if pin.value():
        return
    global start_time, speed
    time_delta = ticks_diff(ticks_ms(), start_time) / 1000  # sec
    speed = WHEEL_PERI / time_delta # m/s
    start_time = ticks_ms()

hall = Pin(HALL, mode=Pin.IN)
timer = Timer(0)
_iqr = hall.irq(
    trigger=Pin.IRQ_FALLING,
    handler=lambda pin: timer.init(
        mode=Timer.ONE_SHOT,
        period=HALL_DEBOUNCE,
        callback=lambda t_: record_speed(pin)
    )
)

ok_pb = Pin(ROT_SW, mode=Pin.IN, pull=Pin.PULL_UP)
rot = RotaryIRQ(
    pin_num_clk=ROT_CLK,
    pin_num_dt=ROT_DT,
    min_val=5,
    max_val=200,
    reverse=True,
    range_mode=RotaryIRQ.RANGE_BOUNDED,
    pull_up=True,
)

mot = PWM(Pin(MOT))

def value_map(value, fromLow, fromHigh, toLow, toHigh):
    return int((value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow)

temp0 = 0
temp1 = 0
actual_peri = 0
rpm = 0
prev_speed = 0
i = 0
lcd.clear()
lcd.hide_cursor()
lcd.blink_cursor_off()
while True:
    if temp0 != speed:
        temp0 = speed
        lcd.move_to(0, 0)
        s = f'{MPS_TO_KMPH*speed:.2f}km/h'
        lcd.putstr(f'Spd: {s:<11}')
        t = actual_peri/speed # sec, time taken to complete 1 revo.
        rpm = 60 * 1/t # rps to rpmA
        # mot.duty(int(value_map(rpm, 0, 500, 0, 1023)))
    cm = rot.value()
    if temp1 != cm:
        temp1 = cm
        lcd.move_to(0, 1)
        d = f'{cm}cm'
        lcd.putstr(f'Dis: {d:<11}')
        actual_peri = 12 * cm/100 # slots=12, cm to m conv.
    sleep_ms(DELAY)
    i += +1 if speed <= prev_speed else -1
    if i * DELAY >= 2000:
        speed *= 0.75
        i = 0
    prev_speed = speed
    print(f'{speed=:0.2f}, {rpm=:0.2f}', end='\r')
