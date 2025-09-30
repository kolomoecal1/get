import RPi.GPIO as GPIO
import time

def voltage_to_number(voltage):
    if not (0.0 <= voltage <= dynamic_range):
        print(f"Напряжение выходит за динамический диапазон ЦАП (0.00 - {dynamic_range:.2f} B)")
        print("Устанавливаем 0.0 В")
        return 0
    number = int(voltage / dynamic_range * 255)
    # Гарантируем, что число не превысит 255 из-за ошибок округления
    return min(number, 255)

def number_to_dac(number):
    binary = bin(number)[2:].zfill(8)  # 8 бит для 8-битного ЦАП
    for i in range(8):
        GPIO.output(dac_bits[i], int(binary[i]))

GPIO.setmode(GPIO.BCM)
dac_bits = [16, 20, 21, 25, 26, 17, 27, 22]
GPIO.setup(dac_bits, GPIO.OUT)
dynamic_range = 3.3

try:
    while True:
        try:
            voltage = float(input("Введите напряжение в вольтах: "))
            number = voltage_to_number(voltage)
            number_to_dac(number)
            print(f"Установлено напряжение: {voltage:.2f} В, код ЦАП: {number}")
            
        except ValueError:
            print("Вы ввели не число. Попробуйте еще раз\n")
        except KeyboardInterrupt:
            print("\nВыход из программы")
            break

finally:
    GPIO.output(dac_bits, 0)
    GPIO.cleanup()