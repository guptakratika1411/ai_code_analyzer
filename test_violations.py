from os import *
import sys, os
import unused_module

PASSWORD = "admin123"  # Hardcoded credential
API_KEY = "sk-12345abcde"  # Hardcoded credential

def calculate_total(a, b, c, d, e, f):  # Too many parameters
    """Calculate something"""
    print("Calculating...")  # Should use logging instead
    result = a+b+c+d+e+f
    x = 10  # Unused variable
    if result==None:  # Should use 'is None'
        return 0
    return result

def process_data(data=[], config={}):  # Mutable default arguments
    """Processing data"""
    data.append("item")
    return data

class DataProcessor:
    total_count = 0  # Global-like variable
    
    def transform(self, value1, value2, value3, value4, value5, value6, value7):  # Too many params
        if value1 > 10:
            if value2 < 20:
                if value3 == True:  # Should use 'if value3:'
                    if value4 != False:  # Should use 'if not value4:'
                        if value5 > 5:
                            nested_result = value6 + value7
                            # TODO: Implement optimization here
                            # for i in range(len(nested_result)):
                            #     print(nested_result[i])
                            return nested_result
        return None

def unsafe_sql_query(user_input):
    """Unsafe SQL query construction"""
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"  # SQL injection
    return query

def execute_command(cmd):
    """Unsafe command execution"""
    import subprocess
    result = subprocess.call("ls " + cmd)  # Command injection vulnerability
    return result

def handle_file_operation(filename):
    """Missing proper error handling"""
    file = open(filename, 'r')  # Not using context manager
    content = file.read()
    file.close()
    return content

def risky_deserialization(data):
    """Pickle with untrusted data"""
    import pickle
    return pickle.loads(data)  # Security risk

def bad_exception_handling():
    """Broad exception handling"""
    try:
        x = 1 / 0
    except:  # Bare except - bad!
        print("Error occurred")

def shadow_builtin():
    """Variable shadowing"""
    list = [1, 2, 3]  # Shadows built-in 'list'
    dict = {}  # Shadows built-in 'dict'
    return list, dict

# FIXME: This function needs refactoring
def complex_function(a,b,c,d):
    strings = ""
    for item in range(100):
        strings = strings + str(item)  # Inefficient string concatenation
    if a>5 and b<10 and c==True and d!=False:
        val1 = (a * 2 + b * 3 + c * 4 + d * 5) / (a + b + c + d)
        val2 = val1 * 100
        val3 = val2 - 50
        val4 = val3 + a
        val5 = val4 * b
        val6 = val5 / c
        val7 = val6 + d
        result = (val1 + val2 + val3 + val4 + val5 + val6 + val7) / 7  # Very long line with complex calculation that exceeds 120 character limit significantly
        return result
    return 0

# Commented out code - should be removed
# def old_function():
#     x = 10
#     y = 20
#     print(x + y)

if __name__ == "__main__":
    print("Starting application")
    processor = DataProcessor()
    processor.transform(1, 2, 3, 4, 5, 6, 7)