__author__ = 'traets'
import pickle
file = open("F:\\Data_smFISH\\Genotype_ST65\\20160614\\batch1\\20160614_batch1.plk",'rb')
object_file = pickle.load(file)


print(object_file.POI['worm_1'])
print(object_file.ROI['worm_1'])
print(object_file.spots)
print(object_file.list_worms)

