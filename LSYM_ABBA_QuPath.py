import pandas as pd
import numpy as np
import os
from paquo.projects import QuPathProject
import jpype
import jpype.imports
import untangle
from jpype.types import *
from qupath.lib.gui.measure import ObservableMeasurementTableData
import urllib.parse
import json
from zipfile import ZipFile


def create_subfolders(ABBA_json, path_prefix, path_prefix_results, result_filename):
    
    allen_json_location="atlas_ontology/1.json" #local copy of the file
    df_atlas=flatten_json_ontology(pd.read_json(allen_json_location) ,[0,0])
 
    ## alternative source 1: read the official Allen Brain Atlas json file:
    #allen_json_location="http://api.brain-map.org/api/v2/structure_graph_download/1.json" #web location
    ## alternative source 2: location used by ABBA
    #allen_json_location="https://zenodo.org/record/4486659/files/1.json" #reserve web location of the file
    ## alternative source 3: from a local flattened csv file: 
    #atlas_tree="atlas_ontology/structure_tree_safe_2017.csv"
    #df_atlas=pd.read_csv(atlas_tree)
    
    
    #creating the subfolders

    try: 
        os.mkdir(path_prefix) 
    except OSError as error:
        if str(error).startswith("[WinError 183]")==False:
            print(error)
    
    try: 
        os.mkdir(path_prefix_results) 
    except OSError as error:
        if str(error).startswith("[WinError 183]")==False:
            print(error)
      

    #parsing the ABBA project data and generating the initial index file ("*_autoindex.xlsx")
    abba_extension="".join(ABBA_json.split(".")[-1])
    
    if (abba_extension.lower()=="json"): #old versions
        df_abba=pd.read_json(ABBA_json)
        df_abba_src=pd.read_json(ABBA_json.partition(".json")[0]+"_sources.json")
        abba_path="" #for the older versions        
    elif (abba_extension.lower()=="abba"): #new version>=0.5.2, need to unzip
        abba_path="\\".join(ABBA_json.split("\\")[:-1])+"\\unzip_tmp_fldr\\" #for the new versions >=0.5.2
        with ZipFile(ABBA_json, 'r') as zip_ref:
            fnames=[name for name in zip_ref.namelist()]
            zip_ref.extractall(abba_path)
        df_abba=pd.read_json(abba_path+"state.json")
        df_abba_src=pd.read_json(abba_path+"sources.json")
    else:
        print("Unknown extension of the ABBA project file ('",abba_extension,"'), please check.")
        return None, None
    
    print("Detected ABBA version %s, parsing..." % df_abba["version"].drop_duplicates()[0])
    
    df_index=parse_abba_project(df_abba, df_abba_src, abba_path)

    df_index.to_excel(path_prefix+result_filename+"autoindex.xlsx",index=False)

    print("\nBased on ABBA project, created a template index file: \n"+path_prefix+result_filename+"autoindex.xlsx")
    print(" -> It can be manually modified, if necessary, to update the list of images which will be processed")
    print(" -> Please make sure that the working index file is specified in the next cell")
    
        
    if (abba_extension.lower()=="abba"): #clean-up temporarily unpacked files
        for fname in fnames:
            try:
                os.remove(abba_path+fname)
            except OSError as e:
                print("Error: %s file could not be deleted. %s" % (e.filename, e.strerror))
        try:
            os.rmdir(abba_path)
        except OSError as e:
            print("Temporary folder %s could not be deleted. %s" % (abba_path, e.strerror))
     
    
    return df_atlas, df_index



def parse_abba_project(df_abba, df_abba_src, abba_path):
    AP_coords_ABBA=[]
    sources_ABBA=[]
    xml_data=[]
    qp_projs=[]

    for i in range(df_abba.shape[0]):
        df_tmp=pd.json_normalize(pd.json_normalize(df_abba.loc[i,"slices_state_list"]).loc[0,"actions"])
        idx_lst=df_tmp.loc[0,"original_sources.source_indexes"]
        sources_ABBA.append(df_abba_src.loc[idx_lst[0],"source_name"]+".csv")
        if "location" in df_tmp:
            locs=df_tmp["location"].dropna()
            AP_coords_ABBA.append(locs.iloc[locs.shape[0]-1])
        else:
            AP_coords_ABBA.append(df_tmp.loc[0,"original_location"])
        xml_data.append(pd.json_normalize(df_abba_src.loc[idx_lst[0],"sac"]).loc[0,"spimdata.datalocation"])

               
    xml_data_files=pd.Series(xml_data, copy=False).drop_duplicates()
    for i in range(xml_data_files.shape[0]):    
        obj = untangle.parse(abba_path+xml_data_files.iloc[i])
        try: #try old style xml file
            s=obj.SpimData.SequenceDescription.ImageLoader.qupath_project.cdata
        except AttributeError: 
            s=""
        if (len(s)>0):
            qp_projs = [s[1:-1].partition("file:/")[2] if x == xml_data_files.iloc[i] else x for x in xml_data]
            xml_data=qp_projs
        else: #try the new style
            try:
                s=obj.SpimData.SequenceDescription.ImageLoader.openers.cdata                
            except AttributeError:
                s=""
            if (len(s)>0):
                dict_list=json.loads(s)
                qp_projs = qp_projs + [x['location'] if x['type']=='QUPATH' else "Unsupported opener (not QuPath)" for x in dict_list]
                

    d={"Filename":sources_ABBA, "QuPath_project_location":qp_projs, "AP_mm":AP_coords_ABBA,"Swap_sides":False,"Swap_node":""}
    df_index=pd.DataFrame(data=d)
    
    return df_index
    



