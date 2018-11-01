import json
import random

def main():
    targetList = [i for i in range(256)]
    random.shuffle(targetList)
    sourceTargetMap = dict()
    for i in range(256):
        sourceTargetMap[i] = targetList[i]
    print('generate map:',sourceTargetMap)
    fileDir = '../KeyMap.json'
    with open(fileDir,'w') as f:
        json.dump(sourceTargetMap,f)
    print("saved to ",fileDir)

if __name__ == '__main__':
    main()

