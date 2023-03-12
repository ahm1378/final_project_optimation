import time
from genetic_improved import get_model_cost
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
import numpy as np
import pythoncom
from genetic_improved import *


def calculate(array,coef):
    fit = []
    print(len(array))
    for data in array:
        fit.append(cost_function(data, coef))

    return fit



@api_view(['POST', "GET"])
def send_data(request):
    pythoncom.CoInitialize()
    data = request.data.get('data')
    coef = request.data.get('coef')
    np_array = np.array(data)
    result = calculate(np_array,coef)
    #time.sleep(10 * 60)
    return Response(data=result, status=status.HTTP_200_OK)
