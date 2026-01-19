import csv;
import statistics;
from sklearn import tree as sk;
import sklearn.model_selection as sk1;
from sklearn.naive_bayes import CategoricalNB;
from sklearn.preprocessing import OrdinalEncoder;
from sklearn import tree;
level1Models = [];
r1 = 5;
r2 = 6;
r3 = 10;
categories = ["ON-VIEW ARREST", "TAKEN INTO CUSTODY", "SUMMONED/ CITED"];
ogData = [];

def main():
  #read in the data
  data2 = processData("arrayifiedData.csv");
  #ask user what model they want to test with
  subModelName = input("What subModel do you want to use?: ");
  global ogData;
  ogData = [[] for d in range(len(data2[0]))];

  #array rows
  arrRows = [12, 13, 14, 15, 16];

  #screw around with the data so that scikit learn will be ok with it
  if subModelName != "1R":
    data1 = changeNonArrayVals(data2[1:], arrRows);
    data1 = changeClass(data1);
    data1 = changeArrayVals(data1, arrRows);
  else:
    data1 = data2[1:];
    

  #split the data
  data, test = sk1.train_test_split(data1, train_size=0.7, test_size=0.3, random_state=1880333);

  #build all of the oneR models
  buildArrayModels(arrRows, data, subModelName);

  #run all of the predictions on data and test
  dataTransformed = transformData(arrRows, data, subModelName);
  testTransformed = transformData(arrRows, test, subModelName);
 
  #if had to be transformed, change it back
  if subModelName != "1R":
    for i in range(len(data2[0])-1):
      if i in arrRows:
        continue;
      for j in range(len(dataTransformed)):
        dataTransformed[j][i] = ogData[i][dataTransformed[j][i]];
      for j in range(len(testTransformed)):
        testTransformed[j][i] = ogData[i][testTransformed[j][i]];
  print(dataTransformed[0]);
  
  #export it all to csv files
  file2 = open('level1Train.csv', mode= 'w', newline="");
  csv_write = csv.writer(file2);
  csv_write.writerows(dataTransformed);

  file3 = open('level1Test.csv', mode = 'w', newline="");
  csv_write = csv.writer(file3);
  csv_write.writerows(testTransformed);

  file4 = open('level1Both.csv', mode = 'w', newline="");
  csv_write = csv.writer(file4);
  csv_write.writerows(dataTransformed + testTransformed);

############################################################### Change values #################################################################################
def changeNonArrayVals(data, arrayRows):
  global ogData;
  for d in range(len(data[0])-1):
    if d in arrayRows:
      continue;
    #find all the possible values
    possibleVals = [];
    for i, val in enumerate([dataPoint[d] for dataPoint in data]):
      if val not in possibleVals: possibleVals.append(val);
      data[i][d] = possibleVals.index(data[i][d]);
    ogData[d] = possibleVals;
  return data;
      
def changeClass(data):
  for d in data:
    d[-1] = categories.index(d[-1]);
  return data;

def changeArrayVals(data, arrayRows):
  #this function is going to give all of the array values a number
  global ogData;
  #start by finding all possible values
  for arrayRow in arrayRows:
    possibleVals = [];
    for i, subArray in enumerate([[dataPoint.strip("'[] ") for dataPoint in d[arrayRow].split("', '")] for d in data]):
      newSubArray = [];
      for val in subArray:
        if val not in possibleVals: possibleVals.append(val);
        newSubArray.append(possibleVals.index(val));
      data[i][arrayRow] = newSubArray;
    ogData[arrayRow] = possibleVals;

  return data;

############################################################### File reading ##################################################################################

def processData(filename):
 #process the data
  returnable = [];
  file = open(filename, "r");
  csv_reader = csv.reader(file);
  for row in csv_reader:
    returnable.append([*row]);
  file.close();
  return returnable;

############################################################### 1R Methods ####################################################################################

def build1RModel(data):
  #counter keeps track of vals in this way --> {value of attribute1: {class1: count, class2: count}, etc.}
  counter = {};

  for row in range(len(data)):
    val = getVal(row, 0, data);
    class1 = getClass(row, data);

    if val in counter:
      if class1 in counter[val]: counter[val][class1] += 1;
      else: counter[val][class1] = 1;
    else:
      counter[val] = {};
      counter[val][class1] = 1;

  #val: class
  newRule = {};
  for val in counter:
    newRule[val] = getMax(counter[val]);
  return newRule;

def getVal(row, attribute, data):
  return data[row][attribute];

def getClass(row, data):
  return data[row][-1];

def getMax(vals):
  value = None;
  max = 0;
  for v in vals:
    if vals[v] > max: 
      max = vals[v];
      value = v;
  return value;

############################################################### Generalized model building ######################################################################

def buildArrayModels(cols, data, subModelName):
  global level1Models;
  #train on data and build all of the models
  for column in cols:
    if subModelName == "1R":
      inputs = [];
      for c in data:
        for j in [dataPoint.strip("'[] ") for dataPoint in c[column].split("', '")]:
          inputs.append([j, c[-1]]);
      clf = build1RModel(inputs);
      level1Models.append(clf);

    elif subModelName == "NB":
      inputs = [];
      outputs = [];
      for c in data:
        for j in c[column]:
          inputs.append([c[r1], c[r2], c[r3], j]);
          outputs.append(c[-1]);
      clf = CategoricalNB();
      clf.fit(inputs, outputs);
      level1Models.append(clf);

    elif subModelName == "DT":
      inputs = [];
      outputs = [];
      for c in data:
        for j in c[column]:
          inputs.append([c[r1], c[r2], c[r3], j]);
          outputs.append(c[-1]);
      clf = tree.DecisionTreeClassifier();
      clf.fit(inputs, outputs);
      level1Models.append(clf);
      


############################################################### Model Predicting ################################################################################

def makePrediction1R(input, modelIndex):
  #make the prediction from the tree
  if input in level1Models[modelIndex]:
    return level1Models[modelIndex][input];
  else:
    return "ON-VIEW ARREST";
  

def makePrediction(input, modelIndex, subModelName):
  #figure out how it should make prediction
  if subModelName == "1R":
    return makePrediction1R(input, modelIndex);
  else:
    try:
      return categories[level1Models[modelIndex].predict(input)[0]];
    except:
      print(input);
      return "ON-VIEW ARREST";



def transformData(cols, data, subModelName):
  newData = data; 
  #transform all of the data
  for i, column in enumerate(cols):
    inputs = [];
    if subModelName == "1R":
      inputs = [[dataPoint.strip("'[] ") for dataPoint in c[column].split("', '")] for c in data];
    else:
      inputs = [c[column] for c in data];
    outputs = [];
    if subModelName == "1R": outputs = [[makePrediction(k, i, subModelName) for k in j] for j in inputs];
    else: outputs = [[makePrediction([[data[index][r1], data[index][r2], data[index][r3], k]], i, subModelName) for k in j] for index, j in enumerate(inputs)];
    for j in range(len(data)):
      newVal = statistics.mode(outputs[j]);
      data[j][column] = newVal;
  return newData;

def runTest(clf, test, subModelName):
  correct = 0.0;
  total = 0.0;
  for t in test:
    prediction = makePrediction(t[:-1], clf, subModelName);
    if t[-1] == prediction and t[-1] == "ON-VIEW ARREST": correct += 1.0;
    elif t[-1] == prediction and t[-1] == "TAKEN INTO CUSTODY": correct += 1.0;
    elif t[-1] == prediction and t[-1] == "SUMMONED/ CITED": correct += 1.0;
    total += 1.0;
  return correct/total;

if __name__ == "__main__":
  main();