def analyse_tree_eng(df, idx, lvl):
#recursive function (_eng is for "engine" ;-) anaylising the heirarchical tree of anatomical structures from the root down 
#works on the same dataframe passed as an input parameter
    if (lvl == 0):
    #initialize results columns 
        df["Tree_level"]=-1
        df["Term_leaf"]=False  
    df.at[idx, "Tree_level"]=lvl
    is_parent = df["Parent"] == df.at[idx, "Name"]
    pos = np.flatnonzero(is_parent)
    n = len(pos)
    # print (n, lvl)
    if n==0:
        df.at[idx, "Term_leaf"]=True
        return df
    else:
        for i in range(n):
            df=analyse_tree_eng(df, pos[i], lvl+1)
    return df


def analyse_tree(df):
#this function applies analyse_tree_eng() to the dataframe containing pre-processed output from the QuPath analysis
    root_pos = df["Parent"] == ""
    pos = np.flatnonzero(root_pos)
    print("Data table containing", len(df["Parent"]), "rows. Starting from the root found at the row number", pos[0])
    print("Analysing the tree...")

    df=analyse_tree_eng(df, pos[0], 0)
    entries = df["Tree_level"] != -1
    n_entries = np.flatnonzero(entries)
    n_term_leaves = np.flatnonzero(df["Term_leaf"])
    maxlevels=np.max(df.loc[:,"Tree_level"])
    print("Assigned levels to",len(n_entries), "tree entries, out of which",len(n_term_leaves), "are terminal leaves; maximal depth is:", maxlevels)

    return df




def expand_tree_df(input_df, cols_to_keep):
#creating a dataframe with expanded tree structure columns
#selected original data columns listed in 'cols_to_keep' are inherited from original dataframe along with some essential columns
    keepdata={}
    to_keep=["ori_index","AP_coord mm","Root_Atlas_AP","ROI_Atlas_AP", "Tree_level", "Term_leaf", "Name", "Class", "ID"]
    #to_keep.extend(cols_to_keep)
    to_keep+=cols_to_keep
    
    col_cntr=len(to_keep)
    
    for i in range(len(to_keep)):
        keepdata[to_keep[i]] = input_df[to_keep[i]]
    tree_df=pd.DataFrame.from_dict(keepdata)
    
    levels=np.max(tree_df.loc[:,"Tree_level"])+1
    
    for i in range(levels):
        tree_df.insert(col_cntr, "level_"+str(i), "")
        col_cntr+=1
    
    for i in range(tree_df.shape[0]):
        levels=tree_df.at[i,"Tree_level"]
        tree_df.at[i,"level_"+str(levels)]=tree_df.at[i,"Name"]
        idx = i
        for j in range(levels):
            find_parent = input_df["Name"] == input_df.at[idx, "Parent"]
            pos = np.flatnonzero(find_parent)
            idx=pos[0]
            tree_df.at[i,"level_"+str(levels-1-j)]=input_df.at[idx,"Name"]
    
    return tree_df



def flatten_df_by_Name(df, classes_list):
#the function takes as an input a dataframe compiled out of the joined per-slice dataframes
# and "collates" by the names of individual anatomical structures, summing up the number of detections
# per each structure, and re-calculates the density based on the summed area
# Original index and AP positions collated for each structure are stored as comma-separated strings in the output dataframe
    struc=df["Name"].unique()
    cls=len(classes_list)
    for i in range(len(struc)):
        if i==0:
            d = {'ori_index': "", 'Image': "", 'AP_coord mm': "" , 'Root_Atlas_AP': "", 'ROI_Atlas_AP': ""}
            d.update({"Name": "","Class": "","Parent": "","ID": "","Parent ID": "",})
            d.update({"Num Detections": 1.0,"Area µm^2": 1.0, "Left_side": False, "Density_Detections": 1.0})
            for j in range(cls):
                d.update({"Num "+classes_list[j]: 1.0,"Density_"+classes_list[j]: 1.0})
            df_collated=pd.DataFrame(data=d, index={0})
        
        df_c=df.where(df["Name"]==struc[i]).dropna(axis=0, how='all')
        indices=df_c["ori_index"].tolist()
        index_list=",".join([str(round(element)) for element in indices])
        coords=df_c["AP_coord mm"].tolist()
        coords_atlas=df_c["Root_Atlas_AP"].tolist()
        rois_coords_atlas=df_c["Atlas_X"].tolist()
        AP_list=",".join([str(element) for element in coords])
        atlas_AP_list=",".join([str(element) for element in coords_atlas])
        ROI_AP_list=";".join([str(element) for element in rois_coords_atlas])
        image_list=",".join(df_c["Image"].tolist())
    
        df_collated.at[i,"ori_index"]=index_list
        df_collated.at[i,"AP_coord mm"]=AP_list
        df_collated.at[i,"Root_Atlas_AP"]=atlas_AP_list
        df_collated.at[i,"ROI_Atlas_AP"]=ROI_AP_list
        df_collated.at[i,"Image"]=image_list
        df_collated.at[i,"Num Detections"]=df_c["Num Detections"].sum()
        for j in range(cls):
            df_collated.at[i,"Num "+classes_list[j]]=df_c["Num "+classes_list[j]].sum()
        df_collated.at[i,"Area µm^2"]=df_c["Area µm^2"].sum()
        df_collated.at[i,"Name"]=struc[i] #df_c["Name"].iloc[0]
        df_collated.at[i,"Class"]=df_c["Class"].iloc[0]
        df_collated.at[i,"Parent"]=df_c["Parent"].iloc[0]
        df_collated.at[i,"ID"]=df_c["ID"].iloc[0]
        df_collated.at[i,"Parent ID"]=df_c["Parent ID"].iloc[0]
        df_collated.at[i,"Left_side"]=df_c["Left_side"].iloc[0]
        check=np.array([len(df_c["Parent"].unique()),len(df_c["ID"].unique()),len(df_c["Parent ID"].unique())])
        if check.sum() != 3:
            print(" -> Warning!!! Parents or (Parent) IDs for the structure", "\'"+df_c["Name"].iloc[0]+"\'","(index list:",index_list+")","seem to be different!")
        
    df_collated["Density_Detections"]=df_collated["Num Detections"]/df_collated["Area µm^2"]*1e6
    
    for j in range(cls):
        df_collated["Density_"+classes_list[j]]=df_collated["Num "+classes_list[j]]/df_collated["Area µm^2"]*1e6
        
        
    return df_collated



