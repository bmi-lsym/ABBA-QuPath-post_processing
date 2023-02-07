#pragma TextEncoding = "Windows-1252"
#pragma rtGlobals=3		// Use modern global access method and strict wave access.


Menu "ABBA/QuPath post-analysis" 

	"Start GUI", /Q, ABBA_processing_GUI_main()
	"Getting started help", /Q, DoWindow/F $"Manual"
	
End


Function ABBA_processing_GUI_main()

 SetDataFolder root:
 NVAR cancel_flag=gCancelFlag
 if (NVAR_Exists(cancel_flag)!=1)
  Variable/G gCancelFlag
  NVAR cancel_flag=gCancelFlag
  cancel_flag=0
 endif
 
 SVAR dataset_list=gDatasetList
 if (SVAR_Exists(dataset_list)!=1)
  String/G gDatasetList
  SVAR dataset_list=gDatasetList
  dataset_list=""
 endif
 
 cancel_flag=0

 NewPanel /K=2/N=tmp_PauseforChoosing /W=(100,100,400,320) as "Choose action..."
	
	Button button0,pos={20,20},size={260,25},title="Load new dataset (one brain)", proc=UserMainChoice
	Button button1,pos={20,60},size={260,25},title="Process a dataset (one brain)", proc=UserMainChoice
	Button button2,pos={20,100},size={260,25},title="Average across several datasets", proc=UserMainChoice
	Button button3,pos={20,140},size={260,25},title="Finish", proc=UserMainChoice
	Button button0k,pos={20,180},size={260,25},title="Remove a dataset (one brain)", proc=UserMainChoice
	
	
   PauseForUser tmp_PauseforChoosing
   
  // KillVariables/Z cancel_flag


End


Function ABBA_processing_GUI_load()

 SetDataFolder root:
 NVAR cancel_flag=gCancelFlag
 SVAR dataset_list=gDatasetList
 
 
 SVAR animalID=gAnimalID
  if(SVAR_Exists(AnimalID)!=1)
	  String/G gAnimalID="AB1234"
	  SVAR animalID=gAnimalID
   endif
   
 SVAR pathDataset=gpathDataset
  if(SVAR_Exists(pathDataset)!=1)
	  String/G gpathDataset="D:Data:Example:"
	  SVAR pathDataset=gpathDataset
   endif
   
 SVAR prefixDataset=gprefixDataset
  if(SVAR_Exists(prefixDataset)!=1)
	  String/G gprefixDataset=""
	  SVAR prefixDataset=gprefixDataset
   endif
   
 SVAR suffixDataset=gsuffixDataset
  if(SVAR_Exists(suffixDataset)!=1)
	  String/G gsuffixDataset="whole"
	  SVAR suffixDataset=gsuffixDataset
   endif
   
 String animal_ID=animalID
 String path_Dataset=pathDataset
 String prefix_Dataset=prefixDataset
 String suffix_Dataset=suffixDataset
 

   Prompt animal_ID, "The brain ID (a folder to be made)"
	Prompt path_Dataset, "Path to the dataset on the disk"
	Prompt prefix_Dataset, "Filename prefix"
	Prompt suffix_Dataset, "Filename suffix"
	
	DoPrompt "Dataset parameters", animal_ID,path_Dataset,prefix_Dataset,suffix_Dataset
	
   cancel_flag=V_flag
   
   if (cancel_flag==0)
	
    animalID=animal_ID
    pathDataset=path_Dataset
    prefixDataset=prefix_Dataset
    suffixDataset=suffix_Dataset
    
    dataset_list=ReplaceString(animal_ID+";", dataset_list, "")+animal_ID+";"
	
    create_folders_load_data(animal_ID,path_Dataset,prefix_Dataset,suffix_Dataset)
    
   
       
  endif
  
  
  ABBA_processing_GUI_main()
 
  

End



