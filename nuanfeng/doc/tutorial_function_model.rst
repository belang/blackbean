#######################
Function Model Tutorial
#######################

Write the python Functions for the computing function
=====================================================

Write fuctions to realise the computing functions you need.
For example, if you want to do a integar addition or subtraction according to a flag,
and saturate the result if it exceed 32 bits, you can define::

   def add_t(a, b, f):
       if isinstance(a, int) and isinstance(b, int):
           if f > 100:
               c = a+b
           elif 0 < f <= 100:
               c = a-b
           else:
               raise ValueError("flag must be 0 or 1.")
           if c.bit_length > 32:
               return 2**33-1
           else:
               return c
       else:
           raise TypeError("data in must be integer.")

You can also use fucntion calls and seperate config and computing::

   def config_add_t(f):
       if f > 100:
           return 1
       elif 0 < f <= 100:
           return 0
       else:
           raise ValueError("flag must larger than 0.")

   def add_t(a, b, f):
       is_int(a, b):
       c = add_sub(a, b, f)
       return saterate_int32(c)

   def is_int(*v):
       for one in v:
           if not isinstance(one, int):
               raise TypeError("data in must be integer.")

   def add_sub(a, b, f):
       if f:
           return a+b
       elif:
           return a-b

   def saterate_int32(d):
       if d.bit_length > 32:
           return 2**33-1
       else:
           return d