def swap_subtrees(df, df_tree, idx):
#recursive function that swaps the values of specified columns of the input dataframe for the specified sub-tree 
#df - input dataframe, it will be modified by swapping
#df_tree - dataframe initially prepared from df; will not be modified but used to go through the tree
#idx - starting index of the swap node in df_right (top of the sub-tree)

    side_tree=df_tree.at[idx, "Class"].split(":")[0]

    row=np.flatnonzero((df["Class"] == df_tree.at[idx, "Class"]) & (df["swapped_sides_flag"]==0))[0]
    
    if side_tree=="Left":
        df.loc[row, "Class"]="Right:"+df.loc[row, "Class"].split(":")[1]
    elif side_tree=="Right":
        df.loc[row, "Class"]="Left:"+df.loc[row, "Class"].split(":")[1]
    df.loc[row,"swapped_sides_flag"]=1
    
    is_parent = df_tree["Parent"] == df_tree.at[idx, "Name"]
    pos = np.flatnonzero(is_parent)
    n = len(pos)
       
    if n==0:
        return df
    else:
        for i in range(n):
            df=swap_subtrees(df, df_tree, pos[i])
    return df

def acronym_list_subtree(df, acro_lst, idx, term_only):
#recursive function which generates a list of acronyms that belong to a specified sub-tree 
#  (all nodes below and including the one specified)
#df - input dataframe
#acro_lst - the starting list of acronyms, will be updated by adding acronyms in the order of exploring the sub-tree. 
#  It can be empty at start
#idx - index in df of the top node of the sub-tree to be explored
#term_only - bool flag; if True, then only terminal leaves of the sub-tree will be reported  

    if (df.at[idx, "Class"] not in acro_lst) and term_only!=True:
        acro_lst.append(df.at[idx, "Class"])

    is_parent = df["Parent"] == df.at[idx, "Name"]
    pos = np.flatnonzero(is_parent)
    n = len(pos)
       
    if n==0:
        if (df.at[idx, "Class"] not in acro_lst) and term_only==True:
            acro_lst.append(df.at[idx, "Class"])
        return acro_lst
    else:
        for i in range(n):
            acro_lst=acronym_list_subtree(df, acro_lst, pos[i], term_only)
    return acro_lst


def flatten_json_ontology(df, from_to):
    #recrusively flattens the hierarchical tree of atlas ontology loaded from json file
    #df - the dataframe obtained after first normalization step of json file,
    #i.e. it should contain the column "children" with the nested dictionary inside
    
    if from_to[0]==0 and from_to[1]==0:
        df=pd.json_normalize(df.loc[0,"msg"])
    
    idxs=df.index[df["children"].str.replace(" ","") != "[]"]
    run_on = [j for j in idxs if j >= from_to[0] and j <= from_to[1]]
    for i in range(len(run_on)):
        tmp=pd.json_normalize(df.loc[run_on[i],"children"])
        df.loc[run_on[i],"children"]="[]"
        df=df.append(tmp, ignore_index=True, sort=False)
        df=flatten_json_ontology(df, [df.shape[0]-tmp.shape[0], df.shape[0]-1])
    
    if from_to[0]==0 and from_to[1]==0:
        df.drop(columns=["children"], inplace=True)
    
    return df

def sum_up_rows(df):
    df_res=df.copy()
    rows=list(range(1,df.shape[0]))
    cols=df.columns
    df_res.drop(rows, inplace=True)
    for c in cols:
        df_res.at[0,c]=df[c].sum()
    return df_res




def import_QuPath_annotations_java(image):

    #col_names=['Image','Name','Class','Parent','ROI','Centroid X µm','Centroid Y µm','ID','Parent ID','Side','Num Detections','Area µm^2','Perimeter µm',"Atlas_X", "Atlas_Y", "Atlas_Z"]
    
    # We need the ImageData and the Annotations we want the results from 
    imagedata = image.java_object.readImageData()
    objects = imagedata.getHierarchy().getAnnotationObjects()

    # This class is the one that produces the same results as 
    # Measure > Show Annotation Measurements
    ob = ObservableMeasurementTableData()
    #This line creates all the measurements
    ob.setImageData(imagedata , objects)
    
    col_names=[]
    for i in range(len(ob.getAllNames())):
        col_names.append(ob.getAllNames()[i])
        
    channels_list=[s.replace("Num ","") for s in col_names if "Num " in s and s != "Num Detections"]    
    
    N_ans=len(objects)

    anno_data=np.empty((N_ans,len(col_names)),dtype="U256")

    for i in range(N_ans):
         for j in range(len(col_names)):
            anno_data[i,j]=str(ob.getStringValue(objects[i], col_names[j]))

   

    objects_det = imagedata.getHierarchy().getDetectionObjects()
    ob_det = ObservableMeasurementTableData()
    ob_det.setImageData(imagedata , objects_det)
    
    dets_col_names=["Image", "Class", "Centroid X µm","Centroid Y µm","Nucleus: Area","Nucleus: Perimeter","Nucleus: Circularity","Atlas_X", "Atlas_Y", "Atlas_Z"]
    
    #append the columns with the data on mean cell intensity
    for i in range(len(ob_det.getAllNames())):
        if ("Cell:" in ob_det.getAllNames()[i] and "mean" in ob_det.getAllNames()[i]):
            dets_col_names.append(ob_det.getAllNames()[i])
   
    N_dets=len(objects_det)
    dets_data=np.empty((N_dets,len(dets_col_names)),dtype="U256")
    for i in range(N_dets):
         for j in range(len(dets_col_names)):
            dets_data[i,j]=str(ob_det.getStringValue(objects_det[i], dets_col_names[j]))

 
    anno_df=pd.DataFrame(anno_data, columns=col_names) 
    anno_df.loc[(anno_df['Class'] == "None"), 'Class'] = ""
    dets_df=pd.DataFrame(dets_data, columns=dets_col_names)


    return anno_df, dets_df, channels_list
    
    


