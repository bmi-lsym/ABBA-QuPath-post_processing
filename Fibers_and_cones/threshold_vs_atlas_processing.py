# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 21:27:39 2023

@author: Admin
"""


import pandas as pd

# Set the folder path to the .csv file created by the fiber_cone tool
fpath="D:\\Data\\Folder\\"
# Set the suffix of the .csv filenames
ftype="_aligned_th_x_ROIs.csv"
# Generate the list of file prefixes
fprefix=["jy"+str(i+1).zfill(2) for i in range(17)]

df_pooled=pd.DataFrame()

# Define the list of brain areas to include into the results
select_grand_areas=["VISC1","VISC2/3","VISC4","VISC5","VISC6a", "SSs1","SSs2/3","SSs4","SSs5","SSs6a", "SSp", "AIp1","AIp2/3","AIp5","AIp6a","TEa", "AUDv", "ECT", "PERI", "ENT", "CLA", "EPd", "EPv", "PIR"]

# Here, define the list of the parent (or same) brain areas for the one above
# Overall, the total area of these regions should include (=cover) ALL regions from the list above 
grand_areas=["Isocortex", "CLA", "EP", "OLF","ENT"]
  
for k, fp in enumerate(fprefix):
    df=pd.read_csv(fpath+fp+ftype, index_col=0, encoding='cp1252')
    df["brain_area"]=df["Label"].apply(lambda row: row.split(" x ")[1])
    brain_areas=list(df["brain_area"].unique())
    volumes=[]
    slices=[]
    for br in brain_areas:
        df_br=df.where(df["brain_area"]==br).dropna()
        volumes.append(df_br["Area (µm^2)"].sum())
        slices.append(",".join([str(int(s)) for s in df_br["Slice"].to_list()]))
    
    
    d={"Animal":fp, "Brain area":brain_areas, "Total area (µm^2)":volumes, "List of slices":slices}
    res_df_all=pd.DataFrame(data=d)
    res_df_all.sort_values(by=["Brain area"], axis=0, ascending=True, inplace=True, ignore_index=True)
   
    res_df_grands=res_df_all[res_df_all["Brain area"].isin(select_grand_areas)].copy()
    tot_a=res_df_grands["Total area (µm^2)"].sum()
    
    df_grands=res_df_all[res_df_all["Brain area"].isin(grand_areas)].copy()
    total_grands=df_grands["Total area (µm^2)"].sum()
    
    #d_grands={"Animal":fp, "Brain area":"Others", "Total area (µm^2)":total_grands-tot_a, "List of slices":""}
    #res_df_grands=pd.concat([res_df_grands, pd.DataFrame([d_grands])], axis=0, ignore_index = True)
    
    res_df_grands["Norm. area"]=res_df_grands["Total area (µm^2)"].apply(lambda row: row/tot_a*100)
    df_pooled=pd.concat([df_pooled,res_df_grands], ignore_index = True)

df_pooled.reset_index()

pooled_brain_areas=list(df_pooled["Brain area"].unique())
pooled_brain_areas.sort()
#pooled_brain_areas.remove("Others")
#pooled_brain_areas.append("Others")

print(pooled_brain_areas)

df_summary_abs=pd.DataFrame()
df_summary_norm=pd.DataFrame()

for fp in fprefix:
    d_abs_data={"Animal":fp}
    d_norm_data={"Animal":fp}
    df_per_mouse=df_pooled[df_pooled['Animal']==fp]
    for br in pooled_brain_areas:
        abs_area=df_per_mouse[df_per_mouse['Brain area']==br]["Total area (µm^2)"]
        norm_area=df_per_mouse[df_per_mouse['Brain area']==br]["Norm. area"]
        if (abs_area.shape[0]>0):
            d_abs_data[br]=abs_area.item()
            d_norm_data[br]=norm_area.item()
        else:
            d_abs_data[br]=0
            d_norm_data[br]=0
    
    
    df_summary_abs=pd.concat([df_summary_abs, pd.DataFrame([d_abs_data])], axis=0, ignore_index = True)
    df_summary_norm=pd.concat([df_summary_norm, pd.DataFrame([d_norm_data])], axis=0, ignore_index = True)
           
pooled_brain_areas.insert(0,"Animal")
df_summary_abs=df_summary_abs[pooled_brain_areas]
df_summary_norm=df_summary_norm[pooled_brain_areas]


# Saving the results
df_pooled.to_csv(fpath+"ALL"+ftype)
df_summary_abs.to_csv(fpath+"SUMMARY_ABS"+ftype)
df_summary_norm.to_csv(fpath+"SUMMARY_NORM"+ftype)