import csv;

def main():
  file = open('Copy of 2024_Arrest_Data.csv', mode='r');
  csv_reader = csv.reader(file);

  oldData = [];
  for line in csv_reader:
    oldData.append(line);

  data = [];
  current = 0;
  for line in oldData:
    #take care of the header
    if current == 0: 
      data.append(line);
      current += 1;
      continue;
    #combine the rest of the data
    #if same arrestID
    if line[0] == data[-1][0]:
      #things to modify: statue, statute_description, IBR code, IBR description, felonymisdemenor
      #get the old arrays
      statute = data[-1][13];
      statute_description = data[-1][14];
      ibr_code = data[-1][15];
      ibr_description = data[-1][16];
      felony_misdemeanor = data[-1][17];

      #add the new stuff to the arrays
      statute.append(line[13]);
      statute_description.append(line[14]);
      ibr_code.append(line[15]);
      ibr_description.append(line[16]);
      felony_misdemeanor.append(line[17]);

    else:
      line[13] = [line[13]];
      line[14] = [line[14]];
      line[15] = [line[15]];
      line[16] = [line[16]];
      line[17] = [line[17]];
      data.append(line);

  #transform it all into strings
  for line in data:
    for j in range(len(line)):
      if j in {13, 14, 15, 16, 17}:
        line[j] = f"{line[j]}";

  file2 = open('output.csv', mode= 'w', newline="");
  csv_write = csv.writer(file2);
  csv_write.writerows(data);

if __name__ == "__main__":
  main();