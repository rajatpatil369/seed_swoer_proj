from micropython import const
from machine import Pin, Timer, PWM
from esp32_gpio_lcd import GpioLcd
from time import sleep_ms, ticks_ms, ticks_diff
from rotary_irq_esp import RotaryIRQ

MPS_TO_KMPH = const(3.6)  # ((1000m / (60sec*60min)) ** -1
INCH_TO_METER = const(0.0254)


def value_map(value, from_low, from_high, to_low, to_high):
    return int((value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low)


class MyApp:
    WHEEL_PERI = const(1.11715)  # m, dispatcher wheel diameter: 14"

    def __init__(self):
        self.mot = PWM(Pin(22), duty_u16=0)
        self.buz = Pin(21, mode=Pin.OUT)

        self.lcd = GpioLcd(
            d7_pin=Pin(27),
            d6_pin=Pin(26),
            d5_pin=Pin(25),
            d4_pin=Pin(33),
            rs_pin=Pin(32),
            enable_pin=Pin(23),
        )

        self.rot = RotaryIRQ(
            pin_num_clk=19,
            pin_num_dt=18,
            min_val=2,  # inch
            max_val=78,
            reverse=True,
            range_mode=RotaryIRQ.RANGE_BOUNDED,
            pull_up=True,
        )

        self.speed = 0  # m/s
        self.actual_peri = 0  # m
        self.start_time = ticks_ms()  # ms

        hall = Pin(4, mode=Pin.IN)
        timer = Timer(0)
        _iqr = hall.irq(
            trigger=Pin.IRQ_FALLING,
            handler=lambda pin: timer.init(
                mode=Timer.ONE_SHOT,
                period=50,  # hall sensor debounce time, tractor speed should not exceed: 3.6*(1.11715/0.05) ~ 81kmph
                callback=lambda t_: self.record_speed(pin)
            )
        )

    def record_speed(self, pin):
        if pin.value():
            return
        time_delta = ticks_diff(ticks_ms(), self.start_time) / 1000  # sec
        self.speed = MyApp.WHEEL_PERI / time_delta  # m/s
        self.start_time = ticks_ms()

    def run_main_loop(self):
        temp0 = 0
        temp1 = 0
        rpm = 0  # utilized only in print
        duty = 0
        iteration_delay = 100
        i = 0
        prev_speed = 0
        r0, r1a, r1b, lcd_cont = 'Spd: 0.00kmp/h', '', 'RPM:0', ''
        self.lcd.clear()
        while True:
            inch = self.rot.value()
            if temp0 != inch:
                temp0 = inch
                self.lcd.move_to(0, 1)
                d = f'{inch}"'
                r1a = f'Dis:{d:<4}'
                self.actual_peri = 12 * (INCH_TO_METER * inch)  # slots=12, inch to m conv.
            if temp1 != self.speed:
                temp1 = self.speed
                self.lcd.move_to(0, 0)
                s = f'{MPS_TO_KMPH * self.speed:.2f}km/h'
                r0 = f'Spd: {s:<11}'
                t = self.actual_peri / self.speed  # sec, time taken to complete 1 revo.
                rpm = 60 * 1 / t  # rps to rpm
                self.lcd.move_to(10, 1)
                r1b = f'RPM:{round(rpm):<4}'
                duty = value_map(rpm, 0, 500, 0, 65535)
                if duty > 65535:
                    self.mot.duty_u16(0)
                    self.buz.value(1)
                    sleep_ms(100)
                    self.buz.value(0)
                    sleep_ms(100)
                    self.buz.value(1)
                    sleep_ms(100)
                    self.buz.value(0)
                    self.speed = 0.001
                    self.start_time = ticks_ms()
                else:
                    self.mot.duty_u16(duty)
            if (temp3 := f'{r0}\n{r1a}{r1b}') != lcd_cont:
                self.lcd.move_to(0, 0)
                self.lcd.putstr(temp3)
                lcd_cont = temp3
            sleep_ms(iteration_delay)
            i += +1 if self.speed <= prev_speed else -1
            if i * iteration_delay >= 4000:
                self.speed *= 0.75
                i = 0
            prev_speed = self.speed
            # print(f'{self.speed=:0.2f}, {rpm=:0.2f}, {duty=}                                              ', end='\r')


if __name__ == '__main__':
    MyApp().run_main_loop()
