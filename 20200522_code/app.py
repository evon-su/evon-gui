from arduino_to_sql_3 import User, Daq

# INPUT user_name, numbers_of_sensors, COM, frequency, plot_time(seconds)
d = Daq(user_name='JU', num_sensors=12, sr=100, max_runtime=60, com1='COM10', com2='COM12', plot_second=10)
#d.cali_time()

# main program
d.main()