def read_index_file(index_filename, path_prefix):
    df_index=pd.read_excel(path_prefix+index_filename)

    if (("Swap_sides" in df_index.columns.to_list()) and ("Swap_node" in df_index.columns.to_list())):
        swaps = df_index["Swap_sides"] == True
        swap_pos = np.flatnonzero(swaps)
    else:
        swap_pos = []
    
    qp_list=df_index["QuPath_project_location"].drop_duplicates()   
    if (len(qp_list)>1):
        prjs="projects"
    else:
        prjs="project"
        
    print(" -> Index file has",df_index.shape[0],"entries distributed over",len(qp_list),"QuPath "+prjs+".")
    
    return df_index, swap_pos


def extract_QuPath_data(df_index, path_prefix):
    
    qp_list=df_index["QuPath_project_location"].apply(urllib.parse.unquote).drop_duplicates()   
    if (len(qp_list)>1):
        prjs="projects"
    else:
        prjs="project"
        

    # opening the QuPath project for read-only import
    print("\n -> Reading the QuPath "+prjs+"...")

    # matching the index file with the images present in QuPath project(s)
    qp_idx=[]
    qp_image_idx=[]
    qp_image_list=[]
    idx_files_list=[]
    dets_files_list=[]
  
    for qp_path in qp_list:
        qp = QuPathProject(qp_path, mode='r')  # open an existing project

        for ims in range(len(qp.images)):
            matched_index=df_index[df_index['Filename'].str.contains(qp.images[ims].image_name, regex=False)].reset_index()
            if (matched_index.shape[0]>0):
                qp_idx.append(qp)
                qp_image_idx.append(ims)
                qp_image_list.append(qp.images[ims].image_name)
                idx_files_list.append(matched_index.at[0,'Filename'])
                dets_files_list.append(".".join(matched_index.at[0,'Filename'].split(".")[:-1])+"_detections.csv")
            
            
    print(" -> Found",len(idx_files_list),"images in the QuPath "+prjs+" that matched with the index file records")
    print(" -> List of matched images:",qp_image_list)

    # extracting the anotations measurements data from the QuPath project and saving as individual excel files per each image
    print(" -> Extracting and saving the annotations and detections data from the QuPath project...")
    print(" ->  (may take a while in case of many detections)\n")
    global_classes_list=[]    
    for i in range(len(idx_files_list)):
        image = qp_idx[i].images[qp_image_idx[i]]  # get the image
        pixelWidth=float(image._image_server.getMetadata().getPixelWidthMicrons())
        pixelHeight=float(image._image_server.getMetadata().getPixelHeightMicrons())
        print("     Importing annotations from the image",image.image_name,"(",image.width,"x",image.height,"px /","{:.1f}".format(image.width*pixelWidth),"x","{:.1f}".format(image.height*pixelHeight),"micron)...")
        qp_anno_df, qp_dets_df, channels_list = import_QuPath_annotations_java(image)
        if (len(channels_list)>0):
            s_ch=(" in "+str(len(channels_list))+" classes: ")+"".join('"'+str(s)+'",' for s in channels_list)[:-1]
            classes_list=[str(s) for s in channels_list]
        else:
            classes_list=[]
            s_ch=", unclassified"
        global_classes_list+=classes_list
        print("          It has",len(image.hierarchy.annotations), "annotations and",len(image.hierarchy.detections),"detections"+s_ch)
        qp_anno_df.to_csv(path_prefix+idx_files_list[i],index=False)
        qp_dets_df.to_csv(path_prefix+dets_files_list[i],index=False)
        
    print("\n -> Done!") 
    print(" -> Stored",len(idx_files_list),"annotation and",len(idx_files_list),"detection .csv files in the folder", path_prefix)
    global_classes_list=list(set(global_classes_list))
    if (len(global_classes_list)>0):
        s_ch="".join('"'+str(s)+'",' for s in global_classes_list)[:-1]
        print(" -> Identified",len(global_classes_list),"detection classes:",s_ch)
    else:
        print(" -> All detections unclassified")
    
    
    return idx_files_list, dets_files_list, global_classes_list