Function ABBA_processing_GUI_doone()

 SetDataFolder root:
 NVAR cancel_flag=gCancelFlag
 SVAR dataset_list=gDatasetList
 
 SVAR sortBy=gsortBy
  if(SVAR_Exists(sortBy)!=1)
	  String/G gsortBy="left"
	  SVAR sortBy=gsortBy
   endif 

   
 String dataset_ID=StringFromList(0,dataset_list,";")
 
 SVAR datasetID=gdatasetID
  if(SVAR_Exists(datasetID)!=1)
	  String/G gdatasetID=dataset_ID
	  SVAR datasetID=gdatasetID
	elseif (WhichListItem(datasetID,dataset_list)>=0)
     dataset_ID=datasetID
   endif
   

 SVAR globalclasses_list=root:gGlobalClasses
 if (SVAR_Exists(globalclasses_list)!=1)
  String/G root:gGlobalClasses
  SVAR globalclasses_list=root:gGlobalClasses
  globalclasses_list=""
 endif  
   
    
 SVAR byclass=gByClass
  if(SVAR_Exists(byclass)!=1)
	  String/G gByClass=StringFromList(0,globalclasses_list,";")
	  SVAR byclass=gByClass
   endif  
   
  
   
 NVAR plotN=gplotN
  if(NVAR_Exists(plotN)!=1)
	  Variable/G gplotN=10
	  NVAR plotN=gplotN
  endif    
   
   
 
 Variable list_l=ItemsInList(dataset_list,";"), plot_N
 
  
  
 SetDataFolder $"root:Brain_Areas:"
 
 String brain_areas_list=WaveList("*_acronyms", ";", "TEXT:1"), brain_areas, brain_area
 
 SetDataFolder $"root:"
 
  
 brain_areas=ReplaceString("_acronyms",brain_areas_list,"")
 brain_area=StringFromList(0, brain_areas, ";")
 
 plot_N=plotN
 
  SVAR brain_ar=gBrainArea
  if(SVAR_Exists(brain_ar)!=1)
	  String/G gBrainArea=brain_area
	  SVAR brain_ar=gBrainArea
	else
    brain_area=brain_ar
   endif
 
 
 
 String sort_By=sortBy, sortBy_list="left;right"
 
 
 String LayoutsIndividual
 
 SVAR Layouts_individual=gLayoutsIndividual
  if(SVAR_Exists(Layouts_individual)!=1)
	  String/G gLayoutsIndividual="Layout_dens;Layout_dets"
	  SVAR Layouts_individual=gLayoutsIndividual
   endif
 
 LayoutsIndividual=Layouts_individual
 
 String globalclasses=globalclasses_list, by_class=byclass
 
 
 if (list_l)
  
   
  
 

   Prompt dataset_ID, "Choose the ID of dataset to be analyzed", popup, dataset_list
   Prompt by_class, "Choose the detection class", popup, globalclasses
   Prompt brain_area, "Choose the brain area (from Brain_Areas folder)", popup, brain_areas
   Prompt sort_By, "Master sorting by which side?", popup, sortBy_list
   Prompt plot_N, "How many of the top AP-traces to plot?"
   Prompt LayoutsIndividual, "Layout windows for appending the respective results (density;detections)"
	
   DoPrompt "Set analysis parameters", dataset_ID, by_class, brain_area, sort_By, plot_N, LayoutsIndividual
	
   cancel_flag=V_flag
   
   if (cancel_flag==0)
   
     sortBy=sort_By
     byclass=by_class
     brain_ar=brain_area
     datasetID=dataset_ID
     plotN=plot_N
     
     Layouts_individual=LayoutsIndividual
     
     String lay_dens=StringFromList(0, LayoutsIndividual,";"), lay_dets=StringFromList(1, LayoutsIndividual,";")
     String populate_layout, graphs_left, graphs_right     
     Variable i, lay_dens_existed=1, lay_dets_existed=1
     String class_path=by_class+":", class_short="C"+num2str(WhichListItem(by_class,globalclasses,";"))
     
     
     Wave/T atlas_acros=$"root:Atlas_DB:atlas_acronyms", atlas_names=$"root:Atlas_DB:atlas_names"
     Wave/T acros=$"root:Brain_Areas:"+brain_area+"_acronyms"
     
     Wave/T dataset_acros_left=$"root:Dataset_acronyms:"+dataset_ID+"_left_all_acronyms"
     Wave/T dataset_waves_left=$"root:Dataset_acronyms:"+dataset_ID+"_left_all_waves"
     String total_density_left="root:"+dataset_ID+":left:total_density:"+class_path
     String total_detections_left="root:"+dataset_ID+":left:total_detections:"+class_path
     
     Wave/T dataset_acros_right=$"root:Dataset_acronyms:"+dataset_ID+"_right_all_acronyms"
     Wave/T dataset_waves_right=$"root:Dataset_acronyms:"+dataset_ID+"_right_all_waves"
     String total_density_right="root:"+dataset_ID+":right:total_density:"+class_path
     String total_detections_right="root:"+dataset_ID+":right:total_detections:"+class_path
	
	  String res_dens_left="root:"+dataset_ID+":res:"+class_path+"dens_left_"+brain_area
	  String res_dens_right="root:"+dataset_ID+":res:"+class_path+"dens_right_"+brain_area
	  String res_densAP_left="root:"+dataset_ID+":res:"+class_path+"densAP_left_"+brain_area
	  String res_densAP_right="root:"+dataset_ID+":res:"+class_path+"densAP_right_"+brain_area
	   
	  String res_dets_left="root:"+dataset_ID+":res:"+class_path+"dets_left_"+brain_area
	  String res_dets_right="root:"+dataset_ID+":res:"+class_path+"dets_right_"+brain_area
	  String res_detsAP_left="root:"+dataset_ID+":res:"+class_path+"detsAP_left_"+brain_area
	  String res_detsAP_right="root:"+dataset_ID+":res:"+class_path+"detsAP_right_"+brain_area
	  
	  
	
     SetDataFolder $("root:"+dataset_ID+":res:")
     
     
      if (strlen(WinList(lay_dens, ";", "WIN:4"))==0)
       NewLayout as "Density of detections for "+dataset_ID
       DoWindow/C $lay_dens
       lay_dens_existed=0
      endif
     
     if (strlen(WinList(lay_dets, ";", "WIN:4"))==0)
      NewLayout as "Number of detections for "+dataset_ID
      DoWindow/C $lay_dets
      lay_dets_existed=0
     endif
               
     
   
     if (CmpStr(sort_By,"left")==0) //master sort by the left side
 
      //density
      
      Process_acronyms_list(acros, dataset_acros_left, dataset_waves_left, total_density_left, atlas_acros, atlas_names,  1 , res_dens_left)
      Process_acronyms_list($(res_dens_left+"_acros"), dataset_acros_right, dataset_waves_right, total_density_right, atlas_acros, atlas_names,  0 , res_dens_right)
      MakeBarGraph($(res_dens_left+"_sortvals"), $(res_dens_right+"_sortvals"), $(res_dens_left+"_labels"), $(res_dens_left+"_label_locs"),dataset_ID+"_"+brain_area+"_totdens"+class_short,"total density of detections (mm\\S-2\\M)")
      
      DoWindow/F $lay_dens
     
      if (lay_dens_existed)
        LayoutPageAction appendPage
      endif
      
       AppendLayoutObject/F=0/T=1/R=(45,78,570,540) Graph $(dataset_ID+"_"+brain_area+"_totdens"+class_short)
	   SetDrawLayer UserFront
	   SetDrawEnv fsize= 14
	   DrawText 29.25,60.75,"Data for "+ dataset_ID
	   SetDrawEnv fsize= 14
	   DrawText 101.25,75, brain_area+" areas: total density of detections. Detection class: \""+by_class+"\""
      
      lay_dens_existed=1
      
      
      Duplicate/O $(res_dens_left+"_wavelist") $(res_densAP_left+"_wavelist")
      Duplicate/O $(res_dens_right+"_wavelist") $(res_densAP_right+"_wavelist")
      Wave/T densAP_left=$(res_densAP_left+"_wavelist"), densAP_right=$(res_densAP_right+"_wavelist") 
      densAP_left=ReplaceString("total_density", densAP_left[p], "density")
      densAP_right=ReplaceString("total_density", densAP_right[p], "density")
      
      MakeAPGraph_uniqueAPs(acros, densAP_left, min(plot_N,numpnts(densAP_left)),dataset_ID+"_"+brain_area+"_APldens"+class_short,"density of detections (mm\\S-2\\M)", "(65535,0,0)")
      plotN=min(plot_N,numpnts(densAP_left))
      MakeAPGraph_uniqueAPs(acros, densAP_right, min(plot_N,numpnts(densAP_right)),dataset_ID+"_"+brain_area+"_APrdens"+class_short,"density of detections (mm\\S-2\\M)", "(0,0,65535)")
      
      DoWindow/F $lay_dens
      AppendLayoutObject/F=0/T=1/R=(42,587,288,770) Graph $(dataset_ID+"_"+brain_area+"_APldens"+class_short)
	   AppendLayoutObject/F=0/T=1/R=(303,583,564,771) Graph $(dataset_ID+"_"+brain_area+"_APrdens"+class_short)
	   SetDrawLayer UserFront
      SetDrawEnv fsize= 14
	   DrawText 84,582, brain_area+" areas: spatial distribution of the density of detections" 
          

       //detections
       
       
      Process_acronyms_list(acros, dataset_acros_left, dataset_waves_left, total_detections_left, atlas_acros, atlas_names,  1 , res_dets_left)
      Process_acronyms_list($(res_dets_left+"_acros"), dataset_acros_right, dataset_waves_right, total_detections_right, atlas_acros, atlas_names,  0 , res_dets_right)
      MakeBarGraph($(res_dets_left+"_sortvals"), $(res_dets_right+"_sortvals"), $(res_dets_left+"_labels"), $(res_dets_left+"_label_locs"),dataset_ID+"_"+brain_area+"_totdets"+class_short,"total number of detections")
     
       DoWindow/F $lay_dets
     
       if (lay_dets_existed)
        LayoutPageAction appendPage
       endif
      
      AppendLayoutObject/F=0/T=1/R=(45,78,570,540) Graph $(dataset_ID+"_"+brain_area+"_totdets"+class_short)
	   SetDrawLayer UserFront
	   SetDrawEnv fsize= 14
	   DrawText 29.25,60.75,"Data for "+ dataset_ID
	   SetDrawEnv fsize= 14
	   DrawText 101.25,75, brain_area+" areas: total number of detections. Detection class: \""+by_class+"\"" 
      
      lay_dets_existed=1
     
          
      
      Duplicate/O $(res_dets_left+"_wavelist") $(res_detsAP_left+"_wavelist")
      Duplicate/O $(res_dets_right+"_wavelist") $(res_detsAP_right+"_wavelist")
      Wave/T detsAP_left=$(res_detsAP_left+"_wavelist"), detsAP_right=$(res_detsAP_right+"_wavelist") 
      detsAP_left=ReplaceString("total_detections", detsAP_left[p], "detections")
      detsAP_right=ReplaceString("total_detections", detsAP_right[p], "detections")
      
      MakeAPGraph_uniqueAPs(acros, detsAP_left, min(plot_N,numpnts(detsAP_left)),dataset_ID+"_"+brain_area+"_APldets"+class_short,"number of detections", "(65535,0,0)")
      plotN=min(plot_N,numpnts(detsAP_left))
      MakeAPGraph_uniqueAPs(acros, detsAP_right, min(plot_N,numpnts(detsAP_right)),dataset_ID+"_"+brain_area+"_APrdets"+class_short,"number of detections", "(0,0,65535)")

      
      DoWindow/F $lay_dets
      AppendLayoutObject/F=0/T=1/R=(42,587,288,770) Graph $(dataset_ID+"_"+brain_area+"_APldets"+class_short)
	   AppendLayoutObject/F=0/T=1/R=(303,583,564,771) Graph $(dataset_ID+"_"+brain_area+"_APrdets"+class_short)
	   SetDrawLayer UserFront
      SetDrawEnv fsize= 14
	   DrawText 84,582, brain_area+" areas: spatial distribution of the detections"  
       
       

     else //master sort by the right side

	 
	     //density
      
      Process_acronyms_list(acros, dataset_acros_right, dataset_waves_right, total_density_right, atlas_acros, atlas_names,  1 , res_dens_right)
      Process_acronyms_list($(res_dens_right+"_acros"), dataset_acros_left, dataset_waves_left, total_density_left, atlas_acros, atlas_names,  0 , res_dens_left)
      MakeBarGraph($(res_dens_left+"_sortvals"), $(res_dens_right+"_sortvals"), $(res_dens_right+"_labels"), $(res_dens_right+"_label_locs"),dataset_ID+"_"+brain_area+"_totdens"+class_short,"total density of detections (mm\\S-2\\M)")
      
       DoWindow/F $lay_dens
     
      if (lay_dens_existed)
        LayoutPageAction appendPage
      endif
      
       AppendLayoutObject/F=0/T=1/R=(45,78,570,540) Graph $(dataset_ID+"_"+brain_area+"_totdens"+class_short)
	   SetDrawLayer UserFront
	   SetDrawEnv fsize= 14
	   DrawText 29.25,60.75,"Data for "+ dataset_ID
	   SetDrawEnv fsize= 14
	   DrawText 167.25,75, brain_area+" areas: total density of detections. Detection class: \""+by_class+"\"" 
      
      lay_dens_existed=1
      
      
      Duplicate/O $(res_dens_left+"_wavelist") $(res_densAP_left+"_wavelist")
      Duplicate/O $(res_dens_right+"_wavelist") $(res_densAP_right+"_wavelist")
      Wave/T densAP_left=$(res_densAP_left+"_wavelist"), densAP_right=$(res_densAP_right+"_wavelist") 
      densAP_left=ReplaceString("total_density", densAP_left[p], "density")
      densAP_right=ReplaceString("total_density", densAP_right[p], "density")
      
      MakeAPGraph_uniqueAPs(acros, densAP_left, min(plot_N,numpnts(densAP_left)),dataset_ID+"_"+brain_area+"_APldens"+class_short,"density of detections (mm\\S-2\\M)", "(65535,0,0)")
      MakeAPGraph_uniqueAPs(acros, densAP_right, min(plot_N,numpnts(densAP_right)),dataset_ID+"_"+brain_area+"_APrdens"+class_short,"density of detections (mm\\S-2\\M)", "(0,0,65535)")
      plotN=min(plot_N,numpnts(densAP_right))

   
      DoWindow/F $lay_dens
      AppendLayoutObject/F=0/T=1/R=(42,587,288,770) Graph $(dataset_ID+"_"+brain_area+"_APldens"+class_short)
	   AppendLayoutObject/F=0/T=1/R=(303,583,564,771) Graph $(dataset_ID+"_"+brain_area+"_APrdens"+class_short)
	   SetDrawLayer UserFront
      SetDrawEnv fsize= 14
	   DrawText 84,582, brain_area+" areas: spatial distribution of the density of detections" 
          




       //detections
       
       
      Process_acronyms_list(acros, dataset_acros_right, dataset_waves_right, total_detections_right, atlas_acros, atlas_names,  1 , res_dets_right)
      Process_acronyms_list($(res_dets_right+"_acros"), dataset_acros_left, dataset_waves_left, total_detections_left, atlas_acros, atlas_names,  0 , res_dets_left)
      MakeBarGraph($(res_dets_left+"_sortvals"), $(res_dets_right+"_sortvals"), $(res_dets_right+"_labels"), $(res_dets_right+"_label_locs"),dataset_ID+"_"+brain_area+"_totdets"+class_short,"total number of detections")
     
       DoWindow/F $lay_dets
     
       if (lay_dets_existed)
        LayoutPageAction appendPage
       endif
      
      AppendLayoutObject/F=0/T=1/R=(45,78,570,540) Graph $(dataset_ID+"_"+brain_area+"_totdets"+class_short)
	   SetDrawLayer UserFront
	   SetDrawEnv fsize= 14
	   DrawText 29.25,60.75,"Data for "+ dataset_ID
	   SetDrawEnv fsize= 14
	   DrawText 167.25,75, brain_area+" areas: total number of detections. Detection class: \""+by_class+"\"" 
      
      lay_dets_existed=1
     
     
      
      Duplicate/O $(res_dets_left+"_wavelist") $(res_detsAP_left+"_wavelist")
      Duplicate/O $(res_dets_right+"_wavelist") $(res_detsAP_right+"_wavelist")
      Wave/T detsAP_left=$(res_detsAP_left+"_wavelist"), detsAP_right=$(res_detsAP_right+"_wavelist") 
      detsAP_left=ReplaceString("total_detections", detsAP_left[p], "detections")
      detsAP_right=ReplaceString("total_detections", detsAP_right[p], "detections")
      
      MakeAPGraph_uniqueAPs(acros, detsAP_left, min(plot_N,numpnts(detsAP_left)),dataset_ID+"_"+brain_area+"_APldets"+class_short,"number of detections", "(65535,0,0)")
      plotN=min(plot_N,numpnts(detsAP_left))
      MakeAPGraph_uniqueAPs(acros, detsAP_right, min(plot_N,numpnts(detsAP_right)),dataset_ID+"_"+brain_area+"_APrdets"+class_short,"number of detections", "(0,0,65535)")

      
      DoWindow/F $lay_dets
      AppendLayoutObject/F=0/T=1/R=(42,587,288,770) Graph $(dataset_ID+"_"+brain_area+"_APldets"+class_short)
	   AppendLayoutObject/F=0/T=1/R=(303,583,564,771) Graph $(dataset_ID+"_"+brain_area+"_APrdets"+class_short)
	   SetDrawLayer UserFront
      SetDrawEnv fsize= 14
	   DrawText 84,582, brain_area+" areas: spatial distribution of the detections" 
       



	  endif
     
    endif

  else
      DoAlert /T="Warning" 0, "There are no loaded datasets!"
  endif

  
  
  ABBA_processing_GUI_main()
 
  

End





