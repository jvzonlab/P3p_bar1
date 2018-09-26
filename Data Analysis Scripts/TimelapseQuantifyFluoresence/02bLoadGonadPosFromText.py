import matplotlib.pyplot as plt
import pickle
import pandas as pd
import seaborn as sns
import numpy as np

########################################################################################################################
###Options
experiment_date = '20180111'
worm_number = 'NewW7'

###############################################################
### Pickle file of worm 
f = 'G:\\Jason\\'+ str(experiment_date)+ '\\worm' + str(worm_number) + '.pickle'
### Excel file of coordinates for initial ROI
custom_f = 'G:\\Jason\\'+str(experiment_date)+'\\'+str(experiment_date)+'_'+str(worm_number)+'.xlsx'

exp = f[9:17]
worm = f[22:25]

print ("Experiment name is "+ exp + " & worm name is "+ worm)
print ("Experiment name is " + str(experiment_date) + " & worm name is " + str(worm_number))
###############################################################
###Load existing pickle from  the downsizing, and when the hatching was found

print ("Loading pickle file...")
df = pickle.load( open(f, "rb"))
print ("Pickle file has been loaded...")
if 'gonadPos' in df.columns:
    df = df.drop("gonadPos", 1)
    print (df)

###############################################################
###Read an excel or text file that contains the coordinates, X and Y
###add to a list... "list within a list"
###Gonad pos is a list item [x, y]
###append the [x, y] coordinates to the custom_df

print ("Loading excel file with the custom gonadPos...")
custom_df = pd.read_excel(custom_f, sheetname = 0, parse_cols = 3)
print ("Adding custom gonad position to each image in the dataframe...")
x_list = custom_df['custom_X'].tolist()
y_list = custom_df['custom_Y'].tolist()
xy_list = list(zip(x_list, y_list))
xy_list = list(map(list, xy_list))
custom_df['gonadPos'] = xy_list
custom_df = custom_df.drop('custom_Y', 1)
custom_df = custom_df.drop('custom_X', 1)
custom_df = custom_df.drop('custom_zFrame', 1)

##############################################################
### Merge the coordinates from the custom_df to the real df
### First decide or find out what time points should be added

combined_df = df.merge(custom_df, on= "tidx", how="left")
if 'gonadPos_x' in combined_df.columns:
    combined_df = combined_df.drop('gonadPos_x', 1)
if 'gonadPos_y' in combined_df.columns:
    combined_df = combined_df.drop("gonadPos_y", 1)
print(combined_df)

##############################################################
###Save the pickle file
pickle.dump(combined_df, open( f, "wb" ) )
print("Pickle file has been saved...")