def load_csv_data(df_index, swap_pos, classes_list, path_prefix, path_prefix_results, result_filename, df_atlas):

    df=pd.DataFrame()
    df_dets=pd.DataFrame()

    file_cntr=0
    skip_cntr=0
    swap_cntr=0
    total_dets=0

    for i in range(df_index.shape[0]):
        if os.path.isfile(path_prefix+df_index.at[i, "Filename"])==True:
            tmp=pd.read_csv(path_prefix+df_index.at[i, "Filename"])
            #replacing the acronyms in the columns "Name" and "Parent" with the structure names taken from the atlas annotation file
            for j in range(tmp.shape[0]):
                idx=df_atlas.index[df_atlas["acronym"]==tmp.loc[j,"Name"]].tolist()
                if len(idx)>0:
                    tmp.loc[j, "Name"]=df_atlas.loc[idx[0],"name"]
                idx=df_atlas.index[df_atlas["acronym"]==tmp.loc[j,"Parent"]].tolist()
                if len(idx)>0:
                    tmp.loc[j, "Parent"]=df_atlas.loc[idx[0],"name"] 
            if tmp.shape[0]>0:
                file_cntr+=1
                root_pos = np.flatnonzero((tmp["Parent"] == "Image") & (tmp["Name"] == "Root"))
                root_atlas_Z = tmp.at[root_pos[0], "Atlas_X"]
                tmp.insert(tmp.shape[1],"Root_Atlas_AP", root_atlas_Z)           
                tmp.insert(tmp.shape[1],"AP_coord mm", df_index.at[i, "AP_mm"])
                tmp.insert(tmp.shape[1],"swapped_sides_flag", 0)
                if i in swap_pos: #performing a swap of the data values
                    swap_cntr+=1
                    df_right=tmp.where(tmp["Class"].str.contains("Right")==True).dropna(axis=0, how='all')
                    df_right.reset_index(drop=False, inplace=True)
                    df_left=tmp.where(tmp["Class"].str.contains("Left")==True).dropna(axis=0, how='all')
                    df_left.reset_index(drop=False, inplace=True)
                    tmp=swap_subtrees(tmp, df_right, df_right.index[df_right["Name"]==df_index.at[i,"Swap_node"]][0])
                    right_left=tmp["swapped_sides_flag"].sum()
                    tmp=swap_subtrees(tmp, df_left, df_left.index[df_left["Name"]==df_index.at[i,"Swap_node"]][0])
                    print(" -> Swapped ","\'"+df_index.at[i,"Swap_node"]+"\'","in ", "\'"+df_index.at[i, "Filename"]+"\':",
                    right_left,"swaps R=>L and",tmp["swapped_sides_flag"].sum()-right_left,"L=>R")
                df=df.append(tmp, ignore_index=True, sort=False)
                tmp_det=pd.read_csv(path_prefix+".".join(df_index.at[i, "Filename"].split(".")[:-1])+"_detections.csv")
                if tmp_det.shape[0]>0:
                    tmp_det.insert(tmp_det.shape[1],"Root_Atlas_AP", root_atlas_Z)
                    tmp_det.insert(tmp_det.shape[1],"AP_coord mm", df_index.at[i, "AP_mm"])
                    df_dets=df_dets.append(tmp_det, ignore_index=True, sort=False)
                    total_dets+=tmp_det.shape[0]
            else:
                skip_cntr+=1
            
            
    cls=len(classes_list)
    
    df["Num Detections"]=df["Num Detections"].fillna(0)
    
    for i in range(cls):
        df["Num "+classes_list[i]]=df["Num "+classes_list[i]].fillna(0)
                
    print("\n -> Loaded the data, in total",df.shape[0],"data rows in",df.shape[1]-1,"columns from",file_cntr,".csv files, skipped",skip_cntr,"empty file(s).")
    print("\n -> Found in total",total_dets,"detections.")
    print(" -> Swapped sides in",swap_cntr,"file(s).")

    df.to_csv(path_prefix_results+result_filename+"combined.csv",index_label="index")
    print("\n -> Saved the combined dataframe into the file","\'"+result_filename+"combined.csv\'")

    df_dets.to_csv(path_prefix_results+result_filename+"combined_detections.csv",index_label="index")
    print("\n -> Saved the combined detections into the file","\'"+result_filename+"combined_detections.csv\'")

    df_dets[["Atlas_X","Atlas_Y","Atlas_Z"]].to_csv(path_prefix_results+result_filename+"detection_coordinates.csv",index=False)
    print("\n -> Saved "+str(df_dets.shape[0])+" unclassified detection coordinates into","\'"+result_filename+"detection_coordinates.csv\'")
    
    for i in range(cls):
        san="".join(c.replace(" ", "_") for c in classes_list[i] if c not in "\/:*?<>|")
        filename=result_filename+"detection_coordinates_"+san+".csv"
        df_i=df_dets.where(df_dets["Class"]==classes_list[i]).dropna(axis=0, how='all')[["Atlas_X","Atlas_Y","Atlas_Z"]]
        df_i.to_csv(path_prefix_results+filename,index=False)
        print("\n -> Saved "+str(df_i.shape[0])+" detection coordinates for the class \""+classes_list[i]+"\" into","\'"+filename+"\'")
    
    
    return df, df_dets
    