Function ABBA_processing_GUI_domany()

 SetDataFolder root:
 NVAR cancel_flag=gCancelFlag
 SVAR dataset_list=gDatasetList
 
 SVAR sortBy=gsortBy
  if(SVAR_Exists(sortBy)!=1)
	  String/G gsortBy="left"
	  SVAR sortBy=gsortBy
   endif 
   
   
 SVAR datasetIDlist=gdatasetIDlist
  if(SVAR_Exists(datasetIDlist)!=1)
	  String/G gdatasetIDlist=dataset_list
	  SVAR datasetIDlist=gdatasetIDlist
  endif  
   
 String dataset_IDlist=datasetIDlist
   
 SVAR globalclasses_list=root:gGlobalClasses
 if (SVAR_Exists(globalclasses_list)!=1)
  String/G root:gGlobalClasses
  SVAR globalclasses_list=root:gGlobalClasses
  globalclasses_list=""
 endif  
   
    
 SVAR byclass=gByClass
  if(SVAR_Exists(byclass)!=1)
	  String/G gByClass=StringFromList(0,globalclasses_list,";")
	  SVAR byclass=gByClass
   endif  
     
   
   
 NVAR plotN=gplotN
  if(NVAR_Exists(plotN)!=1)
	  Variable/G gplotN=10
	  NVAR plotN=gplotN
  endif    
      
 
 Variable list_l=ItemsInList(dataset_list,";"), plot_N
 
    
 SetDataFolder $"root:Brain_Areas:"
 
 String brain_areas_list=WaveList("*_acronyms", ";", "TEXT:1"), brain_areas, brain_area
 
 SetDataFolder $"root:"
 
  
 brain_areas=ReplaceString("_acronyms",brain_areas_list,"")
 brain_area=StringFromList(0, brain_areas, ";")
 
 plot_N=plotN
 
  SVAR brain_ar=gBrainArea
  if(SVAR_Exists(brain_ar)!=1)
	  String/G gBrainArea=brain_area
	  SVAR brain_ar=gBrainArea
	else
    brain_area=brain_ar
   endif
   
   SVAR avprefix=gAvPrefix
  if(SVAR_Exists(avprefix)!=1)
	  String/G gAvPrefix="av"
	  SVAR avprefix=gAvPrefix
	endif
 
 String LayoutsAverage
 
 SVAR Layouts_Average=gLayoutsAverage
  if(SVAR_Exists(Layouts_Average)!=1)
	  String/G gLayoutsAverage="LayoutAverages_dens;LayoutAverages_dets"
	  SVAR Layouts_Average=gLayoutsAverage
   endif
 
 LayoutsAverage=Layouts_Average
 
 
 String sort_By=sortBy, sortBy_list="left;right", av_prefix=avprefix, dataset_ID
 
 
 String globalclasses=globalclasses_list, by_class=byclass
  
 if (list_l)
  
 
   Prompt dataset_IDlist, "Define the ID list of the datasets to be averaged"
   Prompt by_class, "Choose the detection class", popup, globalclasses
   Prompt brain_area, "Choose the brain area (from Brain_Areas folder)", popup, brain_areas
   Prompt av_prefix, "Set a prefix for the new (average) dataset"
   Prompt sort_By, "Master sorting by which side?", popup, sortBy_list
   Prompt plot_N, "How many of the top AP-traces to plot?"
   Prompt LayoutsAverage, "Layout windows for appending the respective results (density;detections)"
	
   DoPrompt "Set analysis parameters", dataset_IDlist, by_class, brain_area, av_prefix, sort_By, plot_N, LayoutsAverage
	
   cancel_flag=V_flag
   
   if (cancel_flag==0)
   
     sortBy=sort_By
     brain_ar=brain_area
     byclass=by_class
     datasetIDlist=dataset_IDlist
     plotN=plot_N
     avprefix=av_prefix
     Layouts_Average=LayoutsAverage
     
     String lay_dens=StringFromList(0, LayoutsAverage,";"), lay_dets=StringFromList(1, LayoutsAverage,";")
     String populate_layout, graphs_left, graphs_right
     Variable i, lay_dens_existed=1, lay_dets_existed=1
     String class_path=by_class+":", class_short="C"+num2str(WhichListItem(by_class,globalclasses,";"))
     
     
     
     dataset_ID=av_prefix+"_"+brain_area
     
     Wave/T atlas_acros=$"root:Atlas_DB:atlas_acronyms", atlas_names=$"root:Atlas_DB:atlas_names"
     Wave/T acros=$"root:Brain_Areas:"+brain_area+"_acronyms"
     
     	  
     Average_across_mice(dataset_IDlist, by_class, acros, dataset_ID) //list the mouse folders as the first parameter
     
     //add a new dataset which is an average
     dataset_list=ReplaceString(avprefix+"_"+brain_area+";", dataset_list, "")+avprefix+"_"+brain_area+";"
     
	
     SetDataFolder $("root:"+dataset_ID+":res:")
     
     
     Wave/T dataset_acros_left=$"root:Dataset_acronyms:"+dataset_ID+"_left_all_acronyms"
     Wave/T dataset_waves_left=$"root:Dataset_acronyms:"+dataset_ID+"_left_all_waves"
     String total_density_left="root:"+dataset_ID+":left:total_density:"+class_path
     String total_detections_left="root:"+dataset_ID+":left:total_detections:"+class_path
     
     Wave/T dataset_acros_right=$"root:Dataset_acronyms:"+dataset_ID+"_right_all_acronyms"
     Wave/T dataset_waves_right=$"root:Dataset_acronyms:"+dataset_ID+"_right_all_waves"
     String total_density_right="root:"+dataset_ID+":right:total_density:"+class_path
     String total_detections_right="root:"+dataset_ID+":right:total_detections:"+class_path
	
	  String res_dens_left="root:"+dataset_ID+":res:"+class_path+"dens_left_"+brain_area
	  String res_dens_right="root:"+dataset_ID+":res:"+class_path+"dens_right_"+brain_area
	  String res_densAP_left="root:"+dataset_ID+":res:"+class_path+"densAP_left_"+brain_area
	  String res_densAP_right="root:"+dataset_ID+":res:"+class_path+"densAP_right_"+brain_area
	   
	  String res_dets_left="root:"+dataset_ID+":res:"+class_path+"dets_left_"+brain_area
	  String res_dets_right="root:"+dataset_ID+":res:"+class_path+"dets_right_"+brain_area
	  String res_detsAP_left="root:"+dataset_ID+":res:"+class_path+"detsAP_left_"+brain_area
	  String res_detsAP_right="root:"+dataset_ID+":res:"+class_path+"detsAP_right_"+brain_area
	   
     NewDataFolder/O/S $("root:"+dataset_ID+":res:"+by_class)
          
     if (strlen(WinList(lay_dens, ";", "WIN:4"))==0)
      NewLayout as "Average density across experiments"
      DoWindow/C $lay_dens
      lay_dens_existed=0
     endif
     
     if (strlen(WinList(lay_dets, ";", "WIN:4"))==0)
      NewLayout as "Average number of detections across experiments"
      DoWindow/C $lay_dets
      lay_dets_existed=0
     endif
  
        
     if (CmpStr(sort_By,"left")==0) //master sort by the left side
 
      //density
      
      Process_acronyms_list(acros, dataset_acros_left, dataset_waves_left, total_density_left, atlas_acros, atlas_names,  1 , res_dens_left)
      Process_acronyms_list($(res_dens_left+"_acros"), dataset_acros_right, dataset_waves_right, total_density_right, atlas_acros, atlas_names,  0 , res_dens_right)
      MakeBarGraph_average($(res_dens_left+"_sortvals"), $(res_dens_right+"_sortvals"), $(res_dens_left+"_labels"), $(res_dens_left+"_label_locs"),dataset_ID+"_totdens"+class_short,"total density of detections (mm\\S-2\\M)")
      
      
      DoWindow/F $lay_dens
     
      if (lay_dens_existed)
        LayoutPageAction appendPage
      endif
      
      AppendLayoutObject/F=0/T=1/R=(60,133,531,625) Graph $(dataset_ID+"_totdens"+class_short)
	   SetDrawLayer UserFront
	   SetDrawEnv fsize= 14
	   DrawText 29.25,60.75,"AVERAGE of "+dataset_IDlist
	   SetDrawEnv fsize= 14
	   DrawText 150.75,108, brain_area+" areas: total density of detections. Detection class: \""+by_class+"\""
      
      lay_dens_existed=1
      
         
      
      Duplicate/O $(res_dens_left+"_wavelist") $(res_densAP_left+"_wavelist")
      Duplicate/O $(res_dens_right+"_wavelist") $(res_densAP_right+"_wavelist")
      Wave/T densAP_left=$(res_densAP_left+"_wavelist"), densAP_right=$(res_densAP_right+"_wavelist") 
      densAP_left=ReplaceString("total_density", densAP_left[p], "density")
      densAP_right=ReplaceString("total_density", densAP_right[p], "density")
      
      graphs_left=MakeAPGraph_averageAPs(acros, dataset_IDlist, densAP_left, min(plot_N,numpnts(densAP_left)),dataset_ID+"_APldens"+class_short,1,"density of detections (mm\\S-2\\M)", "(65535,0,0)")
      plotN=min(plot_N,numpnts(densAP_left))
      graphs_right=MakeAPGraph_averageAPs(acros, dataset_IDlist, densAP_right, min(plot_N,numpnts(densAP_right)),dataset_ID+"_APrdens"+class_short,1,"density of detections (mm\\S-2\\M)", "(0,0,65535)")

      
      DoWindow/F $lay_dens
      LayoutPageAction appendPage
           
      for(i=0; i<ItemsInList(graphs_left,";"); i+=1)
       AppendLayoutObject/T=1/F=0 Graph $(StringFromList(i, graphs_left, ";"))
       AppendLayoutObject/T=1/F=0 Graph $(StringFromList(i, graphs_right, ";"))
      endfor
      
      Execute "Tile/O=1"
            
      SetDrawEnv fsize= 14
	   DrawText 141.75,762.75, brain_area+" areas: total density of detections"   
      
      
      
       //detections
       
       
      Process_acronyms_list(acros, dataset_acros_left, dataset_waves_left, total_detections_left, atlas_acros, atlas_names,  1 , res_dets_left)
      Process_acronyms_list($(res_dets_left+"_acros"), dataset_acros_right, dataset_waves_right, total_detections_right, atlas_acros, atlas_names,  0 , res_dets_right)
      MakeBarGraph_average($(res_dets_left+"_sortvals"), $(res_dets_right+"_sortvals"), $(res_dets_left+"_labels"), $(res_dets_left+"_label_locs"),dataset_ID+"_totdets"+class_short,"total number of detections")
      
      DoWindow/F $lay_dets
     
      if (lay_dets_existed)
        LayoutPageAction appendPage
      endif
      
      AppendLayoutObject/F=0/T=1/R=(60,133,531,625) Graph $(dataset_ID+"_totdets"+class_short)
	   SetDrawLayer UserFront
	   SetDrawEnv fsize= 14
	   DrawText 29.25,60.75,"AVERAGE of "+dataset_IDlist
	   SetDrawEnv fsize= 14
	   DrawText 150.75,108, brain_area+" areas: total detections. Detection class: \""+by_class+"\""
      
      lay_dets_existed=1
      
      
      Duplicate/O $(res_dets_left+"_wavelist") $(res_detsAP_left+"_wavelist")
      Duplicate/O $(res_dets_right+"_wavelist") $(res_detsAP_right+"_wavelist")
      Wave/T detsAP_left=$(res_detsAP_left+"_wavelist"), detsAP_right=$(res_detsAP_right+"_wavelist") 
      detsAP_left=ReplaceString("total_detections", detsAP_left[p], "detections")
      detsAP_right=ReplaceString("total_detections", detsAP_right[p], "detections")
      
      graphs_left=MakeAPGraph_averageAPs(acros, dataset_IDlist, detsAP_left, min(plot_N,numpnts(detsAP_left)),dataset_ID+"_APldets"+class_short,1,"number of detections", "(65535,0,0)")
      plotN=min(plot_N,numpnts(detsAP_left))
      graphs_right=MakeAPGraph_averageAPs(acros, dataset_IDlist, detsAP_right, min(plot_N,numpnts(detsAP_right)),dataset_ID+"_APrdets"+class_short,1,"number of detections", "(0,0,65535)")

      
      DoWindow/F $lay_dets
      LayoutPageAction appendPage
           
      for(i=0; i<ItemsInList(graphs_left,";"); i+=1)
       AppendLayoutObject/T=1/F=0 Graph $(StringFromList(i, graphs_left, ";"))
       AppendLayoutObject/T=1/F=0 Graph $(StringFromList(i, graphs_right, ";"))
      endfor
      
      Execute "Tile/O=1"
            
      SetDrawEnv fsize= 14
	   DrawText 141.75,762.75, brain_area+" areas: total detections"  
       

     else //master sort by the right side

	 
	     //density
      
      Process_acronyms_list(acros, dataset_acros_right, dataset_waves_right, total_density_right, atlas_acros, atlas_names,  1 , res_dens_right)
      Process_acronyms_list($(res_dens_right+"_acros"), dataset_acros_left, dataset_waves_left, total_density_left, atlas_acros, atlas_names,  0 , res_dens_left)
      MakeBarGraph_average($(res_dens_left+"_sortvals"), $(res_dens_right+"_sortvals"), $(res_dens_right+"_labels"), $(res_dens_right+"_label_locs"),dataset_ID+"_totdens"+class_short,"total density of detections (mm\\S-2\\M)")
      
      
       DoWindow/F $lay_dens
     
      if (lay_dens_existed)
        LayoutPageAction appendPage
      endif
      
      AppendLayoutObject/F=0/T=1/R=(60,133,531,625) Graph $(dataset_ID+"_totdens"+class_short)
	   SetDrawLayer UserFront
	   SetDrawEnv fsize= 14
	   DrawText 29.25,60.75,"AVERAGE of "+dataset_IDlist
	   SetDrawEnv fsize= 14
	   DrawText 150.75,108, brain_area+" areas: total density of detections. Detection class: \""+by_class+"\""
      
      lay_dens_existed=1
      
      
      
      Duplicate/O $(res_dens_left+"_wavelist") $(res_densAP_left+"_wavelist")
      Duplicate/O $(res_dens_right+"_wavelist") $(res_densAP_right+"_wavelist")
      Wave/T densAP_left=$(res_densAP_left+"_wavelist"), densAP_right=$(res_densAP_right+"_wavelist") 
      densAP_left=ReplaceString("total_density", densAP_left[p], "density")
      densAP_right=ReplaceString("total_density", densAP_right[p], "density")
      
      graphs_left=MakeAPGraph_averageAPs(acros, dataset_IDlist, densAP_left, min(plot_N,numpnts(densAP_left)),dataset_ID+"_APldens"+class_short,1, "density of detections (mm\\S-2\\M)", "(65535,0,0)")
      graphs_right=MakeAPGraph_averageAPs(acros, dataset_IDlist, densAP_right, min(plot_N,numpnts(densAP_right)),dataset_ID+"_APrdens"+class_short,1, "density of detections (mm\\S-2\\M)", "(0,0,65535)")
      plotN=min(plot_N,numpnts(densAP_right))
      
      
      DoWindow/F $lay_dens
      LayoutPageAction appendPage
     
      
      for(i=0; i<ItemsInList(graphs_left,";"); i+=1)
       AppendLayoutObject/T=1/F=0 Graph $(StringFromList(i, graphs_left, ";"))
       AppendLayoutObject/T=1/F=0 Graph $(StringFromList(i, graphs_right, ";"))
      endfor
      
      Execute "Tile/O=1"
            
      SetDrawEnv fsize= 14
	   DrawText 141.75,762.75, brain_area+" areas: total density of detections"  
      
      
      

       //detections
       
       
      Process_acronyms_list(acros, dataset_acros_right, dataset_waves_right, total_detections_right, atlas_acros, atlas_names,  1 , res_dets_right)
      Process_acronyms_list($(res_dets_right+"_acros"), dataset_acros_left, dataset_waves_left, total_detections_left, atlas_acros, atlas_names,  0 , res_dets_left)
      MakeBarGraph_average($(res_dets_left+"_sortvals"), $(res_dets_right+"_sortvals"), $(res_dets_right+"_labels"), $(res_dets_right+"_label_locs"),dataset_ID+"_totdets"+class_short,"total number of detections")
     
      
       DoWindow/F $lay_dets
     
      if (lay_dets_existed)
        LayoutPageAction appendPage
      endif
      
      AppendLayoutObject/F=0/T=1/R=(60,133,531,625) Graph $(dataset_ID+"_totdets"+class_short)
	   SetDrawLayer UserFront
	   SetDrawEnv fsize= 14
	   DrawText 29.25,60.75,"AVERAGE of "+dataset_IDlist
	   SetDrawEnv fsize= 14
	   DrawText 150.75,108, brain_area+" areas: total detections. Detection class: \""+by_class+"\""
      
      lay_dets_existed=1
      
      
      
      Duplicate/O $(res_dets_left+"_wavelist") $(res_detsAP_left+"_wavelist")
      Duplicate/O $(res_dets_right+"_wavelist") $(res_detsAP_right+"_wavelist")
      Wave/T detsAP_left=$(res_detsAP_left+"_wavelist"), detsAP_right=$(res_detsAP_right+"_wavelist") 
      detsAP_left=ReplaceString("total_detections", detsAP_left[p], "detections")
      detsAP_right=ReplaceString("total_detections", detsAP_right[p], "detections")
      
      graphs_left=MakeAPGraph_averageAPs(acros, dataset_IDlist, detsAP_left, min(plot_N,numpnts(detsAP_left)),dataset_ID+"_APldets"+class_short,1,"number of detections", "(65535,0,0)")
      plotN=min(plot_N,numpnts(detsAP_left))
      graphs_right=MakeAPGraph_averageAPs(acros, dataset_IDlist, detsAP_right, min(plot_N,numpnts(detsAP_right)),dataset_ID+"_APrdets"+class_short,1,"number of detections", "(0,0,65535)")




      DoWindow/F $lay_dets
      LayoutPageAction appendPage
            
      for(i=0; i<ItemsInList(graphs_left,";"); i+=1)
       AppendLayoutObject/T=1/F=0 Graph $(StringFromList(i, graphs_left, ";"))
       AppendLayoutObject/T=1/F=0 Graph $(StringFromList(i, graphs_right, ";"))
      endfor
      
      Execute "Tile/O=1"
            
      SetDrawEnv fsize= 14
	   DrawText 141.75,762.75, brain_area+" areas: total detections"  




	  endif
     
    endif

  else
      DoAlert /T="Warning" 0, "There are no loaded datasets!"
  endif

  
  
  ABBA_processing_GUI_main()
 
  

