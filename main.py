import cStreamClass as cs
import datetime as dt

print('starting system' + dt.datetime.now().strftime("%H:%M:%S %y-%m-%d"))
rr = cs.circularStream()
rr.run()