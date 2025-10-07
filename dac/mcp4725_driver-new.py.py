import smbus
import time

class MCP4725:
    def __init__(self, dynamic_range, address=0x61, verbose=False):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.verbose = verbose
        self.dynamic_range = dynamic_range
        
        # Проверяем доступность устройства
        self._check_device()

    def _check_device(self):
        """Проверяет доступность устройства по I2C"""
        try:
            self.bus.read_byte(self.address)
            if self.verbose:
                print(f"Устройство MCP4725 найдено по адресу 0x{self.address:02X}")
        except OSError as e:
            raise RuntimeError(f"Устройство по адресу 0x{self.address:02X} не найдено. Ошибка: {e}")

    def deinit(self):
        self.bus.close()

    def set_number(self, number):
        if not isinstance(number, int):
            raise ValueError("На вход ЦАП можно подавать только целые значения")
        
        if not (0 <= number <= 4095):
            raise ValueError("Число выходит за разрядность MCP4725 (12 бит)")
        
        # Формируем данные для MCP4725 (Fast Mode)
        # Бит 15-12: Конфигурация (0100 = Fast mode, write DAC register)
        # Бит 11-0: 12-битное значение
        data = [(number >> 8) & 0x0F, number & 0xFF]
        
        try:
            # Записываем данные напрямую без команды
            self.bus.write_i2c_block_data(self.address, data[0], [data[1]])
            
            if self.verbose:
                print(f"Записано число: {number} (0x{number:03X})")
                print(f"Отправленные байты: [0x{data[0]:02X}, 0x{data[1]:02X}]")
                
        except OSError as e:
            raise RuntimeError(f"Ошибка записи в MCP4725: {e}")

    def set_voltage(self, V):
        if not (0.0 <= V <= self.dynamic_range):
            print(f"Предупреждение: напряжение {V}V выходит за диапазон 0.0-{self.dynamic_range}V")
            V = max(0.0, min(V, self.dynamic_range))
            print(f"Установлено: {V}V")
        
        # Вычисляем код для ЦАП
        nV = int(4095 * V / self.dynamic_range)
        self.set_number(nV)

def scan_i2c_devices():
    """Сканирует I2C шину и показывает доступные устройства"""
    print("Сканирование I2C устройств...")
    bus = smbus.SMBus(1)
    found_devices = []
    
    for address in range(0x03, 0x78):
        try:
            bus.read_byte(address)
            found_devices.append(address)
            print(f"Найдено устройство по адресу: 0x{address:02X}")
        except OSError:
            pass
    
    bus.close()
    return found_devices

if __name__ == "__main__":
    # Сначала просканируем шину
    devices = scan_i2c_devices()
    
    if not devices:
        print("I2C устройства не найдены! Проверьте подключение.")
        exit(1)
    
    if 0x61 not in devices:
        print("MCP4725 не найден по адресу 0x61! Доступные адреса:", [hex(x) for x in devices])
        exit(1)
    
    dac = None
    try:
        dac = MCP4725(5.0, 0x61, True)  # Используем 5.0V как опорное
        print("MCP4725 инициализирован успешно!")
        
        # Тестовая последовательность
        print("Запуск тестовой последовательности...")
        test_voltages = [0.0, 1.0, 2.5, 3.3, 5.0]
        
        for voltage in test_voltages:
            print(f"Устанавливаем {voltage}V...")
            dac.set_voltage(voltage)
            time.sleep(1)
        
        print("Тест завершен. Переходим в интерактивный режим...")
        
        # Интерактивный режим
        while True:
            try:
                user_input = input("\nВведите напряжение (0-5V) или 'q' для выхода: ")
                if user_input.lower() == 'q':
                    break
                    
                voltage = float(user_input)
                dac.set_voltage(voltage)
                
            except ValueError:
                print("Ошибка: введите число или 'q' для выхода!")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Ошибка: {e}")

    except Exception as e:
        print(f"Ошибка инициализации MCP4725: {e}")
    
    finally:
        if dac:
            # Устанавливаем 0V перед выходом
            try:
                dac.set_voltage(0.0)
                dac.deinit()
            except:
                pass
        print("Программа завершена.")