End





Function ABBA_processing_GUI_clear()

 SetDataFolder root:
 NVAR cancel_flag=gCancelFlag
 SVAR dataset_list=gDatasetList
 SVAR classes_list=gClassesList
 SVAR globalclasses_list=root:gGlobalClasses
 
 Variable list_l=ItemsInList(dataset_list,";"), i, j, N, flag

   
 String dataset_ID=StringFromList(0,dataset_list,";"),dataset_classes, s, s1
 

   Prompt dataset_ID, "Choose the dataset ID to be removed", popup, dataset_list
	
   DoPrompt "Choose dataset ID", dataset_ID
	
   cancel_flag=V_flag
   
   if (cancel_flag==0)
   
      DoAlert /T="Warning" 1, "Are you sure?"
   
    if (V_flag==1) 

    dataset_list=ReplaceString(dataset_ID+";",dataset_list,"")
    list_l-=1
    
    dataset_classes=StringByKey(dataset_ID, classes_list,":",";")
    N=ItemsInList(dataset_classes,",")
    
    classes_list=RemoveByKey(dataset_ID, classes_list,":",";")
            
       
    for(i=0; i<N;i+=1)
       flag=1
       s=StringFromList(i, dataset_classes,",")
       for(j=0; j<list_l; j+=1)
         s1=StringByKey(StringFromList(j, dataset_list, ";"), classes_list,":",";")
         if (WhichListItem(s, s1,",")!=-1)
           flag=0
           break
         endif         
       endfor
       if (flag)
        globalclasses_list=ReplaceString(s+";",globalclasses_list,"")
       endif
    endfor
    
    
    
    if (list_l==0)
     dataset_list=""
     classes_list=""
     globalclasses_list=""
    endif
    
   
    SetDataFolder root:
    KillDataFolder/Z $"root:"+dataset_ID
    KillWaves/Z $("root:Dataset_acronyms:"+dataset_ID+"_right_all_waves"),$("root:Dataset_acronyms:"+dataset_ID+"_right_all_acronyms")
    KillWaves/Z $("root:Dataset_acronyms:"+dataset_ID+"_left_all_waves"),$("root:Dataset_acronyms:"+dataset_ID+"_left_all_acronyms") 
    
    printf "Removed the dataset \"%s\".\r => %d datasets left in the memory\r", dataset_ID, list_l
    
    endif   
       
   endif

  
  ABBA_processing_GUI_main()
 
  

End






Function UserMainChoice(ctrlName) : ButtonControl
	String ctrlName
   
   NVAR cancel_flag=gCancelFlag
   SVAR dataset_list=gDatasetList
 
     
   if (stringmatch(ctrlName,"button3"))
    cancel_flag=1
    DoWindow/K tmp_PauseforChoosing
   
   elseif (stringmatch(ctrlName,"button0"))
    DoWindow/K tmp_PauseforChoosing
    ABBA_processing_GUI_load()
      
   elseif (stringmatch(ctrlName,"button1"))
    DoWindow/K tmp_PauseforChoosing
    ABBA_processing_GUI_doone()
    
   elseif (stringmatch(ctrlName,"button2"))
    DoWindow/K tmp_PauseforChoosing
    ABBA_processing_GUI_domany()
   
   elseif (stringmatch(ctrlName,"button0k"))
    
    if (ItemsInList(dataset_list,";"))
       DoWindow/K tmp_PauseforChoosing
       ABBA_processing_GUI_clear()
    else
     DoAlert /T="Warning" 0, "There are no loaded datasets!"
    endif
    
   endif

			
End





Function create_folders(top_node)
 String top_node

NewDataFolder/O/S $top_node

NewDataFolder/O res

NewDataFolder/O/S right

NewDataFolder/O total_detections
NewDataFolder/O total_density
NewDataFolder/O total_areas
NewDataFolder/O detections
NewDataFolder/O density
NewDataFolder/O areas

SetDataFolder ::

NewDataFolder/O/S left

NewDataFolder/O total_detections
NewDataFolder/O total_density
NewDataFolder/O total_areas
NewDataFolder/O detections
NewDataFolder/O density
NewDataFolder/O areas

SetDataFolder ::
SetDataFolder ::

End



Function create_folders_load_data(top_node, filepath, prefix, suffix)
 String top_node, filepath, prefix, suffix

 String filename
 
 Variable i, j, N, Nclasses
 String s, s1, class_names
 
 SVAR classes_list=root:gClassesList
 if (SVAR_Exists(classes_list)!=1)
  String/G root:gClassesList
  SVAR classes_list=root:gClassesList
  classes_list=""
 endif
 
 SVAR globalclasses_list=root:gGlobalClasses
 if (SVAR_Exists(globalclasses_list)!=1)
  String/G root:gGlobalClasses
  SVAR globalclasses_list=root:gGlobalClasses
  globalclasses_list=""
 endif
 
 
NewPath /O/Q/Z pth filepath

SetDataFolder $"root:"

NewDataFolder/O/S $top_node

NewDataFolder/O/S right

NewDataFolder/O/S total_detections
filename=prefix+"right_data_vsAP_"+suffix+"_tot_detections.csv"
DoWindow/K tmp_table
LoadWave /J/K=0/P=pth/W/A/Q/O filename
Get_acronyms_from_waves(S_waveNames, "root:Dataset_acronyms", top_node+"_right_all", root:Atlas_DB:atlas_acronyms)

class_names=split_by_classes(S_waveNames, 1)
Nclasses=ItemsInList(class_names, ",")

classes_list+=top_node+":"+class_names+";"

for (i=0; i<Nclasses; i+=1)
 s=StringFromList(i, class_names, ",")
 if (WhichListItem(s, globalclasses_list, ";")==-1)
   globalclasses_list+=s+";"
 endif
endfor



NewDataFolder/O/S $"root:"+top_node+":right:total_density"
filename=prefix+"right_data_vsAP_"+suffix+"_tot_density.csv"
LoadWave /J/K=0/P=pth/W/A/Q/O filename
split_by_classes(S_waveNames, 0)

SetDataFolder ::


NewDataFolder/O/S total_areas
filename=prefix+"right_data_vsAP_"+suffix+"_tot_areas.csv"
LoadWave /J/P=pth/W/A/Q/O filename
SetDataFolder ::


NewDataFolder/O/S detections

for (j=0; j<Nclasses; j+=1) //over classes

s=StringFromList(j, class_names, ",")
if (stringmatch(s,"Detections"))
  s1=""
else 
  s1="_"+s
endif

NewDataFolder/O/S $s

filename=prefix+"right_data_vsAP_"+suffix+"_Detections"+s1+".csv"
LoadWave /J/P=pth/W/A/Q/O filename
NewDataFolder/O dropped_nan
 s=WaveList("*",",","")
 N=ItemsInList(s,",")
 Wave AP_coord=$"AP_coord_mm"
 for (i=0;i<N;i+=1)
  s1=StringFromList(i,s,",")
  if (stringmatch(s1,"AP_coord_mm")!=1)
   Sort AP_coord, $s1
   drop_Nan($s1,"dropped_nan")
  else
   continue
  endif
 endfor
 Sort AP_coord, AP_coord
 
 SetDataFolder ::
 
endfor //over classes
 
SetDataFolder ::


NewDataFolder/O/S density

for (j=0; j<Nclasses; j+=1) //over classes

s=StringFromList(j, class_names, ",")
if (stringmatch(s,"Detections"))
  s1=""
else 
  s1="_"+s
endif

NewDataFolder/O/S $s

filename=prefix+"right_data_vsAP_"+suffix+"_Density"+s1+".csv"
LoadWave /J/P=pth/W/A/Q/O filename
NewDataFolder/O dropped_nan
 s=WaveList("*",",","")
 N=ItemsInList(s,",")
 Wave AP_coord=$"AP_coord_mm"
 for (i=0;i<N;i+=1)
  s1=StringFromList(i,s,",")
  if (stringmatch(s1,"AP_coord_mm")!=1)
   Sort AP_coord, $s1
   drop_Nan($s1,"dropped_nan")
  else
   continue
  endif
 endfor
 Sort AP_coord, AP_coord
 
 SetDataFolder ::
 
