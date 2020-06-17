from arduino_to_sql_2 import User, Daq


# arc = ArduinoToSql(sensors_number=6, user_name='YH', com='COM10')
# try:
#     arc.start()
# except KeyboardInterrupt:
#     arc.close()

# INPUT user_name, numbers_of_sensors, COM, frequency, plot_time(seconds)
d = Daq(user_name='YH', num_sensors=6, com='COM10', fq=20, plot_second=10)
#d.cali_time()
# main program
d.main(run_time=20)


# except KeyboardInterrupt:
#     print('interrupt')
#     d.is_run = False



