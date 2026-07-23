import copy
def main():
    a=[[1,2,3],[4,5,6],[7,8,9]]
    b=a.copy()
    c=copy.copy(a)
    d=copy.deepcopy(a)

    print("Original list 'a':", a)
    print("Shallow copy 'b':", b)
    print("Shallow copy 'c':", c)
    print("Deep copy 'd':", d)


if __name__ == "__main__":
    main()