def process_left_right_trees(df, classes_list, path_prefix_results, result_filename):
    
    df["Left_side"]=df["Class"].str.contains("Left")
    df.astype({"Num Detections": 'int64'})
    df["Density_Detections"]=df["Num Detections"]/df["Area µm^2"]*1e6
    list_to_keep=["Num Detections", "Area µm^2", "Density_Detections"]
        
    # additional cycling through the classes
    cls=len(classes_list)
    for i in range(cls):
        list_to_keep.append("Num "+classes_list[i])
        list_to_keep.append("Density_"+classes_list[i])
        df.astype({"Num "+classes_list[i]: 'int64'})
        df["Density_"+classes_list[i]]=df["Num "+classes_list[i]]/df["Area µm^2"]*1e6
    
    print("Splitting the data into the LEFT and the RIGHT subsets...")
    df_left=df.copy()
    df_left=df.where(df["Left_side"]).where(df["Parent"]!="Image").dropna(axis=0, how='all')
    #df_left.drop_duplicates(keep=False, inplace=True)
    df_left["Parent"]=df_left["Parent"].mask(df_left["Name"]=="root", "")
    df_left["Class"]=df_left["Class"].str.split(":",expand=True)[1].str.lstrip(to_strip=" ").str.replace(","," ")
    df_left.reset_index(drop=False, inplace=True)
    df_left.rename(columns={"index": "ori_index"}, inplace=True)
    df_left.astype({"Num Detections": 'int64'})
    for i in range(cls):
        df_left.astype({"Num "+classes_list[i]: 'int64'})
    df_left.to_csv(path_prefix_results+result_filename+"left.csv",index_label="index")
    print("Saved the file","\'"+result_filename+"left.csv\'","for the LEFT side")

    df_right=df.copy()
    df_right=df.where(df["Left_side"]==False).where(df["Parent"]!="Image").dropna(axis=0, how='all')
    #df_right.drop_duplicates(keep=False, inplace=True)
    df_right["Parent"]=df_right["Parent"].mask(df_right["Name"]=="root", "")
    df_right["Class"]=df_right["Class"].str.split(":",expand=True)[1].str.lstrip(to_strip=" ").str.replace(","," ")
    df_right.reset_index(drop=False, inplace=True)
    df_right.rename(columns={"index": "ori_index"}, inplace=True)
    df_right.astype({"Num Detections": 'int64'})
    for i in range(cls):
        df_right.astype({"Num "+classes_list[i]: 'int64'})
    df_right.to_csv(path_prefix_results+result_filename+"right.csv",index_label="index")
    print("Saved the file","\'"+result_filename+"right.csv\'","for the RIGHT side")
    print("\nCollating the RIGHT-side dataframe...")
    df_right_collated=flatten_df_by_Name(df_right, classes_list)
    print(" ->",df_right_collated.shape[0],"resulting rows, i.e. unique structure names.")

    df_right_collated[["Class",'ROI_Atlas_AP']].to_csv(path_prefix_results+result_filename+"collated_right_AP_coordinates.csv",index=False)
    print(" -> Saved the RIGHT-side AP coordinate lists per each atlas ROI (centroids) into the file","\'"+result_filename+"collated_right_AP_coordinates.csv\'")

    print("\nCollating the LEFT-side dataframe...")
    df_left_collated=flatten_df_by_Name(df_left,classes_list)
    print(" ->",df_left_collated.shape[0],"resulting rows, i.e. unique structure names.")

    df_left_collated[["Class",'ROI_Atlas_AP']].to_csv(path_prefix_results+result_filename+"collated_left_AP_coordinates.csv",index=False)
    print(" -> Saved the LEFT-side AP coordinate lists per each atlas ROI (centroids) into the file","\'"+result_filename+"collated_left_AP_coordinates.csv\'")

    print("\nAnalysing the tree for the collated RIGHT-side dataframe \'df_right_collated\'")
    df_right_collated=analyse_tree(df_right_collated)
    df_right_tree=expand_tree_df(df_right_collated, list_to_keep)
    df_right_tree.to_csv(path_prefix_results+result_filename+"right_tree.csv",index_label="index")
    print("Saved the file","\'"+result_filename+"right_tree.csv\'","for the RIGHT-side collated tree")

    print("\nAnalysing the tree for the collated LEFT-side dataframe \'df_left_collated\'")
    df_left_collated=analyse_tree(df_left_collated)
    df_left_tree=expand_tree_df(df_left_collated, list_to_keep)
    df_left_tree.to_csv(path_prefix_results+result_filename+"left_tree.csv",index_label="index")
    print("Saved the file","\'"+result_filename+"left_tree.csv\'","for the LEFT-side collated tree")
    
    df_list=[df_left, df_left_tree, df_left_collated, df_right, df_right_tree, df_right_collated]
           
    return df_list
    
    
    
   
def generate_AP_traces(tree_df, ori_df, column, AP_values, mode, lst):
    #tree_df - dataframe containing the collated tree
    #ori_df - uncollated dataframe over multiple slices which was used as a source for creating the collated tree
    #column - name of the column with values to be sampled over AP axis
    #AP_values - name of the column with the AP coordinate values to take
    #mode: if 1, then the AP graphs will be generated only for the terminal leaves of the tree
    #      if 2, then for ALL the entries in the dataframe (every row)
    #      if 3, then for the structures whose acronyms ("Class") are listed in the list 'lst'
    #      if 4, then for the structures whose IDs ("ID") are listed in the list 'lst'
    #      if <=0, then for the entries of hierarchical level equal to (-1)*mode
    #lst: list with the values, only taken into account when mode=3 or mode=4
    if mode<=0:
        df_masked=tree_df.where(tree_df["Tree_level"] == -mode).dropna(axis=0, how='all')
    elif mode==1:
        df_masked=tree_df.where(tree_df["Term_leaf"] == True).dropna(axis=0, how='all')
    elif mode==3:
        df_masked=pd.concat([tree_df.where(tree_df["Class"]==element).dropna(axis=0, how='all') for element in lst],ignore_index=True,sort=False)
    elif mode==4:
        df_masked=pd.concat([tree_df.where(tree_df["ID"]==element).dropna(axis=0, how='all') for element in lst],ignore_index=True,sort=False)
    elif mode==2:
        df_masked=tree_df.dropna(axis=0, how='all')
    
    AP_coords = ori_df[AP_values].unique()
    idx = np.arange(len(AP_coords))
    nans = np.zeros(len(AP_coords))
    nans = np.nan
    d = {AP_values: AP_coords}
    for i in range(df_masked.shape[0]):
        s=df_masked["Class"].iloc[i]+";"+df_masked["Name"].iloc[i]
        bla = {s: nans}
        d.update(bla)
        
    df_AP_graphs=pd.DataFrame(data=d, index=idx)
    
    for i in range(df_masked.shape[0]):
        AP_lst=[float(element) for element in df_masked[AP_values].iloc[i].split(",")]
        idx_lst=[int(element) for element in df_masked["ori_index"].iloc[i].split(",")]
        for j in range(len(AP_coords)):
            if AP_coords[j] in AP_lst:
                k=ori_df.index[ori_df["ori_index"] == idx_lst[AP_lst.index(AP_coords[j])]].tolist()
                df_AP_graphs.iloc[j, i+1]=ori_df.loc[k[0],column]
                if len(k)>1:
                    print(" -> Warning!!! Seems like there are multiple identical indices in the original dataframe.")
                
            
            
    return df_AP_graphs
 
 
    
