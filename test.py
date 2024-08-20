SLOT_CUBE_TYPE = ["SMALL", "SMALL", "SMALL"]

def test(slotCubeType):
    if 'LARGE' in slotCubeType:
        print("LARGE")
    elif 'MID' in slotCubeType:
        print("MID")
    elif 'SMALL' in slotCubeType:
        print("SMALL")

print(SLOT_CUBE_TYPE)
test(SLOT_CUBE_TYPE)
print(SLOT_CUBE_TYPE)