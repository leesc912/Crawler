from argparse import ArgumentTypeError

def bool_spelling_check(string) :
    if string.lower() == 'true' :
        return True
    elif string.lower() == 'false' :
        return False
    else :
        raise ArgumentTypeError(
            "\n\ttrue, false만 입력 가능 (입력된 값 : {})\n".format(string))
        
def level_spelling_check(string) :
    if string not in ["초급", "중급", "고급"] :
        raise ArgumentTypeError(
            "\n\t초급, 중급, 고급만 입력 가능 (입력된 값 : {})\n".format(string))
    else :
        return string