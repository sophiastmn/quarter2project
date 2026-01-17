import csv;
import statistics;
from sklearn import tree as sk;
import sklearn.model_selection as sk1;
level1Models = [];

def main():
  #read in the data
  data1 = processData("arrayifiedData.csv");
  print(data1[1]);

  #split the data
  data, test = sk1.train_test_split(data1[1:], train_size=0.7, test_size=0.3, random_state=1880333);

  #array rows
  arrRows = [12, 13, 14, 15, 16];

  #build all of the oneR models
  buildArrayModels(arrRows, data);

  #run all of the predictions on data and test
  dataTransformed = transformData(arrRows, data);
  testTransformed = transformData(arrRows, test);
  
  #export it all to csv files
  file2 = open('level1Train.csv', mode= 'w', newline="");
  csv_write = csv.writer(file2);
  csv_write.writerows(dataTransformed);

  file3 = open('level1Test.csv', mode = 'w', newline="");
  csv_write = csv.writer(file3);
  csv_write.writerows(testTransformed);

def processData(filename):
 #process the data
  returnable = [];
  file = open(filename, "r");
  csv_reader = csv.reader(file);
  for row in csv_reader:
    returnable.append([*row]);
  file.close();
  return returnable;

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

def buildArrayModels(cols, data):
  global level1Models;
  #train on data and build all of the models
  for column in cols:
    inputs = [];
    print(data[0][column]);
    for c in data:
      for j in [dataPoint.strip("'[] ") for dataPoint in c[column].split(",")]:
        inputs.append([j, c[-1]]);

    clf = build1RModel(inputs);
    level1Models.append(clf);

def makePrediction(input, modelIndex):
  #make the prediction from the tree
  if input in level1Models[modelIndex]:
    return level1Models[modelIndex][input];
  else:
    return "ON-VIEW ARREST";

def transformData(cols, data):
  newData = data; 
  #transform all of the data
  for i, column in enumerate(cols):
    inputs = [[dataPoint.strip("'[] ") for dataPoint in c[column].split(",")] for c in data];
    outputs = [[makePrediction(k, i) for k in j] for j in inputs];
    for j in range(len(data)):
      newVal = statistics.mode(outputs[j]);
      data[j][column] = newVal;
  return newData;
    

def runTest(clf, test):
  #a == onViewArrest, b == takenIntoCustody, c == summoned/cited
  cmatrix = [0, 0, 0, 0, 0, 0, 0, 0, 0];
  total = 0;
  for t in test:
    prediction = makePrediction(t[:-1], clf);
    if t[-1] == prediction and t[-1] == "ON-VIEW ARREST": cmatrix[0] += 1;
    elif t[-1] == prediction and t[-1] == "TAKEN INTO CUSTODY": cmatrix[4] += 1;
    elif t[-1] == prediction and t[-1] == "SUMMONED/ CITED": cmatrix[8] += 1;
    elif prediction == "TAKEN INTO CUSTODY" and t[-1] == "ON-VIEW ARREST": cmatrix[1] += 1;
    elif prediction == "SUMMONED/ CITED" and t[-1] == "ON-VIEW ARREST": cmatrix[2] += 1;
    elif prediction == "ON-VIEW ARREST" and t[-1] == "TAKEN INTO CUSTODY": cmatrix[3] += 1;
    elif prediction == "SUMMONED/ CITED" and t[-1] == "TAKEN INTO CUSTODY": cmatrix[5] += 1;
    elif prediction == "ON-VIEW ARREST" and t[-1] == "SUMMONED/ CITED": cmatrix[6] += 1;
    else: cmatrix[7] += 1;
    total += 1;
  return cmatrix;


def confusionMatrix(cmatrix):
    print("Confusion Matrix");
    print(f"Predictions:              onViewArrest     takenIntoCustody       summoned/Cited");
    print(f"Actual: onViewArrest        {cmatrix[0]}           {cmatrix[1]}             {cmatrix[2]}");
    print(f"Actual: takenIntoCustody    {cmatrix[3]}           {cmatrix[4]}             {cmatrix[5]}");
    print(f"Actual: summoned/Cited      {cmatrix[6]}           {cmatrix[7]}             {cmatrix[8]}");

def accuracy(cmatrix):
  acc = (cmatrix[0] + cmatrix[4] + cmatrix[8])/sum(cmatrix);
  print(f"Accuracy: {acc}");
  return acc;
  

if __name__ == "__main__":
  main();