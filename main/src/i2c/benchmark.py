from arduino import Arduino
import timeit

arduino = Arduino()


n = 500
total_time = timeit.timeit(arduino.test_write8, number=n)
write_kbits_per_second = 8 * n * 8 / total_time / 1000

print("Writes of 8 bytes: " + '%.1f' % write_kbits_per_second + " kilobits/second")

n = 500
total_time = timeit.timeit(arduino.test_read8, number=n)
read_kbits_per_second = 8 * n * 8 / total_time / 1000

print("Reads of 8 bytes: " + '%.1f' % read_kbits_per_second + " kilobits/second")
