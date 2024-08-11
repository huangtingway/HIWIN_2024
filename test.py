SORT_LARGE_ORG_POS = [-343.0 ,254.0  ,160  ,180.0  ,0.0  ,180.0] #分揀位置原點(大)

def test(position, testval):
    position[2] += testval
    print(position)

print(SORT_LARGE_ORG_POS)
test(SORT_LARGE_ORG_POS.copy(), 100)
print(SORT_LARGE_ORG_POS)