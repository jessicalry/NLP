import math

def cos_sim(l1,l2):
    numerator = sum([a * b for a, b in zip(l1,l2)])
    sumA = 0
    sumB = 0
    for num in l1:
        sumA+=num**2
    for numm in l2:
        sumB+=numm**2
    denom = math.sqrt(sumA*sumB)
    print(numerator/denom)
    return numerator/denom


cos_sim([0,5,0,5,0],[0,7,0,9,0])