def summary_per_ROI(df_list, super_list, classes_list, mode, save_mode, term_flag, target, path_prefix_results, result_filename):
    
    cls=len(classes_list)
    
    num_dets_list=["Num Detections"]
    dens_list=["Density_Detections"]
    classes_index=["Detections"]
    det_files=["Detections"]
    den_files=["Density"]
    over_all=["over all"]
        
    for i in range(cls):
        num_dets_list.append("Num "+classes_list[i])
        dens_list.append("Density_"+classes_list[i])
        classes_index.append(classes_list[i])
        san="".join(c.replace(" ", "_") for c in classes_list[i] if c not in "\/:*?<>|")
        det_files.append("Detections_"+san)
        den_files.append("Density_"+san)
        over_all.append("over all")
        
    AP_coords="Root_Atlas_AP"    
         
    df_left = df_list[0]
    df_left_tree = df_list[1]
    df_left_collated = df_list[2]
    df_right = df_list[3]
    df_right_tree = df_list[4]
    df_right_collated = df_list[5]
        
    left_dict={}
    right_dict={}
         
    for struc in super_list:
            
        print("\n=> Processing", struc)
        if mode>0 and mode<4:
        # here, generate the list of acronyms by the selected top node of a sub-tree
            lst_right=acronym_list_subtree(df_right_collated, [], df_right_collated.index[df_right_collated["Class"]==str(struc)][0],term_flag)
            lst_left=acronym_list_subtree(df_left_collated, [], df_left_collated.index[df_left_collated["Class"]==str(struc)][0],term_flag)
        if mode==3:
            target=str(struc)
           
        print("\nCalculating the traces vs AP coordinates for the RIGHT-side...")
         
        right_concat_dict_dets={}
                    
        for i in range(cls+1):
            right_dict[num_dets_list[i]]=generate_AP_traces(df_right_tree, df_right, num_dets_list[i], AP_coords, 3, lst_right)
            right_dict[dens_list[i]]=generate_AP_traces(df_right_tree, df_right, dens_list[i], AP_coords, 3, lst_right)
            right_concat_dict_dets[num_dets_list[i]]=sum_up_rows(right_dict[num_dets_list[i]])
                          
        df_right_area_vsAP=generate_AP_traces(df_right_tree, df_right, "Area µm^2", AP_coords, 3,  lst_right)
        right_dict["areas_vs_AP"]=df_right_area_vsAP
        
        df_right_area_sum=sum_up_rows(df_right_area_vsAP)
            
        df_right_dets_sum=pd.concat(list(dict.values(right_concat_dict_dets)),ignore_index=True)
        df_right_dens_sum=df_right_dets_sum.copy()
        
        for i in range(df_right_dens_sum.shape[0]):
            df_right_dens_sum.iloc[i]=df_right_dets_sum.iloc[i]/df_right_area_sum.iloc[0]*1e6
        
        df_right_dets_sum.insert(1, "Class_name", classes_index)#.index=classes_index
        df_right_dens_sum.insert(1, "Class_name", classes_index)#.index=classes_index
        
        df_right_dets_sum.drop(AP_coords, inplace=True, axis=1)
        df_right_dets_sum.insert(1, AP_coords, over_all)
            
        df_right_dens_sum.drop(AP_coords, inplace=True, axis=1)
        df_right_dens_sum.insert(1, AP_coords, over_all)
            
        df_right_area_sum.drop(AP_coords, inplace=True, axis=1)
        df_right_area_sum.insert(1, AP_coords, ["over all"])
        
        right_dict["detections_total"]=df_right_dets_sum
        right_dict["densities_total"]=df_right_dens_sum
        right_dict["areas_total"]=df_right_area_sum
             
        print("\n -> Generated",right_dict[num_dets_list[0]].shape[1]-1,"traces.")
        if mode>=1 and mode<=3:
            print("\n Processed acronyms:",lst_right)

        if save_mode=="xlsx":
            with pd.ExcelWriter(path_prefix_results+result_filename+"right_data_vsAP_"+target+".xlsx") as writer:  
                for i in range(cls+1):
                    right_dict[num_dets_list[i]].rename(columns={AP_coords: 'AP_coord_mm'}).to_excel(writer, sheet_name=det_files[i])
                    right_dict[dens_list[i]].rename(columns={AP_coords: 'AP_coord_mm'}).to_excel(writer, sheet_name=den_files[i])                
                df_right_area_vsAP.rename(columns={AP_coords: 'AP_coord_mm'}).to_excel(writer, sheet_name='Area (µm^2)')
                df_right_dets_sum.rename(columns={AP_coords: 'AP_coord_mm'}).to_excel(writer, sheet_name='Tot. Detections')
                df_right_area_sum.rename(columns={AP_coords: 'AP_coord_mm'}).to_excel(writer, sheet_name='Tot. area (µm^2)')
                df_right_dens_sum.rename(columns={AP_coords: 'AP_coord_mm'}).to_excel(writer, sheet_name='Tot. density per mm^2')
                print("\nSaved the file","\'"+result_filename+"right_data_vsAP_"+target+".xlsx\'","for the data vs AP coordinates.")
        elif save_mode=="csv":
            for i in range(cls+1):
                right_dict[num_dets_list[i]].rename(columns={AP_coords: 'AP_coord_mm'}).to_csv(path_prefix_results+result_filename+"right_data_vsAP_"+target+"_"+det_files[i]+".csv")
                right_dict[dens_list[i]].rename(columns={AP_coords: 'AP_coord_mm'}).to_csv(path_prefix_results+result_filename+"right_data_vsAP_"+target+"_"+den_files[i]+".csv")
            df_right_area_vsAP.rename(columns={AP_coords: 'AP_coord_mm'}).to_csv(path_prefix_results+result_filename+"right_data_vsAP_"+target+"_areas.csv")
            df_right_dets_sum.rename(columns={AP_coords: 'AP_coord_mm'}).to_csv(path_prefix_results+result_filename+"right_data_vsAP_"+target+"_tot_detections.csv")
            df_right_area_sum.rename(columns={AP_coords: 'AP_coord_mm'}).to_csv(path_prefix_results+result_filename+"right_data_vsAP_"+target+"_tot_areas.csv")
            df_right_dens_sum.rename(columns={AP_coords: 'AP_coord_mm'}).to_csv(path_prefix_results+result_filename+"right_data_vsAP_"+target+"_tot_density.csv")
            print("\nSaved "+str((cls+3)*2)+" .csv files","\'"+result_filename+"right_data_vsAP_"+target+"*.csv\'","for the data vs AP coordinates.")

     
        print("\n\nCalculating the traces vs AP coordinates for the LEFT-side...")
         
        left_concat_dict_dets={}
                    
        for i in range(cls+1):
            left_dict[num_dets_list[i]]=generate_AP_traces(df_left_tree, df_left, num_dets_list[i], AP_coords, 3, lst_left)
            left_dict[dens_list[i]]=generate_AP_traces(df_left_tree, df_left, dens_list[i], AP_coords, 3, lst_left)
            left_concat_dict_dets[num_dets_list[i]]=sum_up_rows(left_dict[num_dets_list[i]])
                          
        df_left_area_vsAP=generate_AP_traces(df_left_tree, df_left, "Area µm^2", AP_coords, 3,  lst_left)
        left_dict["areas_vs_AP"]=df_left_area_vsAP
        
        df_left_area_sum=sum_up_rows(df_left_area_vsAP)
            
        df_left_dets_sum=pd.concat(list(dict.values(left_concat_dict_dets)),ignore_index=True)
        df_left_dens_sum=df_left_dets_sum.copy()
        
        for i in range(df_left_dens_sum.shape[0]):
            df_left_dens_sum.iloc[i]=df_left_dets_sum.iloc[i]/df_left_area_sum.iloc[0]*1e6
        
        df_left_dets_sum.insert(1, "Class_name", classes_index)#.index=classes_index
        df_left_dens_sum.insert(1, "Class_name", classes_index)#.index=classes_index
        
        df_left_dets_sum.drop(AP_coords, inplace=True, axis=1)
        df_left_dets_sum.insert(1, AP_coords, over_all)
            
        df_left_dens_sum.drop(AP_coords, inplace=True, axis=1)
        df_left_dens_sum.insert(1, AP_coords, over_all)
            
        df_left_area_sum.drop(AP_coords, inplace=True, axis=1)
        df_left_area_sum.insert(1, AP_coords, ["over all"])
        
        left_dict["detections_total"]=df_left_dets_sum
        left_dict["densities_total"]=df_left_dens_sum
        left_dict["areas_total"]=df_left_area_sum
             
        print("\n -> Generated",left_dict[num_dets_list[0]].shape[1]-1,"traces.")
        if mode>=1 and mode<=3:
            print("\n Processed acronyms:",lst_left)

        if save_mode=="xlsx":
            with pd.ExcelWriter(path_prefix_results+result_filename+"left_data_vsAP_"+target+".xlsx") as writer:  
                for i in range(cls+1):
                    left_dict[num_dets_list[i]].rename(columns={AP_coords: 'AP_coord_mm'}).to_excel(writer, sheet_name=det_files[i])
                    left_dict[dens_list[i]].rename(columns={AP_coords: 'AP_coord_mm'}).to_excel(writer, sheet_name=den_files[i])                
                df_left_area_vsAP.rename(columns={AP_coords: 'AP_coord_mm'}).to_excel(writer, sheet_name='Area (µm^2)')
                df_left_dets_sum.rename(columns={AP_coords: 'AP_coord_mm'}).to_excel(writer, sheet_name='Tot. Detections')
                df_left_area_sum.rename(columns={AP_coords: 'AP_coord_mm'}).to_excel(writer, sheet_name='Tot. area (µm^2)')
                df_left_dens_sum.rename(columns={AP_coords: 'AP_coord_mm'}).to_excel(writer, sheet_name='Tot. density per mm^2')
                print("\nSaved the file","\'"+result_filename+"left_data_vsAP_"+target+".xlsx\'","for the data vs AP coordinates.")
        elif save_mode=="csv":
            for i in range(cls+1):
                left_dict[num_dets_list[i]].rename(columns={AP_coords: 'AP_coord_mm'}).to_csv(path_prefix_results+result_filename+"left_data_vsAP_"+target+"_"+det_files[i]+".csv")
                left_dict[dens_list[i]].rename(columns={AP_coords: 'AP_coord_mm'}).to_csv(path_prefix_results+result_filename+"left_data_vsAP_"+target+"_"+den_files[i]+".csv")
            df_left_area_vsAP.rename(columns={AP_coords: 'AP_coord_mm'}).to_csv(path_prefix_results+result_filename+"left_data_vsAP_"+target+"_areas.csv")
            df_left_dets_sum.rename(columns={AP_coords: 'AP_coord_mm'}).to_csv(path_prefix_results+result_filename+"left_data_vsAP_"+target+"_tot_detections.csv")
            df_left_area_sum.rename(columns={AP_coords: 'AP_coord_mm'}).to_csv(path_prefix_results+result_filename+"left_data_vsAP_"+target+"_tot_areas.csv")
            df_left_dens_sum.rename(columns={AP_coords: 'AP_coord_mm'}).to_csv(path_prefix_results+result_filename+"left_data_vsAP_"+target+"_tot_density.csv")
            print("\nSaved "+str((cls+3)*2)+" .csv files","\'"+result_filename+"left_data_vsAP_"+target+"*.csv\'","for the data vs AP coordinates.")
    
    return left_dict, right_dict
 