endfor //over classes
 
SetDataFolder ::



NewDataFolder/O/S areas
filename=prefix+"right_data_vsAP_"+suffix+"_areas.csv"
LoadWave /J/P=pth/W/A/Q/O filename
NewDataFolder/O dropped_nan
 s=WaveList("*",",","")
 N=ItemsInList(s,",")
 Wave AP_coord=$"AP_coord_mm"
 for (i=0;i<N;i+=1)
  s1=StringFromList(i,s,",")
  if (stringmatch(s1,"AP_coord_mm")!=1)
   Sort AP_coord, $s1
   drop_Nan($s1,"dropped_nan")
  else
   continue
  endif
 endfor
 Sort AP_coord, AP_coord
SetDataFolder ::




NewDataFolder/O/S AP_coordinates
filename=prefix+"collated_right_AP_coordinates.csv"
LoadWave /J/P=pth/W/A/Q/O/K=2 filename
printf "  Extracted AP coordinate axis for %d acronyms\r", process_AP_coord_lists($"Class", $"ROI_Atlas_AP")
SetDataFolder ::

SetDataFolder ::




NewDataFolder/O/S left

NewDataFolder/O/S total_detections
filename=prefix+"left_data_vsAP_"+suffix+"_tot_detections.csv"
DoWindow/K tmp_table
LoadWave /J/K=0/P=pth/W/A/Q/O filename
Get_acronyms_from_waves(S_waveNames,"root:Dataset_acronyms",top_node+"_left_all", root:Atlas_DB:atlas_acronyms)
split_by_classes(S_waveNames, 0)


NewDataFolder/O/S $"root:"+top_node+":left:total_density"
filename=prefix+"left_data_vsAP_"+suffix+"_tot_density.csv"
LoadWave /J/K=0/P=pth/W/A/Q/O filename
split_by_classes(S_waveNames, 0)


SetDataFolder ::

NewDataFolder/O/S total_areas
filename=prefix+"left_data_vsAP_"+suffix+"_tot_areas.csv"
LoadWave /J/P=pth/W/A/Q/O filename
SetDataFolder ::



NewDataFolder/O/S detections

for (j=0; j<Nclasses; j+=1) //over classes

s=StringFromList(j, class_names, ",")
if (stringmatch(s,"Detections"))
  s1=""
else 
  s1="_"+s
endif

NewDataFolder/O/S $s

filename=prefix+"left_data_vsAP_"+suffix+"_Detections"+s1+".csv"
LoadWave /J/P=pth/W/A/Q/O filename
NewDataFolder/O dropped_nan
 s=WaveList("*",",","")
 N=ItemsInList(s,",")
 Wave AP_coord=$"AP_coord_mm"
 for (i=0;i<N;i+=1)
  s1=StringFromList(i,s,",")
  if (stringmatch(s1,"AP_coord_mm")!=1)
   Sort AP_coord, $s1
   drop_Nan($s1,"dropped_nan")
  else
   continue
  endif
 endfor
 Sort AP_coord, AP_coord
 
 SetDataFolder ::
 
endfor //over classes

 
SetDataFolder ::

NewDataFolder/O/S density

for (j=0; j<Nclasses; j+=1) //over classes

s=StringFromList(j, class_names, ",")
if (stringmatch(s,"Detections"))
  s1=""
else 
  s1="_"+s
endif

NewDataFolder/O/S $s

filename=prefix+"left_data_vsAP_"+suffix+"_Density"+s1+".csv"
LoadWave /J/P=pth/W/A/Q/O filename
NewDataFolder/O dropped_nan
 s=WaveList("*",",","")
 N=ItemsInList(s,",")
 Wave AP_coord=$"AP_coord_mm"
 for (i=0;i<N;i+=1)
  s1=StringFromList(i,s,",")
  if (stringmatch(s1,"AP_coord_mm")!=1)
   Sort AP_coord, $s1
   drop_Nan($s1,"dropped_nan")
  else
   continue
  endif
 endfor
 Sort AP_coord, AP_coord
 
 SetDataFolder ::
 
endfor //over classes
 
 
SetDataFolder ::

NewDataFolder/O/S areas
filename=prefix+"left_data_vsAP_"+suffix+"_areas.csv"
LoadWave /J/P=pth/W/A/Q/O filename
NewDataFolder/O dropped_nan
 s=WaveList("*",",","")
 N=ItemsInList(s,",")
 Wave AP_coord=$"AP_coord_mm"
 for (i=0;i<N;i+=1)
  s1=StringFromList(i,s,",")
  if (stringmatch(s1,"AP_coord_mm")!=1)
   Sort AP_coord, $s1
   drop_Nan($s1,"dropped_nan")
  else
   continue
  endif
 endfor
 Sort AP_coord, AP_coord
SetDataFolder ::

NewDataFolder/O/S AP_coordinates
filename=prefix+"collated_left_AP_coordinates.csv"
LoadWave /J/P=pth/W/A/Q/O/K=2 filename
printf "  Extracted AP coordinate axis for %d acronyms\r", process_AP_coord_lists($"Class", $"ROI_Atlas_AP")


SetDataFolder $("root:"+top_node)
NewDataFolder/O/S res

for (j=0; j<Nclasses; j+=1) //over classes

s=StringFromList(j, class_names, ",")
if (stringmatch(s,"Detections"))
  s1=""
else 
  s1="_"+s
endif
NewDataFolder/O $s

endfor


SetDataFolder $"root:"


KillPath/Z pth

End


Function process_AP_coord_lists(acronym, AP_coords)
 Wave/T acronym, AP_coords
 
 Variable i, N=numpnts(acronym), cntr=0, j, M
 
 for(i=0; i<N; i+=1)
  if (strlen(acronym[i])>0)
   M=ItemsInList(AP_coords[i],";")
   Make/N=(M)/O $(acronym[i]+"_AP_coord")
   Wave APs=$(acronym[i]+"_AP_coord")
   APs=str2num(StringfromList(p,AP_coords[i],";"))
   Sort APs, APs
   cntr+=1
  endif

 endfor 

  return cntr
 
End



Function cycling(in)
 Wave/T in
 Variable i, N=numpnts(in)
 
 for(i=0; i<N; i+=1)
  Execute "create_folders(\""+in[i]+"\")"
 endfor
 
 
  
End


Function/T sanitize(in_str)
 String in_str
 
 String bad_ones="\/:*?<>|", clean=in_str
 Variable i, N=strlen(bad_ones)
 
 for(i=0;i<N;i+=1)
  clean=replacestring(bad_ones[i],clean,"_")  
 endfor
  
  clean=replacestring(" ",clean,"")
  
  return clean
 
End


Function/T Split_by_classes(waves_list, report)
 String waves_list
 Variable report
 
 Variable i, j, classes, N=ItemsInList(waves_list, ";")
 String s, str, class_names_list=""
 
 Wave idx=$"XWave"
   
 if (WhichListItem("Class_name", waves_list,",")==-1) //compatibility with the old style Python script when the classes wave did not exist
   if (numpnts(idx)>1)
     printf "Error: cound not find the wave with the names of the detection classes. Aborted."
     return "" 
   else
     Make/T/O/N=1 $"Class_name" = {"Detections"}
     waves_list=waves_list+"Class_name;"
   endif
 endif 
 
 Wave/T class_list=$("Class_name")
 
 classes=numpnts(class_list)
 
 for(i=0; i<classes; i+=1)
  str=sanitize(class_list[i])
  class_names_list+=str+","
  NewDataFolder/O $str  
 endfor
 

  for(i=0; i<N; i+=1)
  
  s=StringFromList(i,waves_list,";")
  
  if (stringmatch(s,"XWave") || stringmatch(s,"AP_coord_mm") || stringmatch(s,"Class_name"))
    KillWaves/Z $s
    continue
  endif
   
   Wave wav_i=$s
   
   for(j=0;j<classes;j+=1)
    str=":"+StringFromList(j,class_names_list,",")+":"+s
    Make/N=1/O $str
    Wave wav_i_j=$str
    wav_i_j[0]=wav_i[j]
   endfor
  
   KillWaves/Z wav_i

  endfor

 if (report) 
  printf "Found data for %d classes.\r", classes
 endif
 
 return class_names_list

End



Function Get_acronyms_from_waves(waves_list, res_folder, res, atlas_db) 
 String waves_list, res_folder, res
 Wave/T atlas_db
 
 String table=StringFromList(0,WinList("*",";","WIN:"),";")
 Variable i=0, cntr=0, j, M=numpnts(atlas_db), maxlen, N=ItemsInList(waves_list, ";")
 
 NewDataFolder/O $res_folder
 
 Make/T/O/N=0 $(res_folder+":"+res+"_waves"), $(res_folder+":"+res+"_acronyms") 
 Wave/T wavs=$(res_folder+":"+res+"_waves"), acros=$(res_folder+":"+res+"_acronyms") 
 
 String s, str
 
  
 for(i=0; i<N; i+=1)
  
  s=StringFromList(i,waves_list,";")
  
  if (stringmatch(s,"XWave") || stringmatch(s,"AP_coord_mm") || stringmatch(s,"Class_name"))
    continue
  endif
   
   InsertPoints cntr, 1, wavs, acros
   
   wavs[cntr]=s
   maxlen=0
   for(j=0;j<M;j+=1) 
      str=ReplaceString("/",ReplaceString("-",atlas_db[j],"_"),"_")+"_*"
    if (stringmatch(s,str)==1 && strlen(str)>maxlen)
      acros[cntr]=atlas_db[j]
      maxlen=strlen(str)
    endif
   endfor
   
   cntr+=1


  endfor
  
  printf "Created index of acronyms and data for %d loaded waves\r", cntr
  
  return cntr
  
 
End 


Function Get_acronyms_from_table(res_folder, res, atlas_db) //for the top window
 String res_folder, res
 Wave/T atlas_db
 
 String table=StringFromList(0,WinList("*",";","WIN:"),";")
 Variable i=0, cntr=0, j, M=numpnts(atlas_db), maxlen
 
 NewDataFolder/O/S $res_folder
 
 Make/T/O/N=0 $(res+"_waves"), $(res+"_acronyms") 
 Wave/T wavs=$(res+"_waves"), acros=$(res+"_acronyms") 
 
 String s, str
 
  do
   Wave wav_i=WaveRefIndexed(table, i, 1)
   if (WaveExists(wav_i)==0)
     break
   elseif (stringmatch(NameOfWave(wav_i),"AP_coord_mm"))
     i+=1
     continue
   endif
   
   s=NameOfWave(wav_i)
   InsertPoints cntr, 1, wavs, acros
   
   wavs[cntr]=s
   maxlen=0
   for(j=0;j<M;j+=1) 
      str=ReplaceString("/",ReplaceString("-",atlas_db[j],"_"),"_")+"_*"
    if (stringmatch(s,str)==1 && strlen(str)>maxlen)
      acros[cntr]=atlas_db[j]
      maxlen=strlen(str)
    endif
   endfor
   
   cntr+=1
   i+=1
  while(1)
  
  printf "Created index of acronyms and data for %d waves in the top table.\r", cntr
  
 
End 





Function CompareTextWaves(w1, w2, sort_flag)
 Wave/T w1, w2
 Variable sort_flag
 Variable i, N=numpnts(w1)
 variable flg=1
 
 if (N!=numpnts(w2) || N==0)
   return 0
 endif
 
 if (sort_flag)
  Sort/A w1, w1
  Sort/A w2, w2
 endif
 
 
 for(i=0;i<N;i+=1)
  if (stringmatch(w1[i],w2[i])==0)
    flg=0
    break
  endif  
 endfor
 
 return flg
 
 
 
 
End



Function StrucsFromString(str, dict_acros, dict_titles, res, sort_flag)
String str
Wave/T dict_acros, dict_titles
String res
Variable sort_flag

variable i, N=ItemsInList(str,",")

Make/N=(N)/T/O $(res+"_acronyms"),$(res+"_names")
Wave/T res_a=$(res+"_acronyms"),res_n=$(res+"_names")
 
