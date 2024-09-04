import re
import logging
import numpy as np
log_file = "putty-reg10-500-interrupt.log"
output_file_name= "../analyzer-outputs/matrixtester-" + log_file
logging.basicConfig(level=logging.INFO, filename=output_file_name,filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")

#region core test functions

def dimensionality_check(matrix1):
    row_quantity = matrix1.__len__()
    if row_quantity != 40:
        logging.error("dimensionality_check  >> FAILED << row quantity: %s", row_quantity)
        return False
    
    column_quantity_list = [ i.__len__() for i in matrix1]
    for i in range(40):
        if(row_quantity != column_quantity_list[i]):
            logging.error("dimensionality_check  >> FAILED << in row: %s", i)
            return False
    logging.info("dimensionality_check  >> PASSED <<")
    return True

def same_value_check(matrix):
    for i in range (40):
        if(len(set(matrix[i])) != 1):
            logging.error("same_value_check      >> FAILED << in row: %s", i)
            return False

    logging.info("same_value_check      >> PASSED <<")
    return True

def identity_matrix_check(matrix1, matrix2):
    for i in range(40):
        if( list( set( matrix1[i]) | set( matrix2[i] ) ).__len__() > 1):
            logging.error("identity_matrix_check >> FAILED << in row: %s                note: Comparison of untouched and fault injected result matrixes.", i)
            return False
    logging.info("identity_matrix_check >> PASSED <<                note: Comparison of untouched and fault injected result matrixes.")
    return True

#endregion
untouched_matrix = []
fault_injected_matrix = []
matrix_1 = []
matrix_2 = []
#region initialization functions

def initialize_matrix(value, matrix):
    for i in range(0,40):
        for j in range (0,40):
            matrix[i][j] = value
    return matrix

untouched_matrix = [ [0.049200013279914855957031250000000000000000000000]*40 for _ in range(40)]

#endregion

def print_matrix_information(matrix1, columnQuantityList, currentsection):
    if currentsection == "iteration":
        logging.info(">> CRASH << ")
        return False
    else:
        dimensionality_check_result = dimensionality_check(matrix1)
        if dimensionality_check_result == True:
            same_value_check_result = same_value_check(matrix1)
        if(dimensionality_check_result == True and same_value_check_result == True):
            identity_matrix_check(matrix1, untouched_matrix)


def test_the_log_file(log_file):
    untouched_matrix = []
    fault_injected_matrix = []
    matrix_1 = []
    matrix_2 = []
    current_section = None
    columnQuantityList = []
    random_parameter_string = ""
    bitNumberIndex = 0
    matrix_1_value = 0.0
    matrix_2_value = 0.0
    matrix_golden_value = 0.0
    rowValues = []

    with open(log_file, 'r') as f:
        for line in f:
            if line.startswith("_____ITERATION"):
                a = list(map(int,re.findall(r'\d+', line)))
                if a[0] != 1:
                    print_matrix_information(fault_injected_matrix, columnQuantityList, current_section)
                current_section = "iteration"
                logging.info("_____ITERATION_ %d _____________________________________________________________________________________________________", a[0])

            elif line.startswith("---FAULT INJECTION INFORMATION---"):
                random_parameter_string += "Randomly obtained fault injection parameters:  "

            elif line.startswith("Register Number:"):
                random_parameter_string += "  " + line.strip()
            elif line.startswith("Bit Number:"):
                random_parameter_string += "  " + line.strip()
            elif line.startswith("RandomBit"):
                random_parameter_string += " " + line.strip()
            elif line.startswith("Prescaler value:"):
                random_parameter_string += " " + line.strip()
            elif line.startswith("Period value:"):
                random_parameter_string += " " + line.strip()
            elif line.startswith("Time Interrupt Occured:"):
                random_parameter_string += " " + line.strip()
            elif line.startswith("__RESULT MATRIX - fault injected:"):
                current_section = "fault_injected"
                logging.info("%s", random_parameter_string)
                random_parameter_string = ""
                fault_injected_matrix = []
                columnQuantityList = []
                logging.info("__RESULT MATRIX - fault injected:")
            elif line.startswith("|"):  # then it is the real matrix region
                rowValues = []
                #region get values from dirty values - log
                dirtyvalues = line.split("|")
                try:
                    dirtyvalues.remove('')
                except ValueError:
                    continue
                try:
                    dirtyvalues.remove('\n')
                except ValueError:
                    continue
                #endregion

                #region get the values in float format, if dirty than -1.1
                for dirtyvalue in dirtyvalues:
                    try:
                        rowValues.append(float(dirtyvalue))    
                    except ValueError:
                        rowValues.append(-1.1) 
                #endregion
                if current_section == "fault_injected":
                    fault_injected_matrix.append(rowValues)
            elif line.startswith("__RESULT MATRIX - untouched - golden:"):
                current_section = "golden"
            else:
                continue
comparison_data = test_the_log_file("../fault-injection-logs/" + log_file)