import io
from jvm_opcode import op_code

def parse_u1(fin):
    return int.from_bytes(fin.read(1))

def parse_u2(fin):
    return int.from_bytes(fin.read(2))

def parse_u4(fin):
    return int.from_bytes(fin.read(4))

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

ACCESS_FLAGS = dict(
    ACC_PUBLIC = 0x0001,
    ACC_FINAL = 0x0010,
    ACC_SUPER = 0x0020,
    ACC_INTERFACE = 0x0200,
    ACC_ABSTRACT = 0x0400,
    ACC_SYNTHETIC = 0x1000,
    ACC_ANNOTATION = 0x2000,
    ACC_ENUM = 0x4000
)

def get_flags(flag_map, flag):
    return [k for k, v in flag_map.items() if (v & flag != 0)]

def parse_attributes(fin, attributes_count):
    attributes = []
    for i in range(attributes_count):
        attribute_name_index = parse_u2(fin)
        attribute_length = parse_u4(fin)
        info = fin.read(attribute_length)
        attributes.append({
            'attribute_name_index': attribute_name_index,
            'attribute_length': attribute_length,
            'info': info
        })
    return attributes

def parse_constant_pool(fin, constant_pool_count):
    constant_pool = [None]
    for i in range(1, constant_pool_count):
        tag = parse_u1(fin)
        if tag == CONSTANT_Methodref or tag == CONSTANT_Fieldref or tag == CONSTANT_InterfaceMethodref:
            class_index = parse_u2(fin)
            name_and_type_index = parse_u2(fin)
            constant_pool.append({
                'tag': tag,
                'class_index': class_index,
                'name_and_type_index': name_and_type_index
            })

        elif tag == CONSTANT_String:
            string_index = parse_u2(fin)
            constant_pool.append({
                'tag': tag,
                'string_index': string_index
            })
        
        elif tag == CONSTANT_Class:
            name_index = parse_u2(fin)
            constant_pool.append({
                'tag': tag,
                'name_index': name_index
            })

        elif tag == CONSTANT_Utf8:
            length = parse_u2(fin)
            bytes_ = fin.read(length)
            constant_pool.append({
                'tag': tag,
                'length': length,
                'bytes': bytes_
            })
        
        elif tag == CONSTANT_NameAndType:
            name_index = parse_u2(fin)
            descriptor_index = parse_u2(fin)
            constant_pool.append({
                'tag': tag,
                'name_index': name_index,
                'descriptor_index': descriptor_index
            })
        else:
            assert False, f"Tag not implemented: {tag}"
    return constant_pool

class JVMClass:
    def __init__(self, class_name):
        self.class_name = class_name
        self.classFile = {}

        with open(f'{class_name}.class', 'rb') as fin:
            magic = parse_u4(fin)
            assert magic == 0xCAFEBABE, "Invalid class file"

            self.classFile['magic'] = hex(magic)
            self.classFile['minor_version'] = parse_u2(fin)
            self.classFile['major_version'] = parse_u2(fin)
            self.classFile['constant_pool_count'] = parse_u2(fin)
            self.classFile['constant_pool'] = parse_constant_pool(fin, self.classFile['constant_pool_count'])
            self.classFile['access_flags'] = parse_u2(fin)
            self.classFile['this_class'] = parse_u2(fin)
            self.classFile['super_class'] = parse_u2(fin)
            self.classFile['interfaces_count'] = parse_u2(fin)

            for i in range(self.classFile['interfaces_count']):
                assert False, 'Interfaces not implemented'
            
            self.classFile['fields_count'] = parse_u2(fin)
            self.classFile['methods_count'] = parse_u2(fin)

            methods = []
            for i in range(self.classFile['methods_count']):
                method = {}
                method['access_flags'] = parse_u2(fin)
                method['name_index'] = parse_u2(fin)
                method['descriptor_index'] = parse_u2(fin)
                method['attributes_count'] = parse_u2(fin)
                method['attributes'] = parse_attributes(fin, method['attributes_count'])
                methods.append(method)

            self.classFile['methods'] = methods
            self.classFile['attributes_count'] = parse_u2(fin)
            self.classFile['attributes'] = parse_attributes(fin, self.classFile['attributes_count'])

    def get_classFile(self):
        return self.classFile
    
    def get_constant(self, idx):
        return self.classFile['constant_pool'][idx]

    def get_method_by_name(self, name: bytes):
        for method in self.classFile['methods']:
            method_name = self.get_constant(method['name_index'])['bytes']
            if method_name == name:
                return method
        return None

    def get_code_attribute(self, method):
        code_attr = {}
        for attr in method['attributes']:
            attr_name = self.get_constant(attr['attribute_name_index'])['bytes']
            if attr_name == b'Code':
                info = attr['info']
                info_io = io.BytesIO(info)
                code_attr['max_stack'] = parse_u2(info_io)
                code_attr['max_locals'] = parse_u2(info_io)
                code_attr['code_length'] = parse_u4(info_io)
                code_attr['code'] = info_io.read(code_attr['code_length'])

                return code_attr
        return None

    def execute(self, code_attr):
        code_io = io.BytesIO(code_attr['code'])

        while code_io.tell() < len(code_attr['code']):
            op = parse_u1(code_io)

            if op == op_code['getstatic']:
                print('getstatic')
                val = parse_u2(code_io)
            elif op == op_code['ldc']:
                print('ldc')
                val = parse_u1(code_io)
            elif op == op_code['invokevirtual']:
                print('invokevirtual')
                val = parse_u2(code_io)
            elif op == op_code['return']:
                print('return')
            elif op == op_code['invokespecial']:
                print('invokespecial')
                val = parse_u2(code_io)
            elif op == op_code['aload_0']:
                print('aload_0')
            elif op == op_code['iload_0']:
                print('iload_0')
            elif op == op_code['iconst_1']:
                print('iconst_1')
            elif op == op_code['iadd']:
                print('iadd')
            elif op == op_code['ireturn']:
                print('ireturn')
            else:
                print(hex(op))
                assert False, 'Op Code Not implemented'