# f = open('myFile.txt','a')
# f.write('This is new line')
import os


# print(conent)
# for line in f:
#     number_of_lines+=1
#
#     number_of_words += line.count(' ')+1
#     # for word in line.split():
#         # number_of_words+=1
#         # print(word,end='-')
#     print()
# f.close()
#create file
# f=open('file1.txt','w')
# f.write('Hello World\nthis is new file\ncreated by me')
# f=open('file1.txt')
# print(f.read())

# ignoring errors if file is not exist
try:
    f=open('myddFile.txt','r')
    # print(f.read())
    conent=f.read()
    number_of_lines=conent.count('\n')+1
    number_of_words=conent.count(' ')+number_of_lines
    print(f"Number of Lines: {number_of_lines}\nNumber of Words: {number_of_words}")
except:
    print('file is not exist')

# if os.path.exists('myddFile.txt'):
#     f=open('myddFile.txt')
# else:
#     print('not exist')


# removing file
rmv=input('y to delete file and c to cancel')
if rmv=='y':
    os.remove('file1.txt')
    print('file deleted successfully')


