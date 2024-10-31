import io
import pprint
from jvm_opcode import op_code

pp = pprint.PrettyPrinter(indent=2)
bytecode_file = 'Main.class'

CONSTANT_Class = 7
CONSTANT_Fieldref = 9
CONSTANT_Methodref = 10
CONSTANT_InterfaceMethodref = 11
CONSTANT_String = 8
CONSTANT_Integer = 3
CONSTANT_Float = 4
CONSTANT_Long = 5
CONSTANT_Double = 6
CONSTANT_NameAndType = 12
CONSTANT_Utf8 = 1
CONSTANT_MethodHandle = 15
CONSTANT_MethodType = 16
CONSTANT_InvokeDynamic = 18

ACC_PUBLIC = 0x0001 # Declared public; may be accessed from outside its package.
ACC_FINAL = 0x0010 # Declared final; no subclasses allowed.
ACC_SUPER = 0x0020 # Treat superclass methods specially when invoked by the invokespecial instruction.
ACC_INTERFACE = 0x0200 # Is an interface, not a class.
ACC_ABSTRACT = 0x0400 # Declared abstract; must not be instantiated.
ACC_SYNTHETIC = 0x1000 # Declared synthetic; not present in the source code.
ACC_ANNOTATION = 0x2000 # Declared as an annotation type.
ACC_ENUM = 0x4000 # Declared as an enum type.

constant_pool = [None]

with open(bytecode_file, 'rb') as fin:
    magic = int.from_bytes(fin.read(4))
    assert magic == 0xCAFEBABE

    minor_version = int.from_bytes(fin.read(2))
    major_version = int.from_bytes(fin.read(2))
    constant_pool_count = int.from_bytes(fin.read(2))

    print("Magic:", hex(magic))
    print("Minor Version:", minor_version)
    print("Major Version:", major_version)
    print("constant_pool_count:", constant_pool_count)

    for i in range(1, constant_pool_count):
        tag = int.from_bytes(fin.read(1))
        if tag == CONSTANT_Methodref or tag == CONSTANT_Fieldref or tag == CONSTANT_InterfaceMethodref:
            class_index = int.from_bytes(fin.read(2))
            name_and_type_index = int.from_bytes(fin.read(2))
            constant_pool.append({
                'tag': tag,
                'class_index': class_index,
                'name_and_type_index': name_and_type_index
            })

        elif tag == CONSTANT_String:
            string_index = int.from_bytes(fin.read(2))
            constant_pool.append({
                'tag': tag,
                'string_index': string_index
            })
        
        elif tag == CONSTANT_Class:
            name_index = int.from_bytes(fin.read(2))
            constant_pool.append({
                'tag': tag,
                'name_index': name_index
            })

        elif tag == CONSTANT_Utf8:
            length = int.from_bytes(fin.read(2))
            bytes_ = fin.read(length)
            # print('length:', length)
            constant_pool.append({
                'tag': tag,
                'length': length,
                'bytes': bytes_
            })
        
        elif tag == CONSTANT_NameAndType:
            name_index = int.from_bytes(fin.read(2))
            descriptor_index = int.from_bytes(fin.read(2))
            constant_pool.append({
                'tag': tag,
                'name_index': name_index,
                'descriptor_index': descriptor_index
            })
        else:
            assert False, tag

    access_flags = int.from_bytes(fin.read(2))
    print('access_flags:', access_flags)

    if access_flags & ACC_PUBLIC:
        print('ACC_PUBLIC')
    if access_flags & ACC_FINAL:
        print('ACC_FINAL')
    if access_flags & ACC_SUPER:
        print('ACC_SUPER')
    if access_flags & ACC_INTERFACE:
        print('ACC_INTERFACE')
    if access_flags & ACC_ABSTRACT:
        print('ACC_ABSTRACT')
    if access_flags & ACC_SYNTHETIC:
        print('ACC_SYNTHETIC')
    if access_flags & ACC_ANNOTATION:
        print('ACC_ANNOTATION')
    if access_flags & ACC_ENUM:
        print('ACC_ENUM')

    this_class = int.from_bytes(fin.read(2))
    print('this_class:', this_class)
    super_class = int.from_bytes(fin.read(2))
    print('super_class:', super_class)

    interfaces_count = int.from_bytes(fin.read(2))
    print('interfaces_count:', interfaces_count)

    for i in range(interfaces_count):
        fin.read(2)

    fields_count = int.from_bytes(fin.read(2))
    print('fields_count:', fields_count)
    
    assert fields_count == 0
    for i in range(fields_count):
        ...
    
    methods_count = int.from_bytes(fin.read(2))
    print('methods_count:', methods_count)
    
    methods = []
    for i in range(methods_count):
        access_flags = int.from_bytes(fin.read(2))
        name_index = int.from_bytes(fin.read(2))
        descriptor_index = int.from_bytes(fin.read(2))
        attributes_count = int.from_bytes(fin.read(2))

        attributes = []
        for j in range(attributes_count):
            attribute_name_index = int.from_bytes(fin.read(2))
            attribute_length = int.from_bytes(fin.read(4))
            info = fin.read(attribute_length)
            attributes.append({
                'attribute_name_index': attribute_name_index,
                'attribute_length': attribute_length,
                'info': info
            })

        methods.append(
            {
                'access_flags': access_flags,
                'name_index': name_index,
                'descriptor_index': descriptor_index,
                'attributes_count': attributes_count,
                'attributes': attributes
            }
        )

    attributes_count = int.from_bytes(fin.read(2))
    print('attributes_count', attributes_count)

    for i in range(attributes_count):
        attribute_name_index = int.from_bytes(fin.read(2))
        attribute_length = int.from_bytes(fin.read(4))
        info = fin.read(attribute_length)
        print('attribute_name_index', attribute_name_index)
        print('attribute_length', attribute_length)
        print('info', info)

    # pp.pprint(constant_pool)
    # pp.pprint(methods)

    assert len(constant_pool) == constant_pool_count

    print('-'* 50)

    for method in methods:
        name_index = method['name_index']
        name_constant = constant_pool[name_index]['bytes']
        name = name_constant.decode('utf-8')
        
        if name == 'main':
            for attr in method['attributes']:
                attribute_name_index = attr['attribute_name_index']
                attribute_name_constant = constant_pool[attribute_name_index]['bytes']
                attribute_name = attribute_name_constant.decode('utf-8')
                
                if attribute_name == 'Code':
                    info = attr['info']
                    info_io = io.BytesIO(info)
                    max_stack = int.from_bytes(info_io.read(2))
                    max_locals = int.from_bytes(info_io.read(2))
                    code_length = int.from_bytes(info_io.read(4))
                    code = info_io.read(code_length)

                    print('max_stack', max_stack)
                    print('max_locals', max_locals)
                    print('code_length', code_length)
                    print('code', code)

                    l = len(code)
                    i = 0
                    while i < l:
                        op = code[i]
                        if op == op_code['getstatic']:
                            print('getstatic')
                            val = code[i+1] << 8 | code[i+2]
                            # print(val)
                            i+=3
                        elif op == op_code['ldc']:
                            print('ldc')
                            val = code[i+1]
                            # print(val)
                            val2 = constant_pool[val]['string_index']
                            print(constant_pool[val2])
                            i+=2
                        elif op == op_code['invokevirtual']:
                            print('invokevirtual')
                            val = code[i+1] << 8 | code[i+2]
                            print(constant_pool[constant_pool[constant_pool[val]['name_and_type_index']]['name_index']])
                            i+=3
                        elif op == op_code['return']:
                            print('return')
                            i+=1
                        else:
                            print(op)
                            assert False
