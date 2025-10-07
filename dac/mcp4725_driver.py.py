import smbus as i2c

class MCP4725:
    def __init__(self, dynamic_range, address=0x61, verbose=False):
        self.bus = i2c.SMBus(1)
        self.address = address
        self.verbose = verbose
        self.dynamic_range = dynamic_range
        self.wm = 0  # Write Mode - обычная запись в DAC
        self.pds = 0  # Power Down Selection - нормальный режим

    def deinit(self):
        self.bus.close()

    def set_number(self, number):
        if not isinstance(number, int):
            raise ValueError("На вход ЦАП можно подавать только целые значения")
        
        if not (0 <= number <= 4095):
            raise ValueError("Число выходит за разрядность MCP4725 (12 бит)")
        
        # Формируем байты для отправки
        first_byte = (self.wm << 5) | (self.pds << 1) | (number >> 8)
        second_byte = number & 0xFF
        
        try:
            self.bus.write_i2c_block_data(self.address, first_byte, [second_byte])
        except OSError as e:
            raise RuntimeError(f"Ошибка I2C связи: {e}")

        if self.verbose:
            print(f"Число: {number}, отправленные по I2C данные: [0x{(self.address):02X}, 0x{first_byte:02X}, 0x{second_byte:02X}]")

    def set_voltage(self, V):
        if not (0.0 <= V <= self.dynamic_range):
            print(f"Напряжение выходит за динамический диапазон ЦАП (0.0-{self.dynamic_range:.2f} В)")
            print("Устанавливаем 0.0")
            V = 0.0
        
        nV = int(4095 * V / self.dynamic_range)
        self.set_number(nV)

if __name__ == "__main__":
    dac = None
    try:
        dac = MCP4725(5.17, 0x61, True)

        while True:
            try:
                user_input = input("Введите напряжение в вольтах (или 'q' для выхода): ")
                if user_input.lower() == 'q':
                    break
                    
                voltage = float(user_input)
                dac.set_voltage(voltage)
                
            except ValueError:
                print("Ошибка: введите число или 'q' для выхода!")
            except Exception as e:
                print(f"Ошибка: {e}")

    except Exception as e:
        print(f"Ошибка инициализации: {e}")
    
    finally:
        if dac:
            dac.deinit()
        print("Программа завершена.")