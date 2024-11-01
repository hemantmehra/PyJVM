import pprint
pp = pprint.PrettyPrinter()
from JVMClass import JVMClass

obj1 = JVMClass('Main')
main_method = obj1.get_method_by_name(b'inc')
code_attr = obj1.get_code_attribute(main_method)
obj1.execute(code_attr)