res_n=""

 res_a=StringFromList(p, str, ",")
 
 for(i=0; i<N; i+=1)
  FindValue/TEXT=(res_a[i])/TXOP=2/Z dict_acros
  if (V_value!=-1)
   res_n[i]=dict_titles[V_value]
  endif
 endfor

 if (sort_flag!=0)
  Sort/A res_a,res_a,res_n
 endif

 return 0

End


Function Process_acronyms_list(acronyms, acros_db, waves_db, path_prefix, atlas_db, names_db, sort_flag, res)
 Wave/T acronyms, acros_db, waves_db
 String path_prefix
 Wave/T atlas_db, names_db
 Variable sort_flag
 String res
 
 Variable i, N=numpnts(acronyms), st=0
 String str
 
 Make/T/O/N=(0) $(res+"_wavelist"), $(res+"_names"), $(res+"_acros"),$(res+"_labels"),$(res+"_dots_waves")
 Make/O/N=(0) $(res+"_sortvals"),$(res+"_sortsem"),$(res+"_label_locs")
 Wave/T acros=$(res+"_acros")
 Wave/T names=$(res+"_names")
 Wave/T list=$(res+"_wavelist")
 Wave/T labels=$(res+"_labels")
 Wave/T dots_waves=$(res+"_dots_waves")
 Wave vals=$(res+"_sortvals"),sems=$(res+"_sortsem"), llocs=$(res+"_label_locs")
 //acros=acronyms
// names=""
 //list=""
// vals=nan
// llocs=p+0.5

 st=0
 
  for(i=0; i<N; i+=1)
    str=acronyms[i]
    FindValue/TEXT=(str)/TXOP=4/Z acros_db
   if (V_value!=-1)
     InsertPoints st, 1, acros, names, list, labels, vals, llocs, sems, dots_waves
     acros[st]=str
     list[st]=path_prefix+waves_db[V_value]
     Wave val=$(list[st])
     vals[st]=val[0]
     Wave sem=$(ReplaceString(NameOfWave(val),list[st],"sem_waves:"+NameOfWave(val)))
     if (WaveExists(sem))
      sems[st]=sem[0]
     else
      sems[st]=nan
     endif
     
     //in case of average waves, look for individual data points
     //if exist - process them
     Wave dots=$(ReplaceString(NameOfWave(val),list[st],"dots_waves:"+NameOfWave(val)))
     if (WaveExists(dots))
      dots_waves[st]=GetWavesDataFolder(dots, 2)
     else
      dots_waves[st]=""
     endif
     
     
     FindValue/TEXT=(str)/TXOP=4/Z atlas_db
     names[st]=names_db[V_value]
     //Wave val=$(list[st])
     //vals[st]=val[0]   
     st+=1 
   endif
   
  endfor
   
   if (sort_flag!=0 && st>0)
    Sort/R vals, sems, vals, list, names, acros, dots_waves
    llocs=p+0.5
   endif
   
   for(i=0;i<st; i+=1)
    if (strlen(dots_waves[i])>0)
     NewDataFolder/O/S $(res+"_dots_locs")
      Duplicate/O $(dots_waves[i]) $(NameOfWave($(dots_waves[i])))
      Wave dots_locations=$(NameOfWave($(dots_waves[i])))
      dots_locations=i+0.5
      
      
     SetDataFolder ::
    else
     continue
    endif
       
   endfor
 
 labels=names+" ; "+acros
 
 //Edit vals, list, names, acros, labels, llocs

End




Function MakeBarGraph(w_left, w_right, names, llocs, res_win, axis_name)
 Wave w_left, w_right //matched values to be plotted for the left and the right sides
 Wave/T names // strings to use as the axis tick labels
 Wave llocs // locations of the ticks
 String res_win
 String axis_name
 Variable max_buf, N=numpnts(w_left)
 DoWindow/K $res_win
   
   Make/O/T/N=(N) $(res_win+"ct")
   Wave/T cat=$(res_win+"ct")
   cat=""
  
	Display /W=(85.2,53.6,556.8,547.4)/VERT/T w_left vs cat
	AppendToGraph/VERT/T=top1 w_right vs cat
	ModifyGraph fSize(top1)=9,axisEnab(top)={0,0.5},axisEnab(top1)={0.5,1.0},freePos(top1)=0
   Wavestats/Q w_right
   SetAxis top1 0,V_max*1.05
   Wavestats/Q w_left
	max_buf=V_max
   SetAxis/R top, V_max*1.05,0
   SetAxis/R left, max(numpnts(w_left),numpnts(w_left))*1.03, *
	DoWindow/C $res_win
	
	ModifyGraph mode=5
	Execute "ModifyGraph rgb("+NameOfWave(w_right)+")=(1,4,52428)"
	//Execute "ModifyGraph muloffset("+NameOfWave(w_left)+")={0,-1}"
	ModifyGraph tick(left)=3, margin(left)=216
	ModifyGraph fSize(left)=8,fSize(top)=9
	ModifyGraph lowTrip(top)=1
	ModifyGraph axThick(left)=0
	ModifyGraph notation(top)=1
	//ModifyGraph prescaleExp(top)=6
	ModifyGraph btLen=4, zero(top)=1
	Label top axis_name//"total density (mm\\S-2\\M)"
	ModifyGraph lblLatPos(top)=56
	TextBox/C/N=text0/J/F=0/A=MC/X=23.53/Y=-29.73 "\\Z09\\s("+NameofWave(w_left)+")left side\r\\s("+NameofWave(w_right)+")right side"

   AppendToGraph/L=label_left/T w_left
   ModifyGraph fSize(label_left)=8,axThick(label_left)=0,userticks(label_left)={llocs,names}, freePos(label_left)=0
   Execute "ModifyGraph lsize("+NameOfWave(w_left)+"#1)=0"
   SetAxis/R label_left N+0.5,0

    printf "//Plotted data for %d nuclei.\n", numpnts(w_left)
End





Function MakeBarGraph_average(w_left, w_right, names, llocs, res_win, axis_name)
 Wave w_left, w_right //matched values to be plotted for the left and the right sides
 Wave/T names // strings to use as the axis tick labels
 Wave llocs // locations of the ticks
 String res_win
 String axis_name
 
 String s1, s2
 
 String left_root, right_root
 
 Variable max_buf, i, N=numpnts(w_left)
 
 Make/O/T/N=(N) $(res_win+"_cat")
   Wave/T cat=$(res_win+"_cat")
   cat=""
 
 DoWindow/K $res_win
	Display /W=(85.2,53.6,556.8,547.4)/VERT/T w_left vs cat
	AppendToGraph/VERT/T=top1 w_right vs cat
	ModifyGraph fSize(top1)=9,axisEnab(top)={0,0.5},axisEnab(top1)={0.5,1.0},freePos(top1)=0
   
   //SetAxis/R left, max(numpnts(w_left),numpnts(w_left))*1.03, *
   SetAxis/R left, *, *
	DoWindow/C $res_win
	ModifyGraph userticks(left)={llocs,names}
	ModifyGraph mode=5
	Execute "ModifyGraph rgb("+NameOfWave(w_right)+")=(1,4,52428)"
	//Execute "ModifyGraph muloffset("+NameOfWave(w_left)+")={0,-1}"
	ModifyGraph tick(left)=3, margin(left)=216
	ModifyGraph fSize(left)=8,fSize(top)=9
	ModifyGraph lowTrip(top)=1
	ModifyGraph axThick(left)=0
	ModifyGraph notation(top)=1
	//ModifyGraph prescaleExp(top)=6
	ModifyGraph btLen=4, zero(top)=1
	Label top axis_name//"total density (mm\\S-2\\M)"
	ModifyGraph lblLatPos(top)=56
	TextBox/C/N=text0/J/F=0/A=MC/X=23.53/Y=-29.73 "\\Z09\\s("+NameofWave(w_left)+")left\r\\s("+NameofWave(w_right)+")right"
	
   AppendToGraph/L=label_left/T w_left
   ModifyGraph fSize(label_left)=8,axThick(label_left)=0,userticks(label_left)={llocs,names}, freePos(label_left)=0
   Execute "ModifyGraph lsize("+NameOfWave(w_left)+"#1)=0"
   SetAxis/R label_left N,0
	

   s1=NameOfWave(w_left)
   s2=ReplaceString("vals",s1,"sem")
   Execute "ErrorBars "+s1+" Y,wave=("+s2+","+s2+")"
   
   s1=NameOfWave(w_right)
   s2=ReplaceString("vals",s1,"sem")
   Execute "ErrorBars "+s1+" Y,wave=("+s2+","+s2+")"
   
   //adding individual points
   s1=NameOfWave(w_left)
   s2=StringFromList(ItemsInList(s1,"_")-1,s1,"_")
   left_root=ReplaceString(s2,s1,"")
   
   max_buf=0
   
   Wave/T dots_wave=$(left_root+"dots_waves")
   for(i=0; i<numpnts(dots_wave); i+=1)
    s1=dots_wave[i]
    s2=StringFromList(ItemsInList(s1,":")-1,s1,":")
    Wave dots=$(s1), dots_locs=$(":"+left_root+"dots_locs:"+s2)
    Wavestats/Q dots
    max_buf=max(max_buf, V_max)
    AppendToGraph/VERT/T=top/L=label_left dots vs dots_locs
    s1=NameOfWave(dots)
    Execute "ModifyGraph mode("+s1+")=3,marker("+s1+")=19,msize("+s1+")=1,offset("+s1+")={-0.25,0}"
   endfor
   
   SetAxis/R top, max_buf*1.05,0
   
   max_buf=0
   
   s1=NameOfWave(w_right)
   s2=StringFromList(ItemsInList(s1,"_")-1,s1,"_")
   right_root=ReplaceString(s2,s1,"")   
   
   Wave/T dots_wave=$(right_root+"dots_waves")
   for(i=0; i<numpnts(dots_wave); i+=1)
    s1=dots_wave[i]
    s2=StringFromList(ItemsInList(s1,":")-1,s1,":")
    Wave dots=$(s1), dots_locs=$(":"+right_root+"dots_locs:"+s2)
    Wavestats/Q dots
    max_buf=max(max_buf, V_max)
    AppendToGraph/VERT/T=top1/L=label_left dots vs dots_locs
    s1=NameOfWave(dots)+"#1"
    Execute "ModifyGraph mode("+s1+")=3,marker("+s1+")=19,msize("+s1+")=1,rgb("+s1+")=(1,4,52428),offset("+s1+")={-0.25,0}"
   endfor
   
   SetAxis top1 0,max_buf*1.05
   
   
  
      

    printf "//Plotted data for %d nuclei.\n", numpnts(w_left)
End







Function MakeAPGraph(w_data, w_AP, top_n, res_win, axis_name)
 Wave/T w_data
 Wave w_AP
 Variable top_n
 String res_win
 String axis_name
 
 Variable i
 
 DoWindow/K $res_win
 
 for(i=0;i<top_n;i+=1)
  Wave dat=$(w_data[i])
 	if (i==0)
 	 Display /W=(85.2,53.6,556.8,547.4) dat vs w_AP
 	 DoWindow/C $res_win
	else
	 AppendToGraph dat vs w_AP
	endif
  endfor
  
 ModifyGraph btLen=4
 Label left axis_name//"density (mm\\S-2\\M)";DelayUpdate
 Label bottom "AP coordinate (mm)"
  
  printf "//Plotted %d graphs.\n", top_n

End


Function drop_Nan(input, output_folder)
 Wave input
 String output_folder
 
 Variable i, N=numpnts(input)
 
 Duplicate/O input, $(":"+output_folder+":"+NameOfWave(input))
 Wave target=$(":"+output_folder+":"+NameOfWave(input))
 for (i=0;i<N;i+=1)
  if (NumType(target[i])==2)
   DeletePoints i, 1, target
   i-=1
   N-=1
  endif
 endfor
 
End


