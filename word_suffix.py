'''
Напишите программу, считывающую с пользовательского ввода целое число nn (неотрицательное), 
выводящее это число в консоль вместе с правильным образом изменённым словом "программист"

'''

n=int(input())
if (n-11)%100!=0 and (n-1)%10==0:
    print(n,"программист")
elif ((n-12)%100!=0 and (n-13)%100!=0 and(n-14)%100!=0) and ((n-2)%10==0 or (n-3)%10==0 or(n-4)%10==0):
    print(n,"программиста")
else:
    print(n,"программистов")

