Search.setIndex({docnames:["00_get_started","01_intro_regions","02_intro_class_ReadGrid","03_intro_class_ReadMultiGrid","04_intro_class_GridData","05_intro_time_handling","api","api_testsuite","config_files","dev01_collocation_multipoints","index","notebooks","readme"],envversion:53,filenames:["00_get_started.rst","01_intro_regions.rst","02_intro_class_ReadGrid.rst","03_intro_class_ReadMultiGrid.rst","04_intro_class_GridData.rst","05_intro_time_handling.rst","api.rst","api_testsuite.rst","config_files.rst","dev01_collocation_multipoints.rst","index.rst","notebooks.rst","readme.rst"],objects:{"pyaerocom.griddata":{GridData:[6,1,1,""]},"pyaerocom.griddata.GridData":{area_weighted_mean:[6,2,1,""],area_weights:[6,3,1,""],calc_area_weights:[6,2,1,""],check_and_regrid_lons:[6,2,1,""],collapsed:[6,2,1,""],crop:[6,2,1,""],grid:[6,3,1,""],has_data:[6,3,1,""],interpolate:[6,2,1,""],intersection:[6,2,1,""],is_cube:[6,3,1,""],latitude:[6,3,1,""],load_input:[6,2,1,""],longitude:[6,3,1,""],name:[6,3,1,""],plot_settings:[6,3,1,""],quickplot_map:[6,2,1,""],shape:[6,3,1,""],short_str:[6,2,1,""],start_time:[6,3,1,""],stop_time:[6,3,1,""],suppl_info:[6,3,1,""],time:[6,3,1,""],time_stamps:[6,2,1,""],var_name:[6,3,1,""]},"pyaerocom.helpers":{cftime_to_datetime64:[6,4,1,""],get_constraint:[6,4,1,""],get_lat_constraint:[6,4,1,""],get_lon_constraint:[6,4,1,""],get_lon_constraint_buggy:[6,4,1,""],get_time_constraint:[6,4,1,""],str_to_iris:[6,4,1,""]},"pyaerocom.io":{fileconventions:[6,0,0,"-"],helpers:[6,0,0,"-"],readgrid:[6,0,0,"-"],readobsdata:[6,0,0,"-"],testfiles:[6,0,0,"-"]},"pyaerocom.io.fileconventions":{FileConventionRead:[6,1,1,""]},"pyaerocom.io.fileconventions.FileConventionRead":{check_validity:[6,2,1,""],file_sep:[6,3,1,""],from_dict:[6,2,1,""],from_file:[6,2,1,""],get_info_from_file:[6,2,1,""],import_default:[6,2,1,""],name:[6,3,1,""],string_mask:[6,2,1,""],to_dict:[6,2,1,""],ts_pos:[6,3,1,""],var_pos:[6,3,1,""],year_pos:[6,3,1,""]},"pyaerocom.io.helpers":{check_time_coord:[6,4,1,""],correct_time_coord:[6,4,1,""],get_all_names:[6,4,1,""],search_names:[6,4,1,""]},"pyaerocom.io.readgrid":{ReadGrid:[6,1,1,""],ReadMultiGrid:[6,1,1,""]},"pyaerocom.io.readgrid.ReadGrid":{data:[6,3,1,""],file_convention:[6,3,1,""],files:[6,3,1,""],from_files:[6,3,1,""],model_dir:[6,3,1,""],name:[6,3,1,""],read_all_vars:[6,2,1,""],read_var:[6,2,1,""],search_all_files:[6,2,1,""],search_model_dir:[6,2,1,""],start_time:[6,3,1,""],stop_time:[6,3,1,""],update:[6,2,1,""],vars:[6,3,1,""],years_to_load:[6,3,1,""]},"pyaerocom.io.readgrid.ReadMultiGrid":{init_results:[6,2,1,""],names:[6,3,1,""],read:[6,2,1,""],results:[6,3,1,""],search_all_files:[6,2,1,""],search_model_dirs:[6,2,1,""],start_time:[6,3,1,""],stop_time:[6,3,1,""]},"pyaerocom.io.readobsdata":{ReadObsData:[6,1,1,""]},"pyaerocom.io.readobsdata.ReadObsData":{CheckObsnetworkName:[6,2,1,""],GetDataDir:[6,2,1,""],GetDataRevision:[6,2,1,""],SUPPORTED_DATASETS:[6,3,1,""],code_lat_lon_in_float:[6,2,1,""],decode_lat_lon_from_float:[6,2,1,""],latitude:[6,3,1,""],longitude:[6,3,1,""],read_daily:[6,2,1,""],station_name:[6,3,1,""],time:[6,3,1,""],to_timeseries:[6,2,1,""]},"pyaerocom.io.testfiles":{get:[6,4,1,""]},"pyaerocom.mathutils":{exponent:[6,4,1,""],range_magnitude:[6,4,1,""]},"pyaerocom.obsdata":{ObsData:[6,1,1,""],ProfileData:[6,1,1,""],StationData:[6,1,1,""]},"pyaerocom.obsdata.ObsData":{import_data:[6,2,1,""],latitude:[6,2,1,""],longitude:[6,2,1,""],time_stamps:[6,2,1,""]},"pyaerocom.obsdata.ProfileData":{import_data:[6,2,1,""],latitude:[6,2,1,""],longitude:[6,2,1,""],time_stamps:[6,3,1,""]},"pyaerocom.plot":{config:[6,0,0,"-"],mapping:[6,0,0,"-"]},"pyaerocom.plot.config":{ColorTheme:[6,1,1,""],MapPlotSettings:[6,1,1,""],get_color_theme:[6,4,1,""]},"pyaerocom.plot.config.ColorTheme":{cmap_map:[6,3,1,""],color_coastline:[6,3,1,""],from_dict:[6,2,1,""],load_default:[6,2,1,""],name:[6,3,1,""],to_dict:[6,2,1,""]},"pyaerocom.plot.config.MapPlotSettings":{load_input:[6,2,1,""]},"pyaerocom.plot.mapping":{plot_map:[6,4,1,""],plot_map_OLD:[6,4,1,""],plot_map_aerocom:[6,4,1,""]},"pyaerocom.region":{Region:[6,1,1,""],get_all_default_region_ids:[6,4,1,""],get_all_default_regions:[6,4,1,""]},"pyaerocom.region.Region":{import_default:[6,2,1,""],lat_range:[6,3,1,""],lat_range_plot:[6,3,1,""],lon_range:[6,3,1,""],lon_range_plot:[6,3,1,""],name:[6,3,1,""]},"pyaerocom.test":{test_mathutils:[7,0,0,"-"]},"pyaerocom.test.test_mathutils":{test_exponent:[7,4,1,""]},pyaerocom:{griddata:[6,0,0,"-"],helpers:[6,0,0,"-"],mathutils:[6,0,0,"-"],obsdata:[6,0,0,"-"],region:[6,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","attribute","Python attribute"],"4":["py","function","Python function"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:attribute","4":"py:function"},terms:{"01t00":[2,3,4,5,6,11],"02t00":[3,11],"0_nrt":[0,8,11],"0allpoint":8,"0x7f1236279320":[0,11],"100m":[5,11],"10s":9,"11min":9,"11t00":[3,5,6,11],"1degre":9,"1e6":6,"1min":9,"23s":9,"24s":9,"29feb2004":[2,11],"29feb2007":[2,11],"30min":9,"31t00":[4,6,11],"33min":9,"33s":9,"3hourli":[0,2,6,11],"3min":9,"3rd":12,"44min":9,"46s":9,"48s":9,"550nm":[2,3,4,11],"abstract":6,"case":[2,4,5,6,11],"class":[0,1,5,6,9,10],"const":[0,6,11],"default":[6,10],"final":[2,5,11],"float":6,"function":[2,4,5,6,9,11],"import":[0,1,2,3,4,5,6,8,9,11],"int":6,"long":9,"new":[0,5,6,11],"public":12,"return":[2,4,5,6,9,11],"short":6,"true":[0,2,3,4,6,11],"try":[4,5,6,11],"var":[2,6,8,11],"while":[0,5,9,11],And:[5,9,11],But:[5,11],For:[4,5,6,7,8,9,11],IDs:[3,6,8,11],That:[5,11],The:[0,2,3,4,5,6,7,8,9,11,12],Then:[0,11],These:[2,3,4,11],Use:[0,6,11],Uses:6,Using:9,Will:6,__dir__:[0,6,11],__version__:[0,11],_cach:[0,11],_cftime:[5,11],_config_ini:[0,11],_datepars:[5,11],_init_testdata_default:[0,1,6,9,11],_netcdf4:[5,11],_netcdftim:[5,11],_str_to_iri:6,aatsr:[5,11,12],aatsr_su_v4:[3,4,5,6,8,11],abl:[0,11],about:[2,3,4,5,6,8,9,11],abov:[0,2,4,5,11],abs550aer:[3,6,11],abs:9,abstractmethod:6,accelar:[5,11],accept:[5,6,11],access:[2,3,5,9,10,11,12],accmip:[3,8,11],accord:[2,5,6,11],actual:[0,2,5,11],adapt:[4,5,11],add_zero:6,addit:[6,9],advanc:12,aerocom1:[0,3,4,8,11],aerocom2:[2,3,6,8,11],aerocom3:[6,8],aerocom3_cam5:[3,6,11],aerocom:[0,2,3,4,6,8,9,10,12],aerocom_obsdata:8,aeronet:[8,9,12],aeronet_inv_v2l15_all_point:8,aeronet_inv_v2l15_all_points_nam:[0,11],aeronet_inv_v2l15_daili:8,aeronet_inv_v2l15_daily_nam:[0,11],aeronet_inv_v2l2_all_point:8,aeronet_inv_v2l2_all_points_nam:[0,11],aeronet_inv_v2l2_daili:8,aeronet_inv_v2l2_daily_nam:[0,11],aeronet_sun_v2l15_aod_all_point:8,aeronet_sun_v2l15_aod_all_points_nam:[0,11],aeronet_sun_v2l15_aod_daili:8,aeronet_sun_v2l15_aod_daily_nam:[0,11],aeronet_sun_v2l2_aod_all_point:8,aeronet_sun_v2l2_aod_all_points_nam:[0,11],aeronet_sun_v2l2_aod_daili:8,aeronet_sun_v2l2_aod_daily_nam:[0,11],aeronet_sun_v2l2_sda_all_point:8,aeronet_sun_v2l2_sda_all_points_nam:[0,11],aeronet_sun_v2l2_sda_daili:8,aeronet_sun_v2l2_sda_daily_nam:[0,11],aeronet_sun_v3l15_aod_all_point:8,aeronet_sun_v3l15_aod_all_points_nam:[0,11],aeronet_sun_v3l15_aod_daili:8,aeronet_sun_v3l15_aod_daily_nam:[0,11],aeronet_sun_v3l2_aod_all_point:8,aeronet_sun_v3l2_aod_all_points_nam:[0,11],aeronet_sun_v3l2_aod_daili:8,aeronet_sun_v3l2_aod_daily_nam:[0,11],aeronet_sun_v3l2_sda_all_point:8,aeronet_sun_v3l2_sda_all_points_nam:[0,11],aeronet_sun_v3l2_sda_daili:8,aeronet_sun_v3l2_sda_daily_nam:[0,11],aeronetinvv2lev1:[0,8,11],aeronetinvv2lev2:[0,8,11],aeronetraw2:8,aeronetsdav2lev2:[0,8,11],aeronetsdav3lev2:[0,8,11],aeronetsun2:8,aeronetsun_2:[0,8,11],aeronetsunnrt:8,aeronetsunv2lev1:[0,8,11],aeronetsunv2lev2:[0,6,8,11],aeronetsunv3lev1:[0,8,11],aeronetsunv3lev2:[0,8,11],aerosol:[2,3,4,5,8,11,12],after:[3,6,9,11],again:[2,9,11],ages:9,aggreg:6,algorithm:6,alias:6,all:[0,1,2,3,5,6,8,9,11],all_fil:6,allow:[2,4,6,11],along:[3,6,11],alreadi:6,also:[3,4,5,6,8,11],america:6,anaconda:12,analys:[0,5,11,12],analysi:[0,4,6,9,10,11],ang4487aer:[2,3,6,11],ani:[5,6,11],answer:[5,11],aod:[2,11],api:10,appar:6,append:[4,6,11],appli:[2,3,6,9,10],applic:6,approxim:9,arang:9,arbitrari:[3,6,11],arbitrarili:[3,11],area:[2,6,11],area_weight:6,area_weighted_mean:[2,6,11],arg:6,argmin:9,argument:6,around:[5,6,9,11],arrai:[3,5,6,9,11],art:12,asarrai:[5,11],asia:[1,8,11],ask:12,aspect:6,assembl:12,assert:6,assert_array_equ:9,assum:6,atmosphere_optical_thickness_due_to_ambient_aerosol:[3,11],attempt:[2,3,11],attr:[4,11],attribut:[2,3,4,5,6,11],attributeerror:[2,3,11],australia:[1,6,8,11],automat:[2,4,5,6,11],avail:[2,3,4,6,11],averag:[2,5,11],avhhr:12,avignon:6,avoid:[5,11],awar:6,axes:6,axi:[2,3,6,11],base:[0,2,3,4,5,6,11,12],based:[5,6,11],basedir:8,basenam:[3,6,11],basic:[4,5,11],becaus:[0,8,11,12],been:[6,12],befor:[0,3,6,9,11],being:[0,6,11],belong:[3,6,11],below:[5,6,11],bin:12,blaaa:[4,11],blob:[5,11],bool:6,boost:[5,11],border:6,both:[3,5,9,11],brief:10,briefli:[2,11],bunch:[3,11],c_over:[4,6,11],c_under:6,calc_area_weight:6,calcul:6,calendar:[5,6,11],call:[0,2,5,6,11],cam5:[3,6,11],cam:[1,2,11],can:[0,2,3,4,5,6,8,9,11,12],cannot:[5,6,11,12],care:[2,11],cartopi:12,categoris:[4,11],cbar_level:6,cbar_tick:6,cci:[3,4,8,11],cci_aerosol_phase1:8,cci_aerosol_phase2:[3,4,8,11],cell:[1,2,3,4,5,11],certain:6,cf_unit:[5,11],cfg:[0,11],cftime:[5,6,11],cftime_to_datetime64:[5,6,11],cfu_str:[5,11],cfunit:[5,6,11],cfunit_str:[5,6,11],cfunit_to_datetime64:6,cgi:12,chang:[0,11],check:[0,2,6,11],check_and_regrid_lon:6,check_nc_fil:6,check_time_coord:6,check_valid:6,checkobsnetworknam:6,china:[1,8,11],choic:[0,11],choos:[0,6,11],circumv:[5,11],citi:[2,11],clean:6,climat:12,clone:[0,11,12],cmap_map:6,coastlin:6,code:[0,4,6,7,11],code_lat_lon_in_float:6,collaps:6,collapse_scalar:6,colloc:9,color:10,color_coastlin:6,color_norm:6,color_them:6,colorbar:[6,8],colormap:6,colorthem:6,colour:6,com:[0,5,11],combin:[5,6,11],come:[6,10],common:[6,12],compar:[0,5,11,12],comparison:12,compat:12,complet:[4,6,7,11],complic:[5,11],compris:8,comput:[2,6,11],concaten:[2,3,6,11],concentr:12,conf:8,conf_aero2:6,conf_aero3:6,config:[0,6,11],config_fil:[0,11],configur:[0,6,10,11],conform:[5,11],consider:[5,9,11],consol:[0,11],constraint:6,constraintmismatcherror:[4,11],consum:8,contain:[0,2,3,4,5,6,8,10,11,12],content:[6,10],control:[0,6,11],conv:6,conveni:6,convent:[2,3,4,5,10,11],convers:[3,5,6,11],convert:[4,6],coord:[3,4,5,6,9,11],coordin:[2,4,6,9,11],corner:6,correct:[2,3,6,11],correct_time_coord:6,correctli:[0,11],correspond:[3,5,6,8,11],could:[2,3,6,11],cover:6,cpu:9,creat:[0,1,2,3,4,6,8,11],crop:[0,2,3,4,6,10],crop_around:9,cross:6,ctrl2016:6,cube:[2,3,4,6,9,10],cube_aatsr:[5,11],cube_crop:6,cube_ecmwf:[5,11],cubelist:6,current:[0,3,4,6,9,11],custom:9,dai:[2,3,5,6,11],daili:[0,2,3,4,6,8,11],dark:6,dat_crop:[3,11],data1:9,data:[0,4,8,9,10,12],data_aatsr:[5,11],data_bc:[4,11],data_crop:6,data_ecmwf:[5,11],data_leipzig:[2,11],data_set_nam:6,data_set_to_read:6,data_so4:[4,11],databas:[0,2,3,4,6,8,11],datapoint:[5,11],dataset:[1,6,11],datatyp:10,date:[3,5,6,11],datetim:[5,6,11],datetime64:[5,6,11],datetimejulian:[5,11],day_unit:[5,11],declar:6,decod:6,decode_lat_lon_from_float:6,decor:6,decreas:[5,11],deeper:[5,11],def:[5,9,11],defin:[0,1,2,3,4,5,6,8,11],definit:[0,1,3,5,6,8,9,10],degre:[5,11],delimit:6,deltaz3d:[3,6,11],densiti:[2,4,5,11],depend:[0,5,11],depth:[2,3,4,11],design:[5,6,11],desir:6,detail:[1,2,5,6,11],detect:[2,3,6,11],determin:[6,8,9],dev1:[0,11],dev:[5,11],develop:[0,4,6,7,9,11,12],dict:[0,6,11],dictionari:[2,3,4,6,11],did:[2,4,11],differ:[2,3,5,6,8,11],dig:10,dimcoord:[4,5,6,11],dimens:[2,3,4,6,11],dir:[2,3,8,11],direcori:[3,11],direct:[4,11,12],directli:[0,4,5,6,9,11],directori:[0,2,3,6,10,11],discret:6,discrete_norm:6,discuss:12,displai:[5,6,11],doc:6,docstr:[6,7],document:[6,7,10],doe:[0,2,6,9,10],doing:9,domain:10,done:[3,5,6,9,11],donotcach:[0,11],donotcachefil:[0,11],down:6,download:[0,11,12],dramat:9,dtype:[5,6,11],due:[5,11],dummi:6,dure:[5,11],dust:[4,11],e6e6e6:6,each:[0,2,3,5,6,8,11],earlinet:[0,6,8,11],earlinet_nam:[0,11],easier:[5,11],easiest:[5,11],easili:8,ebas_multicolumn:8,ebas_multicolumn_nam:[0,11],ebasmc:[0,8,11],ebasmulticolumn:8,eclips:[3,8,11],ecmwf:[0,1,2,3,4,5,8,11],ecmwf_cams_rean:[2,6,11],ecmwf_osuit:[4,5,6,8,11],ecmwf_osuite_nrt:[4,11],ecmwf_osuite_nrt_test:[4,8,11],ectract:6,edit:[0,11],eea:8,eea_aqerep:8,eea_nam:[0,11],eeaaqerep:[0,8,11],either:[4,5,6,11,12],element:6,elif:[5,11],els:[5,6,11],emep:[3,8,11],emep_copernicu:[3,8,11],emep_glob:[3,8,11],emep_svn_test:[3,8,11],emiss:12,emphazis:[5,11],empti:9,encod:[5,11],encrypt:[2,5,6,11],end:[4,5,6,11],end_dat:6,enhanc:[5,6,11],enough:[5,11],ensur:[5,6,11],environ:10,epoch:[5,6,11],equal:[6,9],error:[2,3,4,5,6,11],establish:12,etc:10,europ:[1,6,8,11],even:[5,9,11],everyth:[0,2,6,9,11],exampl:[4,6,10],example_fil:6,exce:6,exceed:6,except:[4,5,11],exist:[0,4,6,11],expand:6,expect:[0,2,11],explain:[0,11],expon:[6,7],extend:[3,4,6,11],extern:[0,11],extract:[2,3,5,6,8,11,12],fail:[2,3,11],fair:[5,11],fals:[0,6,11],far:[4,6,7,8,9,11],fast:[5,9,11],faster:[5,6,9,11],featur:[2,5,10],few:9,field:12,fig1:[4,11],fig2:[4,11],fig:[0,1,3,4,6,11],figh:6,figsiz:[2,11],figur:6,file:[0,1,2,3,4,5,10,11],file_convent:[6,8],file_path:6,file_sep:[6,8],fileconvent:6,fileconventionread:[6,8],filenam:[2,4,6,11],filepath:[4,11],fill:6,filter:[4,11],filterwarn:[3,4,11],find:[2,11,12],finish:6,first:[2,3,5,6,9,11],five:[2,11],fix:6,fix_aspect:[4,6,11],flexibl:[0,2,6,11],fname:6,focu:[0,11],folder:[8,12],follow:[0,1,2,3,4,5,6,8,9,11],form:6,format:[5,11],former:[5,6,9,11],found:[2,3,4,6,11,12],fpath:[4,11],fpath_aatsr:[5,11],fpath_ecmwf:[5,11],freez:[0,11],freq:6,frequenc:[5,6,11],from:[0,1,2,4,5,6,7,9,10,12],from_dict:6,from_fil:6,fulli:6,func:[5,11],fundament:[4,11],further:6,furthermor:[5,11],futur:12,gauss_sigma:[2,11],gaussian_filter1d:[2,11],gcosabscrit:[0,11],gcospercentcrit:[0,11],gener:10,geoax:6,germani:[2,11],get:[4,5,6,9,10],get_all_default_region:6,get_all_default_region_id:[1,6,11],get_all_name:6,get_closest_index:9,get_cmap_levels_auto:6,get_color_them:6,get_constraint:6,get_info_from_fil:6,get_lat_constraint:6,get_lon_constraint:6,get_lon_constraint_buggi:6,get_model_fil:6,get_time_constraint:[2,3,6,11],getdatadir:6,getdatarevis:6,git:[0,11],github:[0,5,11,12],give:[0,9,11,12],given:[2,6,11],gliss:8,glob_mean:[2,11],global:[2,5,6,10,12],globe:9,got:[2,9,11],gpl:12,gregorian:[5,6,11],gregorian_bas:[5,11],grid:[2,3,4,5,11],griddata:[0,1,3,5,6,9,10],griesfel:8,handl:[0,1,10],has:[0,2,3,6,11,12],has_data:6,have:[0,2,3,4,5,6,9,11,12],height:6,held:12,helper:[5,9,10,11],here:[0,2,3,5,6,8,11,12],hich:[1,11],high:6,hint:[4,11],histori:[4,11],history_of_appended_fil:[4,11],hold:[5,11],home:[0,11],hopefulli:6,hourli:[0,2,6,11],how:[0,1,6,10],howev:[5,6,9,11],hr_unit:[5,11],htap:[3,8,11],html:6,http:[0,5,6,11,12],humidity3d:[3,6,11],identifi:6,idl:[9,12],idx_lat:9,idx_lon:9,ignor:[2,3,4,6,11],iii:[3,8,11],illustr:[5,11],imag:[0,11],impact:12,implement:[2,5,6,11],impli:6,import_data:6,import_default:6,importantli:6,improv:[5,11],inca:[3,8,11],inch:6,includ:[2,6,8,9,11,12],incomplet:12,increas:[5,11],ind2:[0,8,11],ind3:[0,8,11],index:[2,5,6,9,10,11],india:[1,6,8,11],indic:[5,6,9,11],individu:6,info:[0,6,11],info_dict:6,inform:[1,2,3,4,5,6,8,11],inherit:9,ini:[0,1,6,8,11],iniat:[0,11],init:6,init_result:6,initi:[3,6,11,12],initialis:[2,4,11],input:[3,4,5,9,10,11],insert:6,instal:[6,10],instanc:[0,1,2,3,4,5,6,8,9,11],instanti:6,instead:6,interact:12,interest:[9,12],interfac:[1,2,3,6,12],interg:6,intern:[5,11,12],interpol:[2,6,11],interpret:[5,6,11],intersect:[6,9],interv:[3,6,9,11],intial:[0,11],introduc:[0,1,2,3,5,10],introduct:[0,10],invalid:[0,2,3,4,5,6,11],invalid_unit:[4,11],inventori:12,invers:8,ioconfig:[0,11],ioerror:6,iri:[2,3,4,6,10,12],irrelev:6,is_cub:6,isinst:[5,11],issu:[2,5,11],item:[3,4,6,11],iter:[5,6,10],itp:6,its:[8,12],jan:8,jona:8,jonasg:[0,11],julian:[5,11],jupyt:10,just:[5,6,9,11],keep:[5,11],kei:[4,6,11],kept:6,keyword:6,kwarg:6,label:[2,11],larg:[2,3,6,11,12],last:[3,6,11],lat:[6,9],lat_leipzig:[2,11],lat_rang:[3,4,6,8,9,11],lat_range_plot:[6,8],lat_tick:8,later:[0,1,2,3,11],latitud:[1,2,3,4,6,8,9,11],latr:9,latter:[0,2,4,5,6,11],lead:[5,11],leap:[2,11],least:6,leav:[0,6,11],left:6,legend:[2,11],leipzig:[2,11],len:[5,9,11],let:[0,3,4,5,9,11],level:[6,8,10],librari:[5,6,11,12],licens:12,light:6,like:[3,5,6,11],linear:9,linspac:9,list:[0,3,5,6,11,12],littl:[5,9,11],little_less_lat:9,little_less_lon:9,loaction:6,load:[0,2,3,4,6,8,9,10],load_config:[0,11],load_cub:6,load_default:6,load_input:6,load_model_data:9,local:[0,11],locat:[0,6,9,11],log:6,log_scal:6,logarithm:6,lon:[6,9],lon_leipzig:[2,11],lon_rang:[3,4,6,8,9,11],lon_range_plot:[6,8],lon_tick:8,longitud:[0,1,2,3,5,6,8,9,10],longitudeconstrainterror:6,lonr:9,look:[2,3,4,5,11],loop:[5,9,11],lost:6,lot:9,low:[6,10],lower:[5,6,11],lustr:[0,2,3,4,8,11],machin:[0,11],made:12,magnitud:6,mai:[4,5,6,11,12],main:6,make:[0,3,6,9,11,12],manag:12,mani:[3,11],map:[1,2,3,10,11],map_axes_aspect:6,map_c_ov:8,map_cbar_level:8,map_cbar_tick:8,map_vmax:8,map_vmin:8,mapplotset:6,mar:[4,11],mask:6,master:[5,11],match:[2,3,6,11],match_str_aero2:6,match_str_aero3:6,mathemat:10,mathutil:6,matplotlib:[6,12],max:[4,6,11],max_year:[0,11],maximum:6,mean:[2,3,4,5,6,11],memori:9,merg:[0,2,11],meridian:6,meridian_centr:6,messag:[2,3,4,11],met:[8,12],meta:[2,3,6,11],meta_info:6,metadata:[2,3,6,11],method:[0,2,3,4,5,7,9,10,11],metno:[0,11],microsec_unit:[5,11],microsecond:[5,11],might:[0,11],millisec_unit:[5,11],min:[4,6,11],min_unit:[5,11],min_year:[0,11],mind:[5,11],miner:[3,11],minyear:[5,11],misr:12,mod:6,mode:[0,11,12],model:[0,4,5,8,9,10,12],model_data:[3,11],model_dir:[3,6,11],name:[2,3,4,5,6,8,11],modelbasedir:[0,11],modeldir:[0,11],modelfold:8,modelimportresult:6,modi:12,modifi:6,modul:[5,6,7,10,11],monthli:[0,2,6,11],more:[0,1,2,5,6,9,10,12],more_lat:9,more_lon:9,most:[4,5,6,11],mostli:[4,8,11],much:[4,11],multipl:[2,4,6,9,10],must:[3,6,11],myconfig:[0,11],nafrica:[1,8,11],name:[0,1,2,4,5,8,10,11],nameerror:6,namerica:[1,8,11],nan:[2,3,11],navig:[0,11],ncalendar:[5,11],nck:[4,11],nco:[4,11],nco_openmp_thread_numb:[4,11],ncurrent:[3,11],ndarrai:[5,6,11],ndimag:[2,11],nearest:[6,9],necess:[5,11],need:[0,6,11],neighbour:9,neirest:9,netcdf4:[5,11],netcdf:[2,4,5,6,11],netcdftim:[5,11],network:[6,8,9],new_val:6,nfirst:[5,11],nice:[0,3,11],nomin:[3,11],nomodelnam:[0,11],non:[5,6,11,12],none:[0,5,6,8,11],nontheless:[5,11],noresm_svn_test:[3,8,11],norm:6,normal:[0,11],north:6,norwai:8,notabl:[5,11],note:[2,5,6,8,9,11],notebook:[0,1,2,4,5,9,10],now:[0,1,2,3,5,9,11],nreceiv:[3,11],nstart:[3,11],nthe:[2,11],ntime:[5,11],num2dat:[5,6,11],num:6,number:[3,5,6,9,11,12],numer:[5,6,11],numpi:[5,6,7,11,12],obj:[5,6,11],object:[0,2,3,4,5,6,11],obs:[6,8],obs_network_nam:6,obsbasedir:[0,11],obsconfig:[0,11],obsdata:6,obsdatacachedir:[0,11],observ:[0,4,8,9,10,11,12],obsfold:8,obsnam:8,obsnet_non:[0,8,11],obsonlymodelnam:8,obsstartyear:8,obviou:[5,11],od440aer:[2,3,6,11],od500aer:6,od550aer3d:[3,6,11],od550aer:[2,3,4,5,6,8,11],od550aerh2o:[3,6,11],od550bc:[2,4,6,11],od550dryaer:[3,6,11],od550dust:[2,3,4,6,11],od550erra:[3,11],od550gt1aer:[3,11],od550lt1aer:[3,6,11],od550oa:[2,4,11],od550so4:[2,4,6,11],od550ss:[2,11],od865aer:[2,11],od870aer:[3,6,11],ofcd:6,offici:10,offset:6,okai:[5,11],on_load:[0,6,11],one:[0,2,3,5,6,9,11],onelin:[0,11],ones:[0,11],onli:[0,2,4,5,6,8,9,11],onload:[0,6,11],onto:6,open:12,optic:[2,3,4,5,11],optimis:6,optimum:[5,11],option:[0,6,8],order:[2,5,6,11],ordereddict:6,org:6,orig:[4,11],origin:[0,4,11],oserror:[2,3,11],oslo_ap3:6,oslo_ctrl2016:[3,6,11],oslo_ctrl2016_od550aer_column_2010_daili:[3,11],oslo_ctrl2016_od550dust_column_2010_daili:[3,11],osuit:[1,4,11],other:[4,8],otherwis:[2,3,11],our:[2,11],out:[0,4,11],out_basedir:[0,11],outperform:9,output:[2,10,11],over:[1,5,6,9,10],overview:[2,11],overwrit:6,overwritten:6,own:[4,6,11],packag:[0,2,3,5,6,10,11,12],page:10,pair:[6,8],panda:[2,5,6,11,12],paramet:[4,5,6,8,11],pars:[4,11],parti:[5,11,12],particular:[5,11],particularli:[5,6,11],pass:[4,6,11],path:[0,2,3,4,6,10,11],pd_od550aer_column_2010_monthli:6,pdseri:6,pdseriesmonthli:6,per:[5,11],perform:[5,6,11],period:[2,6,11],phase:[0,3,8,11,12],pick:[4,11],pleas:[0,5,6,7,11],plot:[0,1,2,3,4,8,10,11,12],plot_dir:[0,11],plot_map:6,plot_map_aerocom:6,plot_map_old:6,plot_set:6,point:[2,3,4,5,6,11,12],pointer:[4,11],polder:12,posit:[2,6,11],post:10,predefin:6,preindustri:12,preload:[4,6,11],previou:[5,11],previous:[3,11],print:[0,1,2,3,4,5,6,8,9,11],problem:[2,5,11],process:[3,11,12],produc:12,profil:6,profiledata:6,program:6,progress:12,proj_dir:6,project:[0,2,3,4,6,8,10,11,12],proleptic_gregorian:[5,11],prone:[5,11],properli:[2,6,11],protocol:12,provid:[2,3,5,6,11,12],pseudo:6,pure:[5,11],put:[2,11],pyaeorocom:[1,6,8,11],pyaerocom:[0,1,2,3,4,6,7,8,9,12],pyaerocom_tconvers:[5,11],pydata:6,python3:[0,11,12],python:[0,5,10,11,12],pyx:[5,11],quick:[4,6,11],quickplot:[4,6,11],quickplot_map:[0,1,3,4,6,11],quit:[5,9,11],rais:[4,5,6,11],rang:[0,1,2,6,8,9,11],range_magnitud:6,rather:[5,6,11],read:[0,10],read_aatsr:[3,11],read_all_var:6,read_cam:6,read_daili:6,read_var:[2,6,11],readabl:[4,11],readgrid:[0,3,6,10],readi:[0,5,9,11],readmultigrid:[2,6,10],readobsdata:6,reanalysi:[2,11],reason:9,recent:6,recommend:[6,12],redefin:[2,11],reduc:[5,11],region:[0,9,10],regular:12,reimplement:[4,6,11],rel:[5,6,11],relat:[1,6,11,12],relev:[0,8,11],reload:[0,9,11],remain:6,remark:10,renam:[2,3,4,6,8,11],replac:12,repo:12,repositori:[0,11,12],repr:[3,4,5,11],repres:[5,6,11],represent:[2,3,4,10],requir:[2,4,5,6,10],res:[5,11],resampl:6,resid:6,resolut:[0,2,3,5,6,9,11],result:[1,2,3,5,6,9,11,12],result_dict:[3,11],reveal:9,revis:[0,6,11],revision_fil:[0,11],right:[6,9],risk:[5,11],roll:[0,1,2,3,4,5,6,9,11],root:[0,11],routin:10,run:[0,5,9,11],s0_case1:9,s0_case2:9,s0_case3:9,s_glob:[2,11],s_leipzig:[2,11],safrica:[1,8,11],same:[0,2,5,6,11],samerica:[0,1,8,11],sampl:6,sample_point:[6,9],satellit:[3,8,11],saw:[5,11],scalar:6,scale:6,scheme:6,scientist:12,scipi:[2,11],sda:8,search:[2,3,6,8,10,11],search_all_fil:6,search_model_dir:6,search_name:6,seawif:12,sec_unit:[5,11],second:6,section:[2,6,11],see:[0,2,4,5,6,11],self:6,sens:[5,9,11],seper:6,sequenc:6,seri:[2,5,6,9,11],server:[0,11],set:[2,3,6,8,10],set_titl:[2,11],setup:[0,11,12],sever:[0,5,6,11],shall:[5,11],shape:[2,6,9,11],short_str:[0,6,11],should:[0,2,6,11],show:[0,5,6,11],shown:[2,11,12],sigma:[2,11],signific:[5,11],significantli:[5,11],similar:[3,11],simpli:[5,6,11],sinc:[3,5,6,9,11],singl:[2,3,5,6,9,11],slitghtli:[4,11],slow:[5,9,11],slower:[5,11],slowest:[5,11],smaller:6,smooth:[2,11],solut:[5,11],some:[1,2,3,4,6,8,10],sometim:[5,11],soon:[0,11],sourc:[6,7,12],space:6,span:6,spare:9,speci:6,specif:[3,4,5,6,10],specifi:[2,4,5,6,11],specifii:6,split:[5,6,11],stabl:6,stamp:[2,3,5,6,11],standard:[5,6,7,11,12],start:[2,3,4,5,6,8,9,10],start_dat:6,start_tim:[2,3,6,11],state:12,statet:[2,11],station:[6,9],station_nam:6,stationdata:6,statment:[4,11],std:[5,11],step:[2,11],stepdeg:9,still:[0,11],stop:[2,3,6,11],stop_tim:[2,3,6,11],store:[0,4,6,9,11],storea:[0,2,3,4,8,11],str:[5,6,11],str_to_iri:6,strind:6,string:[2,3,4,5,6,11],string_mask:6,stuff:[5,11],sub:[5,6,9,11],subclass:6,subirectori:[4,11],subsequ:[0,11],subset:[3,6,11],suggest:6,suit:10,suitabl:9,summaris:[0,11],suppl_info:6,supplementari:[6,8],suppli:6,support:[6,9],supported_dataset:6,suppos:[3,6,11],sure:[0,9,11],surfac:12,surfobs_annualr:12,sys:9,t0_aatsr:[5,11],t0_aatsr_np:[5,11],t0_aatsr_panda:[5,11],t0_ecmwf:[5,11],t0_ecmwf_np:[5,11],t0_ecmwf_panda:[5,11],take:[2,4,9,11],tempor:[0,2,3,5,6,11],test:[1,3,4,5,9,10,11,12],test_expon:7,test_fil:[4,6,11],test_mathutil:7,test_path:8,test_var:[3,11],testfil:[4,5,6,11],than:[6,9,12],thei:[0,4,5,11,12],them:[1,4,5,11],theme:6,theme_nam:6,therefor:6,therein:[5,6,11],thi:[0,1,2,3,4,5,6,9,11,12],thing:[6,9],third:[5,11],thu:6,tick:[6,8],time:[0,3,4,6,8,9,10,12],time_bnd:[4,11],time_idx:[4,6,11],time_rang:[3,6,11],time_stamp:[2,4,5,6,11],timedelta64:[5,11],timeit:[5,11],times_aatsr:[5,11],times_aatsr_conv:[5,11],times_ecmwf:[5,11],times_ecmwf_conv:[5,11],timeseri:6,timesnum:[5,11],timestamp:[3,6],tindex_cub:6,tit:[2,11],titl:6,to_dict:6,to_timeseri:6,todo:[6,8],tom:12,too:8,took:9,tool:[5,9,10,11,12],total:9,traceback:6,translat:[5,11],trend:[2,8,11],ts_po:[6,8],ts_type:[0,2,6,11],tstamp:[4,6,11],tstr:[5,11],tue:[4,11],tupl:6,tutori:[0,1,2,4,5,10],two:[3,4,5,6,9,11],txt:[0,6,11],type:[2,3,4,5,10,11],typeerror:[5,11],typic:6,unchang:6,under:[4,11],underli:[4,5,6,11],understand:[5,6,11,12],understood:[5,11],unidata:[5,11],unifi:[2,3,11],uniqu:6,unit:[3,5,6,8,11],unknown:[4,11],unspecifi:6,unsupport:[5,11],unzip:[0,11],updat:6,update_file_convent:6,update_inifil:6,upper:6,usabl:6,use:[0,2,3,5,6,7,9,11,12],used:[0,1,5,6,8,11,12],useful:[2,11],user:[0,2,3,4,6,8,9,11],uses:[0,3,5,6,11],using:[0,2,3,4,6,8,12],utc:[3,5,6,11],util:[6,7],valid:[0,2,3,4,5,6,11],valu:[3,5,6,8,11],valueerror:[3,4,5,6,11],var_id:6,var_nam:[2,3,4,5,6,11],var_po:[6,8],variabl:[2,4,6,10],vars_to_read:6,verbos:[0,2,3,6,11],veri:[6,10],version:[0,11],via:[0,5,6,11,12],viridi:6,visualis:10,vmax:[4,6,11],vmin:[4,6,11],wai:[0,5,9,11],wall:9,want:[5,6,11],warn:[3,4,11],websit:12,weight:[2,6,11],weightedaggretor:6,well:[0,2,3,4,6,9,11],were:[2,6,11],what:[0,2,3,4,5,6,11],when:[4,6],whenev:[5,11],where:[0,6,11],wherea:6,whether:6,which:[0,2,3,4,5,6,9,11,12],whole:9,why:[0,4,11],width:6,window:6,wipe:6,wish:[5,6,11],within:[0,3,6,9,11],without:[0,6,9,11],won:[2,3,11],work:[0,2,3,4,5,6,11,12],workshop:12,world:[1,6,8,11],would:8,wrapper:[0,11],write:9,written:[0,11,12],xlim:[4,6,11],xtick:6,year:[2,3,5,6,8,11,12],year_po:[6,8],years_to_load:6,yet:[4,11],ylim:[4,6,11],you:[0,2,3,4,5,6,9,11],your:[0,6,11],ytick:6},titles:["Getting started","AEROCOM default regions","Reading model data: the ReadGrid class","Reading data from multiple models: the ReadMultiGrid class","Introducing the <code class=\"docutils literal notranslate\"><span class=\"pre\">GridData</span></code> class","Handling of time in Pyaerocom","API","API test-suite","Configuration files","Inspect performance of iris interpolation schemes","The Pyaerocom website","Tutorials (Jupyter Notebooks)","Introduction"],titleterms:{"case":9,"class":[2,3,4,11],"default":[1,8,11],The:10,access:6,aerocom:[1,11],api:[6,7],appli:[1,11],base:9,brief:[2,11],case1:9,closest:9,color:6,come:[4,11],compar:9,configur:8,convent:[6,8],convert:[5,11],crop:[1,9,11],cube:[5,11],data:[1,2,3,5,6,11],datapoint:9,datatyp:[5,11],definit:[2,4,11],dig:[5,11],directori:8,document:12,doe:[5,11],domain:6,environ:[0,11],etc:6,exampl:[1,5,11],extract:9,featur:[4,11],file:[6,8],find:9,from:[3,11],gener:6,get:[0,11],global:[0,11],grid:[6,9],griddata:[2,4,11],handl:[5,11],helper:[6,7],how:[5,11],indic:10,input:6,inspect:9,instal:[0,11,12],interfac:[5,9,11],interpol:9,introduc:[4,11],introduct:[2,11,12],iri:[5,9,11],iter:[3,11],jupyt:11,level:7,load:[1,5,11],longitud:[4,11],low:7,map:6,mathemat:6,method:6,model:[2,3,6,11],more:[4,11],multipl:[3,11],name:6,notebook:11,numpi:9,obsdata:9,observ:6,option:[5,11],origin:9,other:[5,11],output:6,over:[3,11],path:8,peculiar:[5,11],perform:9,plot:6,point:9,pyaerocom:[5,10,11],read:[2,3,6,11],readgrid:[2,11],readmultigrid:[3,11],realist:9,region:[1,6,8,11],remark:[2,4,11],represent:[5,6,11],requir:[0,11,12],routin:6,scheme:9,set:[0,11],some:[5,11],specif:[1,11],start:[0,11],suit:7,tabl:10,test:[6,7,8],time:[2,5,11],timestamp:[5,11],tutori:11,type:6,ungrid:6,using:[5,9,11],variabl:[0,3,8,11],veri:[2,11],visualis:6,websit:10,when:[5,11]}})