Function MakeAPGraph_uniqueAPs(acronym_lookup, w_data, top_n, res_win, axis_name, color)
 Wave/T acronym_lookup //text wave with the list of acronyms as in atlas.
 //needed to be supplied because of "non-liberal" wave naming of the data which replaced symbols like "/" or "-" in the acronyms with "_"  
 Wave/T w_data //list of waves with the data to be plotted
  //the AP coordinate wave name is then deduced from the w_data list and the "liberal" list of acronyms
 Variable top_n //how many to plot from the start of w_data list 
 String res_win //result prefix
 String axis_name //legend for X-axis
 String color //RGB color to be assigned to the traces 
 
 Variable i, j, M=numpnts(acronym_lookup), match
 String path_to, s, s1, s2
 
 DoWindow/K $res_win
 
 for(i=0;i<top_n;i+=1)
  Wave dat_nans=$(w_data[i])
  s=GetWavesDataFolder(dat_nans, 1)
  Wave dat=$(s+"dropped_nan:"+NameOfWave(dat_nans))
  path_to="root:"+StringFromList(1,w_data[i],":")+":"+StringFromList(2,w_data[i],":")+":AP_coordinates:"
  j=-1
  do
   j+=1
   s1=NameOfWave(dat)
   s2=CleanupName(acronym_lookup[j],0)
   match=1-stringmatch(s1,s2+"*")*stringmatch(s1[strlen(s2)],"_") 
  while (match && j<M-1)
   if (j==M-1 && match)
     printf "Did not find a matching acronym for the data wave %s! Please check the list of acronyms. For now, aborted.\r", w_data[i]
     return -1
   endif
    
  Wave w_AP=$(path_to+"'"+acronym_lookup[j]+"_AP_coord'")

  if (numpnts(dat)!=numpnts(w_AP))
   printf "Warning! Waves %s and %s have different number of points!\r", NameOfWave(dat), NameOfWave(w_AP)
  endif

 
 	if (i==0)
 	 Display /W=(85.2,53.6,556.8,547.4) dat vs w_AP
 	 DoWindow/C $res_win
	else
	 AppendToGraph dat vs w_AP
	endif
	
	Execute "ModifyGraph mode("+NameOfWave(dat)+")=4,marker("+NameOfWave(dat)+")=8,msize("+NameOfWave(dat)+")=1.5, rgb("+NameOfWave(dat)+")="+color
	
  endfor

 
 ModifyGraph btLen=4
 Label left axis_name//"density (mm\\S-2\\M)";DelayUpdate
 Label bottom "AP coordinate (mm)"
  
  printf "//Plotted %d graphs.\n", top_n
  
  return top_n

End


Function/T MakeAPGraph_averageAPs(acronym_lookup, mouse_list, w_data, top_n, res_win, AP_mode, axis_name, color)
 Wave/T acronym_lookup //text wave with the list of acronyms as in atlas.
 //needed to be supplied because of "non-liberal" wave naming of the data which replaced symbols like "/" or "-" in the acronyms with "_"  
 String mouse_list// , - separate list of folders with individual datasets
 Wave/T w_data //list of waves with the data to be plotted
  //the AP coordinate wave name is then deduced from the w_data list and the "liberal" list of acronyms
 Variable top_n //how many to plot from the start of w_data list 
 String res_win //result prefix
 Variable AP_mode //if 0, then the centers of AP histogram bins will be used; if non-zero, then average AP coordinates will be used for X-axis  
 String axis_name //legend for X-axis
 String color
 
 String return_str=""
 
 Variable i, j, M=numpnts(acronym_lookup), match, N=ItemsInList(mouse_list, ";"), acro_n
 String path_to, s, acro, mouse, current, s1, s2
 
  
 for(i=0;i<top_n;i+=1) //over acronyms
  current=StringFromList(1,w_data[i],":")
  Wave dat=$(w_data[i])
  path_to="root:"+current+":"+StringFromList(2,w_data[i],":")+":AP_coordinates:"
  acro_n=-1
  do
   acro_n+=1
   match=1-stringmatch(NameOfWave(dat),CleanupName(acronym_lookup[acro_n],0)+"_*")
  while (match && acro_n<M-1)
   if (acro_n==M-1 && match)
     printf "Did not find a matching acronym for the data wave %s! Please check the list of acronyms. For now, aborted.\r", w_data[i]
     return ";"
   endif
  
  if (AP_mode)  
   Wave w_AP=$(path_to+"'"+acronym_lookup[acro_n]+"_AP_coord'")
  else
   Wave w_AP=$(path_to+"AP_histo_waves:'"+acronym_lookup[acro_n]+"_AP_coord'")
  endif
  
  if (numpnts(dat)!=numpnts(w_AP))
   printf "Warning! Waves %s and %s have different number of points!\r", NameOfWave(dat), NameOfWave(w_AP)
  endif

  acro=CleanupName(acronym_lookup[acro_n],0)

  DoWindow/K $(res_win+acro)
  //adding the average
  Display dat vs w_AP
  DoWindow/C $(res_win+acro)
  
  return_str=return_str+res_win+acro+";"
  
  //adding individual waves
    for(j=0; j<N; j+=1) //over mice
     mouse=StringFromList(j,mouse_list,";")
     Wave dat_jj=$(ReplaceString(current, w_data[i], mouse))
     if (WaveExists(dat_jj))
       s=GetWavesDataFolder(dat_jj, 1)
       Wave dat_j=$(s+"dropped_nan:"+NameOfWave(dat_jj))
       Wave w_AP_j=$(ReplaceString(current, path_to, mouse)+"'"+acronym_lookup[acro_n]+"_AP_coord'")
       AppendToGraph dat_j vs w_AP_j
     endif
    endfor //over mice
    
   ModifyGraph mode=4,marker=8,rgb=(26214,26214,26214)
   s=NameOfWave(dat)
   Execute "ModifyGraph mode("+s+")=4, marker("+s+")=19, lsize("+s+")=1.5, rgb("+s+")="+color
   //adding error bars
   

   s2=GetWavesDataFolder(dat, 1)
   s1=path_to+"AP_sem_waves:'"+acronym_lookup[acro_n]+"_AP_coord'"
   Execute "ErrorBars "+s+" XY,wave=("+s1+","+s1+"),wave=("+s2+"sem_waves:"+s+","+s2+"sem_waves:"+s+")"
   
 
 ModifyGraph btLen=4
 Label left axis_name//"density (mm\\S-2\\M)";DelayUpdate
 Label bottom "AP coordinate (mm)"
 
 SetDrawEnv xcoord= prel,ycoord= prel
 SetDrawEnv fstyle= 1,fsize= 9;DelayUpdate
 DrawText 0.753056234718826,0.111627906976744, acro
 
 endfor //over acronyms
  
  printf "//Plotted %d graphs.\n", top_n
  
  return return_str

End


Function do_average(mouse_list, acronyms, subfolder, output_acro_list, output_waves_list)
 String mouse_list
 Wave/T acronyms
 String subfolder
 String output_acro_list, output_waves_list
 
 Variable i, j, N=ItemsInList(mouse_list,";"), M=numpnts(acronyms), acro_cntr=0, buf_N
 String acro, mouse, wavs, wname
 
 DFREF saveDFR = GetDataFolderDFR()
 NewDataFolder/O/S sem_waves
 DFREF saveDFR_sem = GetDataFolderDFR()
 SetDataFolder saveDFR
 NewDataFolder/O/S N_waves
 DFREF saveDFR_N = GetDataFolderDFR()
 SetDataFolder saveDFR
 NewDataFolder/O/S dots_waves
 DFREF saveDFR_dots = GetDataFolderDFR()
 
 
 Make/O/N=(1) $"root:tmp_Ns"  
 Wave N_wav=$"root:tmp_Ns"
 
 Make/O/T/N=(0) collected_acros, collected_waves
   
 for(i=0;i<M;i+=1) //over acronyms
  acro=CleanupName(acronyms[i], 0)
  N_wav=0   
    
  for(j=0;j<N;j+=1) //over mice
   mouse=StringFromList(j, mouse_list, ";")
   SetDataFolder $("root:"+mouse+":"+subfolder)
   wavs=Wavelist(acro+"_*",";","")
   if (ItemsInList(wavs,";")>0)
     Wave dat=$(StringFromList(0,wavs,";"))
     if (N_wav[0]==0)
      wname=NameOfWave(dat)
      buf_N=numpnts(dat)
      Make/N=(buf_N)/O/D $"root:tmp_averaging",$"root:tmp_sem"
      Wave/D aver=$"root:tmp_averaging",sem=$"root:tmp_sem"
      Make/N=(buf_N)/O/D $"root:tmp_dots"
      Wave dots_wave=$"root:tmp_dots"
      dots_wave=dat[p]
      aver=dat[p]
      sem=dat[p]^2
      N_wav[0]=1
      InsertPoints acro_cntr, 1, collected_acros, collected_waves
      collected_acros[acro_cntr]=acronyms[i]
      collected_waves[acro_cntr]=wname
      acro_cntr+=1
      continue
     else
      buf_N=numpnts(dots_wave)
      InsertPoints buf_N, numpnts(dat), dots_wave
      buf_N=numpnts(dots_wave)-numpnts(dat)
      dots_wave=(p>=buf_N) ? dat[p-buf_N] : dots_wave[p]
      N_wav[0]+=1
      aver+=dat[p]
      sem+=dat[p]^2
     endif
   endif
  endfor //over mice
  
  if (N_wav[0]>0)
   aver=aver[p]/N_wav[0]
   sem=(N_wav[0]>1) ? sqrt(sem[p]/N_wav[0]-aver[p]^2)/sqrt(N_wav[0]-1) : nan
   
   SetDataFolder saveDFR_N
   Duplicate /O N_wav, $wname
   SetDataFolder saveDFR_sem
   Duplicate /O sem, $wname
   SetDataFolder saveDFR_dots
   Duplicate /O dots_wave, $wname
   SetDataFolder saveDFR
   Duplicate /O aver, $wname
  endif
  
  
  
 endfor //over acronyms
 
 Duplicate/O/T collected_acros $(output_acro_list)
 Duplicate/O/T collected_waves $(output_waves_list)
  
 KillWaves/Z aver, sem, N_wav, dots_wave, collected_acros, collected_waves
 
 SetDataFolder saveDFR
 
End



