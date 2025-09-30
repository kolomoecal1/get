import RPi.GPIO as GPIO
import time

def voltage_to_number(voltage):
    if not (0.0 <= voltage <= dinamic_range):
        print(f"Напряжение выходит за динамический диапазон ЦАП (0.00 - {dynamic_range:.2f} B")
        print("Устанавливаем 0.0 В")
        return 0
    return int(voltage / dinamic_range *255)

def number_to_dac(number):
    a = [int(element) for element in bin(number)[2:].zfill(0)]
    for i in range(8):
        GPIO.output(dac_bits[i], a[i])

GPIO.setmode(GPIO.BCM)
dac_bits = [16, 20, 21, 25, 26, 17, 27, 22]
GPIO.setup(dac_bits, GPIO.OUT)
dinamic_range = 3.3
try:
    while True:
        try:
            voltage = float(input("Введите напряжение в вольтах: "))
            number = voltage_to_number(voltage)
            number_to_dac(number)

        except ValueError:
            print("Вы ввели не то число. Попробуйте еще раз\n")

finally:
    GPIO.output(dac_bits, 0)
    GPIO.cleanup()