Function do_average_APtraces(mouse_list, acronyms, subfolder, [ignore_class_subfolder])
 String mouse_list
 Wave/T acronyms
 String subfolder
 Variable ignore_class_subfolder
 Variable i, j, k, L, N=ItemsInList(mouse_list,";"), M=numpnts(acronyms), N_waves, N_histo, min_histo, max_histo, histo_step,  cntr
 String acro, mouse, wavs, wname, AP_wname, w_list, AP_wavs, AP_w_list

 
 DFREF saveDFR = GetDataFolderDFR()
 SetDataFolder ::
 NewDataFolder/O/S AP_coordinates
 DFREF saveDFR_APs = GetDataFolderDFR()
 NewDataFolder/O/S AP_sem_waves
 DFREF saveDFR_AP_sem = GetDataFolderDFR()
 SetDataFolder saveDFR_APs
 NewDataFolder/O/S AP_histo_waves
 DFREF saveDFR_AP_histo = GetDataFolderDFR()
 
 SetDataFolder saveDFR
 NewDataFolder/O/S sem_waves
 DFREF saveDFR_sem = GetDataFolderDFR()
 SetDataFolder saveDFR
 NewDataFolder/O/S N_waves
 DFREF saveDFR_N = GetDataFolderDFR()
 SetDataFolder saveDFR
 

 Variable class_sub=1
 
 if (ParamIsDefault(ignore_class_subfolder)==0)
  class_sub=0 
 endif
 
   
 for(i=0;i<M;i+=1)
  acro=CleanupName(acronyms[i],0)
  
  //getting  arrangements done - for this need to screen the input data waves
    w_list=""
    AP_w_list=""
    for(j=0;j<N;j+=1) //over mice to identify the data waves and corresponding AP_coord waves
     mouse=StringFromList(j, mouse_list, ";")
     SetDataFolder $("root:"+mouse+":"+subfolder+":dropped_nan")
     wavs=Wavelist(acro+"_*",";","")
     if (ItemsInList(wavs,";")>0)
      if (strlen(w_list)>0)
       w_list=w_list+";"+GetWavesDataFolder($(StringFromList(0,wavs,";")),2)
       SetDataFolder $("root:"+mouse+":"+subfolder)
       if (class_sub)
        SetDataFolder ::
       endif
       SetDataFolder ::AP_coordinates
       AP_w_list=AP_w_list+";"+GetWavesDataFolder($(acronyms[i]+"_AP_coord"),2)
      else
       w_list=GetWavesDataFolder($(StringFromList(0,wavs,";")),2)
       SetDataFolder $("root:"+mouse+":"+subfolder)
       if (class_sub)
        SetDataFolder ::
       endif
       SetDataFolder ::AP_coordinates
       AP_w_list=GetWavesDataFolder($(acronyms[i]+"_AP_coord"),2)
      endif      
     endif
            
    endfor //over mice, identification cycle
     
     N_waves=ItemsInList(AP_w_list,";")
     if (N_waves==0)
       continue
     endif
     
     Make/O/N=(N_waves) max_AP, min_AP, N_AP
     
    for(j=0;j<N_waves;j+=1) //over identified AP_coord waves
     Wave AP_wav=$(StringFromList(j,AP_w_list,";"))
     Wavestats/Q AP_wav
     max_AP[j]=V_max
     min_AP[j]=V_min
     N_AP[j]=V_npnts
    endfor//over identified AP_coord waves
    
    Wavestats/Q N_AP
    N_histo=max(V_max, 2)
    Wavestats/Q min_AP
    min_histo=V_min
    Wavestats/Q max_AP
    max_histo=V_max
    
    
   Make/O/N=(N_histo) $"root:tmp_histo"
   Make/O/N=(N_histo+1) $"root:tmp_histo_borders"
   Wave histo_AP=$"root:tmp_histo"
   Wave histo_AP_borders=$"root:tmp_histo_borders"
   histo_step=(max_histo-min_histo)/(N_histo-1)
   histo_AP=min_histo+p*histo_step
   histo_AP_borders=min_histo+histo_step*(p-0.5)
     
   Make/O/N=(N_histo)/D $"root:tmp_averaging",$"root:tmp_sem",$"root:tmp_AP_aver",$"root:tmp_AP_sem", $"root:tmp_Ns"  
   Wave/D aver=$"root:tmp_averaging",sem=$"root:tmp_sem",AP_sem=$"root:tmp_AP_sem",AP_aver=$"root:tmp_AP_aver", N_wav=$"root:tmp_Ns"  
   N_wav=0
   aver=0
   sem=0
   AP_aver=0
   AP_sem=0
  
      
  for(j=0;j<N_waves;j+=1) //over identified data from different mice
   
   Wave dat=$(StringFromList(j,w_list,";"))
   Wave dat_AP=$(StringFromList(j,AP_w_list,";"))
  
   if (j==0)
    wname=NameOfWave(dat)
    AP_wname=(acronyms[i]+"_AP_coord")
   endif
    
    L=numpnts(dat)
    
    for (k=0; k<L; k+=1) //cumulating data into histo across the AP points of a given data wave
     cntr=-1
     do
      cntr+=1
     while ((dat_AP[k]<=histo_AP_borders[cntr] || dat_AP[k]>histo_AP_borders[cntr+1]) && (dat_AP[k]!=histo_AP_borders[cntr] && dat_AP[k]!=histo_AP_borders[cntr+1]))
      aver[cntr]+=dat[k]
      sem[cntr]+=dat[k]^2
      AP_aver[cntr]+=dat_AP[k]
      AP_sem[cntr]+=dat_AP[k]^2
      N_wav[cntr]+=1
    endfor //cumulating data into histo across the AP points of a given data wave
   
  endfor //over identified data from different mice
  
     
   aver=(N_wav[p]>0) ? aver[p]/N_wav[p] : nan
   sem=(N_wav[p]>1) ? sqrt(sem[p]/N_wav[p]-aver[p]^2)/sqrt(N_wav[p]-1) : nan
   AP_aver=(N_wav[p]>0) ? AP_aver[p]/N_wav[p] : nan
   AP_sem=(N_wav[p]>1) ? sqrt(AP_sem[p]/N_wav[p]-AP_aver[p]^2)/sqrt(N_wav[p]-1) : nan
       

   SetDataFolder saveDFR_N
   Duplicate /O N_wav, $wname
   SetDataFolder saveDFR_AP_sem
   Duplicate /O AP_sem, $AP_wname
   SetDataFolder saveDFR_APs
   Duplicate /O AP_aver, $AP_wname
   SetDataFolder saveDFR_AP_histo
   Duplicate /O histo_AP, $AP_wname
   SetDataFolder saveDFR_sem
   Duplicate /O sem, $wname
   SetDataFolder saveDFR
   Duplicate /O aver, $wname
   
 endfor //over acronyms
  
 KillWaves/Z aver, sem, N_wav, AP_aver, AP_sem, histo_AP, histo_AP_borders, max_AP, min_AP, N_AP
 
 SetDataFolder saveDFR
 
End




Function Average_across_mice(mouse_list, class_name, acronyms, result)
//The function goes through the folders with individual mice and averages data waves according to the acronyms list
//As the output, it creates the same structure of folders as for individual mice, but containing the average data
// The data can be then plotted 
  String mouse_list// ; - separated list of folders containing individual mice
  String class_name //detection class name
  Wave/T acronyms //text wave with the list of acronyms as in atlas, to be processed
  String result //resulting folder name
  
  Variable i, N=ItemsInList(mouse_list,";"), M=numpnts(acronyms)
  
  String top_node=result, class_path=":"+class_name
  
  SetDataFolder $"root:"

  NewDataFolder/O/S $top_node
  NewDataFolder/O res
  
  NewDataFolder/O/S right
  
  NewDataFolder/O/S total_detections
  NewDataFolder/O/S $class_name
   do_average(mouse_list, acronyms, "right:total_detections"+class_path, "root:Dataset_acronyms:"+result+"_right_all_acronyms", "root:Dataset_acronyms:"+result+"_right_all_waves")
  
  SetDataFolder ::
  SetDataFolder ::
  NewDataFolder/O/S total_density
  NewDataFolder/O/S $class_name
   do_average(mouse_list, acronyms, "right:total_density"+class_path, "root:Dataset_acronyms:"+result+"_right_all_acronyms", "root:Dataset_acronyms:"+result+"_right_all_waves")
   
  SetDataFolder ::
  SetDataFolder ::
  NewDataFolder/O/S total_areas
   do_average(mouse_list, acronyms, "right:total_areas", "root:Dataset_acronyms:"+result+"_right_all_acronyms", "root:Dataset_acronyms:"+result+"_right_all_waves")
   
  SetDataFolder :: 
  NewDataFolder/O/S detections
  NewDataFolder/O/S $class_name
   do_average_APtraces(mouse_list, acronyms, "right:detections"+class_path)
  
  SetDataFolder ::
  SetDataFolder ::
  NewDataFolder/O/S density
  NewDataFolder/O/S $class_name
   do_average_APtraces(mouse_list, acronyms, "right:density"+class_path)
   
  SetDataFolder ::
  SetDataFolder ::
  NewDataFolder/O/S areas
   do_average_APtraces(mouse_list, acronyms, "right:areas", ignore_class_subfolder=1)
    
  
  
  
  SetDataFolder ::
  SetDataFolder ::
  NewDataFolder/O/S left
  
  NewDataFolder/O/S total_detections
  NewDataFolder/O/S $class_name
   do_average(mouse_list, acronyms, "left:total_detections"+class_path, "root:Dataset_acronyms:"+result+"_left_all_acronyms", "root:Dataset_acronyms:"+result+"_left_all_waves")
  
  SetDataFolder ::
  SetDataFolder ::
  NewDataFolder/O/S total_density
  NewDataFolder/O/S $class_name
   do_average(mouse_list, acronyms, "left:total_density"+class_path, "root:Dataset_acronyms:"+result+"_left_all_acronyms", "root:Dataset_acronyms:"+result+"_left_all_waves")
   
  SetDataFolder ::
  SetDataFolder ::
  NewDataFolder/O/S total_areas
   do_average(mouse_list, acronyms, "left:total_areas", "root:Dataset_acronyms:"+result+"_left_all_acronyms", "root:Dataset_acronyms:"+result+"_left_all_waves")
  
  SetDataFolder :: 
  NewDataFolder/O/S detections
  NewDataFolder/O/S $class_name
   do_average_APtraces(mouse_list, acronyms, "left:detections"+class_path)
  
  SetDataFolder ::
  SetDataFolder ::
  NewDataFolder/O/S density
  NewDataFolder/O/S $class_name
   do_average_APtraces(mouse_list, acronyms, "left:density"+class_path)
   
  SetDataFolder ::
  SetDataFolder ::
  NewDataFolder/O/S areas
   do_average_APtraces(mouse_list, acronyms, "left:areas", ignore_class_subfolder=1)
  
   
   SetDataFolder $"root:"


End







Window num_detections_FV6622() : Layout
	PauseUpdate; Silent 1		// building window...
	NewLayout/W=(20.25,137,508.5,627.5)
	if (IgorVersion() >= 7.00)
		LayoutPageAction size=(612,792),margins=(18,18,18,18)
	endif
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_HY_tot_detections
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_HY_AP_left_dets
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 HYPOTHALAMUS: numbers of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_HY_AP_right_dets
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_TH_tot_detections
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_TH_AP_left_dets
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 THALAMUS: numbers of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_TH_AP_right_dets
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_STR_tot_detections
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_STR_AP_left_dets
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 STRIATUM: numbers of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_STR_AP_right_dets
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_PAL_tot_detections
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_PAL_AP_left_dets
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 PALLIDUM: numbers of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_PAL_AP_right_dets
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_CTXsp_tot_detections
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_CTXsp_AP_left_dets
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 CORTICAL SUBPLATE: numbers of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_CTXsp_AP_right_dets
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_OLF_tot_detections
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_OLF_AP_left_dets
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 OLFACTORY SYSTEM: numbers of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_OLF_AP_right_dets
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_HPF_tot_detections
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_HPF_AP_left_dets
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 HIPPOCAMPAL FORMATION: numbers of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_HPF_AP_right_dets
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_CNU_tot_detections
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_CNU_AP_left_dets
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 CEREBRAL NUCLEI: numbers of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_CNU_AP_right_dets
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,27,570,507) Graph FV6622_Isocortex_tot_detections
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_Isocortex_AP_left_dets
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 Isocortex: numbers of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_Isocortex_AP_right_dets
	LayoutPageAction page= 3
EndMacro



Window density_detections_FV6622() : Layout
	PauseUpdate; Silent 1		// building window...
	NewLayout/W=(20.25,137,508.5,627.5)
	if (IgorVersion() >= 7.00)
		LayoutPageAction size=(612,792),margins=(18,18,18,18)
	endif
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_HY_total_density
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_HY_AP_left_dens
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 HYPOTHALAMUS: density of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_HY_AP_right_dens
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_TH_total_density
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_TH_AP_left_dens
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 THALAMUS: density of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_TH_AP_right_dens
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_STR_total_density
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_STR_AP_left_dens
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 STRIATUM: density of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_STR_AP_right_dens
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_PAL_total_density
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_PAL_AP_left_dens
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 PALLIDUM: density of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_PAL_AP_right_dens
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_CTXsp_total_density
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_CTXsp_AP_left_dens
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 CORTICAL SUBPLATE: density of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_CTXsp_AP_right_dens
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_OLF_total_density
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_OLF_AP_left_dens
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 OLFACTORY SYSTEM: density of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_OLF_AP_right_dens
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_HPF_total_density
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_HPF_AP_left_dens
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 HIPPOCAMPAL FORMATION: density of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_HPF_AP_right_dens
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,28,571,466) Graph FV6622_CNU_total_density
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_CNU_AP_left_dens
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 CEREBRAL NUCLEI: density of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_CNU_AP_right_dens
	LayoutPageAction appendPage
	AppendLayoutObject/F=0/T=1/R=(45,27,570,507) Graph FV6622_Isocortex_total_density
	AppendLayoutObject/F=0/T=1/R=(23,501,311,749) Graph FV6622_Isocortex_AP_left_dens
	TextBox/C/N=text0/F=0/B=1/A=LB/X=1.91/Y=96.43 "FV6622 Isocortex: density of detections"
	AppendLayoutObject/F=0/T=1/R=(290,506,593,755) Graph FV6622_Isocortex_AP_right_dens
	LayoutPageAction page= 3
EndMacro
